from repositorios.base_repositorios import BaseRepositorio


class ConsumibleMesaRepositorio(BaseRepositorio):

    def agregar_a_mesa(self, cod_insumo, mesa_cod, cantidad):
        self._cursor.execute("""
            INSERT INTO con_insum (insumo, mesa, cantidad) VALUES (%s, %s, %s)
            ON DUPLICATE KEY UPDATE cantidad = cantidad + VALUES(cantidad)
        """, (cod_insumo, mesa_cod, cantidad))