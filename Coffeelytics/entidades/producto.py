from entidades.base import EntidadBase
from config.reglas import ESTATUS_ACTIVO


class Producto(EntidadBase):
    def __init__(self, codigo, nombre, precio, estatus, categoria_cod, categoria_nom=""):
        self.codigo = self.validar_texto(codigo, "código de producto", 6).upper()
        self.nombre = self.validar_texto(nombre, "nombre de producto", 80)
        self.precio = self.validar_positivo(precio, "precio")
        self.estatus = int(estatus)
        self.categoria_cod = self.validar_texto(categoria_cod, "categoría", 10).upper()
        self.categoria_nom = categoria_nom

    def esta_disponible(self):
        return self.estatus == ESTATUS_ACTIVO