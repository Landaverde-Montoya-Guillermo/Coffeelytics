IVA_FRONTERA = 0.08   # 8% para ventas en Tijuana y compras a proveedores locales[cite: 6]
IVA_GENERAL  = 0.16   # 16% para compras a proveedores fuera de la franja fronteriza[cite: 6]

ESTATUS_ACTIVO = 1
ESTATUS_NO_DISPONIBLE = 2

UNIDADES_CONTEO_ENTERO = frozenset({
    "BOLS", "BOTE", "CAJA", "GARF", "PAQU",
    "BLS", "BOT", "CJA", "GRF", "PAQ",
    "PZ", "PZA", "PIEZ", "PIEZA", "PIEZAS",
    "SOB", "SOBR", "SOBRE", "SOBRES",
    "PAQUETE", "PAQUETES", "BOTELLA", "BOTELLAS",
    "UND", "UNIDAD", "UNIDADES", "CAJAS",
    "VAS", "VASO", "VASOS", "TAZ", "TAZA", "TAZAS",
})

UNIDADES_CONTINUAS = frozenset({
    "KILO", "KG", "KILOGRAMO", "KILOGRAMOS",
    "GRAM", "GR", "G", "GRAMO", "GRAMOS",
    "LITR", "LT", "L", "LITRO", "LITROS",
    "MILI", "ML", "MILILITRO", "MILILITROS",
    "OZ", "ONZA", "ONZAS",
})

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