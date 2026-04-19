-- Sistema: Plataforma de Seguimiento de Hábitos
-- Equipo: Henrique

CREATE DATABASE IF NOT EXISTS habbitos_db;
USE habbitos_db;

-- Tabla 1: Hábitos
CREATE TABLE IF NOT EXISTS habitos (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    frecuencia ENUM('diaria', 'semanal') NOT NULL DEFAULT 'diaria',
    meta INT NOT NULL COMMENT 'Meta diaria (ej: 1 vez al día) o semanal',
    creado_en TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tabla 2: Registros de cumplimiento
CREATE TABLE IF NOT EXISTS registros (
    id INT AUTO_INCREMENT PRIMARY KEY,
    habito_id INT NOT NULL,
    fecha DATE NOT NULL,
    cumplido BOOLEAN DEFAULT TRUE,
    registrado_en TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (habito_id) REFERENCES habitos(id) ON DELETE CASCADE,
    UNIQUE KEY unique_registro (habito_id, fecha)
);

-- Tabla 3: Rachas actuales
CREATE TABLE IF NOT EXISTS rachas (
    id INT AUTO_INCREMENT PRIMARY KEY,
    habito_id INT NOT NULL UNIQUE,
    racha_actual INT DEFAULT 0,
    racha_maxima INT DEFAULT 0,
    ultima_fecha DATE,
    actualizado_en TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (habito_id) REFERENCES habitos(id) ON DELETE CASCADE
);

-- Insertar datos de ejemplo
INSERT INTO habitos (nombre, frecuencia, meta) VALUES 
('Meditar', 'diaria', 1),
('Leer', 'diaria', 20),
('Ejercicio', 'semanal', 3);

-- Mostrar tablas creadas
SHOW TABLES;
