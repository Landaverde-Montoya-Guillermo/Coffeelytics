-- Consultas utilizadas por el programa Coffeelytics
-- Motor: MySQL/MariaDB

-- =====================
-- Consultas financieras
-- =====================

SELECT COUNT(*) AS num_ventas,
       COALESCE(SUM(total), 0) AS ingresos
FROM venta
WHERE <filtro_fecha>;

SELECT COALESCE(SUM(total), 0) AS gastos
FROM compra
WHERE <filtro_fecha>;

SELECT m.codigo,
       m.descripcion AS metodo,
       COUNT(v.codigo) AS operaciones,
       COALESCE(SUM(x.sub), 0) AS subtotal,
       COALESCE(SUM(x.iva), 0) AS iva,
       COALESCE(SUM(v.total), 0) AS total
FROM venta v
INNER JOIN metodo_pago m ON v.metodoPago = m.codigo
LEFT JOIN (
    SELECT venta, SUM(subtotal) AS sub, SUM(totalIVA) AS iva
    FROM prod_venta
    GROUP BY venta
) x ON x.venta = v.codigo
WHERE DATE(v.fecha) = CURDATE()
GROUP BY m.codigo, m.descripcion
ORDER BY m.descripcion;

SELECT e.num AS id,
       CONCAT(e.nombrePila, ' ', e.primApell) AS barista,
       COUNT(v.codigo) AS tickets,
       COALESCE(SUM(v.total), 0) AS total
FROM empleado e
LEFT JOIN venta v ON v.empleado = e.num
WHERE e.rol = 'BARS'
GROUP BY e.num, e.nombrePila, e.primApell
ORDER BY total DESC, e.num;

-- =====================
-- Ventas
-- =====================

SELECT v.codigo AS folio,
       DATE_FORMAT(v.fecha, '%d/%m/%Y %H:%i') AS fecha,
       v.nombreCliente AS cliente,
       m.descripcion AS metodo,
       v.total
FROM venta v
INNER JOIN empleado e ON v.empleado = e.num
INNER JOIN metodo_pago m ON v.metodoPago = m.codigo
WHERE v.empleado = %s AND e.rol = 'BARS'
ORDER BY v.fecha, v.codigo;

SELECT v.codigo AS folio,
       DATE_FORMAT(v.fecha, '%d/%m %H:%i') AS fecha,
       CONCAT(e.nombrePila, ' ', e.primApell) AS barista,
       v.nombreCliente AS cliente,
       m.descripcion AS metodo,
       v.total
FROM venta v
INNER JOIN empleado e ON v.empleado = e.num
INNER JOIN metodo_pago m ON v.metodoPago = m.codigo
ORDER BY v.codigo DESC
LIMIT %s;

SELECT v.codigo AS folio,
       v.fecha,
       v.nombreCliente,
       CONCAT(e.nombrePila, ' ', e.primApell) AS empleado,
       m.descripcion AS metodoPago,
       v.total
FROM venta v
INNER JOIN empleado e ON v.empleado = e.num
INNER JOIN metodo_pago m ON v.metodoPago = m.codigo
WHERE v.codigo = %s;

SELECT p.codigo,
       p.nombre,
       pv.precioUnitarioVenta AS precio,
       pv.cantidad,
       pv.subtotal,
       pv.totalIVA,
       pv.total
FROM prod_venta pv
INNER JOIN producto p ON pv.producto = p.codigo
WHERE pv.venta = %s;

INSERT INTO venta (fecha, nombreCliente, total, metodoPago, empleado)
VALUES (%s, %s, %s, %s, %s);

INSERT INTO prod_venta
(venta, producto, cantidad, precioUnitarioVenta, subtotal, totalIVA, total)
VALUES (%s, %s, %s, %s, %s, %s, %s);

SELECT DATE_FORMAT(v.fecha, '%Y-%m-%d %H:%i') AS fecha,
       CONCAT_WS(' ', e.nombrePila, e.primApell, e.segApell) AS empleado,
       v.codigo AS folio,
       v.total,
       mp.descripcion AS metodoPago
