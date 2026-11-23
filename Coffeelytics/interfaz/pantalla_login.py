from interfaz.estilos import Color
from consola_ui import (
    limpiar_pantalla, pausar, imprimir_encabezado_sesion,
    pedir_contrasena, pedir_correo, imprimir_caja_credenciales,
    imprimir_banner, _ancho, _prefijo, OperacionCancelada
)


class PantallaLogin:
    def __init__(self, auth_servicio):
        self.auth_servicio = auth_servicio

    def mostrar(self):
        intentos = 0
        mensaje = ""
        while True:
            limpiar_pantalla()
            imprimir_banner()
            imprimir_caja_credenciales()
            print()
            enc = imprimir_encabezado_sesion(None, breadcrumb=["Inicio", "Inicio de Sesion"])
            print(enc)
            if mensaje:
                pfx = _prefijo(_ancho())
                print(f"\n{pfx}  {mensaje}\n")

            try:
                correo = pedir_correo(aceptar_salir=True)
                contra = pedir_contrasena("Contrasena (0/CANCELAR para volver): ")
                empleado = self.auth_servicio.iniciar_sesion(correo, contra)
            except OperacionCancelada:
                print(Color.aviso("Operacion cancelada."))
                pausar()
                return None
            except Exception as error:
                print(Color.error(str(error)))
                pausar()
                continue

            if empleado:
                return empleado

            intentos += 1
            mensaje = Color.error(f"Credenciales incorrectas o cuenta inactiva. Intento {intentos}/3.")
            if intentos >= 3:
                limpiar_pantalla()
                print(Color.error("Demasiados intentos fallidos. El sistema se cerrara."))
                pausar()
                return None