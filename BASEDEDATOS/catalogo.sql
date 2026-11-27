-- Active: 1792597882538@@127.0.0.1@3306@bd_coffeelytics
-- ROL
INSERT INTO ROL (codigo, nombre) VALUES
('ADMN', 'Administrador'),
('BARS', 'Barista'),
('ALMC', 'Almacenista'),
('CAJR', 'Cajero');

-- ESTATUS
INSERT INTO ESTATUS_PRODUCTO (codigo, nombre) VALUES
('ACTV', 'Activo'),
('INAC', 'Inactivo');

-- TIPO_MERMA
INSERT INTO TIPO_MERMA (codigo, nombre) VALUES
('CADUC', 'Caducidad vencida'),
('DERRM', 'Derrame o accidente en barra'),
('EMPAQ', 'Empaque dañado o roto'),
('ERROR', 'Error de preparación en bebida');

-- CATEGORIA_INSUMO
INSERT INTO CATEGORIA_INSUMO (codigo, nombre) VALUES
('CAFE', 'Café y Té'),
('LACT', 'Lácteos y Bebidas Vegetales'),
('JARB', 'Jarabes, Polvos y Endulzantes'),
('DESE', 'Desechables y Empaques'),
('AGUA', 'Hielo y Agua Purificada'),
('MESA', 'Consumibles de Mesa'),
('REPS', 'Repostería terminada');

INSERT INTO categoria_producto VALUES
('CAFE', 'Cafés'),
('PAST', 'Rebanadas de Pastel'),
('GALL', 'Galletas'),
('FEST', 'Bebidas Festivas');
-- METODO_PAGO
INSERT INTO METODO_PAGO (codigo, descripcion) VALUES
('EFEC', 'Efectivo'),
('TDEB', 'Tarjeta de Débito'),
('TCRE', 'Tarjeta de Crédito'),
('TRAN', 'Transferencia Electrónica');

INSERT INTO UNIDAD_MEDIDA (codigo, nombre, abreviatura) VALUES
('KILO', 'Kilogramo', 'kg'),
('LITR', 'Litro', 'L'),
('BOTE', 'Botella', 'bot'),
('PAQU', 'Paquete', 'paq'),
('CAJA', 'Caja', 'cja'),
('BOLS', 'Bolsa', 'bls'),
('GARF', 'Garrafón', 'grf'),
('PIEZ', 'Pieza', 'pza');

INSERT INTO ESTANTE (codigo, capacidad, secciones) VALUES
(1, 10, 4),
(2, 12, 5),
(3, 8, 3),
(4, 15, 4);
-- PROVEEDOR
INSERT INTO PROVEEDOR (codigo, nombre, dirCalle, dirColonia, dirNumero, telefono, ciudad) VALUES
('CSOL', 'Coffee Solutions', 'Dinamarca', 'Juárez', '85', '5552082851', 'Ciudad de México'),
('BARI', 'The Barista Shop', 'Av. Chapultepec', 'Centro Área 4', '67 PB', '5550351044', 'Ciudad de México'),
('EX77', 'Excelso77 Coffee Lab', 'Prol. Paseo de los Héroes', '20 de Noviembre', '3565 L-38/39', '6646862202', 'Tijuana'),
('BOAT', 'Café Boato', 'Av. Herminio Chavarría', 'Santa María Aztahuacán', '37-A', '5536163616', 'Ciudad de México'),
('BERE', 'Beresa Janitor Supply', 'Calz. Ing. Juan Ojeda Robles', 'Buena Vista', '798', '6646241925', 'Tijuana'),
('SMRF', 'Smart & Final', 'Calle Segunda', 'Zona Centro', '7002', '6646859133', 'Tijuana'),
('CFNO', 'Caffenio', 'Av. Vía Rápida Oriente', 'Chamizal', '13660', '8002233646', 'Tijuana'),
('BUHO', 'Hielo Búho Nival', 'Calle 19', 'Libertad', '1063', '6633324736', 'Tijuana'),
('CNCA', 'Cuenca Azul Purificadora', 'Blvd. Díaz Ordaz', 'Las Palmas', '13251 L-F4', '6644759663', 'Tijuana'),
('KTCH', 'Kitchen Experts GDL', 'Av. Tepeyac', 'Prados Tepeyac', '447-2', '3340000228', 'Zapopan'),
('ETRU', 'Café Etrusca Monterrey', 'Av. José Vasconcelos', 'Casco Urbano', '501 L-1', '8183381383', 'San Pedro Garza G.'),
('RODA', 'Grupo Rodalo', 'Prol. Paseo de Amsterdam', 'Ejido Los Olvera', '50 L-5', '4422648562', 'Corregidora'),
('PCUP', 'PrintCup México', 'Calle La Iglesia', 'Ferrocarrilera', '22', '6622848001', 'Hermosillo'),
('BETT', 'Betty''s Pastelería Fina', 'Abasolo', 'Independencia', '398-A', '6646383757', 'Tijuana');

-- INSUMO
INSERT INTO INSUMO (codigo, nombre, stockActual, stockMin, seccion, estante, categoria, unidad) VALUES
('GRNOSC', 'Café en grano tostado oscuro', 24.00, 8, 1, 1, 'CAFE', 'KILO'),
('CAFAME', 'Café americano molido', 18.00, 6, 1, 1, 'CAFE', 'KILO'),
('MATCHA', 'Té matcha ceremonial en polvo', 10.00, 3, 2, 1, 'CAFE', 'BOLS'),
('TISFRU', 'Tisana frutal frutos rojos', 12.00, 4, 2, 1, 'CAFE', 'BOLS'),
('LECENT', 'Leche entera UHT tetrapak', 48.00, 18, 1, 2, 'LACT', 'LITR'),
('LECDES', 'Leche deslactosada UHT 1L', 36.00, 12, 1, 2, 'LACT', 'LITR'),
('ALMEND', 'Bebida vegetal de almendra 1L', 24.00, 8, 2, 2, 'LACT', 'LITR'),
('JRVAIN', 'Jarabe sabor vainilla 750ml', 14.00, 4, 3, 1, 'JARB', 'BOTE'),
('JRCARA', 'Jarabe sabor caramelo 750ml', 12.00, 4, 3, 1, 'JARB', 'BOTE'),
('FRAPPE', 'Base en polvo para frappé neutro 1.5kg', 15.00, 5, 4, 1, 'JARB', 'BOLS'),
('VAS12O', 'Vaso cartón térmico 12oz (paq 50 pzas)', 40.00, 15, 1, 4, 'DESE', 'PAQU'),
('TAP12O', 'Tapa plástica viajera 12oz (paq 100 pzas)', 30.00, 10, 2, 4, 'DESE', 'PAQU'),
('SOBRZU', 'Caja sobres azúcar estándar (2000 pzas)', 8.00, 3, 3, 4, 'MESA', 'CAJA'),
('SOBSPL', 'Caja sobres endulzante Splenda (1000 pzas)', 6.00, 2, 3, 4, 'MESA', 'CAJA'),
('SERVIL', 'Caja servilletas interdoble (3000 pzas)', 10.00, 4, 4, 4, 'MESA', 'CAJA'),
('AGITMA', 'Caja agitadores madera 14cm (1000 pzas)', 7.00, 2, 4, 4, 'MESA', 'CAJA'),
('HIEL5K', 'Bolsa hielo purificado en cubos 5kg', 20.00, 8, 1, 3, 'AGUA', 'BOLS'),
('AGUA20', 'Garrafón agua purificada 20L', 14.00, 5, 2, 3, 'AGUA', 'GARF');


