import os
import urllib.request
import click
from nestc.utils.colors import Colors

from nestc.utils.templates.core_api import NEST_CORE_H_CONTENT, ENV_UTILS_CONTENT, JSON_UTILS_CONTENT, NC_JSON_CONTENT, NC_VALIDATORS_CONTENT


MONGOOSE_VERSION = "7.21"
MONGOOSE_BASE = f"https://raw.githubusercontent.com/cesanta/mongoose/{MONGOOSE_VERSION}"

FROZEN_BASE = "https://raw.githubusercontent.com/cesanta/frozen/master"

DEPENDENCIES = {
    "mongoose.c": f"{MONGOOSE_BASE}/mongoose.c",
    "mongoose.h": f"{MONGOOSE_BASE}/mongoose.h",
    "frozen.c": f"{FROZEN_BASE}/frozen.c",
    "frozen.h": f"{FROZEN_BASE}/frozen.h",
}

def ensure_dependencies():
    """Construye la carpeta @nestcore con todas las dependencias y utilidades."""
    core_dir = "@nestcore"
    os.makedirs(core_dir, exist_ok=True)

    # 0. Escribir el header para manejo de JSON (nc_json.h)
    with open(os.path.join(core_dir, "nc_json.h"), "w") as f:
        f.write(NC_JSON_CONTENT)
        click.echo(f"  {Colors.GREEN}✓{Colors.END} nc_json.h generado en {core_dir}/")
    
    # 0.1 Escribir el header para validadores (nc_validators.h)
    with open(os.path.join(core_dir, "nc_validators.h"), "w") as f:
        f.write(NC_VALIDATORS_CONTENT)
        click.echo(f"  {Colors.GREEN}✓{Colors.END} nc_validators.h generado en {core_dir}/")
    
    # 1: Escribir el header principal de Nest-C (nest_core.h)
    core_header_path = os.path.join(core_dir, "nest_core.h")
    if not os.path.exists(core_header_path):
        with open(core_header_path, "w") as f:
            f.write(NEST_CORE_H_CONTENT)
        click.echo(f"  {Colors.GREEN}✓{Colors.END} nest_core.h generado en {core_dir}/")
    
    # 2. Escribir utilidades nativas de Nest-C (json_utils.h)
    json_path = os.path.join(core_dir, "json_utils.h")
    if not os.path.exists(json_path):
        with open(json_path, "w") as f:
            f.write(JSON_UTILS_CONTENT)
        click.echo(f"  {Colors.GREEN}✓{Colors.END} json_utils.h generado en {core_dir}/")
    
    env_utils_path = os.path.join(core_dir, "env_utils.h")
    if not os.path.exists(env_utils_path):
        with open(env_utils_path, "w") as f:
            f.write(ENV_UTILS_CONTENT)
        click.echo(f"  {Colors.GREEN}✓{Colors.END} env_utils.h generado en {core_dir}/")

    # 3. Descargar librerías de terceros
    for filename, url in DEPENDENCIES.items():
        path = os.path.join(core_dir, filename)
        if not os.path.exists(path):
            click.echo(f"  {Colors.CYAN}↓{Colors.END} Instalando {filename} en {core_dir}/...")
            try:
                req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
                with urllib.request.urlopen(req) as response, open(path, 'wb') as out_file:
                    out_file.write(response.read())
                click.echo(f"  {Colors.GREEN}✓{Colors.END} {filename} instalado.")
            except Exception as e:
                click.echo(f"{Colors.RED}Error descargando {filename}: {e}{Colors.END}")
                if os.path.exists(path): os.remove(path)
                raise SystemExit(1)