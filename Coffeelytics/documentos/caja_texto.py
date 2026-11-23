"""
Constructor de cajas de texto con bordes Unicode para tickets y comprobantes.

Cada linea se devuelve como (texto, estilo): el texto es plano (sin codigos ANSI)
y todas las lineas de una caja miden exactamente `ancho` caracteres, de modo que
los bordes siempre cuadran. El estilo lo aplica consola_ui.imprimir_bloque_centrado.
"""
import textwrap


class Caja:
    def __init__(self, ancho):
        self.ancho = int(ancho)
        self.interior = self.ancho - 2     # espacio entre los bordes laterales
        self.util = self.interior - 2      # con un espacio de margen a cada lado
        self.lineas = []

    def marco(self, izq, car, der, estilo="marco"):
        """Linea de borde, por ejemplo ╠═══╣ o ╟───╢."""
        self.lineas.append((izq + car * self.interior + der, estilo))

    def fila_exacta(self, contenido, estilo=None):
        """Fila con contenido ya formateado a `util` caracteres (tablas y alineaciones)."""
        self.lineas.append(("║ " + contenido.ljust(self.util) + " ║", estilo))

    def texto(self, valor, estilo=None, alin="i"):
        """Texto libre envuelto dentro de la caja. alin: 'i' izquierda, 'c' centrado."""
        for trozo in (textwrap.wrap(str(valor), self.util) or [""]):
            self.fila_exacta(trozo.center(self.util) if alin == "c" else trozo, estilo)

    def dato(self, etiqueta, valor, ancho_et=20, estilo=None):
        """Par etiqueta: valor. El valor se envuelve y se alinea bajo la misma columna."""
        trozos = textwrap.wrap(str(valor), self.util - ancho_et) or [""]
        for i, trozo in enumerate(trozos):
            et = etiqueta if i == 0 else ""
            self.fila_exacta(f"{et:<{ancho_et}}{trozo}", estilo)

    def alineado_derecha(self, etiqueta, valor, estilo=None):
        """Renglon de totales, alineado a la derecha de la caja."""
        self.fila_exacta(f"{etiqueta:<18}{valor:>12}".rjust(self.util), estilo)

    def resultado(self):
        return self.lineas
