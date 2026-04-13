import os
import click
from nestc.utils.colors import Colors

CRUD_METHODS = {
    "find_all": ("GET", "/{name}"),
    "find_one": ("GET", "/{name}/:id"),
    "create":   ("POST", "/{name}"),
    "update":   ("PUT", "/{name}/:id"),
    "remove":   ("DELETE", "/{name}/:id"),
}

# Mapa de macros de NestResponse por método HTTP
METHOD_RESPONSE_MACRO = {
    "find_all": "NESTC_OK_T",
    "find_one": "NESTC_OK_T",
    "create":   "NESTC_CREATED_T",
    "update":   "NESTC_OK_T",
    "remove":   "NESTC_OK_T",
}

def create_resource(name):
    click.echo("Nest-C resource generator")
    transport = click.prompt("What transport layer do you use?", default="REST API")
    is_microservice = transport.strip().lower() == "microservice"
    
    if not is_microservice:
        crud = click.confirm("Would you like to generate CRUD entry points?", default=True)
    else:
        crud = False

    res_dir = os.path.join("src", name)
    os.makedirs(res_dir, exist_ok=True)
    cap = name.capitalize()

    # 1. GENERAR SERVICE
    with open(os.path.join(res_dir, f"{name}.service.c"), "w") as f:
        f.write('#include "@nestcore/nest_core.h"\n')
        
        if crud:
            f.write(f'#include "dto/{name}.dto.c"\n\n')
        else:
            f.write('\n')
        
        f.write(f"// @Service: {cap}Service\ntypedef struct {{\n")
        if crud:
            f.write("    char* (*find_all)();\n")
            f.write("    char* (*find_one)(const char* id);\n")
            f.write(f"    char* (*create)(Create{cap}Dto* dto);\n") 
            f.write(f"    char* (*update)(const char* id, Update{cap}Dto* dto);\n")
            f.write("    char* (*remove)(const char* id);\n")
        else:
            f.write("    char* (*do_something)();\n")
        f.write(f"}} {cap}Service;\n\n")

        if crud:
            f.write(f'char* {name}_logic_all() {{\n')
            f.write(f'    return NESTC_OBJ(NC_STR("res", "{name}"));\n')
            f.write(f'}}\n\n')
            
            f.write(f'char* {name}_logic_one(const char* id) {{\n')
            f.write(f'    return NESTC_OBJ(NC_STR("id", id));\n')
            f.write(f'}}\n\n')
            
            f.write(f'char* {name}_logic_create(Create{cap}Dto* dto) {{\n')
            f.write(f'    // Retornamos el DTO serializado\n')
            f.write(f'    return Create{cap}Dto_to_json(dto);\n')
            f.write(f'}}\n\n')
            
            f.write(f'char* {name}_logic_update(const char* id, Update{cap}Dto* dto) {{\n')
            f.write(f'    return Update{cap}Dto_to_json(dto);\n')
            f.write(f'}}\n\n')
            
            f.write(f'char* {name}_logic_remove(const char* id) {{\n')
            f.write(f'    return NESTC_OBJ(\n')
            f.write(f'        NC_STR("action", "removed"),\n')
            f.write(f'        NC_STR("id", id)\n')
            f.write(f'    );\n')
            f.write(f'}}\n')
        else:
            f.write(f'char* {name}_logic_something() {{\n')
            f.write(f'    return NESTC_OBJ(NC_STR("action", "{name} service executed"));\n')
            f.write(f'}}\n')

    # 2. GENERAR CONTROLLER (NestResponse implementation)
    if not is_microservice:
        with open(os.path.join(res_dir, f"{name}.controller.c"), "w") as f:
            f.write(f'#include "{name}.service.c"\n\n')
            
            if crud:
                for method, (http, route) in CRUD_METHODS.items():
                    parsed_route = route.replace("{name}", name)
                    macro = METHOD_RESPONSE_MACRO[method] # Obtenemos el macro de NestResponse
                    
                    f.write(f"// @{http}: {parsed_route}\n// @Inject: {cap}Service\n")
                    
                    if http == "POST":
                        f.write(f"// @Body: Create{cap}Dto\n")
                    elif http in ["PUT", "PATCH"]:
                        f.write(f"// @Body: Update{cap}Dto\n")
                    
                    args = [f"{cap}Service* s"]
                    if "/:id" in parsed_route: args.append("const char* id")
                    
                    if http == "POST": 
                        args.append(f"Create{cap}Dto* dto")
                    elif http in ["PUT", "PATCH"]: 
                        args.append(f"Update{cap}Dto* dto")
                    
                    call_args = []
                    if "/:id" in parsed_route: call_args.append("id")
                    if http in ["POST", "PUT", "PATCH"]: call_args.append("dto")
                    
                    # Retorno NestResponse y Guard de inyección
                    f.write(f"NestResponse {name}_{method}_handler({', '.join(args)}) {{\n")
                    f.write(f"    if (!s) return NESTC_ERROR(\"{{\\\"error\\\": \\\"Service unavailable\\\"}}\");\n")
                    f.write(f"    return {macro}(s->{method}({', '.join(call_args)}));\n")
                    f.write(f"}}\n\n")
            else:
                f.write(f"// @GET: /{name}\n// @Inject: {cap}Service\n")
                f.write(f"NestResponse {name}_get_handler({cap}Service* s) {{\n")
                f.write(f"    if (!s) return NESTC_ERROR(\"{{\\\"error\\\": \\\"Service unavailable\\\"}}\");\n")
                f.write(f"    return NESTC_OK_T(s->do_something());\n")
                f.write(f"}}\n")

    # 3. GENERAR MÓDULO (Guard en malloc)
    with open(os.path.join(res_dir, f"{name}.module.c"), "w") as f:
        f.write(f'#include "{name}.service.c"\n\n' if is_microservice else f'#include "{name}.controller.c"\n\n')

        f.write(f"// @Init: {cap}Service\nvoid* init_{name}_service() {{\n")
        f.write(f"    {cap}Service* s = malloc(sizeof({cap}Service));\n")
        f.write(f"    if (!s) return NULL;\n") # Protección contra Out of Memory
        
        if crud: 
            f.write(f"    s->find_all = {name}_logic_all;\n")
            f.write(f"    s->find_one = {name}_logic_one;\n")
            f.write(f"    s->create = {name}_logic_create;\n")
            f.write(f"    s->update = {name}_logic_update;\n")
            f.write(f"    s->remove = {name}_logic_remove;\n")
        else:
            f.write(f"    s->do_something = {name}_logic_something;\n")
            
        f.write("    return s;\n}\n\n")
        f.write(f"// @Destroy: {cap}Service\nvoid destroy_{name}_service(void* s) {{\n    if (s) free(s);\n}}\n\n")
        f.write(f"// @Module: {cap}Module\nvoid {name}_module_init() {{}}\n")
    
    # 4. GENERAR DTO
    if crud:
        dto_dir = os.path.join(res_dir, "dto")
        os.makedirs(dto_dir, exist_ok=True)
        dto_path = os.path.join(dto_dir, f"{name}.dto.c")
        
        with open(dto_path, "w") as f:
            f.write(f"#ifndef {cap.upper()}_DTO_H\n")
            f.write(f"#define {cap.upper()}_DTO_H\n\n")
            f.write(f"// @DTO: Create{cap}Dto\n")
            f.write(f"// @Field: nombre (Type: String, Min: 2, Max: 50)\n")
            f.write(f"// @Field: edad (Type: Int, Min: 18)\n")
            f.write(f"typedef struct {{\n")
            f.write(f"    char* nombre;\n")
            f.write(f"    int edad;\n")
            f.write(f"}} Create{cap}Dto;\n")
            f.write(f"char* Create{cap}Dto_to_json(Create{cap}Dto* dto);\n\n")
            
            f.write(f"// @DTO: Update{cap}Dto\n")
            f.write(f"// @Field: nombre (Type: String, Min: 2, Max: 50, Optional)\n")
            f.write(f"// @Field: edad (Type: Int, Min: 18, Optional)\n")
            f.write(f"typedef struct {{\n")
            f.write(f"    char* nombre;\n")
            f.write(f"    int edad;\n")
            f.write(f"}} Update{cap}Dto;\n")
            f.write(f"char* Update{cap}Dto_to_json(Update{cap}Dto* dto);\n\n")
            
            f.write(f"#endif\n")

    click.echo(f"\n{Colors.GREEN}CREATE{Colors.END} {cap}Service ({name}.service.c)")
    if not is_microservice: click.echo(f"{Colors.GREEN}CREATE{Colors.END} {cap}Controller ({name}.controller.c)")
    click.echo(f"{Colors.GREEN}CREATE{Colors.END} {cap}Module ({name}.module.c)")
    if crud: click.echo(f"{Colors.GREEN}CREATE{Colors.END} {cap}Dto (dto/{name}.dto.c)")