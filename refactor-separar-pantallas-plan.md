# Plan: Separar pantalla_admin.py y pantalla_barista.py en archivos por sección

## Top-Level Overview

**Goal:** Dividir `pantalla_admin.py` (872 líneas) y `pantalla_barista.py` (321 líneas) en archivos más pequeños y legibles usando **composición** — cada sección se convierte en su propia clase que `PantallaAdmin` / `PantallaBarista` usa como atributo.

**Convención de composición:**
```python
# Cada clase nueva recibe en su __init__ solo los atributos que necesita
class AdminInventario:
    def __init__(self, usuario, inventario_srv, compra_srv, reportes):
        self.usuario = usuario
        self.inventario_srv = inventario_srv
        ...

# PantallaAdmin las instancia en su __init__
class PantallaAdmin:
    def __init__(self, usuario, servicios, reportes):
        self.inventario_ui = AdminInventario(usuario, servicios["inventario"], ...)
```

**Archivos nuevos a crear (todos en `Coffeelytics/interfaz/`):**
- `admin_inventario.py` — AlertasStock, RegistrarCompra, RegistrarInsumo
- `admin_productos.py` — AltaProducto, ConfigurarReceta, AsignarInsumoReceta
- `admin_consultas.py` — MenuConsultas + C1 a C5
- `admin_empleados.py` — GestionEmpleados, ListarEmpleados, CrearEmpleado, DesactivarEmpleado
- `barista_catalogo.py` — CatalogoProductos, ListarProductosCategoria, PrevisualizarYAgregar
- `barista_carrito.py` — GestionarCarrito, QuitarDelCarrito
- `barista_operaciones.py` — RegistrarMerma, SurtirMesa, DesactivarMiCuenta

**Archivos modificados:**
- `interfaz/pantalla_admin.py` — queda solo con `__init__`, `mostrar()` y funciones módulo-nivel
- `interfaz/pantalla_barista.py` — queda solo con `__init__` y `mostrar()`

**Scope:** Solo reorganización — ningún comportamiento cambia.

---

## Sub-Task 1 — Crear `admin_inventario.py`

**Status:** [x] done

### Intent
Mover los métodos de inventario/insumos a su propia clase `AdminInventario`.

### Expected Outcomes
- `interfaz/admin_inventario.py` existe con clase `AdminInventario`
- Métodos movidos: `_alertas_stock`, `_registrar_compra`, `_registrar_insumo`
- `PantallaAdmin` usa `self.inventario_ui = AdminInventario(...)` y delega con `self.inventario_ui.alertas_stock()` etc.

### Todo List
1. Crear `interfaz/admin_inventario.py` con clase `AdminInventario`
2. Mover los 3 métodos (renombrar: quitar guion bajo inicial ya que son públicos dentro de su clase)
3. `__init__` recibe: `usuario`, `inventario_srv`, `compra_srv`, `reportes`
4. Copiar los imports necesarios al nuevo archivo
5. En `pantalla_admin.py`: añadir `self.inventario_ui`, reemplazar los 3 métodos con llamadas de delegación de una línea

### Relevant Context
- Métodos: `_alertas_stock` (141–157), `_registrar_compra` (191–268), `_registrar_insumo` (270–342)
- Imports usados: `Color`, `consola_ui` (todos los helpers), `_prefijo`, `_ancho`
- `_registrar_compra` usa: `self.compra_srv`, `self.inventario_srv`, `self.usuario`
- `_registrar_insumo` usa: `self.inventario_srv`, `self.usuario`
- `_alertas_stock` usa: `self.inventario_srv`, `self.usuario`

---

## Sub-Task 2 — Crear `admin_productos.py`

**Status:** [x] done

### Intent
Mover los métodos de productos/recetas a su propia clase `AdminProductos`.

### Expected Outcomes
- `interfaz/admin_productos.py` existe con clase `AdminProductos`
- Métodos movidos: `_configurar_receta`, `_asignar_insumo_receta`, `_alta_producto`
- `PantallaAdmin` usa `self.productos_ui = AdminProductos(...)` y delega

