-- Active: 1792597882538@@127.0.0.1@3306@bd_coffeelytics
-- ============================================================================
-- ARCHIVO: bd_coffeelytics.sql
-- UBICACIÓN: coffeelytics/bd_coffeelytics.sql
-- DESCRIPCIÓN: Base de datos relacional corregida para Coffeelytics (22 tablas)
--              con datos iniciales y registros de prueba.
-- ============================================================================

DROP DATABASE IF EXISTS bd_coffeelytics;
CREATE DATABASE bd_coffeelytics CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE bd_coffeelytics;

-- ----------------------------------------------------------------------------
-- 1. CATÁLOGOS INDEPENDIENTES
-- ----------------------------------------------------------------------------

CREATE TABLE proveedor (
    codigo VARCHAR(4) NOT NULL,
    nombre VARCHAR(30) NOT NULL,
    dirCalle VARCHAR(30) NOT NULL,
    dirColonia VARCHAR(30) NOT NULL,
    dirNumero VARCHAR(12) NOT NULL,
    telefono VARCHAR(10) NOT NULL,
    ciudad VARCHAR(20) NOT NULL,
    PRIMARY KEY (codigo)
);

CREATE TABLE tipo_merma (
    codigo VARCHAR(5) NOT NULL,
    nombre VARCHAR(50) NOT NULL,
    PRIMARY KEY (codigo),
    UNIQUE (nombre)
);

CREATE TABLE estante (
    codigo INT NOT NULL AUTO_INCREMENT,
    capacidad INT NOT NULL,
    secciones INT NOT NULL,
    PRIMARY KEY (codigo)
);

CREATE TABLE categoria_insumo (
    codigo VARCHAR(4) NOT NULL,
    nombre VARCHAR(50) NOT NULL UNIQUE,
    PRIMARY KEY (codigo)
);

CREATE TABLE categoria_producto (
    codigo VARCHAR(4) NOT NULL,
    nombre VARCHAR(30) NOT NULL UNIQUE,
    PRIMARY KEY (codigo)
);

CREATE TABLE estatus_producto (
    codigo INT AUTO_INCREMENT NOT NULL,
    nombre VARCHAR(20) NOT NULL,
    PRIMARY KEY (codigo),
    UNIQUE (nombre)
);

CREATE TABLE unidad_medida (
    codigo VARCHAR(4) NOT NULL,
    nombre VARCHAR(30) NOT NULL,
    abreviatura VARCHAR(8) NOT NULL,
    PRIMARY KEY (codigo),
    UNIQUE (nombre)
);

CREATE TABLE rol (
    codigo VARCHAR(4) NOT NULL,
    nombre VARCHAR(15) NOT NULL,
    PRIMARY KEY (codigo),
    UNIQUE (nombre)
);

CREATE TABLE metodo_pago (
    codigo VARCHAR(4) NOT NULL,
    descripcion VARCHAR(30) NOT NULL,
    PRIMARY KEY (codigo),
    UNIQUE (descripcion)
);

-- ----------------------------------------------------------------------------
-- 2. ENTIDADES PRINCIPALES
-- ----------------------------------------------------------------------------

CREATE TABLE producto (
    codigo VARCHAR(4) NOT NULL,
    nombre VARCHAR(30) NOT NULL,
    precio DECIMAL(10,2) NOT NULL,
    estatus INT NOT NULL,
    categoria VARCHAR(4) NOT NULL,
    PRIMARY KEY (codigo),
    UNIQUE (nombre),
    FOREIGN KEY (estatus) REFERENCES estatus_producto(codigo),
    FOREIGN KEY (categoria) REFERENCES categoria_producto(codigo)
);

CREATE TABLE receta (
    codigo VARCHAR(4) NOT NULL,
    producto VARCHAR(4) NOT NULL,
    PRIMARY KEY (codigo),
    FOREIGN KEY (producto) REFERENCES producto(codigo)
);

