#include "@nestcore/nest_core.h"
#include "dto/persona.dto.c"
#include "@nestcore/uuid.c"

#define MAX_PERSONAS 100000

typedef struct {
    char* id;
    char* nombre;
    int edad;
    char* email;
    int isActive;
    char* rol;
    char* telefono;
} Persona;

// Variable global estática para simular la base de datos en memoria del servicio
static Persona bd_personas[MAX_PERSONAS];
static int total_personas = 0;

// @Service: PersonaService
typedef struct PersonaService {
    // Métodos del servicio
    char* (*find_all)();
    char* (*find_one)(const char* id);
    char* (*create)(CreatePersonaDto* dto);
    char* (*update)(const char* id, UpdatePersonaDto* dto);
    char* (*remove)(const char* id);
} PersonaService;

char* persona_logic_all() {
    // Calcular tamaño necesario dinámicamente
    // ~300 bytes por persona + overhead del array
    int buffer_size = (total_personas * 300) + 64;
    if (buffer_size < 1024) buffer_size = 1024;

    char* json_array = malloc(buffer_size);
    if (!json_array) return strdup("[]");

    int written = 1;
    json_array[0] = '[';
    json_array[1] = '\0';

    for (int i = 0; i < total_personas; i++) {
        NcJson j = nc_obj();
        nc_str(&j, "id",       bd_personas[i].id);
        nc_str(&j, "nombre",   bd_personas[i].nombre);
        nc_int(&j, "edad",     bd_personas[i].edad);
        nc_str(&j, "email",    bd_personas[i].email);
        nc_bool(&j, "isActive",bd_personas[i].isActive);
        nc_str(&j, "rol",      bd_personas[i].rol);
        nc_str(&j, "telefono", bd_personas[i].telefono);

        char* obj = nc_build(&j);
        int obj_len = strlen(obj);

        // Verificar que cabe antes de escribir
        if (written + obj_len + 3 >= buffer_size) {
            // Crecer el buffer
            buffer_size = buffer_size * 2 + obj_len;
            char* new_buf = realloc(json_array, buffer_size);
            if (!new_buf) { free(obj); free(json_array); return strdup("[]"); }
            json_array = new_buf;
        }

        if (i > 0) { json_array[written++] = ','; json_array[written] = '\0'; }
        memcpy(json_array + written, obj, obj_len + 1);
        written += obj_len;
        free(obj);
    }

    json_array[written++] = ']';
    json_array[written]   = '\0';
    return json_array;
}

char* persona_logic_one(const char* id) {
    for (int i = 0; i < total_personas; i++) {
        if (strcmp(bd_personas[i].id, id) == 0) {
            return NESTC_OBJ(
                NC_STR("id", bd_personas[i].id),
                NC_STR("nombre", bd_personas[i].nombre),
                NC_INT("edad", bd_personas[i].edad),
                NC_STR("email", bd_personas[i].email),
                NC_BOOL("isActive", bd_personas[i].isActive),
                NC_STR("rol", bd_personas[i].rol),
                NC_STR("telefono", bd_personas[i].telefono)
            );
        }
    }

    return NESTC_OBJ(NC_STR("error", "Persona no encontrada"));
}

char* persona_logic_create(CreatePersonaDto* dto) {
    if (total_personas >= MAX_PERSONAS) {
        return NESTC_OBJ(NC_STR("error", "Límite de memoria alcanzado"));
    }

    Persona nueva_persona;
    
    nueva_persona.id = malloc(32);
    generate_mock_uuid(nueva_persona.id);
    
    nueva_persona.nombre = strdup(dto->nombre);
    nueva_persona.edad = dto->edad;
    nueva_persona.email = strdup(dto->email);
    nueva_persona.isActive = 1; 
    nueva_persona.rol = strdup(dto->rol);
    nueva_persona.telefono = strdup(dto->telefono);

    bd_personas[total_personas] = nueva_persona;
    total_personas++;

    return NESTC_OBJ(
        NC_STR("status", "created"),
        NC_STR("id", nueva_persona.id),
        NC_STR("nombre", nueva_persona.nombre),
        NC_INT("edad", nueva_persona.edad),
        NC_STR("email", nueva_persona.email),
        NC_BOOL("isActive", nueva_persona.isActive),
        NC_STR("rol", nueva_persona.rol),
        NC_STR("telefono", nueva_persona.telefono)
    );
}

char* persona_logic_update(const char* id, UpdatePersonaDto* dto) {
    for (int i = 0; i < total_personas; i++) {
        if (strcmp(bd_personas[i].id, id) == 0) {
            if (dto->nombre) {
                free(bd_personas[i].nombre);
                bd_personas[i].nombre = strdup(dto->nombre);
            }
            if (dto->edad != -2147483648) {
                bd_personas[i].edad = dto->edad;
            }
            if (dto->email) {
                free(bd_personas[i].email);
                bd_personas[i].email = strdup(dto->email);
            }
            if (dto->isActive != -1) { 
                bd_personas[i].isActive = dto->isActive;
            }
            if (dto->rol) {
                free(bd_personas[i].rol);
                bd_personas[i].rol = strdup(dto->rol);
            }
            if (dto->telefono) {
                free(bd_personas[i].telefono);
                bd_personas[i].telefono = strdup(dto->telefono);
            }

            return NESTC_OBJ(
                NC_STR("status", "updated"),
                NC_STR("id", bd_personas[i].id),
                NC_STR("nombre", bd_personas[i].nombre),
                NC_INT("edad", bd_personas[i].edad),
                NC_STR("email", bd_personas[i].email),
                NC_BOOL("isActive", bd_personas[i].isActive),
                NC_STR("rol", bd_personas[i].rol),
                NC_STR("telefono", bd_personas[i].telefono)
            );
        }
    }

    return NESTC_OBJ(NC_STR("error", "Persona no encontrada"));
}

char* persona_logic_remove(const char* id) {
    for (int i = 0; i < total_personas; i++) {
        if (strcmp(bd_personas[i].id, id) == 0) {
            free(bd_personas[i].id);
            free(bd_personas[i].nombre);
            free(bd_personas[i].email);
            free(bd_personas[i].rol);
            free(bd_personas[i].telefono);
            
            for (int j = i; j < total_personas - 1; j++) {
                bd_personas[j] = bd_personas[j + 1];
            }
            total_personas--;
            
            return NESTC_OBJ(NC_STR("action", "removed"), NC_STR("id", id));
        }
    }

    return NESTC_OBJ(NC_STR("error", "Persona no encontrada"));
}