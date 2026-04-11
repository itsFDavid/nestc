import os
import re
from pycparser import c_ast, c_parser
from nestc.utils.timer import timer
from nestc.compiler.decorators import extract_metadata

class DecoratorVisitor(c_ast.NodeVisitor):
    # Recibimos la lista global de servicios para actualizarla
    def __init__(self, source_code, services_list):
        self.source_lines = source_code.splitlines()
        self.controllers = []
        self.modules = []
        self.services_list = services_list 

    def visit_FuncDef(self, node):
        func_name = node.decl.name
        line_num = node.coord.line
        
        start = max(0, line_num - 8)
        comment_block = "\n".join(self.source_lines[start:line_num])
        metadata = extract_metadata(comment_block)

        if metadata["route"]:
            self.controllers.append({
                "route": metadata["route"],
                "method": metadata["method"] or "GET",
                "function": func_name,
                "inject": metadata["inject"]
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
    all_data = {"controllers": [], "services": [], "modules": []}
    parser = c_parser.CParser()

    # --- PASADA 1: Descubrimiento Global ---
    # Primero buscamos TODOS los @Service en todos los archivos
    # para que la lista esté completa antes de intentar hacer conexiones.
    for root, _, files in os.walk(src_dir):
        for file in files:
            if file.endswith(".c") and "mongoose" not in file and "frozen" not in file:
                path = os.path.join(root, file)
                with open(path, "r") as f:
                    code = f.read()
                services_in_file = re.findall(r'@Service:\s*(\S+)', code)
                for s in services_in_file:
                    if not any(x["name"] == s for x in all_data["services"]):
                        all_data["services"].append({"name": s, "init_func": None, "destroy_func": None})

    # --- PASADA 2: Construcción del AST y Enlaces ---
    for root, _, files in os.walk(src_dir):
        for file in files:
            if file.endswith(".c") and "mongoose" not in file and "frozen" not in file:
                path = os.path.join(root, file)
                try:
                    with open(path, "r") as f:
                        code = f.read()

                    clean = "\n".join([l if not l.strip().startswith("#") else "" for l in code.splitlines()])
                    parser_ready = re.sub(r"//.*|/\*[\s\S]*?\*/", lambda m: " " * len(m.group(0)), clean)

                    # Inyectar los tipos falsos dinámicamente basados en la Pasada 1
                    custom_types = [s["name"] for s in all_data["services"]]
                    dummy_headers = "".join([f"typedef int {t};\n" for t in custom_types])

                    ast = parser.parse(dummy_headers + parser_ready)
                    
                    # Ahora el Visitor recibe la lista COMPLETA de servicios
                    visitor = DecoratorVisitor(code, all_data["services"])
                    visitor.visit(ast)
                    
                    all_data["controllers"].extend(visitor.controllers)
                    all_data["modules"].extend(visitor.modules)
                except Exception as e:
                    print(f"Error parseando {file}: {e}")
                    continue
                    
    return all_data