CREATE TABLE empleado (
    num INT AUTO_INCREMENT,
    nombrePila VARCHAR(30) NOT NULL,
    primApell VARCHAR(30) NOT NULL,
    segApell VARCHAR(30),
    RFC VARCHAR(12) NOT NULL,
    telefono VARCHAR(10),
    correo VARCHAR(60) NOT NULL,
    contrasena VARCHAR(60) NOT NULL,
    activo TINYINT(1) NOT NULL DEFAULT 1, -- 1 = Activo, 0 = Eliminado lógicamente
    rol VARCHAR(4) NOT NULL,
    PRIMARY KEY (num),
    UNIQUE (RFC),
    UNIQUE (correo),
    FOREIGN KEY (rol) REFERENCES rol(codigo)
);

CREATE TABLE compra (
    codigo INT AUTO_INCREMENT,
    fecha DATE NOT NULL,
    total DECIMAL(10,2) NOT NULL,
    proveedor VARCHAR(4) NOT NULL,
    metodoPago VARCHAR(4) NOT NULL,
    empleado INT NOT NULL,
    PRIMARY KEY (codigo),
    FOREIGN KEY (proveedor) REFERENCES proveedor(codigo),
    FOREIGN KEY (metodoPago) REFERENCES metodo_pago(codigo),
    FOREIGN KEY (empleado) REFERENCES empleado(num)
);

CREATE TABLE venta (
    codigo INT AUTO_INCREMENT,
    fecha DATETIME NOT NULL,
    nombreCliente VARCHAR(50) NOT NULL DEFAULT 'Mostrador',
    total DECIMAL(10,2) NOT NULL,
    metodoPago VARCHAR(4) NOT NULL,
    empleado INT NOT NULL,
    PRIMARY KEY (codigo),
    FOREIGN KEY (metodoPago) REFERENCES metodo_pago(codigo),
    FOREIGN KEY (empleado) REFERENCES empleado(num)
);

CREATE TABLE insumo (
    codigo VARCHAR(6) NOT NULL,
    nombre VARCHAR(50) NOT NULL,
    stockActual DECIMAL(10,2) NOT NULL DEFAULT 0,
    stockMin DECIMAL(10,2) NOT NULL DEFAULT 0,
    seccion TINYINT NOT NULL,
    unidad VARCHAR(4) NOT NULL,
    estante INT NOT NULL,
    categoria VARCHAR(4) NOT NULL,
    PRIMARY KEY (codigo),
    UNIQUE (nombre),
    FOREIGN KEY (estante) REFERENCES estante(codigo),
    FOREIGN KEY (unidad) REFERENCES unidad_medida(codigo),
    FOREIGN KEY (categoria) REFERENCES categoria_insumo(codigo)
);

CREATE TABLE consumible_mesa (
    codigo VARCHAR(5) NOT NULL,
    nombre VARCHAR(40) NOT NULL,
    empleado INT NOT NULL,
    PRIMARY KEY (codigo),
    UNIQUE (nombre),
    FOREIGN KEY (empleado) REFERENCES empleado(num)
);

CREATE TABLE factura (
    codigo VARCHAR(8) NOT NULL,
    monto DECIMAL(10,2) NOT NULL,
    folioFiscal VARCHAR(36) NOT NULL,
    fecha DATE NOT NULL,
    compra INT NOT NULL,
    PRIMARY KEY (codigo),
    UNIQUE (folioFiscal),
    FOREIGN KEY (compra) REFERENCES compra(codigo)
);

CREATE TABLE merma (
    codigo INT NOT NULL AUTO_INCREMENT,
    motivo VARCHAR(300) NOT NULL,
    fecha DATE NOT NULL,
    cantidad DECIMAL(10,2) NOT NULL,
    tipo VARCHAR(5) NOT NULL,
    insumo VARCHAR(6) NOT NULL,
    idEmpleado INT NULL,  -- barista que registro la merma; NULL en registros previos a esta columna
    PRIMARY KEY (codigo),
    FOREIGN KEY (tipo) REFERENCES tipo_merma(codigo),
    FOREIGN KEY (insumo) REFERENCES insumo(codigo),
    FOREIGN KEY (idEmpleado) REFERENCES empleado(num)
);

