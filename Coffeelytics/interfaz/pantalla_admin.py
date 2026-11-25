from interfaz.estilos import Color
from interfaz.admin_inventario import AdminInventario
from interfaz.admin_productos import AdminProductos
from interfaz.admin_consultas import AdminConsultas
from interfaz.admin_empleados import AdminEmpleados
from consola_ui import (
    limpiar_pantalla, pausar, seleccionar_con_flechas,
    imprimir_encabezado_sesion, ejecutar_accion,
    _ancho, _prefijo, _columnas, formatear_bloque_centrado
)
from documentos.caja_texto import Caja

MAX_ALERTAS_MOSTRADAS = 5  # Lineas de detalle en la caja de alerta del menu principal.


def _es_admin_principal(usuario):
    """True solo para la cuenta fundadora num==1."""
    return usuario is not None and usuario.es_admin() and usuario.num == 1


def _acceso_denegado():
    print(Color.aviso("Acceso restringido: requiere privilegios de Administrador Principal."))
    pausar()
    return False


class PantallaAdmin:
    def __init__(self, usuario, servicios, reportes):
        self.usuario = usuario
        self.inventario_srv = servicios["inventario"]
        self.reporte_srv = servicios["reporte"]
        self.compra_srv = servicios["compra"]
        self.producto_srv = servicios["producto"]
        self.empleado_srv = servicios["empleado"]
        self.reportes = reportes
        self.inventario_ui = AdminInventario(
            usuario,
            servicios["inventario"],
            servicios["compra"],
            reportes
        )
        self.productos_ui = AdminProductos(
            usuario,
            servicios["producto"],
            servicios["inventario"]
        )
        self.consultas_ui = AdminConsultas(
            usuario,
            servicios["reporte"],
            servicios["empleado"],
            servicios["producto"],
            reportes
        )
        self.empleados_ui = AdminEmpleados(
            usuario,
            servicios["empleado"]
        )

    def mostrar(self):
        es_principal = _es_admin_principal(self.usuario)
        marca = "" if es_principal else "  [Solo Admin Principal]"
        opciones = [
            "Alertas de stock bajo",
            "Consultar stock del inventario",
            f"Resumen financiero{marca}",
            "Registrar compra a proveedor",
            "Registrar nuevo insumo",
            f"Asignar insumo a receta de producto{marca}",
            f"Anadir nuevo producto{marca}",
            "Consultas de reportes (exportar .txt)",
            "Gestion de empleados (CRUD)",
            "<< Cerrar sesion y volver al Inicio",
        ]
        while True:
            enc = imprimir_encabezado_sesion(
                self.usuario,
                breadcrumb=["Inicio", "Panel Admin"]
            )
            # La alerta preventiva va arriba del encabezado; se recalcula en cada redibujado.
            alerta = self._caja_alertas_stock()
            encabezado = "\n".join(parte for parte in (alerta, enc) if parte)
            idx = seleccionar_con_flechas("MENU ADMINISTRADOR", opciones, encabezado)
            if idx == 0:
                ejecutar_accion(self._alertas_stock)
            elif idx == 1:
                ejecutar_accion(self._consultar_stock)
            elif idx == 2:
                if not es_principal:
                    _acceso_denegado()
                else:
                    ejecutar_accion(self._resumen_financiero)
            elif idx == 3:
                ejecutar_accion(self._registrar_compra)
            elif idx == 4:
                ejecutar_accion(self._registrar_insumo)
            elif idx == 5:
                if not es_principal:
                    _acceso_denegado()
                else:
                    ejecutar_accion(self._asignar_insumo_receta)
            elif idx == 6:
                if not es_principal:
                    _acceso_denegado()
                else:
                    ejecutar_accion(self._alta_producto)
            elif idx == 7:
                ejecutar_accion(self._menu_consultas)
            elif idx == 8:
                ejecutar_accion(self._gestion_empleados)
            elif idx == 9:
                return
            
    def _caja_alertas_stock(self):
        """
        Caja de alerta preventiva con los insumos en nivel critico o agotados (stockActual <= stockMin).
        Devuelve "" si no hay alertas. Si la consulta falla, muestra un aviso sin bloquear el menu.
        """
        try:
            alertas = self.inventario_srv.obtener_alertas_stock_bajo()
        except Exception as error:
            return formatear_bloque_centrado([(f"[!] No se pudo consultar el stock: {error}", "aviso")])
        if not alertas:
            return ""

        ancho = max(44, min(72, _columnas() - 4))
        c = Caja(ancho)
        c.marco("╔", "═", "╗")
        c.texto("[!] ALERTA PREVENTIVA DE STOCK", "aviso", "c")
        c.texto(f"{len(alertas)} insumo(s) por reabastecer", None, "c")
        c.marco("╟", "─", "╢")
        for a in alertas[:MAX_ALERTAS_MOSTRADAS]:
            actual = float(a["stockActual"])
            minimo = float(a["stockMin"])
            unidad = a.get("abreviatura") or ""
            etiqueta = "[X] AGOTADO" if actual <= 0 else "[!] CRITICO"
            c.texto(f"{etiqueta}  {a['nombre']}")
            c.texto(f"    Stock actual: {actual:g} {unidad}   Minimo: {minimo:g} {unidad}")
        restantes = len(alertas) - MAX_ALERTAS_MOSTRADAS
        if restantes > 0:
            c.texto(f"... y {restantes} insumo(s) mas. Revisa 'Alertas de stock bajo'.", "dim", "c")
        c.marco("╚", "═", "╝")
        return formatear_bloque_centrado(c.resultado())

    def _alertas_stock(self):
        self.inventario_ui.alertas_stock()

    def _consultar_stock(self):
        self.inventario_ui.consultar_stock()

    def _resumen_financiero(self):
        periodos = ["HOY", "SEMANA", "MES", "ANIO"]
        descs = ["Hoy", "Esta semana", "Este mes", "Este anio"]
        enc = imprimir_encabezado_sesion(
            self.usuario,
            breadcrumb=["Inicio", "Panel Admin", "Resumen Financiero"]
        )
        opts = descs + ["<< Volver al Menu Admin"]
        idx = seleccionar_con_flechas("RESUMEN FINANCIERO - Periodo", opts, enc)
        if idx == len(periodos):
            return
        periodo = periodos[idx]
        datos = self.reporte_srv.obtener_resumen_financiero(periodo)
        limpiar_pantalla()
        print(imprimir_encabezado_sesion(
            self.usuario,
            breadcrumb=["Inicio", "Panel Admin", "Resumen Financiero", descs[idx]]
        ))
        ancho_ui = _ancho()
        pfx = _prefijo(ancho_ui)
        sep = pfx + Color.aplicar(Color.CARAMELO, "═" * min(56, ancho_ui - 4))
        print(f"\n{sep}")
        print(f"{pfx}  {Color.titulo('RESUMEN FINANCIERO')}  [{descs[idx].upper()}]")
        print(sep)
        print(f"{pfx}  Ventas realizadas:  {Color.CARAMELO}{datos['num_ventas']}{Color.RESET}")
        print(f"{pfx}  Ingresos totales:   {Color.VERDE_OK}${datos['ingresos']:,.2f}{Color.RESET}")
        print(f"{pfx}  Gastos en insumos:  {Color.ROJO_ALT}${datos['gastos_insumos']:,.2f}{Color.RESET}")
        color_gan = Color.VERDE_OK if datos['ganancia_bruta'] >= 0 else Color.ROJO_ALT
        print(f"{pfx}  Ganancia bruta:     {Color.BOLD}{color_gan}${datos['ganancia_bruta']:,.2f}{Color.RESET}")
        print(sep)
        pausar()

    def _registrar_compra(self):
        self.inventario_ui.registrar_compra()

    def _registrar_insumo(self):
        self.inventario_ui.registrar_insumo()

    def _asignar_insumo_receta(self):
        self.productos_ui.asignar_insumo_receta()

    def _alta_producto(self):
        self.productos_ui.alta_producto()

    def _menu_consultas(self):
        self.consultas_ui.menu()

    def _gestion_empleados(self):
        self.empleados_ui.gestion()