import re

HTTP_METHODS = ["GET", "POST", "PUT", "PATCH", "DELETE"]

PATTERNS = {
    "controller": re.compile(r'@Controller:\s*(\S+)'),
    "inject":     re.compile(r'@Inject:\s*(\S+)'),
    "service":    re.compile(r'@Service:\s*(\S+)'),
    "module":     re.compile(r'@Module:\s*(\S+)'),
    "init":       re.compile(r'@Init:\s*(\S+)'),
    "destroy":    re.compile(r'@Destroy:\s*(\S+)'),
    "body":       re.compile(r'@Body:\s*(\w+)'),
    **{m: re.compile(rf'@{m}:\s*(\S+)') for m in HTTP_METHODS},
}

def extract_metadata(comment_block: str) -> dict:
    metadata = {
        "route": None, "method": None, "inject": None, 
        "module": None, "init": None, "destroy": None,
        "body": None
    }

    found_methods = []
    for http_method in HTTP_METHODS:
        match = PATTERNS[http_method].search(comment_block)
        if match:
            found_methods.append((http_method, match.group(1)))

    if len(found_methods) > 1:
        print(f"\\x1b[33m[WARN] Múltiples métodos HTTP detectados: "
              f"{[m[0] for m in found_methods]}. Se usará: {found_methods[0][0]}\\x1b[0m")

    if found_methods:
        metadata["method"] = found_methods[0][0]
        metadata["route"]  = found_methods[0][1]

    for key in ("controller", "inject", "module", "init", "destroy", "body"):
        match = PATTERNS[key].search(comment_block)
        if match:
            if key == "controller" and metadata["route"] is None:
                metadata["route"] = match.group(1)
                metadata["method"] = "GET"
            elif key != "controller":
                metadata[key] = match.group(1)

    return metadata