import os
import re

def generate_services_discovery(src_dir, output_h):
    """Extrae los typedef struct de los .service.c para que el compilador conozca los tipos."""
    with open(output_h, "w") as out:
        out.write("/* DEFINICIONES DE SERVICIOS GENERADAS AUTOMATICAMENTE */\n")
        out.write("#ifndef SERVICES_DISCOVERY_H\n#define SERVICES_DISCOVERY_H\n\n")
        
        # Agregamos includes básicos necesarios para que el struct compile
        out.write("#include <stdlib.h>\n")
        out.write("#include <stdbool.h>\n")
        out.write("#include \"dto_validators.gen.h\"\n\n") # Para que reconozca los DTOs en el struct
        
        for root, _, files in os.walk(src_dir):
            for file in files:
                if file.endswith(".service.c"):
                    with open(os.path.join(root, file), "r") as f:
                        content = f.read()

                        # 1. Extraer los #define (para constantes de rutas, etc.)
                        defines = re.findall(r"#define\s+\w+\s+\d+", content)
                        for d in defines:
                            out.write(d + "\n")
                        
                        out.write("\n") # Espacio extra tras los defines

                        # 2. Extraer los typedef struct
                        # Regex mejorado para capturar el struct completo con nombre
                        structs = re.findall(r"typedef struct\s*\w*\s*\{.*?\}.*?;", content, re.DOTALL)
                        for s in structs:
                            out.write(s + "\n\n")
                            
        out.write("#endif // SERVICES_DISCOVERY_H\n")