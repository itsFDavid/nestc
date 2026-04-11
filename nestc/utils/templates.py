APP_SERVICE = """#include <stdio.h>
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
"""

APP_CONTROLLER = """#include <stdio.h>
#include "app.service.c" // Cadena de inclusion

// @Controller: /
// @Inject: AppService
char* get_hello_handler(AppService* service) {
    if (service != NULL) {
        return service->get_hello();
    }
    return NESTC_JSON("{\\\"error\\\": \\\"Servicio no inyectado\\\"}");
}
"""
APP_MODULE = """#include <stdio.h>
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
"""