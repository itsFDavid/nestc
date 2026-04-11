import os
import click
from nestc.utils.colors import Colors

def create_project_structure(project_name):
    src_app = os.path.join(project_name, "src", "app")
    folders = [project_name, os.path.join(project_name, "src"), src_app, os.path.join(project_name, "build")]

    click.echo(f"{Colors.BOLD}Creando nuevo proyecto Nest-C: {Colors.BLUE}{project_name}{Colors.END}")

    for folder in folders:
        if not os.path.exists(folder):
            os.makedirs(folder)
            click.echo(f"  {Colors.GREEN}* {Colors.END}Carpeta creada: {folder}")

    # 1. Crear app.service.c (Cero dependencias locales)
    with open(os.path.join(src_app, "app.service.c"), "w") as f:
        f.write("""#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#ifndef NESTC_JSON
#define NESTC_JSON(str) strdup(str)
#endif

// @Service: AppService
typedef struct {
    char* (*get_hello)(); 
} AppService;

char* app_hello_logic() {
    return NESTC_JSON("{\\\"message\\\": \\\"Hola desde el motor OOP de Nest-C!\\\"}");
}
""")

    # 2. Crear app.controller.c (Incluye al Service)
    with open(os.path.join(src_app, "app.controller.c"), "w") as f:
        f.write("""#include <stdio.h>
#include "app.service.c" // Cadena de inclusion

// @Controller: /
// @Inject: AppService
char* get_hello_handler(AppService* service) {
    if (service != NULL) {
        return service->get_hello();
    }
    return NESTC_JSON("{\\\"error\\\": \\\"Servicio no inyectado\\\"}");
}
""")

    # 3. Crear app.module.c (Incluye al Controller)
    with open(os.path.join(src_app, "app.module.c"), "w") as f:
        f.write("""#include <stdio.h>
#include <stdlib.h>
#include "app.controller.c" // Controller ya incluye al Service

// @Init: AppService
void* init_app_service() {
    AppService* s = malloc(sizeof(AppService));
    s->get_hello = app_hello_logic;
    return s;
}

// @Destroy: AppService
void destroy_app_service(void* instance) {
    if (instance != NULL) free(instance);
}

// @Module: AppModule
void app_module_init() {}
""")

    with open(os.path.join(project_name, "src", "main.c"), "w") as f:
        f.write("// Este proyecto usa el Bootstrap automático de Nest-C.\\n")

    with open(os.path.join(project_name, "nestc-config.json"), "w") as f:
        f.write('{\n  "name": "' + project_name + '",\n  "version": "0.1.0",\n  "framework": "Nest-C"\n}')

    click.echo(f"\n{Colors.GREEN}{Colors.BOLD}Proyecto '{project_name}' inicializado. ¡Listo para devolver JSON!{Colors.END}")
    click.echo(f"Escribe: {Colors.YELLOW}cd {project_name} && nestc build{Colors.END}")