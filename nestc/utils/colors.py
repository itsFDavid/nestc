# --- CONFIGURACIÓN DE COLORES (ANSI) ---
class Colors:
    RED = "\033[91m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    BLUE = "\033[94m"
    MAGENTA = "\033[95m"
    CYAN = "\033[96m"
    BOLD = "\033[1m"
    END = "\033[0m"


# --- LOGO ASCII ---
NEST_C_LOGO = rf"""{Colors.RED}{Colors.BOLD}
  _   _           _      ____ 
 | \ | | ___  ___| |_   / ___|
 |  \| |/ _ \/ __| __| | |    
 | |\  |  __/\__ \ |_  | |___ 
 |_| \_|\___||___/\__|  \____|
{Colors.END}{Colors.CYAN}   NestJS-style Framework for C{Colors.END}
"""