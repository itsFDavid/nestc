import os
from nestc.compiler.codegen.discovery import generate_services_discovery
from nestc.compiler.codegen.router import write_router
from nestc.compiler.codegen.shutdown import write_shutdown_logic

def generate_bootstrap_c(data, output_filename):
    build_dir = os.path.dirname(output_filename)
    discovery_path = os.path.join(build_dir, "services_discovery.gen.h")
    generate_services_discovery("src", discovery_path)

    with open(output_filename, "w") as f:
        f.write("/* BOOTSTRAP GENERADO AUTOMATICAMENTE - NO EDITAR */\n")
        f.write("#include <stdio.h>\n#include <string.h>\n#include <stdlib.h>\n#include <time.h>\n")
        f.write("#include \"services_discovery.gen.h\"\n")
        f.write("#include \"../src/mongoose.h\"\n\n")

        f.write("// --- Prototipos de Modulos ---\n")
        for m in data["modules"]:
            f.write(f"extern void {m['init_func']}();\n")

        f.write("\n// --- Prototipos de Lifecycle (Services) ---\n")
        for s in data["services"]:
            if s['init_func']: f.write(f"extern void* {s['init_func']}();\n")
            if s['destroy_func']: f.write(f"extern void {s['destroy_func']}(void* instance);\n")

        f.write("\n// --- Prototipos de Controladores ---\n")
        for c in data["controllers"]:
            args = []
            if c['inject']: args.append(f"{c['inject']}* s")
            if "/:" in c['route']: args.append("const char* id")
            if c.get("method") in ["POST", "PUT", "PATCH"]:
                args.append("const char* body")
            arg_str = ", ".join(args)
            f.write(f"extern char* {c['function']}({arg_str});\n")

        f.write("\n// --- Instancias Globales ---\n")
        for s in data["services"]:
            f.write(f"static void* global_{s['name']} = NULL;\n")

        write_shutdown_logic(f, data)
        write_router(f, data)

        f.write("\n// --- Punto de Entrada Principal ---\nint main() {\n")
        f.write("  atexit(shutdown_framework);\n  struct mg_mgr mgr; mg_mgr_init(&mgr);\n\n")

        # Configuración de logs de Mongoose (opcional, para reducir ruido)
        f.write("  mg_log_set(MG_LL_NONE); // Silenciar logs de Mongoose\n\n")

        f.write('  printf("\\x1b[35m[Nest-C]\\x1b[0m \\x1b[32mLOG\\x1b[0m \\x1b[33m[NestFactory]\\x1b[0m \\x1b[32mStarting Nest-C application...\\x1b[0m\\n");\n\n')

        for s in data["services"]:
            if s['init_func']:
                f.write(f"  global_{s['name']} = {s['init_func']}();\n")
                f.write(f'  printf("\\x1b[35m[Nest-C]\\x1b[0m \\x1b[32mLOG\\x1b[0m \\x1b[33m[InstanceLoader]\\x1b[0m \\x1b[32m{s["name"]} initialized\\x1b[0m\\n");\n')

        for m in data["modules"]:
            f.write(f"  {m['init_func']}();\n")
            f.write(f'  printf("\\x1b[35m[Nest-C]\\x1b[0m \\x1b[32mLOG\\x1b[0m \\x1b[33m[InstanceLoader]\\x1b[0m \\x1b[32m{m["name"]} loaded\\x1b[0m\\n");\n')

        f.write("\n")
        # --- LOGS DE RUTAS MEJORADOS ---
        for c in data["controllers"]:
            method = c.get("method", "GET")
            # Definir color según el método
            color = "\\x1b[36m" # Cyan (GET)
            if method == "POST":   color = "\\x1b[32m" # Green
            if method == "PUT":    color = "\\x1b[33m" # Yellow
            if method == "DELETE": color = "\\x1b[31m" # Red
            
            # Imprimimos: Mapped {/ruta, METODO}
            f.write(f'  printf("\\x1b[35m[Nest-C]\\x1b[0m \\x1b[32mLOG\\x1b[0m \\x1b[33m[RoutesResolver]\\x1b[0m \\x1b[32mMapped {{{c["route"]}, \\x1b[0m{color}{method}\\x1b[0m\\x1b[32m}} route\\x1b[0m\\n");\n')

        f.write('\n  printf("\\n\\x1b[35m[Nest-C]\\x1b[0m \\x1b[32mLOG\\x1b[0m \\x1b[33m[NestApplication]\\x1b[0m \\x1b[32mNest-C server successfully started\\x1b[0m\\n");\n')
        f.write('  printf("\\x1b[35m[Nest-C]\\x1b[0m \\x1b[32mLOG\\x1b[0m \\x1b[33m[NestApplication]\\x1b[0m \\x1b[32mListening at \\x1b[0m\\x1b[36mhttp://localhost:3000\\x1b[0m\\n\\n");\n')
        f.write('  mg_http_listen(&mgr, "http://0.0.0.0:3000", ev_handler, NULL);\n')
        f.write("  for (;;) mg_mgr_poll(&mgr, 1000);\n  return 0;\n}\n")