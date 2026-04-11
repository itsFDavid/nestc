import time
from functools import wraps
from nestc.utils.colors import Colors

def timer(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        start = time.perf_counter()
        result = func(*args, **kwargs)
        elapsed = time.perf_counter() - start
        print(f"{Colors.BLUE}LOG{Colors.END}  {func.__name__}: {Colors.BOLD}{elapsed:.5f}s{Colors.END}")
        return result
    return wrapper