INSERT INTO EMPLEADO (num, nombrePila, primApell, segApell, RFC, telefono, correo, rol) VALUES
(1, 'Guillermo', 'Landaverde', 'Montoya', 'LAMG980512H1', '6641234501', 'admin@coffeelytics.com', 'ADMN'),
(2, 'Ismael', 'Ramírez', 'López', 'RALI000824H2', '6641234502', 'barista@coffeelytics.com', 'BARS'),
(3, 'Sofía', 'Mendoza', 'Cruz', 'MECS011103M3', '6641234503', 'sofia.mendoza@coffeelytics.com', 'CAJR'),
(4, 'Carlos', 'Herrera', 'Vega', 'HEVC990215H4', '6641234504', 'carlos.herrera@coffeelytics.com', 'ALMC');
-- CONSUMIBLE_MESA
INSERT INTO CONSUMIBLE_MESA (codigo, nombre, empleado) VALUES
('MESA1', 'Barra Autoservicio Principal', 2),
('AZUCA', 'Azúcar estándar en sobres', 1),
('SPLEN', 'Endulzante Splenda en sobres', 1),
('SERVI', 'Servilletas', 2),
('AGITA', 'Agitadores de madera', 2);

-- INSUM_MESA
INSERT INTO con_insum (insumo, mesa, cantidad) VALUES
('SOBRZU', 'AZUCA', 1.00),
('SOBSPL', 'SPLEN', 1.00),
('SERVIL', 'SERVI', 1.00),
('AGITMA', 'AGITA', 1.00);

-- VENTA
INSERT INTO VENTA (codigo, fecha, total, metodoPago, empleado) VALUES
(1, '2026-11-09', 48.60, 'EFEC', 2),
(2, '2026-11-09', 70.20, 'TDEB', 2),
(3, '2026-11-10', 64.80, 'TRAN', 2),
(4, '2026-11-11', 81.00, 'EFEC', 2),
(5, '2026-11-12', 37.80, 'EFEC', 3),
(6, '2026-11-13', 118.80, 'TCRE', 3),
(7, '2026-11-14', 48.60, 'EFEC', 2),
(8, '2026-11-16', 70.20, 'TRAN', 3),
(9, '2026-11-17', 135.00, 'TDEB', 2),
(10, '2026-11-18', 302.40, 'EFEC', 2);

-- PROD_VENTA
INSERT INTO PROD_VENTA (venta, producto, cantidad, precioUnitarioVenta, subtotal, totalIVA, total) VALUES
(1, 'AMER', 1, 45.00, 45.00, 3.60, 48.60),
(2, 'LATT', 1, 65.00, 65.00, 5.20, 70.20),
(3, 'CAPU', 1, 60.00, 60.00, 4.80, 64.80),
(4, 'MTCH', 1, 75.00, 75.00, 6.00, 81.00),
(5, 'TISA', 1, 35.00, 35.00, 2.80, 37.80),
(6, 'AMER', 1, 45.00, 45.00, 3.60, 48.60),
(6, 'LATT', 1, 65.00, 65.00, 5.20, 70.20),
(7, 'AMER', 1, 45.00, 45.00, 3.60, 48.60),
(8, 'LATT', 1, 65.00, 65.00, 5.20, 70.20),
(9, 'LATT', 1, 65.00, 65.00, 5.20, 70.20),
(9, 'CAPU', 1, 60.00, 60.00, 4.80, 64.80),
(10, 'AMER', 1, 45.00, 45.00, 3.60, 48.60),
(10, 'LATT', 1, 65.00, 65.00, 5.20, 70.20),
(10, 'CAPU', 1, 60.00, 60.00, 4.80, 64.80),
(10, 'MTCH', 1, 75.00, 75.00, 6.00, 81.00),
(10, 'TISA', 1, 35.00, 35.00, 2.80, 37.80);

-- COMPRA
INSERT INTO COMPRA (codigo, fecha, total, proveedor, metodoPago, empleado) VALUES
(1, '2026-10-27', 6706.80, 'EX77', 'TRAN', 1),
(2, '2026-10-28', 4017.60, 'CFNO', 'TDEB', 1),
(3, '2026-10-29', 2339.28, 'SMRF', 'TCRE', 1),
(4, '2026-10-30', 10416.80, 'BARI', 'TRAN', 1),
(5, '2026-11-02', 3480.00, 'PCUP', 'TRAN', 1),
(6, '2026-11-03', 596.16, 'BUHO', 'EFEC', 1),
(7, '2026-11-05', 2373.84, 'BERE', 'TDEB', 1),
(8, '2026-11-06', 362.88, 'CNCA', 'EFEC', 1),
(9, '2026-11-09', 4454.40, 'CSOL', 'TRAN', 1),
(10, '2026-11-10', 2468.88, 'CFNO', 'TDEB', 1),
(11, '2026-11-12', 2978.88, 'ETRU', 'TCRE', 1),
(12, '2026-11-16', 5589.00, 'EX77', 'TRAN', 1);

