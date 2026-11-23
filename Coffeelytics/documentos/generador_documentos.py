import os
import datetime
import textwrap
from fpdf import FPDF
from config.negocio import INFO_CAFETERIA
from config.reglas import IVA_FRONTERA
from interfaz.estilos import Color
from documentos.caja_texto import Caja

# Carpeta de salida absoluta (relativa a este archivo), independiente del directorio de ejecucion.
_RAIZ_PROYECTO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


class GeneradorDocumentos:
    """Genera tickets de venta y reportes administrativos en PDF dentro de documentos/salida/."""

    DIRECTORIO = os.path.join(_RAIZ_PROYECTO, "documentos", "salida")

    def __init__(self):
        os.makedirs(self.DIRECTORIO, exist_ok=True)

    def _ruta(self, nombre_archivo):
        # Garantiza la carpeta aunque haya sido borrada durante la sesion.
        os.makedirs(self.DIRECTORIO, exist_ok=True)
        return os.path.join(self.DIRECTORIO, nombre_archivo)

    def ticket_venta(self, folio, carrito, metodo_desc, empleado, cambio=0.0):
        """Muestra resumen en consola y exporta el ticket térmico en PDF."""
        ahora = datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S")

        # Configurar PDF formato ticket térmico (80mm ancho)
        pdf = FPDF(orientation="P", unit="mm", format=(80, 180))
        pdf.set_auto_page_break(auto=True, margin=8)
        pdf.add_page()
        pdf.set_margins(5, 5, 5)

        # Encabezado Cafetería
        pdf.set_font("Helvetica", "B", 11)
        pdf.cell(0, 5, INFO_CAFETERIA["nombre"], new_x="LMARGIN", new_y="NEXT", align="C")
        pdf.set_font("Helvetica", "", 7)
        pdf.cell(0, 4, INFO_CAFETERIA["eslogan"], new_x="LMARGIN", new_y="NEXT", align="C")
        pdf.cell(0, 4, INFO_CAFETERIA["direccion"], new_x="LMARGIN", new_y="NEXT", align="C")
        pdf.cell(0, 4, f"RFC: {INFO_CAFETERIA['rfc']} | Tel: {INFO_CAFETERIA['telefono']}", new_x="LMARGIN", new_y="NEXT", align="C")
        pdf.ln(2)
        pdf.cell(0, 0, "", "T", new_x="LMARGIN", new_y="NEXT")
        pdf.ln(2)

        # Datos de la venta
        pdf.set_font("Helvetica", "B", 8)
        pdf.cell(0, 4, f"TICKET #: {folio}", new_x="LMARGIN", new_y="NEXT")
        pdf.set_font("Helvetica", "", 7)
        pdf.cell(0, 4, f"Fecha: {ahora}", new_x="LMARGIN", new_y="NEXT")
        pdf.cell(0, 4, f"Atendio: {empleado.nombre_completo}", new_x="LMARGIN", new_y="NEXT")
        pdf.cell(0, 4, f"Cliente: {carrito.nombre_cliente}", new_x="LMARGIN", new_y="NEXT")
        pdf.ln(2)
        pdf.cell(0, 0, "", "T", new_x="LMARGIN", new_y="NEXT")
        pdf.ln(2)

        # Tabla de productos
        pdf.set_font("Helvetica", "B", 7)
        pdf.cell(36, 4, "PRODUCTO")
        pdf.cell(8, 4, "PZS", align="R")
        pdf.cell(12, 4, "PREC", align="R")
        pdf.cell(14, 4, "TOT", align="R", new_x="LMARGIN", new_y="NEXT")
        pdf.set_font("Helvetica", "", 7)

        for item in carrito.items.values():
            prod = item["producto"]
            cant = item["cantidad"]
            tot = prod.precio * cant
            nombre_corto = prod.nombre[:20]
            pdf.cell(36, 4, nombre_corto)
            pdf.cell(8, 4, str(cant), align="R")
            pdf.cell(12, 4, f"${prod.precio:.2f}", align="R")
            pdf.cell(14, 4, f"${tot:.2f}", align="R", new_x="LMARGIN", new_y="NEXT")

        pdf.ln(2)
        pdf.cell(0, 0, "", "T", new_x="LMARGIN", new_y="NEXT")
        pdf.ln(2)

        # Totales
        tot = carrito.calcular_total()  # el precio ya incluye IVA; no se muestra desglose

        pdf.set_font("Helvetica", "B", 8)
        pdf.cell(56, 5, "TOTAL:", align="R")
        pdf.cell(14, 5, f"${tot:.2f}", align="R", new_x="LMARGIN", new_y="NEXT")

        pdf.ln(2)
        pdf.set_font("Helvetica", "", 7)
        pdf.cell(0, 4, f"Metodo de pago: {metodo_desc}", new_x="LMARGIN", new_y="NEXT")
        if metodo_desc == "Efectivo" and cambio > 0:
            pdf.cell(0, 4, f"Cambio entregado: ${cambio:.2f}", new_x="LMARGIN", new_y="NEXT")
        if metodo_desc == "Transferencia SPEI":
            pdf.cell(0, 4, f"CLABE: {INFO_CAFETERIA['clabe_transferencia']}", new_x="LMARGIN", new_y="NEXT")
            pdf.cell(0, 4, f"Banco: {INFO_CAFETERIA['banco']}", new_x="LMARGIN", new_y="NEXT")

        pdf.ln(3)
        pdf.set_font("Helvetica", "I", 7)
        pdf.cell(0, 4, "Gracias por su visita!", new_x="LMARGIN", new_y="NEXT", align="C")

        ruta = self._ruta(f"Ticket_Venta_{folio}.pdf")
        pdf.output(ruta)
        return ruta

    # ── COMPROBANTE DE VENTA (TICKET EN CONSOLA Y RESPALDO .TXT) ─────────────

    def ruta_respaldo_txt(self, folio):
        return self._ruta(f"Ticket_Venta_{folio}.txt")

    def datos_ticket(self, folio, carrito, metodo_desc, empleado,
                     recibido=None, cambio=0.0, fecha=None):
        """Reune los datos del comprobante. No escribe archivos."""
        cliente = (carrito.nombre_cliente or "").strip()
        if not cliente or cliente.lower() == "mostrador":
            cliente = "Publico General"
        items = []
        for item in carrito.items.values():
            prod = item["producto"]
            cant = item["cantidad"]
            items.append((cant, prod.nombre, prod.precio, round(prod.precio * cant, 2)))
        ruta = self.ruta_respaldo_txt(folio)
        return {
            "folio": f"#{int(folio):05d}",
            "folio_num": int(folio),
            "fecha": fecha or carrito.fecha_venta
                     or datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "atendido": empleado.nombre_completo,
            "cliente": cliente,
            "items": items,
            "subtotal": carrito.calcular_subtotal(),
            "iva": carrito.calcular_iva(),
            "iva_pct": int(round(IVA_FRONTERA * 100)),
            "total": carrito.calcular_total(),
            "metodo": metodo_desc,
            "recibido": recibido,
            "cambio": cambio,
            "respaldo": os.path.relpath(ruta, _RAIZ_PROYECTO).replace(os.sep, "/"),
        }

    def guardar_ticket_txt(self, datos):
        """Escribe el respaldo .txt. Si falla, lanza la excepcion al llamador."""
        os.makedirs(self.DIRECTORIO, exist_ok=True)
        ruta = self.ruta_respaldo_txt(datos["folio_num"])
        contenido = "\n".join(texto for texto, _ in lineas_ticket(datos)) + "\n"
        with open(ruta, "w", encoding="utf-8") as archivo:
            archivo.write(contenido)
        return ruta

    def _escribir_txt(self, ruta, lineas, datos):
        """Escribe el respaldo .txt con el mismo contenido que se imprime en consola."""
        os.makedirs(self.DIRECTORIO, exist_ok=True)
        datos["respaldo"] = os.path.relpath(ruta, _RAIZ_PROYECTO).replace(os.sep, "/")
        contenido = "\n".join(texto for texto, _ in lineas) + "\n"
        with open(ruta, "w", encoding="utf-8") as archivo:
            archivo.write(contenido)
        return ruta

    def guardar_comprobante_compra_txt(self, datos):
        ruta = self._ruta(f"Compra_{datos['folio_num']}.txt")
        return self._escribir_txt(ruta, lineas_comprobante_compra(datos), datos)

    def guardar_corte_txt(self, datos):
        stamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        ruta = self._ruta(f"Corte_Caja_{stamp}.txt")
        return self._escribir_txt(ruta, lineas_corte_caja(datos), datos)

    def reporte_generico(self, nombre_archivo, titulo, columnas, filas,
                         subtitulo="", encabezado_extra=""):
        """Exporta el reporte administrativo en PDF si el usuario lo confirma."""
        print(Color.info(f"\nDeseas exportar el reporte a PDF? ({nombre_archivo}.pdf)"))
        print(Color.aviso("  [S] Si exportar     [cualquier tecla] No exportar"))
        respuesta = input("  > ").strip().upper()
        if respuesta != "S":
            return

        ahora = datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        pdf = FPDF(orientation="L", unit="mm", format="Letter")
        pdf.add_page()

        # Encabezado
        pdf.set_font("Helvetica", "B", 14)
        pdf.cell(0, 7, f"{INFO_CAFETERIA['nombre']} - {titulo}", new_x="LMARGIN", new_y="NEXT")
        pdf.set_font("Helvetica", "", 9)
        if subtitulo:
            pdf.cell(0, 5, f"Detalle: {subtitulo}", new_x="LMARGIN", new_y="NEXT")
        if encabezado_extra:
            pdf.cell(0, 5, encabezado_extra, new_x="LMARGIN", new_y="NEXT")
        pdf.cell(0, 5, f"Generado: {ahora}", new_x="LMARGIN", new_y="NEXT")
        pdf.ln(4)

        # Normalizar filas
        if filas and isinstance(filas[0], dict):
            filas_limpias = [[str(f.get(c, "")) for c in columnas] for f in filas]
        else:
            filas_limpias = [[str(c2) for c2 in fila] for fila in filas]

        ancho_disponible = pdf.w - 20
        ancho_col = ancho_disponible / max(1, len(columnas))

        # Cabecera de tabla
        pdf.set_font("Helvetica", "B", 8)
        pdf.set_fill_color(130, 80, 40)
        pdf.set_text_color(255, 255, 255)
        for col in columnas:
            pdf.cell(ancho_col, 7, str(col)[:25], border=1, align="C", fill=True)
        pdf.ln()

        # Filas de tabla
        pdf.set_font("Helvetica", "", 8)
        pdf.set_text_color(0, 0, 0)
        if not filas_limpias:
            pdf.cell(ancho_disponible, 7, "(Sin registros)", border=1, align="C", new_x="LMARGIN", new_y="NEXT")
        else:
            for fila in filas_limpias:
                for i in range(len(columnas)):
                    val = fila[i] if i < len(fila) else ""
                    pdf.cell(ancho_col, 6, str(val)[:28], border=1, align="C")
                pdf.ln()

        ruta = self._ruta(f"{nombre_archivo}.pdf")
        pdf.output(ruta)
        print(Color.ok(f"Reporte PDF guardado: {ruta}"))


