class ErrorNegocio(Exception):
    """Excepción base para reglas de negocio y validaciones de dominio."""
    pass


class ValidacionError(ErrorNegocio):
    """Se lanza cuando un atributo de una entidad no cumple las reglas."""
    pass


class StockInsuficienteError(ErrorNegocio):
    """Se lanza cuando no hay stock suficiente para vender, mermar o surtir."""
    pass


class EntidadBase:
    """Clase base con métodos comunes de validación para todas las entidades."""

    @staticmethod
    def validar_texto(valor, campo, max_len=None, obligatorio=True):
        texto = str(valor or "").strip()
        if obligatorio and not texto:
            raise ValidacionError(f"El campo '{campo}' es obligatorio.")
        if max_len and len(texto) > max_len:
            raise ValidacionError(f"El campo '{campo}' no puede exceder {max_len} caracteres.")
        return texto

    @staticmethod
    def validar_positivo(valor, campo, permitir_cero=False):
        try:
            num = float(valor)
        except (TypeError, ValueError):
            raise ValidacionError(f"El campo '{campo}' debe ser numérico.")
        if permitir_cero and num < 0:
            raise ValidacionError(f"El campo '{campo}' no puede ser negativo.")
        if not permitir_cero and num <= 0:
            raise ValidacionError(f"El campo '{campo}' debe ser mayor a cero.")
        return num