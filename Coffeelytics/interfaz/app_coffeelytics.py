from mysql.connector import Error as ErrorBaseDatos

from interfaz.estilos import Color
from consola_ui import (
    habilitar_ansi_windows, limpiar_pantalla, pausar,
    _centrar_texto, OperacionCancelada,
)
from documentos.generador_documentos import GeneradorDocumentos

from servicios.auth_servicio import AuthServicio
from servicios.empleado_servicio import EmpleadoServicio
from servicios.inventario_servicio import InventarioServicio
from servicios.producto_servicio import ProductoServicio
from servicios.venta_servicio import VentaServicio
from servicios.compra_servicio import CompraServicio
from servicios.merma_servicio import MermaServicio
from servicios.despacho_servicio import DespachoServicio
from servicios.reporte_servicio import ReporteServicio

from interfaz.pantalla_login import PantallaLogin
from interfaz.pantalla_barista import PantallaBarista
from interfaz.pantalla_admin import PantallaAdmin


class AppCoffeelytics:
    def __init__(self):
        habilitar_ansi_windows()
        self.usuario = None
        self.reportes = GeneradorDocumentos()

        self.servicios = {
            "auth": AuthServicio(),
            "empleado": EmpleadoServicio(),
            "inventario": InventarioServicio(),
            "producto": ProductoServicio(),
            "venta": VentaServicio(),
            "compra": CompraServicio(),
            "merma": MermaServicio(),
            "despacho": DespachoServicio(),
            "reporte": ReporteServicio(),
        }

    def _mostrar_error_y_continuar(self, mensaje):
        """Muestra un error de forma visible y espera ENTER antes de volver al inicio."""
        limpiar_pantalla()
        print(_centrar_texto(Color.error(mensaje)))
        pausar()
        self.usuario = None

    def ejecutar(self):
        """
        Bucle principal: login -> panel segun rol -> login.
        Ningun error de base de datos o de captura cierra el programa de forma inesperada:
        se muestra el mensaje y se regresa al inicio de sesion.
        """
        while True:
            try:
                pantalla_login = PantallaLogin(self.servicios["auth"])
                self.usuario = pantalla_login.mostrar()

                if self.usuario is None:
                    break

                if self.usuario.es_admin():
                    pantalla_admin = PantallaAdmin(self.usuario, self.servicios, self.reportes)
                    pantalla_admin.mostrar()
                else:
                    pantalla_barista = PantallaBarista(self.usuario, self.servicios, self.reportes)
                    pantalla_barista.mostrar()

                self.usuario = None
            except OperacionCancelada:
                self._mostrar_error_y_continuar("Operacion cancelada.")
            except ErrorBaseDatos as error:
                self._mostrar_error_y_continuar(
                    f"Error de base de datos: {error}. Revisa el archivo .env y que MySQL este activo."
                )
            except (KeyboardInterrupt, EOFError):
                limpiar_pantalla()
                print(_centrar_texto(Color.aviso("Sesion cerrada por el usuario.")))
                break
            except Exception as error:  # Red de seguridad: el programa nunca se cae por una pantalla.
                self._mostrar_error_y_continuar(f"Error inesperado: {error}")
