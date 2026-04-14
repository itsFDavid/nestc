#include "app.service.c"

// @Controller: /
// @Inject: AppService
NestResponse get_hello_handler(AppService* service) {
    if (!service) return NESTC_ERROR("{\"error\": \"Servicio no inyectado\"}");
    return NESTC_OK_T(service->get_hello());
}