-- ----------------------------------------------------------------------------
-- 3. TABLAS INTERMEDIAS (RELACIONES MUCHOS A MUCHOS)
-- ----------------------------------------------------------------------------

CREATE TABLE prod_venta (
    venta INT NOT NULL,
    producto VARCHAR(4) NOT NULL,
    cantidad INT NOT NULL,
    precioUnitarioVenta DECIMAL(10,2) NOT NULL,
    subtotal DECIMAL(10,2) NOT NULL,
    totalIVA DECIMAL(10,2) NOT NULL,
    total DECIMAL(10,2) NOT NULL,
    PRIMARY KEY (venta, producto),
    FOREIGN KEY (venta) REFERENCES venta(codigo),
    FOREIGN KEY (producto) REFERENCES producto(codigo)
);

CREATE TABLE con_insum (
    insumo VARCHAR(6) NOT NULL,
    mesa VARCHAR(5) NOT NULL,
    cantidad DECIMAL(10,2) NOT NULL,
    PRIMARY KEY (insumo, mesa),
    FOREIGN KEY (insumo) REFERENCES insumo(codigo),
    FOREIGN KEY (mesa) REFERENCES consumible_mesa(codigo)
);

CREATE TABLE insum_com (
    compra INT NOT NULL,
    insumo VARCHAR(6) NOT NULL,
    cantidad DECIMAL(10,2) NOT NULL,
    precioUnitarioCom DECIMAL(10,2) NOT NULL,
    subtotal DECIMAL(10,2) NOT NULL,
    totalIVA DECIMAL(10,2) NOT NULL,
    total DECIMAL(10,2) NOT NULL,
    PRIMARY KEY (compra, insumo),
    FOREIGN KEY (compra) REFERENCES compra(codigo),
    FOREIGN KEY (insumo) REFERENCES insumo(codigo)
);

CREATE TABLE rec_insum (
    insumo VARCHAR(6) NOT NULL,
    receta VARCHAR(4) NOT NULL,
    cantidad DECIMAL(10,2) NOT NULL,
    PRIMARY KEY (insumo, receta),
    FOREIGN KEY (insumo) REFERENCES insumo(codigo),
    FOREIGN KEY (receta) REFERENCES receta(codigo)
);

-- ============================================================================
-- 4. INSERCIÓN DE DATOS INICIALES Y DE PRUEBA (PARA EXPOSICIÓN)
-- ============================================================================

INSERT INTO rol VALUES ('ADMN', 'Administrador'), ('BARS', 'Barista');

INSERT INTO empleado (nombrePila, primApell, segApell, RFC, telefono, correo, contrasena, rol) VALUES
('Guillermo', 'Landaverde', 'Montoya', 'LAMG010101A1', '6641234567', 'admin@coffeelytics.com', 'admin123', 'ADMN'),
('Cristian', 'Gomez', 'Santos', 'GOSC020202B2', '6647654321', 'barista@coffeelytics.com', 'barista123', 'BARS'),
('Jorge', 'Huizar', 'Ruvalcaba', 'HURJ030303C3', '6649876543', 'jorge@coffeelytics.com', '1234', 'BARS');

INSERT INTO estatus_producto (nombre) VALUES ('Activo'), ('No Disponible');

INSERT INTO categoria_producto VALUES
('CAFE', 'Cafés'),
('PAST', 'Rebanadas de Pastel'),
('GALL', 'Galletas'),
('FEST', 'Bebidas Festivas');

INSERT INTO metodo_pago VALUES
('EFEC', 'Efectivo'),
('TARJ', 'Tarjeta Crédito/Débito'),I
('TRAN', 'Transferencia Electrónica');

INSERT INTO unidad_medida VALUES
('GRAM', 'Gramos', 'g'),
('MILI', 'Mililitros', 'ml'),
('PIEZ', 'Piezas', 'pz');

INSERT INTO categoria_insumo VALUES
('GRAN', 'Granos de Café'),
('LACT', 'Lácteos'),
('JARA', 'Jarabes y Endulzantes'),
('REPS', 'Repostería'),
('DESC', 'Desechables');

