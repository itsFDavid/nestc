import os
import click
from nestc.utils.colors import Colors
from nestc.utils.json_utils import JSON_UTILS_CONTENT
from nestc.utils.templates import APP_SERVICE, APP_CONTROLLER, APP_MODULE

def create_project_structure(project_name):
    os.makedirs(os.path.join(project_name, "src", "utils"), exist_ok=True)
    src_app = os.path.join(project_name, "src", "app")
    folders = [project_name, os.path.join(project_name, "src"), src_app, os.path.join(project_name, "build")]

    click.echo(f"{Colors.BOLD}Creando nuevo proyecto Nest-C: {Colors.BLUE}{project_name}{Colors.END}")

    # 1. Generar src/utils/json_utils.h
    # EXISTE EN LOS UTILS DEL CLI, SE COPIA DESDE ALLÍ
    json_utils_path = os.path.join(project_name, "src", "utils", "json_utils.h")
    with open(json_utils_path, "w") as f:
        f.write(JSON_UTILS_CONTENT)
    click.echo(f"  {Colors.GREEN}* {Colors.END}Archivo creado: {json_utils_path}")

    for folder in folders:
        if not os.path.exists(folder):
            os.makedirs(folder)
            click.echo(f"  {Colors.GREEN}* {Colors.END}Carpeta creada: {folder}")

    # 1. Crear app.service.c (Cero dependencias locales)
    with open(os.path.join(src_app, "app.service.c"), "w") as f:
        f.write(APP_SERVICE)

    # 2. Crear app.controller.c (Incluye al Service)
    with open(os.path.join(src_app, "app.controller.c"), "w") as f:
        f.write(APP_CONTROLLER)

    # 3. Crear app.module.c (Incluye al Controller)
    with open(os.path.join(src_app, "app.module.c"), "w") as f:
        f.write(APP_MODULE)

    with open(os.path.join(project_name, "src", "main.c"), "w") as f:
        f.write("// Este proyecto usa el Bootstrap automático de Nest-C.\\n")

    with open(os.path.join(project_name, "nestc-config.json"), "w") as f:
        f.write('{\n  "name": "' + project_name + '",\n  "version": "0.1.0",\n  "framework": "Nest-C"\n}')

    click.echo(f"\n{Colors.GREEN}{Colors.BOLD}Proyecto '{project_name}' inicializado. ¡Listo para devolver JSON!{Colors.END}")
    click.echo(f"Escribe: {Colors.YELLOW}cd {project_name} && nestc build{Colors.END}")