-- INSUM_COM
INSERT INTO INSUM_COM (compra, insumo, cantidad, precioUnitarioCom, subtotal, totalIVA, total) VALUES
(1, 'GRNOSC', 18.00, 345.00, 6210.00, 496.80, 6706.80),
(2, 'CAFAME', 15.00, 248.00, 3720.00, 297.60, 4017.60),
(3, 'LECENT', 36.00, 24.50, 882.00, 70.56, 952.56),
(3, 'LECDES', 24.00, 27.50, 660.00, 52.80, 712.80),
(3, 'ALMEND', 12.00, 52.00, 624.00, 49.92, 673.92),
(4, 'MATCHA', 4.00, 1180.00, 4720.00, 755.20, 5475.20),
(4, 'JRVAIN', 6.00, 350.00, 2100.00, 336.00, 2436.00),
(4, 'JRCARA', 6.00, 360.00, 2160.00, 345.60, 2505.60),
(5, 'VAS12O', 20.00, 96.00, 1920.00, 307.20, 2227.20),
(5, 'TAP12O', 15.00, 72.00, 1080.00, 172.80, 1252.80),
(6, 'HIEL5K', 12.00, 46.00, 552.00, 44.16, 596.16),
(7, 'SERVIL', 4.00, 389.00, 1556.00, 124.48, 1680.48),
(7, 'AGITMA', 3.00, 214.00, 642.00, 51.36, 693.36),
(8, 'AGUA20', 8.00, 42.00, 336.00, 26.88, 362.88),
(9, 'FRAPPE', 6.00, 640.00, 3840.00, 614.40, 4454.40),
(10, 'SOBRZU', 3.00, 372.00, 1116.00, 89.28, 1205.28),
(10, 'SOBSPL', 2.00, 585.00, 1170.00, 93.60, 1263.60),
(11, 'TISFRU', 6.00, 428.00, 2568.00, 410.88, 2978.88),
(12, 'GRNOSC', 15.00, 345.00, 5175.00, 414.00, 5589.00);

-- FACTURA
INSERT INTO FACTURA (codigo, monto, folioFiscal, fecha, compra) VALUES
('FCOMP001', 6706.80, 'F38B2FFC-80A4-4F5A-91C9-BC701E7EA419', '2026-10-28', 1),
('FCOMP002', 4017.60, '1A466884-F3F4-4249-9C28-FF90A5AEC797', '2026-10-28', 2),
('FCOMP003', 2339.28, '8E7AA6E9-9F19-4504-99DD-251DE5121482', '2026-10-29', 3),
('FCOMP004', 10416.80, 'D7A7A3CC-8C3D-4F16-9293-DE8FC88B2875', '2026-10-31', 4),
('FCOMP005', 3480.00, 'C0433CBD-7DAB-4929-84A3-34BFC6CD75E9', '2026-11-03', 5),
('FCOMP006', 596.16, '9D3C7DEC-00A6-4F93-BD6C-51E370EB9A0A', '2026-11-03', 6),
('FCOMP007', 2373.84, '1919E93A-D117-45AD-8988-93101C593AF5', '2026-11-05', 7),
('FCOMP008', 362.88, 'AF67D461-E416-4207-9094-499602F0EE99', '2026-11-06', 8),
('FCOMP009', 4454.40, '65B00A2D-35D1-4880-9071-950EADEC6F11', '2026-11-09', 9),
('FCOMP010', 2468.88, 'EDE7BD0C-FFB8-4309-BADB-890859001AC9', '2026-11-10', 10),
('FCOMP011', 2978.88, 'BEF7E268-FFE9-46AB-A058-1CCACE1D62E0', '2026-11-13', 11),
('FCOMP012', 5589.00, '57241955-B91D-4DD9-9389-B372A341738C', '2026-11-16', 12);

-- MERMA
INSERT INTO MERMA (codigo, motivo, fecha, cantidad, tipo, insumo) VALUES
(1, 'Leche entera UHT con fecha de caducidad vencida detectada en almacén', '2026-11-03', 6, 'CADUC', 'LECENT'),
(2, 'Derrame de leche deslactosada al preparar bebidas en barra', '2026-11-04', 2, 'DERRM', 'LECDES'),
(3, 'Paquete de vasos de cartón dañado por humedad y con empaque roto', '2026-11-06', 1, 'EMPAQ', 'VAS12O'),
(4, 'Café molido desperdiciado por error en la preparación de un café americano', '2026-11-07', 0.25, 'ERROR', 'CAFAME'),
(5, 'Botella de jarabe de vainilla caída y rota en barra', '2026-11-10', 1, 'DERRM', 'JRVAIN'),
(6, 'Bebida vegetal de almendra vencida detectada en almacén', '2026-11-11', 3, 'CADUC', 'ALMEND'),
(7, 'Garrafón de agua purificada con fuga por tapa dañada', '2026-11-13', 1, 'EMPAQ', 'AGUA20'),
(8, 'Base en polvo para frappé desperdiciada por error en la preparación', '2026-11-14', 0.3, 'ERROR', 'FRAPPE');

-- 1. Productos base (coinciden con los precios de PROD_VENTA y estatus ACTV)
INSERT INTO PRODUCTO (codigo, nombre, precio, categoria, estatus) VALUES
('AMER', 'Café Americano', 45.00, 'CAFE', 1),
('LATT', 'Café Latte', 65.00, 'CAFE', 1),
('CAPU', 'Capuchino', 60.00, 'CAFE', 1),
('LVAI', 'Latte Vainilla', 70.00, 'CAFE', 1),
('CARM', 'Caramel Macchiato', 72.00, 'CAFE', 1),
('LALM', 'Latte de Almendra', 75.00, 'CAFE', 1),
('LDES', 'Latte Deslactosado', 68.00, 'CAFE', 1),
('MTCH', 'Matcha Latte', 75.00, 'FEST', 1),
('TISA', 'Tisana Frutos Rojos', 35.00, 'FEST', 1),
('FRAP', 'Frappé Clásico', 78.00, 'FEST', 1),
('FRMO', 'Frappé Mocha', 82.00, 'FEST', 2),
('PCHO', 'Pastel de Chocolate', 65.00, 'PAST', 1),
('PZAN', 'Pastel de Zanahoria', 62.00, 'PAST', 1),
('GCHO', 'Galleta Chispas Choc', 30.00, 'GALL', 1),
('GAVE', 'Galleta de Avena', 28.00, 'GALL', 1);
-- 2. Recetas vinculadas a cada producto (máx. 4 caracteres)
INSERT INTO RECETA (codigo, producto) VALUES
('RAME', 'AMER'),
('RLAT', 'LATT'),
('RCAP', 'CAPU'),
('RMTC', 'MTCH'),
('RTIS', 'TISA');

