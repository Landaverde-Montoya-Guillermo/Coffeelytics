import shutil

from config.negocio import INFO_CAFETERIA
from interfaz.estilos import Color
from documentos.generador_documentos import lineas_ticket, ancho_ticket
from interfaz.visor_cliente import renderizar_visor_coffeelytics
from consola_ui import (
    limpiar_pantalla, pausar, seleccionar_con_flechas,
    imprimir_encabezado_sesion, pedir_nombre_cliente,
    pedir_monto_efectivo, _imprimir_guia, _input_centrado,
    _ancho, _prefijo, OperacionCancelada, PasoAnterior,
    imprimir_bloque_centrado, _centrar_texto
)


class ModalCobro:
    def __init__(self, usuario, carrito, venta_servicio, reportes):
        self.usuario = usuario
        self.carrito = carrito
        self.venta_servicio = venta_servicio
        self.reportes = reportes

    def procesar(self):
        """Procesa el pago, guarda la venta y muestra el ticket. Devuelve True si se cobro."""
        limpiar_pantalla()
        recibido = None
        cambio = 0.0
        try:
            enc = imprimir_encabezado_sesion(
                self.usuario,
                breadcrumb=["Inicio", "Panel Barista", "Nueva Venta", "Carrito", "Cobro"]
            )
            print(enc)
            pfx = _prefijo(_ancho())
            total_venta = self.carrito.calcular_total()
            print(renderizar_visor_coffeelytics(self.carrito, ultimo_evento="LISTO PARA COBRAR"))
            print()

            while True:
                try:
                    nombre_cliente = pedir_nombre_cliente()
                    break
                except ValueError as error:
                    print(Color.error(str(error)))
                    pausar()

            metodos = [
                ("EFEC", "Efectivo"),
                ("TARJ", "Tarjeta bancaria"),
                ("TRAN", "Transferencia Electronica"),
            ]
            enc2 = "\n".join([
                imprimir_encabezado_sesion(
                    self.usuario,
                    breadcrumb=["Inicio", "Panel Barista", "Nueva Venta", "Carrito", "Cobro", "Metodo de pago"]
                ),
                renderizar_visor_coffeelytics(self.carrito, ultimo_evento="LISTO PARA COBRAR"),
            ])
            opciones_pago = [m[1] for m in metodos] + ["<< Cancelar cobro"]
            idx_m = seleccionar_con_flechas("Metodo de pago", opciones_pago, enc2)
            if idx_m == len(metodos):
                print(Color.aviso("Operacion cancelada. No se registro la venta."))
                pausar()
                return False
            cod_pago, desc_pago = metodos[idx_m]

            if cod_pago == "EFEC":
                limpiar_pantalla()
                print(imprimir_encabezado_sesion(
                    self.usuario,
                    breadcrumb=["Inicio", "Panel Barista", "Nueva Venta", "Cobro", "Efectivo"]
                ))
                print(renderizar_visor_coffeelytics(self.carrito, ultimo_evento="LISTO PARA COBRAR"))
                while True:
                    try:
                        recibido, cambio = pedir_monto_efectivo(total_venta)
                        break
                    except ValueError as error:
                        print(Color.error(str(error)))
                        pausar()
            elif cod_pago == "TARJ":
                _imprimir_guia(
                    "Pago con tarjeta bancaria en terminal POS",
                    "Pasa la tarjeta en el lector POS y presiona ENTER para confirmar",
                    "ENTER",
                    "El sistema registra el pago con metodo TARJ sin datos de la tarjeta."
                )
                confirmacion = _input_centrado(
                    "Presiona ENTER cuando el cobro en terminal sea confirmado"
                )
                if confirmacion.strip().upper() in ("0", "CANCELAR"):
                    raise OperacionCancelada()
            elif cod_pago == "TRAN":
                _imprimir_guia(
                    "Pago por Transferencia SPEI",
                    "El cliente transfiere a la CLABE indicada y presiona ENTER para confirmar",
                    "ENTER",
                    f"CLABE: {INFO_CAFETERIA['clabe_transferencia']}  Banco: {INFO_CAFETERIA['banco']}"
                )
                print(f"{pfx}  {Color.CARAMELO}CLABE: {INFO_CAFETERIA['clabe_transferencia']}  "
                      f"Banco: {INFO_CAFETERIA['banco']}{Color.RESET}")
                confirmacion = _input_centrado(
                    "Presiona ENTER cuando recibas la confirmacion de la transferencia"
                )
                if confirmacion.strip().upper() in ("0", "CANCELAR"):
                    raise OperacionCancelada()
        except (OperacionCancelada, PasoAnterior):
            print(Color.aviso("Operacion cancelada. No se registro la venta."))
            pausar()
            return False
        except Exception as error:
            print(Color.error(str(error)))
            pausar()
            return False

        self.carrito.nombre_cliente = nombre_cliente
        try:
            ok, msg, folio = self.venta_servicio.registrar_venta(
                self.carrito, cod_pago, self.usuario.num
            )
        except Exception as error:
            print(Color.error(str(error)))
            pausar()
            return False
        if not ok:
            print(Color.error(msg))
            pausar()
            return False

        # Venta registrada en MySQL: se construye el comprobante antes de vaciar el carrito.
        datos = self.reportes.datos_ticket(
            folio, self.carrito, desc_pago, self.usuario,
            recibido=recibido, cambio=cambio
        )
        aviso_respaldo = None
        try:
            self.reportes.guardar_ticket_txt(datos)
        except Exception as error:
            datos["respaldo"] = None
            aviso_respaldo = f"No se pudo guardar el respaldo .txt: {error}"
        try:
            self.reportes.ticket_venta(
                folio, self.carrito, desc_pago, self.usuario, cambio
            )
        except Exception as error:
            aviso_respaldo = aviso_respaldo or f"No se pudo generar el PDF: {error}"

        limpiar_pantalla()
        print(imprimir_encabezado_sesion(
            self.usuario,
            breadcrumb=["Inicio", "Panel Barista", "Nueva Venta", "Cobro", "Ticket"]
        ))
        print()
        columnas = shutil.get_terminal_size(fallback=(80, 24)).columns
        imprimir_bloque_centrado(lineas_ticket(datos, ancho_ticket(columnas)))
        if aviso_respaldo:
            print(_centrar_texto(Color.aviso(aviso_respaldo)))
        print()
        pausar("Presiona ENTER para continuar y volver al menu...")

        self.carrito.vaciar()
        return True
