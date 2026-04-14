// Nest-C Generated Utility
#ifndef JSON_UTILS_H
#define JSON_UTILS_H

#include <string.h>
#include "@nestcore/frozen.h" 

#define JSON_GET_STR(json, path, dest, size) \
    json_scanf(json, strlen(json), path, (int)size, dest)

#define JSON_GET_INT(json, path, dest) \
    json_scanf(json, strlen(json), path, dest)

#endif
