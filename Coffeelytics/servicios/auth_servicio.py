from config.database import transaccion
from repositorios.empleado_repositorio import EmpleadoRepositorio


class AuthServicio:

    @staticmethod
    def hashear_contrasena(texto_plano):
        return str(texto_plano or "").strip()

    def iniciar_sesion(self, correo, contrasena):
        correo_limpio = str(correo or "").strip().lower()
        pwd_limpia = self.hashear_contrasena(contrasena)
        with transaccion(dictionary=True) as cursor:
            repo = EmpleadoRepositorio(cursor)
            return repo.obtener_por_correo_y_hash(correo_limpio, pwd_limpia)