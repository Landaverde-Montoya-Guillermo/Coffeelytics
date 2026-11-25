from repositorios.base_repositorios import BaseRepositorio


class CatalogosRepositorio(BaseRepositorio):

    def listar_unidades_medida(self):
        self._cursor.execute(
            "SELECT codigo, abreviatura FROM unidad_medida ORDER BY codigo"
        )
        return self._cursor.fetchall()

    def listar_categorias_insumo(self):
        self._cursor.execute(
            "SELECT codigo, nombre FROM categoria_insumo ORDER BY codigo"
        )
        return self._cursor.fetchall()