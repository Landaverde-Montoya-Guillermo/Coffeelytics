from datetime import datetime
from decimal import Decimal
from mysql.connector import Error
from config.database import transaccion
<<<<<<< HEAD
from config.reglas import IVA_FRONTERA
=======
from config.negocio import TASA_IVA
>>>>>>> 65287f2 (Programa completo)
from entidades.base import StockInsuficienteError, ValidacionError
from repositorios.venta_repositorios import VentaRepositorio
from repositorios.producto_repositorio import ProductoRepositorio
from repositorios.insumo_repositorio import InsumoRepositorio
from servicios.inventario_servicio import InventarioServicio


class VentaServicio:

    def registrar_venta(self, carrito, metodo_pago_cod, num_empleado):
        if not carrito.items:
            return False, "El carrito está vacío.", None

        try:
            with transaccion(dictionary=True) as cursor:
                venta_repo = VentaRepositorio(cursor)
                prod_repo = ProductoRepositorio(cursor)
                insumo_repo = InsumoRepositorio(cursor)

                # 1. Calcular demanda total de insumos del carrito y validar stock antes de vender
                consumo_total = {}
                for item in carrito.items.values():
                    prod = item["producto"]
                    cant = Decimal(str(item["cantidad"]))
                    if not prod_repo.es_vendible(prod.codigo):
                        raise ValidacionError(
                            f"El producto '{prod.nombre}' ya no esta activo "
                            "o no tiene insumos en su receta."
                        )
                    receta = prod_repo.obtener_receta(prod.codigo)
                    for ing in receta:
                        cod_ins = ing["insumo_codigo"]
                        req = Decimal(str(ing["requerido"])) * cant
                        consumo_total[cod_ins] = consumo_total.get(cod_ins, Decimal("0")) + req

                for cod_ins, req_total in consumo_total.items():
                    ins_db = insumo_repo.obtener_por_codigo(cod_ins)
                    if not ins_db:
                        raise StockInsuficienteError(f"El insumo {cod_ins} no existe en inventario.")
                    stock_actual = Decimal(str(ins_db["stockActual"]))
                    if stock_actual < req_total:
                        raise StockInsuficienteError(
                            f"Stock insuficiente de '{ins_db['nombre']}': "
                            f"disponible {stock_actual}, requerido {req_total}."
                        )

                # 2. Insertar encabezado de venta
                fecha_actual = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                total_venta = carrito.calcular_total()
                folio = venta_repo.insertar_encabezado(
                    fecha_actual, carrito.nombre_cliente, total_venta,
                    metodo_pago_cod, num_empleado
                )

                # 3. Insertar líneas de detalle en prod_venta
                for item in carrito.items.values():
                    prod = item["producto"]
                    cant = item["cantidad"]
                    # El precio ya incluye IVA: el importe de la linea es el total y el subtotal se desglosa.
                    tot_linea = round(prod.precio * cant, 2)
                    sub = round(tot_linea / (1 + TASA_IVA), 2)
                    iva = round(tot_linea - sub, 2)
                    venta_repo.insertar_linea(
                        folio, prod.codigo, cant, prod.precio, sub, iva, tot_linea
                    )

                # 4. Descontar stock real de insumos
                for cod_ins, req_total in consumo_total.items():
                    ins_db = insumo_repo.obtener_por_codigo(cod_ins)
                    nuevo_stock = Decimal(str(ins_db["stockActual"])) - req_total
                    insumo_repo.actualizar_stock(cod_ins, nuevo_stock)

                # 5. Sincronizar estatus de productos
                InventarioServicio.sincronizar_estatus_productos(cursor)

            carrito.fecha_venta = fecha_actual  # misma fecha que se guardo en la BD
            return True, f"Venta #{folio} registrada.", folio
        except StockInsuficienteError as e:
            return False, str(e), None
        except ValidacionError as e:
            return False, str(e), None
        except Error as e:
            return False, f"Error en venta: {str(e)}", None