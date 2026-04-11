import os
import urllib.request
import click
from nestc.utils.colors import Colors

# Fijamos la versión para garantizar reproducibilidad
MONGOOSE_VERSION = "7.21"
MONGOOSE_BASE = f"https://raw.githubusercontent.com/cesanta/mongoose/{MONGOOSE_VERSION}"

DEPENDENCIES = {
    "mongoose.c": f"{MONGOOSE_BASE}/mongoose.c",
    "mongoose.h": f"{MONGOOSE_BASE}/mongoose.h",
}

def ensure_dependencies(src_dir: str):
    """Descarga dependencias faltantes si no existen."""
    for filename, url in DEPENDENCIES.items():
        path = os.path.join(src_dir, filename)
        if not os.path.exists(path):
            click.echo(f"  {Colors.CYAN}↓{Colors.END} Descargando {filename} v{MONGOOSE_VERSION}...")
            try:
                urllib.request.urlretrieve(url, path)
                click.echo(f"  {Colors.GREEN}✓{Colors.END} {filename} descargado.")
            except Exception as e:
                click.echo(f"{Colors.RED}Error descargando {filename}: {e}{Colors.END}")
                raise SystemExit(1)