### Todo List
1. Crear `interfaz/admin_productos.py` con clase `AdminProductos`
2. Mover los 3 métodos
3. `__init__` recibe: `usuario`, `producto_srv`, `inventario_srv`
4. En `pantalla_admin.py`: añadir `self.productos_ui`, reemplazar los 3 métodos con delegación

### Relevant Context
- Métodos: `_configurar_receta` (83–139), `_asignar_insumo_receta` (344–401), `_alta_producto` (403–447)
- `_alta_producto` llama a `self._configurar_receta` — en la nueva clase será `self.configurar_receta`
- Usa: `self.producto_srv`, `self.inventario_srv`, `self.usuario`

---

## Sub-Task 3 — Crear `admin_consultas.py`

**Status:** [x] done

### Intent
Mover el menú de consultas y las 5 consultas a su propia clase `AdminConsultas`.

### Expected Outcomes
- `interfaz/admin_consultas.py` existe con clase `AdminConsultas`
- Métodos movidos: `_menu_consultas`, `_consulta_1` a `_consulta_5`
- `PantallaAdmin` usa `self.consultas_ui = AdminConsultas(...)` y delega con `self.consultas_ui.menu()`

### Todo List
1. Crear `interfaz/admin_consultas.py` con clase `AdminConsultas`
2. Mover los 6 métodos
3. `__init__` recibe: `usuario`, `reporte_srv`, `empleado_srv`, `producto_srv`, `reportes`
4. En `pantalla_admin.py`: añadir `self.consultas_ui`, reemplazar `_menu_consultas` con delegación

### Relevant Context
- Métodos: `_menu_consultas` (449–475), `_consulta_1` (477–529), `_consulta_2` (531–573), `_consulta_3` (575–640), `_consulta_4` (642–686), `_consulta_5` (688–720)
- `_consulta_4` usa `self.empleado_srv` — incluir en `__init__`
- `_consulta_5` usa `self.producto_srv` — incluir en `__init__`
- Usa `datetime` — incluir import
- `_menu_consultas` llama a los otros `_consulta_*` — en la nueva clase serán `self._consulta_1()` etc. (pueden mantener guion bajo por ser privados)

---

## Sub-Task 4 — Crear `admin_empleados.py`

**Status:** [x] done

### Intent
Mover los métodos de gestión de empleados a su propia clase `AdminEmpleados`.

### Expected Outcomes
- `interfaz/admin_empleados.py` existe con clase `AdminEmpleados`
- Métodos movidos: `_gestion_empleados`, `_listar_empleados`, `_crear_empleado`, `_desactivar_empleado`
- `PantallaAdmin` usa `self.empleados_ui = AdminEmpleados(...)` y delega

### Todo List
1. Crear `interfaz/admin_empleados.py` con clase `AdminEmpleados`
2. Mover los 4 métodos
3. `__init__` recibe: `usuario`, `empleado_srv`
4. En `pantalla_admin.py`: añadir `self.empleados_ui`, reemplazar `_gestion_empleados` con delegación

### Relevant Context
- Métodos: `_gestion_empleados` (722–754), `_listar_empleados` (756–767), `_crear_empleado` (769–841), `_desactivar_empleado` (843–872)
- `_es_admin_principal(usuario)` y `_acceso_denegado()` son funciones de módulo en `pantalla_admin.py` — importarlas en el nuevo archivo o moverlas también

---

## Sub-Task 5 — Limpiar `pantalla_admin.py`

**Status:** [x] done

### Intent
Después de las 4 sub-tareas anteriores, `pantalla_admin.py` debe quedar solo con la coordinación central.

### Expected Outcomes
- `pantalla_admin.py` queda con ~120 líneas
- Contiene: imports, `_es_admin_principal`, `_acceso_denegado`, clase `PantallaAdmin` con `__init__` y `mostrar()`
- `__init__` instancia las 4 clases de composición
- `mostrar()` delega a las clases correspondientes según la opción del menú
- El comportamiento del menú principal no cambia

### Todo List
1. Verificar que todos los métodos movidos estén correctamente eliminados de `pantalla_admin.py`
2. Verificar que `mostrar()` llama a los métodos de composición correctamente
3. Eliminar imports que ya no se usan directamente en `pantalla_admin.py`
4. Ejecutar `python -m py_compile` en todos los archivos

