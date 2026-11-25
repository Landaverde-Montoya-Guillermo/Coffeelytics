from repositorios.base_repositorios import BaseRepositorio


class VentaRepositorio(BaseRepositorio):

    def insertar_encabezado(self, fecha, nombre_cliente, total, metodo_pago, num_empleado):
        self._cursor.execute("""
            INSERT INTO venta (fecha, nombreCliente, total, metodoPago, empleado)
            VALUES (%s, %s, %s, %s, %s)
        """, (fecha, nombre_cliente, total, metodo_pago, num_empleado))
        return self._cursor.lastrowid

    def insertar_linea(self, folio_venta, cod_producto, cantidad, precio_unit, subtotal, total_iva, total):
        self._cursor.execute("""
            INSERT INTO prod_venta
            (venta, producto, cantidad, precioUnitarioVenta, subtotal, totalIVA, total)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """, (folio_venta, cod_producto, cantidad, precio_unit, subtotal, total_iva, total))