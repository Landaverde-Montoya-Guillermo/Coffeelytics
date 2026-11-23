IVA_FRONTERA = 0.08   # 8% para ventas en Tijuana y compras a proveedores locales[cite: 6]
IVA_GENERAL  = 0.16   # 16% para compras a proveedores fuera de la franja fronteriza[cite: 6]

ESTATUS_ACTIVO = 1
ESTATUS_NO_DISPONIBLE = 2

UNIDADES_CONTEO_ENTERO = frozenset({"BOLS", "BOTE", "CAJA", "GARF", "PAQU"})

CIUDADES_FRONTERA = [
    "tijuana",
    "mexicali",
    "ensenada",
    "tecate",
    "rosarito",
    "playas de rosarito",
    "ciudad juarez",
    "nuevo laredo",
    "reynosa",
    "matamoros"
]