def write_router(f, data):
    f.write("\n// Utility: Limpia la ruta de dobles slashes para normalizarla\n")
    f.write("void normalize_path(char *path) {\n")
    f.write("  char *src = path, *dst = path;\n")
    f.write("  while (*src) {\n")
    f.write("    if (*src == '/' && *(src+1) == '/') { src++; continue; }\n")
    f.write("    *dst++ = *src++;\n")
    f.write("  }\n")
    f.write("  *dst = '\\0';\n")
    f.write("}\n\n")

    f.write("// --- Enrutador HTTP (Mongoose Integration) ---\n")
    f.write("void handle_request(struct mg_connection *c, struct mg_http_message *hm) {\n")
    
    f.write("  char *method = malloc(hm->method.len + 1);\n")
    f.write("  if (!method) return;\n")
    f.write("  snprintf(method, hm->method.len + 1, \"%.*s\", (int)hm->method.len, hm->method.buf);\n\n")

    f.write("  const char *headers = \"Content-Type: application/json\\r\\n\"\n")
    f.write("                        \"Access-Control-Allow-Origin: *\\r\\n\"\n")
    f.write("                        \"Access-Control-Allow-Methods: GET, POST, PUT, DELETE, OPTIONS\\r\\n\"\n")
    f.write("                        \"Access-Control-Allow-Headers: Content-Type, Authorization\\r\\n\";\n\n")

    f.write("  if (strcmp(method, \"OPTIONS\") == 0) {\n")
    f.write("    mg_http_reply(c, 204, headers, \"\");\n")
    f.write("    free(method);\n    return;\n  }\n\n")

    f.write("  char *uri = malloc(hm->uri.len + 1);\n")
    f.write("  if (!uri) { free(method); return; }\n")
    f.write("  snprintf(uri, hm->uri.len + 1, \"%.*s\", (int)hm->uri.len, hm->uri.buf);\n\n")

    f.write("  normalize_path(uri);\n")
    f.write("  if (strstr(uri, \"..\")) {\n")
    f.write("    mg_http_reply(c, 400, headers, \"{\\\"error\\\": \\\"Security Violation: Path Traversal Detected\\\"}\\n\");\n")
    f.write("    printf(\"\\x1b[35m[Nest-C]\\x1b[0m - \\x1b[31m[SECURITY BLOCK]\\x1b[0m \\x1b[36m%s\\x1b[0m \\x1b[90m-->\\x1b[0m \\x1b[31m400\\x1b[0m\\n\", uri);\n")
    f.write("    free(uri); free(method); return;\n  }\n\n")

    f.write("  if (hm->body.len > (global_app_config.payload_limit_mb * 1048576)) {\n")
    f.write("    mg_http_reply(c, 413, headers, \"{\\\"error\\\": \\\"Payload Too Large.\\\"}\\n\");\n")
    f.write("    printf(\"\\x1b[35m[Nest-C]\\x1b[0m - \\x1b[31m[PAYLOAD BLOCK]\\x1b[0m \\x1b[36m%s\\x1b[0m \\x1b[90m-->\\x1b[0m \\x1b[31m413\\x1b[0m\\n\", uri);\n")
    f.write("    free(uri); free(method); return;\n  }\n\n")

    f.write("  char *req_body = malloc(hm->body.len + 1);\n")
    f.write("  if (req_body) {\n")
    f.write("    snprintf(req_body, hm->body.len + 1, \"%.*s\", (int)hm->body.len, hm->body.buf);\n")
    f.write("  } else { req_body = strdup(\"\"); }\n\n")

    # MIGRACIÓN A NESTRESPONSE
    f.write("  NestResponse nest_res = {0, NULL};\n")
    f.write("  int handled = 0;\n\n")

    first = True
    for c_info in data["controllers"]:
        http_method = c_info.get("method", "GET")
        route = c_info["route"]
        has_param = "/:" in route
        dto_name = c_info.get("dto")

        if_keyword = "if" if first else "else if"
        first = False
        
        call_args = []
        if c_info["inject"]: call_args.append(f"({c_info['inject']}*)global_{c_info['inject']}")
        if has_param: call_args.append("raw_id")
        
        if http_method in ["POST", "PUT", "PATCH"]:
            if dto_name:
                call_args.append("&dto_obj") 
            else:
                call_args.append("req_body") 

        arg_string = ", ".join(call_args)

        if has_param:
            base_route = route.split("/:")[0]
            base_len = len(base_route) + 1
            f.write(f'  {if_keyword} (strcmp(method, "{http_method}") == 0 && strncmp(uri, "{base_route}/", {base_len}) == 0) {{\n')
            f.write(f'    char *raw_id = strdup(uri + {base_len});\n')
            f.write('    if (raw_id) {\n')
            f.write('      char *slash = strchr(raw_id, \'/\');\n')
            f.write('      if (slash) *slash = \'\\0\';\n')
            indent = "      "
        else:
            f.write(f'  {if_keyword} (strcmp(method, "{http_method}") == 0 && strcmp(uri, "{route}") == 0) {{\n')
            indent = "    "

        if dto_name:
            f.write(f'{indent}{dto_name} dto_obj;\n')
            f.write(f'{indent}char dto_err[256] = "";\n')
            f.write(f'{indent}if (!validate_{dto_name}(req_body, &dto_obj, dto_err)) {{\n')
            f.write(f'{indent}  char err_res[512];\n')
            f.write(f'{indent}  snprintf(err_res, sizeof(err_res), "{{\\"error\\": \\"Bad Request\\", \\"message\\": \\"%s\\"}}", dto_err);\n')
            f.write(f'{indent}  nest_res = NESTC_BAD_REQUEST(err_res);\n') # Macro implementada
            f.write(f'{indent}}} else {{\n')
            f.write(f'{indent}  nest_res = {c_info["function"]}({arg_string});\n') # Retorno de struct
            f.write(f'{indent}  free_{dto_name}(&dto_obj);\n')
            f.write(f'{indent}}}\n')
        else:
            f.write(f'{indent}nest_res = {c_info["function"]}({arg_string});\n') # Retorno de struct
        
        if has_param:
            f.write('      free(raw_id);\n')
            f.write('    } else {\n')
            f.write('      nest_res = NESTC_ERROR("{\\"error\\": \\"Internal Server Error (OOM)\\"}");\n')
            f.write('    }\n')
        
        f.write(f'    handled = 1;\n') 
        f.write("  }\n")

    # 404 Fallback actualizado a NestResponse
    f.write("\n  if (!handled) {\n")
    f.write('    nest_res = NESTC_NOT_FOUND("{\\"error\\": \\"Route not found\\"}");\n')
    f.write("  }\n\n")

    f.write("  if (!nest_res.body) {\n")
    f.write('    nest_res = NESTC_ERROR("{\\"error\\": \\"Internal Server Error\\"}");\n')
    f.write("  }\n\n")

    f.write('  mg_http_reply(c, nest_res.status, headers, "%s\\n", nest_res.body);\n\n')

    # Logger
    f.write("  time_t rawtime; struct tm * timeinfo; char time_buffer[80];\n")
    f.write("  time(&rawtime); timeinfo = localtime(&rawtime);\n")
    f.write('  strftime(time_buffer, 80, "%d/%m/%Y, %I:%M:%S %p", timeinfo);\n')
    f.write('  char *st_color = "\\x1b[32m"; // Verde (2xx)\n')
    f.write('  if (nest_res.status >= 400 && nest_res.status < 500) st_color = "\\x1b[33m"; // Amarillo (4xx)\n')
    f.write('  if (nest_res.status >= 500) st_color = "\\x1b[31m"; // Rojo (5xx)\n\n')
    f.write('  printf("\\x1b[35m[Nest-C]\\x1b[0m - %s  \\x1b[33m%s\\x1b[0m \\x1b[36m%s\\x1b[0m \\x1b[90m-->\\x1b[0m %s%d\\x1b[0m\\n", ')
    f.write('time_buffer, method, uri, st_color, nest_res.status);\n\n')

    # Limpieza
    f.write("  if (nest_res.body) free(nest_res.body);\n")
    f.write("  free(req_body);\n")
    f.write("  free(uri);\n")
    f.write("  free(method);\n")
    f.write("}\n")

    f.write("\nstatic void ev_handler(struct mg_connection *c, int ev, void *ev_data) {\n")
    f.write("  if (ev == MG_EV_HTTP_MSG) handle_request(c, (struct mg_http_message *) ev_data);\n}\n")