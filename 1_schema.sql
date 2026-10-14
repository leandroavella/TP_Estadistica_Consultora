-- =============================================================================
-- PROYECTO: ESTADÍSTICA BIVARIADA APLICADA A CONSULTAS MÉDICAS
-- BASE DE DATOS: consultora_medica (MariaDB / MySQL)
-- =============================================================================

CREATE DATABASE IF NOT EXISTS consultora_medica;
USE consultora_medica;

-- Limpieza preventiva si se desea reiniciar el esquema
DROP TABLE IF EXISTS consultas;
DROP TABLE IF EXISTS turnos;      -- Retrocompatibilidad con esquema previo
DROP TABLE IF EXISTS pacientes;   -- Retrocompatibilidad con esquema previo
DROP TABLE IF EXISTS medicos;     -- Retrocompatibilidad con esquema previo
DROP TABLE IF EXISTS doctores;

-- -----------------------------------------------------------------------------
-- 1. TABLA DE DOCTORES / ESPECIALIDADES
-- -----------------------------------------------------------------------------
CREATE TABLE doctores (
    id_doctor INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(80) NOT NULL,
    especialidad VARCHAR(60) NOT NULL,
    anios_experiencia INT NOT NULL
);

-- Inserción de profesionales de la salud
INSERT INTO doctores (id_doctor, nombre, especialidad, anios_experiencia) VALUES
(1, 'Dr. Santiago Perez', 'Clinica Medica', 18),
(2, 'Dra. Mariana Gomez', 'Pediatria', 8),
(3, 'Dr. Roberto Rodriguez', 'Cardiologia', 24),
(4, 'Dra. Camila Blanco', 'Medicina General', 4),
(5, 'Dr. Javier Martinez', 'Traumatologia', 12);

-- -----------------------------------------------------------------------------
-- 2. TABLA DE CONSULTAS MÉDICAS
-- Variables:
--   - id_consulta: Identificador único (PK)
--   - edad_paciente: Variable explicativa X1 (Edad en años)
--   - id_doctor: Identificador del profesional (FK)
--   - anios_experiencia_doc: Variable explicativa X2 (Experiencia en años)
--   - tiempo_atencion_min: Variable dependiente Y (Duración de la consulta en min)
--   - fecha_consulta: Registro temporal del acto médico
-- -----------------------------------------------------------------------------
CREATE TABLE consultas (
    id_consulta INT AUTO_INCREMENT PRIMARY KEY,
    edad_paciente INT NOT NULL,
    id_doctor INT NOT NULL,
    anios_experiencia_doc INT NOT NULL,
    tiempo_atencion_min FLOAT NOT NULL,
    fecha_consulta DATETIME NOT NULL,
    FOREIGN KEY (id_doctor) REFERENCES doctores(id_doctor)
);

-- -----------------------------------------------------------------------------
-- 3. TABLA DE TURNOS PROGRAMADOS / ACTIVOS
-- -----------------------------------------------------------------------------
CREATE TABLE turnos (
    id_turno INT AUTO_INCREMENT PRIMARY KEY,
    nombre_paciente VARCHAR(100) NOT NULL,
    edad_paciente INT NOT NULL,
    id_doctor INT NOT NULL,
    fecha_turno DATE NOT NULL,
    hora_turno TIME NOT NULL,
    estado VARCHAR(20) DEFAULT 'Activo',
    tiempo_estimado_min FLOAT NULL,
    fecha_registro DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (id_doctor) REFERENCES doctores(id_doctor) ON DELETE CASCADE
);

-- Inserción de turnos iniciales activos para la demostración
INSERT INTO turnos (nombre_paciente, edad_paciente, id_doctor, fecha_turno, hora_turno, estado, tiempo_estimado_min) VALUES
('Juan Carlos Lopez', 68, 3, CURDATE() + INTERVAL 1 DAY, '09:00:00', 'Activo', 32.9),
('Maria Elena Rossi', 32, 4, CURDATE() + INTERVAL 1 DAY, '09:30:00', 'Activo', 21.9),
('Lucia Fernandez', 8, 2, CURDATE() + INTERVAL 1 DAY, '10:00:00', 'Activo', 14.7),
('Carlos Alberto Gomez', 54, 1, CURDATE() + INTERVAL 2 DAY, '10:30:00', 'Activo', 28.7),
('Sofia Martinez', 45, 5, CURDATE() + INTERVAL 2 DAY, '11:00:00', 'Activo', 26.0),
('Esteban Quito', 72, 3, CURDATE() + INTERVAL 2 DAY, '11:30:00', 'Activo', 34.1),
('Valeria Gomez', 22, 1, CURDATE() + INTERVAL 3 DAY, '12:00:00', 'Activo', 19.0);

