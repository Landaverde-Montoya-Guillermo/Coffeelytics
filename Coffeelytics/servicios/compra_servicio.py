import datetime
from decimal import Decimal
from mysql.connector import Error
from config.database import transaccion
from config.reglas import IVA_FRONTERA, IVA_GENERAL, CIUDADES_FRONTERA
from entidades.base import EntidadBase, ValidacionError
from repositorios.compra_repositorios import CompraRepositorio
from repositorios.proveedor_repositorio import ProveedorRepositorio
from repositorios.insumo_repositorio import InsumoRepositorio
from servicios.inventario_servicio import InventarioServicio


class CompraServicio:

    def listar_proveedores(self):
        with transaccion(dictionary=True) as cursor:
            repo = ProveedorRepositorio(cursor)
            return repo.listar_todos()

    @staticmethod
    def calcular_totales_previos(ciudad_proveedor, cantidad, precio_unit):
        ciudad = str(ciudad_proveedor or "").strip().lower()
        tasa = IVA_FRONTERA if ciudad in CIUDADES_FRONTERA else IVA_GENERAL
        sub = round(float(cantidad) * float(precio_unit), 2)
        iva = round(sub * tasa, 2)
        total = round(sub + iva, 2)
        return tasa, sub, iva, total

    def registrar_compra_proveedor(self, cod_proveedor, cod_insumo, cantidad, precio_unit,
                                   metodo_pago, num_empleado, autorizo="", unidad=""):
        """
        Registra la compra y actualiza el stock.
        Devuelve (ok, mensaje, datos). `datos` es el dict del comprobante (None si falla),
        con el que GeneradorDocumentos arma el ticket en consola y el respaldo .txt.
        """
        try:
            cant_val = EntidadBase.validar_positivo(cantidad, "cantidad comprada")
            precio_val = EntidadBase.validar_positivo(precio_unit, "precio unitario")

            with transaccion(dictionary=True) as cursor:
                prov_repo = ProveedorRepositorio(cursor)
                compra_repo = CompraRepositorio(cursor)
                insumo_repo = InsumoRepositorio(cursor)

                prov = prov_repo.obtener_por_codigo(cod_proveedor)
                if not prov:
                    raise ValidacionError("Proveedor no encontrado.")

                ins_db = insumo_repo.obtener_por_codigo(cod_insumo)
                if not ins_db:
                    raise ValidacionError("Insumo no encontrado.")

                tasa, sub, iva, total = self.calcular_totales_previos(
                    prov.get("ciudad", ""), cant_val, precio_val
                )

                folio = compra_repo.insertar_encabezado(total, cod_proveedor, metodo_pago, num_empleado)
                compra_repo.insertar_linea(folio, cod_insumo, cant_val, precio_val, sub, iva, total)

                stock_anterior = Decimal(str(ins_db["stockActual"]))
                nuevo_stock = stock_anterior + Decimal(str(cant_val))
                insumo_repo.actualizar_stock(cod_insumo, nuevo_stock)

                InventarioServicio.sincronizar_estatus_productos(cursor)

            datos = {
                "folio": f"#{int(folio):05d}",
                "folio_num": int(folio),
                "fecha": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "proveedor": prov["nombre"],
                "ciudad": prov.get("ciudad") or "",
                "autorizo": autorizo or f"Empleado {num_empleado}",
                "metodo": metodo_pago,
                "insumo": ins_db["nombre"],
                "cantidad": float(cant_val),
                "unidad": unidad,
                "costo_unit": float(precio_val),
                "subtotal": sub,
                "iva": iva,
                "iva_pct": int(round(tasa * 100)),
                "total": total,
                "stock_anterior": float(stock_anterior),
                "stock_nuevo": float(nuevo_stock),
                "respaldo": None,
            }
            return True, f"Compra #{folio} registrada (IVA {int(tasa * 100)}%). Productos reactivados.", datos
        except ValidacionError as e:
            return False, str(e), None
        except Error as e:
            return False, f"Error al registrar compra: {str(e)}", None