-- 3. Insumos por receta vinculados a INSUMO y RECETA
INSERT INTO REC_INSUM (insumo, receta, cantidad) VALUES
-- Receta RAME -> AMER (Café Americano)
('CAFAME', 'RAME', 0.02),
('AGUA20', 'RAME', 0.02),
('VAS12O', 'RAME', 0.02),
('TAP12O', 'RAME', 0.01),
('GRNOSC', 'RLAT', 0.02),
('LECENT', 'RLAT', 0.25),
('VAS12O', 'RLAT', 0.02),
('TAP12O', 'RLAT', 0.01),
('GRNOSC', 'RCAP', 0.02),
('LECENT', 'RCAP', 0.18),
('VAS12O', 'RCAP', 0.02),
('TAP12O', 'RCAP', 0.01),
('MATCHA', 'RMTC', 0.01),
('LECENT', 'RMTC', 0.25),
('VAS12O', 'RMTC', 0.02),
('TAP12O', 'RMTC', 0.01),
('TISFRU', 'RTIS', 0.02),
('AGUA20', 'RTIS', 0.02),
('VAS12O', 'RTIS', 0.02),
('TAP12O', 'RTIS', 0.01);

INSERT INTO INSUMO (codigo, nombre, stockActual, stockMin, seccion, estante, categoria, unidad) VALUES
('ESPRES', 'Café espresso molido medio', 16.00, 5, 3, 1, 'CAFE', 'KILO'),
('CHOCPO', 'Cocoa en polvo sin azúcar 1kg', 11.00, 4, 4, 1, 'JARB', 'BOLS'),
('AVALIT', 'Bebida vegetal de avena 1L', 22.00, 8, 3, 2, 'LACT', 'LITR'),
('CREBAT', 'Crema batida spray 500g', 14.00, 5, 4, 2, 'LACT', 'BOTE'),
('JRMOCH', 'Jarabe sabor moka 750ml', 10.00, 3, 2, 1, 'JARB', 'BOTE'),
('VAS16O', 'Vaso cartón térmico 16oz (paq 50 pzas)', 28.00, 10, 1, 4, 'DESE', 'PAQU'),
('POPOTE', 'Paquete popotes biodegradables (250 pzas)', 18.00, 6, 2, 4, 'DESE', 'PAQU'),
('CANELA', 'Canela molida repostería 500g', 9.00, 3, 3, 3, 'MESA', 'BOLS'),
-- Repostería comprada terminada: el stock inicial queda en cero hasta capturar el conteo real.
('PTCHOC', 'Pastel de Chocolate listo para venta', 0.00, 0.00, 1, 4, 'REPS', 'PIEZ'),
('PTZAN', 'Pastel de Zanahoria listo para venta', 0.00, 0.00, 1, 4, 'REPS', 'PIEZ'),
('GLCHOC', 'Galleta Chispas Choc lista para venta', 0.00, 0.00, 1, 4, 'REPS', 'PIEZ'),
('GLAVEN', 'Galleta de Avena lista para venta', 0.00, 0.00, 1, 4, 'REPS', 'PIEZ'),
('PTREDV', 'Pastel Red Velvet listo para venta', 0.00, 0.00, 1, 4, 'REPS', 'PIEZ'),
('GLNUEZ', 'Galleta Nuez Choco lista para venta', 0.00, 0.00, 1, 4, 'REPS', 'PIEZ');

-- Nuevos productos
INSERT INTO PRODUCTO (codigo, nombre, precio, categoria, estatus) VALUES
('ESPR', 'Espresso Doble', 42.00, 'CAFE', '1'),
('MOCH', 'Moka Caliente', 74.00, 'CAFE', '1'),
('LAVE', 'Latte de Avena', 75.00, 'CAFE', '1'),
('FCRE', 'Frappé Crema', 80.00, 'FEST', '1'),
('PRLC', 'Pastel Red Velvet', 68.00, 'PAST', '1'),
('GNUT', 'Galleta Nuez Choco', 32.00, 'GALL', '1');

-- Nuevas recetas de bebidas
INSERT INTO RECETA (codigo, producto) VALUES
('RPCH', 'PCHO'),
('RPZN', 'PZAN'),
('RGCH', 'GCHO'),
('RGAV', 'GAVE'),
('RPRL', 'PRLC'),
('RGNU', 'GNUT');

-- Nuevos insumos por receta
INSERT INTO REC_INSUM (insumo, receta, cantidad) VALUES
('ESPRES', 'RESP', 0.02),
('VAS12O', 'RESP', 0.02),
('TAP12O', 'RESP', 0.01),
('ESPRES', 'RMOC', 0.02),
('LECENT', 'RMOC', 0.22),
('JRMOCH', 'RMOC', 0.03),
('CHOCPO', 'RMOC', 0.01),
('VAS12O', 'RMOC', 0.02),
('TAP12O', 'RMOC', 0.01),
('ESPRES', 'RLAV', 0.02),
('AVALIT', 'RLAV', 0.25),
('VAS12O', 'RLAV', 0.02),
('TAP12O', 'RLAV', 0.01),
('FRAPPE', 'RFCR', 0.05),
('LECENT', 'RFCR', 0.15),
('HIEL5K', 'RFCR', 0.04),
('CREBAT', 'RFCR', 0.02),
('VAS16O', 'RFCR', 0.02),
('POPOTE', 'RFCR', 0.01),

-- Cada producto de repostería comprado consume una pieza del inventario al venderse.
INSERT INTO REC_INSUM (insumo, receta, cantidad)
('PTCHOC', 'RPCH', 1.00),
('PTZAN', 'RPZN', 1.00),
('GLCHOC', 'RGCH', 1.00),
('GLAVEN', 'RGAV', 1.00),
('PTREDV', 'RPRL', 1.00),
('GLNUEZ', 'RGNU', 1.00);

