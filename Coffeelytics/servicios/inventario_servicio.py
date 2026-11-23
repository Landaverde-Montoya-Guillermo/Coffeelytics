from decimal import Decimal
from mysql.connector import Error
from config.database import transaccion
from config.reglas import ESTATUS_ACTIVO, ESTATUS_NO_DISPONIBLE
from entidades.base import EntidadBase, ValidacionError
from repositorios.catalogos_repositorio import CatalogosRepositorio
from repositorios.insumo_repositorio import InsumoRepositorio
from repositorios.producto_repositorio import ProductoRepositorio


class InventarioServicio:

    @staticmethod
    def sincronizar_estatus_productos(cursor):
        """
        Recorre todos los productos dentro de una transacción activa:
        Si algún insumo de su receta tiene stock < requerido -> ESTATUS_NO_DISPONIBLE (2).
        Si todos alcanzan -> ESTATUS_ACTIVO (1).
        """
        prod_repo = ProductoRepositorio(cursor)
        for cod_prod in prod_repo.listar_codigos():
            ingredientes = prod_repo.obtener_receta(cod_prod)
            disponible = all(
                Decimal(str(ing["stockActual"])) >= Decimal(str(ing["requerido"]))
                for ing in ingredientes
            ) if ingredientes else True
            nuevo_estatus = ESTATUS_ACTIVO if disponible else ESTATUS_NO_DISPONIBLE
            prod_repo.actualizar_estatus(cod_prod, nuevo_estatus)

    def listar_todos_insumos(self):
        with transaccion(dictionary=True) as cursor:
            repo = InsumoRepositorio(cursor)
            return repo.listar_todos()

    def obtener_stock_general(self):
        with transaccion(dictionary=True) as cursor:
            repo = InsumoRepositorio(cursor)
            return repo.obtener_stock_general()

    def obtener_detalle_stock(self, cod_insumo):
        with transaccion(dictionary=True) as cursor:
            repo = InsumoRepositorio(cursor)
            return repo.obtener_detalle_stock(cod_insumo)

    def obtener_insumos_mesa(self):
        with transaccion(dictionary=True) as cursor:
            repo = InsumoRepositorio(cursor)
            return repo.obtener_insumos_mesa()

    def obtener_insumos_receta(self):
        with transaccion(dictionary=True) as cursor:
            repo = InsumoRepositorio(cursor)
            return repo.obtener_insumos_receta()

    def listar_unidades_medida(self):
        with transaccion(dictionary=True) as cursor:
            repo = CatalogosRepositorio(cursor)
            return repo.listar_unidades_medida()

    def listar_categorias_insumo(self):
        with transaccion(dictionary=True) as cursor:
            repo = CatalogosRepositorio(cursor)
            return repo.listar_categorias_insumo()

    def obtener_alertas_stock_bajo(self):
        with transaccion(dictionary=True) as cursor:
            repo = InsumoRepositorio(cursor)
            return repo.obtener_alertas_stock_bajo()

    def registrar_insumo(self, codigo, nombre, stock_ini, stock_min, seccion, unidad, estante, cat):
        try:
            cod_limpio = EntidadBase.validar_texto(codigo, "código", 6).upper()
            nom_limpio = EntidadBase.validar_texto(nombre, "nombre", 60)
            s_ini = EntidadBase.validar_positivo(stock_ini, "stock inicial", permitir_cero=True)
            s_min = EntidadBase.validar_positivo(stock_min, "stock mínimo", permitir_cero=True)

            with transaccion() as cursor:
                repo = InsumoRepositorio(cursor)
                repo.insertar(cod_limpio, nom_limpio, s_ini, s_min, seccion, unidad, estante, cat)
            return True, f"Insumo '{nom_limpio}' registrado."
        except ValidacionError as e:
            return False, str(e)
        except Error as e:
            return False, f"Error al registrar insumo: {str(e)}"