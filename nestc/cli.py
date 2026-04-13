import os
import shutil
import click
import platform
import subprocess

from nestc.commands.build import execute_build
from nestc.commands.new import create_project_structure
from nestc.commands.run import execute_run
from nestc.commands.generate import create_resource
from nestc.utils.fs import assert_nestc_project
from nestc.commands.doctor import run_doctor

@click.group()
@click.version_option(version='1.0.0', prog_name='Nest-C')
def main():
  """Nest-C CLI: Tu framework de C con estilo NestJS."""
  pass

@main.command()
def build():
  """Transpila y genera el binario de C."""
  assert_nestc_project()
  execute_build()

@main.command()
@click.argument('name')
def new(name):
  """Crea un nuevo proyecto Nest-C desde cero."""
  create_project_structure(name)

@main.command()
def start():
    """Build y ejecución del proyecto."""
    assert_nestc_project()
    execute_run()

# Grupo para generar cosas (nestc generate ...)
@main.group()
def generate():
    """Generador de recursos."""
    pass

@generate.command()
@click.argument('name')
def resource(name):
    """Genera un nuevo recurso (Controller + Service)."""
    assert_nestc_project()
    create_resource(name)

@main.command(name='g')
@click.argument('type')
@click.argument('name')
@click.pass_context
def generate_alias(ctx, type, name):
    """Alias para generate."""
    assert_nestc_project()
    if type == 'resource' or type == 'res':
        ctx.invoke(resource, name=name)
    else:
        click.echo(f"Tipo desconocido: {type}")

@main.command(name="doctor")
def doctor():
    """Verifica si el sistema tiene las dependencias necesarias."""
    run_doctor()

@main.command()
def info():
    """Muestra información del entorno de Nest-C."""
    click.echo("\n Nest-C Environment Info\n" + "-"*30)
    click.echo(f" Nest-C Version : 1.0.0")
    click.echo(f" OS Platform    : {platform.system()} {platform.release()}")
    click.echo(f"  Architecture   : {platform.machine()}")
    
    # Intentar obtener la versión de GCC
    try:
        gcc_version = subprocess.check_output(["gcc", "-dumpversion"], stderr=subprocess.STDOUT).decode().strip()
        click.echo(f"  GCC Version    : {gcc_version}")
    except (FileNotFoundError, subprocess.CalledProcessError):
        click.echo(f"  GCC Version    : No encontrado (Ejecuta 'nestc doctor')")
    click.echo("-" * 30 + "\n")

@main.command()
def clean():
    """Limpia los archivos compilados (carpeta build/)."""
    assert_nestc_project()
    if os.path.exists("build"):
        shutil.rmtree("build")
        click.echo(f" Carpeta 'build/' eliminada exitosamente. Entorno limpio.")
    else:
        click.echo(f"ℹ El proyecto ya está limpio (no existe 'build/').")

if __name__ == "__main__":
  main()