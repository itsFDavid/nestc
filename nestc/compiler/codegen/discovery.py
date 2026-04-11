import os
import re

def generate_services_discovery(src_dir, output_h):
    """Extrae los typedef struct de los .service.c para que el compilador conozca los tipos."""
    with open(output_h, "w") as out:
        out.write("/* DEFINICIONES DE SERVICIOS GENERADAS AUTOMATICAMENTE */\n")
        out.write("#ifndef SERVICES_DISCOVERY_H\n#define SERVICES_DISCOVERY_H\n\n")
        out.write("/* MACROS DEL FRAMEWORK */\n")
        out.write("#define NESTC_JSON(str) strdup(str)\n\n")
        
        for root, _, files in os.walk(src_dir):
            for file in files:
                if file.endswith(".service.c"):
                    with open(os.path.join(root, file), "r") as f:
                        content = f.read()
                        # Extrae el bloque typedef struct completo
                        structs = re.findall(r"typedef struct\s*\{.*?\}.*?;", content, re.DOTALL)
                        for s in structs:
                            out.write(s + "\n\n")
                            
        out.write("#endif // SERVICES_DISCOVERY_H\n")