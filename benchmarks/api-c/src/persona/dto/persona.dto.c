#ifndef PERSONA_DTO_H
#define PERSONA_DTO_H

// @DTO: CreatePersonaDto
// @Field: nombre (Type: String, Min: 2, Max: 50)
// @Field: edad (Type: Int, Min: 18)
// @Field: email (Type: Email)
// @Field: isActive (Type: Bool)
// @Field: rol      (Type: Enum, Values: admin|user|guest)
// @Field: telefono (Type: Phone, Optional)
typedef struct {
    char* nombre;
    int edad;
    char* email;
    int isActive;
    char* rol;
    char* telefono;
} CreatePersonaDto;
char* CreatePersonaDto_to_json(CreatePersonaDto* dto);

// @DTO: UpdatePersonaDto
// @Field: nombre (Type: String, Min: 2, Max: 50, Optional)
// @Field: edad (Type: Int, Min: 18, Optional)
// @Field: email (Type: Email, Optional)
// @Field: isActive (Type: Bool, Optional)
// @Field: rol      (Type: Enum, Values: admin|user|guest, Optional)
// @Field: telefono (Type: Phone, Optional)
typedef struct {
    char* nombre;
    int edad;
    char* email;
    int isActive;
    char* rol;
    char* telefono;
} UpdatePersonaDto;
char* UpdatePersonaDto_to_json(UpdatePersonaDto* dto);

#endif
