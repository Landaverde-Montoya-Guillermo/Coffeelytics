from repositorios.base_repositorios import BaseRepositorio


class ConsultasRepositorio(BaseRepositorio):

    def resumen_financiero(self, filtro_sql):
        self._cursor.execute(
            f"SELECT COUNT(*) AS num_ventas, COALESCE(SUM(total),0) AS ingresos FROM venta WHERE {filtro_sql}"
        )
        ventas = self._cursor.fetchone() or {"num_ventas": 0, "ingresos": 0}
        self._cursor.execute(
            f"SELECT COALESCE(SUM(total),0) AS gastos FROM compra WHERE {filtro_sql}"
        )
        compras = self._cursor.fetchone() or {"gastos": 0}
        return ventas, compras

    def ventas_del_dia_por_metodo(self):
        """
        Ventas de la fecha actual agrupadas por metodo de pago.
        El subtotal e IVA salen de las lineas (prod_venta); el total, de la cabecera (venta).
        """
        self._cursor.execute("""
            SELECT m.codigo, m.descripcion AS metodo,
                   COUNT(v.codigo)           AS operaciones,
                   COALESCE(SUM(x.sub), 0)   AS subtotal,
                   COALESCE(SUM(x.iva), 0)   AS iva,
                   COALESCE(SUM(v.total), 0) AS total
            FROM venta v
            INNER JOIN metodo_pago m ON v.metodoPago = m.codigo
            LEFT JOIN (
                SELECT venta, SUM(subtotal) AS sub, SUM(totalIVA) AS iva
                FROM prod_venta
                GROUP BY venta
            ) x ON x.venta = v.codigo
            WHERE DATE(v.fecha) = CURDATE()
            GROUP BY m.codigo, m.descripcion
            ORDER BY m.descripcion
        """)
        return self._cursor.fetchall()

    def ventas_por_barista(self):
        """Todos los baristas (LEFT JOIN empleado-venta) con numero de tickets y total vendido."""
        self._cursor.execute("""
            SELECT e.num AS id,
                   CONCAT(e.nombrePila, ' ', e.primApell) AS barista,
                   COUNT(v.codigo)           AS tickets,
                   COALESCE(SUM(v.total), 0) AS total
            FROM empleado e
            LEFT JOIN venta v ON v.empleado = e.num
            WHERE e.rol = 'BARS'
            GROUP BY e.num, e.nombrePila, e.primApell
            ORDER BY total DESC, e.num
        """)
        return self._cursor.fetchall()

    def ventas_de_barista(self, num_empleado):
        """Todos los tickets cobrados por un barista, del mas reciente al mas antiguo."""
        self._cursor.execute("""
            SELECT v.codigo AS folio,
                   DATE_FORMAT(v.fecha, '%d/%m/%Y %H:%i') AS fecha,
                   v.nombreCliente AS cliente,
                   m.descripcion   AS metodo,
                   v.total
            FROM venta v
            INNER JOIN empleado e ON v.empleado = e.num
            INNER JOIN metodo_pago m ON v.metodoPago = m.codigo
            WHERE v.empleado = %s AND e.rol = 'BARS'
            ORDER BY v.fecha, v.codigo
        """, (num_empleado,))
        return self._cursor.fetchall()

    def listar_ventas_recientes(self, limite=20):
        self._cursor.execute(f"""
            SELECT v.codigo AS folio,
                   DATE_FORMAT(v.fecha, '%d/%m %H:%i') AS fecha,
                   CONCAT(e.nombrePila,' ',e.primApell) AS barista,
                   v.nombreCliente                       AS cliente,
                   m.descripcion                        AS metodo,
                   v.total
            FROM venta v
            INNER JOIN empleado e    ON v.empleado   = e.num
            INNER JOIN metodo_pago m ON v.metodoPago = m.codigo
            ORDER BY v.codigo DESC
            LIMIT {int(limite)}
        """)
        return self._cursor.fetchall()

    def detalle_venta_encabezado(self, folio_venta):
        self._cursor.execute("""
            SELECT v.codigo AS folio, v.fecha, v.nombreCliente,
                   CONCAT(e.nombrePila,' ',e.primApell) AS empleado,
                   m.descripcion AS metodoPago, v.total
            FROM venta v
            INNER JOIN empleado e    ON v.empleado   = e.num
            INNER JOIN metodo_pago m ON v.metodoPago = m.codigo
            WHERE v.codigo = %s
        """, (folio_venta,))
        return self._cursor.fetchone()

    def detalle_venta_lineas(self, folio_venta):
        self._cursor.execute("""
            SELECT p.codigo, p.nombre, pv.precioUnitarioVenta AS precio,
                   pv.cantidad, pv.subtotal, pv.totalIVA, pv.total
            FROM prod_venta pv
            INNER JOIN producto p ON pv.producto = p.codigo
            WHERE pv.venta = %s
        """, (folio_venta,))
        return self._cursor.fetchall()

    def detalle_compra_encabezado(self, folio_compra):
        self._cursor.execute("""
            SELECT c.codigo AS folio, c.fecha, p.nombre AS proveedor, p.ciudad, c.total
            FROM compra c
            INNER JOIN proveedor p ON c.proveedor = p.codigo
            WHERE c.codigo = %s
        """, (folio_compra,))
        return self._cursor.fetchone()

    def compras_registradas(self):
        self._cursor.execute("""
            SELECT c.codigo AS folio,
                   DATE_FORMAT(c.fecha, '%d/%m/%Y') AS fecha,
                   p.nombre AS proveedor,
                   COALESCE(NULLIF(CONCAT_WS(' ', e.nombrePila, e.primApell, e.segApell), ''),
                            'Sin asignar') AS empleado,
                   c.total
            FROM compra c
            INNER JOIN proveedor p ON c.proveedor = p.codigo
            INNER JOIN empleado e ON c.empleado = e.num
            ORDER BY c.codigo DESC
        """)
        return self._cursor.fetchall()

    def detalle_compra_lineas(self, folio_compra):
        self._cursor.execute("""
            SELECT i.codigo, i.nombre, ic.precioUnitarioCom AS precio,
                   ic.cantidad, ic.subtotal, ic.totalIVA, ic.total
            FROM insum_com ic
            INNER JOIN insumo i ON ic.insumo = i.codigo
            WHERE ic.compra = %s
        """, (folio_compra,))
        return self._cursor.fetchall()

    def mermas_ultima_semana(self):
        self._cursor.execute("""
            SELECT m.codigo, m.fecha, i.codigo AS insumo_codigo, i.nombre AS insumo,
                   CONCAT(m.cantidad,' ',u.abreviatura) AS cantidad,
                   tm.nombre AS tipo_merma, m.motivo,
                   COALESCE(NULLIF(CONCAT_WS(' ', e.nombrePila, e.primApell, e.segApell), ''),
                            'Sin asignar') AS barista
            FROM merma m
            INNER JOIN insumo i        ON m.insumo = i.codigo
            INNER JOIN unidad_medida u ON i.unidad = u.codigo
            INNER JOIN tipo_merma tm   ON m.tipo   = tm.codigo
            LEFT JOIN empleado e       ON m.idEmpleado = e.num
            WHERE m.fecha >= DATE_SUB(CURDATE(), INTERVAL 7 DAY)
            ORDER BY m.fecha DESC, m.codigo DESC
        """)
        return self._cursor.fetchall()

    def merma_por_folio(self, folio):
        self._cursor.execute("""
            SELECT m.codigo, m.fecha, i.codigo AS insumo_codigo, i.nombre AS insumo,
                   CONCAT(m.cantidad,' ',u.abreviatura) AS cantidad,
                   tm.nombre AS tipo_merma, m.motivo,
                   COALESCE(NULLIF(CONCAT_WS(' ', e.nombrePila, e.primApell, e.segApell), ''),
                            'Sin asignar') AS barista
            FROM merma m
            INNER JOIN insumo i        ON m.insumo = i.codigo
            INNER JOIN unidad_medida u ON i.unidad = u.codigo
            INNER JOIN tipo_merma tm   ON m.tipo   = tm.codigo
            LEFT JOIN empleado e       ON m.idEmpleado = e.num
            WHERE m.codigo = %s
        """, (folio,))
        return self._cursor.fetchone()

    def ventas_por_empleado_fecha(self, num_empleado, fecha_str):
        self._cursor.execute("""
            SELECT DATE_FORMAT(v.fecha, '%Y-%m-%d %H:%i') AS fecha,
                   CONCAT_WS(' ', e.nombrePila, e.primApell, e.segApell) AS empleado,
                   v.codigo AS folio,
                   v.total,
                   mp.descripcion AS metodoPago
            FROM venta v
            INNER JOIN empleado e ON v.empleado = e.num
            INNER JOIN metodo_pago mp ON v.metodoPago = mp.codigo
            WHERE DATE(v.fecha) = %s AND v.empleado = %s AND e.rol = 'BARS'
            ORDER BY v.fecha, v.codigo
        """, (fecha_str, num_empleado))
        return self._cursor.fetchall()

    def ventas_barista_ultimos_7_dias(self, num_empleado):
        self._cursor.execute("""
            SELECT DATE_FORMAT(v.fecha, '%Y-%m-%d %H:%i') AS fecha,
                   CONCAT_WS(' ', e.nombrePila, e.primApell, e.segApell) AS empleado,
                   v.codigo AS folio,
                   v.total,
                   mp.descripcion AS metodoPago
            FROM venta v
            INNER JOIN empleado e ON v.empleado = e.num
            INNER JOIN metodo_pago mp ON v.metodoPago = mp.codigo
            WHERE v.fecha >= DATE_SUB(CURDATE(), INTERVAL 7 DAY)
              AND v.empleado = %s AND e.rol = 'BARS'
            ORDER BY v.fecha, v.codigo
        """, (num_empleado,))
        return self._cursor.fetchall()

    def ventas_barista_por_mes(self, num_empleado, mes, anio):
        self._cursor.execute("""
            SELECT DATE_FORMAT(v.fecha, '%Y-%m-%d %H:%i') AS fecha,
                   CONCAT_WS(' ', e.nombrePila, e.primApell, e.segApell) AS empleado,
                   v.codigo AS folio,
                   v.total,
                   mp.descripcion AS metodoPago
            FROM venta v
            INNER JOIN empleado e ON v.empleado = e.num
            INNER JOIN metodo_pago mp ON v.metodoPago = mp.codigo
            WHERE MONTH(v.fecha) = %s AND YEAR(v.fecha) = %s
              AND v.empleado = %s AND e.rol = 'BARS'
            ORDER BY v.fecha, v.codigo
        """, (mes, anio, num_empleado))
        return self._cursor.fetchall()