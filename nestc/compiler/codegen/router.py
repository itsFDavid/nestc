def write_router(f, data):
    f.write("\n// --- Enrutador HTTP (Mongoose Integration) ---\n")
    f.write("void handle_request(struct mg_connection *c, struct mg_http_message *hm) {\n")
    
    f.write("  char *uri = malloc(hm->uri.len + 1);\n")
    f.write("  if (!uri) return;\n")
    f.write("  snprintf(uri, hm->uri.len + 1, \"%.*s\", (int)hm->uri.len, hm->uri.buf);\n\n")

    f.write("  char *method = malloc(hm->method.len + 1);\n")
    f.write("  if (!method) { free(uri); return; }\n")
    f.write("  snprintf(method, hm->method.len + 1, \"%.*s\", (int)hm->method.len, hm->method.buf);\n\n")

    # Extraer el Body de forma segura
    f.write("  char *req_body = malloc(hm->body.len + 1);\n")
    f.write("  if (req_body) {\n")
    f.write("    snprintf(req_body, hm->body.len + 1, \"%.*s\", (int)hm->body.len, hm->body.buf);\n")
    f.write("  } else { req_body = strdup(\"\"); }\n\n")

    f.write("  time_t rawtime; struct tm * timeinfo; char time_buffer[80];\n")
    f.write("  time(&rawtime); timeinfo = localtime(&rawtime);\n")
    f.write('  strftime(time_buffer, 80, "%d/%m/%Y, %I:%M:%S %p", timeinfo);\n')
    f.write('  printf("\\x1b[35m[Nest-C]\\x1b[0m - %s  \\x1b[33m%s\\x1b[0m \\x1b[36m%s\\x1b[0m\\n", time_buffer, method, uri);\n\n')

    f.write("  char *json_res = NULL;\n  int status_code = 200;\n  int handled = 0;\n\n")

    first = True
    for c_info in data["controllers"]:
        http_method = c_info.get("method", "GET")
        route = c_info["route"]
        has_param = "/:" in route

        if_keyword = "if" if first else "else if"
        first = False
        
        # Construimos dinámicamente los argumentos de inyección
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

    f.write("\n  if (!handled) {\n    status_code = 404;\n")
    f.write('    json_res = strdup("{\\"error\\": \\"Not Found\\"}");\n  }\n\n')

    f.write("  if (json_res == NULL) json_res = strdup(\"{}\");\n\n")

    f.write("  if (json_res != NULL) {\n")
    f.write('    mg_http_reply(c, status_code, "Content-Type: application/json\\r\\n", "%s\\n", json_res);\n')
    f.write("    free(json_res);\n  } else {\n")
    f.write('    mg_http_reply(c, 500, "Content-Type: application/json\\r\\n", "{\\"error\\": \\"Internal OOM\\"}");\n  }\n\n')

    f.write("  free(req_body);\n  free(uri);\n  free(method);\n}\n")

    f.write("\nstatic void ev_handler(struct mg_connection *c, int ev, void *ev_data) {\n")
    f.write("  if (ev == MG_EV_HTTP_MSG) handle_request(c, (struct mg_http_message *) ev_data);\n}\n")