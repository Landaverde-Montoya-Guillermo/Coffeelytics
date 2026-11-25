class Color:
    RESET     = "\033[0m"
    BOLD      = "\033[1m"
    DIM       = "\033[2m"

    CAFE      = "\033[38;5;130m"
    CARAMELO  = "\033[38;5;172m"
    CREMA     = "\033[38;5;223m"
    BLANCO    = "\033[97m"
    GRIS      = "\033[37m"
    VERDE     = "\033[32m"
    VERDE_OK  = "\033[92m"
    ROJO      = "\033[31m"
    ROJO_ALT  = "\033[91m"
    AMARILLO  = "\033[33m"
    CIAN      = "\033[36m"

    BG_CAFE      = "\033[48;5;130m"
    BG_OSCURO    = "\033[48;5;52m"
    BG_CARAMELO  = "\033[48;5;172m"

    @staticmethod
    def aplicar(codigo, texto):
        return f"{codigo}{texto}{Color.RESET}"

    @staticmethod
    def titulo(texto):
        return f"{Color.BOLD}{Color.CARAMELO}{texto}{Color.RESET}"

    @staticmethod
    def ok(texto):
        return f"{Color.VERDE_OK}[OK] {texto}{Color.RESET}"

    @staticmethod
    def error(texto):
        return f"{Color.ROJO_ALT}[X]  {texto}{Color.RESET}"
    @staticmethod
    def aviso(texto):
        return f"{Color.AMARILLO}[!]  {texto}{Color.RESET}"

    @staticmethod
    def info(texto):
        return f"{Color.CIAN}[>>] {texto}{Color.RESET}"