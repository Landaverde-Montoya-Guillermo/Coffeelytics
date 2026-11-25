from mysql.connector import Error
from config.database import transaccion
from config.reglas import ESTATUS_ACTIVO
from entidades.base import EntidadBase, ValidacionError
from entidades.producto import Producto
from repositorios.producto_repositorio import ProductoRepositorio
from servicios.inventario_servicio import InventarioServicio


class ProductoServicio:

    def obtener_categorias_con_conteo(self):
        with transaccion(dictionary=True) as cursor:
            repo = ProductoRepositorio(cursor)
            return repo.obtener_categorias_con_conteo()

    def obtener_productos_por_categoria(self, cod_categoria):
        with transaccion(dictionary=True) as cursor:
            repo = ProductoRepositorio(cursor)
            return repo.obtener_por_categoria(cod_categoria)

    def obtener_catalogo_vendible(self):
        """Catalogo vendible completo (todas las categorias), para el buscador del barista."""
        with transaccion(dictionary=True) as cursor:
            repo = ProductoRepositorio(cursor)
            return repo.obtener_catalogo_vendible()

    def es_producto_vendible(self, cod_producto):
        with transaccion(dictionary=True) as cursor:
            repo = ProductoRepositorio(cursor)
            return repo.es_vendible(cod_producto)

    def listar_todos_productos(self):
        with transaccion(dictionary=True) as cursor:
            repo = ProductoRepositorio(cursor)
            return repo.listar_todos()

    def obtener_receta(self, prod_codigo):
        with transaccion(dictionary=True) as cursor:
            repo = ProductoRepositorio(cursor)
            return repo.obtener_receta(prod_codigo)

    def crear_producto_menu(self, codigo, nombre, precio, categoria_cod):
        try:
            nuevo_prod = Producto(codigo, nombre, precio, ESTATUS_ACTIVO, categoria_cod)
            with transaccion() as cursor:
                repo = ProductoRepositorio(cursor)
                repo.crear(nuevo_prod)
            return True, f"Producto '{nuevo_prod.nombre}' agregado."
        except ValidacionError as e:
            return False, str(e)
        except Error as e:
            return False, f"Error al crear producto: {str(e)}"

    def registrar_insumo_en_receta(self, cod_producto, cod_insumo, cantidad):
        return self.registrar_insumos_en_receta(
            cod_producto, [{"codigo": cod_insumo, "cantidad": cantidad}]
        )

    def registrar_insumos_en_receta(self, cod_producto, insumos):
        try:
            if not insumos:
                raise ValidacionError("Debes agregar al menos un insumo a la receta.")

            with transaccion(dictionary=True) as cursor:
                repo = ProductoRepositorio(cursor)
                cod_rec = repo.obtener_codigo_receta(cod_producto)
                if not cod_rec:
                    base = cod_producto[:3]
                    contador = 1
                    candidato = f"R{base}"
                    while repo.existe_codigo_receta(candidato):
                        candidato = f"R{base[:2]}{contador}"
                        contador += 1
                    cod_rec = candidato
                    repo.crear_receta(cod_rec, cod_producto)
                for insumo in insumos:
                    cant_val = EntidadBase.validar_positivo(
                        insumo["cantidad"], "cantidad en receta"
                    )
                    repo.asignar_insumo_receta(
                        cod_rec, insumo["codigo"], cant_val
                    )
                InventarioServicio.sincronizar_estatus_productos(cursor)
            return True, f"Receta {cod_rec} guardada con {len(insumos)} insumo(s)."
        except ValidacionError as e:
            return False, str(e)
        except Error as e:
            return False, f"Error en receta: {str(e)}"