INSERT INTO estante (capacidad, secciones) VALUES (500, 4), (300, 3);

INSERT INTO proveedor VALUES
('PR01', 'Café de Baja S.A.', 'Blvd. Agua Caliente', 'Aviación', '1040', '6641112233', 'Tijuana'),
('PR02', 'Lácteos del Noroeste', 'Av. Revolución', 'Centro', '512', '6644445566', 'Tijuana'),
('PR03', 'Insumos Dulces MX', 'Av. Reforma', 'Juárez', '890', '5559998877', 'CDMX');

INSERT INTO tipo_merma VALUES
('TM001', 'Derrame accidental en barra'),
('TM002', 'Producto caducado'),
('TM003', 'Error de preparación');

-- Insumos (Nota: INS004 tiene stock bajo intencional para probar alerta al Admin)
INSERT INTO insumo VALUES
('INS001', 'Café Espresso Molido', 5000.00, 500.00, 1, 'GRAM', 1, 'GRAN'),
('INS002', 'Leche Entera', 8000.00, 1000.00, 2, 'MILI', 1, 'LACT'),
('INS003', 'Jarabe de Vainilla', 2500.00, 300.00, 3, 'MILI', 1, 'JARA'),
('INS004', 'Jarabe de Calabaza', 120.00, 150.00, 3, 'MILI', 1, 'JARA'),
('INS005', 'Rebanada Pastel Chocolate', 15.00, 3.00, 1, 'PIEZ', 2, 'REPS'),
('INS006', 'Galleta Chispas Chocolate', 20.00, 5.00, 2, 'PIEZ', 2, 'REPS'),
('INS007', 'Azúcar Morena (Sobres)', 400.00, 50.00, 4, 'PIEZ', 1, 'DESC');

-- Productos (Nota: P006 está No Disponible por falta de Jarabe de Calabaza)
INSERT INTO producto VALUES
('P001', 'Americano Clásico', 45.00, 1, 'CAFE'),
('P002', 'Latte Vainilla', 65.00, 1, 'CAFE'),
('P003', 'Capuchino Cremoso', 60.00, 1, 'CAFE'),
('P004', 'Pastel Chocolate', 75.00, 1, 'PAST'),
('P005', 'Galleta Chispas', 35.00, 1, 'GALL'),
('P006', 'Latte Calabaza Festivo', 78.00, 2, 'FEST');

-- Recetas y sus insumos
INSERT INTO receta VALUES
('R001', 'P001'), ('R002', 'P002'), ('R003', 'P003'),
('R004', 'P004'), ('R005', 'P005'), ('R006', 'P006');

INSERT INTO rec_insum VALUES
('INS001', 'R001', 18.00),
('INS001', 'R002', 18.00), ('INS002', 'R002', 200.00), ('INS003', 'R002', 30.00),
('INS001', 'R003', 18.00), ('INS002', 'R003', 180.00),
('INS005', 'R004', 1.00),
('INS006', 'R005', 1.00),
('INS001', 'R006', 18.00), ('INS002', 'R006', 200.00), ('INS004', 'R006', 40.00);

-- Mesa de consumibles
INSERT INTO consumible_mesa VALUES ('MESA1', 'Barra Autoservicio Principal', 2);
INSERT INTO con_insum VALUES ('INS007', 'MESA1', 50.00);

-- Compras iniciales (Para vincular proveedores con insumos)
INSERT INTO compra (fecha, total, proveedor, metodoPago, empleado) VALUES
(CURDATE(), 1215.00, 'PR01', 'TRAN', 1),
(CURDATE(), 432.00, 'PR02', 'EFEC', 1),
(CURDATE(), 580.00, 'PR03', 'TARJ', 1);

INSERT INTO insum_com VALUES
(1, 'INS001', 2500.00, 0.45, 1125.00, 90.00, 1215.00),
(2, 'INS002', 8000.00, 0.05, 400.00, 32.00, 432.00),
(3, 'INS004', 500.00, 1.00, 500.00, 80.00, 580.00);

