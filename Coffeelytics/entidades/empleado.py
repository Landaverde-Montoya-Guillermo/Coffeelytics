from entidades.base import EntidadBase, ValidacionError


class Empleado(EntidadBase):
    def __init__(self, num, nombre_pila, prim_apell, correo, rol_codigo,
                 rol_nombre="", seg_apell="", rfc="", telefono="",
                 contrasena="", activo=1):
        self.num = int(num) if num is not None else None
        self.nombre_pila = self.validar_texto(nombre_pila, "nombre", 50)
        self.prim_apell = self.validar_texto(prim_apell, "primer apellido", 50)
        self.seg_apell = self.validar_texto(seg_apell, "segundo apellido", 50, obligatorio=False)
        self.correo = self.validar_texto(correo, "correo", 100).lower()
        self.rol_codigo = self.validar_texto(rol_codigo, "rol", 4).upper()
        self.rol_nombre = rol_nombre
        self.rfc = rfc.upper() if rfc else ""
        self.telefono = telefono
        self.contrasena = contrasena
        self.activo = int(activo)

        if self.rfc and len(self.rfc) not in (12, 13):
            raise ValidacionError("El RFC debe tener 12 o 13 caracteres.")

    @property
    def nombre_completo(self):
        return f"{self.nombre_pila} {self.prim_apell}".strip()

    def es_admin(self):
        return self.rol_codigo == "ADMN"

    def es_admin_principal(self):
        return self.es_admin() and self.num == 1