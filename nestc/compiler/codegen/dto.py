import os
import re

STRING_LIKE_TYPES = {
    "String",
    "Email",
    "URL",
    "UUID",
    "Date",
    "DateTime",
    "Phone",
    "Regex",
    "Enum",
}
NUMBER_TYPES = {"Int", "Float"}

TOKEN_TYPE_MAP = {
    "String": "JSON_TYPE_STRING",
    "Int": "JSON_TYPE_NUMBER",
    "Float": "JSON_TYPE_NUMBER",
    "Bool": None,  # Manejo especial
    "Email": "JSON_TYPE_STRING",
    "URL": "JSON_TYPE_STRING",
    "UUID": "JSON_TYPE_STRING",
    "Date": "JSON_TYPE_STRING",
    "DateTime": "JSON_TYPE_STRING",
    "Phone": "JSON_TYPE_STRING",
    "Regex": "JSON_TYPE_STRING",
    "Enum": "JSON_TYPE_STRING",
}

EXTRACT_FMT = {
    "String": "%Q",
    "Int": "%d",
    "Float": "%g",
    "Bool": "%B",
    "Email": "%Q",
    "URL": "%Q",
    "UUID": "%Q",
    "Date": "%Q",
    "DateTime": "%Q",
    "Phone": "%Q",
    "Regex": "%Q",
    "Enum": "%Q",
}


def generate_dto_validators(src_dir, build_dir):
    dtos = []
    for root, _, files in os.walk(src_dir):
        for file in files:
            if file.endswith(".dto.c"):
                path = os.path.join(root, file)
                with open(path, "r") as f:
                    content = f.read()
                current_dto = None
                for line in content.splitlines():
                    dto_match = re.search(r"//\s*@DTO:\s*(\w+)", line)
                    if dto_match:
                        if current_dto:
                            dtos.append(current_dto)
                        current_dto = {
                            "name": dto_match.group(1),
                            "file_path": os.path.relpath(path, build_dir),
                            "fields": [],
                        }
                        continue
                    if current_dto:
                        field_match = re.search(
                            r"//\s*@Field:\s*(\w+)\s*\((.*?)\)", line
                        )
                        if field_match:
                            f_name, rules_str = field_match.groups()
                            rules = {
                                r.split(":")[0].strip(): (
                                    r.split(":")[1].strip() if ":" in r else True
                                )
                                for r in rules_str.split(",")
                            }
                            current_dto["fields"].append(
                                {"name": f_name, "rules": rules}
                            )
                if current_dto:
                    dtos.append(current_dto)

    # --- HEADER ---
    with open(os.path.join(build_dir, "dto_validators.gen.h"), "w") as f:
        f.write(
            "#ifndef DTO_VALIDATORS_H\n#define DTO_VALIDATORS_H\n#include <stdbool.h>\n#include <string.h>\n"
        )
        for dto in dtos:
            f.write(f'#include "{dto["file_path"]}"\n')
        for dto in dtos:
            f.write(
                f'bool validate_{dto["name"]}(const char* json, {dto["name"]}* out, char* err);\n'
            )
            f.write(f'void free_{dto["name"]}({dto["name"]}* dto);\n')
            f.write(f'char* {dto["name"]}_to_json({dto["name"]}* dto);\n')
        f.write("#endif\n")

    # --- IMPLEMENTACIÓN ---
    with open(os.path.join(build_dir, "dto_validators.gen.c"), "w") as f:
        f.write('#include "dto_validators.gen.h"\n#include "@nestcore/frozen.h"\n')
        f.write('#include "@nestcore/nc_validators.h"\n#include <stdio.h>\n#include <stdlib.h>\n\n')

        for dto in dtos:
            # 3.1 Función de Limpieza (¡INDISPENSABLE!)
            f.write(f"void free_{dto['name']}({dto['name']}* dto) {{\n")
            for field in dto["fields"]:
                if field["rules"].get("Type", "String") in STRING_LIKE_TYPES:
                    f.write(f"    if (dto->{field['name']}) free(dto->{field['name']});\n")
            f.write("}\n\n")

            # 3.2 Función de Validación e Inicialización
            f.write(f"bool validate_{dto['name']}(const char* json, {dto['name']}* out, char* err) {{\n")
            
            f.write("    // 1. Inicializar para evitar basura en memoria\n")
            for field in dto["fields"]:
                f_name = field["name"]
                f_type = field["rules"].get("Type", "String")
                if f_type in STRING_LIKE_TYPES:
                    f.write(f"    out->{f_name} = NULL;\n")
                elif f_type == "Int":
                    f.write(f"    out->{f_name} = -2147483648;\n")
                elif f_type == "Float":
                    f.write(f"    out->{f_name} = 0.0;\n")
                elif f_type == "Bool":
                    f.write(f"    out->{f_name} = 0;\n")
            
            f.write("\n    // 2. Ejecutar validadores por campo\n")
            for field in dto["fields"]:
                _write_field_validation(f, field)
            
            f.write("    return true;\n}\n\n")

            # 3.3 Serialización
            _write_serialization(f, dto)

    return dtos