INSERT INTO MERMA (codigo, motivo, fecha, cantidad, tipo, insumo) VALUES
(9, 'Lata de crema batida spray con fecha de caducidad vencida en refrigeración', '2026-11-16', 2.00, 'CADUC', 'CREBAT'),
(10, 'Derrame de bebida vegetal de avena al vaporizar en barra', '2026-11-17', 1.50, 'DERRM', 'AVALIT'),
(11, 'Paquete de vasos térmicos 16oz aplastado y con empaque roto en almacén', '2026-11-19', 1.00, 'EMPAQ', 'VAS16O'),
(12, 'Café espresso molido desperdiciado al calibrar molino en turno matutino', '2026-11-21', 0.35, 'ERROR', 'ESPRES'),
(13, 'Botella de jarabe sabor moka rota por caída accidental en estación de bebidas', '2026-11-23', 1.00, 'DERRM', 'JRMOCH'),
(14, 'Bolsa de cocoa en polvo con sellado dañado por humedad', '2026-11-25', 0.50, 'EMPAQ', 'CHOCPO'),
(15, 'Leche entera UHT vencida detectada durante inventario de cierre de mes', '2026-11-27', 4.00, 'CADUC', 'LECENT'),
(16, 'Té matcha ceremonial desperdiciado por error en dosificación de bebida', '2026-11-29', 0.15, 'ERROR', 'MATCHA');

INSERT INTO VENTA (codigo, fecha, total, metodoPago, empleado) VALUES
(11, '2026-10-26', 81.00, 'EFEC', 2),
(12, '2026-10-27', 140.40, 'TDEB', 3),
(13, '2026-10-28', 129.60, 'TRAN', 2),
(14, '2026-10-29', 136.08, 'EFEC', 2),
(15, '2026-10-30', 144.72, 'TCRE', 3),
(16, '2026-10-31', 201.96, 'EFEC', 2),
(17, '2026-11-02', 171.72, 'TDEB', 2),
(18, '2026-11-04', 116.64, 'EFEC', 3),
(19, '2026-11-06', 160.92, 'TRAN', 2),
(20, '2026-11-08', 159.84, 'TCRE', 3),
(21, '2026-11-20', 111.24, 'EFEC', 2),
(22, '2026-11-22', 223.56, 'TDEB', 3),
(23, '2026-11-25', 237.60, 'TRAN', 2),
(24, '2026-11-28', 250.56, 'EFEC', 3);

INSERT INTO PROD_VENTA (venta, producto, cantidad, precioUnitarioVenta, subtotal, totalIVA, total) VALUES
(11, 'AMER', 1, 45.00, 45.00, 3.60, 48.60),
(11, 'GCHO', 1, 30.00, 30.00, 2.40, 32.40),
(12, 'LATT', 1, 65.00, 65.00, 5.20, 70.20),
(12, 'PCHO', 1, 65.00, 65.00, 5.20, 70.20),
(13, 'CAPU', 2, 60.00, 120.00, 9.60, 129.60),
(14, 'LVAI', 1, 70.00, 70.00, 5.60, 75.60),
(14, 'GAVE', 2, 28.00, 56.00, 4.48, 60.48),
(15, 'CARM', 1, 72.00, 72.00, 5.76, 77.76),
(15, 'PZAN', 1, 62.00, 62.00, 4.96, 66.96),
(16, 'AMER', 2, 45.00, 90.00, 7.20, 97.20),
(16, 'LATT', 1, 65.00, 65.00, 5.20, 70.20),
(16, 'GNUT', 1, 32.00, 32.00, 2.56, 34.56),
(17, 'ESPR', 2, 42.00, 84.00, 6.72, 90.72),
(17, 'LAVE', 1, 75.00, 75.00, 6.00, 81.00),
(18, 'FRAP', 1, 78.00, 78.00, 6.24, 84.24),
(18, 'GCHO', 1, 30.00, 30.00, 2.40, 32.40),
(19, 'MOCH', 1, 74.00, 74.00, 5.92, 79.92),
(19, 'LALM', 1, 75.00, 75.00, 6.00, 81.00),
(20, 'FCRE', 1, 80.00, 80.00, 6.40, 86.40),
(20, 'PRLC', 1, 68.00, 68.00, 5.44, 73.44),
(21, 'LDES', 1, 68.00, 68.00, 5.44, 73.44),
(21, 'TISA', 1, 35.00, 35.00, 2.80, 37.80),
(22, 'LVAI', 1, 70.00, 70.00, 5.60, 75.60),
(22, 'CARM', 1, 72.00, 72.00, 5.76, 77.76),
(22, 'PCHO', 1, 65.00, 65.00, 5.20, 70.20),
(23, 'FRAP', 2, 78.00, 156.00, 12.48, 168.48),
(23, 'GNUT', 2, 32.00, 64.00, 5.12, 69.12),
(24, 'LATT', 2, 65.00, 130.00, 10.40, 140.40),
(24, 'MOCH', 1, 74.00, 74.00, 5.92, 79.92),
(24, 'GAVE', 1, 28.00, 28.00, 2.24, 30.24);

INSERT INTO EMPLEADO (num, nombrePila, primApell, segApell, RFC, telefono, correo, rol) VALUES
(5, 'Valeria', 'Navarro', 'Sánchez', 'NASV970918M5', '6641234505', 'valeria.navarro@coffeelytics.com', 'ADMN'),
(6, 'Diego', 'Castillo', 'Ríos', 'CARD960411H6', '6641234506', 'diego.castillo@coffeelytics.com', 'ADMN'),
(7, 'Fernanda', 'Ortega', 'Jiménez', 'OEJF991207M7', '6641234507', 'fernanda.ortega@coffeelytics.com', 'ADMN');

INSERT INTO EMPLEADO (num, nombrePila, primApell, segApell, RFC, telefono, correo, rol) VALUES
(8, 'Mateo', 'Guzmán', 'Flores', 'GUGM010319H8', '6641234508', 'mateo.guzman@coffeelytics.com', 'BARS'),
(9, 'Camila', 'Reyes', 'Morales', 'REMC020725M9', '6641234509', 'camila.reyes@coffeelytics.com', 'BARS'),
(10, 'Sebastián', 'Vargas', 'Silva', 'VASO001114H0', '6641234510', 'sebastian.vargas@coffeelytics.com', 'BARS');

