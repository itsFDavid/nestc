# nestc/compiler/codegen/shutdown.py

def write_shutdown_logic(f, data):
    f.write("\n// --- Graceful Shutdown System ---\n")
    f.write("#include <signal.h>\n\n") # Inyectamos signal.h
    
    # Esta función se ejecutará al recibir Ctrl+C
    f.write("void handle_sigint(int sig) {\n")
    f.write('  printf("\\n\\x1b[33m[Nest-C] Apagado elegante iniciado (Señal %d)...\\x1b[0m\\n", sig);\n')
    f.write("  exit(0); // Esto disparará shutdown_framework gracias a atexit()\n")
    f.write("}\n\n")

    f.write("void shutdown_framework() {\n")
    f.write('  NC_INFO("Shutdown", "Deteniendo servicios y liberando memoria...");\n\n')

    for s in data["services"]:
        if s['destroy_func']:
            # Llamamos al destructor inyectando la instancia global
            f.write(f"  if (global_{s['name']}) {{\n")
            f.write(f"    {s['destroy_func']}(global_{s['name']});\n")
            f.write(f"    global_{s['name']} = NULL;\n")
            f.write("  }\n")

    f.write('  NC_SUCCESS("Shutdown", "Nest-C se detuvo correctamente. RAM limpia.");\n')
    f.write("}\n")