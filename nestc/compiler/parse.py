import os
import re
from pycparser import c_ast, c_parser
from nestc.utils.timer import timer
from nestc.compiler.decorators import extract_metadata

class DecoratorVisitor(c_ast.NodeVisitor):
    def __init__(self, source_code):
        self.source_lines = source_code.splitlines()
        self.controllers = []
        self.services = []
        self.modules = []

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

        if metadata["service"]:
            self.services.append({"name": metadata["service"], "init_func": None, "destroy_func": None})

        if metadata["init"]:
            for s in self.services:
                if s["name"] == metadata["init"]: s["init_func"] = func_name

        if metadata["destroy"]:
            for s in self.services:
                if s["name"] == metadata["destroy"]: s["destroy_func"] = func_name

        if metadata["module"]:
            self.modules.append({"name": metadata["module"], "init_func": func_name})

@timer
def analyze_project(src_dir):
    all_data = {"controllers": [], "services": [], "modules": []}
    parser = c_parser.CParser()

    for root, _, files in os.walk(src_dir):
        for file in files:
            if file.endswith(".c") and "mongoose" not in file:
                path = os.path.join(root, file)
                try:
                    with open(path, "r") as f:
                        code = f.read()

                    clean = "\n".join([l if not l.strip().startswith("#") else "" for l in code.splitlines()])
                    parser_ready = re.sub(r"//.*|/\*[\s\S]*?\*/", lambda m: " " * len(m.group(0)), clean)

                    # --- FIX PYCPARSER ---
                    # Inyectamos tipos falsos para que el AST no confunda los punteros con multiplicaciones
                    custom_types = set(re.findall(r'\b[A-Z]\w+Service\b', parser_ready))
                    dummy_headers = "".join([f"typedef int {t};\n" for t in custom_types])

                    ast = parser.parse(dummy_headers + parser_ready)
                    visitor = DecoratorVisitor(code)
                    visitor.visit(ast)
                    
                    all_data["controllers"].extend(visitor.controllers)
                    all_data["services"].extend(visitor.services)
                    all_data["modules"].extend(visitor.modules)
                except Exception as e:
                    print(f"Error parseando {file}: {e}")
                    continue
    return all_data