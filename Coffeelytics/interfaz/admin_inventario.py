import shutil

from interfaz.estilos import Color
from consola_ui import tabla_centrada
from consola_ui import (
    limpiar_pantalla, pausar, seleccionar_con_flechas,
    imprimir_encabezado_sesion, imprimir_tabla,
    pedir_codigo, pedir_nombre_propio,
    pedir_numero_positivo, pedir_precio,
    _imprimir_guia, _input_centrado, _verificar_cancelacion,
    _ancho, _prefijo, OperacionCancelada, PasoAnterior,
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

        paso = 1
        try:
            while paso <= 5:
                try:
                    if paso == 1:
                        enc = imprimir_encabezado_sesion(
                            self.usuario,
                            breadcrumb=["Inicio", "Panel Admin", "Registrar Compra", "Proveedor"]
                        )
                        opts = [f"{p['codigo']:<10} {p['nombre']:<30} {p['ciudad']}"
                                for p in proveedores] + ["<< Volver al menu anterior"]
                        idx = seleccionar_con_flechas(
                            "REGISTRAR COMPRA - Selecciona proveedor", opts, enc
                        )
                        if idx == len(proveedores):
                            return
                        prov = proveedores[idx]
                    elif paso == 2:
                        filas_ins = [
                            (i["codigo"], i["nombre"], i["stockActual"], i["abreviatura"])
                            for i in insumos
                        ]
                        enc = "\n".join([
                            imprimir_encabezado_sesion(
                                self.usuario,
                                breadcrumb=["Inicio", "Panel Admin", "Registrar Compra", "Insumo"]
                            ),
                            tabla_centrada("INSUMOS DEL CATALOGO",
                                           ["CODIGO", "INSUMO", "STOCK ACTUAL", "UNIDAD"],
                                           filas_ins),
                        ])
                        opts = [
                            f"{i['codigo']:<12} {i['nombre']:<30} "
                            f"Stock: {i['stockActual']} {i['abreviatura']}"
                            for i in insumos
                        ] + ["<< Paso anterior", "<< Cancelar compra"]
                        idx = seleccionar_con_flechas("Selecciona insumo a comprar", opts, enc)
                        if idx == len(insumos) + 1:
                            return
                        ins = insumos[idx]
                    elif paso == 3:
                        limpiar_pantalla()
                        print(imprimir_encabezado_sesion(
                            self.usuario,
                            breadcrumb=["Inicio", "Panel Admin", "Registrar Compra", "Cantidad"]
                        ))
                        cantidad = pedir_numero_positivo(
                            prompt="Cantidad comprada", unidad=ins["abreviatura"],
                            ejemplo="1000", nombre_campo="cantidad",
                            unidad_codigo=ins["unidad_codigo"]
                        )
                    elif paso == 4:
                        precio_unit = pedir_precio(ejemplo="0.85")
                    elif paso == 5:
                        tasa, sub, iva_v, total = self.compra_srv.calcular_totales_previos(
                            prov.get("ciudad", ""), cantidad, precio_unit
                        )
                        pfx = _prefijo(_ancho())
                        print(f"\n{pfx}  Subtotal: ${sub:.2f}  IVA ({int(tasa*100)}%): ${iva_v:.2f}  "
                              f"Total: {Color.CARAMELO}${total:.2f}{Color.RESET}")
                        metodos = [("EFEC", "Efectivo"), ("TARJ", "Tarjeta"),
                                   ("TRAN", "Transferencia Electronica")]
                        enc = imprimir_encabezado_sesion(
                            self.usuario,
                            breadcrumb=["Inicio", "Panel Admin", "Registrar Compra",
                                        "Metodo de pago"]
                        )
                        opts = [m[1] for m in metodos] + [
                            "<< Paso anterior", "<< Cancelar compra"
                        ]
                        idx = seleccionar_con_flechas("Metodo de pago al proveedor", opts, enc)
                        if idx == len(metodos) + 1:
                            return
                        cod_pago = metodos[idx][0]
                    paso += 1
                except PasoAnterior:
                    if paso == 1:
                        return
                    paso -= 1
                except ValueError as error:
                    print(Color.error(str(error)))
                    pausar()
        except (OperacionCancelada, PasoAnterior):
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
            estantes = self.inventario_srv.listar_estantes()
        except Exception as error:
            print(Color.error(str(error)))
            pausar()
            return
        if not unidades or not categorias:
            print(Color.error("No hay unidades de medida o categorias de insumo disponibles."))
            pausar()
            return
        if not estantes:
            print(Color.error("No hay estantes registrados. Registra un estante antes de crear insumos."))
            pausar()
            return

        paso = 1
        try:
            while paso <= 8:
                try:
                    if paso == 1:
                        codigo = pedir_codigo(
                            prompt="Codigo del insumo", longitud_max=6, ejemplo="INS008"
                        )
                        for insumo in insumos_existentes:
                            if codigo.upper() == insumo["codigo"].upper():
                                raise ValueError(f"El codigo '{codigo}' ya esta registrado.")
                    elif paso == 2:
                        nombre = pedir_nombre_propio(
                            prompt="Nombre del insumo", ejemplo="Leche Entera"
                        )
                    elif paso == 3:
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
                        unidad = _input_centrado(
                            f"Codigo de unidad (ej. {opciones_unidad})"
                        )
                        _verificar_cancelacion(unidad)
                        unidad = unidad.upper()
                        if not unidad:
                            raise ValueError("El codigo de unidad no puede estar vacio.")
                        unidad_abreviatura = ""
                        for item in unidades:
                            if unidad == item["codigo"].upper():
                                unidad_abreviatura = item["abreviatura"]
                        if not unidad_abreviatura:
                            raise ValueError(f"La unidad '{unidad}' no existe.")
                    elif paso == 4:
                        stock_ini = pedir_numero_positivo(
                            prompt="Stock inicial", unidad=unidad_abreviatura,
                            ejemplo="500", nombre_campo="stock inicial",
                            unidad_codigo=unidad
                        )
                    elif paso == 5:
                        stock_min = pedir_numero_positivo(
                            prompt="Stock minimo de alerta", unidad=unidad_abreviatura,
                            ejemplo="100", nombre_campo="stock minimo",
                            unidad_codigo=unidad
                        )
                    elif paso == 6:
                        filas_estantes = [
                            (e["codigo"], f'Estante {e["codigo"]}', e["capacidad"],
                             f'1-{e["secciones"]}' if e["secciones"] else "Ninguna")
                            for e in estantes
                        ]
                        imprimir_tabla(
                            "ESTANTES DISPONIBLES",
                            ["CODIGO", "DESCRIPCION", "CAPACIDAD", "SECCIONES DISPONIBLES"],
                            filas_estantes
                        )
                        codigos_estantes = ", ".join(str(e["codigo"]) for e in estantes)
                        _imprimir_guia(
                            "Codigo del estante donde se almacenara el insumo",
                            "Codigo numerico registrado en la base de datos",
                            codigos_estantes,
                            "Elige un estante de la tabla superior."
                        )
                        codigo_estante = _input_centrado(
                            f"Codigo de estante (ej. {codigos_estantes})"
                        ).strip().upper()
                        _verificar_cancelacion(codigo_estante)
                        estante_valido = False
                        for item in estantes:
                            if codigo_estante == str(item["codigo"]).strip().upper():
                                estante_valido = True
                        if not estante_valido:
                            raise ValueError(
                                f"El estante '{codigo_estante}' no existe. "
                                "Revisa la tabla superior e ingresa un codigo valido."
                            )
                        estante = int(codigo_estante)
                    elif paso == 7:
                        secciones = self.inventario_srv.listar_secciones_almacen(estante)
                        if not secciones:
                            print(Color.error(
                                f"El estante '{estante}' no tiene secciones disponibles."
                            ))
                            pausar()
                            paso = 6
                            continue
                        filas_secciones = [(s["codigo"], s["nombre"]) for s in secciones]
                        imprimir_tabla(
                            f"SECCIONES DISPONIBLES DEL ESTANTE {estante}",
                            ["CODIGO", "DESCRIPCION"],
                            filas_secciones
                        )
                        codigos_secciones = ", ".join(str(s["codigo"]) for s in secciones)
                        _imprimir_guia(
                            "Codigo de la seccion dentro del estante",
                            "Numero de seccion disponible para el estante elegido",
                            codigos_secciones,
                            "Elige una seccion de la tabla superior."
                        )
                        codigo_seccion = _input_centrado(
                            f"Codigo de seccion (ej. {codigos_secciones})"
                        ).strip().upper()
                        _verificar_cancelacion(codigo_seccion)
                        seccion_valida = False
                        for item in secciones:
                            if codigo_seccion == str(item["codigo"]).strip().upper():
                                seccion_valida = True
                        if not seccion_valida:
                            raise ValueError(
                                f"La seccion '{codigo_seccion}' no existe en el estante "
                                f"{estante}. Revisa la tabla superior e ingresa un codigo valido."
                            )
                        seccion = int(codigo_seccion)
                    elif paso == 8:
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
                        cat_ins = _input_centrado(
                            f"Categoria de insumo (ej. {opciones_categoria})"
                        )
                        _verificar_cancelacion(cat_ins)
                        cat_ins = cat_ins.upper()
                        if not cat_ins:
                            raise ValueError("El codigo de categoria no puede estar vacio.")
                        categoria_valida = False
                        for item in categorias:
                            if cat_ins == item["codigo"].upper():
                                categoria_valida = True
                        if not categoria_valida:
                            raise ValueError(f"La categoria '{cat_ins}' no existe.")
                    paso += 1
                except PasoAnterior:
                    if paso == 1:
                        return
                    paso -= 1
                except ValueError as error:
                    print(Color.error(str(error)))
                    pausar()
        except (OperacionCancelada, PasoAnterior):
            print(Color.aviso("Operacion cancelada. No se registro el insumo."))
            pausar()
            return
        except Exception as error:
            print(Color.error(str(error)))
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
            except (OperacionCancelada, PasoAnterior):
                print(Color.aviso("Operacion cancelada. No se registro el insumo."))
                pausar()
                return
