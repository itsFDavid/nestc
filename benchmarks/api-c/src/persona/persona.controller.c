#include "persona.service.c"

// @GET: /persona
// @Inject: PersonaService
NestResponse persona_find_all_handler(PersonaService* s) {
    if (!s) return NESTC_ERROR("{\"error\": \"Service unavailable\"}");
    return NESTC_OK_T(s->find_all());
}

// @GET: /persona/:id
// @Inject: PersonaService
NestResponse persona_find_one_handler(PersonaService* s, const char* id) {
    if (!s) return NESTC_ERROR("{\"error\": \"Service unavailable\"}");
    return NESTC_OK_T(s->find_one(id));
}

// @POST: /persona
// @Inject: PersonaService
// @Body: CreatePersonaDto
NestResponse persona_create_handler(PersonaService* s, CreatePersonaDto* dto) {
    if (!s) return NESTC_ERROR("{\"error\": \"Service unavailable\"}");
    return NESTC_CREATED_T(s->create(dto));
}

// @PUT: /persona/:id
// @Inject: PersonaService
// @Body: UpdatePersonaDto
NestResponse persona_update_handler(PersonaService* s, const char* id, UpdatePersonaDto* dto) {
    if (!s) return NESTC_ERROR("{\"error\": \"Service unavailable\"}");
    return NESTC_OK_T(s->update(id, dto));
}

// @DELETE: /persona/:id
// @Inject: PersonaService
NestResponse persona_remove_handler(PersonaService* s, const char* id) {
    if (!s) return NESTC_ERROR("{\"error\": \"Service unavailable\"}");
    return NESTC_OK_T(s->remove(id));
}

