#include "persona.controller.c"

// @Init: PersonaService
void* init_persona_service() {
    PersonaService* s = malloc(sizeof(PersonaService));
    if (!s) return NULL;
    s->find_all = persona_logic_all;
    s->find_one = persona_logic_one;
    s->create = persona_logic_create;
    s->update = persona_logic_update;
    s->remove = persona_logic_remove;
    return s;
}

// @Destroy: PersonaService
void destroy_persona_service(void* s) {
    if (s) {
        // Limpiar las entidades que quedaron en memoria
        for (int i = 0; i < total_personas; i++) {
            free(bd_personas[i].id);
            free(bd_personas[i].nombre);
            free(bd_personas[i].email);
            free(bd_personas[i].rol);
            free(bd_personas[i].telefono);
        }
        free(s);
    }
}

// @Module: PersonaModule
void persona_module_init() {}
