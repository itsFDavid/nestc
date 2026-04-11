def write_router(f, data):
    f.write("\n// --- Enrutador HTTP (Mongoose Integration) ---\n")
    f.write("void handle_request(struct mg_connection *c, struct mg_http_message *hm) {\n")
    
    # Allocación de URI y Método
    f.write("  char *uri = malloc(hm->uri.len + 1);\n")
    f.write("  if (!uri) return;\n")
    f.write("  snprintf(uri, hm->uri.len + 1, \"%.*s\", (int)hm->uri.len, hm->uri.buf);\n\n")

    f.write("  char *method = malloc(hm->method.len + 1);\n")
    f.write("  if (!method) { free(uri); return; }\n")
    f.write("  snprintf(method, hm->method.len + 1, \"%.*s\", (int)hm->method.len, hm->method.buf);\n\n")

    # Extraer Body
    f.write("  char *req_body = malloc(hm->body.len + 1);\n")
    f.write("  if (req_body) {\n")
    f.write("    snprintf(req_body, hm->body.len + 1, \"%.*s\", (int)hm->body.len, hm->body.buf);\n")
    f.write("  } else { req_body = strdup(\"\"); }\n\n")

    # Variables de estado
    f.write("  char *json_res = NULL;\n")
    f.write("  int status_code = 200;\n")
    f.write("  int handled = 0;\n\n")

    # Lógica de Enrutamiento
    first = True
    for c_info in data["controllers"]:
        http_method = c_info.get("method", "GET")
        route = c_info["route"]
        has_param = "/:" in route

        if_keyword = "if" if first else "else if"
        first = False
        
        call_args = []
        if c_info["inject"]: call_args.append(f"({c_info['inject']}*)global_{c_info['inject']}")
        if has_param: call_args.append("raw_id")
        if http_method in ["POST", "PUT", "PATCH"]: call_args.append("req_body")
        arg_string = ", ".join(call_args)

        if has_param:
            base_route = route.split("/:")[0]
            base_len = len(base_route) + 1
            f.write(f'  {if_keyword} (strcmp(method, "{http_method}") == 0 && strncmp(uri, "{base_route}/", {base_len}) == 0) {{\n')
            f.write(f'    char *raw_id = strdup(uri + {base_len});\n')
            f.write('    if (raw_id) {\n')
            f.write('      char *slash = strchr(raw_id, \'/\');\n')
            f.write('      if (slash) *slash = \'\\0\';\n')
            f.write(f"      json_res = {c_info['function']}({arg_string});\n")
            f.write('      free(raw_id);\n    }\n')
            f.write("    handled = 1;\n  }\n")
        else:
            f.write(f'  {if_keyword} (strcmp(method, "{http_method}") == 0 && strcmp(uri, "{route}") == 0) {{\n')
            f.write(f"    json_res = {c_info['function']}({arg_string});\n")
            f.write("    handled = 1;\n  }\n")

    # 404 Fallback
    f.write("\n  if (!handled) {\n    status_code = 404;\n")
    f.write('    json_res = strdup("{\\"error\\": \\"Not Found\\"}");\n  }\n\n')

    # Responder al cliente
    f.write("  if (json_res == NULL) { json_res = strdup(\"{}\"); status_code = 500; }\n")
    f.write('  mg_http_reply(c, status_code, "Content-Type: application/json\\r\\n", "%s\\n", json_res);\n\n')

    # --- NUEVO LOGGER CON ESTATUS ---
    f.write("  // Logger Final\n")
    f.write("  time_t rawtime; struct tm * timeinfo; char time_buffer[80];\n")
    f.write("  time(&rawtime); timeinfo = localtime(&rawtime);\n")
    f.write('  strftime(time_buffer, 80, "%d/%m/%Y, %I:%M:%S %p", timeinfo);\n')
    
    # Lógica de colores para el estatus en el printf
    f.write('  char *st_color = "\\x1b[32m"; // Verde (2xx)\n')
    f.write('  if (status_code >= 400 && status_code < 500) st_color = "\\x1b[33m"; // Amarillo (4xx)\n')
    f.write('  if (status_code >= 500) st_color = "\\x1b[31m"; // Rojo (5xx)\n\n')
    
    f.write('  printf("\\x1b[35m[Nest-C]\\x1b[0m - %s  \\x1b[33m%s\\x1b[0m \\x1b[36m%s\\x1b[0m \\x1b[90m-->\\x1b[0m %s%d\\x1b[0m\\n", ')
    f.write('time_buffer, method, uri, st_color, status_code);\n\n')

    # Limpieza
    f.write("  if (json_res) free(json_res);\n")
    f.write("  free(req_body);\n")
    f.write("  free(uri);\n")
    f.write("  free(method);\n")
    f.write("}\n")

    f.write("\nstatic void ev_handler(struct mg_connection *c, int ev, void *ev_data) {\n")
    f.write("  if (ev == MG_EV_HTTP_MSG) handle_request(c, (struct mg_http_message *) ev_data);\n}\n")