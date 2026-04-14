<div align="center">

```bash
███╗   ██╗███████╗███████╗████████╗      ██████╗
████╗  ██║██╔════╝██╔════╝╚══██╔══╝     ██╔════╝
██╔██╗ ██║█████╗  ███████╗   ██║   ████╗██║
██║╚██╗██║██╔══╝  ╚════██║   ██║   ╚═══╝██║
██║ ╚████║███████╗███████║   ██║        ╚██████╗
╚═╝  ╚═══╝╚══════╝╚══════╝   ╚═╝         ╚═════╝
```

**The performance of C. The Developer Experience of NestJS.**

[![License: MIT](https://img.shields.io/badge/License-MIT-violet.svg)](https://opensource.org/licenses/MIT)
[![Language: C](https://img.shields.io/badge/Language-C-blue.svg)](<https://en.wikipedia.org/wiki/C_(programming_language)>)
[![CLI: Python](https://img.shields.io/badge/CLI-Python-yellow.svg)](https://www.python.org/)
[![Author](https://img.shields.io/badge/Author-itsFDavid-red.svg)](https://github.com/itsFDavid)

</div>

---

## ¿Qué es Nest-C?

**Nest-C** es un framework de backend escrito en Python (CLI) que genera y transpila código nativo en C. Adopta la arquitectura de NestJS — con Services, Controllers y Modules — implementada mediante **decoradores en comentarios** y un **motor de inyección de dependencias** que el compilador resuelve en tiempo de build.

## Metricas y Rendimiento

Sin runtime, sin intérprete. El output es un binario nativo que responde peticiones HTTP en microsegundos.

En pruebas de estrés masivo (800 usuarios concurrentes), **Nest-C demostró procesar más de 1 millón de peticiones (CRUD completo) manteniendo una latencia máxima de 404ms**, superando abismalmente la resiliencia de frameworks basados en Node.js/V8.

**[Lee el reporte de benchmark completo (Nest-C vs NestJS) aquí](./benchmarks/README.md)**

```bash
  Tu código C con decoradores
          │
          ▼
  nestc build
  ┌─────────────────────────────────┐
  │  Parser Python  →  AST Visitor  │
  │  Codegen       →  Glue Code C   │
  │  GCC           →  Binario nativo│
  └─────────────────────────────────┘
          │
          ▼
  build/app  →  HTTP en :8080
```

---

## Instalación rápida

Instala el CLI de forma global con un solo comando:

```bash
curl -sSL https://raw.githubusercontent.com/itsFDavid/nestc/main/install.sh | bash
```

Luego verifica que tu entorno tenga las herramientas necesarias:

```bash
nestc doctor
```

`nestc doctor` revisa la existencia de **GCC**, **Git** y **Make**. Si falta alguna dependencia, el CLI ofrecerá instalarla automáticamente según tu sistema operativo (macOS o Linux).

---

## CLI — Comandos

| Comando                | Descripción                                                              |
| ---------------------- | ------------------------------------------------------------------------ |
| `nestc new <nombre>`   | Inicializa un nuevo proyecto con estructura base y dependencias core     |
| `nestc g res <nombre>` | Genera un recurso completo: Controller, Service, Module y DTOs           |
| `nestc build`          | Analiza decoradores, transpila el código y genera el binario en `build/` |
| `nestc start`          | Ejecuta el build y levanta el servidor inmediatamente                    |
| `nestc doctor`         | Diagnóstico del sistema y gestión de dependencias nativas                |

---

## Inicio rápido

```bash
# 1. Crear proyecto
nestc new mi-api && cd mi-api

# 2. Generar un recurso
nestc g res usuarios

# 3. Compilar y levantar el servidor
nestc start
```

Output esperado:

```
[Nest-C] LOG  [NestFactory]    Starting Nest-C application...
[Nest-C] LOG  [InstanceLoader] UsuariosService initialized
[Nest-C] LOG  [InstanceLoader] UsuariosModule loaded
[Nest-C] LOG  [RoutesResolver] Mapped {/usuarios, GET} route
[Nest-C] LOG  [RoutesResolver] Mapped {/usuarios/:id, GET} route
[Nest-C] LOG  [RoutesResolver] Mapped {/usuarios, POST} route
[Nest-C] LOG  [RoutesResolver] Mapped {/usuarios/:id, PUT} route
[Nest-C] LOG  [RoutesResolver] Mapped {/usuarios/:id, DELETE} route
[Nest-C] INFO [NestApplication] Listening at http://0.0.0.0:8080
```

---

## Arquitectura

Nest-C organiza cada recurso en tres capas desacopladas:

### 1. Service — Lógica de negocio

Define los métodos como punteros a función dentro de un `struct`, simulando comportamiento de clase:

```c
// @Service: UsuariosService
typedef struct {
    char* (*find_all)();
    char* (*find_one)(const char* id);
    char* (*create)(CreateUsuariosDto* dto);
    char* (*update)(const char* id, UpdateUsuariosDto* dto);
    char* (*remove)(const char* id);
} UsuariosService;
```

### 2. Controller — Rutas HTTP

Mapea rutas HTTP mediante decoradores en comentarios. `@Inject` recibe la instancia del servicio. `@Body` activa la validación automática del DTO antes de que llegue al handler:

```c
// @GET: /usuarios
// @Inject: UsuariosService
NestResponse usuarios_find_all_handler(UsuariosService* s) {
    if (!s) return NESTC_ERROR("{\"error\": \"Service unavailable\"}");
    return NESTC_OK_T(s->find_all());
}

// @POST: /usuarios
// @Inject: UsuariosService
// @Body: CreateUsuariosDto
NestResponse usuarios_create_handler(UsuariosService* s, CreateUsuariosDto* dto) {
    if (!s) return NESTC_ERROR("{\"error\": \"Service unavailable\"}");
    return NESTC_CREATED_T(s->create(dto));
}
```

### 3. Module — Ciclo de vida

Controla la inicialización y destrucción del servicio. `@Init` reserva memoria con `malloc` y `@Destroy` garantiza su liberación con `free`:

```c
// @Init: UsuariosService
void* init_usuarios_service() {
    UsuariosService* s = malloc(sizeof(UsuariosService));
    if (!s) return NULL;
    s->find_all = usuarios_logic_all;
    s->create   = usuarios_logic_create;
    return s;
}

// @Destroy: UsuariosService
void destroy_usuarios_service(void* s) {
    if (s) free(s);
}

// @Module: UsuariosModule
void usuarios_module_init() {}
```

### 4. DTO — Validación de datos

Los DTOs definen esquemas con reglas declaradas en comentarios. El compilador los transforma en código C de validación real antes de que el request llegue al handler:

```c
// @DTO: CreateUsuariosDto
// @Field: nombre   (Type: String, Min: 2, Max: 50)
// @Field: email    (Type: Email)
// @Field: edad     (Type: Int, Min: 18, Max: 120)
// @Field: rol      (Type: Enum, Values: admin|user|guest)
// @Field: telefono (Type: Phone, Optional)
typedef struct {
    char* nombre;
    char* email;
    int   edad;
    char* rol;
    char* telefono;
} CreateUsuariosDto;
```

Errores de validación automáticos:

```bash
curl -X POST http://localhost:8080/usuarios \
  -H "Content-Type: application/json" \
  -d '{"nombre": "A", "email": "no-es-email", "edad": 15, "rol": "superadmin"}'

# Respuesta:
{"error": "Bad Request", "message": "Field 'nombre' must be at least 2 characters."}
```

---

## Sistema de respuestas — `NestResponse`

Todos los handlers retornan `NestResponse`, una estructura que encapsula el status HTTP y el body JSON. El router libera la memoria automáticamente:

```c
// Macros que copian el string (para literales):
NESTC_OK(json)           // 200
NESTC_CREATED(json)      // 201
NESTC_BAD_REQUEST(json)  // 400
NESTC_NOT_FOUND(json)    // 404
NESTC_ERROR(json)        // 500

// Macros de transferencia de ownership (para heap strings del service):
NESTC_OK_T(heap_json)      // 200 — sin copia extra
NESTC_CREATED_T(heap_json) // 201 — sin copia extra
```

---

## Tipos de campo en DTOs

| Tipo       | Descripción                    | Reglas disponibles       |
| ---------- | ------------------------------ | ------------------------ |
| `String`   | Cadena de texto                | `Min`, `Max`, `Optional` |
| `Int`      | Entero                         | `Min`, `Max`, `Optional` |
| `Float`    | Número decimal                 | `Min`, `Max`, `Optional` |
| `Bool`     | Booleano (`true`/`false`)      | `Optional`               |
| `Email`    | Dirección de correo válida     | `Optional`               |
| `URL`      | URL con `http://` o `https://` | `Optional`               |
| `UUID`     | UUID en formato estándar       | `Optional`               |
| `Date`     | Fecha `YYYY-MM-DD`             | `Optional`               |
| `DateTime` | Fecha y hora ISO 8601          | `Optional`               |
| `Phone`    | Número telefónico              | `Min`, `Optional`        |
| `Enum`     | Valor de una lista fija        | `Values`, `Optional`     |

---

## Características técnicas

**Gestión de memoria** — El ciclo de vida de cada servicio está controlado por `@Init` y `@Destroy`. El router libera el body de cada respuesta automáticamente después de enviarla. Sin fugas de memoria en el happy path.

**Validación de tipos estricta** — Los DTOs verifican el tipo real del token JSON (usando `%T` de frozen) antes de extraer el valor. Un campo `Int` con valor `"texto"` o `3.14` es rechazado con un error descriptivo.

**Seguridad en el router** — El router generado incluye protección contra path traversal (`..`), límite de tamaño de payload configurable, y manejo de CORS con soporte a preflight `OPTIONS`.

**Alto rendimiento** — El output es un binario nativo compilado con GCC `-O2`. Sin VM, sin GC, sin overhead de runtime. Las latencias son del orden de microsegundos.

**Apagado elegante** — El framework captura `atexit` para ejecutar los destructores de todos los servicios registrados y cerrar los sockets de Mongoose ordenadamente.

---

## Dependencias

Nest-C descarga y gestiona sus dependencias automáticamente en la carpeta `@nestcore/`:

| Dependencia                                     | Versión | Uso                          |
| ----------------------------------------------- | ------- | ---------------------------- |
| [Mongoose](https://github.com/cesanta/mongoose) | 7.21    | Servidor HTTP embebido       |
| [Frozen](https://github.com/cesanta/frozen)     | latest  | Parsing y serialización JSON |

---

## Autor

**Francisco David Colin Lira**  
Computer Systems Engineering Student & RPA Developer

[![GitHub](https://img.shields.io/badge/GitHub-itsFDavid-181717?logo=github)](https://github.com/itsFDavid)

---

<div align="center">

_Nest-C — Backend de alto rendimiento, con la ergonomía que mereces._

</div>
