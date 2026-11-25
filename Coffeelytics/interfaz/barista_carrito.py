from interfaz.estilos import Color
from interfaz.visor_cliente import renderizar_visor_coffeelytics
from consola_ui import (
    pausar, seleccionar_con_flechas,
    imprimir_encabezado_sesion, imprimir_tabla,
    _centrar_texto, limpiar_pantalla,
    pedir_cantidad_a_quitar, OperacionCancelada, PasoAnterior
)
from interfaz.visor_cliente import renderizar_visor_coffeelytics
from interfaz.modal_cobro import ModalCobro


class BaristaCarrito:
    def __init__(self, usuario, venta_srv, carrito, reportes):
        self.usuario = usuario
        self.venta_srv = venta_srv
        self.carrito = carrito
        self.reportes = reportes

    def gestionar_carrito(self):
        while True:
            limpiar_pantalla()
            breadcrumb = ["Inicio", "Panel Barista", "Nueva Venta", "Carrito"]
            if not self.carrito.items:
                # Pedido vacio (o recien vaciado): el visor muestra $0.00 y se regresa al catalogo.
                print(imprimir_encabezado_sesion(self.usuario, breadcrumb=breadcrumb))
                print(renderizar_visor_coffeelytics(self.carrito))
                pausar()
                return

            # El visor (banner, tabla del pedido y TOTAL A PAGAR) se dibuja siempre arriba del menu.
            encabezado_carrito = "\n".join([
                imprimir_encabezado_sesion(self.usuario, breadcrumb=breadcrumb),
                renderizar_visor_coffeelytics(self.carrito),
            ])
            opts = [
                "Cobrar (procesar pago)",
                "Quitar producto del carrito",
                "Vaciar carrito",
                "<< Volver sin cobrar",
            ]
            idx = seleccionar_con_flechas(
                "Que deseas hacer?", opts, encabezado_carrito
            )
            if idx == 0:
                modal = ModalCobro(self.usuario, self.carrito, self.venta_srv, self.reportes)
                if modal.procesar():
                    return
            elif idx == 1:
                self._quitar_del_carrito()
            elif idx == 2:
                if self._confirmar_vaciado():
                    self.carrito.vaciar()
                    self.carrito.ultimo_evento = "PEDIDO VACIADO"
                    # El siguiente ciclo muestra el visor vacio con $0.00 y regresa.
            elif idx == 3:
                return

    def _confirmar_vaciado(self):
        """Pide confirmacion antes de vaciar el pedido. Devuelve True si se confirma."""
        enc = imprimir_encabezado_sesion(
            self.usuario,
            breadcrumb=["Inicio", "Panel Barista", "Nueva Venta", "Carrito", "Vaciar pedido"]
        )
        opciones = ["Si, vaciar el pedido", "No, conservar el pedido"]
        return seleccionar_con_flechas(
            "Seguro que deseas vaciar el pedido?", opciones, enc
        ) == 0

    def _encabezado_visor(self, breadcrumb):
        """Encabezado de sesion con el visor en vivo debajo (banner, productos y total)."""
        return "\n".join([
            imprimir_encabezado_sesion(self.usuario, breadcrumb=breadcrumb),
            renderizar_visor_coffeelytics(self.carrito),
        ])

    def _quitar_del_carrito(self):
        """
        Quitar producto con visor en vivo: el visor queda arriba del selector y de la
        pantalla de cantidad, y se redibuja con el nuevo total y el ultimo evento.
        """
        breadcrumb = ["Inicio", "Panel Barista", "Nueva Venta", "Carrito", "Quitar producto"]
        codigos = list(self.carrito.items.keys())
        if not codigos:
            return
        nombres = [
            f"{self.carrito.items[c]['producto'].nombre} x{self.carrito.items[c]['cantidad']}"
            for c in codigos
        ] + ["<< Cancelar"]
        idx = seleccionar_con_flechas(
            "Selecciona producto a quitar", nombres, self._encabezado_visor(breadcrumb)
        )
        if idx >= len(codigos):
            return

        codigo = codigos[idx]
        producto = self.carrito.items[codigo]["producto"]
        disponible = self.carrito.items[codigo]["cantidad"]
        estilo = Color.ok
        try:
            if disponible == 1:
                cantidad = 1  # Unica unidad: se elimina directamente, sin preguntar.
            else:
                limpiar_pantalla()
                print(self._encabezado_visor(breadcrumb))
                cantidad = pedir_cantidad_a_quitar(producto.nombre, disponible)
            self.carrito.quitar_producto(codigo, cantidad)  # actualiza ultimo_evento
            if cantidad >= disponible:
                mensaje = f"'{producto.nombre}' eliminado del carrito."
            else:
                mensaje = f"Se quitaron {cantidad} de '{producto.nombre}'. Quedan {disponible - cantidad}."
        except (OperacionCancelada, PasoAnterior):
            mensaje = "No se quito ninguna unidad."
            estilo = Color.aviso
        except ValueError as error:
            mensaje = str(error)
            estilo = Color.error

        # Redibuja la pantalla con el visor ya actualizado (nuevo total y evento).
        limpiar_pantalla()
        print(self._encabezado_visor(breadcrumb))
        print(_centrar_texto(estilo(mensaje)))
        pausar()
