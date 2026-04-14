// @nestcore/nc_validators.h
#ifndef NC_VALIDATORS_H
#define NC_VALIDATORS_H

#include <string.h>
#include <ctype.h>
#include <stdlib.h>

static inline int _nestc_validate_email(const char* s) {
    if (!s || !*s) return 0;
    const char* at = strchr(s, '@');
    if (!at || at == s || strchr(at + 1, '@')) return 0;
    const char* dot = strchr(at + 1, '.');
    if (!dot || *(dot + 1) == '\0') return 0; 
    return 1;
}

static inline int _nestc_validate_url(const char* s) {
    if (!s) return 0;
    if (strncmp(s, "http://", 7) == 0 && strlen(s) > 7) return 1;
    if (strncmp(s, "https://", 8) == 0 && strlen(s) > 8) return 1;
    return 0;
}

static inline int _nestc_validate_uuid(const char* s) {
    if (!s || strlen(s) != 36) return 0;
    if (s[8] != '-' || s[13] != '-' || s[18] != '-' || s[23] != '-') return 0;
    for (int i = 0; i < 36; i++) {
        if (i == 8 || i == 13 || i == 18 || i == 23) continue;
        if (!isxdigit((unsigned char)s[i])) return 0;
    }
    return 1;
}

// --- Date (YYYY-MM-DD) ---
static inline int _nestc_validate_date(const char* s) {
    if (!s || strlen(s) < 10) return 0; // Cambiado != 10 a < 10
    if (s[4] != '-' || s[7] != '-') return 0;
    for (int i = 0; i < 10; i++) {
        if (i == 4 || i == 7) continue;
        if (!isdigit((unsigned char)s[i])) return 0;
    }
    return 1;
}

// --- DateTime (ISO 8601: YYYY-MM-DDTHH:MM:SS) ---
static inline int _nestc_validate_datetime(const char* s) {
    if (!s || strlen(s) < 19) return 0;
    if (!_nestc_validate_date(s)) return 0; 
    if (s[10] != 'T') return 0;
    for (int i = 11; i < 19; i++) {
        if (i == 13 || i == 16) { if (s[i] != ':') return 0; continue; }
        if (!isdigit((unsigned char)s[i])) return 0;
    }
    int h = atoi(s + 11);
    int m = atoi(s + 14);
    int sec = atoi(s + 17);
    if (h > 23 || m > 59 || sec > 59) return 0;
    return 1;
}

static inline int _nestc_validate_phone(const char* s) {
    if (!s) return 0;
    int digit_count = 0;
    for (int i = 0; s[i]; i++) {
        if (isdigit((unsigned char)s[i])) { digit_count++; continue; }
        if (strchr("+- ()\\", s[i])) continue;
        return 0;
    }
    return digit_count >= 7;
}
#endif
