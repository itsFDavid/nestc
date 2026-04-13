import os
import re
from pycparser import c_ast, c_parser
from nestc.utils.timer import timer
from nestc.compiler.decorators import extract_metadata

FILES_TO_IGNORE = {
    "mongoose.c",
    "frozen.c",
    "mongoose.h",
    "frozen.h",
    "json_utils.h",
    "nest_core.h",
    "main.c",
}


class DecoratorVisitor(c_ast.NodeVisitor):
    # Recibimos line_shift para compensar las líneas falsas inyectadas
    def __init__(self, source_code, services_list, line_shift=0):
        self.source_lines = source_code.splitlines()
        self.controllers = []
        self.modules = []
        self.services_list = services_list
        self.line_shift = line_shift # <-- Guardamos el desfase

    def visit_FuncDef(self, node):
        func_name = node.decl.name
        
        # Compensamos el desfase matemático
        real_line = node.coord.line - self.line_shift
        line_index = real_line - 1 # Índice de array base 0
        
        # Escanear hacia arriba buscando solo los comentarios inmediatos
        comments = []
        for i in range(line_index - 1, -1, -1):
            line = self.source_lines[i].strip()
            if line.startswith("//"):
                comments.insert(0, line)
            elif line == "":
                continue # Ignorar saltos de línea en blanco
            else:
                break # Detenerse al tocar código

        comment_block = "\n".join(comments)
        metadata = extract_metadata(comment_block)

        if metadata["route"]:
            self.controllers.append({
                "route": metadata["route"],
                "method": metadata["method"] or "GET",
                "function": func_name,
                "inject": metadata["inject"],
                "dto": metadata["body"]
            })

        if metadata["init"]:
            for s in self.services_list:
                if s["name"] == metadata["init"]: s["init_func"] = func_name

        if metadata["destroy"]:
            for s in self.services_list:
                if s["name"] == metadata["destroy"]: s["destroy_func"] = func_name

        if metadata["module"]:
            self.modules.append({"name": metadata["module"], "init_func": func_name})


@timer
def analyze_project(src_dir):
    all_data = {"controllers": [], "services": [], "modules": [], "dtos": []}
    parser = c_parser.CParser()

    # --- PASADA 1: Descubrimiento Global ---
    for root, _, files in os.walk(src_dir):
        for file in files:
            if file.endswith(".c") and file not in FILES_TO_IGNORE:
                path = os.path.join(root, file)
                with open(path, "r") as f:
                    code = f.read()
                
                # Buscar servicios globalmente para luego inyectar tipos falsos en la PASADA 2
                services_in_file = re.findall(r"@Service:\s*(\S+)", code)
                for s in services_in_file:
                    if not any(x["name"] == s for x in all_data["services"]):
                        all_data["services"].append(
                            {"name": s, "init_func": None, "destroy_func": None}
                        )
                
                # Buscar DTOs globalmente para luego generar validadores
                dtos_in_file = re.findall(r"@DTO:\s*(\w+)", code)
                for d in dtos_in_file:
                    if d not in all_data["dtos"]:
                        all_data["dtos"].append(d)

    # --- PASADA 2: Construcción del AST y Enlaces ---
    for root, _, files in os.walk(src_dir):
        for file in files:
            if file.endswith(".c") and file not in FILES_TO_IGNORE:
                path = os.path.join(root, file)
                try:
                    with open(path, "r") as f:
                        code = f.read()

                    clean = "\n".join(
                        [
                            l if not l.strip().startswith("#") else ""
                            for l in code.splitlines()
                        ]
                    )
                    parser_ready = re.sub(
                        r"//.*|/\*[\s\S]*?\*/", lambda m: " " * len(m.group(0)), clean
                    )

                    # Inyectar los tipos falsos dinámicamente
                    service_names = [s["name"] for s in all_data["services"]]
                    custom_types = service_names + all_data["dtos"] + ["NestResponse", "NcJson"]
                    dummy_headers = "".join(
                        [f"typedef int {t};\n" for t in custom_types]
                    )
                    
                    # Calculamos cuántas líneas inyectamos
                    shift = len(custom_types) 

                    ast = parser.parse(dummy_headers + parser_ready)

                    # Le pasamos el 'shift' al Visitor para que corrija la miopía
                    visitor = DecoratorVisitor(code, all_data["services"], line_shift=shift)
                    visitor.visit(ast)

                    all_data["controllers"].extend(visitor.controllers)
                    all_data["modules"].extend(visitor.modules)
                except Exception as e:
                    print(f"Error parseando {file}: {e}")
                    continue

    return all_data