# ── CONSTRUCTORES DE COMPROBANTES (consola y archivo .txt comparten el mismo contenido) ──

TICKET_ANCHO_IDEAL = 60
TICKET_ANCHO_MINIMO = 34      # minimo absoluto del ticket
TICKET_ANCHO_TABLA = 46       # desde este ancho el detalle usa tabla; debajo, bloque por producto
COMPROBANTE_ANCHO_MINIMO = 46


def ancho_ticket(columnas_terminal):
    """Ancho del ticket: 60 columnas, reducido si la terminal es mas angosta."""
    return max(TICKET_ANCHO_MINIMO, min(TICKET_ANCHO_IDEAL, columnas_terminal - 2))


def ancho_comprobante(columnas_terminal):
    return max(COMPROBANTE_ANCHO_MINIMO, min(TICKET_ANCHO_IDEAL, columnas_terminal - 2))


def _dinero(valor):
    return f"${float(valor):.2f}"


def estatus_arqueo(diferencia):
    """Estatus del arqueo y su estilo visual, segun la diferencia (contado - esperado)."""
    if diferencia == 0:
        return "[OK] CAJA CUADRADA EXACTA", "total"
    if diferencia > 0:
        return f"[!] SOBRANTE EN CAJA: +{_dinero(diferencia)}", "aviso"
    return f"[X] FALTANTE EN CAJA: -{_dinero(abs(diferencia))}", "error"


