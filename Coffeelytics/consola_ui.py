"""
Motor de interfaz de consola de Coffeelytics.

Usa unicamente la libreria estandar de Python (sin textual, rich ni curses).
Todos los bloques (banner, cajas, menus, tablas y formularios) se centran
horizontalmente con el ancho real de la terminal y los textos largos se
envuelven con textwrap para no romper los bordes.
"""
import os
import re
import sys
import shutil
import getpass
import datetime
import math
import textwrap

from mysql.connector import Error as ErrorBaseDatos

from interfaz.estilos import Color
from config.negocio import INFO_CAFETERIA, LINEAS_BANNER_GRANDE


# ── EXCEPCION DE CANCELACION ─────────────────────────────────────────────────

class OperacionCancelada(Exception):
    """Se lanza cuando el usuario escribe 0 o CANCELAR en cualquier campo."""
    pass


# ── ANCHO Y CENTRADO ─────────────────────────────────────────────────────────

ANCHO_MAXIMO_UI = 132
_RE_ANSI = re.compile(r"\x1b\[[0-9;]*[A-Za-z]")


def _columnas():
    """Columnas reales de la terminal (con respaldo de 80 si no se detectan)."""
    return shutil.get_terminal_size(fallback=(80, 24)).columns


def _filas():
    """Filas reales de la terminal (con respaldo de 24 si no se detectan)."""
    return shutil.get_terminal_size(fallback=(80, 24)).lines


def _ancho():
    """Ancho util de los bloques de la UI, acotado a ANCHO_MAXIMO_UI."""
    return min(_columnas(), ANCHO_MAXIMO_UI)