INSERT INTO INSUMO (codigo, nombre, stockActual, stockMin, seccion, estante, categoria, unidad) VALUES
('SOBSTE', 'Caja sobres azúcar stevia (1000 pzas)', 6.00, 2.00, 3, 4, 'MESA', 'CAJA'),
('TOALLH', 'Paquete toallas húmedas (200 pzas)', 9.00, 3.00, 4, 4, 'MESA', 'PAQU'),
('AZUMAS', 'Bolsa azúcar mascabado 2kg', 10.00, 3.00, 5, 2, 'MESA', 'BOLS');

INSERT INTO CONSUMIBLE_MESA (codigo, nombre, empleado) VALUES
('STEVI', 'Endulzante stevia en sobres', 1),
('TOALL', 'Toallas húmedas para mesa', 2),
('MASCA', 'Azúcar mascabado', 8);

INSERT INTO con_insum (insumo, mesa, cantidad) VALUES
('SOBSTE', 'STEVI', 1.00),
('TOALLH', 'TOALL', 1.00),
('AZUMAS', 'MASCA', 1.00);

-- =========================================================================
-- 1. CABECERA DE VENTAS (30 ventas: codigos 27 al 56)
-- =========================================================================
INSERT INTO venta (codigo, fecha, nombreCliente, total, metodoPago, empleado) VALUES
-- 10 ventas para Barista 8 (Mateo Guzmán)
(27, '2026-10-03 08:30:00', 'Mostrador', 48.60, 'EFEC', 8),
(28, '2026-10-07 10:15:00', 'Mostrador', 135.00, 'TDEB', 8),
(29, '2026-10-12 16:40:00', 'Mostrador', 64.80, 'TRAN', 8),
(30, '2026-10-18 09:20:00', 'Mostrador', 113.40, 'EFEC', 8),
(31, '2026-10-25 13:10:00', 'Mostrador', 81.00, 'TDEB', 8),
(32, '2026-11-02 08:45:00', 'Mostrador', 129.60, 'EFEC', 8),
(33, '2026-11-06 11:30:00', 'Mostrador', 81.00, 'TRAN', 8),
(34, '2026-11-11 17:05:00', 'Mostrador', 145.80, 'TDEB', 8),
(35, '2026-11-16 09:50:00', 'Mostrador', 75.60, 'EFEC', 8),
(36, '2026-11-21 15:25:00', 'Mostrador', 115.56, 'TRAN', 8)

-- 10 ventas para Barista 9 (Camila Reyes)
INSERT INTO venta (codigo, fecha, nombreCliente, total, metodoPago, empleado) VALUES
(37, '2026-10-04 09:00:00', 'Mostrador', 70.20, 'TDEB', 9),
(38, '2026-10-09 12:20:00', 'Mostrador', 97.20, 'EFEC', 9),
(39, '2026-10-14 15:45:00', 'Mostrador', 135.00, 'TRAN', 9),
(40, '2026-10-20 08:15:00', 'Mostrador', 37.80, 'EFEC', 9),
(41, '2026-10-27 14:30:00', 'Mostrador', 118.80, 'TDEB', 9),
(42, '2026-11-03 10:40:00', 'Mostrador', 90.72, 'EFEC', 9),
(43, '2026-11-08 16:10:00', 'Mostrador', 151.20, 'TRAN', 9),
(44, '2026-11-13 09:35:00', 'Mostrador', 64.80, 'EFEC', 9),
(45, '2026-11-18 13:50:00', 'Mostrador', 113.40, 'TDEB', 9),
(46, '2026-11-22 11:15:00', 'Mostrador', 81.00, 'EFEC', 9)

-- 10 ventas para Barista 10 (Sebastián Vargas)
INSERT INTO venta (codigo, fecha, nombreCliente, total, metodoPago, empleado) VALUES
(47, '2026-10-05 10:10:00', 'Mostrador', 81.00, 'EFEC', 10),
(48, '2026-10-10 14:25:00', 'Mostrador', 129.60, 'TDEB', 10),
(49, '2026-10-16 08:55:00', 'Mostrador', 60.48, 'TRAN', 10),
(50, '2026-10-22 17:20:00', 'Mostrador', 162.00, 'EFEC', 10),
(51, '2026-10-29 11:45:00', 'Mostrador', 97.20, 'TDEB', 10),
(52, '2026-11-04 09:15:00', 'Mostrador', 113.40, 'EFEC', 10),
(53, '2026-11-09 15:00:00', 'Mostrador', 75.60, 'TRAN', 10),
(54, '2026-11-14 12:35:00', 'Mostrador', 135.00, 'TDEB', 10),
(55, '2026-11-19 08:40:00', 'Mostrador', 81.00, 'EFEC', 10),
(56, '2026-11-23 16:50:00', 'Mostrador', 118.80, 'TRAN', 10);

-- =========================================================================
-- 2. DETALLE DE PRODUCTOS POR VENTA (Ajusta el nombre de la tabla si difiere)
-- =========================================================================
INSERT INTO prod_venta (venta, producto, cantidad, precioUnitarioVenta, subtotal, totalIVA, total) VALUES
-- Detalle Barista 8 (ventas 27 a 36)
(27, 'AMER', 1, 45.00, 45.00, 3.60, 48.60),
(28, 'CAPU', 1, 60.00, 60.00, 4.80, 64.80),
(28, 'LATT', 1, 65.00, 65.00, 5.20, 70.20),
(29, 'CAPU', 1, 60.00, 60.00, 4.80, 64.80),
(30, 'LATT', 1, 65.00, 65.00, 5.20, 70.20),
(30, 'TISA', 1, 35.00, 35.00, 2.80, 37.80),
(30, 'GCHO', 1, 5.00, 5.00, 0.40, 5.40),
(31, 'MTCH', 1, 75.00, 75.00, 6.00, 81.00),
(32, 'CAPU', 2, 60.00, 120.00, 9.60, 129.60),
(33, 'LAVE', 1, 75.00, 75.00, 6.00, 81.00),
(34, 'LATT', 1, 65.00, 65.00, 5.20, 70.20),
(34, 'LVAI', 1, 70.00, 70.00, 5.60, 75.60),
(35, 'LVAI', 1, 70.00, 70.00, 5.60, 75.60),
(36, 'LATT', 1, 65.00, 65.00, 5.20, 70.20),
(36, 'ESPR', 1, 42.00, 42.00, 3.36, 45.36)