def lineas_ticket(datos, ancho=TICKET_ANCHO_IDEAL):
    """Ticket de venta como lista de (texto, estilo). Todas las lineas miden `ancho`."""
    c = Caja(max(TICKET_ANCHO_MINIMO, int(ancho)))
    pn = c.util - 31                       # columna PRODUCTO (solo modo tabla)

    c.marco("╔", "═", "╗")
    c.texto("COFFEELYTICS - PUNTO DE VENTA", "titulo", "c")
    c.texto("TICKET OFICIAL DE VENTA", None, "c")
    c.marco("╠", "═", "╣")
    c.dato("Folio de venta:", datos["folio"])
    c.dato("Fecha y hora:", datos["fecha"])
    c.dato("Atendido por:", datos["atendido"])
    c.dato("Cliente:", datos["cliente"])
    c.marco("╟", "─", "╢")

    if c.ancho >= TICKET_ANCHO_TABLA:
        c.fila_exacta(f"{'CANT':>4} │ {'PRODUCTO':<{pn}} │ {'P.UNIT':>9} │ {'IMPORTE':>9}", "negrita")
        c.fila_exacta("─" * 4 + "─┼─" + "─" * pn + "─┼─" + "─" * 9 + "─┼─" + "─" * 9)
        for cant, nombre, precio, importe in datos["items"]:
            partes = textwrap.wrap(nombre, pn) or [""]
            c.fila_exacta(f"{cant:>4} │ {partes[0]:<{pn}} │ {_dinero(precio):>9} │ {_dinero(importe):>9}")
            for parte in partes[1:]:
                c.fila_exacta(f"{'':>4} │ {parte:<{pn}} │ {'':>9} │ {'':>9}")
    else:
        # Terminal estrecha: cada producto ocupa dos renglones, nada se recorta.
        for cant, nombre, precio, importe in datos["items"]:
            for parte in (textwrap.wrap(f"{cant} x {nombre}", c.util) or [""]):
                c.fila_exacta(parte)
            c.fila_exacta(f"  {_dinero(precio)} c/u".ljust(c.util - 12) + f"{_dinero(importe):>12}")
    c.marco("╟", "─", "╢")

    # El precio ya incluye IVA: al cliente solo se le muestra el total a pagar.
    c.alineado_derecha("TOTAL A PAGAR:", _dinero(datos["total"]), "total")
    c.marco("╟", "─", "╢")

    c.dato("Metodo de pago:", datos["metodo"])
    if datos["metodo"] == "Efectivo" and datos.get("recibido") is not None:
        c.dato("Efectivo recibido:", _dinero(datos["recibido"]))
        c.dato("Cambio entregado:", _dinero(datos["cambio"] or 0.0))
    c.marco("╟", "─", "╢")

    c.texto("Gracias por su preferencia", "titulo", "c")
    _pie_respaldo(c, datos)
    c.marco("╚", "═", "╝")
    return c.resultado()