-- 10 Ventas de prueba (Cumple mínimo de 10 registros para Consultas)
INSERT INTO venta (fecha, nombreCliente, total, metodoPago, empleado) VALUES
(NOW(), 'Ana López', 48.60, 'EFEC', 2),
(NOW(), 'Carlos Ruiz', 70.20, 'TARJ', 2),
(NOW(), 'Sofía Mendoza', 64.80, 'TRAN', 2),
(NOW(), 'Luis Pérez', 81.00, 'EFEC', 2),
(NOW(), 'Elena Torres', 37.80, 'EFEC', 3),
(NOW(), 'Marco Díaz', 118.80, 'TARJ', 3),
(NOW(), 'Lucía Gómez', 48.60, 'EFEC', 2),
(NOW(), 'Pedro Salas', 70.20, 'TRAN', 3),
(NOW(), 'Valeria Cruz', 135.00, 'TARJ', 2),
(NOW(), 'Diego Castro', 318.60, 'EFEC', 2);

-- Venta 10 tiene 5 productos distintos (Cumple Consulta 1: mínimo 5 productos)
INSERT INTO prod_venta VALUES
(1, 'P001', 1, 45.00, 45.00, 3.60, 48.60),
(2, 'P002', 1, 65.00, 65.00, 5.20, 70.20),
(3, 'P003', 1, 60.00, 60.00, 4.80, 64.80),
(4, 'P004', 1, 75.00, 75.00, 6.00, 81.00),
(5, 'P005', 1, 35.00, 35.00, 2.80, 37.80),
(6, 'P001', 1, 45.00, 45.00, 3.60, 48.60),
(6, 'P002', 1, 65.00, 65.00, 5.20, 70.20),
(7, 'P001', 1, 45.00, 45.00, 3.60, 48.60),
(8, 'P002', 1, 65.00, 65.00, 5.20, 70.20),
(9, 'P003', 1, 60.00, 60.00, 4.80, 64.80),
(9, 'P002', 1, 65.00, 65.00, 5.20, 70.20),
(10, 'P001', 1, 45.00, 45.00, 3.60, 48.60),
(10, 'P002', 1, 65.00, 65.00, 5.20, 70.20),
(10, 'P003', 1, 60.00, 60.00, 4.80, 64.80),
(10, 'P004', 1, 75.00, 75.00, 6.00, 81.00),
(10, 'P005', 1, 35.00, 35.00, 2.80, 37.80);

-- 10 Mermas de prueba (Cumple mínimo de 10 registros para Consulta 3)
INSERT INTO merma (motivo, fecha, cantidad, tipo, insumo) VALUES
('Se cayó jarra de leche al vaporizar', CURDATE(), 250.00, 'TM001', 'INS002'),
('Café molido húmedo por filtro roto', CURDATE(), 36.00, 'TM003', 'INS001'),
('Rebanada de pastel aplastada en vitrina', CURDATE(), 1.00, 'TM001', 'INS005'),
('Galleta rota al sacar de charola', CURDATE(), 1.00, 'TM001', 'INS006'),
('Leche cortada antes de abrir', DATE_SUB(CURDATE(), INTERVAL 1 DAY), 500.00, 'TM002', 'INS002'),
('Derrame de jarabe de vainilla', DATE_SUB(CURDATE(), INTERVAL 1 DAY), 50.00, 'TM001', 'INS003'),
('Error en bebida equivocada', DATE_SUB(CURDATE(), INTERVAL 2 DAY), 18.00, 'TM003', 'INS001'),
('Leche derramada en barra', DATE_SUB(CURDATE(), INTERVAL 2 DAY), 200.00, 'TM001', 'INS002'),
('Galleta vencida de lote anterior', DATE_SUB(CURDATE(), INTERVAL 3 DAY), 2.00, 'TM002', 'INS006'),
('Jarabe de calabaza derramado', DATE_SUB(CURDATE(), INTERVAL 3 DAY), 40.00, 'TM001', 'INS004');