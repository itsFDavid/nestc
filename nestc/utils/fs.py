import os
import json
import click
from nestc.utils.colors import Colors

def assert_nestc_project():
    """Lanza SystemExit si no estamos en un proyecto Nest-C válido."""
    if not os.path.exists("nestc-config.json"):
        click.echo(
            f"{Colors.RED}Error: No se encontró nestc-config.json.{Colors.END}\n"
            f"Asegúrate de estar dentro de un proyecto Nest-C.\n"
            f"Para crear uno: {Colors.YELLOW}nestc new <nombre>{Colors.END}"
        )
        raise SystemExit(1)

def read_project_config() -> dict:
    """Devuelve el contenido del archivo de configuración."""
    with open("nestc-config.json") as f:
        return json.load(f)