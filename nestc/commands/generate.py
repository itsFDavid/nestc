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
        f.write("#include <stdio.h>\n#include <string.h>\n")
        f.write("#ifndef NESTC_JSON\n#define NESTC_JSON(str) strdup(str)\n#endif\n\n")
        
        f.write(f"// @Service: {cap}Service\ntypedef struct {{\n")
        if crud:
            f.write("    char* (*find_all)();\n")
            f.write("    char* (*find_one)(const char* id);\n")
            f.write("    char* (*create)(const char* body);\n")
            f.write("    char* (*update)(const char* id, const char* body);\n")
            f.write("    char* (*remove)(const char* id);\n")
        else:
            f.write("    char* (*do_something)();\n")
        f.write(f"}} {cap}Service;\n\n")

        if crud:
            f.write(f'char* {name}_logic_all() {{\n    return NESTC_JSON("{{\\\"res\\\": \\\"{name}\\\"}}");\n}}\n\n')
            
            f.write(f'char* {name}_logic_one(const char* id) {{\n')
            f.write(f'    char buffer[256];\n')
            f.write(f'    snprintf(buffer, sizeof(buffer), "{{\\\"id\\\": \\\"%s\\\"}}", id);\n')
            f.write(f'    return NESTC_JSON(buffer);\n}}\n\n')
            
            f.write(f'char* {name}_logic_create(const char* body) {{\n')
            f.write(f'    char buffer[1024];\n')
            f.write(f'    snprintf(buffer, sizeof(buffer), "{{\\\"action\\\": \\\"created\\\", \\\"payload\\\": %s}}", body[0] ? body : "{{\\"empty\\\":true}}");\n')
            f.write(f'    return NESTC_JSON(buffer);\n}}\n\n')
            
            f.write(f'char* {name}_logic_update(const char* id, const char* body) {{\n')
            f.write(f'    char buffer[1024];\n')
            f.write(f'    snprintf(buffer, sizeof(buffer), "{{\\\"action\\\": \\\"updated\\\", \\\"id\\\": \\\"%s\\\", \\\"payload\\\": %s}}", id, body[0] ? body : "{{\\"empty\\\":true}}");\n')
            f.write(f'    return NESTC_JSON(buffer);\n}}\n\n')
            
            f.write(f'char* {name}_logic_remove(const char* id) {{\n')
            f.write(f'    char buffer[256];\n')
            f.write(f'    snprintf(buffer, sizeof(buffer), "{{\\\"action\\\": \\\"removed\\\", \\\"id\\\": \\\"%s\\\"}}", id);\n')
            f.write(f'    return NESTC_JSON(buffer);\n}}\n')
        else:
            f.write(f'char* {name}_logic_something() {{\n    return NESTC_JSON("{{\\\"action\\\": \\\"{name} service executed\\\"}}");\n}}\n')

    # 2. GENERAR CONTROLLER
    if not is_microservice:
        with open(os.path.join(res_dir, f"{name}.controller.c"), "w") as f:
            f.write(f"// Controlador para {name}\n")
            f.write(f'#include "{name}.service.c"\n\n')
            
            if crud:
                for method, (http, route) in CRUD_METHODS.items():
                    parsed_route = route.replace("{name}", name)
                    f.write(f"// @{http}: {parsed_route}\n// @Inject: {cap}Service\n")
                    
                    args = [f"{cap}Service* s"]
                    if "/:id" in parsed_route: args.append("const char* id")
                    if http in ["POST", "PUT", "PATCH"]: args.append("const char* body")
                    
                    call_args = []
                    if "/:id" in parsed_route: call_args.append("id")
                    if http in ["POST", "PUT", "PATCH"]: call_args.append("body")
                    
                    f.write(f"char* {name}_{method}_handler({', '.join(args)}) {{\n")
                    f.write(f"    return s->{method}({', '.join(call_args)});\n}}\n\n")
            else:
                f.write(f"// @GET: /{name}\n// @Inject: {cap}Service\n")
                f.write(f"char* {name}_find_all_handler({cap}Service* s) {{\n")
                f.write(f"    return s->do_something();\n}}\n")

    # 3. GENERAR MÓDULO
    with open(os.path.join(res_dir, f"{name}.module.c"), "w") as f:
        f.write(f'#include <stdio.h>\n#include <stdlib.h>\n')
        f.write(f'#include "{name}.service.c"\n\n' if is_microservice else f'#include "{name}.controller.c"\n\n')

        f.write(f"// @Init: {cap}Service\nvoid* init_{name}_service() {{\n")
        f.write(f"    {cap}Service* s = malloc(sizeof({cap}Service));\n")
        
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

    click.echo(f"\n{Colors.GREEN}CREATE{Colors.END} {cap}Service ({name}.service.c)")
    if not is_microservice: click.echo(f"{Colors.GREEN}CREATE{Colors.END} {cap}Controller ({name}.controller.c)")
    click.echo(f"{Colors.GREEN}CREATE{Colors.END} {cap}Module ({name}.module.c)")