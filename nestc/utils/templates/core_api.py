NC_JSON_CONTENT = """// Nest-C JSON Builder & Ergonomic API
#ifndef NC_JSON_H
#define NC_JSON_H

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "@nestcore/frozen.h"

#define NC_JSON_MAX_SIZE 8192

// ==========================================
// OPCIÓN 2: Builder Fluent (Para condicionales)
// ==========================================
typedef struct {
    char   buf[NC_JSON_MAX_SIZE];
    int    len;
    int    first_field;
} NcJson;

static inline NcJson nc_obj() {
    NcJson j; j.buf[0] = '{'; j.len = 1; j.first_field = 1; return j;
}

static inline void nc_str(NcJson* j, const char* key, const char* val) {
    if (!j->first_field) j->buf[j->len++] = ',';
    j->first_field = 0;
    j->len += snprintf(j->buf + j->len, NC_JSON_MAX_SIZE - j->len, "\\"%s\\":\\"%s\\"", key, val ? val : "");
}

static inline void nc_int(NcJson* j, const char* key, int val) {
    if (!j->first_field) j->buf[j->len++] = ',';
    j->first_field = 0;
    j->len += snprintf(j->buf + j->len, NC_JSON_MAX_SIZE - j->len, "\\"%s\\":%d", key, val);
}

static inline void nc_bool(NcJson* j, const char* key, int val) {
    if (!j->first_field) j->buf[j->len++] = ',';
    j->first_field = 0;
    j->len += snprintf(j->buf + j->len, NC_JSON_MAX_SIZE - j->len, "\\"%s\\":%s", key, val ? "true" : "false");
}

static inline void nc_null(NcJson* j, const char* key) {
    if (!j->first_field) j->buf[j->len++] = ',';
    j->first_field = 0;
    j->len += snprintf(j->buf + j->len, NC_JSON_MAX_SIZE - j->len, "\\"%s\\":null", key);
}

static inline char* nc_build(NcJson* j) {
    if (j->len < NC_JSON_MAX_SIZE - 1) { j->buf[j->len++] = '}'; j->buf[j->len] = '\\0'; }
    return strdup(j->buf);
}

// ==========================================
// OPCIÓN 3: Macros Variádicas (Sintaxis JS)
// ==========================================
typedef enum { _NC_STR, _NC_INT, _NC_BOOL, _NC_NULL } _NcType;

typedef struct {
    const char* key;
    _NcType     type;
    const char* sval;
    int         ival;
} _NcField;

#define NC_STR(k, v)  (_NcField){(k), _NC_STR,  (v),   0}
#define NC_INT(k, v)  (_NcField){(k), _NC_INT,  NULL,  (v)}
#define NC_BOOL(k, v) (_NcField){(k), _NC_BOOL, NULL,  (v)}
#define NC_NULL(k)    (_NcField){(k), _NC_NULL, NULL,  0}

#define NESTC_OBJ(...) _nc_build_obj((_NcField[]){__VA_ARGS__, {NULL}})

static inline char* _nc_build_obj(_NcField* fields) {
    char buf[NC_JSON_MAX_SIZE] = "{";
    int  len = 1;
    int  first = 1;
    for (int i = 0; fields[i].key != NULL; i++) {
        if (!first) buf[len++] = ',';
        first = 0;
        switch (fields[i].type) {
            case _NC_STR:
                len += snprintf(buf + len, sizeof(buf) - len, "\\"%s\\":\\"%s\\"", fields[i].key, fields[i].sval ? fields[i].sval : "");
                break;
            case _NC_INT:
                len += snprintf(buf + len, sizeof(buf) - len, "\\"%s\\":%d", fields[i].key, fields[i].ival);
                break;
            case _NC_BOOL:
                len += snprintf(buf + len, sizeof(buf) - len, "\\"%s\\":%s", fields[i].key, fields[i].ival ? "true" : "false");
                break;
            case _NC_NULL:
                len += snprintf(buf + len, sizeof(buf) - len, "\\"%s\\":null", fields[i].key);
                break;
        }
    }
    if (len < (int)sizeof(buf) - 1) { buf[len++] = '}'; buf[len] = '\\0'; }
    return strdup(buf);
}

// ==========================================
// UTILIDAD: Deserializadores manuales
// ==========================================
static inline char* nc_get_str(const char* json, const char* key) {
    char* out = NULL; char fmt[64];
    snprintf(fmt, sizeof(fmt), "{%s: %%Q}", key);
    json_scanf(json, strlen(json), fmt, &out);
    return out; 
}

static inline int nc_get_int(const char* json, const char* key, int fallback) {
    int out = fallback; char fmt[64];
    snprintf(fmt, sizeof(fmt), "{%s: %%d}", key);
    json_scanf(json, strlen(json), fmt, &out);
    return out;
}
#endif
"""

