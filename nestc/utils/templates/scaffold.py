
MAIN_TEMPLATE = """#include <stdio.h>
#include <stdlib.h>
#include "@nestcore/nest_core.h" 
#include "@nestcore/frozen.h" 

int main() {
    NestApp app = NestFactory_create();

    app.enable_cors = 1;
    app.payload_limit_mb = 5;

    char* env_port = getenv("PORT");
    app.port = env_port ? atoi(env_port) : 3000;

    NC_INFO("Bootstrap", "Configuración cargada en el puerto %d", app.port);
    NestFactory_listen(&app);

    return 0;
}
"""

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
#include "app.service.c"

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
#include "app.controller.c"

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