---

## Sub-Task 6 — Crear `barista_catalogo.py`

**Status:** [x] done

### Intent
Mover los métodos de catálogo/productos del barista a su propia clase `BaristaCatalogo`.

### Expected Outcomes
- `interfaz/barista_catalogo.py` existe con clase `BaristaCatalogo`
- Métodos movidos: `_catalogo_productos`, `_listar_productos_categoria`, `_previsualizar_y_agregar`
- `PantallaBarista` usa `self.catalogo_ui = BaristaCatalogo(...)` y delega

### Todo List
1. Crear `interfaz/barista_catalogo.py` con clase `BaristaCatalogo`
2. Mover los 3 métodos
3. `__init__` recibe: `usuario`, `producto_srv`, `carrito` — el carrito debe ser compartido con `barista_carrito.py`
4. En `pantalla_barista.py`: añadir `self.catalogo_ui`, reemplazar con delegación

### Relevant Context
- Métodos: `_catalogo_productos` (53–71), `_listar_productos_categoria` (73–93), `_previsualizar_y_agregar` (95–128)
- El `carrito` es un objeto compartido entre catálogo y carrito — se instancia en `PantallaBarista.__init__` y se pasa a ambas clases de composición

---

## Sub-Task 7 — Crear `barista_carrito.py`

**Status:** [x] done

### Intent
Mover los métodos del carrito a su propia clase `BaristaCarrito`.

### Expected Outcomes
- `interfaz/barista_carrito.py` existe con clase `BaristaCarrito`
- Métodos movidos: `_gestionar_carrito`, `_quitar_del_carrito`
- `PantallaBarista` usa `self.carrito_ui = BaristaCarrito(...)` y delega

### Todo List
1. Crear `interfaz/barista_carrito.py` con clase `BaristaCarrito`
2. Mover los 2 métodos
3. `__init__` recibe: `usuario`, `venta_srv`, `carrito`, `reportes`
4. En `pantalla_barista.py`: añadir `self.carrito_ui`, reemplazar con delegación

### Relevant Context
- Métodos: `_gestionar_carrito` (130–180), `_quitar_del_carrito` (182–195)
- `_gestionar_carrito` llama a `self._quitar_del_carrito` — en la nueva clase será `self._quitar_del_carrito()`

---

## Sub-Task 8 — Crear `barista_operaciones.py`

**Status:** [x] done

### Intent
Mover merma, surtir mesa y desactivar cuenta a su propia clase `BaristaOperaciones`.

### Expected Outcomes
- `interfaz/barista_operaciones.py` existe con clase `BaristaOperaciones`
- Métodos movidos: `_registrar_merma`, `_surtir_mesa`, `_desactivar_mi_cuenta`
- `PantallaBarista` usa `self.operaciones_ui = BaristaOperaciones(...)` y delega

### Todo List
1. Crear `interfaz/barista_operaciones.py` con clase `BaristaOperaciones`
2. Mover los 3 métodos
3. `__init__` recibe: `usuario`, `inventario_srv`, `despacho_srv`, `empleado_srv`
4. En `pantalla_barista.py`: añadir `self.operaciones_ui`, reemplazar con delegación

### Relevant Context
- Métodos: `_registrar_merma` (197–253), `_surtir_mesa` (255–297), `_desactivar_mi_cuenta` (299–321)
- `_desactivar_mi_cuenta` llama a `self.empleado_srv.desactivar_cuenta`

---

## Sub-Task 9 — Limpiar `pantalla_barista.py`

**Status:** [x] done

### Intent
Después de las 3 sub-tareas anteriores, `pantalla_barista.py` queda solo con coordinación.

### Expected Outcomes
- `pantalla_barista.py` queda con ~80 líneas
- Contiene: imports, clase `PantallaBarista` con `__init__` y `mostrar()`
- `__init__` instancia las 3 clases de composición y el `carrito` compartido
- El comportamiento del menú no cambia

### Todo List
1. Verificar que todos los métodos movidos están eliminados
2. Verificar que `mostrar()` delega correctamente
3. Limpiar imports innecesarios
4. Ejecutar `python -m py_compile` en todos los archivos nuevos y modificados
