from decimal import Decimal
from mysql.connector import Error
from config.database import transaccion
from config.reglas import UNIDADES_CONTEO_ENTERO
from entidades.base import EntidadBase, ValidacionError, StockInsuficienteError
from repositorios.consumible_mesa_repositorio import ConsumibleMesaRepositorio
from repositorios.insumo_repositorio import InsumoRepositorio
from servicios.inventario_servicio import InventarioServicio


class DespachoServicio:

    def surtir_mesa_consumibles(self, cod_insumo, cantidad, mesa_cod="MESA1"):
        try:
            cant_val = EntidadBase.validar_positivo(cantidad, "cantidad a surtir")

            with transaccion(dictionary=True) as cursor:
                mesa_repo = ConsumibleMesaRepositorio(cursor)
                insumo_repo = InsumoRepositorio(cursor)

                ins_db = insumo_repo.obtener_por_codigo(cod_insumo)
                if not ins_db:
                    raise ValidacionError("Insumo no encontrado.")

                stock_actual = Decimal(str(ins_db["stockActual"]))
                cant_dec = Decimal(str(cant_val))
                if (
                    ins_db["unidad_codigo"] in UNIDADES_CONTEO_ENTERO
                    and cant_dec != cant_dec.to_integral_value()
                ):
                    raise ValidacionError(
                        f"No se permiten decimales para la unidad "
                        f"{ins_db['unidad_codigo']}. Ingresa una cantidad entera."
                    )
                if stock_actual < cant_dec:
                    raise StockInsuficienteError(
                        f"Stock insuficiente en almacén ({stock_actual}) para surtir {cant_dec}."
                    )

                insumo_repo.actualizar_stock(cod_insumo, stock_actual - cant_dec)
                mesa_repo.agregar_a_mesa(cod_insumo, mesa_cod, cant_dec)
                InventarioServicio.sincronizar_estatus_productos(cursor)

            return True, "Mesa surtida correctamente."
        except (ValidacionError, StockInsuficienteError) as e:
            return False, str(e)
        except Error as e:
            return False, f"Error al surtir mesa: {str(e)}"