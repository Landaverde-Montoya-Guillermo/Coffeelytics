from config.negocio import TASA_IVA
from entidades.base import EntidadBase, ValidacionError


class CarritoVenta(EntidadBase):
    def __init__(self):
        self._items = {}
        self._nombre_cliente = "Mostrador"
        self.fecha_venta = None  # fecha exacta con la que se registro la venta en MySQL
        # Ultimo evento del pedido, que el visor del cliente muestra en el banner amarillo.
        self.ultimo_evento = ""

    @property
    def items(self):
        return self._items

    @property
    def nombre_cliente(self):
        return self._nombre_cliente

    @nombre_cliente.setter
    def nombre_cliente(self, valor):
        texto = str(valor or "").strip()
        self._nombre_cliente = texto.title()[:50] if texto else "Mostrador"

    def agregar_producto(self, producto, cantidad=1):
        cant = int(self.validar_positivo(cantidad, "cantidad"))
        if producto.codigo in self._items:
            self._items[producto.codigo]["cantidad"] += cant
        else:
            self._items[producto.codigo] = {"producto": producto, "cantidad": cant}
        self.ultimo_evento = f"AGREGADO: {cant}x {producto.nombre} - ${producto.precio:.2f} c/u"

    def quitar_producto(self, codigo, cantidad=None):
        """
        Quita unidades de un producto del pedido.
        - Sin cantidad (None): elimina el renglon completo.
        - Con cantidad: resta esas unidades; si igualan la existencia, elimina el renglon.
        Devuelve las unidades quitadas. Los importes se recalculan solos (son derivados).
        """
        if codigo not in self._items:
            return 0
        actual = self._items[codigo]["cantidad"]
        nombre = self._items[codigo]["producto"].nombre
        if cantidad is None:
            cant = actual
        else:
            cant = int(self.validar_positivo(cantidad, "cantidad a quitar"))
            if cant > actual:
                raise ValidacionError(
                    f"No puedes quitar {cant} unidades: solo hay {actual} en el pedido.")
        if cant == actual:
            self._items.pop(codigo)
        else:
            self._items[codigo]["cantidad"] = actual - cant
        if cant == actual:
            self.ultimo_evento = f"ELIMINADO: {nombre}"
        else:
            self.ultimo_evento = f"ACTUALIZADO: -{cant}x {nombre} (Quedan: {actual - cant})"
        return cant

    def vaciar(self):
        self._items.clear()
        self._nombre_cliente = "Mostrador"
        self.fecha_venta = None
        self.ultimo_evento = ""

    def calcular_total(self):
        """Total a pagar: suma directa de precio x cantidad (el precio ya incluye IVA)."""
        return round(sum(i["producto"].precio * i["cantidad"] for i in self._items.values()), 2)

    def calcular_subtotal(self):
        """Subtotal sin IVA, desglosado hacia atras del total. Uso interno (BD y corte)."""
        return round(self.calcular_total() / (1 + TASA_IVA), 2)

    def calcular_iva(self):
        """IVA incluido en el total. Uso interno (BD y corte); no se muestra al cliente."""
        return round(self.calcular_total() - self.calcular_subtotal(), 2)