FROM venta v
INNER JOIN empleado e ON v.empleado = e.num
INNER JOIN metodo_pago mp ON v.metodoPago = mp.codigo
WHERE DATE(v.fecha) = %s AND v.empleado = %s AND e.rol = 'BARS'
ORDER BY v.fecha, v.codigo;

SELECT DATE_FORMAT(v.fecha, '%Y-%m-%d %H:%i') AS fecha,
       CONCAT_WS(' ', e.nombrePila, e.primApell, e.segApell) AS empleado,
       v.codigo AS folio,
       v.total,
       mp.descripcion AS metodoPago
FROM venta v
INNER JOIN empleado e ON v.empleado = e.num
INNER JOIN metodo_pago mp ON v.metodoPago = mp.codigo
WHERE v.fecha >= DATE_SUB(CURDATE(), INTERVAL 7 DAY)
  AND v.empleado = %s AND e.rol = 'BARS'
ORDER BY v.fecha, v.codigo;

SELECT DATE_FORMAT(v.fecha, '%Y-%m-%d %H:%i') AS fecha,
       CONCAT_WS(' ', e.nombrePila, e.primApell, e.segApell) AS empleado,
       v.codigo AS folio,
       v.total,
       mp.descripcion AS metodoPago
FROM venta v
INNER JOIN empleado e ON v.empleado = e.num
INNER JOIN metodo_pago mp ON v.metodoPago = mp.codigo
WHERE MONTH(v.fecha) = %s AND YEAR(v.fecha) = %s
  AND v.empleado = %s AND e.rol = 'BARS'
ORDER BY v.fecha, v.codigo;

-- =====================
-- Compras
-- =====================

SELECT c.codigo AS folio,
       c.fecha,
       p.nombre AS proveedor,
       p.ciudad,
       c.total
FROM compra c
INNER JOIN proveedor p ON c.proveedor = p.codigo
WHERE c.codigo = %s;

SELECT c.codigo AS folio,
       DATE_FORMAT(c.fecha, '%d/%m/%Y') AS fecha,
       p.nombre AS proveedor,
       COALESCE(NULLIF(CONCAT_WS(' ', e.nombrePila, e.primApell, e.segApell), ''),
                'Sin asignar') AS empleado,
       c.total
FROM compra c
INNER JOIN proveedor p ON c.proveedor = p.codigo
INNER JOIN empleado e ON c.empleado = e.num
ORDER BY c.codigo DESC;

SELECT i.codigo,
       i.nombre,
       ic.precioUnitarioCom AS precio,
       ic.cantidad,
       ic.subtotal,
       ic.totalIVA,
       ic.total
FROM insum_com ic
INNER JOIN insumo i ON ic.insumo = i.codigo
WHERE ic.compra = %s;

INSERT INTO compra (fecha, total, proveedor, metodoPago, empleado)
VALUES (CURDATE(), %s, %s, %s, %s);

INSERT INTO insum_com
(compra, insumo, cantidad, precioUnitarioCom, subtotal, totalIVA, total)
VALUES (%s, %s, %s, %s, %s, %s, %s);

-- =====================
-- Empleados y autenticacion
-- =====================

SELECT e.num,
       e.nombrePila,
       e.primApell,
       e.segApell,
       e.RFC,
       e.telefono,
       e.correo,
       e.activo,
       e.rol AS rol_codigo,
       r.nombre AS rol_nombre
FROM empleado e
INNER JOIN rol r ON e.rol = r.codigo
WHERE e.correo = %s AND e.contrasena = %s AND e.activo = 1;

INSERT INTO empleado
(nombrePila, primApell, segApell, RFC, telefono, correo, contrasena, activo, rol)
VALUES (%s, %s, %s, %s, %s, %s, %s, 1, %s);

UPDATE empleado
SET activo = 0
WHERE num = %s;

SELECT e.num,
       CONCAT(e.nombrePila, ' ', e.primApell) AS nombre,
       e.RFC AS rfc,
       e.correo,
       r.nombre AS rol,
       e.activo
