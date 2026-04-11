import os
import urllib.request
import click
from nestc.utils.colors import Colors


MONGOOSE_VERSION = "7.21"
MONGOOSE_BASE = f"https://raw.githubusercontent.com/cesanta/mongoose/{MONGOOSE_VERSION}"

FROZEN_BASE = "https://raw.githubusercontent.com/cesanta/frozen/master"

DEPENDENCIES = {
    "mongoose.c": f"{MONGOOSE_BASE}/mongoose.c",
    "mongoose.h": f"{MONGOOSE_BASE}/mongoose.h",
    "frozen.c": f"{FROZEN_BASE}/frozen.c",
    "frozen.h": f"{FROZEN_BASE}/frozen.h",
}

def ensure_dependencies(src_dir: str):
    """Descarga dependencias faltantes si no existen."""
    for filename, url in DEPENDENCIES.items():
        path = os.path.join(src_dir, filename)
        if not os.path.exists(path):
            click.echo(f"  {Colors.CYAN}↓{Colors.END} Descargando {filename}...")
            try:
                # Algunos servidores bloquean peticiones sin User-Agent
                req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
                with urllib.request.urlopen(req) as response, open(path, 'wb') as out_file:
                    out_file.write(response.read())
                click.echo(f"  {Colors.GREEN}✓{Colors.END} {filename} descargado.")
            except Exception as e:
                click.echo(f"{Colors.RED}Error descargando {filename}: {e}{Colors.END}")
                # Si falla, eliminamos el archivo parcial para no corromper el build
                if os.path.exists(path): os.remove(path)
                raise SystemExit(1)