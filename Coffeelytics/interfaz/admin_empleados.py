from interfaz.estilos import Color
from consola_ui import tabla_centrada
from consola_ui import (
    limpiar_pantalla, pausar, seleccionar_con_flechas,
    imprimir_encabezado_sesion, imprimir_tabla,
    pedir_correo, pedir_nombre_propio, pedir_rfc,
    pedir_telefono,
    _imprimir_guia, _input_centrado, _ancho, _prefijo, OperacionCancelada
)


def _es_admin_principal(usuario):
    """True solo para la cuenta fundadora num==1."""
    return usuario is not None and usuario.es_admin() and usuario.num == 1


class AdminEmpleados:
    def __init__(self, usuario, empleado_srv):
        self.usuario = usuario
        self.empleado_srv = empleado_srv

    def gestion(self):
        es_principal = _es_admin_principal(self.usuario)
        if es_principal:
            opciones = [
                "Listar todos los empleados",
                "Dar de alta nuevo empleado",
                "Desactivar cuenta de empleado",
                "<< Volver al Menu Admin",
            ]
        else:
            opciones = [
                "Listar todos los empleados",
                "Dar de alta nuevo Barista",
                "<< Volver al Menu Admin",
            ]
        while True:
            enc = imprimir_encabezado_sesion(
                self.usuario,
                breadcrumb=["Inicio", "Panel Admin", "Gestion de Empleados"]
            )
            enc = "\n".join([enc, self._tabla_personal()])
            idx = seleccionar_con_flechas("GESTION DE EMPLEADOS", opciones, enc)
            ultima = len(opciones) - 1
            if idx == ultima:
                return
            if idx == 0:
                self._listar_empleados()
            elif idx == 1:
                if es_principal:
                    self._crear_empleado()
                else:
                    self._crear_empleado(forzar_barista=True)
            elif idx == 2 and es_principal:
                self._desactivar_empleado()

    def _tabla_personal(self):
        """Tabla centrada del personal registrado (para evitar correos e IDs duplicados)."""
        empleados = self.empleado_srv.listar_empleados()
        cols = ["ID", "NOMBRE", "CORREO", "ROL", "ESTATUS"]
        filas = [(e["num"], e["nombre"], e["correo"], e["rol"],
                  "ACTIVO" if e["activo"] else "INACTIVO") for e in empleados]
        return tabla_centrada("PERSONAL REGISTRADO ACTUALMENTE", cols, filas)

    def _listar_empleados(self):
        empleados = self.empleado_srv.listar_empleados()
        cols = ["#", "Nombre", "Correo", "Rol", "Activo"]
        filas = [(e["num"], e["nombre"], e["correo"], e["rol"],
                  "SI" if e["activo"] else "NO") for e in empleados]
        limpiar_pantalla()
        print(imprimir_encabezado_sesion(
            self.usuario,
            breadcrumb=["Inicio", "Panel Admin", "Gestion de Empleados", "Listar"]
        ))
        imprimir_tabla("EMPLEADOS REGISTRADOS", cols, filas)
        pausar()

    def _crear_empleado(self, forzar_barista=False):
        es_principal = _es_admin_principal(self.usuario)
        if not es_principal:
            forzar_barista = True

        limpiar_pantalla()
        print(imprimir_encabezado_sesion(
            self.usuario,
            breadcrumb=["Inicio", "Panel Admin", "Gestion de Empleados", "Alta Empleado"]
        ))
        pfx = _prefijo(_ancho())
        print(f"\n{pfx}  {Color.titulo('ALTA DE NUEVO EMPLEADO')}\n")
        print(self._tabla_personal())
        print(Color.info("Completa los datos del nuevo colaborador."))
        if forzar_barista:
            print(Color.aviso("Como Admin Secundario solo puedes crear cuentas de Barista."))
        print()
        try:
            empleados_existentes = self.empleado_srv.listar_empleados()
        except Exception as error:
            print(Color.error(str(error)))
            pausar()
            return

        try:
            while True:
                try:
                    nombre = pedir_nombre_propio(prompt="Nombre(s)", ejemplo="Maria")
                    break
                except ValueError as error:
                    print(Color.error(str(error)))
                    pausar()

            while True:
                try:
                    apell1 = pedir_nombre_propio(prompt="Primer apellido", ejemplo="Garcia")
                    break
                except ValueError as error:
                    print(Color.error(str(error)))
                    pausar()

            while True:
                try:
                    _imprimir_guia(
                        "Segundo apellido del empleado (opcional)",
                        "Texto libre, maximo 50 caracteres. ENTER para omitir.",
                        "Lopez",
                        "Se ajusta a Formato Titulo."
                    )
                    raw_a2 = _input_centrado("Segundo apellido (ENTER si no aplica)")
                    if raw_a2.strip().upper() in ("0", "CANCELAR"):
                        raise OperacionCancelada()
                    apell2 = raw_a2.strip().title()
                    if len(apell2) > 50:
                        raise ValueError("El segundo apellido no puede superar 50 caracteres.")
                    break
                except ValueError as error:
                    print(Color.error(str(error)))
                    pausar()

            while True:
                try:
                    rfc = pedir_rfc()
                    rfc_repetido = False
                    for empleado in empleados_existentes:
                        if rfc.upper() == str(empleado.get("rfc", "")).upper():
                            rfc_repetido = True
                    if rfc_repetido:
                        raise ValueError(f"El RFC '{rfc}' ya esta registrado.")
                    break
                except ValueError as error:
                    print(Color.error(str(error)))
                    pausar()

            while True:
                try:
                    tel = pedir_telefono()
                    break
                except ValueError as error:
                    print(Color.error(str(error)))
                    pausar()

            while True:
                try:
                    correo = pedir_correo()
                    correo_repetido = False
                    for empleado in empleados_existentes:
                        if correo.lower() == str(empleado.get("correo", "")).lower():
                            correo_repetido = True
                    if correo_repetido:
                        raise ValueError(f"El correo '{correo}' ya esta registrado.")
                    break
                except ValueError as error:
                    print(Color.error(str(error)))
                    pausar()

            while True:
                try:
                    _imprimir_guia(
                        "Contrasena inicial de acceso",
                        "Minimo 4 caracteres, sin espacios",
                        "cof2024",
                        "El empleado podra usarla de inmediato al iniciar sesion."
                    )
                    raw_contra = _input_centrado("Contrasena inicial (minimo 4 chars)")
                    if raw_contra.strip().upper() in ("0", "CANCELAR"):
                        raise OperacionCancelada()
                    contra = raw_contra.strip()
                    if len(contra) < 4 or " " in contra:
                        raise ValueError(
                            "Contrasena invalida. Debe tener al menos 4 caracteres y no incluir espacios.")
                    break
                except ValueError as error:
                    print(Color.error(str(error)))
                    pausar()

            if forzar_barista:
                rol = "BARI"
                print(Color.info("Rol asignado automaticamente: Barista."))
            else:
                enc = imprimir_encabezado_sesion(
                    self.usuario,
                    breadcrumb=["Inicio", "Panel Admin", "Gestion de Empleados", "Alta", "Rol"]
                )
                opts = ["Barista", "Administrador Secundario", "<< Cancelar"]
                idx = seleccionar_con_flechas("Rol del nuevo empleado", opts, enc)
                if idx == 2:
                    return
                rol = "BARI" if idx == 0 else "ADMN"
        except OperacionCancelada:
            print(Color.aviso("Operacion cancelada. No se creo el empleado."))
            pausar()
            return

        while True:
            try:
                ok, msg = self.empleado_srv.crear_empleado(
                    nombre, apell1, apell2, rfc, tel, correo, contra, rol
                )
            except Exception as error:
                print(Color.error(str(error)))
                pausar()
                return
            if ok:
                print(Color.ok(msg))
                pausar()
                return

            print(Color.error(msg))
            pausar()
            texto = msg.lower()
            if "duplicate" in texto or "duplicad" in texto:
                try:
                    empleados_existentes = self.empleado_srv.listar_empleados()
                except Exception as error:
                    print(Color.error(str(error)))
                    pausar()
                    return
                try:
                    if "correo" in texto:
                        while True:
                            try:
                                correo = pedir_correo()
                                correo_repetido = False
                                for empleado in empleados_existentes:
                                    if correo.lower() == str(empleado.get("correo", "")).lower():
                                        correo_repetido = True
                                if correo_repetido:
                                    raise ValueError(f"El correo '{correo}' ya esta registrado.")
                                break
                            except ValueError as error:
                                print(Color.error(str(error)))
                                pausar()
                    elif "rfc" in texto:
                        while True:
                            try:
                                rfc = pedir_rfc()
                                rfc_repetido = False
                                for empleado in empleados_existentes:
                                    if rfc.upper() == str(empleado.get("rfc", "")).upper():
                                        rfc_repetido = True
                                if rfc_repetido:
                                    raise ValueError(f"El RFC '{rfc}' ya esta registrado.")
                                break
                            except ValueError as error:
                                print(Color.error(str(error)))
                                pausar()
                    else:
                        return
                except OperacionCancelada:
                    print(Color.aviso("Operacion cancelada. No se creo el empleado."))
                    pausar()
                    return
                continue
            return

    def _desactivar_empleado(self):
        while True:
            limpiar_pantalla()
            try:
                empleados = self.empleado_srv.listar_empleados()
                candidatos = [e for e in empleados
                              if e["activo"] and e["num"] != 1 and e["num"] != self.usuario.num]
                if not candidatos:
                    print(Color.aviso("No hay cuentas desactivables disponibles."))
                    print(Color.info("Nota: La cuenta Admin Principal (num=1) no puede desactivarse."))
                    pausar()
                    return
                enc = imprimir_encabezado_sesion(
                    self.usuario,
                    breadcrumb=["Inicio", "Panel Admin", "Gestion de Empleados", "Desactivar"]
                )
                opts = [f"{e['num']:>4}  {e['nombre']:<30} {e['rol']}  {'Activo' if e['activo'] else 'Inactivo'}"
                        for e in candidatos] + ["<< Cancelar y regresar"]
                idx = seleccionar_con_flechas("Selecciona cuenta a desactivar", opts, enc)
                if idx == len(candidatos):
                    return
                emp = candidatos[idx]
                enc2 = imprimir_encabezado_sesion(
                    self.usuario,
                    breadcrumb=["Inicio", "Panel Admin", "Gestion de Empleados", "Confirmar desactivacion"]
                )
                opts2 = [
                    f"Confirmar - desactivar a {emp['nombre']}",
                    f"<< Cancelar - no desactivar a {emp['nombre']}"
                ]
                idx2 = seleccionar_con_flechas("Confirmar desactivacion", opts2, enc2)
                if idx2 != 0:
                    return
                ok = self.empleado_srv.desactivar_cuenta(emp["num"])
                if not ok:
                    raise ValueError("No se pudo desactivar la cuenta.")
                print(Color.ok(f"Cuenta de {emp['nombre']} desactivada."))
                pausar()
                return
            except Exception as error:
                print(Color.error(str(error)))
                pausar()
