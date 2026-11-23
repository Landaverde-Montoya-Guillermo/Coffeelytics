from consola_ui import (
    seleccionar_con_flechas,
    imprimir_encabezado_sesion,
    ejecutar_accion,
)
from entidades.carrito_venta import CarritoVenta
from interfaz.barista_catalogo import BaristaCatalogo
from interfaz.barista_carrito import BaristaCarrito
from interfaz.barista_operaciones import BaristaOperaciones


class PantallaBarista:
    def __init__(self, usuario, servicios, reportes):
        self.usuario = usuario
        self.producto_srv = servicios["producto"]
        self.venta_srv = servicios["venta"]
        self.inventario_srv = servicios["inventario"]
        self.merma_srv = servicios["merma"]
        self.despacho_srv = servicios["despacho"]
        self.empleado_srv = servicios["empleado"]
        self.reportes = reportes

    def mostrar(self):
        carrito = CarritoVenta()
        carrito_ui = BaristaCarrito(self.usuario, self.venta_srv, carrito, self.reportes)
        catalogo_ui = BaristaCatalogo(
            self.usuario, self.producto_srv, carrito, carrito_ui
        )
        operaciones_ui = BaristaOperaciones(
            self.usuario,
            self.inventario_srv,
            self.despacho_srv,
            self.empleado_srv,
            self.merma_srv,
        )
        opciones = [
            "Nueva venta - Catalogo de productos",
            "Registrar merma",
            "Surtir mesa de consumibles",
            "Mi cuenta (desactivar)",
            "<< Cerrar sesion y volver al Inicio",
        ]
        while True:
            enc = imprimir_encabezado_sesion(
                self.usuario,
                breadcrumb=["Inicio", "Panel Barista"]
            )
            idx = seleccionar_con_flechas("MENU BARISTA", opciones, enc)
            if idx == 0:
                ejecutar_accion(catalogo_ui.catalogo_productos)
            elif idx == 1:
<<<<<<< HEAD
                operaciones_ui.registrar_merma()
            elif idx == 2:
                operaciones_ui.surtir_mesa()
            elif idx == 3:
                if operaciones_ui.desactivar_mi_cuenta():
=======
                ejecutar_accion(operaciones_ui.registrar_merma)
            elif idx == 2:
                ejecutar_accion(operaciones_ui.surtir_mesa)
            elif idx == 3:
                if ejecutar_accion(operaciones_ui.desactivar_mi_cuenta):
>>>>>>> 65287f2 (Programa completo)
                    return
            elif idx == 4:
                return
