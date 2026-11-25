class BaseRepositorio:
    """Clase base para todos los repositorios. Encapsula el cursor de MySQL."""

    def __init__(self, cursor):
        self._cursor = cursor