def _write_field_validation(f, field, indent="    "):
    f_name = field["name"]
    rules = field["rules"]
    f_type = rules.get("Type", "String")
    is_opt = "Optional" in rules

    f.write(f"{indent}{{\n")
    f.write(f"{indent}    struct json_token _tok;\n")
    f.write(
        f'{indent}    int _found = json_scanf(json, strlen(json), "{{{f_name}: %T}}", &_tok);\n'
    )

    if is_opt:
        f.write(f"{indent}    if (!_found) goto _skip_{f_name};\n")
    else:
        f.write(
            f'{indent}    if (!_found) {{ sprintf(err, "Field \'%s\' is required.", "{f_name}"); return false; }}\n'
        )

    # Verificación de Tipo
    if f_type == "Bool":
        f.write(
            f"{indent}    if (_tok.type != JSON_TYPE_TRUE && _tok.type != JSON_TYPE_FALSE) {{ strcpy(err, \"Field '{f_name}' must be a boolean.\"); return false; }}\n"
        )
    elif f_type == "Int":
        f.write(
            f"{indent}    if (_tok.type != JSON_TYPE_NUMBER) {{ strcpy(err, \"Field '{f_name}' must be an integer.\"); return false; }}\n"
        )
        f.write(
            f"{indent}    for(int _i=0; _i<_tok.len; _i++) if(_tok.ptr[_i]=='.') {{ strcpy(err, \"Field '{f_name}' must be an integer (no float).\"); return false; }}\n"
        )
    elif f_type == "Float":
        f.write(
            f"{indent}    if (_tok.type != JSON_TYPE_NUMBER) {{ strcpy(err, \"Field '{f_name}' must be a number.\"); return false; }}\n"
        )
    else:
        token_expected = TOKEN_TYPE_MAP.get(f_type, "JSON_TYPE_STRING")
        f.write(
            f"{indent}    if (_tok.type != {token_expected}) {{ strcpy(err, \"Field '{f_name}' must be a String.\"); return false; }}\n"
        )

    # Extracción y Reglas
    fmt = EXTRACT_FMT.get(f_type, "%Q")
    f.write(
        f'{indent}    json_scanf(json, strlen(json), "{{{f_name}: {fmt}}}", &out->{f_name});\n'
    )
    _write_type_rules(f, f_name, f_type, rules, indent)

    if is_opt:
        f.write(f"{indent}    _skip_{f_name}:;\n")
    f.write(f"{indent}}}\n")


def _write_type_rules(f, f_name, f_type, rules, indent):
    if f_type in STRING_LIKE_TYPES:
        if "Min" in rules:
            f.write(
                f"{indent}    if (out->{f_name} && strlen(out->{f_name}) < {rules['Min']}) {{ sprintf(err, \"Field '{f_name}' must be at least {rules['Min']} chars.\"); return false; }}\n"
            )
        if "Max" in rules:
            f.write(
                f"{indent}    if (out->{f_name} && strlen(out->{f_name}) > {rules['Max']}) {{ sprintf(err, \"Field '{f_name}' must be at most {rules['Max']} chars.\"); return false; }}\n"
            )

        # Validadores de nc_validators.h
        val_map = {
            "Email": "_nestc_validate_email",
            "URL": "_nestc_validate_url",
            "UUID": "_nestc_validate_uuid",
            "Date": "_nestc_validate_date",
            "DateTime": "_nestc_validate_datetime",
            "Phone": "_nestc_validate_phone",
        }
        if f_type in val_map:
            f.write(
                f"{indent}    if (out->{f_name} && !{val_map[f_type]}(out->{f_name})) {{ strcpy(err, \"Field '{f_name}' has invalid format.\"); return false; }}\n"
            )

        if f_type == "Enum":
            vals = [v.strip() for v in rules.get("Values", "").split("|")]
            check = " && ".join([f'strcmp(out->{f_name}, "{v}") != 0' for v in vals])
            f.write(
                f"{indent}    if (out->{f_name} && ({check})) {{ strcpy(err, \"Field '{f_name}' must be one of: {'|'.join(vals)}.\"); return false; }}\n"
            )

    elif f_type in NUMBER_TYPES:
        if "Min" in rules:
            f.write(
                f"{indent}    if (out->{f_name} < {rules['Min']}) {{ strcpy(err, \"Field '{f_name}' is too small.\"); return false; }}\n"
            )
        if "Max" in rules:
            f.write(
                f"{indent}    if (out->{f_name} > {rules['Max']}) {{ strcpy(err, \"Field '{f_name}' is too large.\"); return false; }}\n"
            )


def _write_serialization(f, dto):
    f.write(f"char* {dto['name']}_to_json({dto['name']}* dto) {{\n")
    f.write('    char buffer[4096] = {0}; int first = 1; strcat(buffer, "{");\n')
    for field in dto["fields"]:
        f_name = field["name"]; f_type = field["rules"].get("Type", "String"); is_opt = "Optional" in field["rules"]
        
        c_is_opt = "1" if is_opt else "0"

        if f_type in STRING_LIKE_TYPES:
            f.write(f'    if (dto->{f_name}) {{ if(!first) strcat(buffer,", "); sprintf(buffer+strlen(buffer), "\\"{f_name}\\": \\"%s\\"", dto->{f_name}); first=0; }}\n')
        elif f_type == "Int":
            f.write(f'    if (!{c_is_opt} || dto->{f_name} != -2147483648) {{ if(!first) strcat(buffer,", "); sprintf(buffer+strlen(buffer), "\\"{f_name}\\": %d", dto->{f_name}); first=0; }}\n')
        elif f_type == "Float":
            f.write(f'    if (!{c_is_opt} || dto->{f_name} != 0.0) {{ if(!first) strcat(buffer,", "); sprintf(buffer+strlen(buffer), "\\"{f_name}\\": %g", dto->{f_name}); first=0; }}\n')
        elif f_type == "Bool":
            f.write(f'    if(!first) strcat(buffer,", "); sprintf(buffer+strlen(buffer), "\\"{f_name}\\": %s", dto->{f_name} ? "true":"false"); first=0;\n')
    f.write('    strcat(buffer, "}"); return strdup(buffer);\n}\n\n')
