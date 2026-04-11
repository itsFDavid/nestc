def write_shutdown_logic(f, data):
    f.write("\n// --- Lifecycle: Shutdown Sequence ---\n")
    f.write("void shutdown_framework() {\n")
    f.write('  printf("\\n\\x1b[35m[Nest-C]\\x1b[0m \\x1b[33m[NestApplication]\\x1b[0m \\x1b[33mClosing application...\\x1b[0m\\n");\n')
    
    for s in data["services"]:
        if s.get("destroy_func"):
            f.write(f"  if (global_{s['name']} != NULL) {{\n")
            f.write(f"    {s['destroy_func']}(global_{s['name']});\n")
            f.write(f'    printf("\\x1b[35m[Nest-C]\\x1b[0m \\x1b[32mLOG\\x1b[0m \\x1b[33m[InstanceLoader]\\x1b[0m \\x1b[32m{s["name"]} destroyed\\x1b[0m\\n");\n')
            f.write("  }\n")
            
    f.write('  printf("\\x1b[35m[Nest-C]\\x1b[0m \\x1b[32mLOG\\x1b[0m \\x1b[33m[NestApplication]\\x1b[0m \\x1b[32mGoodbye!\\x1b[0m\\n");\n')
    f.write("}\n")