import os
import subprocess
import click
from nestc.compiler.parse import analyze_project
from nestc.compiler.codegen.bootstrap import generate_bootstrap_c
from nestc.utils.colors import Colors, NEST_C_LOGO
from nestc.utils.downloader import ensure_dependencies

def execute_build()->bool:
    click.echo(NEST_C_LOGO)
    click.echo(f"{Colors.BOLD}Iniciando build modular del proyecto...{Colors.END}")

    # 1. Aseguramos dependencias en la raíz (@nestcore)
    ensure_dependencies() 

    src_dir = "src"
    build_dir = "build"
    output_bin = os.path.join(build_dir, "app")

    if not os.path.exists(build_dir):
        os.makedirs(build_dir)

    # 2. Escaneo inteligente
    data = analyze_project(src_dir)

    # 3. Generar pegamento (Glue Code) y la API pública (nest_core.h)
    bootstrap_path = "build/main.gen.c"
    generate_bootstrap_c(data, bootstrap_path)

    # 4. Recolectar archivos para compilar
    c_files = set()
    for root, _, files in os.walk(src_dir):
        for f in files:
            if f.endswith(".module.c"):
                c_files.add(os.path.join(root, f))
            # CRÍTICO: Ahora SÍ compilamos el main.c del usuario
            if f == "main.c" and root == "src":
                c_files.add(os.path.join(root, f))

    c_files.add(bootstrap_path)
    # Cambiamos src por el alias de nuestra nueva arquitectura
    c_files.add("@nestcore/mongoose.c")
    c_files.add("@nestcore/frozen.c")

    # 5. Comando de compilación (Añadido -I. para el alias)
    compile_cmd = [
        "gcc",
        "-O2", 
        *list(c_files),
        "-o", "build/app",
        "-I.",
        "-Isrc",     
        "-Ibuild"    
    ]
    
    result = subprocess.run(compile_cmd)

    if result.returncode == 0:
        click.echo(f"\n{Colors.GREEN}{Colors.BOLD}Nest-C application successfully started{Colors.END}")
        click.echo(f"{Colors.YELLOW}[OK] {output_bin}{Colors.END}\n")
        return True
    else:
        click.echo(f"\n{Colors.RED}Falló la compilación de los módulos.{Colors.END}")
        return False