import shutil

from interfaz.estilos import Color
from consola_ui import tabla_centrada
from consola_ui import (
    limpiar_pantalla, pausar, seleccionar_con_flechas,
    imprimir_encabezado_sesion, imprimir_tabla,
    pedir_codigo, pedir_nombre_propio,
    pedir_numero_positivo, pedir_precio,
    _imprimir_guia, _input_centrado, _ancho, _prefijo, OperacionCancelada,
    imprimir_bloque_centrado, _centrar_texto
)
from documentos.generador_documentos import lineas_comprobante_compra, ancho_comprobante


class AdminInventario:
    def __init__(self, usuario, inventario_srv, compra_srv, reportes):
        self.usuario = usuario
        self.inventario_srv = inventario_srv
        self.compra_srv = compra_srv
        self.reportes = reportes

    def alertas_stock(self):
        alertas = self.inventario_srv.obtener_alertas_stock_bajo()
        cols = ["Codigo", "Insumo", "Stock", "Min", "Unidad", "Proveedor", "Telefono", "Ciudad"]
        filas = [(a["codigo"], a["nombre"], a["stockActual"], a["stockMin"],
                  a["abreviatura"], a["proveedor"], a["telefono"], a["ciudad"])
                 for a in alertas]
        limpiar_pantalla()
        print(imprimir_encabezado_sesion(
            self.usuario,
            breadcrumb=["Inicio", "Panel Admin", "Alertas de Stock"]
        ))
        if not alertas:
            print(Color.ok("\n  Todos los insumos tienen stock suficiente."))
        else:
            print(Color.aviso(f"\n  {len(alertas)} insumo(s) con stock bajo:\n"))
            imprimir_tabla("ALERTAS DE STOCK BAJO", cols, filas)
        pausar()

    def consultar_stock(self):
        opciones = [
            "Consulta general de stock",
            "Consulta individual de stock",
            "<< Volver",
        ]
        while True:
            limpiar_pantalla()
            enc = imprimir_encabezado_sesion(
                self.usuario,
                breadcrumb=["Inicio", "Panel Admin", "Inventario", "Consultar stock"]
            )
            idx = seleccionar_con_flechas("CONSULTA DE STOCK", opciones, enc)
            if idx == 0:
                self._consultar_stock_general()
            elif idx == 1:
                self._consultar_stock_individual()
            else:
                return

    def _consultar_stock_general(self):
        try:
            insumos = self.inventario_srv.obtener_stock_general()
        except Exception as error:
            print(Color.error(str(error)))
            pausar()
            return

        limpiar_pantalla()
        print(imprimir_encabezado_sesion(
            self.usuario,
            breadcrumb=["Inicio", "Panel Admin", "Inventario", "Stock general"]
        ))
        if not insumos:
            print(Color.aviso("\n  No hay insumos registrados."))
        else:
            columnas = [
                "Codigo", "Nombre", "Categoria", "Unidad",
                "Stock Actual", "Stock Minimo", "Estado",
            ]
            filas = []
            for insumo in insumos:
                estado = Color.error("[BAJO]") if insumo["stockActual"] <= insumo["stockMin"] \
                    else Color.ok("Suficiente")
                filas.append((
                    insumo["codigo"],
                    insumo["nombre"],
                    insumo["categoria"],
                    insumo["unidad"],
                    insumo["stockActual"],
                    insumo["stockMin"],
                    estado,
                ))
            imprimir_tabla("STOCK GENERAL DEL INVENTARIO", columnas, filas)
        pausar()

    def _consultar_stock_individual(self):
        try:
            insumos = self.inventario_srv.obtener_stock_general()
        except Exception as error:
            print(Color.error(str(error)))
            pausar()
            return

        if not insumos:
            limpiar_pantalla()
            print(imprimir_encabezado_sesion(
                self.usuario,
                breadcrumb=["Inicio", "Panel Admin", "Inventario", "Stock individual"]
            ))
            print(Color.aviso("\n  No hay insumos registrados."))
            pausar()
            return

        opciones = [
            f"{insumo['codigo']:<10} {insumo['nombre']:<30} "
            f"Stock: {insumo['stockActual']} {insumo['unidad']}"
            for insumo in insumos
        ] + ["<< Volver"]
        # Tabla completa de existencias antes de pedir el insumo a consultar.
        cols = ["CODIGO", "INSUMO", "CATEGORIA", "STOCK ACTUAL", "STOCK MIN", "UNIDAD", "ESTADO"]
        filas = [
            (i["codigo"], i["nombre"], i["categoria"], i["stockActual"], i["stockMin"], i["unidad"],
             "[BAJO]" if i["stockActual"] <= i["stockMin"] else "Suficiente")
            for i in insumos
        ]
        enc = "\n".join([
            imprimir_encabezado_sesion(
                self.usuario,
                breadcrumb=["Inicio", "Panel Admin", "Inventario", "Stock individual"]
            ),
            tabla_centrada("EXISTENCIAS ACTUALES DEL INVENTARIO", cols, filas),
        ])
        idx = seleccionar_con_flechas("SELECCIONA UN INSUMO", opciones, enc)
        if idx == len(insumos):
            return

        insumo_seleccionado = insumos[idx]
        try:
            detalle = self.inventario_srv.obtener_detalle_stock(
                insumo_seleccionado["codigo"]
            )
        except Exception as error:
            print(Color.error(str(error)))
            pausar()
            return

        limpiar_pantalla()
        print(imprimir_encabezado_sesion(
            self.usuario,
            breadcrumb=[
                "Inicio", "Panel Admin", "Inventario",
                f"Detalle {insumo_seleccionado['codigo']}"
            ]
        ))
        if not detalle:
            print(Color.error("El insumo seleccionado ya no esta disponible."))
            pausar()
            return

        pfx = _prefijo(_ancho())
        print(f"\n{pfx}  {Color.titulo('FICHA DE STOCK DEL INSUMO')}")
        print(f"{pfx}  Codigo:          {detalle['codigo']}")
        print(f"{pfx}  Nombre:          {detalle['nombre']}")
        print(f"{pfx}  Categoria:       {detalle['categoria']} ({detalle['categoria_codigo']})")
        print(f"{pfx}  Unidad:          {detalle['unidad_medida']} ({detalle['unidad']})")
        print(f"{pfx}  Stock actual:    {detalle['stockActual']} {detalle['unidad']}")
        print(f"{pfx}  Stock minimo:    {detalle['stockMin']} {detalle['unidad']}")
        print(f"{pfx}  Seccion almacen: {detalle['seccion']}")
        print(f"{pfx}  Estante:         {detalle['estante']}")
        if detalle["stockActual"] <= detalle["stockMin"]:
            print(f"{pfx}  Estado:          {Color.error('[BAJO]')}")
        else:
            print(f"{pfx}  Estado:          {Color.ok('Suficiente')}")
        pausar()

    def registrar_compra(self):
        limpiar_pantalla()
        try:
            proveedores = self.compra_srv.listar_proveedores()
            insumos = self.inventario_srv.listar_todos_insumos()
        except Exception as error:
            print(Color.error(str(error)))
            pausar()
            return
        if not proveedores or not insumos:
            print(Color.aviso("No hay proveedores o insumos registrados."))
            pausar()
            return

        while True:
            try:
                enc = imprimir_encabezado_sesion(
                    self.usuario,
                    breadcrumb=["Inicio", "Panel Admin", "Registrar Compra", "Proveedor"]
                )
                opts = [f"{p['codigo']:<10} {p['nombre']:<30} {p['ciudad']}"
                        for p in proveedores] + ["<< Cancelar y regresar"]
                idx = seleccionar_con_flechas("REGISTRAR COMPRA - Selecciona proveedor", opts, enc)
                if idx == len(proveedores):
                    return
                prov = proveedores[idx]
                break
            except Exception as error:
                print(Color.error(str(error)))
                pausar()

        while True:
            try:
                filas_ins = [(i["codigo"], i["nombre"], i["stockActual"], i["abreviatura"])
                             for i in insumos]
                enc = "\n".join([
                    imprimir_encabezado_sesion(
                        self.usuario,
                        breadcrumb=["Inicio", "Panel Admin", "Registrar Compra", "Insumo"]
                    ),
                    tabla_centrada("INSUMOS DEL CATALOGO", ["CODIGO", "INSUMO", "STOCK ACTUAL", "UNIDAD"],
                                   filas_ins),
                ])
                opts2 = [f"{i['codigo']:<12} {i['nombre']:<30} Stock: {i['stockActual']} {i['abreviatura']}"
                         for i in insumos] + ["<< Cancelar y regresar"]
                idx2 = seleccionar_con_flechas("Selecciona insumo a comprar", opts2, enc)
                if idx2 == len(insumos):
                    return
                ins = insumos[idx2]
                break
            except Exception as error:
                print(Color.error(str(error)))
                pausar()

        limpiar_pantalla()
        print(imprimir_encabezado_sesion(
            self.usuario,
            breadcrumb=["Inicio", "Panel Admin", "Registrar Compra", "Datos"]
        ))
        pfx = _prefijo(_ancho())
        print(f"\n{pfx}  {Color.titulo('REGISTRAR COMPRA A PROVEEDOR')}")
        print(f"{pfx}  Proveedor: {Color.CARAMELO}{prov['nombre']}{Color.RESET}  "
              f"Ciudad: {prov['ciudad']}")
        print(f"{pfx}  Insumo:    {Color.CARAMELO}{ins['nombre']}{Color.RESET}\n")
        print(Color.info("El IVA se calculara automaticamente: 8% si el proveedor es de frontera, "
                         "16% si es del interior del pais."))
        print()

        try:
            while True:
                try:
                    cantidad = pedir_numero_positivo(
                        prompt="Cantidad comprada",
                        unidad=ins["abreviatura"],
                        ejemplo="1000",
                        nombre_campo="cantidad"
                    )
                    break
                except ValueError as error:
                    print(Color.error(str(error)))
                    pausar()

            while True:
                try:
                    precio_unit = pedir_precio(ejemplo="0.85")
                    break
                except ValueError as error:
                    print(Color.error(str(error)))
                    pausar()

            tasa, sub, iva_v, total = self.compra_srv.calcular_totales_previos(
                prov.get("ciudad", ""), cantidad, precio_unit
            )
            print(f"\n{pfx}  Subtotal: ${sub:.2f}  IVA ({int(tasa*100)}%): ${iva_v:.2f}  "
                  f"Total: {Color.CARAMELO}${total:.2f}{Color.RESET}")

            metodos = [("EFEC", "Efectivo"), ("TARJ", "Tarjeta"),
                       ("TRAN", "Transferencia Electronica")]
            enc3 = imprimir_encabezado_sesion(
                self.usuario,
                breadcrumb=["Inicio", "Panel Admin", "Registrar Compra", "Metodo de pago"]
            )
            idx_m = seleccionar_con_flechas(
                "Metodo de pago al proveedor",
                [m[1] for m in metodos] + ["<< Cancelar compra"],
                enc3
            )
            if idx_m == len(metodos):
                return
            cod_pago = metodos[idx_m][0]
        except OperacionCancelada:
            print(Color.aviso("Operacion cancelada. No se registro la compra."))
            pausar()
            return

        while True:
            try:
                ok, msg, datos = self.compra_srv.registrar_compra_proveedor(
                    prov["codigo"], ins["codigo"], cantidad, precio_unit,
                    cod_pago, self.usuario.num,
                    autorizo=self.usuario.nombre_completo,
                    unidad=ins["abreviatura"]
                )
            except Exception as error:
                print(Color.error(str(error)))
                pausar()
                return
            if ok:
                metodo_desc = next(desc for cod, desc in metodos if cod == cod_pago)
                self._mostrar_comprobante_compra(datos, metodo_desc)
                pausar()
                return
            print(Color.error(msg))
            pausar()
            texto = msg.lower()
            if "proveedor no encontrado" in texto:
                try:
                    proveedores = self.compra_srv.listar_proveedores()
                except Exception as error:
                    print(Color.error(str(error)))
                    pausar()
                    return
                while True:
                    opts = [f"{p['codigo']:<10} {p['nombre']:<30} {p['ciudad']}"
                            for p in proveedores] + ["<< Cancelar y regresar"]
                    idx = seleccionar_con_flechas(
                        "Selecciona proveedor", opts,
                        imprimir_encabezado_sesion(
                            self.usuario,
                            breadcrumb=["Inicio", "Panel Admin", "Registrar Compra", "Proveedor"]
                        )
                    )
                    if idx == len(proveedores):
                        return
                    prov = proveedores[idx]
                    break
                continue
            if "insumo no encontrado" in texto:
                try:
                    insumos = self.inventario_srv.listar_todos_insumos()
                except Exception as error:
                    print(Color.error(str(error)))
                    pausar()
                    return
                while True:
                    opts2 = [
                        f"{i['codigo']:<12} {i['nombre']:<30} Stock: {i['stockActual']} {i['abreviatura']}"
                        for i in insumos
                    ] + ["<< Cancelar y regresar"]
                    idx2 = seleccionar_con_flechas(
                        "Selecciona insumo a comprar", opts2,
                        imprimir_encabezado_sesion(
                            self.usuario,
                            breadcrumb=["Inicio", "Panel Admin", "Registrar Compra", "Insumo"]
                        )
                    )
                    if idx2 == len(insumos):
                        return
                    ins = insumos[idx2]
                    break
                continue
            return

    def _mostrar_comprobante_compra(self, datos, metodo_desc):
        """
        Guarda el respaldo .txt y dibuja el COMPROBANTE DE COMPRA centrado en consola.
        Si el .txt no se puede guardar, el comprobante se muestra igual con un aviso.
        """
        datos["metodo"] = metodo_desc
        aviso = None
        try:
            self.reportes.guardar_comprobante_compra_txt(datos)
        except Exception as error:
            datos["respaldo"] = None
            aviso = f"No se pudo guardar el respaldo .txt: {error}"

        limpiar_pantalla()
        print(imprimir_encabezado_sesion(
            self.usuario,
            breadcrumb=["Inicio", "Panel Admin", "Registrar Compra", "Comprobante"]
        ))
        print()
        columnas = shutil.get_terminal_size(fallback=(80, 24)).columns
        imprimir_bloque_centrado(lineas_comprobante_compra(datos, ancho_comprobante(columnas)))
        if aviso:
            print(_centrar_texto(Color.aviso(aviso)))
        print()

    def registrar_insumo(self):
        limpiar_pantalla()
        print(imprimir_encabezado_sesion(
            self.usuario,
            breadcrumb=["Inicio", "Panel Admin", "Registrar Insumo"]
        ))
        pfx = _prefijo(_ancho())
        print(f"\n{pfx}  {Color.titulo('REGISTRAR NUEVO INSUMO EN ALMACEN')}\n")
        print(Color.info("Completa los siguientes datos para dar de alta el insumo en el inventario."))
        print()

        try:
            insumos_existentes = self.inventario_srv.listar_todos_insumos()
            unidades = self.inventario_srv.listar_unidades_medida()
            categorias = self.inventario_srv.listar_categorias_insumo()
        except Exception as error:
            print(Color.error(str(error)))
            pausar()
            return
        if not unidades or not categorias:
            print(Color.error("No hay unidades de medida o categorias de insumo disponibles."))
            pausar()
            return

        try:
            while True:
                try:
                    codigo = pedir_codigo(
                        prompt="Codigo del insumo", longitud_max=6, ejemplo="INS008"
                    )
                    codigo_repetido = False
                    for insumo in insumos_existentes:
                        if codigo.upper() == insumo["codigo"].upper():
                            codigo_repetido = True
                    if codigo_repetido:
                        raise ValueError(f"El codigo '{codigo}' ya esta registrado.")
                    break
                except ValueError as error:
                    print(Color.error(str(error)))
                    pausar()

            while True:
                try:
                    nombre = pedir_nombre_propio(prompt="Nombre del insumo", ejemplo="Leche Entera")
                    break
                except ValueError as error:
                    print(Color.error(str(error)))
                    pausar()

            while True:
                try:
                    stock_ini = pedir_numero_positivo(
                        prompt="Stock inicial", unidad="", ejemplo="500",
                        nombre_campo="stock inicial"
                    )
                    break
                except ValueError as error:
                    print(Color.error(str(error)))
                    pausar()

            while True:
                try:
                    stock_min = pedir_numero_positivo(
                        prompt="Stock minimo de alerta", unidad="", ejemplo="100",
                        nombre_campo="stock minimo"
                    )
                    break
                except ValueError as error:
                    print(Color.error(str(error)))
                    pausar()

            while True:
                try:
                    _imprimir_guia(
                        "Seccion del almacen donde se guarda el insumo",
                        "Texto libre, maximo 30 caracteres",
                        "Refrigeracion o Bodega seca",
                        "Permite ubicar fisicamente el insumo en almacen."
                    )
                    raw_sec = _input_centrado("Seccion de almacen")
                    if raw_sec.strip().upper() in ("0", "CANCELAR"):
                        raise OperacionCancelada()
                    seccion = raw_sec.strip().title()
                    if not seccion:
                        raise ValueError("La seccion del almacen no puede estar vacia.")
                    if len(seccion) > 30:
                        raise ValueError("La seccion no puede superar 30 caracteres.")
                    break
                except ValueError as error:
                    print(Color.error(str(error)))
                    pausar()

            while True:
                try:
                    opciones_unidad = " o ".join(
                        item["codigo"].upper() for item in unidades
                    )
                    ejemplos_unidad = ", ".join(
                        f'{item["codigo"].upper()} ({item["abreviatura"]})'
                        for item in unidades
                    )
                    _imprimir_guia(
                        "Codigo de unidad de medida",
                        "Codigo corto en mayusculas registrado en la BD",
                        ejemplos_unidad,
                        f"Opciones validas: {opciones_unidad}. Debe coincidir exactamente."
                    )
                    raw_uni = _input_centrado(
                        f"Codigo de unidad (ej. {opciones_unidad})"
                    )
                    if raw_uni.strip().upper() in ("0", "CANCELAR"):
                        raise OperacionCancelada()
                    unidad = raw_uni.strip().upper()
                    if not unidad:
                        raise ValueError("El codigo de unidad no puede estar vacio.")
                    unidad_valida = False
                    for item in unidades:
                        if unidad == item["codigo"].upper():
                            unidad_valida = True
                    if not unidad_valida:
                        raise ValueError(f"La unidad '{unidad}' no existe.")
                    break
                except ValueError as error:
                    print(Color.error(str(error)))
                    pausar()

            while True:
                try:
                    _imprimir_guia(
                        "Estante o ubicacion exacta dentro de la seccion",
                        "Texto libre, maximo 20 caracteres",
                        "Estante-A3 o Frio-2",
                        "Referencia visual para el personal de almacen."
                    )
                    raw_est = _input_centrado("Estante / ubicacion")
                    if raw_est.strip().upper() in ("0", "CANCELAR"):
                        raise OperacionCancelada()
                    estante = raw_est.strip()
                    if not estante:
                        raise ValueError("El estante o ubicacion no puede estar vacio.")
                    if len(estante) > 20:
                        raise ValueError("El estante o ubicacion no puede superar 20 caracteres.")
                    break
                except ValueError as error:
                    print(Color.error(str(error)))
                    pausar()

            while True:
                try:
                    ejemplos_categoria = ", ".join(
                        f'{item["codigo"].upper()} ({item["nombre"]})'
                        for item in categorias
                    )
                    opciones_categoria = " o ".join(
                        item["codigo"].upper() for item in categorias
                    )
                    _imprimir_guia(
                        "Categoria del insumo en el almacen",
                        "Codigo de categoria registrado en la BD",
                        ejemplos_categoria,
                        f"Opciones validas: {opciones_categoria}. Debe coincidir exactamente."
                    )
                    raw_cat = _input_centrado(
                        f"Categoria de insumo (ej. {opciones_categoria})"
                    )
                    if raw_cat.strip().upper() in ("0", "CANCELAR"):
                        raise OperacionCancelada()
                    cat_ins = raw_cat.strip().upper()
                    if not cat_ins:
                        raise ValueError("El codigo de categoria no puede estar vacio.")
                    categoria_valida = False
                    for item in categorias:
                        if cat_ins == item["codigo"].upper():
                            categoria_valida = True
                    if not categoria_valida:
                        raise ValueError(f"La categoria '{cat_ins}' no existe.")
                    break
                except ValueError as error:
                    print(Color.error(str(error)))
                    pausar()
        except OperacionCancelada:
            print(Color.aviso("Operacion cancelada. No se registro el insumo."))
            pausar()
            return

        while True:
            try:
                ok, msg = self.inventario_srv.registrar_insumo(
                    codigo, nombre, stock_ini, stock_min, seccion, unidad, estante, cat_ins
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
            texto = msg.lower()
            if "duplicate" not in texto and "duplicad" not in texto:
                return
            try:
                insumos_existentes = self.inventario_srv.listar_todos_insumos()
            except Exception as error:
                print(Color.error(str(error)))
                pausar()
                return
            try:
                while True:
                    try:
                        codigo = pedir_codigo(
                            prompt="Codigo del insumo", longitud_max=6, ejemplo="INS008"
                        )
                        repetido = False
                        for insumo in insumos_existentes:
                            if codigo.upper() == insumo["codigo"].upper():
                                repetido = True
                        if repetido:
                            raise ValueError(f"El codigo '{codigo}' ya esta registrado.")
                        break
                    except ValueError as error:
                        print(Color.error(str(error)))
                        pausar()
            except OperacionCancelada:
                print(Color.aviso("Operacion cancelada. No se registro el insumo."))
                pausar()
                return