def lineas_comprobante_compra(datos, ancho=TICKET_ANCHO_IDEAL):
    """Comprobante de compra a proveedor (insumos) como lista de (texto, estilo)."""
    c = Caja(max(COMPROBANTE_ANCHO_MINIMO, int(ancho)))
    pn = c.util - 34                       # columna INSUMO

    c.marco("╔", "═", "╗")
    c.texto("COFFEELYTICS - COMPRAS A PROVEEDOR", "titulo", "c")
    c.texto("COMPROBANTE DE COMPRA A PROVEEDOR", None, "c")
    c.marco("╠", "═", "╣")
    c.dato("Folio de compra:", datos["folio"])
    c.dato("Fecha y hora:", datos["fecha"])
    c.dato("Proveedor:", f"{datos['proveedor']} ({datos['ciudad']})")
    c.dato("Autorizo:", datos["autorizo"])
    c.dato("Metodo de pago:", datos["metodo"])
    c.marco("╟", "─", "╢")

    c.fila_exacta(f"{'CANT':>7} │ {'INSUMO':<{pn}} │ {'C.UNIT':>9} │ {'IMPORTE':>9}", "negrita")
    c.fila_exacta("─" * 7 + "─┼─" + "─" * pn + "─┼─" + "─" * 9 + "─┼─" + "─" * 9)
    partes = textwrap.wrap(datos["insumo"], pn) or [""]
    c.fila_exacta(f"{datos['cantidad']:>7g} │ {partes[0]:<{pn}} │ "
                  f"{_dinero(datos['costo_unit']):>9} │ {_dinero(datos['subtotal']):>9}")
    for parte in partes[1:]:
        c.fila_exacta(f"{'':>7} │ {parte:<{pn}} │ {'':>9} │ {'':>9}")
    c.marco("╟", "─", "╢")

    c.alineado_derecha("Subtotal:", _dinero(datos["subtotal"]))
    c.alineado_derecha(f"IVA ({datos['iva_pct']}%):", _dinero(datos["iva"]))
    c.alineado_derecha("TOTAL COMPRA:", _dinero(datos["total"]), "total")
    c.marco("╟", "─", "╢")

    c.dato("Stock anterior:", f"{datos['stock_anterior']:g} {datos['unidad']}")
    c.dato("Stock actualizado:", f"{datos['stock_nuevo']:g} {datos['unidad']}", estilo="negrita")
    c.texto("[OK] Stock del insumo actualizado en inventario", "titulo", "c")
    c.marco("╟", "─", "╢")
    _pie_respaldo(c, datos)
    c.marco("╚", "═", "╝")
    return c.resultado()


