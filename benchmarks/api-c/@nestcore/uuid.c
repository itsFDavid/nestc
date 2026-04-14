#include <stdio.h>
#include <string.h>
#include <stdlib.h>

// Utilidad simple para generar un ID único
void generate_mock_uuid(char* buffer) {
    static int id_counter = 0;
    sprintf(buffer, "uuid-persona-%04d", ++id_counter);
}