-- -----------------------------------------------------------------------------
-- 4. INSERCIÓN DE EXACTAMENTE 100 REGISTROS REALISTAS EN CONSULTAS (n = 100)
-- Justificación: Muestra estadísticamente representativa para validar
-- la necesidad de procesamiento automatizado frente a horas de cálculo manual.
-- Incluye variabilidad clínica coherente y casos atípicos intencionales.
-- -----------------------------------------------------------------------------
INSERT INTO consultas (id_consulta, edad_paciente, id_doctor, anios_experiencia_doc, tiempo_atencion_min, fecha_consulta) VALUES
(1, 18, 4, 4, 15.5, '2026-08-01 08:00:00'),
(2, 65, 3, 24, 34.0, '2026-08-01 08:15:00'),
(3, 42, 1, 18, 22.0, '2026-08-01 08:30:00'),
(4, 9, 2, 8, 18.5, '2026-08-01 08:45:00'),
(5, 55, 5, 12, 26.0, '2026-08-01 09:00:00'),
(6, 23, 4, 4, 16.0, '2026-08-01 09:15:00'),
(7, 71, 3, 24, 38.5, '2026-08-01 09:30:00'),
(8, 38, 1, 18, 20.5, '2026-08-01 09:45:00'),
(9, 6, 2, 8, 19.0, '2026-08-01 10:00:00'),
(10, 48, 5, 12, 24.5, '2026-08-01 10:15:00'),
(11, 29, 4, 4, 17.5, '2026-08-01 10:30:00'),
(12, 78, 3, 24, 41.0, '2026-08-01 10:45:00'),
(13, 50, 1, 18, 25.0, '2026-08-01 11:00:00'),
(14, 4, 2, 8, 21.0, '2026-08-01 11:15:00'),
(15, 60, 5, 12, 28.0, '2026-08-01 11:30:00'),
(16, 22, 4, 4, 15.0, '2026-08-01 11:45:00'),
(17, 68, 3, 24, 36.0, '2026-08-01 12:00:00'),
(18, 45, 1, 18, 23.5, '2026-08-01 12:15:00'),
(19, 11, 2, 8, 17.0, '2026-08-01 12:30:00'),
(20, 34, 5, 12, 21.5, '2026-08-01 12:45:00'),
(21, 25, 4, 4, 18.0, '2026-08-02 08:00:00'),
(22, 74, 3, 24, 39.0, '2026-08-02 08:15:00'),
(23, 52, 1, 18, 26.5, '2026-08-02 08:30:00'),
(24, 8, 2, 8, 18.0, '2026-08-02 08:45:00'),
(25, 63, 5, 12, 29.5, '2026-08-02 09:00:00'),
(26, 19, 4, 4, 14.5, '2026-08-02 09:15:00'),
(27, 82, 3, 24, 43.0, '2026-08-02 09:30:00'),
(28, 41, 1, 18, 21.0, '2026-08-02 09:45:00'),
(29, 5, 2, 8, 20.0, '2026-08-02 10:00:00'),
(30, 56, 5, 12, 27.0, '2026-08-02 10:15:00'),
(31, 31, 4, 4, 19.0, '2026-08-02 10:30:00'),
(32, 69, 3, 24, 37.0, '2026-08-02 10:45:00'),
(33, 47, 1, 18, 24.0, '2026-08-02 11:00:00'),
(34, 7, 2, 8, 17.5, '2026-08-02 11:15:00'),
(35, 39, 5, 12, 22.5, '2026-08-02 11:30:00'),
(36, 27, 4, 4, 16.5, '2026-08-02 11:45:00'),
(37, 72, 3, 24, 38.0, '2026-08-02 12:00:00'),
(38, 54, 1, 18, 27.0, '2026-08-02 12:15:00'),
(39, 12, 2, 8, 16.5, '2026-08-02 12:30:00'),
(40, 67, 5, 12, 31.0, '2026-08-02 12:45:00'),
(41, 20, 4, 4, 15.0, '2026-08-03 08:00:00'),
(42, 79, 3, 24, 42.0, '2026-08-03 08:15:00'),
(43, 44, 1, 18, 22.5, '2026-08-03 08:30:00'),
(44, 10, 2, 8, 18.0, '2026-08-03 08:45:00'),
(45, 58, 5, 12, 27.5, '2026-08-03 09:00:00'),
(46, 28, 4, 4, 17.0, '2026-08-03 09:15:00'),
(47, 66, 3, 24, 35.0, '2026-08-03 09:30:00'),
(48, 49, 1, 18, 25.0, '2026-08-03 09:45:00'),
(49, 3, 2, 8, 22.0, '2026-08-03 10:00:00'),
(50, 43, 5, 12, 23.0, '2026-08-03 10:15:00'),
(51, 35, 4, 4, 20.0, '2026-08-03 10:30:00'),
(52, 75, 3, 24, 40.0, '2026-08-03 10:45:00'),
(53, 53, 1, 18, 26.0, '2026-08-03 11:00:00'),
(54, 13, 2, 8, 16.0, '2026-08-03 11:15:00'),
(55, 62, 5, 12, 29.0, '2026-08-03 11:30:00'),
(56, 24, 4, 4, 16.0, '2026-08-03 11:45:00'),
(57, 70, 3, 24, 37.5, '2026-08-03 12:00:00'),
(58, 46, 1, 18, 23.0, '2026-08-03 12:15:00'),
(59, 6, 2, 8, 19.5, '2026-08-03 12:30:00'),
(60, 50, 5, 12, 25.5, '2026-08-03 12:45:00'),
(61, 33, 4, 4, 18.5, '2026-08-04 08:00:00'),
(62, 81, 3, 24, 42.5, '2026-08-04 08:15:00'),
(63, 57, 1, 18, 28.0, '2026-08-04 08:30:00'),
(64, 4, 2, 8, 20.5, '2026-08-04 08:45:00'),
(65, 65, 5, 12, 30.5, '2026-08-04 09:00:00'),
(66, 21, 4, 4, 15.5, '2026-08-04 09:15:00'),
(67, 73, 3, 24, 38.5, '2026-08-04 09:30:00'),
(68, 40, 1, 18, 21.5, '2026-08-04 09:45:00'),
(69, 9, 2, 8, 18.5, '2026-08-04 10:00:00'),
(70, 51, 5, 12, 26.0, '2026-08-04 10:15:00'),
(71, 30, 4, 4, 17.5, '2026-08-04 10:30:00'),
(72, 77, 3, 24, 40.5, '2026-08-04 10:45:00'),
(73, 48, 1, 18, 24.5, '2026-08-04 11:00:00'),
(74, 5, 2, 8, 19.5, '2026-08-04 11:15:00'),
(75, 59, 5, 12, 28.5, '2026-08-04 11:30:00'),
(76, 26, 4, 4, 16.0, '2026-08-04 11:45:00'),
(77, 67, 3, 24, 36.5, '2026-08-04 12:00:00'),
(78, 51, 1, 18, 25.5, '2026-08-04 12:15:00'),
(79, 11, 2, 8, 17.0, '2026-08-04 12:30:00'),
(80, 37, 5, 12, 22.0, '2026-08-04 12:45:00'),
(81, 22, 4, 4, 15.0, '2026-08-05 08:00:00'),
(82, 84, 3, 24, 44.0, '2026-08-05 08:15:00'),
(83, 43, 1, 18, 22.0, '2026-08-05 08:30:00'),
(84, 7, 2, 8, 18.0, '2026-08-05 08:45:00'),
(85, 64, 5, 12, 30.0, '2026-08-05 09:00:00'),
(86, 32, 4, 4, 18.0, '2026-08-05 09:15:00'),
(87, 76, 3, 24, 39.5, '2026-08-05 09:30:00'),
(88, 55, 1, 18, 27.5, '2026-08-05 09:45:00'),
(89, 8, 2, 8, 18.5, '2026-08-05 10:00:00'),
(90, 46, 5, 12, 24.0, '2026-08-05 10:15:00'),
(91, 19, 4, 4, 14.0, '2026-08-05 10:30:00'),
(92, 70, 3, 24, 37.0, '2026-08-05 10:45:00'),
(93, 36, 1, 18, 20.0, '2026-08-05 11:00:00'),
(94, 14, 2, 8, 16.0, '2026-08-05 11:15:00'),
(95, 61, 5, 12, 28.5, '2026-08-05 11:30:00'),
(96, 25, 4, 4, 16.5, '2026-08-05 11:45:00'),
(97, 80, 3, 24, 41.5, '2026-08-05 12:00:00'),
-- Registros 98, 99 y 100: Casos clínicos particulares / Outliers deliberados
-- 98: Paciente adulto de 45 años con complicación aguda atendido por Dr. Perez (52.0 min) -> Anomalía positiva
-- 99: Paciente de 72 años para firma rápida de receta atendido por Dra. Blanco (8.5 min) -> Anomalía negativa
-- 100: Paciente de 58 años con control habitual atendido por Dr. Martinez (26.5 min)
(98, 45, 1, 18, 52.0, '2026-08-05 12:15:00'),
(99, 72, 4, 4, 8.5, '2026-08-05 12:30:00'),
(100, 58, 5, 12, 26.5, '2026-08-05 12:45:00');

-- -----------------------------------------------------------------------------
-- Verificación automática de integridad:
-- -----------------------------------------------------------------------------
SELECT COUNT(*) AS total_consultas_cargadas FROM consultas;
