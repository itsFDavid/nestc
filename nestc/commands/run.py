import os
import subprocess
import click
from nestc.commands.build import execute_build
from nestc.utils.colors import Colors

def execute_run():
    if execute_build():
        bin_path = "./build/app"
        if os.path.exists(bin_path):
            click.echo(f"{Colors.CYAN}Ejecutando binario...{Colors.END}\n")
            
            # Lanzamos el proceso
            process = subprocess.Popen([bin_path])
            
            try:
                # Esperamos a que el proceso termine (ya sea por éxito o señal)
                process.wait()
            except KeyboardInterrupt:
                # Si el usuario presiona Ctrl+C en Python:
                # 1. No matamos al hijo, el hijo ya recibió la señal SIGINT por el SO.
                # 2. Esperamos a que el proceso de C termine su lógica de @Destroy
                process.wait()
                click.echo(f"\n{Colors.YELLOW}Nest-C: Proceso finalizado correctamente.{Colors.END}")
        else:
            click.echo(f"{Colors.RED}Error: No se encontró el binario en {bin_path}{Colors.END}")