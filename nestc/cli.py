import click
from nestc.commands.build import execute_build
from nestc.commands.new import create_project_structure
from nestc.commands.run import execute_run
from nestc.commands.generate import create_resource
from nestc.utils.fs import assert_nestc_project
from nestc.commands.doctor import run_doctor

@click.group()
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

if __name__ == "__main__":
  main()