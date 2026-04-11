import re

HTTP_METHODS = {"GET", "POST", "PUT", "PATCH", "DELETE"}

PATTERNS = {
    "controller": re.compile(r'@Controller:\s*(\S+)'),
    "inject":     re.compile(r'@Inject:\s*(\S+)'),
    "service":    re.compile(r'@Service:\s*(\S+)'),
    "module":     re.compile(r'@Module:\s*(\S+)'),
    "init":       re.compile(r'@Init:\s*(\S+)'),
    "destroy":    re.compile(r'@Destroy:\s*(\S+)'),
    **{m: re.compile(rf'@{m}:\s*(\S+)') for m in HTTP_METHODS},
}

def extract_metadata(comment_block: str) -> dict:
    metadata = {
        "route": None, "method": None, "inject": None, 
        "service": None, "module": None, "init": None, "destroy": None
    }

    # 1. Métodos HTTP tienen prioridad
    for http_method in HTTP_METHODS:
        match = PATTERNS[http_method].search(comment_block)
        if match:
            metadata["method"] = http_method
            metadata["route"] = match.group(1)
            break

    # 2. Resto de decoradores
    for key in ("controller", "inject", "service", "module", "init", "destroy"):
        match = PATTERNS[key].search(comment_block)
        if match:
            if key == "controller" and metadata["route"] is None:
                metadata["route"] = match.group(1)
                metadata["method"] = "GET" # Default
            elif key != "controller":
                metadata[key] = match.group(1)

    return metadata