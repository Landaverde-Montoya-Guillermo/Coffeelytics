from decimal import Decimal
from mysql.connector import Error
from config.database import transaccion
from entidades.base import EntidadBase, ValidacionError, StockInsuficienteError
from repositorios.merma_repositorio import MermaRepositorio
from repositorios.insumo_repositorio import InsumoRepositorio
from servicios.inventario_servicio import InventarioServicio


class MermaServicio:

    def listar_tipos_merma(self):
        with transaccion(dictionary=True) as cursor:
            repo = MermaRepositorio(cursor)
            return repo.listar_tipos()

    def registrar_merma(self, cod_insumo, tipo_merma, cantidad, motivo, num_empleado):
        try:
            cant_val = EntidadBase.validar_positivo(cantidad, "cantidad de merma")
            motivo_limpio = EntidadBase.validar_texto(motivo, "motivo", 300)

            with transaccion(dictionary=True) as cursor:
                merma_repo = MermaRepositorio(cursor)
                insumo_repo = InsumoRepositorio(cursor)

                ins_db = insumo_repo.obtener_por_codigo(cod_insumo)
                if not ins_db:
                    raise ValidacionError("Insumo no encontrado.")

                stock_actual = Decimal(str(ins_db["stockActual"]))
                cant_dec = Decimal(str(cant_val))
                if stock_actual < cant_dec:
                    raise StockInsuficienteError(
                        f"No puedes mermar {cant_dec}; el stock actual es {stock_actual}."
                    )

                merma_repo.insertar(motivo_limpio, cant_val, tipo_merma, cod_insumo, num_empleado)
                insumo_repo.actualizar_stock(cod_insumo, stock_actual - cant_dec)
                InventarioServicio.sincronizar_estatus_productos(cursor)

            return True, "Merma registrada y stock actualizado."
        except (ValidacionError, StockInsuficienteError) as e:
            return False, str(e)
        except Error as e:
            return False, f"Error al registrar merma: {str(e)}"