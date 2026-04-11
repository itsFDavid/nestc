import os
import subprocess
import click
import urllib.request
import sys
from nestc.compiler.parse import analyze_project
from nestc.compiler.codegen.bootstrap import generate_bootstrap_c
from nestc.utils.colors import Colors, NEST_C_LOGO

def execute_build()->bool:
    click.echo(NEST_C_LOGO)
    click.echo(f"{Colors.BOLD}Iniciando build modular del proyecto...{Colors.END}")

    src_dir = "src"
    ensure_mongoose_exists(src_dir)
    build_dir = "build"
    output_bin = os.path.join(build_dir, "app")

    if not os.path.exists(build_dir):
        os.makedirs(build_dir)

    # 1. Escaneo inteligente (Busca en todos los módulos/carpetas)
    data = analyze_project(src_dir)

    # 2. Generar pegamento (Glue Code)
    bootstrap_path = "build/main.gen.c"
    generate_bootstrap_c(data, bootstrap_path)

    # 3. Recolectar todos los archivos .c del src
    c_files = set()
    for root, _, files in os.walk(src_dir):
        for f in files:
            # IMPORTANTE: Solo compilamos los módulos. 
            # Services y Controllers entran al binario a través del #include del módulo.
            if f.endswith(".module.c"):
                c_files.add(os.path.join(root, f))

    c_files.add(bootstrap_path)
    c_files.add("src/mongoose.c")

    # GCC necesita saber dónde están los headers generados (-Ibuild)
    compile_cmd = ["gcc"] + list(c_files) + ["-o", "build/app", "-Isrc", "-Ibuild"]
    
    result = subprocess.run(compile_cmd)

    if result.returncode == 0:
        click.echo(f"\n{Colors.GREEN}{Colors.BOLD}Nest-C application successfully started{Colors.END}")
        click.echo(f"{Colors.YELLOW}[OK] {output_bin}{Colors.END}\n")
        return True
    else:
        click.echo(f"\n{Colors.RED}Falló la compilación de los módulos.{Colors.END}")
        return False


def ensure_mongoose_exists(src_dir):
    """Descarga mongoose.c y mongoose.h si no están presentes."""
    files = {
        "mongoose.c": "https://raw.githubusercontent.com/cesanta/mongoose/master/mongoose.c",
        "mongoose.h": "https://raw.githubusercontent.com/cesanta/mongoose/master/mongoose.h"
    }
    
    for filename, url in files.items():
        path = os.path.join(src_dir, filename)
        if not os.path.exists(path):
            click.echo(f"  {Colors.CYAN}↓{Colors.END} Descargando {filename} para el servidor HTTP...")
            try:
                urllib.request.urlretrieve(url, path)
            except Exception as e:
                click.echo(f"{Colors.RED}Error descargando dependencias: {e}{Colors.END}")
                sys.exit(1)