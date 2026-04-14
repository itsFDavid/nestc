// Nest-C Public API
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
#define NC_LOG(ctx, fmt, ...)     printf("\x1b[35m[Nest-C]\x1b[0m \x1b[32mLOG\x1b[0m \x1b[33m[%s]\x1b[0m \x1b[32m" fmt "\x1b[0m\n", ctx, ##__VA_ARGS__)
#define NC_INFO(ctx, fmt, ...)    printf("\x1b[35m[Nest-C]\x1b[0m \x1b[36mINFO\x1b[0m \x1b[33m[%s]\x1b[0m \x1b[36m" fmt "\x1b[0m\n", ctx, ##__VA_ARGS__)
#define NC_SUCCESS(ctx, fmt, ...) printf("\x1b[35m[Nest-C]\x1b[0m \x1b[32mSUCCESS\x1b[0m \x1b[33m[%s]\x1b[0m \x1b[32m" fmt "\x1b[0m\n", ctx, ##__VA_ARGS__)
#define NC_WARN(ctx, fmt, ...)    printf("\x1b[35m[Nest-C]\x1b[0m \x1b[33mWARN\x1b[0m \x1b[33m[%s]\x1b[0m \x1b[33m" fmt "\x1b[0m\n", ctx, ##__VA_ARGS__)
#define NC_ERROR(ctx, fmt, ...)   printf("\x1b[35m[Nest-C]\x1b[0m \x1b[31mERROR\x1b[0m \x1b[33m[%s]\x1b[0m \x1b[31m" fmt "\x1b[0m\n", ctx, ##__VA_ARGS__)

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
