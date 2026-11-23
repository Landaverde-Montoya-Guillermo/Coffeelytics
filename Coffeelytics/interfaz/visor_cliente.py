"""
Visor de pedido en vivo de Coffeelytics.

Bloque que se dibuja arriba de los menus del barista (catalogo y carrito) para que el
cliente vea su pedido mientras se arma: banner con el ultimo evento, tabla de productos
y el TOTAL A PAGAR (el precio ya incluye IVA, por eso no se muestran subtotal ni IVA).
"""
from consola_ui import formatear_bloque_centrado, imprimir_tabla


def renderizar_visor_coffeelytics(carrito, ultimo_evento=""):
    """
    Devuelve el visor como cadena lista para imprimir, centrada en la terminal.
    `ultimo_evento` se muestra en el banner amarillo; si viene vacio se usa el del carrito.
    """
    evento = ultimo_evento or getattr(carrito, "ultimo_evento", "")
    partes = [formatear_bloque_centrado([("COFFEELYTICS - VISOR DE PEDIDO EN VIVO", "titulo")])]
    if evento:
        partes.append(formatear_bloque_centrado([(f">> {evento}", "aviso")]))

    if carrito.items:
        cols = ["CANT", "PRODUCTO", "PRECIO", "IMPORTE"]
        filas = []
        for item in carrito.items.values():
            prod = item["producto"]
            cant = item["cantidad"]
            filas.append((cant, prod.nombre, f"${prod.precio:.2f}", f"${prod.precio * cant:.2f}"))
        partes.append(imprimir_tabla("PEDIDO ACTUAL", cols, filas, retornar_texto=True))
    else:
        partes.append(formatear_bloque_centrado([("Pedido vacio - Esperando productos...", "dim")]))

    partes.append(formatear_bloque_centrado(
        [(f"TOTAL A PAGAR: ${carrito.calcular_total():.2f}", "total")]
    ))
    return "\n".join(partes)
