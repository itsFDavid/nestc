#include "@nestcore/nest_core.h"

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