def lineas_corte_caja(datos, ancho=TICKET_ANCHO_IDEAL):
    """Corte de caja del dia con arqueo de efectivo como lista de (texto, estilo)."""
    c = Caja(max(COMPROBANTE_ANCHO_MINIMO, int(ancho)))
    c.marco("╔", "═", "╗")
    c.texto("COFFEELYTICS - CORTE DE CAJA", "titulo", "c")
    c.texto("RESUMEN Y ARQUEO DEL DIA", None, "c")
    c.marco("╠", "═", "╣")
    c.dato("Fecha:", datos["fecha"])
    c.dato("Realizo el corte:", datos["cajero"])
    c.marco("╟", "─", "╢")

    if not datos["metodos"]:
        c.texto("[!] No hay ventas registradas el dia de hoy", "aviso", "c")
    else:
        c.texto("VENTAS POR METODO DE PAGO", "negrita")
        for m in datos["metodos"]:
            c.texto(f"{m['metodo']} - {m['operaciones']} operacion(es)", "negrita")
            c.dato("   Subtotal:", _dinero(m["subtotal"]))
            c.dato(f"   IVA ({datos['iva_pct']}%):", _dinero(m["iva"]))
            c.dato("   Total:", _dinero(m["total"]))
        c.marco("╟", "─", "╢")
        g = datos["gran"]
        c.texto("GRAN TOTAL DEL DIA", "negrita")
        c.dato("Operaciones:", g["operaciones"])
        c.alineado_derecha("Subtotal:", _dinero(g["subtotal"]))
        c.alineado_derecha(f"IVA ({datos['iva_pct']}%):", _dinero(g["iva"]))
        c.alineado_derecha("GRAN TOTAL:", _dinero(g["total"]), "total")
        c.marco("╟", "─", "╢")
        c.texto("ARQUEO DE EFECTIVO", "titulo", "c")
        c.dato("Efectivo Esperado (Sistema):", _dinero(datos["esperado"]), ancho_et=29)
        c.dato("Efectivo Contado (Fisico):", _dinero(datos["contado"]), ancho_et=29)
        texto_estatus, estilo = estatus_arqueo(datos["diferencia"])
        c.texto(texto_estatus, estilo, "c")
    c.marco("╟", "─", "╢")
    _pie_respaldo(c, datos)
    c.marco("╚", "═", "╝")
    return c.resultado()


def _pie_respaldo(c, datos):
    if datos.get("respaldo"):
        c.texto("Respaldo guardado en:", None, "c")
        c.texto(datos["respaldo"], "dim", "c")
    else:
        c.texto("Respaldo .txt no disponible", "aviso", "c")