FROM empleado e
INNER JOIN rol r ON e.rol = r.codigo
ORDER BY e.num;

SELECT e.num,
       CONCAT_WS(' ', e.nombrePila, e.primApell, e.segApell) AS nombre,
       e.correo
FROM empleado e
WHERE e.rol = 'BARS'
ORDER BY e.num;

-- =====================
-- Inventario e insumos
-- =====================

SELECT codigo, capacidad, secciones
FROM estante
ORDER BY codigo;

SELECT secciones
FROM estante
WHERE codigo = %s;

SELECT i.codigo,
       i.nombre,
       i.stockActual,
       i.stockMin,
       u.codigo AS unidad_codigo,
       u.abreviatura,
       ci.nombre AS categoria
FROM insumo i
INNER JOIN unidad_medida u ON i.unidad = u.codigo
INNER JOIN categoria_insumo ci ON i.categoria = ci.codigo
ORDER BY i.codigo;

SELECT i.codigo,
       i.nombre,
       ci.nombre AS categoria,
       u.abreviatura AS unidad,
       i.stockActual,
       i.stockMin
FROM insumo i
INNER JOIN categoria_insumo ci ON i.categoria = ci.codigo
INNER JOIN unidad_medida u ON i.unidad = u.codigo
ORDER BY i.codigo;

SELECT i.codigo,
       i.nombre,
       ci.codigo AS categoria_codigo,
       ci.nombre AS categoria,
       u.nombre AS unidad_medida,
       u.abreviatura AS unidad,
       i.stockActual,
       i.stockMin,
       i.seccion,
       e.codigo AS estante
FROM insumo i
INNER JOIN categoria_insumo ci ON i.categoria = ci.codigo
INNER JOIN unidad_medida u ON i.unidad = u.codigo
INNER JOIN estante e ON i.estante = e.codigo
WHERE i.codigo = %s;

SELECT i.codigo,
       i.nombre,
       i.stockActual,
       i.stockMin,
       u.codigo AS unidad_codigo,
       u.abreviatura
FROM insumo i
INNER JOIN unidad_medida u ON i.unidad = u.codigo
WHERE i.categoria = 'MESA'
ORDER BY i.codigo;

SELECT i.codigo,
       i.nombre,
       i.stockActual,
       i.stockMin,
       u.codigo AS unidad_codigo,
       u.abreviatura
FROM insumo i
INNER JOIN unidad_medida u ON i.unidad = u.codigo
WHERE i.categoria <> 'MESA'
ORDER BY i.codigo;

SELECT codigo,
       nombre,
       stockActual,
       stockMin,
       unidad AS unidad_codigo
FROM insumo
WHERE codigo = %s;

INSERT INTO insumo
(codigo, nombre, stockActual, stockMin, seccion, unidad, estante, categoria)
VALUES (%s, %s, %s, %s, %s, %s, %s, %s);

UPDATE insumo
SET stockActual = %s
WHERE codigo = %s;

SELECT i.codigo,
       i.nombre,
       i.stockActual,
       i.stockMin,
       u.abreviatura,
       COALESCE(p.nombre, 'Sin proveedor') AS proveedor,
       COALESCE(p.telefono, 'N/A') AS telefono,
       COALESCE(p.ciudad, 'Tijuana') AS ciudad
FROM insumo i
INNER JOIN unidad_medida u ON i.unidad = u.codigo
LEFT JOIN insum_com ic ON i.codigo = ic.insumo
LEFT JOIN compra c ON ic.compra = c.codigo
LEFT JOIN proveedor p ON c.proveedor = p.codigo
WHERE i.stockActual <= i.stockMin
GROUP BY i.codigo,
         i.nombre,
         i.stockActual,
         i.stockMin,
         u.abreviatura,
         p.nombre,
         p.telefono,
         p.ciudad
ORDER BY i.stockActual ASC;

-- =====================
-- Productos y recetas
-- =====================

SELECT c.codigo,
       c.nombre,
       COUNT(DISTINCT p.codigo) AS total,
       COUNT(DISTINCT CASE
           WHEN p.estatus = %s AND ri.insumo IS NOT NULL THEN p.codigo
       END) AS disponibles
