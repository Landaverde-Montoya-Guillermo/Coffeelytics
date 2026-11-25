import datetime
import shutil
from typing import Any
from interfaz.estilos import Color
from consola_ui import (
    limpiar_pantalla, pausar, seleccionar_con_flechas,
    imprimir_encabezado_sesion, imprimir_tabla,
    pedir_entero_positivo, pedir_monto_contado,
    imprimir_bloque_centrado, _centrar_texto,
    _ancho, _prefijo, OperacionCancelada, PasoAnterior
)
from config.reglas import IVA_FRONTERA
from consola_ui import tabla_centrada
from documentos.generador_documentos import lineas_corte_caja, ancho_comprobante


class AdminConsultas:
    def __init__(self, usuario, reporte_srv, empleado_srv, producto_srv, reportes):
        self.usuario = usuario
        self.reporte_srv = reporte_srv
        self.empleado_srv = empleado_srv
        self.producto_srv = producto_srv
        self.reportes = reportes

    def menu(self):
        opciones = [
            "C1 - Detalle de venta por folio",
            "C2 - Detalle de compra por folio",
            "C3 - Mermas",
            "C4 - Ventas por barista y fecha",
            "C5 - Insumos de la receta de un producto",
            "Ventas por Barista (Resumen y Detalle)",
            "Corte de Caja del Dia (Resumen y Arqueo)",
            "<< Volver al Menu Admin",
        ]
        while True:
            enc = imprimir_encabezado_sesion(
                self.usuario,
                breadcrumb=["Inicio", "Panel Admin", "Consultas y Reportes"]
            )
            idx = seleccionar_con_flechas("CONSULTAS Y REPORTES", opciones, enc)
            if idx == 0:
                self._consulta_1()
            elif idx == 1:
                self._consulta_2()
            elif idx == 2:
                self._consulta_3()
            elif idx == 3:
                self._consulta_4()
            elif idx == 4:
                self._consulta_5()
            elif idx == 5:
                self._ventas_por_barista()
            elif idx == 6:
                self._corte_caja()
            elif idx == 7:
                return

    def _tabla_ultimos_folios(self):
        """Tabla centrada con los ultimos 15 folios registrados."""
        ventas = self.reporte_srv.listar_ventas_recientes(15)
        cols = ["FOLIO", "FECHA Y HORA", "BARISTA", "METODO PAGO", "TOTAL"]
        filas = [(v["folio"], v["fecha"], v["barista"], v["metodo"], f"${v['total']:.2f}")
                 for v in ventas]
        return tabla_centrada("ULTIMOS 15 FOLIOS REGISTRADOS", cols, filas)

    def _ventas_por_barista(self):
        """Resumen de ventas por barista (tabla centrada) y detalle de tickets del barista elegido."""
        while True:
            limpiar_pantalla()
            try:
                resumen = self.reporte_srv.resumen_ventas_por_barista()
            except Exception as error:
                print(Color.error(str(error)))
                pausar()
                return
            if not resumen:
                print(_centrar_texto(Color.aviso("No hay empleados registrados.")))
                pausar()
                return
            cols = ["ID", "BARISTA", "TICKETS", "TOTAL VENDIDO"]
            filas = [(r["id"], r["barista"], r["tickets"], f"${r['total']:.2f}") for r in resumen]
            enc = "\n".join([
                imprimir_encabezado_sesion(
                    self.usuario,
                    breadcrumb=["Inicio", "Panel Admin", "Consultas", "Ventas por Barista"]
                ),
                tabla_centrada("VENTAS POR BARISTA", cols, filas),
            ])
            opts = [f"{r['id']:<5} {r['barista']:<30} Tickets: {r['tickets']}" for r in resumen]
            opts.append("<< Volver a Consultas")
            idx = seleccionar_con_flechas("VENTAS POR BARISTA - Selecciona barista", opts, enc)
            if idx == len(resumen):
                return
            barista = resumen[idx]
            tickets = self.reporte_srv.detalle_ventas_barista(barista["id"])
            limpiar_pantalla()
            print(imprimir_encabezado_sesion(
                self.usuario,
                breadcrumb=["Inicio", "Panel Admin", "Consultas", "Ventas por Barista", barista["barista"]]
            ))
            print()
            cols_d = ["FOLIO", "FECHA Y HORA", "CLIENTE", "METODO PAGO", "TOTAL"]
            filas_d = [(t["folio"], t["fecha"], t["cliente"], t["metodo"], f"${t['total']:.2f}")
                       for t in tickets]
            print(tabla_centrada(f"TICKETS DE {barista['barista']}", cols_d, filas_d))
            pausar()

    def _corte_caja(self):
        """
        Corte de caja del dia: resumen por metodo de pago, arqueo del efectivo fisico
        y comprobante centrado + respaldo .txt.
        """
        corte = self.reporte_srv.obtener_corte_dia()
        limpiar_pantalla()
        print(imprimir_encabezado_sesion(
            self.usuario,
            breadcrumb=["Inicio", "Panel Admin", "Consultas y Reportes", "Corte de Caja"]
        ))
        print()
        if not corte["metodos"]:
            print(_centrar_texto(Color.aviso("No hay ventas registradas el dia de hoy.")))
            pausar()
            return

        cols = ["Metodo de pago", "Oper.", "Subtotal", "IVA", "Total"]
        filas = [
            (m["metodo"], m["operaciones"], f"${m['subtotal']:.2f}",
             f"${m['iva']:.2f}", f"${m['total']:.2f}")
            for m in corte["metodos"]
        ]
        imprimir_tabla("VENTAS DE HOY POR METODO DE PAGO", cols, filas)
        g = corte["gran"]
        print(_centrar_texto(f"Gran total del dia: {Color.CARAMELO}{Color.BOLD}${g['total']:.2f}{Color.RESET}"))
        print()

        esperado = corte["esperado"]
        while True:
            try:
                contado = pedir_monto_contado(esperado)
                break
            except (OperacionCancelada, PasoAnterior):
                print(Color.aviso("Corte cancelado. No se genero el comprobante."))
                pausar()
                return
            except ValueError as error:
                print(Color.error(str(error)))
                pausar()

        datos = {
            "fecha": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "cajero": self.usuario.nombre_completo,
            "iva_pct": int(round(IVA_FRONTERA * 100)),
            "metodos": corte["metodos"],
            "gran": g,
            "esperado": esperado,
            "contado": contado,
            "diferencia": round(contado - esperado, 2),
            "respaldo": None,
        }
        aviso = None
        try:
            self.reportes.guardar_corte_txt(datos)
        except Exception as error:
            aviso = f"No se pudo guardar el respaldo .txt: {error}"

        limpiar_pantalla()
        print(imprimir_encabezado_sesion(
            self.usuario,
            breadcrumb=["Inicio", "Panel Admin", "Consultas y Reportes", "Corte de Caja", "Comprobante"]
        ))
        print()
        columnas = shutil.get_terminal_size(fallback=(80, 24)).columns
        imprimir_bloque_centrado(lineas_corte_caja(datos, ancho_comprobante(columnas)))
        if aviso:
            print(_centrar_texto(Color.aviso(aviso)))
        print()
        pausar()

    def _consulta_1(self):
        while True:
            limpiar_pantalla()
            print(imprimir_encabezado_sesion(
                self.usuario,
                breadcrumb=["Inicio", "Panel Admin", "Consultas", "C1 - Detalle Venta"]
            ))
            print(f"\n  {Color.titulo('C1 - DETALLE DE VENTA')}\n")
            try:
                # Tabla de referencia: los ultimos 15 folios, para no adivinar folios.
                print(self._tabla_ultimos_folios())
                folio = pedir_entero_positivo(prompt="Numero de folio de venta", ejemplo="1")
                enc_venta, lineas = self.reporte_srv.consulta_1_detalle_venta(folio)
                if not enc_venta:
                    raise ValueError("Venta no encontrada.")

                limpiar_pantalla()
                print(imprimir_encabezado_sesion(
                    self.usuario,
                    breadcrumb=["Inicio", "Panel Admin", "Consultas", f"Venta #{folio}"]
                ))
                pfx = _prefijo(_ancho())
                print(f"\n{pfx}  {Color.titulo('DETALLE VENTA #' + str(folio))}\n")
                print(f"{pfx}  Fecha:        {enc_venta['fecha']}")
                print(f"{pfx}  Cliente:      {enc_venta['nombreCliente']}")
                print(f"{pfx}  Empleado:     {enc_venta['empleado']}")
                print(f"{pfx}  Metodo pago:  {enc_venta['metodoPago']}")
                print(f"{pfx}  Total:        {Color.CARAMELO}${enc_venta['total']:.2f}{Color.RESET}")
                if lineas:
                    cols = ["Codigo", "Producto", "Precio", "Cant.", "Subtotal", "IVA", "Total"]
                    filas = [(l["codigo"], l["nombre"], f"${l['precio']:.2f}",
                              l["cantidad"], f"${l['subtotal']:.2f}",
                              f"${l['totalIVA']:.2f}", f"${l['total']:.2f}") for l in lineas]
                    imprimir_tabla("Productos vendidos", cols, filas)
                    self.reportes.reporte_generico(
                        f"Reporte_C1_Venta_{folio}",
                        "DETALLE VENTA",
                        ["Codigo", "Producto", "Precio", "Cant.", "Subtotal", "IVA", "Total"],
                        [[l["codigo"], l["nombre"], f"${l['precio']:.2f}", l["cantidad"],
                          f"${l['subtotal']:.2f}", f"${l['totalIVA']:.2f}", f"${l['total']:.2f}"]
                         for l in lineas],
                        subtitulo=f"Folio #{folio}",
                        encabezado_extra=f"Cliente: {enc_venta['nombreCliente']}  Empleado: {enc_venta['empleado']}"
                    )
                else:
                    print(Color.aviso("Esta venta no tiene productos registrados. No se genero reporte."))
                pausar()
                return
            except (OperacionCancelada, PasoAnterior):
                return
            except Exception as error:
                print(Color.error(str(error)))
                pausar()

    def _consulta_2(self):
        while True:
            limpiar_pantalla()
            print(imprimir_encabezado_sesion(
                self.usuario,
                breadcrumb=["Inicio", "Panel Admin", "Consultas", "C2 - Detalle Compra"]
            ))
            print(f"\n  {Color.titulo('C2 - DETALLE DE COMPRA')}\n")
            try:
                compras = self.reporte_srv.listar_compras_registradas()
                cols_compras = ["FOLIO", "FECHA", "PROVEEDOR", "EMPLEADO / USUARIO", "TOTAL"]
                filas_compras = [
                    (c["folio"], c["fecha"], c["proveedor"], c["empleado"],
                     f"${c['total']:.2f}")
                    for c in compras
                ]
                imprimir_tabla("COMPRAS REGISTRADAS", cols_compras, filas_compras)
                folio = pedir_entero_positivo(prompt="Numero de folio de compra", ejemplo="1")
                enc_compra, lineas = self.reporte_srv.consulta_2_detalle_compra(folio)
                if not enc_compra:
                    raise ValueError("Compra no encontrada.")
                limpiar_pantalla()
                print(imprimir_encabezado_sesion(
                    self.usuario,
                    breadcrumb=["Inicio", "Panel Admin", "Consultas", f"Compra #{folio}"]
                ))
                pfx = _prefijo(_ancho())
                print(f"\n{pfx}  {Color.titulo('DETALLE COMPRA #' + str(folio))}\n")
                print(f"{pfx}  Fecha:      {enc_compra['fecha']}")
                print(f"{pfx}  Proveedor:  {enc_compra['proveedor']}  ({enc_compra['ciudad']})")
                print(f"{pfx}  Total:      {Color.CARAMELO}${enc_compra['total']:.2f}{Color.RESET}")
                if lineas:
                    cols = ["Codigo", "Insumo", "Precio U.", "Cant.", "Subtotal", "IVA", "Total"]
                    filas = [(l["codigo"], l["nombre"], f"${l['precio']:.2f}",
                              l["cantidad"], f"${l['subtotal']:.2f}",
                              f"${l['totalIVA']:.2f}", f"${l['total']:.2f}") for l in lineas]
                    imprimir_tabla("Insumos comprados", cols, filas)
                self.reportes.reporte_generico(
                    f"Reporte_C2_Compra_{folio}",
                    "DETALLE COMPRA",
                    ["Codigo", "Insumo", "Precio U.", "Cant.", "Subtotal", "IVA", "Total"],
                    [[l["codigo"], l["nombre"], f"${l['precio']:.2f}", l["cantidad"],
                      f"${l['subtotal']:.2f}", f"${l['totalIVA']:.2f}", f"${l['total']:.2f}"]
                     for l in (lineas or [])],
                    subtitulo=f"Folio #{folio}",
                    encabezado_extra=f"Proveedor: {enc_compra['proveedor']}  Ciudad: {enc_compra['ciudad']}"
                )
                pausar()
                return
            except (OperacionCancelada, PasoAnterior):
                return
            except Exception as error:
                print(Color.error(str(error)))
                pausar()

    def _consulta_3(self):
        enc = imprimir_encabezado_sesion(
            self.usuario,
            breadcrumb=["Inicio", "Panel Admin", "Consultas", "C3 - Mermas"]
        )
        opts = [
            "Ver mermas de los ultimos 7 dias",
            "Buscar merma por folio",
            "<< Cancelar y regresar",
        ]
        idx = seleccionar_con_flechas("C3 - MERMAS", opts, enc)
        if idx == 2:
            return

        # Historial de mermas: solo consulta. El registro lo hacen los baristas desde su menu.
        cols = ["FOLIO", "FECHA", "BARISTA", "COD. INSUMO", "INSUMO",
                "CANTIDAD", "TIPO DE MERMA", "MOTIVO"]

        if idx == 0:
            try:
                mermas = self.reporte_srv.consulta_3_mermas_semana()
            except Exception as error:
                print(Color.error(str(error)))
                pausar()
                return
            filas = [(m["codigo"], m["fecha"], m["barista"], m["insumo_codigo"],
                      m["insumo"], m["cantidad"], m["tipo_merma"], m["motivo"])
                     for m in mermas]
            limpiar_pantalla()
            print(imprimir_encabezado_sesion(
                self.usuario,
                breadcrumb=["Inicio", "Panel Admin", "Consultas", "C3 - Mermas 7 dias"]
            ))
            imprimir_tabla("C3 - MERMAS ULTIMOS 7 DIAS", cols, filas)
            self.reportes.reporte_generico(
                "Reporte_C3_Mermas_Semana",
                "MERMAS ULTIMOS 7 DIAS",
                cols, filas,
                subtitulo=datetime.datetime.now().strftime("%d/%m/%Y")
            )
            pausar()

        elif idx == 1:
            while True:
                limpiar_pantalla()
                print(imprimir_encabezado_sesion(
                    self.usuario,
                    breadcrumb=["Inicio", "Panel Admin", "Consultas", "C3 - Merma por folio"]
                ))
                try:
                    folio = pedir_entero_positivo(prompt="Numero de folio de merma", ejemplo="3")
                    merma = self.reporte_srv.consulta_3_merma_por_folio(folio)
                    if not merma:
                        raise ValueError(f"No se encontro la merma con folio {folio}.")
                    limpiar_pantalla()
                    print(imprimir_encabezado_sesion(
                        self.usuario,
                        breadcrumb=["Inicio", "Panel Admin", "Consultas", f"C3 - Merma #{folio}"]
                    ))
                    filas = [(merma["codigo"], merma["fecha"], merma["barista"],
                              merma["insumo_codigo"], merma["insumo"], merma["cantidad"],
                              merma["tipo_merma"], merma["motivo"])]
                    imprimir_tabla(f"C3 - MERMA #{folio}", cols, filas)
                    self.reportes.reporte_generico(
                        f"Reporte_C3_Merma_{folio}",
                        "DETALLE MERMA",
                        cols, filas,
                        subtitulo=f"Folio #{folio}"
                    )
                    pausar()
                    return
                except (OperacionCancelada, PasoAnterior):
                    return
                except Exception as error:
                    print(Color.error(str(error)))
                    pausar()

    def _consulta_4(self):
        while True:
            limpiar_pantalla()
            try:
                baristas = self.empleado_srv.listar_baristas()
                if not baristas:
                    print(Color.aviso("No hay baristas registrados."))
                    pausar()
                    return
                cols_baristas = ["ID", "NOMBRE COMPLETO", "CORREO / USUARIO"]
                filas_baristas = [(b["num"], b["nombre"], b["correo"]) for b in baristas]
                tabla_baristas = imprimir_tabla(
                    "BARISTAS REGISTRADOS", cols_baristas, filas_baristas,
                    retornar_texto=True
                )
                enc = imprimir_encabezado_sesion(
                    self.usuario,
                    breadcrumb=["Inicio", "Panel Admin", "Consultas", "C4 - Ventas por barista"]
                )
                enc = "\n".join([enc, tabla_baristas])
                opts = [f"{b['num']:>4}  {b['nombre']:<30} {b['correo']}"
                        for b in baristas] + ["<< Cancelar y regresar"]
                idx = seleccionar_con_flechas("C4 - Selecciona barista", opts, enc)
                if idx == len(baristas):
                    return
                emp = baristas[idx]
                ventas_barista = self.reporte_srv.detalle_ventas_barista(emp["num"])
                limpiar_pantalla()
                print(imprimir_encabezado_sesion(
                    self.usuario,
                    breadcrumb=["Inicio", "Panel Admin", "Consultas", "C4", emp["nombre"]]
                ))
                pfx = _prefijo(_ancho())
                print(f"\n{pfx}  {Color.titulo('C4 - VENTAS POR BARISTA Y FECHA')}")
                print(f"{pfx}  Barista: {Color.CARAMELO}{emp['nombre']}{Color.RESET}\n")
                cols_ventas = ["CODIGO", "FECHA", "CLIENTE", "METODO DE PAGO", "TOTAL"]
                filas_ventas = [
                    (v["folio"], v["fecha"], v["cliente"], v["metodo"], f"${v['total']:.2f}")
                    for v in ventas_barista
                ]
                imprimir_tabla(f"VENTAS DE {emp['nombre']}", cols_ventas, filas_ventas)
                if not ventas_barista:
                    print(Color.aviso("Este barista aun no tiene ventas registradas."))
                    pausar()
                    return
                while True:
                    try:
                        fecha = input("Fecha a consultar (YYYY-MM-DD): ").strip()
                        if len(fecha) != 10:
                            raise ValueError
                        datetime.datetime.strptime(fecha, "%Y-%m-%d")
                        break
                    except ValueError:
                        print(Color.error(
                            "Fecha invalida. Ingresa una fecha existente con formato YYYY-MM-DD."
                        ))
                        pausar()
                ventas = self.reporte_srv.consulta_4_ventas_por_empleado_fecha(emp["num"], fecha)
                filas = [
                    (v["folio"], v["fecha"], v["nombreCliente"], v["metodoPago"],
                     f"${v['total']:.2f}")
                    for v in ventas
                ]
                limpiar_pantalla()
                print(imprimir_encabezado_sesion(
                    self.usuario,
                    breadcrumb=["Inicio", "Panel Admin", "Consultas", "C4",
                                emp["nombre"], fecha]
                ))
                imprimir_tabla(f"C4 - VENTAS DE {emp['nombre']} EL {fecha}",
                               cols_ventas, filas)
                if not ventas:
                    print(Color.aviso("Este barista no tiene ventas en la fecha seleccionada."))
                self.reportes.reporte_generico(
                    f"Reporte_C4_{emp['num']}_{fecha.replace('-', '')}",
                    "VENTAS POR BARISTA",
                    cols_ventas, filas,
                    subtitulo=f"{emp['nombre']} | {fecha}"
                )
                pausar()
                return
            except (OperacionCancelada, PasoAnterior):
                return
            except Exception as error:
                print(Color.error(str(error)))
                pausar()

    def _consulta_5(self):
        try:
            productos: Any = self.producto_srv.listar_todos_productos()
        except Exception as error:
            print(Color.error(str(error)))
            pausar()
            return
        if not productos:
            print(Color.aviso(texto="No hay productos."))
            pausar()
            return
        enc: str = imprimir_encabezado_sesion(
            empleado=self.usuario,
            breadcrumb=["Inicio", "Panel Admin", "Consultas", "C5 - Receta"]
        )
        opts: list[str] = [f"{p['codigo']:<10} {p['nombre']:<30} {p['categoria']}"
                for p in productos] + ["<< Cancelar y regresar"]
        idx = seleccionar_con_flechas("C5 - Insumos de la receta - Selecciona producto", opts, enc)
        if idx == len(productos):
            return
        prod = productos[idx]
        try:
            receta = self.reporte_srv.consulta_5_insumos_receta(prod["codigo"])
        except Exception as error:
            print(Color.error(str(error)))
            pausar()
            return
        cols = ["Codigo", "Insumo", "Requerido", "Stock Actual", "Unidad"]
        filas = [(r["insumo_codigo"], r["nombre"], r["requerido"],
                  r["stockActual"], r["abreviatura"]) for r in receta]
        limpiar_pantalla()
        print(imprimir_encabezado_sesion(
            self.usuario,
            breadcrumb=["Inicio", "Panel Admin", "Consultas", "C5", prod["nombre"]]
        ))
        imprimir_tabla(f"C5 - RECETA: {prod['nombre']}", cols, filas)
        self.reportes.reporte_generico(
            f"Reporte_C5_Receta_{prod['codigo']}",
            "INSUMOS DE RECETA",
            cols, filas,
            subtitulo=prod["nombre"]
        )
        pausar()
