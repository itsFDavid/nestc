import os
from nestc.compiler.codegen.discovery import generate_services_discovery
from nestc.compiler.codegen.router import write_router
from nestc.compiler.codegen.shutdown import write_shutdown_logic

def generate_bootstrap_c(data, output_filename):
    build_dir = os.path.dirname(output_filename)
    discovery_path = os.path.join(build_dir, "services_discovery.gen.h")
    generate_services_discovery("src", discovery_path)

    # 1. Generar el motor interno (main.gen.c)
    with open(output_filename, "w") as f:
        f.write("/* BOOTSTRAP GENERADO AUTOMATICAMENTE - NO EDITAR */\n")
        f.write("#include <stdio.h>\n#include <string.h>\n#include <stdlib.h>\n#include <time.h>\n")
        
        f.write("#include \"dto_validators.gen.h\"\n")
        f.write("#include \"services_discovery.gen.h\"\n")
        
        f.write("#include \"@nestcore/nest_core.h\"\n")
        f.write("#include \"@nestcore/mongoose.h\"\n\n")

        f.write("// Variable global de configuración expuesta al router\n")
        f.write("NestApp global_app_config;\n\n")

        # --- Declaraciones Externas ---
        for m in data["modules"]: f.write(f"extern void {m['init_func']}();\n")
        for s in data["services"]:
            if s['init_func']: f.write(f"extern void* {s['init_func']}();\n")
            if s['destroy_func']: f.write(f"extern void {s['destroy_func']}(void* instance);\n")
        
        for c in data["controllers"]:
            args = [f"{c['inject']}* s"] if c['inject'] else []
            if "/:" in c['route']: args.append("const char* id")
            if c.get("method") in ["POST", "PUT", "PATCH"]:
                if c.get("dto"):
                    args.append(f"{c['dto']}* dto")
                else:
                    args.append("const char* body")
            f.write(f"extern NestResponse {c['function']}({', '.join(args)});\n")

        f.write("\n// --- Instancias Globales ---\n")
        for s in data["services"]: f.write(f"static void* global_{s['name']} = NULL;\n")

        write_shutdown_logic(f, data)
        write_router(f, data)

        # --- NESTFACTORY ---
        f.write("\n// --- NestFactory: Creación --- \n")
        f.write("#include \"@nestcore/env_utils.h\"\n\n")
        f.write("NestApp NestFactory_create() {\n")

        f.write("  // 1. Cargar variables de entorno automáticamente\n")
        f.write("  load_env(\".env\");\n\n")

        f.write("  NestApp app = {3000, 1, 1};\n")
        f.write("  atexit(shutdown_framework);\n\n")
        f.write('  NC_LOG("NestFactory", "Starting Nest-C application...");\n\n')

        for s in data["services"]:
            if s['init_func']:
                f.write(f"  global_{s['name']} = {s['init_func']}();\n")
                f.write(f'  NC_LOG("InstanceLoader", "{s["name"]} initialized");\n')

        for m in data["modules"]:
            f.write(f"  {m['init_func']}();\n")
            f.write(f'  NC_LOG("InstanceLoader", "{m["name"]} loaded");\n')

        f.write("\n")
        for c in data["controllers"]:
            method = c.get("method", "GET")
            color = "\\x1b[36m"
            if method == "POST":   color = "\\x1b[32m"
            if method == "PUT":    color = "\\x1b[33m"
            if method == "DELETE": color = "\\x1b[31m"
            f.write(f'  printf("\\x1b[35m[Nest-C]\\x1b[0m \\x1b[32mLOG\\x1b[0m \\x1b[33m[RoutesResolver]\\x1b[0m \\x1b[32mMapped {{{c["route"]}, \\x1b[0m{color}{method}\\x1b[0m\\x1b[32m}} route\\x1b[0m\\n");\n')

        f.write("  return app;\n}\n\n")

        f.write("// --- NestFactory: Escucha --- \n")
        f.write("void NestFactory_listen(NestApp *app) {\n")
        f.write("  global_app_config = *app; \n")

        f.write("  mg_log_set(MG_LL_NONE); // Silenciar a Mongoose temprano\n")
        f.write("  struct mg_mgr mgr; mg_mgr_init(&mgr);\n")
        
        f.write("  char listen_url[64];\n")
        f.write("  snprintf(listen_url, sizeof(listen_url), \"http://0.0.0.0:%d\", app->port);\n")
        f.write("  mg_http_listen(&mgr, listen_url, ev_handler, NULL);\n")
        
        f.write('\n  NC_SUCCESS("NestApplication", "Nest-C server successfully started");\n')
        f.write('  NC_INFO("NestApplication", "Listening at %s", listen_url);\n\n')
        
        f.write("  for (;;) mg_mgr_poll(&mgr, 1000);\n")
        f.write("}\n")