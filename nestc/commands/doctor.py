import os
import shutil
import subprocess
import platform
import click
from nestc.utils.colors import Colors

# Lista de dependencias esenciales
DEPENDENCIES = {
    "gcc": "Compilador de C (Necesario para 'nestc build')",
    "git": "Control de versiones (Necesario para descargar @nestcore)",
    "make": "Herramienta de automatización"
}

def check_dependency(cmd):
    """Revisa si un comando existe en el PATH."""
    return shutil.which(cmd) is not None

def get_install_command():
    """Retorna el comando de instalación según el OS."""
    os_type = platform.system()
    if os_type == "Darwin":  # macOS
        return "xcode-select --install" # Instala las herramientas de línea de comandos de Apple
    elif os_type == "Linux":
        # Intentamos detectar el gestor de paquetes
        if shutil.which("apt-get"):
            return "sudo apt-get update && sudo apt-get install -y build-essential git"
        elif shutil.which("dnf"):
            return "sudo dnf groupinstall 'Development Tools' && sudo dnf install git"
    return None

def run_doctor():
    """Ejecuta el diagnóstico completo."""
    click.echo(f"{Colors.BOLD}🩺 Nest-C Doctor: Verificando salud del sistema...{Colors.END}\n")
    
    missing = []
    for cmd, desc in DEPENDENCIES.items():
        if check_dependency(cmd):
            click.echo(f"  {Colors.GREEN}✓{Colors.END} {Colors.BOLD}{cmd}{Colors.END}: Instalado")
        else:
            click.echo(f"  {Colors.RED}✗{Colors.END} {Colors.BOLD}{cmd}{Colors.END}: {Colors.YELLOW}No encontrado{Colors.END}")
            click.echo(f"    {Colors.CYAN}↳ {desc}{Colors.END}")
            missing.append(cmd)

    if not missing:
        click.echo(f"\n{Colors.GREEN}{Colors.BOLD}¡Todo perfecto! Tu entorno está listo para Nest-C. {Colors.END}")
        return

    # Si faltan cosas, ofrecer instalación
    click.echo(f"\n{Colors.YELLOW} Se detectaron dependencias faltantes.{Colors.END}")
    install_cmd = get_install_command()

    if install_cmd:
        if click.confirm(f"¿Deseas que Nest-C intente instalar las herramientas faltantes por ti?"):
            click.echo(f"\n{Colors.CYAN}Ejecutando: {install_cmd}{Colors.END}")
            try:
                # shell=True es necesario para concatenar comandos con &&
                subprocess.run(install_cmd, shell=True, check=True)
                click.echo(f"\n{Colors.GREEN} Instalación completada. Vuelve a correr 'nestc doctor' para verificar.{Colors.END}")
            except subprocess.CalledProcessError:
                click.echo(f"\n{Colors.RED} Error durante la instalación. Por favor, instálalas manualmente.{Colors.END}")
    else:
        click.echo(f"{Colors.RED}No se pudo determinar un comando de instalación para tu sistema ({platform.system()}).{Colors.END}")
        click.echo("Por favor, instala GCC y Git manualmente.")