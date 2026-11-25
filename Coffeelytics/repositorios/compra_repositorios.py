from repositorios.base_repositorios import BaseRepositorio


class CompraRepositorio(BaseRepositorio):

    def insertar_encabezado(self, total, cod_proveedor, metodo_pago, num_empleado):
        self._cursor.execute("""
            INSERT INTO compra (fecha, total, proveedor, metodoPago, empleado)
            VALUES (CURDATE(), %s, %s, %s, %s)
        """, (total, cod_proveedor, metodo_pago, num_empleado))
        return self._cursor.lastrowid

    def insertar_linea(self, folio_compra, cod_insumo, cantidad, precio_unit, subtotal, total_iva, total):
        self._cursor.execute("""
            INSERT INTO insum_com
            (compra, insumo, cantidad, precioUnitarioCom, subtotal, totalIVA, total)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """, (folio_compra, cod_insumo, cantidad, precio_unit, subtotal, total_iva, total))