FROM categoria_producto c
LEFT JOIN producto p ON c.codigo = p.categoria
LEFT JOIN receta r ON r.producto = p.codigo
LEFT JOIN rec_insum ri ON ri.receta = r.codigo
GROUP BY c.codigo, c.nombre
ORDER BY c.codigo;

SELECT p.codigo,
       p.nombre,
       p.precio,
       p.estatus,
       c.codigo AS cat_cod,
       c.nombre AS cat_nom
FROM producto p
INNER JOIN categoria_producto c ON p.categoria = c.codigo
WHERE p.categoria = %s
  AND p.estatus = %s
  AND EXISTS (
      SELECT 1
      FROM receta r
      INNER JOIN rec_insum ri ON ri.receta = r.codigo
      WHERE r.producto = p.codigo
  )
ORDER BY p.codigo;

SELECT 1
FROM producto p
WHERE p.codigo = %s
  AND p.estatus = %s
  AND EXISTS (
      SELECT 1
      FROM receta r
      INNER JOIN rec_insum ri ON ri.receta = r.codigo
      WHERE r.producto = p.codigo
  );

SELECT p.codigo,
       p.nombre,
       p.precio,
       p.estatus,
       c.codigo AS cat_cod,
       c.nombre AS cat_nom
FROM producto p
INNER JOIN categoria_producto c ON p.categoria = c.codigo
WHERE p.estatus = %s
  AND EXISTS (
      SELECT 1
      FROM receta r
      INNER JOIN rec_insum ri ON ri.receta = r.codigo
      WHERE r.producto = p.codigo
  )
ORDER BY p.nombre;

SELECT p.codigo,
       p.nombre,
       p.precio,
       p.estatus,
       c.nombre AS categoria
FROM producto p
INNER JOIN categoria_producto c ON p.categoria = c.codigo
ORDER BY p.codigo;

SELECT codigo
FROM producto;

INSERT INTO producto (codigo, nombre, precio, estatus, categoria)
VALUES (%s, %s, %s, %s, %s);

UPDATE producto
SET estatus = %s
WHERE codigo = %s;

SELECT i.codigo AS insumo_codigo,
       i.nombre,
       ri.cantidad,
       ri.cantidad AS requerido,
       i.stockActual,
       u.abreviatura,
       u.abreviatura AS unidad_medida
FROM receta r
JOIN rec_insum ri ON r.codigo = ri.receta
JOIN insumo i ON ri.insumo = i.codigo
JOIN unidad_medida u ON i.unidad = u.codigo
WHERE r.producto = %s
ORDER BY i.nombre;

SELECT codigo
FROM receta
WHERE producto = %s;

SELECT 1
FROM receta
WHERE codigo = %s;

INSERT INTO receta (codigo, producto)
VALUES (%s, %s);

INSERT INTO rec_insum (insumo, receta, cantidad)
VALUES (%s, %s, %s)
ON DUPLICATE KEY UPDATE cantidad = VALUES(cantidad);

-- =====================
-- Consumibles de mesa
-- =====================

INSERT INTO con_insum (insumo, mesa, cantidad)
VALUES (%s, %s, %s)
ON DUPLICATE KEY UPDATE cantidad = cantidad + VALUES(cantidad);

-- =====================
-- Proveedores y catalogos
-- =====================

SELECT codigo,
       nombre,
       ciudad,
       telefono
FROM proveedor
ORDER BY codigo;

SELECT codigo,
       nombre,
       ciudad,
       telefono
FROM proveedor
WHERE codigo = %s;

SELECT codigo, abreviatura
FROM unidad_medida
ORDER BY codigo;

SELECT codigo, nombre
FROM categoria_insumo
ORDER BY codigo;

-- =====================
-- Mermas
-- =====================

SELECT codigo, nombre
FROM tipo_merma
ORDER BY codigo;

INSERT INTO merma (motivo, fecha, cantidad, tipo, insumo, idEmpleado)
VALUES (%s, CURDATE(), %s, %s, %s, %s);

