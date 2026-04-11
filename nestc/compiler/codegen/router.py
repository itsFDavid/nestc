def write_router(f, data):
    f.write("\n// --- Enrutador HTTP (Mongoose Integration) ---\n")
    f.write("void handle_request(struct mg_connection *c, struct mg_http_message *hm) {\n")
    f.write("  char uri[256];\n")
    f.write('  snprintf(uri, sizeof(uri), "%.*s", (int)hm->uri.len, hm->uri.buf);\n')
    f.write("  char method[10];\n")
    f.write('  snprintf(method, sizeof(method), "%.*s", (int)hm->method.len, hm->method.buf);\n\n')

    # Logger
    f.write("  time_t rawtime; struct tm * timeinfo; char time_buffer[80];\n")
    f.write("  time(&rawtime); timeinfo = localtime(&rawtime);\n")
    f.write('  strftime(time_buffer, 80, "%d/%m/%Y, %I:%M:%S %p", timeinfo);\n')
    f.write('  printf("\\x1b[35m[Nest-C]\\x1b[0m - %s  \\x1b[33m%s\\x1b[0m \\x1b[36m%s\\x1b[0m\\n", time_buffer, method, uri);\n\n')

    for c_info in data["controllers"]:
        http_method = c_info.get("method", "GET")
        route = c_info["route"]
        
        # Detectar si es una ruta con parámetro (ej: /users/:id)
        has_param = "/:" in route
        
        if has_param:
            base_route = route.split("/:")[0]
            param_name = route.split("/:")[1]
            f.write(f'  if (strcmp(method, "{http_method}") == 0 && strncmp(uri, "{base_route}/", {len(base_route) + 1}) == 0) {{\n')
            f.write(f'    const char* {param_name} = uri + {len(base_route) + 1};\n')
        else:
            f.write(f'  if (strcmp(method, "{http_method}") == 0 && strcmp(uri, "{route}") == 0) {{\n')

        f.write("    char* json_res = NULL;\n")
        
        # Lógica de inyección y parámetros
        if c_info["inject"] and has_param:
            f.write(f"    json_res = {c_info['function']}(({c_info['inject']}*)global_{c_info['inject']}, {param_name});\n")
        elif c_info["inject"]:
            f.write(f"    json_res = {c_info['function']}(({c_info['inject']}*)global_{c_info['inject']});\n")
        elif has_param:
            f.write(f"    json_res = {c_info['function']}({param_name});\n")
        else:
            f.write(f"    json_res = {c_info['function']}();\n")
            
        f.write('    if (json_res == NULL) json_res = strdup("{}");\n')
        f.write('    mg_http_reply(c, 200, "Content-Type: application/json\\r\\n", "%s\\n", json_res);\n')
        f.write("    free(json_res); // Liberar memoria (Convención de Ownership)\n") 
        f.write("    return;\n  }\n")

    f.write('  mg_http_reply(c, 404, "Content-Type: application/json\\r\\n", "{\\"error\\": \\"Not Found\\"}\\n");\n')
    f.write("}\n")

    f.write("\nstatic void ev_handler(struct mg_connection *c, int ev, void *ev_data) {\n")
    f.write("  if (ev == MG_EV_HTTP_MSG) handle_request(c, (struct mg_http_message *) ev_data);\n")
    f.write("}\n")