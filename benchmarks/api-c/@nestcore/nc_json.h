// Nest-C JSON Builder & Ergonomic API
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
    j->len += snprintf(j->buf + j->len, NC_JSON_MAX_SIZE - j->len, "\"%s\":\"%s\"", key, val ? val : "");
}

static inline void nc_int(NcJson* j, const char* key, int val) {
    if (!j->first_field) j->buf[j->len++] = ',';
    j->first_field = 0;
    j->len += snprintf(j->buf + j->len, NC_JSON_MAX_SIZE - j->len, "\"%s\":%d", key, val);
}

static inline void nc_bool(NcJson* j, const char* key, int val) {
    if (!j->first_field) j->buf[j->len++] = ',';
    j->first_field = 0;
    j->len += snprintf(j->buf + j->len, NC_JSON_MAX_SIZE - j->len, "\"%s\":%s", key, val ? "true" : "false");
}

static inline void nc_null(NcJson* j, const char* key) {
    if (!j->first_field) j->buf[j->len++] = ',';
    j->first_field = 0;
    j->len += snprintf(j->buf + j->len, NC_JSON_MAX_SIZE - j->len, "\"%s\":null", key);
}

static inline void nc_raw(NcJson* j, const char* key, const char* raw_json) {
    if (!j->first_field) j->buf[j->len++] = ',';
    j->first_field = 0;
    j->len += snprintf(j->buf + j->len, NC_JSON_MAX_SIZE - j->len, "\"%s\":%s", key, raw_json);
}

static inline char* nc_build(NcJson* j) {
    if (j->len < NC_JSON_MAX_SIZE - 1) { j->buf[j->len++] = '}'; j->buf[j->len] = '\0'; }
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
                len += snprintf(buf + len, sizeof(buf) - len, "\"%s\":\"%s\"", fields[i].key, fields[i].sval ? fields[i].sval : "");
                break;
            case _NC_INT:
                len += snprintf(buf + len, sizeof(buf) - len, "\"%s\":%d", fields[i].key, fields[i].ival);
                break;
            case _NC_BOOL:
                len += snprintf(buf + len, sizeof(buf) - len, "\"%s\":%s", fields[i].key, fields[i].ival ? "true" : "false");
                break;
            case _NC_NULL:
                len += snprintf(buf + len, sizeof(buf) - len, "\"%s\":null", fields[i].key);
                break;
        }
    }
    if (len < (int)sizeof(buf) - 1) { buf[len++] = '}'; buf[len] = '\0'; }
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

static inline int nc_get_bool(const char* json, const char* key, int fallback) {
    int out = fallback; char fmt[64];
    snprintf(fmt, sizeof(fmt), "{%s: %%B}", key);
    json_scanf(json, strlen(json), fmt, &out);
    return out;
}
#endif