def _margen(ancho_caja):
    """Margen izquierdo para centrar horizontalmente una caja de ancho dado."""
    return max(0, (_columnas() - ancho_caja) // 2)


def _prefijo(ancho_caja):
    """Cadena de espacios que centra una caja de ancho_caja columnas."""
    return " " * _margen(ancho_caja)


def _visible(texto):
    """Quita los codigos ANSI para medir el texto tal como se ve en pantalla."""
    return _RE_ANSI.sub("", str(texto))


def _largo_visible(texto):
    return len(_visible(texto))


def _centrar_texto(texto):
    """Antepone el margen que centra una linea (puede llevar codigos ANSI)."""
    return " " * max(0, (_columnas() - _largo_visible(texto)) // 2) + texto


def _partir(texto, ancho):
    """
    Parte un texto en lineas de como maximo `ancho` columnas visibles.
    Si ya cabe (o trae ANSI, que no se puede partir sin romper colores), lo devuelve tal cual.
    """
    if _largo_visible(texto) <= ancho or "\x1b" in texto:
        return [texto]
    return textwrap.wrap(texto, width=ancho, break_long_words=True,
                         break_on_hyphens=False) or [texto]


# ── SOPORTE DE TERMINAL (WINDOWS / LINUX / MAC) ──────────────────────────────

def habilitar_ansi_windows():
    """
    Prepara la consola: activa secuencias ANSI y UTF-8 en Windows para que
    los bordes Unicode se vean bien, y fuerza UTF-8 en los flujos de salida.
    """
    if sys.platform == "win32":
        os.system("")                   # activa VT100/ANSI en cmd y PowerShell
        os.system("chcp 65001 > nul")   # codificacion UTF-8 para bordes Unicode
    for flujo in (sys.stdout, sys.stderr):
        try:
            if (flujo.encoding or "").lower().replace("-", "") != "utf8":
                flujo.reconfigure(encoding="utf-8", errors="replace")
        except (AttributeError, ValueError):
            pass


# ── PANTALLA ─────────────────────────────────────────────────────────────────

def limpiar_pantalla():
    """Limpia la terminal. En Windows usa cls; en Linux/macOS, secuencias ANSI."""
    if sys.platform == "win32":
        os.system("cls")
    elif sys.stdout.isatty():
        print("\033[H\033[2J\033[3J", end="", flush=True)


def pausar(mensaje="Presiona ENTER para continuar..."):
    print(f"\n{_centrar_texto(Color.GRIS + mensaje + Color.RESET)}")
    try:
        input()
    except KeyboardInterrupt:
        pass
    # EOFError (entrada cerrada) se deja propagar para que ningun bucle de error se repita sin fin.


# ── LECTURA DE TECLAS (MULTIPLATAFORMA) ──────────────────────────────────────

def _es_tty():
    return sys.stdin.isatty()


def _leer_byte_unix(fd, espera=None):
    """
    Lee un byte del descriptor de archivo directamente (os.read).
    Se usa os.read y no sys.stdin.read porque el buffer de Python oculta bytes
    ya recibidos y select() no los vería; con os.read el sondeo es exacto.
    `espera` (segundos) limita cuanto se espera el byte; None espera sin limite.
    """
    import select
    if espera is not None:
        listos, _, _ = select.select([fd], [], [], espera)
        if not listos:
            return ""
    dato = os.read(fd, 1)
    return dato.decode("utf-8", errors="replace") if dato else ""


def leer_tecla():
    """
    Lee una tecla sin ENTER. Devuelve:
      'ARRIBA', 'ABAJO', 'IZQUIERDA', 'DERECHA', 'ENTER', 'ESC' o el caracter leido.
    Ctrl+C se re-lanza como KeyboardInterrupt (en modo raw no genera la senal).
    """
    if not _es_tty():
        return "ENTER"

    if sys.platform == "win32":
        import msvcrt
        ch = msvcrt.getch()
        if ch in (b'\xe0', b'\x00'):
            ch2 = msvcrt.getch()
            return {b'H': "ARRIBA", b'P': "ABAJO", b'K': "IZQUIERDA", b'M': "DERECHA"}.get(ch2, "")
        if ch in (b'\r', b'\n'):
            return "ENTER"
        if ch == b'\x1b':
            return "ESC"
        if ch == b'\x03':
            raise KeyboardInterrupt
        decoded = ch.decode("utf-8", errors="replace")
        if decoded in ("w", "W"):
            return "ARRIBA"
        if decoded in ("s", "S"):
            return "ABAJO"
        return decoded

    import termios
    import tty
    fd = sys.stdin.fileno()
    antiguo = termios.tcgetattr(fd)
    try:
        tty.setraw(fd)
        ch = _leer_byte_unix(fd)
        if ch == "\x03":
            raise KeyboardInterrupt
        if ch == "\x1b":
            # Si no llega nada en 50 ms es ESC real; si llega '[' u 'O' es una flecha.
            sig = _leer_byte_unix(fd, 0.05)
            if sig == "":
                return "ESC"
            if sig in ("[", "O"):
                final = ""
                for _ in range(8):
                    c = _leer_byte_unix(fd, 0.05)
                    if c == "":
                        break
                    if c.isalpha() or c == "~":
                        final = c
                        break
                return {"A": "ARRIBA", "B": "ABAJO", "C": "DERECHA", "D": "IZQUIERDA"}.get(final, "")
            return ""
        if ch in ("\r", "\n"):
            return "ENTER"
        if ch in ("w", "W"):
            return "ARRIBA"
        if ch in ("s", "S"):
            return "ABAJO"
        return ch
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, antiguo)


# ── SELECTOR INTERACTIVO CON FLECHAS ─────────────────────────────────────────

def seleccionar_con_flechas(titulo, opciones, encabezado_extra=""):
    """
    Menu vertical navegable con flechas ARRIBA/ABAJO y ENTER.
    `encabezado_extra` se dibuja SIEMPRE arriba del menu (por ejemplo, la tabla
    del carrito), de modo que el contexto queda visible mientras se elige.
    ESC selecciona la ultima opcion (normalmente "Volver" o "Cancelar").
    """
    if not opciones:
        return 0

    ancho = _ancho()
    pfx = _prefijo(ancho)
    sep = pfx + Color.DIM + "─" * ancho + Color.RESET
    total = len(opciones)
    ultima_es_volver = any(kw in opciones[-1].lower()
                           for kw in ["volver", "cancelar", "salir", "<<"])
    ancho_txt = max(20, ancho - 12)
    filas = max(10, _filas())

    def _lineas_encabezado():
        if not encabezado_extra:
            return []
        presupuesto = max(3, filas - 16)
        lineas = str(encabezado_extra).splitlines()
        if len(lineas) > presupuesto:
            return lineas[-presupuesto:]
        return lineas

    def _titulo_linea():
        titulo_fmt = f" {titulo} "
        pad = max(0, (ancho - len(titulo_fmt)) // 2)
        return f"{pfx}{' ' * pad}{Color.BOLD}{Color.CARAMELO}{titulo_fmt}{Color.RESET}"

    if not _es_tty():
        limpiar_pantalla()
        if encabezado_extra:
            print(encabezado_extra)
        print(sep)
        print(_titulo_linea())
        print(sep)
        for i, op in enumerate(opciones, 1):
            print(f"{pfx}  {Color.CARAMELO}{i:2}.{Color.RESET} {op}")
        print()
        while True:
            try:
                raw = input(f"{pfx}{Color.CIAN}  Numero de opcion: {Color.RESET}").strip()
            except EOFError:
                raise  # entrada cerrada: no repetir el aviso en bucle
            try:
                n = int(raw)
                if 1 <= n <= total:
                    return n - 1
            except ValueError:
                pass
            print(_centrar_texto(Color.error("Numero invalido.")))

    sel = 0
    while True:
        limpiar_pantalla()
        lineas_encabezado = _lineas_encabezado()
        if lineas_encabezado:
            print("\n".join(lineas_encabezado))
        print(sep)
        print(_titulo_linea())
        print(sep)

        presupuesto_lineas = max(4, filas - len(lineas_encabezado) - 10)
        cantidad_visible = 0
        lineas_consumidas = 0
        for op in opciones:
            lineas_opcion = max(1, len(_partir(op, ancho_txt)))
            lineas_con_separador = lineas_opcion + 1
            if lineas_consumidas + lineas_con_separador > presupuesto_lineas:
                break
            lineas_consumidas += lineas_con_separador
            cantidad_visible += 1
        cantidad_visible = min(total, max(1, cantidad_visible))
        if total <= cantidad_visible:
            inicio = 0
            fin = total
        else:
            inicio = max(0, min(sel - cantidad_visible // 2, total - cantidad_visible))
            fin = inicio + cantidad_visible

        if inicio > 0:
            print(f"{pfx}  {Color.DIM}... {inicio} opcion(es) anteriores ...{Color.RESET}")

        for i in range(inicio, fin):
            op = opciones[i]
            es_volver = ultima_es_volver and i == total - 1
            trozos = _partir(op, ancho_txt)
            for j, trozo in enumerate(trozos):
                if i == sel:
                    marca = (" [<<] " if es_volver else " [>>] ") if j == 0 else "      "
                    cuerpo = _visible(f"{marca}{trozo}")
                    relleno = max(0, ancho - 4 - len(cuerpo))
                    fondo = Color.BG_OSCURO if es_volver else Color.BG_CAFE
                    tinta = Color.AMARILLO if es_volver else Color.CREMA
                    print(f"{pfx}  {fondo}{tinta}{Color.BOLD}{cuerpo}{' ' * relleno}{Color.RESET}")
                else:
                    marca = ("  [<<] " if es_volver else "  [  ] ") if j == 0 else "       "
                    color = Color.AMARILLO if es_volver else Color.CREMA
                    print(f"{pfx}  {color}{marca}{trozo}{Color.RESET}")
            if i < total - 1:
                print(f"{pfx}  {Color.DIM}{'─' * (ancho - 4)}{Color.RESET}")

        if fin < total:
            print(f"{pfx}  {Color.DIM}... {total - fin} opcion(es) siguientes ...{Color.RESET}")

        print()
        print(_centrar_texto(
            f"{Color.DIM}[^] Arriba   [v] Abajo   [ENTER] Seleccionar   [ESC] Volver{Color.RESET}"
        ))

        tecla = leer_tecla()
        if tecla == "ARRIBA":
            sel = (sel - 1) % total
        elif tecla == "ABAJO":
            sel = (sel + 1) % total
        elif tecla == "ENTER":
            return sel
        elif tecla == "ESC":
            return total - 1


# ── BREADCRUMB Y ENCABEZADO DE SESION ────────────────────────────────────────

def _agrupar_en_lineas(partes, separador="  "):
    """Une partes visibles en lineas que no excedan el ancho de la terminal."""
    limite = max(20, _columnas() - 2)
    lineas, actual = [], ""
    for parte in partes:
        candidato = parte if not actual else f"{actual}{separador}{parte}"
        if _largo_visible(candidato) <= limite or not actual:
            actual = candidato
        else:
            lineas.append(actual)
            actual = parte
    if actual:
        lineas.append(actual)
    return lineas


def imprimir_breadcrumb(ruta):
    ancho = _ancho()
    pfx = _prefijo(ancho)
    sep = pfx + Color.DIM + "─" * ancho + Color.RESET
    texto = "Ubicacion: " + " > ".join(ruta)
    print(sep)
    for linea in textwrap.wrap(texto, width=max(20, ancho - 4)) or [texto]:
        print(_centrar_texto(f"{Color.DIM}{linea}{Color.RESET}"))
    print(sep)


def imprimir_encabezado_sesion(empleado, breadcrumb=None):
    ancho = _ancho()
    pfx = _prefijo(ancho)
    ahora = datetime.datetime.now().strftime("%d/%m/%Y %H:%M")
    if empleado is None:
        nom = "---"
        etiqueta_rol = "---"
    else:
        nom = empleado.nombre_completo
        if empleado.es_admin():
            if empleado.num == 1:
                etiqueta_rol = f"{Color.CARAMELO}[ADMIN PRINCIPAL]{Color.RESET}"
            else:
                etiqueta_rol = f"{Color.AMARILLO}[ADMIN SECUNDARIO]{Color.RESET}"
        else:
            etiqueta_rol = f"{Color.VERDE_OK}[{empleado.rol_nombre}]{Color.RESET}"

    marca = f"{Color.BG_CAFE}{Color.CREMA}{Color.BOLD} COFFEELYTICS {Color.RESET}"
    partes = [marca, f"{Color.CARAMELO}{nom}{Color.RESET}", etiqueta_rol,
              f"{Color.DIM}{ahora}{Color.RESET}"]
    salida = [_centrar_texto(linea) for linea in _agrupar_en_lineas(partes)]

    if breadcrumb:
        sep = pfx + Color.DIM + "─" * ancho + Color.RESET
        texto_bc = "Ubicacion: " + " > ".join(breadcrumb)
        bc = [_centrar_texto(f"{Color.DIM}{l}{Color.RESET}")
              for l in (textwrap.wrap(texto_bc, width=max(20, ancho - 4)) or [texto_bc])]
        return "\n".join(salida + [sep] + bc + [sep])
    return "\n".join(salida)


# ── EJECUCION SEGURA DE ACCIONES DE MENU ─────────────────────────────────────

def ejecutar_accion(accion, *args, **kwargs):
    """
    Ejecuta una accion de un menu. Si falla, muestra el motivo, espera ENTER
    y devuelve None, de modo que el panel sigue abierto en lugar de cerrarse.
    EOFError y KeyboardInterrupt se re-lanzan: son fin de entrada, no errores.
    """
    try:
        return accion(*args, **kwargs)
    except (EOFError, KeyboardInterrupt):
        raise
    except OperacionCancelada:
        print(_centrar_texto(Color.aviso("Operacion cancelada.")))
    except ErrorBaseDatos as error:
        print(_centrar_texto(Color.error(f"Error de base de datos: {error}")))
    except Exception as error:
        print(_centrar_texto(Color.error(f"Error inesperado: {error}")))
    pausar()
    return None


# ── BLOQUES DE TEXTO CENTRADOS (tickets y comprobantes) ──────────────────────

ESTILOS_BLOQUE = {
    "marco":   Color.CARAMELO,
    "titulo":  Color.BOLD + Color.CARAMELO,
    "negrita": Color.BOLD,
    "total":   Color.BOLD + Color.VERDE_OK,
    "dim":     Color.DIM,
    "aviso":   Color.AMARILLO,
    "error":   Color.ROJO_ALT,
}


def formatear_bloque_centrado(lineas):
    """
    Devuelve un bloque [(texto, estilo)] como cadena centrada horizontalmente.
    El margen sale del ancho visible del bloque (sin ANSI), asi todas las lineas
    comparten la misma sangria y los bordes quedan alineados.
    """
    ancho = max((_largo_visible(texto) for texto, _ in lineas), default=0)
    margen = " " * max(0, (_columnas() - ancho) // 2)
    salida = []
    for texto, estilo in lineas:
        color = ESTILOS_BLOQUE.get(estilo, "")
        salida.append(margen + (color + texto + Color.RESET if color else texto))
    return "\n".join(salida)


def imprimir_bloque_centrado(lineas):
    print(formatear_bloque_centrado(lineas))


# ── BANNER DE INICIO ─────────────────────────────────────────────────────────

def _ancho_banner_grande():
    return max(_largo_visible(linea) for linea in LINEAS_BANNER_GRANDE)


def _imprimir_banner_compacto():
    """Encabezado de doble borde para terminales mas angostas que el banner grande."""
    cols = _columnas()
    interior = max(16, min(cols - 6, 56))
    pfx = " " * max(0, (cols - (interior + 2)) // 2)
    filas = [(textwrap.wrap("C O F F E E L Y T I C S", interior - 2) or [""], Color.BOLD + Color.CARAMELO),
             (textwrap.wrap(INFO_CAFETERIA["eslogan"], interior - 2) or [""], Color.CREMA)]
    print()
    print(pfx + Color.CARAMELO + "╔" + "═" * interior + "╗" + Color.RESET)
    for lineas, estilo in filas:
        for linea in lineas:
            print(pfx + Color.CARAMELO + "║" + Color.RESET + estilo
                  + linea.center(interior) + Color.RESET + Color.CARAMELO + "║" + Color.RESET)
    print(pfx + Color.CARAMELO + "╚" + "═" * interior + "╝" + Color.RESET)
    print()


def imprimir_banner():
    """Banner grande centrado; si la terminal es angosta, usa el encabezado compacto."""
    ancho_banner = _ancho_banner_grande()
    cols = _columnas()
    if cols < ancho_banner + 2:
        _imprimir_banner_compacto()
        return
    pfx = " " * max(0, (cols - ancho_banner) // 2)
    print()
    for linea in LINEAS_BANNER_GRANDE:
        print(pfx + linea)
    print()


# ── CAJA DE CREDENCIALES DE PRUEBA ───────────────────────────────────────────

def imprimir_caja_credenciales():
    contenido = [
        ("titulo", "Cuentas de acceso para pruebas"),
        ("sep", ""),
        ("item", "Admin Principal (Acceso Total):  admin@coffeelytics.com  /  admin123"),
        ("item", "Barista (Operacion POS):         barista@coffeelytics.com  /  barista123"),
        ("sep", ""),
        ("nota", "[!] Los nuevos administradores creados tendran rol de Administrador "
                 "Secundario (privilegios operativos limitados)."),
    ]
    interior = max(12, min(_columnas() - 4, _ancho() - 6, 76))  # ancho entre bordes
    util = interior - 2                          # ancho util con un espacio a cada lado
    pfx = " " * max(0, (_columnas() - (interior + 2)) // 2)
    vbar = Color.CARAMELO + "│" + Color.RESET

    print(pfx + Color.CARAMELO + "┌" + "─" * interior + "┐" + Color.RESET)
    for tipo, texto in contenido:
        if tipo == "sep":
            print(pfx + Color.CARAMELO + "├" + "─" * interior + "┤" + Color.RESET)
            continue
        if tipo == "titulo":
            for trozo in textwrap.wrap(texto, interior) or [""]:
                linea = Color.BOLD + Color.CARAMELO + trozo.center(interior) + Color.RESET
                print(pfx + vbar + linea + vbar)
            continue
        color = Color.CREMA if tipo == "item" else Color.AMARILLO
        for trozo in textwrap.wrap(texto, util) or [""]:
            print(pfx + vbar + color + f" {trozo:<{util}} " + Color.RESET + vbar)
    print(pfx + Color.CARAMELO + "└" + "─" * interior + "┘" + Color.RESET)


# ── TABLA UNICODE CON CUADRICULA Y AJUSTE DE TEXTO ───────────────────────────

def _tabla_vertical(titulo, columnas, filas, limite, cols_term):
    """
    Respaldo para terminales muy angostas: cada fila se muestra como una ficha
    de pares etiqueta: valor. Las etiquetas y valores se envuelven; nada se recorta.
    """
    etiq_w = min(max(len(_visible(c)) for c in columnas) + 1, max(8, limite // 3))
    util = max(8, limite - etiq_w - 1)
    sep = "─" * max(10, min(limite, 60))
    lineas = [Color.titulo(titulo), sep]
    if not filas:
        lineas.append("(Sin registros)")
    for idx, fila in enumerate(filas):
        if idx:
            lineas.append(sep)
        for col, celda in zip(columnas, fila):
            etiquetas = textwrap.wrap(f"{col}:", etiq_w) or [""]
            valores = textwrap.wrap(_visible(celda), util) or [""]
            alto = max(len(etiquetas), len(valores))
            for r in range(alto):
                et = etiquetas[r] if r < len(etiquetas) else ""
                va = valores[r] if r < len(valores) else ""
                lineas.append(f"{et:<{etiq_w}} {Color.CREMA}{va}{Color.RESET}")
    ancho_bloque = max(_largo_visible(l) for l in lineas)
    margen = " " * max(0, (cols_term - ancho_bloque) // 2)
    return "\n".join(margen + l for l in lineas)


def imprimir_tabla(titulo, columnas, filas, ancho_min=12, retornar_texto=False):
    """
    Dibuja una tabla con cuadricula Unicode centrada en la terminal.
    - Las columnas se reducen (la mas ancha primero) para caber en cols - 4.
    - Las celdas que no caben se parten en varias lineas: nada se recorta.
    """
    columnas = [str(c) for c in columnas]
    n = len(columnas)

    if filas and isinstance(filas[0], dict):
        filas = [[str(f.get(c, "")) for c in columnas] for f in filas]
    else:
        filas = [[str(c2) for c2 in fila][:n] + [""] * (n - len(fila)) for fila in filas]

    anchos = [max(len(_visible(columnas[i])),
                  *(len(_visible(f[i])) for f in filas), 4)
              for i in range(n)]

    cols_term = _columnas()
    limite = min(cols_term, ANCHO_MAXIMO_UI) - 4
    piso_preferido = max(4, min(ancho_min, 12))

    def ancho_total(a):
        # 2 espacios de sangria + bordes + 4 por celda + separadores
        return sum(a) + 5 * n + 3

    # Palabra mas larga de cada columna: una cifra o un codigo no debe partirse.
    naturales = list(anchos)
    tokens = [max([4] + [len(p) for p in _visible(columnas[i]).split()]
                  + [len(p) for f in filas for p in _visible(f[i]).split()])
              for i in range(n)]

    # Reducir la columna mas ancha sin bajar de su palabra mas larga (una cifra o
    # un codigo nunca se parte). Si aun asi no cabe, imprimir_tabla usa la vista de fichas.
    pisos = [max(piso_preferido, min(tokens[i], naturales[i])) for i in range(n)]
    while ancho_total(anchos) > limite:
        candidatas = [i for i in range(n) if anchos[i] > pisos[i]]
        if not candidatas:
            break
        idx = max(candidatas, key=lambda i: anchos[i])
        anchos[idx] -= 1

    if ancho_total(anchos) > limite:
        # Terminal demasiado estrecha para una cuadricula: se usa vista de fichas.
        texto = _tabla_vertical(titulo, columnas, filas, limite, cols_term)
        if retornar_texto:
            return texto
        print(texto)
        return

    total = ancho_total(anchos)
    margen = " " * max(0, (cols_term - total) // 2)

    def render_fila(celdas, color):
        partes = []
        for i, celda in enumerate(celdas):
            vis = _visible(celda)
            if len(vis) <= anchos[i]:
                partes.append([celda])
            else:
                partes.append(textwrap.wrap(vis, width=anchos[i], break_long_words=True,
                                            break_on_hyphens=False) or [""])
        alto = max(len(p) for p in partes)
        salida = []
        for r in range(alto):
            segs = []
            for i, p in enumerate(partes):
                txt = p[r] if r < len(p) else ""
                relleno = anchos[i] - len(_visible(txt))
                segs.append(f"  {color}{txt}{Color.RESET}{' ' * relleno}  ")
            salida.append(margen + "  ║" + "│".join(segs) + "║")
        return salida

    sep_top = margen + "  ╔" + "╤".join("═" * (a + 4) for a in anchos) + "╗"
    sep_hdr = margen + "  ╠" + "╪".join("═" * (a + 4) for a in anchos) + "╣"
    sep_mid = margen + "  ├" + "┼".join("─" * (a + 4) for a in anchos) + "┤"
    sep_bot = margen + "  ╚" + "╧".join("═" * (a + 4) for a in anchos) + "╝"

    pad_titulo = max(0, (total - 2 - len(titulo)) // 2)
    lineas = [
        "",
        f"{margen}  {' ' * pad_titulo}{Color.titulo(titulo)}",
        sep_top,
    ]
    lineas += render_fila(columnas, Color.CARAMELO + Color.BOLD)
    lineas.append(sep_hdr)
    if not filas:
        lineas += render_fila(["(Sin registros)"] + [""] * (n - 1), Color.GRIS)
    else:
        for idx, fila in enumerate(filas):
            color = Color.CREMA if idx % 2 == 0 else Color.GRIS
            lineas += render_fila(fila, color)
            if idx < len(filas) - 1:
                lineas.append(sep_mid)
    lineas.append(sep_bot)

    texto = "\n".join(lineas)
    if retornar_texto:
        return texto
    print(texto)


# ── ENTRADA DE CONTRASENA OCULTA ─────────────────────────────────────────────

def tabla_centrada(titulo, columnas, filas):
    """
    Tabla de referencia centrada con bordes Unicode, lista para imprimir o para usar
    como encabezado_extra de seleccionar_con_flechas. Sin filas muestra un aviso centrado.
    """
    if not filas:
        return formatear_bloque_centrado([(titulo, "titulo"), ("Sin registros.", "dim")])
    return imprimir_tabla(titulo, columnas, filas, retornar_texto=True)


def pedir_contrasena(prompt="Contrasena: "):
    """Lee la contrasena sin mostrarla en pantalla (getpass)."""
    pfx = _prefijo(_ancho())
    raw = getpass.getpass(f"{pfx}  {prompt}")
    _verificar_cancelacion(raw)
    return raw


# ── FUNCIONES DE ENTRADA VALIDADA CON NORMALIZACION ──────────────────────────

def _imprimir_guia(que, formato, ejemplo, accion="", nota=None):
    """Caja de ayuda para un campo. Los valores largos se envuelven dentro de la caja."""
    ancho = _ancho()
    caja_w = max(40, min(74, ancho - 4))
    p = " " * _margen(caja_w)
    sep_in = p + Color.DIM + "─" * caja_w + Color.RESET
    etiqueta_w = 13
    util = caja_w - 2 - etiqueta_w

    def linea(etiqueta, valor, color_valor=""):
        trozos = textwrap.wrap(str(valor), width=util) or [""]
        salida = [f"{p}  {Color.CIAN}{etiqueta:<{etiqueta_w}}{Color.RESET}{color_valor}{trozos[0]}{Color.RESET}"]
        for t in trozos[1:]:
            salida.append(f"{p}  {' ' * etiqueta_w}{color_valor}{t}{Color.RESET}")
        return salida

    print(sep_in)
    for l in linea("[>>] Dato:", que):
        print(l)
    for l in linea("Formato:", formato):
        print(l)
    for l in linea("Ejemplo:", ejemplo, Color.CARAMELO):
        print(l)
    if accion:
        for l in linea("Accion:", accion, Color.DIM):
            print(l)
    nota = nota or "Escribe 0 o CANCELAR para abortar y volver atras sin guardar."
    for l in textwrap.wrap(nota, width=caja_w - 2):
        print(f"{p}  {Color.DIM}{l}{Color.RESET}")
    print(sep_in)


def _verificar_cancelacion(val):
    normalizado = val.strip().upper()
    if normalizado in ("0", "CANCELAR"):
        raise OperacionCancelada("Operacion cancelada por el usuario.")


def _input_centrado(prompt):
    ancho = _ancho()
    pfx = _prefijo(ancho)
    print(f"{pfx}  {Color.CIAN}{prompt}: {Color.RESET}", end="", flush=True)
    return input().strip()


def pedir_correo(prompt="Correo electronico", obligatorio=True, aceptar_salir=False):
    _imprimir_guia(
        "Correo electronico del usuario",
        "usuario@dominio.com  (sin espacios, con @ y punto en dominio)",
        "ejemplo@coffeelytics.com",
        "Se convierte automaticamente a minusculas."
    )
    raw = _input_centrado(prompt)
    if aceptar_salir and raw.strip().upper() == "SALIR":
        raise OperacionCancelada("Operacion cancelada por el usuario.")
    _verificar_cancelacion(raw)
    val = raw.lower()
    if not obligatorio and val == "":
        return val
    if "@" in val and "." in val.split("@")[-1] and " " not in val:
        return val
    raise ValueError("Formato invalido. Debe contener '@' y dominio con punto. Sin espacios.")


def pedir_codigo(prompt="Codigo", longitud_max=10, ejemplo="INS008"):
    _imprimir_guia(
        f"Codigo identificador (maximo {longitud_max} caracteres alfanumericos)",
        f"Solo letras y numeros, sin espacios, maximo {longitud_max} chars",
        ejemplo,
        "Se convierte automaticamente a MAYUSCULAS."
    )
    raw = _input_centrado(prompt)
    _verificar_cancelacion(raw)
    val = raw.upper()
    if val and len(val) <= longitud_max and val.replace("-", "").replace("_", "").isalnum():
        return val
    raise ValueError(
        f"Codigo invalido. Solo letras y numeros, sin espacios, maximo {longitud_max} caracteres.")


def pedir_nombre_propio(prompt="Nombre", max_len=50, ejemplo="Juan Perez"):
    _imprimir_guia(
        "Nombre propio (persona, producto o insumo)",
        f"Texto libre, maximo {max_len} caracteres",
        ejemplo,
        "Se ajusta automaticamente a Formato Titulo: 'juan perez' -> 'Juan Perez'."
    )
    raw = _input_centrado(prompt)
    _verificar_cancelacion(raw)
    val = raw.title()
    if val and len(val) <= max_len:
        return val
    if not val:
        raise ValueError("El nombre no puede estar vacio.")
    raise ValueError(f"El nombre no puede superar {max_len} caracteres.")


def pedir_rfc(prompt="RFC"):
    _imprimir_guia(
        "RFC de persona fisica o moral",
        "12 o 13 caracteres alfanumericos (sin espacios ni guiones)",
        "COF260101TJ8  o  VECJ880326XXX",
        "Se convierte automaticamente a MAYUSCULAS."
    )
    raw = _input_centrado(prompt)
    _verificar_cancelacion(raw)
    val = raw.upper().replace("-", "").replace(" ", "")
    if 12 <= len(val) <= 13 and val.isalnum():
        return val
    raise ValueError("RFC invalido. Debe tener 12 o 13 caracteres alfanumericos sin espacios.")


def pedir_telefono(prompt="Telefono"):
    _imprimir_guia(
        "Numero de telefono de 10 digitos",
        "Solo digitos numericos, exactamente 10",
        "6641234567",
        "Se valida que sea exactamente 10 digitos."
    )
    raw = _input_centrado(prompt)
    _verificar_cancelacion(raw)
    val = raw.replace("-", "").replace(" ", "").replace("(", "").replace(")", "")
    if val.isdigit() and len(val) == 10:
        return val
    raise ValueError("Telefono invalido. Debe tener exactamente 10 digitos numericos.")


def pedir_numero_positivo(prompt="Cantidad", unidad="", ejemplo="1000",
                          stock_max=None, nombre_campo="cantidad", solo_entero=False):
    formato = "Numero entero positivo" if solo_entero else \
        f"Numero entero o decimal positivo{' en ' + unidad if unidad else ''}"
    desc_stock = f"  No puede exceder el stock disponible ({stock_max} {unidad})." \
                 if stock_max is not None else ""
    _imprimir_guia(
        f"{nombre_campo.capitalize()} numerica mayor a cero",
        formato,
        ejemplo,
        f"Se validara antes de registrar.{desc_stock}"
    )
    raw = _input_centrado(f"{prompt}{' (' + unidad + ')' if unidad else ''}")
    _verificar_cancelacion(raw)
    try:
        val = float(raw)
    except ValueError:
        raise ValueError(f"Valor invalido. '{raw.strip()}' no es un numero positivo.")
    if not math.isfinite(val) or val <= 0:
        raise ValueError("La cantidad debe ser un numero finito mayor a cero.")
    if solo_entero and not val.is_integer():
        raise ValueError(
            f"No se permiten decimales para la unidad {unidad}. Ingresa una cantidad entera."
        )
    if stock_max is not None and val > float(stock_max):
        raise ValueError(
            f"La cantidad ({val}) supera el stock disponible ({stock_max} {unidad}).")
    return int(val) if solo_entero else val


def pedir_precio(prompt="Precio unitario ($MXN)", ejemplo="0.85"):
    _imprimir_guia(
        "Precio en pesos mexicanos (MXN)",
        "Numero decimal positivo con hasta 2 decimales",
        ejemplo,
        "El sistema calculara IVA 8% (proveedor frontera) o 16% (interior) automaticamente."
    )
    raw = _input_centrado(f"{prompt} $")
    _verificar_cancelacion(raw)
    try:
        val = float(raw)
    except ValueError:
        raise ValueError("Precio invalido. Ingresa un numero mayor a 0 (ej. 0.85 o 150).")
    if math.isfinite(val) and val > 0:
        return val
    raise ValueError("Precio invalido. Ingresa un numero mayor a 0 (ej. 0.85 o 150).")


def pedir_motivo(prompt="Motivo", ejemplo="Derrame accidental en barra"):
    _imprimir_guia(
        "Motivo o descripcion de la incidencia",
        "Texto libre, maximo 300 caracteres",
        ejemplo,
        "La primera letra se convierte automaticamente a mayuscula."
    )
    raw = _input_centrado(prompt)
    _verificar_cancelacion(raw)
    val = raw.capitalize()
    if val and len(val) <= 300:
        return val
    if not val:
        raise ValueError("El motivo no puede estar vacio.")
    raise ValueError("El motivo no puede superar 300 caracteres.")


def pedir_fecha(prompt="Fecha (YYYY-MM-DD)"):
    _imprimir_guia(
        "Fecha en formato ISO 8601",
        "YYYY-MM-DD  (anio 4 digitos, mes 2, dia 2)",
        datetime.datetime.now().strftime("%Y-%m-%d"),
        "El sistema buscara todas las ventas de ese empleado en esa fecha exacta."
    )
    raw = _input_centrado(prompt)
    _verificar_cancelacion(raw)
    try:
        datetime.datetime.strptime(raw, "%Y-%m-%d")
        return raw
    except ValueError:
        raise ValueError("Formato invalido. Usa YYYY-MM-DD (ej. 2024-12-25).")


def pedir_entero_positivo(prompt="Folio", ejemplo="5"):
    _imprimir_guia(
        "Numero entero positivo",
        "Solo digitos, sin puntos ni comas",
        ejemplo,
        "El sistema buscara el registro con ese folio en la base de datos."
    )
    raw = _input_centrado(prompt)
    _verificar_cancelacion(raw)
    if raw.isdigit() and int(raw) > 0:
        return int(raw)
    raise ValueError("Folio invalido. Ingresa un numero entero positivo.")


def pedir_nombre_cliente():
    _imprimir_guia(
        "Nombre del cliente para el ticket",
        "Texto libre, maximo 50 caracteres. ENTER para 'Mostrador'",
        "Maria Garcia",
        "Se ajusta a Formato Titulo. Aparece impreso en el ticket de venta."
    )
    raw = _input_centrado("Nombre del cliente (ENTER = Mostrador)")
    if not raw:
        return "Mostrador"
    _verificar_cancelacion(raw)
    if len(raw) > 50:
        raise ValueError("El nombre del cliente no puede superar 50 caracteres.")
    return raw.title()[:50]


def pedir_monto_efectivo(total):
    _imprimir_guia(
        "Monto en efectivo entregado por el cliente",
        f"Numero mayor o igual al total: ${total:.2f}",
        f"{total:.2f}  o  200.00",
        f"El sistema calculara el cambio automaticamente: cambio = monto - ${total:.2f}."
    )
    raw = _input_centrado("Monto recibido $")
    _verificar_cancelacion(raw)
    try:
        val = float(raw)
    except ValueError:
        raise ValueError("Ingresa una cantidad numerica valida (ej. 200 o 150.50).")
    if not math.isfinite(val):
        raise ValueError("Ingresa una cantidad numerica valida y finita.")
    if val >= total:
        cambio = round(val - total, 2)
        print(_centrar_texto(Color.ok(f"Cambio: ${cambio:.2f}")))
        return val, cambio
    raise ValueError(f"Monto insuficiente. El total es ${total:.2f}.")


def pedir_input_centrado(prompt):
    """Lee un texto libre centrado (ENTER permitido). Devuelve el texto sin espacios extremos."""
    return _input_centrado(prompt)


def pedir_cantidad_a_quitar(nombre_producto, maximo):
    """
    Pide cuantas unidades quitar del pedido (1 a `maximo`).
    0 o CANCELAR lanza OperacionCancelada y no se quita nada.
    """
    _imprimir_guia(
        f"Unidades de '{nombre_producto}' a quitar del pedido",
        f"Entero entre 1 y {maximo} (cantidad actual en el pedido)",
        "1",
        "Se resta del pedido y los importes se recalculan.",
        nota="Escribe 0 o CANCELAR para no quitar nada."
    )
    raw = _input_centrado(f"Unidades a quitar (1-{maximo})")
    _verificar_cancelacion(raw)
    if raw.isdigit() and 1 <= int(raw) <= maximo:
        return int(raw)
    raise ValueError(f"Cantidad invalida. Ingresa un entero entre 1 y {maximo}.")


def pedir_monto_contado(esperado):
    """
    Efectivo fisico contado en caja: numero >= 0 (0 es valido). CANCELAR aborta.
    """
    _imprimir_guia(
        "Efectivo fisico contado en caja",
        "Numero mayor o igual a 0 (puede ser 0)",
        f"{esperado:.2f}",
        "Se compara contra el efectivo esperado por el sistema.",
        nota="Escribe CANCELAR para salir sin generar el corte."
    )
    raw = _input_centrado("Efectivo contado $")
    if raw.strip().upper() == "CANCELAR":
        raise OperacionCancelada("Corte cancelado por el usuario.")
    try:
        val = float(raw)
    except ValueError:
        raise ValueError("Monto invalido. Ingresa un numero mayor o igual a 0.")
    if not math.isfinite(val) or val < 0:
        raise ValueError("Monto invalido. Ingresa un numero mayor o igual a 0.")
    return round(val, 2)


def pedir_cantidad_carrito(nombre_producto):
    _imprimir_guia(
        f"Cantidad de '{nombre_producto}' a agregar al pedido",
        "Numero entero positivo (minimo 1)",
        "1  o  2",
        "Se suma al carrito activo. Puedes agregar mas unidades del mismo producto."
    )
    raw = _input_centrado("Cantidad (ENTER = 1)")
    _verificar_cancelacion(raw)
    if raw == "":
        return 1
    try:
        cant = int(raw)
        if cant > 0:
            return cant
    except ValueError:
        raise ValueError("La cantidad debe ser un numero entero positivo.")
    raise ValueError("La cantidad debe ser un numero entero positivo.")
