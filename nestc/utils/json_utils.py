JSON_UTILS_CONTENT = """// Nest-C Generated Utility
#ifndef JSON_UTILS_H
#define JSON_UTILS_H

#include <string.h>
#include "../frozen.h"

/**
 * Macro para extraer un string de forma segura.
 * path: el patrón de búsqueda (ej: "{name: %s}")
 * size: tamaño máximo del buffer destino
 */
#define JSON_GET_STR(json, path, dest, size) \\
    json_scanf(json, strlen(json), path, (int)size, dest)

/**
 * Macro para extraer un entero.
 * path: el patrón de búsqueda (ej: "{id: %d}")
 */
#define JSON_GET_INT(json, path, dest) \\
    json_scanf(json, strlen(json), path, dest)

#endif
"""