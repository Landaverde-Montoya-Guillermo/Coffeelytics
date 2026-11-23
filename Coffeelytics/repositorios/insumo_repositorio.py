from repositorios.base_repositorios import BaseRepositorio


class InsumoRepositorio(BaseRepositorio):

    def listar_todos(self):
        self._cursor.execute("""
            SELECT i.codigo, i.nombre, i.stockActual, i.stockMin, u.abreviatura,
                   ci.nombre AS categoria
            FROM insumo i
            INNER JOIN unidad_medida u ON i.unidad = u.codigo
            INNER JOIN categoria_insumo ci ON i.categoria = ci.codigo
            ORDER BY i.codigo
        """)
        return self._cursor.fetchall()

    def obtener_stock_general(self):
        self._cursor.execute("""
            SELECT i.codigo, i.nombre, ci.nombre AS categoria,
                   u.abreviatura AS unidad, i.stockActual, i.stockMin
            FROM insumo i
            INNER JOIN categoria_insumo ci ON i.categoria = ci.codigo
            INNER JOIN unidad_medida u ON i.unidad = u.codigo
            ORDER BY i.codigo
        """)
        return self._cursor.fetchall()

    def obtener_detalle_stock(self, cod_insumo):
        self._cursor.execute("""
            SELECT i.codigo, i.nombre, ci.codigo AS categoria_codigo,
                   ci.nombre AS categoria, u.nombre AS unidad_medida,
                   u.abreviatura AS unidad, i.stockActual, i.stockMin,
                   i.seccion, e.codigo AS estante
            FROM insumo i
            INNER JOIN categoria_insumo ci ON i.categoria = ci.codigo
            INNER JOIN unidad_medida u ON i.unidad = u.codigo
            INNER JOIN estante e ON i.estante = e.codigo
            WHERE i.codigo = %s
        """, (cod_insumo,))
        return self._cursor.fetchone()

    def obtener_insumos_mesa(self):
        self._cursor.execute("""
            SELECT i.codigo, i.nombre, i.stockActual, i.stockMin, u.abreviatura
            FROM insumo i
            INNER JOIN unidad_medida u ON i.unidad = u.codigo
            WHERE i.categoria = %s
            ORDER BY i.codigo
        """, ("DESC",))
        return self._cursor.fetchall()

    def obtener_insumos_receta(self):
        self._cursor.execute("""
            SELECT i.codigo, i.nombre, i.stockActual, i.stockMin, u.abreviatura
            FROM insumo i
            INNER JOIN unidad_medida u ON i.unidad = u.codigo
            WHERE i.categoria <> %s
            ORDER BY i.codigo
        """, ("DESC",))
        return self._cursor.fetchall()

    def obtener_por_codigo(self, cod_insumo):
        self._cursor.execute(
            "SELECT codigo, nombre, stockActual, stockMin FROM insumo WHERE codigo = %s",
            (cod_insumo,)
        )
        return self._cursor.fetchone()

    def insertar(self, codigo, nombre, stock_ini, stock_min, seccion, unidad, estante, cat):
        self._cursor.execute("""
            INSERT INTO insumo
            (codigo, nombre, stockActual, stockMin, seccion, unidad, estante, categoria)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """, (codigo.upper(), nombre, stock_ini, stock_min, seccion, unidad, estante, cat))

    def actualizar_stock(self, cod_insumo, nuevo_stock):
        self._cursor.execute(
            "UPDATE insumo SET stockActual = %s WHERE codigo = %s",
            (nuevo_stock, cod_insumo)
        )

    def obtener_alertas_stock_bajo(self):
        self._cursor.execute("""
            SELECT i.codigo, i.nombre, i.stockActual, i.stockMin, u.abreviatura,
                   COALESCE(p.nombre,   'Sin proveedor') AS proveedor,
                   COALESCE(p.telefono, 'N/A')           AS telefono,
                   COALESCE(p.ciudad,   'Tijuana')       AS ciudad
            FROM insumo i
            INNER JOIN unidad_medida u ON i.unidad = u.codigo
            LEFT  JOIN insum_com ic    ON i.codigo  = ic.insumo
            LEFT  JOIN compra c        ON ic.compra = c.codigo
            LEFT  JOIN proveedor p     ON c.proveedor = p.codigo
            WHERE i.stockActual <= i.stockMin
            GROUP BY i.codigo, i.nombre, i.stockActual, i.stockMin,
                     u.abreviatura, p.nombre, p.telefono, p.ciudad
            ORDER BY i.stockActual ASC
        """)
        return self._cursor.fetchall()