SELECT m.codigo,
       DATE_FORMAT(m.fecha, '%d/%m/%Y') AS fecha,
       i.codigo AS insumo_codigo,
       i.nombre AS insumo,
       CONCAT(m.cantidad, ' ', u.abreviatura) AS cantidad,
       tm.nombre AS tipo_merma,
       m.motivo,
       COALESCE(NULLIF(CONCAT_WS(' ', e.nombrePila, e.primApell, e.segApell), ''),
                'Sin asignar') AS barista
FROM merma m
INNER JOIN insumo i ON m.insumo = i.codigo
INNER JOIN unidad_medida u ON i.unidad = u.codigo
INNER JOIN tipo_merma tm ON m.tipo = tm.codigo
LEFT JOIN empleado e ON m.idEmpleado = e.num
WHERE m.fecha >= DATE_SUB(CURDATE(), INTERVAL 7 DAY)
ORDER BY m.fecha DESC, m.codigo DESC;

SELECT m.codigo,
       DATE_FORMAT(m.fecha, '%d/%m/%Y') AS fecha,
       i.codigo AS insumo_codigo,
       i.nombre AS insumo,
       CONCAT(m.cantidad, ' ', u.abreviatura) AS cantidad,
       tm.nombre AS tipo_merma,
       m.motivo,
       COALESCE(NULLIF(CONCAT_WS(' ', e.nombrePila, e.primApell, e.segApell), ''),
                'Sin asignar') AS barista
FROM merma m
INNER JOIN insumo i ON m.insumo = i.codigo
INNER JOIN unidad_medida u ON i.unidad = u.codigo
INNER JOIN tipo_merma tm ON m.tipo = tm.codigo
LEFT JOIN empleado e ON m.idEmpleado = e.num
WHERE m.codigo = %s;

SELECT e.num AS id,
       CONCAT_WS(' ', e.nombrePila, e.primApell, e.segApell) AS barista,
       COUNT(m.codigo) AS mermas,
       COALESCE(MAX(DATE_FORMAT(m.fecha, '%d/%m/%Y')), 'Sin registros') AS ultima_merma
FROM empleado e
LEFT JOIN merma m ON m.idEmpleado = e.num
WHERE e.rol = 'BARS'
GROUP BY e.num, e.nombrePila, e.primApell, e.segApell
ORDER BY mermas DESC, e.num;

SELECT m.codigo AS folio,
       DATE_FORMAT(m.fecha, '%d/%m/%Y') AS fecha,
       i.codigo AS insumo_codigo,
       i.nombre AS insumo,
       CONCAT(m.cantidad, ' ', u.abreviatura) AS cantidad,
       tm.nombre AS tipo_merma,
       m.motivo
FROM merma m
INNER JOIN empleado e ON m.idEmpleado = e.num
INNER JOIN insumo i ON m.insumo = i.codigo
INNER JOIN unidad_medida u ON i.unidad = u.codigo
INNER JOIN tipo_merma tm ON m.tipo = tm.codigo
WHERE m.idEmpleado = %s AND e.rol = 'BARS'
ORDER BY m.fecha DESC, m.codigo DESC;

SELECT m.codigo,
       DATE_FORMAT(m.fecha, '%d/%m/%Y') AS fecha,
       i.codigo AS insumo_codigo,
       i.nombre AS insumo,
       CONCAT(m.cantidad, ' ', u.abreviatura) AS cantidad,
       tm.nombre AS tipo_merma,
       m.motivo,
       COALESCE(NULLIF(CONCAT_WS(' ', e.nombrePila, e.primApell, e.segApell), ''),
                'Sin asignar') AS barista
FROM merma m
INNER JOIN insumo i ON m.insumo = i.codigo
INNER JOIN unidad_medida u ON i.unidad = u.codigo
INNER JOIN tipo_merma tm ON m.tipo = tm.codigo
LEFT JOIN empleado e ON m.idEmpleado = e.num
WHERE MONTH(m.fecha) = %s AND YEAR(m.fecha) = %s
ORDER BY m.fecha DESC, m.codigo DESC;