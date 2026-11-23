from repositorios.base_repositorios import BaseRepositorio


class MermaRepositorio(BaseRepositorio):

    def listar_tipos(self):
        self._cursor.execute("SELECT codigo, nombre FROM tipo_merma ORDER BY codigo")
        return self._cursor.fetchall()

    def insertar(self, motivo, cantidad, tipo_merma, cod_insumo, id_empleado):
        self._cursor.execute(
            "INSERT INTO merma (motivo, fecha, cantidad, tipo, insumo, idEmpleado) "
            "VALUES (%s, CURDATE(), %s, %s, %s, %s)",
            (motivo, cantidad, tipo_merma, cod_insumo, id_empleado)
        )
        return self._cursor.lastrowid