-- Detalle Barista 9 (ventas 37 a 46)
INSERT INTO prod_venta (venta, producto, cantidad, precioUnitarioVenta, subtotal, totalIVA, total) VALUES
(37, 'LATT', 1, 65.00, 65.00, 5.20, 70.20),
(38, 'AMER', 2, 45.00, 90.00, 7.20, 97.20),
(39, 'CAPU', 1, 60.00, 60.00, 4.80, 64.80),
(39, 'LATT', 1, 65.00, 65.00, 5.20, 70.20),
(40, 'TISA', 1, 35.00, 35.00, 2.80, 37.80),
(41, 'MTCH', 1, 75.00, 75.00, 6.00, 81.00),
(41, 'TISA', 1, 35.00, 35.00, 2.80, 37.80),
(42, 'ESPR', 2, 42.00, 84.00, 6.72, 90.72),
(43, 'LVAI', 2, 70.00, 140.00, 11.20, 151.20),
(44, 'CAPU', 1, 60.00, 60.00, 4.80, 64.80),
(45, 'LALM', 1, 75.00, 75.00, 6.00, 81.00),
(45, 'GCHO', 1, 30.00, 30.00, 2.40, 32.40),
(46, 'MTCH', 1, 75.00, 75.00, 6.00, 81.00)

-- Detalle Barista 10 (ventas 47 a 56)
INSERT INTO prod_venta (venta, producto, cantidad, precioUnitarioVenta, subtotal, totalIVA, total) VALUESNecesito solucionar dos problemas en el panel del administrador de Coffeelytics: el registro del rol de empleado (error de llave foranea en MySQL) y el filtro por barista y fecha en la consulta de ventas.

CONTEXTO DEL PROYECTO Y RESTRICCIONES ACADEMICAS:
- Proyecto: Coffeelytics (sistema de cafeteria en consola/TUI en Python + MySQL).
- Arquitectura de 4 capas: interfaz/, servicios/, repositorios/, datos/ (sin ORM, consultas SQL directas con `dictionary=True`).
- Nivel de codigo requerido: Programacion Orientada a Objetos (POO) basica/intermedia de estudiante de 3er cuatrimestre. Usa clases, metodos claros, listas, diccionarios, ciclos while/for, try/except e if/else simples. Evita patrones avanzados (sin decoradores, sin lambdas complejas, sin generadores).
- UI en consola: Usar exclusivamente las funciones existentes de `consola_ui.py` (`limpiar_pantalla`, `pausar`, `seleccionar_con_flechas`, `imprimir_encabezado_sesion`, `imprimir_tabla`, `_ancho`, `_prefijo`, `OperacionCancelada`, `PasoAnterior`) y `Color` de `interfaz/estilos.py`.

CAMBIOS EXACTOS A REALIZAR:

1. Corregir registro de rol de empleado por texto (`#file:admin_empleados.py` y su servicio/repositorio):
   - En la base de datos (`#file:BD.sql`), la tabla `rol` solo tiene dos PK validas: `ADMN` (Administrador) y `BARS` (Barista).
   - Permite que el usuario ingrese el rol mediante texto (`input`), mostrando claramente en el mensaje guia las PK validas:
     `Rol del empleado (ADMN = Administrador | BARS = Barista): `
   - Convierte la entrada a mayusculas y limpia espacios (`.strip().upper()`). Acepta tambien si el usuario escribe `"ADMINISTRADOR"` o `"BARISTA"` convirtiendolo automaticamente a `"ADMN"` o `"BARS"`.
   - Valida en ese mismo paso (dentro de un `while True:`) que el codigo resultante sea exactamente `'ADMN'` o `'BARS'` antes de llegar al `INSERT` en MySQL. Si escribe otra cosa, muestra `Color.error("Rol invalido. Debes ingresar ADMN (Administrador) o BARS (Barista).")`, haz `pausar()` y repite solo ese paso sin perder los datos ya capturados.
   - Verifica en el repositorio/servicio que la columna del rol en `INSERT INTO empleado` reciba esa PK (`'ADMN'` o `'BARS'`) y no un numero o texto largo que cause error `1452` de MySQL.

2. Filtrar consulta de ventas solo por Baristas y luego por fecha especifica (`#file:admin_consultas.py` y su servicio/repositorio):
   - Paso 1 (Seleccionar Barista):
     * Consulta unicamente a los empleados cuyo rol sea Barista (`WHERE rol = 'BARS'`), excluyendo administradores.
     * Muestra una tabla (`imprimir_tabla`) con solo esos baristas (Codigo/ID, Nombre completo, Correo/Usuario) y permite seleccionar uno (ya sea con `seleccionar_con_flechas` o ingresando su codigo validado).
   - Paso 2 (Ver ventas de ese barista y filtrar por fecha):
     * Muestra en una tabla (`imprimir_tabla`) UNICAMENTE las ventas realizadas por ese barista seleccionado (`WHERE v.empleado = %s`), ordenadas por fecha, mostrando codigo de venta, fecha, cliente, metodo de pago y total.
     * Permite elegir una fecha especifica (mostrando las fechas en las que ese barista tiene ventas o pidiendo la fecha `YYYY-MM-DD`) para filtrar y ver las ventas de ese barista en esa fecha exacta (o el detalle de una venta de esa fecha)
(47, 'LALM', 1, 75.00, 75.00, 6.00, 81.00),
(48, 'CAPU', 2, 60.00, 120.00, 9.60, 129.60),
(49, 'GAVE', 2, 28.00, 56.00, 4.48, 60.48),
(50, 'MTCH', 1, 75.00, 75.00, 6.00, 81.00),
(50, 'LAVE', 1, 75.00, 75.00, 6.00, 81.00),
(51, 'AMER', 2, 45.00, 90.00, 7.20, 97.20),
(52, 'LATT', 1, 65.00, 65.00, 5.20, 70.20),
(52, 'TISA', 1, 35.00, 35.00, 2.80, 37.80),
(52, 'GCHO', 1, 5.00, 5.00, 0.40, 5.40),
(53, 'LVAI', 1, 70.00, 70.00, 5.60, 75.60),
(54, 'CAPU', 1, 60.00, 60.00, 4.80, 64.80),
(54, 'LATT', 1, 65.00, 65.00, 5.20, 70.20),
(55, 'LAVE', 1, 75.00, 75.00, 6.00, 81.00),
(56, 'MTCH', 1, 75.00, 75.00, 6.00, 81.00),
(56, 'TISA', 1, 35.00, 35.00, 2.80, 37.80);

