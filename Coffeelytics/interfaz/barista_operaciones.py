from interfaz.estilos import Color
from consola_ui import tabla_centrada
from config.reglas import UNIDADES_CONTEO_ENTERO
from consola_ui import (
    limpiar_pantalla, pausar, seleccionar_con_flechas,
    imprimir_encabezado_sesion,
    pedir_numero_positivo, pedir_motivo,
    _ancho, _prefijo, OperacionCancelada
)


class BaristaOperaciones:
    def __init__(self, usuario, inventario_srv, despacho_srv, empleado_srv, merma_srv):
        self.usuario = usuario
        self.inventario_srv = inventario_srv
        self.despacho_srv = despacho_srv
        self.empleado_srv = empleado_srv
        self.merma_srv = merma_srv

    def registrar_merma(self):
        limpiar_pantalla()
        try:
            insumos = self.inventario_srv.listar_todos_insumos()
            tipos_merma = self.merma_srv.listar_tipos_merma()
        except Exception as error:
            print(Color.error(str(error)))
            pausar()
            return
        if not insumos or not tipos_merma:
            print(Color.aviso("No hay insumos o tipos de merma registrados."))
            pausar()
            return

        # Tabla de referencia de insumos activos antes de elegir el insumo a mermar.
        filas_ins = [(i["codigo"], i["nombre"], i["stockActual"], i["abreviatura"]) for i in insumos]
        enc = "\n".join([
            imprimir_encabezado_sesion(
                self.usuario,
                breadcrumb=["Inicio", "Panel Barista", "Registrar Merma", "Selecciona insumo"]
            ),
            tabla_centrada("INSUMOS ACTIVOS", ["CODIGO", "INSUMO", "STOCK ACTUAL", "UNIDAD"], filas_ins),
        ])
        opts_i = [
            f"{i['codigo']:<12} {i['nombre']:<26} Categoria: {i['categoria']:<22} "
            f"Stock: {i['stockActual']} {i['abreviatura']}"
            for i in insumos
        ] + ["<< Cancelar y regresar"]
        idx_i = seleccionar_con_flechas("REGISTRAR MERMA - Selecciona insumo", opts_i, enc)
        if idx_i == len(insumos):
            return
        ins = insumos[idx_i]

        enc = imprimir_encabezado_sesion(
            self.usuario,
            breadcrumb=["Inicio", "Panel Barista", "Registrar Merma", "Tipo de merma"]
        )
        opts_t = [t["nombre"] for t in tipos_merma] + ["<< Cancelar y regresar"]
        idx_t = seleccionar_con_flechas("Tipo de merma", opts_t, enc)
        if idx_t == len(tipos_merma):
            return
        tipo = tipos_merma[idx_t]

        limpiar_pantalla()
        print(imprimir_encabezado_sesion(
            self.usuario,
            breadcrumb=["Inicio", "Panel Barista", "Registrar Merma"]
        ))
        pfx = _prefijo(_ancho())
        print(f"\n{pfx}  {Color.titulo('REGISTRAR MERMA')}")
        print(f"{pfx}  Insumo: {Color.CARAMELO}{ins['nombre']}{Color.RESET}  "
              f"Categoria: {ins['categoria']}")
        print(f"{pfx}  Stock actual disponible: {Color.CARAMELO}"
              f"{ins['stockActual']} {ins['abreviatura']}{Color.RESET}")
        print(f"{pfx}  Tipo:   {Color.CARAMELO}{tipo['nombre']}{Color.RESET}\n")

        try:
            while True:
                try:
                    cantidad = pedir_numero_positivo(
                        prompt="Cantidad a dar de baja",
                        unidad=ins["abreviatura"],
                        ejemplo=f"{min(1, float(ins['stockActual'])):.1f}",
                        stock_max=float(ins["stockActual"]),
                        nombre_campo="cantidad de merma"
                    )
                    break
                except ValueError as error:
                    print(Color.error(str(error)))
                    pausar()
            while True:
                try:
                    motivo = pedir_motivo(ejemplo="Derrame accidental en barra")
                    break
                except ValueError as error:
                    print(Color.error(str(error)))
                    pausar()
        except OperacionCancelada:
            print(Color.aviso("Operacion cancelada. No se registro la merma."))
            pausar()
            return

        while True:
            try:
                ok, msg = self.merma_srv.registrar_merma(
                    ins["codigo"], tipo["codigo"], cantidad, motivo,
                    self.usuario.num  # idEmpleado del barista autenticado
                )
            except Exception as error:
                print(Color.error(str(error)))
                pausar()
                return
            if ok:
                print(Color.ok(msg))
                pausar()
                return

            print(Color.error(msg))
            pausar()
            if "stock" not in msg.lower():
                return
            try:
                insumos = self.inventario_srv.listar_todos_insumos()
            except Exception as error:
                print(Color.error(str(error)))
                pausar()
                return
            insumo_actual = None
            for item in insumos:
                if item["codigo"] == ins["codigo"]:
                    insumo_actual = item
            if insumo_actual is None:
                print(Color.error("El insumo ya no existe. Selecciona otro para continuar."))
                pausar()
                return
            ins = insumo_actual
            try:
                while True:
                    try:
                        cantidad = pedir_numero_positivo(
                            prompt="Cantidad a dar de baja",
                            unidad=ins["abreviatura"],
                            ejemplo=f"{min(1, float(ins['stockActual'])):.1f}",
                            stock_max=float(ins["stockActual"]),
                            nombre_campo="cantidad de merma"
                        )
                        break
                    except ValueError as error:
                        print(Color.error(str(error)))
                        pausar()
            except OperacionCancelada:
                print(Color.aviso("Operacion cancelada. No se registro la merma."))
                pausar()
                return

    def surtir_mesa(self):
        limpiar_pantalla()
        try:
            insumos = self.inventario_srv.obtener_insumos_mesa()
        except Exception as error:
            print(Color.error(str(error)))
            pausar()
            return
        if not insumos:
            print(Color.aviso("No hay consumibles de mesa registrados."))
            pausar()
            return
        enc = imprimir_encabezado_sesion(
            self.usuario,
            breadcrumb=["Inicio", "Panel Barista", "Surtir Mesa"]
        )
        opts = [f"{i['codigo']:<12} {i['nombre']:<30} Stock: {i['stockActual']} {i['abreviatura']}"
                for i in insumos] + ["<< Cancelar y regresar"]
        idx = seleccionar_con_flechas("SURTIR MESA - Selecciona insumo", opts, enc)
        if idx == len(insumos):
            return
        ins = insumos[idx]

        limpiar_pantalla()
        print(imprimir_encabezado_sesion(
            self.usuario,
            breadcrumb=["Inicio", "Panel Barista", "Surtir Mesa", ins["nombre"]]
        ))
        pfx = _prefijo(_ancho())
        print(f"\n{pfx}  {Color.titulo('SURTIR MESA DE CONSUMIBLES')}")
        print(f"{pfx}  Insumo: {Color.CARAMELO}{ins['nombre']}{Color.RESET}  "
              f"Stock disponible: {ins['stockActual']} {ins['abreviatura']}\n")

        try:
            while True:
                try:
                    cantidad = pedir_numero_positivo(
                        prompt="Cantidad a surtir",
                        unidad=ins["abreviatura"],
                        ejemplo="1" if ins["unidad_codigo"] in UNIDADES_CONTEO_ENTERO else "50",
                        stock_max=float(ins["stockActual"]),
                        nombre_campo="cantidad a surtir",
                        solo_entero=ins["unidad_codigo"] in UNIDADES_CONTEO_ENTERO
                    )
                    break
                except ValueError as error:
                    print(Color.error(str(error)))
                    pausar()
        except OperacionCancelada:
            print(Color.aviso("Operacion cancelada. No se surtio la mesa."))
            pausar()
            return

        while True:
            try:
                ok, msg = self.despacho_srv.surtir_mesa_consumibles(ins["codigo"], cantidad)
            except Exception as error:
                print(Color.error(str(error)))
                pausar()
                return
            if ok:
                print(Color.ok(msg))
                pausar()
                return
            print(Color.error(msg))
            pausar()
            if "stock" not in msg.lower():
                return
            try:
                insumos = self.inventario_srv.obtener_insumos_mesa()
            except Exception as error:
                print(Color.error(str(error)))
                pausar()
                return
            insumo_actual = None
            for item in insumos:
                if item["codigo"] == ins["codigo"]:
                    insumo_actual = item
            if insumo_actual is None:
                print(Color.error("El insumo ya no existe. Selecciona otro para continuar."))
                pausar()
                return
            ins = insumo_actual
            try:
                while True:
                    try:
                        cantidad = pedir_numero_positivo(
                            prompt="Cantidad a surtir",
                            unidad=ins["abreviatura"],
                            ejemplo="1" if ins["unidad_codigo"] in UNIDADES_CONTEO_ENTERO else "50",
                            stock_max=float(ins["stockActual"]),
                            nombre_campo="cantidad a surtir",
                            solo_entero=ins["unidad_codigo"] in UNIDADES_CONTEO_ENTERO
                        )
                        break
                    except ValueError as error:
                        print(Color.error(str(error)))
                        pausar()
            except OperacionCancelada:
                print(Color.aviso("Operacion cancelada. No se surtio la mesa."))
                pausar()
                return

    def desactivar_mi_cuenta(self):
        while True:
            limpiar_pantalla()
            print(imprimir_encabezado_sesion(
                self.usuario,
                breadcrumb=["Inicio", "Panel Barista", "Mi Cuenta"]
            ))
            print(Color.aviso("\n  ATENCION: Esta accion desactivara tu cuenta y cerrara la sesion."))
            enc = imprimir_encabezado_sesion(
                self.usuario,
                breadcrumb=["Inicio", "Panel Barista", "Mi Cuenta", "Desactivar"]
            )
            opts = ["Confirmar - desactivar mi cuenta", "<< Cancelar - no desactivar mi cuenta"]
            idx = seleccionar_con_flechas("Desactivar cuenta propia", opts, enc)
            if idx != 0:
                return False
            try:
                ok = self.empleado_srv.desactivar_cuenta(self.usuario.num)
                if not ok:
                    raise ValueError("No se pudo desactivar la cuenta.")
                print(Color.ok("Cuenta desactivada. Sesion cerrada."))
                pausar()
                return True
            except Exception as error:
                print(Color.error(str(error)))
                pausar()
