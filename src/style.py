class Colors:
    RED = "\033[0;31m"
    GREEN = "\033[0;32m"
    YELLOW = "\033[0;33m"
    BLUE = "\033[0;36m"
    RESET = "\033[0;0m"

def success(msg):
    print(f"{Colors.GREEN}✅ {msg}{Colors.RESET}")

def warning(msg):
    print(f"{Colors.YELLOW}⚠️ {msg}{Colors.RESET}")

def error(msg):
    print(f"{Colors.RED}❌ {msg}{Colors.RESET}")
