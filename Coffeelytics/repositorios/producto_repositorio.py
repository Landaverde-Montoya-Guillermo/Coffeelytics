from repositorios.base_repositorios import BaseRepositorio
from entidades.producto import Producto
from config.reglas import ESTATUS_ACTIVO


class ProductoRepositorio(BaseRepositorio):

    def obtener_categorias_con_conteo(self):
        self._cursor.execute("""
            SELECT c.codigo, c.nombre,
                   COUNT(DISTINCT p.codigo) AS total,
                   COUNT(DISTINCT CASE
                       WHEN p.estatus = %s AND ri.insumo IS NOT NULL THEN p.codigo
                   END) AS disponibles
            FROM categoria_producto c
            LEFT JOIN producto p ON c.codigo = p.categoria
            LEFT JOIN receta r ON r.producto = p.codigo
            LEFT JOIN rec_insum ri ON ri.receta = r.codigo
            GROUP BY c.codigo, c.nombre
            ORDER BY c.codigo
        """, (ESTATUS_ACTIVO,))
        return self._cursor.fetchall()

    def obtener_por_categoria(self, cod_categoria):
        self._cursor.execute("""
            SELECT p.codigo, p.nombre, p.precio, p.estatus,
                   c.codigo AS cat_cod, c.nombre AS cat_nom
            FROM producto p
            INNER JOIN categoria_producto c ON p.categoria = c.codigo
            WHERE p.categoria = %s
              AND p.estatus = %s
              AND EXISTS (
                  SELECT 1
                  FROM receta r
                  INNER JOIN rec_insum ri ON ri.receta = r.codigo
                  WHERE r.producto = p.codigo
              )
            ORDER BY p.codigo
        """, (cod_categoria, ESTATUS_ACTIVO))
        return [
            Producto(f["codigo"], f["nombre"], f["precio"],
                     f["estatus"], f["cat_cod"], f["cat_nom"])
            for f in self._cursor.fetchall()
        ]

    def es_vendible(self, cod_producto):
        self._cursor.execute("""
            SELECT 1
            FROM producto p
            WHERE p.codigo = %s
              AND p.estatus = %s
              AND EXISTS (
                  SELECT 1
                  FROM receta r
                  INNER JOIN rec_insum ri ON ri.receta = r.codigo
                  WHERE r.producto = p.codigo
              )
        """, (cod_producto, ESTATUS_ACTIVO))
        return self._cursor.fetchone() is not None

    def obtener_catalogo_vendible(self):
        """Todos los productos activos con receta y insumos, de todas las categorias."""
        self._cursor.execute("""
            SELECT p.codigo, p.nombre, p.precio, p.estatus,
                   c.codigo AS cat_cod, c.nombre AS cat_nom
            FROM producto p
            INNER JOIN categoria_producto c ON p.categoria = c.codigo
            WHERE p.estatus = %s
              AND EXISTS (
                  SELECT 1
                  FROM receta r
                  INNER JOIN rec_insum ri ON ri.receta = r.codigo
                  WHERE r.producto = p.codigo
              )
            ORDER BY p.nombre
        """, (ESTATUS_ACTIVO,))
        return [
            Producto(f["codigo"], f["nombre"], f["precio"],
                     f["estatus"], f["cat_cod"], f["cat_nom"])
            for f in self._cursor.fetchall()
        ]

    def listar_todos(self):
        self._cursor.execute("""
            SELECT p.codigo, p.nombre, p.precio, p.estatus, c.nombre AS categoria
            FROM producto p
            INNER JOIN categoria_producto c ON p.categoria = c.codigo
            ORDER BY p.codigo
        """)
        return self._cursor.fetchall()

    def listar_codigos(self):
        self._cursor.execute("SELECT codigo FROM producto")
        return [fila["codigo"] if isinstance(fila, dict) else fila[0]
                for fila in self._cursor.fetchall()]

    def crear(self, producto):
        self._cursor.execute("""
            INSERT INTO producto (codigo, nombre, precio, estatus, categoria)
            VALUES (%s, %s, %s, %s, %s)
        """, (producto.codigo, producto.nombre, producto.precio,
              producto.estatus, producto.categoria_cod))

    def actualizar_estatus(self, cod_producto, nuevo_estatus):
        self._cursor.execute(
            "UPDATE producto SET estatus = %s WHERE codigo = %s",
            (nuevo_estatus, cod_producto)
        )

    def obtener_receta(self, prod_codigo):
        self._cursor.execute(
            """
            SELECT i.codigo AS insumo_codigo,
                   i.nombre,
                   ri.cantidad,
                   ri.cantidad AS requerido,
                   i.stockActual,
                   u.abreviatura,
                   u.abreviatura AS unidad_medida
            FROM receta r
            JOIN rec_insum ri ON r.codigo = ri.receta
            JOIN insumo i ON ri.insumo = i.codigo
            JOIN unidad_medida u ON i.unidad = u.codigo
            WHERE r.producto = %s
            ORDER BY i.nombre
            """,
            (prod_codigo,)
        )
        return self._cursor.fetchall()

    def obtener_codigo_receta(self, cod_producto):
        self._cursor.execute("SELECT codigo FROM receta WHERE producto = %s", (cod_producto,))
        fila = self._cursor.fetchone()
        if not fila:
            return None
        return fila["codigo"] if isinstance(fila, dict) else fila[0]

    def existe_codigo_receta(self, cod_receta):
        self._cursor.execute("SELECT 1 FROM receta WHERE codigo = %s", (cod_receta,))
        return self._cursor.fetchone() is not None

    def crear_receta(self, cod_receta, cod_producto):
        self._cursor.execute(
            "INSERT INTO receta (codigo, producto) VALUES (%s, %s)",
            (cod_receta, cod_producto)
        )

    def asignar_insumo_receta(self, cod_receta, cod_insumo, cantidad):
        self._cursor.execute("""
            INSERT INTO rec_insum (insumo, receta, cantidad) VALUES (%s, %s, %s)
            ON DUPLICATE KEY UPDATE cantidad = VALUES(cantidad)
        """, (cod_insumo, cod_receta, cantidad))