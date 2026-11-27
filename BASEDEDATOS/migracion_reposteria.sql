-- Registra reposteria comprada como producto terminado.
-- Cada venta consume 1 pieza del inventario; el stock inicial se conserva si ya existe.

INSERT INTO categoria_insumo (codigo, nombre) VALUES
('REPS', 'Repostería terminada')
ON DUPLICATE KEY UPDATE nombre = VALUES(nombre);

INSERT INTO unidad_medida (codigo, nombre, abreviatura) VALUES
('PIEZ', 'Pieza', 'pza')
ON DUPLICATE KEY UPDATE nombre = VALUES(nombre), abreviatura = VALUES(abreviatura);

INSERT INTO insumo
    (codigo, nombre, stockActual, stockMin, seccion, estante, categoria, unidad)
VALUES
    ('PTCHOC', 'Pastel de Chocolate listo para venta', 0.00, 0.00, 1, 4, 'REPS', 'PIEZ'),
    ('PTZAN', 'Pastel de Zanahoria listo para venta', 0.00, 0.00, 1, 4, 'REPS', 'PIEZ'),
    ('GLCHOC', 'Galleta Chispas Choc lista para venta', 0.00, 0.00, 1, 4, 'REPS', 'PIEZ'),
    ('GLAVEN', 'Galleta de Avena lista para venta', 0.00, 0.00, 1, 4, 'REPS', 'PIEZ'),
    ('PTREDV', 'Pastel Red Velvet listo para venta', 0.00, 0.00, 1, 4, 'REPS', 'PIEZ'),
    ('GLNUEZ', 'Galleta Nuez Choco lista para venta', 0.00, 0.00, 1, 4, 'REPS', 'PIEZ')
ON DUPLICATE KEY UPDATE
    nombre = VALUES(nombre),
    categoria = VALUES(categoria),
    unidad = VALUES(unidad);

INSERT INTO receta (codigo, producto) VALUES
    ('RPCH', 'PCHO'),
    ('RPZN', 'PZAN'),
    ('RGCH', 'GCHO'),
    ('RGAV', 'GAVE'),
    ('RPRL', 'PRLC'),
    ('RGNU', 'GNUT')
ON DUPLICATE KEY UPDATE producto = VALUES(producto);

INSERT INTO rec_insum (insumo, receta, cantidad) VALUES
    ('PTCHOC', 'RPCH', 1.00),
    ('PTZAN', 'RPZN', 1.00),
    ('GLCHOC', 'RGCH', 1.00),
    ('GLAVEN', 'RGAV', 1.00),
    ('PTREDV', 'RPRL', 1.00),
    ('GLNUEZ', 'RGNU', 1.00)
ON DUPLICATE KEY UPDATE cantidad = VALUES(cantidad);

-- Mantiene el estatus alineado con el stock real de cada producto.
UPDATE producto p
SET p.estatus = CASE
    WHEN EXISTS (
        SELECT 1
        FROM receta r
        INNER JOIN rec_insum ri ON ri.receta = r.codigo
        INNER JOIN insumo i ON i.codigo = ri.insumo
        WHERE r.producto = p.codigo
          AND i.stockActual < ri.cantidad
    ) THEN 2
    ELSE 1
END
WHERE p.codigo IN ('PCHO', 'PZAN', 'GCHO', 'GAVE', 'PRLC', 'GNUT');
