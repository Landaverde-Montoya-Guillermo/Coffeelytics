from repositorios.base_repositorios import BaseRepositorio


class ProveedorRepositorio(BaseRepositorio):

    def listar_todos(self):
        self._cursor.execute("SELECT codigo, nombre, ciudad, telefono FROM proveedor ORDER BY codigo")
        return self._cursor.fetchall()

    def obtener_por_codigo(self, cod_proveedor):
        self._cursor.execute("SELECT codigo, nombre, ciudad, telefono FROM proveedor WHERE codigo = %s", (cod_proveedor,))
        return self._cursor.fetchone()