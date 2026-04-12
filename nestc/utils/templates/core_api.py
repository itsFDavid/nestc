
NEST_CORE_H_CONTENT = """// Nest-C Public API
#ifndef NEST_CORE_H
#define NEST_CORE_H

#include <stdio.h>

// --- Nest-C Logger ---
#define NC_LOG(ctx, fmt, ...)     printf("\\x1b[35m[Nest-C]\\x1b[0m \\x1b[32mLOG\\x1b[0m \\x1b[33m[%s]\\x1b[0m \\x1b[32m" fmt "\\x1b[0m\\n", ctx, ##__VA_ARGS__)
#define NC_INFO(ctx, fmt, ...)    printf("\\x1b[35m[Nest-C]\\x1b[0m \\x1b[36mINFO\\x1b[0m \\x1b[33m[%s]\\x1b[0m \\x1b[36m" fmt "\\x1b[0m\\n", ctx, ##__VA_ARGS__)
#define NC_SUCCESS(ctx, fmt, ...) printf("\\x1b[35m[Nest-C]\\x1b[0m \\x1b[32mSUCCESS\\x1b[0m \\x1b[33m[%s]\\x1b[0m \\x1b[32m" fmt "\\x1b[0m\\n", ctx, ##__VA_ARGS__)
#define NC_WARN(ctx, fmt, ...)    printf("\\x1b[35m[Nest-C]\\x1b[0m \\x1b[33mWARN\\x1b[0m \\x1b[33m[%s]\\x1b[0m \\x1b[33m" fmt "\\x1b[0m\\n", ctx, ##__VA_ARGS__)
#define NC_ERROR(ctx, fmt, ...)   printf("\\x1b[35m[Nest-C]\\x1b[0m \\x1b[31mERROR\\x1b[0m \\x1b[33m[%s]\\x1b[0m \\x1b[31m" fmt "\\x1b[0m\\n", ctx, ##__VA_ARGS__)

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