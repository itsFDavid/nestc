import os
import re

def generate_dto_validators(src_dir, build_dir):
    dtos = []
    
    # 1. Escanear todos los archivos .dto.c buscando MÚLTIPLES DTOs
    for root, _, files in os.walk(src_dir):
        for file in files:
            if file.endswith(".dto.c"):
                path = os.path.join(root, file)
                with open(path, "r") as f:
                    content = f.read()
                
                current_dto = None
                
                for line in content.splitlines():
                    dto_match = re.search(r'//\s*@DTO:\s*(\w+)', line)
                    if dto_match:
                        if current_dto: dtos.append(current_dto)
                        rel_path = os.path.relpath(path, build_dir)
                        current_dto = {"name": dto_match.group(1), "file_path": rel_path, "fields": []}
                        continue
                    
                    if current_dto:
                        field_match = re.search(r'//\s*@Field:\s*(\w+)\s*\((.*?)\)', line)
                        if field_match:
                            f_name = field_match.group(1)
                            rules_str = field_match.group(2)
                            rules = {}
                            for rule in rules_str.split(','):
                                if ':' in rule:
                                    k, v = rule.split(':', 1)
                                    rules[k.strip()] = v.strip()
                                else:
                                    rules[rule.strip()] = True
                            current_dto["fields"].append({"name": f_name, "rules": rules})
                
                if current_dto: dtos.append(current_dto)

    # 2. Generar HEADER (dto_validators.gen.h)
    h_path = os.path.join(build_dir, "dto_validators.gen.h")
    with open(h_path, "w") as f:
        f.write("#ifndef DTO_VALIDATORS_H\n#define DTO_VALIDATORS_H\n\n")
        f.write("#include <stdbool.h>\n\n")
        for dto in dtos:
            f.write(f'#include "{dto["file_path"]}"\n')
        f.write("\n")
        for dto in dtos:
            f.write(f'bool validate_{dto["name"]}(const char* json, {dto["name"]}* out, char* err);\n')
            f.write(f'void free_{dto["name"]}({dto["name"]}* dto);\n')
            # --- SERIALIZACIÓN ---
            f.write(f'char* {dto["name"]}_to_json({dto["name"]}* dto);\n') 
        f.write("\n#endif\n")

    # 3. Generar IMPLEMENTACIÓN (dto_validators.gen.c)
    c_path = os.path.join(build_dir, "dto_validators.gen.c")
    with open(c_path, "w") as f:
        f.write("#include \"dto_validators.gen.h\"\n")
        f.write("#include \"@nestcore/frozen.h\"\n")
        f.write("#include <string.h>\n")
        f.write("#include <stdlib.h>\n")
        f.write("#include <stdio.h>\n\n")

        for dto in dtos:
            # --- 3.1 Limpieza ---
            f.write(f"void free_{dto['name']}({dto['name']}* dto) {{\n")
            for field in dto["fields"]:
                if field["rules"].get("Type") == "String":
                    f.write(f"    if (dto->{field['name']}) free(dto->{field['name']});\n")
            f.write("}\n\n")

            # --- 3.2 Validación (json -> struct) ---
            f.write(f"bool validate_{dto['name']}(const char* json, {dto['name']}* out, char* err) {{\n")
            scanf_fmt = "{"
            scanf_args = []
            for field in dto["fields"]:
                if field["rules"].get("Type") == "String":
                    f.write(f"    out->{field['name']} = NULL;\n")
                    scanf_fmt += f"{field['name']}: %Q, "
                    scanf_args.append(f"&out->{field['name']}")
                elif field["rules"].get("Type") == "Int":
                    f.write(f"    out->{field['name']} = -2147483648;\n")
                    scanf_fmt += f"{field['name']}: %d, "
                    scanf_args.append(f"&out->{field['name']}")
                    
            scanf_fmt = scanf_fmt.rstrip(", ") + "}"
            f.write(f"\n    json_scanf(json, strlen(json), \"{scanf_fmt}\", {', '.join(scanf_args)});\n\n")

            for field in dto["fields"]:
                f_name = field["name"]
                rules = field["rules"]
                is_opt = "Optional" in rules
                if rules.get("Type") == "String":
                    if not is_opt: f.write(f"    if (out->{f_name} == NULL) {{ strcpy(err, \"Field '{f_name}' is required.\"); return false; }}\n")
                    f.write(f"    if (out->{f_name} != NULL) {{\n")
                    if "Min" in rules: f.write(f"        if (strlen(out->{f_name}) < {rules['Min']}) {{ sprintf(err, \"Field '{f_name}' must be at least {rules['Min']} chars.\"); return false; }}\n")
                    if "Max" in rules: f.write(f"        if (strlen(out->{f_name}) > {rules['Max']}) {{ sprintf(err, \"Field '{f_name}' must be at most {rules['Max']} chars.\"); return false; }}\n")
                    f.write("    }\n")
                elif rules.get("Type") == "Int":
                    if not is_opt: f.write(f"    if (out->{f_name} == -2147483648) {{ strcpy(err, \"Field '{f_name}' is required.\"); return false; }}\n")
                    f.write(f"    if (out->{f_name} != -2147483648) {{\n")
                    if "Min" in rules: f.write(f"        if (out->{f_name} < {rules['Min']}) {{ sprintf(err, \"Field '{f_name}' must be >= {rules['Min']}.\"); return false; }}\n")
                    if "Max" in rules: f.write(f"        if (out->{f_name} > {rules['Max']}) {{ sprintf(err, \"Field '{f_name}' must be <= {rules['Max']}.\"); return false; }}\n")
                    f.write("    }\n")

            f.write("\n    return true;\n}\n\n")

            # --- 3.3 SERIALIZACIÓN (struct -> json) ---
            f.write(f"char* {dto['name']}_to_json({dto['name']}* dto) {{\n")
            # 1. Inicializamos el buffer a 0 para que strlen funcione bien
            f.write("    char buffer[2048] = {0};\n") 
            f.write("    int first = 1;\n")
            f.write("    strcat(buffer, \"{\");\n\n")
            
            for field in dto["fields"]:
                f_name = field["name"]
                f_type = field["rules"].get("Type")
                is_opt = "Optional" in field["rules"]
                
                if f_type == "String":
                    if is_opt:
                        f.write(f"    if (dto->{f_name} != NULL) {{\n")
                        f.write(f"        if (!first) strcat(buffer, \", \");\n")
                        f.write(f"        snprintf(buffer + strlen(buffer), sizeof(buffer) - strlen(buffer), \"\\\"{f_name}\\\": \\\"%s\\\"\", dto->{f_name});\n")
                        f.write(f"        first = 0;\n")
                        f.write(f"    }}\n")
                    else:
                        f.write(f"    if (!first) strcat(buffer, \", \");\n")
                        f.write(f"    snprintf(buffer + strlen(buffer), sizeof(buffer) - strlen(buffer), \"\\\"{f_name}\\\": \\\"%s\\\"\", dto->{f_name} ? dto->{f_name} : \"\");\n")
                        f.write(f"    first = 0;\n")
                        
                elif f_type == "Int":
                    if is_opt:
                        f.write(f"    if (dto->{f_name} != -2147483648) {{\n")
                        f.write(f"        if (!first) strcat(buffer, \", \");\n")
                        f.write(f"        snprintf(buffer + strlen(buffer), sizeof(buffer) - strlen(buffer), \"\\\"{f_name}\\\": %d\", dto->{f_name});\n")
                        f.write(f"        first = 0;\n")
                        f.write(f"    }}\n")
                    else:
                        f.write(f"    if (!first) strcat(buffer, \", \");\n")
                        f.write(f"    snprintf(buffer + strlen(buffer), sizeof(buffer) - strlen(buffer), \"\\\"{f_name}\\\": %d\", dto->{f_name});\n")
                        f.write(f"    first = 0;\n")
            
            # Cierre seguro del JSON
            f.write("\n    strcat(buffer, \"}\");\n")
            f.write("    return strdup(buffer);\n")
            f.write("}\n\n")

    return dtos