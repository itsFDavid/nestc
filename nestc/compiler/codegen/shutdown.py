def write_shutdown_logic(f, data):
    f.write("\n// --- Lifecycle: Shutdown Sequence ---\n")
    f.write("void shutdown_framework() {\n")
    f.write('  NC_WARN("NestApplication", "Closing application...");\n')
    
    for s in data["services"]:
        if s.get("destroy_func"):
            f.write(f"  if (global_{s['name']} != NULL) {{\n")
            f.write(f"    {s['destroy_func']}(global_{s['name']});\n")
            f.write(f'    NC_LOG("InstanceLoader", "{s["name"]} destroyed");\n')
            f.write("  }\n")
            
    f.write('  NC_SUCCESS("NestApplication", "Goodbye!");\n')
    f.write("}\n")