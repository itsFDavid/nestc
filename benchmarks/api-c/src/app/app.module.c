#include "app.controller.c"

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
