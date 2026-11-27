from config.database import transaccion
from repositorios.consultas_repositorio import ConsultasRepositorio
from repositorios.producto_repositorio import ProductoRepositorio


class ReporteServicio:

    def obtener_resumen_financiero(self, periodo="HOY"):
        filtros = {
            "HOY":    "DATE(fecha) = CURDATE()",
            "SEMANA": "YEARWEEK(fecha, 1) = YEARWEEK(CURDATE(), 1)",
            "MES":    "MONTH(fecha) = MONTH(CURDATE()) AND YEAR(fecha) = YEAR(CURDATE())",
            "ANIO":   "YEAR(fecha) = YEAR(CURDATE())",
        }
        filtro = filtros.get(periodo, "1=1")
        with transaccion(dictionary=True) as cursor:
            repo = ConsultasRepositorio(cursor)
            ventas, compras = repo.resumen_financiero(filtro)
            ingresos = float(ventas["ingresos"])
            gastos = float(compras["gastos"])
            return {
                "num_ventas": ventas["num_ventas"],
                "ingresos": ingresos,
                "gastos_insumos": gastos,
                "ganancia_bruta": round(ingresos - gastos, 2)
            }

    def obtener_corte_dia(self):
        """
        Corte de caja del dia: ventas por metodo de pago, gran total y efectivo esperado
        (total de ventas con metodo EFEC). Importes en float para el comprobante.
        """
        with transaccion(dictionary=True) as cursor:
            repo = ConsultasRepositorio(cursor)
            filas = repo.ventas_del_dia_por_metodo()

        metodos = []
        esperado = 0.0
        for f in filas:
            fila = {
                "metodo": f["metodo"],
                "operaciones": int(f["operaciones"]),
                "subtotal": float(f["subtotal"]),
                "iva": float(f["iva"]),
                "total": float(f["total"]),
            }
            metodos.append(fila)
            if f["codigo"] == "EFEC":
                esperado = fila["total"]

        gran = {
            "operaciones": sum(m["operaciones"] for m in metodos),
            "subtotal": round(sum(m["subtotal"] for m in metodos), 2),
            "iva": round(sum(m["iva"] for m in metodos), 2),
            "total": round(sum(m["total"] for m in metodos), 2),
        }
        return {"metodos": metodos, "gran": gran, "esperado": round(esperado, 2)}

    def resumen_ventas_por_barista(self):
        with transaccion(dictionary=True) as cursor:
            repo = ConsultasRepositorio(cursor)
            filas = repo.ventas_por_barista()
        return [{"id": f["id"], "barista": f["barista"],
                 "tickets": int(f["tickets"]), "total": float(f["total"])} for f in filas]

    def detalle_ventas_barista(self, num_empleado):
        with transaccion(dictionary=True) as cursor:
            repo = ConsultasRepositorio(cursor)
            filas = repo.ventas_de_barista(num_empleado)
        return [{"folio": f["folio"], "fecha": f["fecha"], "cliente": f["cliente"],
                 "metodo": f["metodo"], "total": float(f["total"])} for f in filas]

    def listar_ventas_recientes(self, limite=20):
        with transaccion(dictionary=True) as cursor:
            repo = ConsultasRepositorio(cursor)
            return repo.listar_ventas_recientes(limite)

    def consulta_1_detalle_venta(self, folio_venta):
        with transaccion(dictionary=True) as cursor:
            repo = ConsultasRepositorio(cursor)
            enc = repo.detalle_venta_encabezado(folio_venta)
            lineas = repo.detalle_venta_lineas(folio_venta)
            return enc, lineas

    def consulta_2_detalle_compra(self, folio_compra):
        with transaccion(dictionary=True) as cursor:
            repo = ConsultasRepositorio(cursor)
            enc = repo.detalle_compra_encabezado(folio_compra)
            lineas = repo.detalle_compra_lineas(folio_compra)
            return enc, lineas

    def listar_compras_registradas(self):
        with transaccion(dictionary=True) as cursor:
            repo = ConsultasRepositorio(cursor)
            filas = repo.compras_registradas()
        return [{"folio": f["folio"], "fecha": f["fecha"],
                 "proveedor": f["proveedor"], "empleado": f["empleado"],
                 "total": float(f["total"])} for f in filas]

    def consulta_3_mermas_semana(self):
        with transaccion(dictionary=True) as cursor:
            repo = ConsultasRepositorio(cursor)
            return repo.mermas_ultima_semana()

    def consulta_3_merma_por_folio(self, folio):
        with transaccion(dictionary=True) as cursor:
            repo = ConsultasRepositorio(cursor)
            return repo.merma_por_folio(folio)

    def consulta_4_ventas_por_empleado_fecha(self, num_empleado, fecha_str):
        with transaccion(dictionary=True) as cursor:
            repo = ConsultasRepositorio(cursor)
            filas = repo.ventas_por_empleado_fecha(num_empleado, fecha_str)
        return self._normalizar_ventas_consulta_4(filas)

    def consulta_4_ventas_ultimos_7_dias(self, num_empleado):
        with transaccion(dictionary=True) as cursor:
            repo = ConsultasRepositorio(cursor)
            filas = repo.ventas_barista_ultimos_7_dias(num_empleado)
        return self._normalizar_ventas_consulta_4(filas)

    def consulta_4_ventas_por_mes(self, num_empleado, mes, anio):
        with transaccion(dictionary=True) as cursor:
            repo = ConsultasRepositorio(cursor)
            filas = repo.ventas_barista_por_mes(num_empleado, mes, anio)
        return self._normalizar_ventas_consulta_4(filas)

    def _normalizar_ventas_consulta_4(self, filas):
        return [{
            "fecha": f["fecha"],
            "empleado": f["empleado"],
            "folio": f["folio"],
            "total": float(f["total"]),
            "metodoPago": f["metodoPago"],
        } for f in filas]

    def consulta_5_insumos_receta(self, cod_producto):
        with transaccion(dictionary=True) as cursor:
            repo = ProductoRepositorio(cursor)
            return repo.obtener_receta(cod_producto)