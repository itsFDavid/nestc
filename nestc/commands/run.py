import os
import subprocess
import click
from nestc.commands.build import execute_build
from nestc.utils.colors import Colors

def execute_run():
    # 1. Intentamos compilar primero
    if execute_build():
        # 2. Si el build fue exitoso, ejecutamos
        bin_path = "./build/app"
        if os.path.exists(bin_path):
            click.echo(f"{Colors.CYAN}Ejecutando binario...{Colors.END}\n")
            try:
                subprocess.run([bin_path], check=True)
            except KeyboardInterrupt:
                click.echo(f"\n{Colors.YELLOW}Servidor detenido por el usuario.{Colors.END}")
        else:
            click.echo(f"{Colors.RED}Error: No se encontró el binario en {bin_path}{Colors.END}")