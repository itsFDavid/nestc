MAIN_TEMPLATE = """#include "@nestcore/nest_core.h" 
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

APP_SERVICE = """#include "@nestcore/nest_core.h"

// @Service: AppService
typedef struct {
    char* (*get_hello)(); 
} AppService;

char* app_hello_logic() {
    return NESTC_OBJ(
        NC_STR("message", "Hola desde el motor OOP de Nest-C!"),
        NC_INT("status", 200)
    );
}
"""

APP_CONTROLLER = """#include "app.service.c"

// @Controller: /
// @Inject: AppService
NestResponse get_hello_handler(AppService* service) {
    if (!service) return NESTC_ERROR("{\\\"error\\\": \\\"Servicio no inyectado\\\"}");
    return NESTC_OK_T(service->get_hello());
}
"""

APP_MODULE = """#include "app.controller.c"

// @Init: AppService
void* init_app_service() {
    AppService* s = malloc(sizeof(AppService));
    if (!s) return NULL; // Protección OOM
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