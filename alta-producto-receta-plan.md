# Plan: Alta de Producto con Asignación de Receta

## Top-Level Overview

**Goal:** After creating a new product in `_alta_producto`, automatically redirect the admin into an interactive recipe-assignment loop (`_configurar_receta`) where they can add multiple insumos (with quantities) until they choose to finish.

**Scope:**
- Fix `_configurar_receta` to use the current service/dict API (matching `_asignar_insumo_receta`'s patterns).
- Wire the success path of `_alta_producto` to call `_configurar_receta` instead of returning.

**Out of scope:** No changes to services, repositories, DB schema, or any other screen.

**Files touched:**
- `Coffeelytics/interfaz/pantalla_admin.py` only.

---

## Sub-Task 1 — Fix `_configurar_receta` to use the current API

**Status:** [ ] pending

### Intent
`_configurar_receta` already has the correct loop structure and UX intent, but was written against a stale API:
- It accesses services via `self.servicios["producto"]` / `self.servicios["inventario"]` (dict) — the current arch uses `self.producto_srv` / `self.inventario_srv` (instance attrs).
- It treats insumos as objects with `.codigo`, `.nombre`, `.stock_actual`, `.unidad_medida` attributes — the current arch returns dicts with keys `codigo`, `nombre`, `stockActual`, `abreviatura`.
- It calls `self.servicios["producto"].agregar_insumo_a_receta(...)` — the correct method is `self.producto_srv.registrar_insumo_en_receta(cod_producto, cod_insumo, cantidad)`.
- It calls `self.servicios["inventario"].listar_todos()` — the correct method is `self.inventario_srv.listar_todos_insumos()`.

### Expected Outcomes
- `_configurar_receta(prod_codigo, prod_nombre)` works standalone (callable from anywhere in `PantallaAdmin`).
- Each loop iteration: clears screen, prints header + breadcrumb, prints the current recipe table (using `imprimir_tabla`), then presents the insumo list via `seleccionar_con_flechas`.
- The final option in the selector is `"[OK] Finalizar y guardar receta"`.
- When an insumo is selected: `pedir_numero_positivo` collects the quantity; `self.producto_srv.registrar_insumo_en_receta(prod_codigo, ins["codigo"], cant)` is called; result message is printed; `pausar()` waits; loop continues.
- `OperacionCancelada` during quantity input: `continue` (skip, re-show loop).
- If the user selects "Finalizar": prints appropriate ok/aviso message and breaks.

### Todo List
1. Rewrite `_configurar_receta` body — replace all stale API calls with current equivalents.
   - `self.servicios["inventario"].listar_todos()` → `self.inventario_srv.listar_todos_insumos()`
   - `self.servicios["producto"].obtener_receta(prod_codigo)` → `self.producto_srv.obtener_receta(prod_codigo)`
   - Insumo object attrs → dict keys: `ins["codigo"]`, `ins["nombre"]`, `ins["stockActual"]`, `ins["abreviatura"]`
   - `agregar_insumo_a_receta(prod_codigo, ins.codigo, cant)` → `registrar_insumo_en_receta(prod_codigo, ins["codigo"], cant)` and handle `(ok, msg)` return tuple
2. Update breadcrumb to `["Inicio", "Panel Admin", "Alta de Producto", f"Receta: {prod_nombre}"]` (consistent with the rest of `PantallaAdmin`).
3. Update `imprimir_tabla` row construction to use dict keys: `r["insumo_codigo"]`, `r["nombre"]`, `r["cantidad_requerida"]`, `r["unidad_medida"]` (verify exact keys against `obtener_receta` query in `ProductoRepositorio`).

### Relevant Context
- Pattern to follow: `_asignar_insumo_receta` (lines 343–400 of `pantalla_admin.py`) — same service calls, same dict keys, same `(ok, msg)` handling.
- `obtener_receta` returns dicts; check `ProductoRepositorio.obtener_receta` for exact column aliases.
- `listar_todos_insumos` returns dicts with keys: `codigo`, `nombre`, `stockActual`, `abreviatura`.
- `imprimir_tabla` and `seleccionar_con_flechas` are already imported.

---

## Sub-Task 2 — Wire `_alta_producto` to `_configurar_receta`

**Status:** [ ] pending

### Intent
Currently `_alta_producto` ends by printing the result of `crear_producto_menu` and calling `pausar()` before returning. On success, control must flow into `_configurar_receta` so the admin can assign insumos immediately without navigating back through the menu.

### Expected Outcomes
- On failure: behavior unchanged — print error, `pausar()`, return.
- On success: print the success message (no pause), print an info line like `"Ahora puedes asignar los insumos de la receta."`, then immediately call `self._configurar_receta(codigo, nombre)`.
- After `_configurar_receta` returns, `_alta_producto` also returns (no extra pause needed — `_configurar_receta` already ends with `pausar()`).

### Todo List
1. In `_alta_producto`, replace the final block:
   ```
   ok, msg = self.producto_srv.crear_producto_menu(...)
   print(Color.ok(msg) if ok else Color.error(msg))
   pausar()
   ```
   with:
   ```
   ok, msg = self.producto_srv.crear_producto_menu(...)
   if not ok:
       print(Color.error(msg))
       pausar()
       return
   print(Color.ok(msg))
   print(Color.info("Ahora puedes asignar los insumos de la receta."))
   self._configurar_receta(codigo, nombre)
   ```

### Relevant Context
- `_alta_producto` lines 401–441 of `pantalla_admin.py`.
- `codigo` and `nombre` are already in scope from `pedir_codigo` / `pedir_nombre_propio` calls above.
- `Color.info(...)` is used throughout the file for informational messages.
