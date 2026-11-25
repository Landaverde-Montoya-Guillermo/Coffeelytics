
from interfaz.estilos import Color
from consola_ui import tabla_centrada
from consola_ui import (
    limpiar_pantalla, pausar, seleccionar_con_flechas,
    imprimir_encabezado_sesion, imprimir_tabla,
    pedir_codigo, pedir_nombre_propio, pedir_precio,
    pedir_numero_positivo,
    _ancho, _prefijo, OperacionCancelada, PasoAnterior
)


class AdminProductos:
    def __init__(self, usuario, producto_srv, inventario_srv):
        self.usuario = usuario
        self.producto_srv = producto_srv
        self.inventario_srv = inventario_srv

    def configurar_receta(self, prod_codigo, prod_nombre):
        pendientes = []
        limpiar_pantalla()
        encabezado = imprimir_encabezado_sesion(
            self.usuario,
            breadcrumb=["Inicio", "Panel Admin", "Anadir Producto", f"Receta: {prod_nombre}"]
        )
        print(encabezado)
        while True:
            try:
                receta_actual = self.producto_srv.obtener_receta(prod_codigo)
                filas_receta = []
                for r in receta_actual:
                    fila = [r["insumo_codigo"], r["nombre"],
                            f"{r['cantidad']} {r['unidad_medida']}"]
                    filas_receta.append(fila)
                for insumo in pendientes:
                    filas_receta.append([
                        insumo["codigo"],
                        insumo["nombre"],
                        f"{insumo['cantidad']} {insumo['unidad']}"
                    ])
                imprimir_tabla(f"Insumos de '{prod_nombre}' ({prod_codigo})",
                               ["Codigo", "Insumo", "Cantidad por unidad"], filas_receta)

                insumos = self.inventario_srv.obtener_insumos_receta()
                if not insumos:
                    print(Color.aviso("No hay insumos registrados en el inventario."))
                    pausar()
                    return

                opciones = []
                for ins in insumos:
                    linea = f"{ins['codigo']:<12} {ins['nombre']:<30} Stock: {ins['stockActual']} {ins['abreviatura']}"
                    opciones.append(linea)
                opciones.append("[OK] Finalizar receta")
                opciones.append("<< Cancelar y regresar")

                idx = seleccionar_con_flechas(
                    f"Selecciona un insumo para agregar a '{prod_nombre}'",
                    opciones,
                    encabezado_extra=encabezado
                )
                if idx == len(opciones) - 1:
                    print(Color.aviso("Operacion cancelada. No se guardaron los cambios pendientes."))
                    pausar()
                    return

                if idx == len(opciones) - 2:
                    if not receta_actual and not pendientes:
                        print(Color.error(
                            "Debes agregar al menos un insumo a la receta antes de finalizar."
                        ))
                        pausar()
                        continue
                    if pendientes:
                        try:
                            ok, msg = self.producto_srv.registrar_insumos_en_receta(
                                prod_codigo, pendientes
                            )
                        except Exception as error:
                            print(Color.error(str(error)))
                            pausar()
                            continue
                        if not ok:
                            print(Color.error(msg))
                            pausar()
                            continue
                        print(Color.ok(msg))
                    else:
                        print(Color.ok(
                            f"Receta de '{prod_nombre}' finalizada con {len(receta_actual)} insumo(s)."
                        ))
                    pausar()
                    return

                ins_sel = insumos[idx]
                while True:
                    try:
                        cant = pedir_numero_positivo(
                            prompt=f"Cantidad de {ins_sel['nombre']} por cada '{prod_nombre}'",
                            unidad=ins_sel["abreviatura"],
                            ejemplo="250",
                            nombre_campo="cantidad requerida",
                            unidad_codigo=ins_sel["unidad_codigo"]
                        )
                        break
                    except ValueError as error:
                        print(Color.error(str(error)))
                        pausar()
                pendientes.append({
                    "codigo": ins_sel["codigo"],
                    "nombre": ins_sel["nombre"],
                    "cantidad": cant,
                    "unidad": ins_sel["abreviatura"],
                })
                print(Color.info(
                    "Insumo agregado a la lista. La receta se guardara al finalizar."
                ))
                pausar()
            except OperacionCancelada:
                print(Color.aviso("Operacion cancelada. No se guardaron los cambios pendientes."))
                pausar()
                return
            except Exception as error:
                print(Color.error(str(error)))
                pausar()

    def _tablas_receta(self, prod, insumos):
        """Tablas centradas: receta actual del producto y catalogo de insumos disponibles."""
        receta = self.producto_srv.obtener_receta(prod["codigo"])
        filas_receta = [(r["nombre"], r["requerido"], r["abreviatura"]) for r in receta]
        filas_cat = [(i["codigo"], i["nombre"], i["stockActual"], i["abreviatura"]) for i in insumos]
        return "\n".join([
            tabla_centrada("RECETA ACTUAL DEL PRODUCTO", ["INSUMO", "CANTIDAD", "UNIDAD"], filas_receta),
            tabla_centrada("CATALOGO DE INSUMOS DISPONIBLES",
                           ["CODIGO", "INSUMO", "STOCK ACTUAL", "UNIDAD"], filas_cat),
        ])

    def asignar_insumo_receta(self):
        while True:
            try:
                limpiar_pantalla()
                productos = self.producto_srv.listar_todos_productos()
                insumos = self.inventario_srv.obtener_insumos_receta()
                if not productos or not insumos:
                    print(Color.aviso("No hay productos o insumos suficientes."))
                    pausar()
                    return

                paso = 1
                while paso <= 3:
                    try:
                        if paso == 1:
                            enc = imprimir_encabezado_sesion(
                                self.usuario,
                                breadcrumb=["Inicio", "Panel Admin", "Asignar Insumo a Receta",
                                            "Producto"]
                            )
                            opts = [
                                f"{p['codigo']:<10} {p['nombre']:<30} ${p['precio']:.2f} "
                                f"{p['categoria']}" for p in productos
                            ] + ["<< Volver al menu anterior"]
                            idx = seleccionar_con_flechas(
                                "ASIGNAR INSUMO A RECETA - Producto", opts, enc
                            )
                            if idx == len(productos):
                                return
                            prod = productos[idx]
                        elif paso == 2:
                            enc = "\n".join([
                                imprimir_encabezado_sesion(
                                    self.usuario,
                                    breadcrumb=["Inicio", "Panel Admin", "Asignar Insumo a Receta",
                                                "Insumo"]
                                ),
                                self._tablas_receta(prod, insumos),
                            ])
                            opts = [
                                f"{i['codigo']:<12} {i['nombre']:<30} "
                                f"Stock: {i['stockActual']} {i['abreviatura']}"
                                for i in insumos
                            ] + ["<< Paso anterior", "<< Cancelar y regresar"]
                            idx = seleccionar_con_flechas(
                                "Selecciona insumo a asignar a la receta", opts, enc
                            )
                            if idx == len(insumos) + 1:
                                return
                            ins = insumos[idx]
                        elif paso == 3:
                            limpiar_pantalla()
                            print(imprimir_encabezado_sesion(
                                self.usuario,
                                breadcrumb=["Inicio", "Panel Admin", "Asignar Insumo a Receta",
                                            "Cantidad"]
                            ))
                            pfx = _prefijo(_ancho())
                            print(f"\n{pfx}  {Color.titulo('ASIGNAR INSUMO A RECETA')}")
                            print(f"{pfx}  Producto: {Color.CARAMELO}{prod['nombre']}{Color.RESET}")
                            print(f"{pfx}  Insumo:   {Color.CARAMELO}{ins['nombre']}{Color.RESET}  "
                                  f"({ins['abreviatura']})\n")
                            print(Color.info(
                                "La cantidad indica cuanto de este insumo se consume por "
                                "UNIDAD vendida del producto."
                            ))
                            print()
                            cantidad = pedir_numero_positivo(
                                prompt="Cantidad requerida por unidad de producto",
                                unidad=ins["abreviatura"],
                                ejemplo="250",
                                nombre_campo="cantidad en receta",
                                unidad_codigo=ins["unidad_codigo"]
                            )
                        paso += 1
                    except PasoAnterior:
                        if paso == 1:
                            return
                        paso -= 1
                    except ValueError as error:
                        print(Color.error(str(error)))
                        pausar()

                while True:
                    try:
                        ok, msg = self.producto_srv.registrar_insumo_en_receta(
                            prod["codigo"], ins["codigo"], cantidad
                        )
                    except Exception as error:
                        print(Color.error(str(error)))
                        pausar()
                        return
                    if ok:
                        print(Color.ok(msg))
                        print(self._tablas_receta(prod, insumos))  # receta ya refrescada
                        pausar()
                        break

                    print(Color.error(msg))
                    pausar()
                    texto = msg.lower()
                    if "cantidad" in texto:
                        continue
                    if "insumo" in texto and ("no encontrado" in texto or "foreign key" in texto):
                        try:
                            insumos = self.inventario_srv.obtener_insumos_receta()
                        except Exception as error:
                            print(Color.error(str(error)))
                            pausar()
                            return
                        opts2 = [f"{i['codigo']:<12} {i['nombre']:<30} Stock: {i['stockActual']} {i['abreviatura']}"
                                 for i in insumos] + ["<< Cancelar y regresar"]
                        idx2 = seleccionar_con_flechas(
                            "Selecciona insumo a asignar a la receta",
                            opts2,
                            imprimir_encabezado_sesion(
                                self.usuario,
                                breadcrumb=["Inicio", "Panel Admin", "Asignar Insumo a Receta", "Insumo"]
                            )
                        )
                        if idx2 == len(insumos):
                            return
                        ins = insumos[idx2]
                        continue
                    if "producto" in texto and ("no encontrado" in texto or "foreign key" in texto):
                        try:
                            productos = self.producto_srv.listar_todos_productos()
                        except Exception as error:
                            print(Color.error(str(error)))
                            pausar()
                            return
                        opts = [f"{p['codigo']:<10} {p['nombre']:<30} ${p['precio']:.2f}  {p['categoria']}"
                                for p in productos] + ["<< Cancelar y regresar"]
                        idx = seleccionar_con_flechas(
                            "Selecciona producto",
                            opts,
                            imprimir_encabezado_sesion(
                                self.usuario,
                                breadcrumb=["Inicio", "Panel Admin", "Asignar Insumo a Receta", "Producto"]
                            )
                        )
                        if idx == len(productos):
                            return
                        prod = productos[idx]
                        continue
                    return
            except OperacionCancelada:
                print(Color.aviso("Operacion cancelada. No se asigno el insumo."))
                pausar()
                return
            except Exception as error:
                print(Color.error(str(error)))
                pausar()
                continue

    def alta_producto(self):
        limpiar_pantalla()
        try:
            categorias = self.producto_srv.obtener_categorias_con_conteo()
            productos_existentes = self.producto_srv.listar_todos_productos()
        except Exception as error:
            print(Color.error(str(error)))
            pausar()
            return
        if not categorias:
            print(Color.aviso("No hay categorias disponibles."))
            pausar()
            return

        datos = {}
        paso = 1
        try:
            while paso <= 4:
                try:
                    if paso == 1:
                        enc = imprimir_encabezado_sesion(
                            self.usuario,
                            breadcrumb=["Inicio", "Panel Admin", "Anadir Producto", "Categoria"]
                        )
                        opts = [f"{c['codigo']:<10} {c['nombre']}" for c in categorias]
                        opts.append("<< Volver al menu anterior")
                        idx = seleccionar_con_flechas(
                            "ANADIR PRODUCTO - Selecciona categoria", opts, enc
                        )
                        if idx == len(categorias):
                            return
                        datos["categoria"] = categorias[idx]
                    elif paso == 2:
                        codigo = pedir_codigo(
                            prompt="Codigo del producto", longitud_max=4, ejemplo="P099"
                        )
                        for producto in productos_existentes:
                            if codigo.upper() == producto["codigo"].upper():
                                raise ValueError(f"El codigo '{codigo}' ya esta registrado.")
                        datos["codigo"] = codigo
                    elif paso == 3:
                        datos["nombre"] = pedir_nombre_propio(
                            prompt="Nombre del producto", ejemplo="Moka Navideno"
                        )
                    elif paso == 4:
                        datos["precio"] = pedir_precio(ejemplo="65.00")
                    paso += 1
                except PasoAnterior:
                    if paso == 1:
                        return
                    paso -= 1
                except ValueError as error:
                    print(Color.error(str(error)))
                    pausar()
        except (OperacionCancelada, PasoAnterior):
            print(Color.aviso("Operacion cancelada. No se creo el producto."))
            pausar()
            return

        cat = datos["categoria"]
        codigo = datos["codigo"]
        nombre = datos["nombre"]
        precio = datos["precio"]
        limpiar_pantalla()
        print(imprimir_encabezado_sesion(
            self.usuario,
            breadcrumb=["Inicio", "Panel Admin", "Anadir Producto", "Datos"]
        ))
        pfx = _prefijo(_ancho())
        print(f"\n{pfx}  {Color.titulo('ANADIR NUEVO PRODUCTO')}")
        print(f"{pfx}  Categoria: {Color.CARAMELO}{cat['nombre']}{Color.RESET}\n")
        print(Color.info("El producto quedara con estatus Activo. Para que sea vendible debe tener receta asignada."))
        print()

        while True:
            try:
                ok, msg = self.producto_srv.crear_producto_menu(
                    codigo, nombre, precio, cat["codigo"]
                )
            except Exception as error:
                print(Color.error(str(error)))
                pausar()
                return
            if ok:
                print(Color.ok(msg))
                pausar()
                break

            print(Color.error(msg))
            pausar()
            texto = msg.lower()
            if "duplicate" in texto or "duplicad" in texto:
                try:
                    productos_existentes = self.producto_srv.listar_todos_productos()
                except Exception as error:
                    print(Color.error(str(error)))
                    pausar()
                    return
                try:
                    while True:
                        try:
                            codigo = pedir_codigo(
                                prompt="Codigo del producto", longitud_max=4, ejemplo="P099"
                            )
                            repetido = False
                            for producto in productos_existentes:
                                if codigo.upper() == producto["codigo"].upper():
                                    repetido = True
                            if repetido:
                                raise ValueError(f"El codigo '{codigo}' ya esta registrado.")
                            break
                        except ValueError as error:
                            print(Color.error(str(error)))
                            pausar()
                except (OperacionCancelada, PasoAnterior):
                    print(Color.aviso("Operacion cancelada. No se creo el producto."))
                    pausar()
                    return
                continue
            if "categoria" in texto and "foreign key" in texto:
                try:
                    categorias = self.producto_srv.obtener_categorias_con_conteo()
                except Exception as error:
                    print(Color.error(str(error)))
                    pausar()
                    return
                opts = [f"{c['codigo']:<10} {c['nombre']}" for c in categorias] + [
                    "<< Cancelar y regresar"
                ]
                idx = seleccionar_con_flechas(
                    "ANADIR PRODUCTO - Selecciona categoria",
                    opts,
                    imprimir_encabezado_sesion(
                        self.usuario,
                        breadcrumb=["Inicio", "Panel Admin", "Anadir Producto", "Categoria"]
                    )
                )
                if idx == len(categorias):
                    return
                cat = categorias[idx]
                continue
            return
        print(Color.info("Ahora puedes asignar los insumos de la receta."))
        self.configurar_receta(codigo.upper(), nombre)
