from repositorios.base_repositorios import BaseRepositorio
from entidades.empleado import Empleado


class EmpleadoRepositorio(BaseRepositorio):

    def obtener_por_correo_y_hash(self, correo, hash_contrasena):
        self._cursor.execute("""
            SELECT e.num, e.nombrePila, e.primApell, e.segApell, e.RFC,
                   e.telefono, e.correo, e.activo, e.rol AS rol_codigo,
                   r.nombre AS rol_nombre
            FROM empleado e
            INNER JOIN rol r ON e.rol = r.codigo
            WHERE e.correo = %s AND e.contrasena = %s AND e.activo = 1
        """, (correo, hash_contrasena))
        fila = self._cursor.fetchone()
        if not fila:
            return None
        return Empleado(
            num=fila["num"],
            nombre_pila=fila["nombrePila"],
            prim_apell=fila["primApell"],
            seg_apell=fila.get("segApell", ""),
            rfc=fila.get("RFC", ""),
            telefono=fila.get("telefono", ""),
            correo=fila["correo"],
            rol_codigo=fila["rol_codigo"],
            rol_nombre=fila["rol_nombre"],
            activo=fila["activo"]
        )

    def crear(self, empleado):
        self._cursor.execute("""
            INSERT INTO empleado
            (nombrePila, primApell, segApell, RFC, telefono, correo, contrasena, activo, rol)
            VALUES (%s, %s, %s, %s, %s, %s, %s, 1, %s)
        """, (
            empleado.nombre_pila, empleado.prim_apell, empleado.seg_apell,
            empleado.rfc, empleado.telefono, empleado.correo,
            empleado.contrasena, empleado.rol_codigo
        ))
        return self._cursor.lastrowid

    def desactivar(self, num_empleado):
        self._cursor.execute("UPDATE empleado SET activo = 0 WHERE num = %s", (num_empleado,))
        return self._cursor.rowcount > 0

    def listar_todos(self):
        self._cursor.execute("""
            SELECT e.num, CONCAT(e.nombrePila, ' ', e.primApell) AS nombre,
                   e.RFC AS rfc, e.correo, r.nombre AS rol, e.activo
            FROM empleado e
            INNER JOIN rol r ON e.rol = r.codigo
            ORDER BY e.num
        """)
        return self._cursor.fetchall()