import os
import click
from nestc.utils.colors import Colors
from nestc.utils.templates.scaffold import MAIN_TEMPLATE, APP_CONTROLLER, APP_MODULE, APP_SERVICE
from nestc.utils.downloader import ensure_dependencies

def create_project_structure(project_name):
    """Crea la estructura de carpetas y archivos base para un nuevo proyecto Nest-C."""
    src_app = os.path.join(project_name, "src", "app")
    folders = [project_name, os.path.join(project_name, "src"), src_app, os.path.join(project_name, "build")]

    click.echo(f"{Colors.BOLD}Creando nuevo proyecto Nest-C: {Colors.BLUE}{project_name}{Colors.END}")

    for folder in folders:
        if not os.path.exists(folder):
            os.makedirs(folder)
            click.echo(f"  {Colors.GREEN}* {Colors.END}Carpeta creada: {folder}")
    
    original_dir = os.getcwd()
    os.chdir(project_name)
    ensure_dependencies()
    os.chdir(original_dir)

    # 2. Crear app.service.c
    with open(os.path.join(src_app, "app.service.c"), "w") as f:
        f.write(APP_SERVICE)

    # 3. Crear app.controller.c
    with open(os.path.join(src_app, "app.controller.c"), "w") as f:
        f.write(APP_CONTROLLER)

    # 4. Crear app.module.c
    with open(os.path.join(src_app, "app.module.c"), "w") as f:
        f.write(APP_MODULE)

    # 5. Crear el main.c REAL usando el MAIN_TEMPLATE
    main_path = os.path.join(project_name, "src", "main.c")
    with open(main_path, "w") as f:
        f.write(MAIN_TEMPLATE)
    click.echo(f"  {Colors.GREEN}* {Colors.END}Archivo creado: {main_path}")

    # 6. Crear archivo .env base
    with open(os.path.join(project_name, ".env"), "w") as f:
        f.write("# Configuracion de Nest-C\n")
        f.write("PORT=8080\n")
        f.write("DB_HOST=localhost\n")
        f.write("DB_USER=root\n")
        f.write("DB_PASS=1234\n")

    # 7. Crear configuración
    with open(os.path.join(project_name, "nestc-config.json"), "w") as f:
        f.write('{\n  "name": "' + project_name + '",\n  "version": "0.1.0",\n  "framework": "Nest-C"\n}')

    click.echo(f"\n{Colors.GREEN}{Colors.BOLD}Proyecto '{project_name}' inicializado. ¡Listo para desarrollar!{Colors.END}")
    click.echo(f"Escribe: {Colors.YELLOW}cd {project_name} && nestc build && nestc start{Colors.END}")