INSERT INTO producto (codigo, nombre, precio, estatus, categoria) VALUES
('GMAN', 'Galleta Mantequilla', 26.00, 1, 'GALL'),
('GRED', 'Galleta Red Velvet', 32.00, 1, 'GALL'),
('GMAC', 'Galleta Macadamia', 34.00, 1, 'GALL'),
('GDOU', 'Galleta Doble Chocolate', 32.00, 1, 'GALL'),
('GCAN', 'Galleta Canela Azúcar', 28.00, 1, 'GALL'),
('PCHE', 'Cheesecake Clásico', 72.00, 1, 'PAST'),
('PTRL', 'Pastel Tres Leches', 68.00, 1, 'PAST'),
('PTIR', 'Pastel Tiramisú', 75.00, 1, 'PAST'),
('PLIM', 'Pay de Limón', 60.00, 1, 'PAST'),
('PMOK', 'Pastel de Moka', 66.00, 1, 'PAST');

INSERT INTO receta (codigo, producto) VALUES
-- Recetas GALL
('RGMA', 'GMAN'),
('RGRE', 'GRED'),
('RGMC', 'GMAC'),
('RGDO', 'GDOU'),
('RGCA', 'GCAN'),
('RPTR', 'PTRL'),
('RPTI', 'PTIR'),
('RPLI', 'PLIM'),
('RPMO', 'PMOK');

INSERT INTO rec_insum (insumo, receta, cantidad) VALUES
-- Galletas existentes (RGAV, RGCH, RGNU)
('LECENT', 'RGAV', 0.05),
('CANELA', 'RGAV', 0.01),
('SERVIL', 'RGAV', 0.01),

('CHOCPO', 'RGCH', 0.02),
('LECENT', 'RGCH', 0.05),
('SERVIL', 'RGCH', 0.01),

('CHOCPO', 'RGNU', 0.02),
('JRVAIN', 'RGNU', 0.01),
('SERVIL', 'RGNU', 0.01)

-- Galletas nuevas (RGMA, RGRE, RGMC, RGDO, RGCA)
INSERT INTO rec_insum (insumo, receta, cantidad) VALUES
('LECENT', 'RGMA', 0.05),
('JRVAIN', 'RGMA', 0.01),
('SERVIL', 'RGMA', 0.01),

('CHOCPO', 'RGRE', 0.02),
('CREBAT', 'RGRE', 0.02),
('SERVIL', 'RGRE', 0.01),

('JRVAIN', 'RGMC', 0.01),
('LECENT', 'RGMC', 0.05),
('SERVIL', 'RGMC', 0.01),

('CHOCPO', 'RGDO', 0.03),
('JRMOCH', 'RGDO', 0.01),
('SERVIL', 'RGDO', 0.01),

('CANELA', 'RGCA', 0.02),
('AZUMAS', 'RGCA', 0.02),
('SERVIL', 'RGCA', 0.01)

-- Pasteles existentes (RPCH, RPRL, RPZN)
INSERT INTO rec_insum (insumo, receta, cantidad) VALUES
('CHOCPO', 'RPCH', 0.04),
('LECENT', 'RPCH', 0.08),
('CREBAT', 'RPCH', 0.02),
('SERVIL', 'RPCH', 0.01),

('LECENT', 'RPRL', 0.08),
('CREBAT', 'RPRL', 0.03),
('JRVAIN', 'RPRL', 0.01),
('SERVIL', 'RPRL', 0.01),

('CANELA', 'RPZN', 0.01),
('LECENT', 'RPZN', 0.08),
('CREBAT', 'RPZN', 0.02),
('SERVIL', 'RPZN', 0.01)

INSERT IGNORE INTO producto (codigo, nombre, precio, estatus, categoria) VALUES
('PCHE', 'Cheesecake Clásico', 72.00, 1, 'PAST'),
('PTRL', 'Pastel Tres Leches', 68.00, 1, 'PAST'),
('PTIR', 'Pastel Tiramisú', 75.00, 1, 'PAST'),
('PLIM', 'Pay de Limón', 60.00, 1, 'PAST'),
('PMOK', 'Pastel de Moka', 66.00, 1, 'PAST');

INSERT IGNORE INTO receta (codigo, producto) VALUES
('RPCE', 'PCHE'),
('RPTR', 'PTRL'),
('RPTI', 'PTIR'),
('RPLI', 'PLIM'),
('RPMO', 'PMOK');

-- Pasteles nuevos (RPCE, RPTR, RPTI, RPLI, RPMO)
INSERT INTO rec_insum (insumo, receta, cantidad) VALUES
('LECENT', 'RGMA', 0.05),
('JRVAIN', 'RGMA', 0.01),
('SERVIL', 'RGMA', 0.01),

('CHOCPO', 'RGRE', 0.02),
('CREBAT', 'RGRE', 0.02),
('SERVIL', 'RGRE', 0.01),

('JRVAIN', 'RGMC', 0.01),
('LECENT', 'RGMC', 0.05),
('SERVIL', 'RGMC', 0.01),

('CHOCPO', 'RGDO', 0.03),
('JRMOCH', 'RGDO', 0.01),
('SERVIL', 'RGDO', 0.01),

('CANELA', 'RGCA', 0.02),
('AZUMAS', 'RGCA', 0.02),
('SERVIL', 'RGCA', 0.01),

('LECENT', 'RPCE', 0.10),
('CREBAT', 'RPCE', 0.03),
('JRVAIN', 'RPCE', 0.01),
('SERVIL', 'RPCE', 0.01),

('LECENT', 'RPTR', 0.15),
('CREBAT', 'RPTR', 0.03),
('CANELA', 'RPTR', 0.01),
('SERVIL', 'RPTR', 0.01),

('ESPRES', 'RPTI', 0.02),
('CHOCPO', 'RPTI', 0.02),
('CREBAT', 'RPTI', 0.03),
('SERVIL', 'RPTI', 0.01),

('LECENT', 'RPLI', 0.08),
('CREBAT', 'RPLI', 0.03),
('SERVIL', 'RPLI', 0.01),

('ESPRES', 'RPMO', 0.02),
('JRMOCH', 'RPMO', 0.02),
('CREBAT', 'RPMO', 0.02),
('SERVIL', 'RPMO', 0.01);