NEST_CORE_H_CONTENT = """// Nest-C Public API
#ifndef NEST_CORE_H
#define NEST_CORE_H

#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#include "@nestcore/nc_json.h"

// --- Nest-C Global Utils ---
// Macro para empaquetar JSON de forma segura y transferir su propiedad al Router
#define NESTC_JSON(str) strdup(str)

// --- Nest-C Logger ---
#define NC_LOG(ctx, fmt, ...)     printf("\\x1b[35m[Nest-C]\\x1b[0m \\x1b[32mLOG\\x1b[0m \\x1b[33m[%s]\\x1b[0m \\x1b[32m" fmt "\\x1b[0m\\n", ctx, ##__VA_ARGS__)
#define NC_INFO(ctx, fmt, ...)    printf("\\x1b[35m[Nest-C]\\x1b[0m \\x1b[36mINFO\\x1b[0m \\x1b[33m[%s]\\x1b[0m \\x1b[36m" fmt "\\x1b[0m\\n", ctx, ##__VA_ARGS__)
#define NC_SUCCESS(ctx, fmt, ...) printf("\\x1b[35m[Nest-C]\\x1b[0m \\x1b[32mSUCCESS\\x1b[0m \\x1b[33m[%s]\\x1b[0m \\x1b[32m" fmt "\\x1b[0m\\n", ctx, ##__VA_ARGS__)
#define NC_WARN(ctx, fmt, ...)    printf("\\x1b[35m[Nest-C]\\x1b[0m \\x1b[33mWARN\\x1b[0m \\x1b[33m[%s]\\x1b[0m \\x1b[33m" fmt "\\x1b[0m\\n", ctx, ##__VA_ARGS__)
#define NC_ERROR(ctx, fmt, ...)   printf("\\x1b[35m[Nest-C]\\x1b[0m \\x1b[31mERROR\\x1b[0m \\x1b[33m[%s]\\x1b[0m \\x1b[31m" fmt "\\x1b[0m\\n", ctx, ##__VA_ARGS__)

// --- Nest-C Response System ---
// Encapsula el resultado de un handler: status HTTP + body JSON.
// OWNERSHIP: El campo `body` es heap-allocated. El router llama free() automáticamente.
typedef struct {
    int   status;
    char* body;
} NestResponse;

// Macros de conveniencia — usan strdup para garantizar heap ownership
#define NESTC_OK(json)           ((NestResponse){200, strdup(json)})
#define NESTC_CREATED(json)      ((NestResponse){201, strdup(json)})
#define NESTC_BAD_REQUEST(json)  ((NestResponse){400, strdup(json)})
#define NESTC_NOT_FOUND(json)    ((NestResponse){404, strdup(json)})
#define NESTC_ERROR(json)        ((NestResponse){500, strdup(json)})

#define NESTC_NO_CONTENT()       ((NestResponse){204, strdup("")})
#define NESTC_UNAUTHORIZED(json) ((NestResponse){401, strdup(json)})
#define NESTC_FORBIDDEN(json)    ((NestResponse){403, strdup(json)})
#define NESTC_CONFLICT(json)     ((NestResponse){409, strdup(json)})

// --- Macros que TOMAN OWNERSHIP (para heap strings del service) ---
// El puntero que entras es el que el router va a liberar. No hay copia.
#define NESTC_OK_T(heap_json)      ((NestResponse){200, (heap_json)})
#define NESTC_CREATED_T(heap_json) ((NestResponse){201, (heap_json)})
#define NESTC_OK_CODE(code, heap_json) ((NestResponse){(code), (heap_json)})

// Macro de bajo nivel para status codes arbitrarios
#define NESTC_REPLY(code, json)  ((NestResponse){code, strdup(json)})

typedef struct {
    int port;
    int enable_cors;
    int payload_limit_mb;
} NestApp;

NestApp NestFactory_create();
void NestFactory_listen(NestApp *app);

#endif
"""

JSON_UTILS_CONTENT = """// Nest-C Generated Utility
#ifndef JSON_UTILS_H
#define JSON_UTILS_H

#include <string.h>
#include "@nestcore/frozen.h" 

#define JSON_GET_STR(json, path, dest, size) \\
    json_scanf(json, strlen(json), path, (int)size, dest)

#define JSON_GET_INT(json, path, dest) \\
    json_scanf(json, strlen(json), path, dest)

#endif
"""

ENV_UTILS_CONTENT = """// Nest-C DotEnv Loader
#ifndef ENV_UTILS_H
#define ENV_UTILS_H

#include <stdio.h>
#include <stdlib.h>
#include <string.h>

static inline void load_env(const char *filename) {
    FILE *file = fopen(filename, "r");
    if (!file) return;

    char line[256];
    while (fgets(line, sizeof(line), file)) {
        if (line[0] == '#' || line[0] == '\\n' || line[0] == '\\r') continue;

        char *eq = strchr(line, '=');
        if (eq) {
            *eq = '\\0';
            char *key = line;
            char *val = eq + 1;
            val[strcspn(val, "\\r\\n")] = 0;
            setenv(key, val, 1); 
        }
    }
    fclose(file);
}

#endif
"""