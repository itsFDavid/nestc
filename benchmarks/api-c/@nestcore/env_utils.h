// Nest-C DotEnv Loader
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
        if (line[0] == '#' || line[0] == '\n' || line[0] == '\r') continue;

        char *eq = strchr(line, '=');
        if (eq) {
            *eq = '\0';
            char *key = line;
            char *val = eq + 1;
            val[strcspn(val, "\r\n")] = 0;
            setenv(key, val, 1); 
        }
    }
    fclose(file);
}

#endif
