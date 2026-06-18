-- ============================================================
--  BASE DE DATOS: colegio_db
--  Sistema de Gestión Académica
-- ============================================================

-- Crear la base de datos
-- CREATE DATABASE colegio_db;
-- copiar esta base de datos a PostgreSQL
-- en PostgreSQL, la creación de la base de datos se hace fuera del script, pero se incluye aquí como referencia.

-- ============================================================
--  ROLES DE USUARIO
-- ============================================================
CREATE TABLE IF NOT EXISTS roles (
    id_rol      SERIAL PRIMARY KEY,
    nombre_rol  VARCHAR(50) NOT NULL UNIQUE
);

INSERT INTO roles (nombre_rol) VALUES
    ('ADMIN'),
    ('PROFESOR'),
    ('ESTUDIANTE'),
    ('ADMINISTRATIVO')
ON CONFLICT DO NOTHING;

-- ============================================================
--  USUARIOS (autenticación)
-- ============================================================
CREATE TABLE IF NOT EXISTS usuarios (
    id_usuario      SERIAL PRIMARY KEY,
    nombre_usuario  VARCHAR(100) NOT NULL UNIQUE,
    password        VARCHAR(255) NOT NULL,
    id_rol          INTEGER NOT NULL REFERENCES roles(id_rol),
    estado          BOOLEAN NOT NULL DEFAULT TRUE
);

-- Usuario administrador por defecto
INSERT INTO usuarios (nombre_usuario, password, id_rol) VALUES
    ('admin', 'admin', (SELECT id_rol FROM roles WHERE nombre_rol = 'ADMIN'))
ON CONFLICT DO NOTHING;

-- ============================================================
--  CURSOS  (ej: 1ro Bachillerato, 2do Básica …)
-- ============================================================
CREATE TABLE IF NOT EXISTS cursos (
    id_curso      SERIAL PRIMARY KEY,
    nombre_curso  VARCHAR(100) NOT NULL
);

-- ============================================================
--  PARALELOS  (ej: A, B, C …)
-- ============================================================
CREATE TABLE IF NOT EXISTS paralelos (
    id_paralelo      SERIAL PRIMARY KEY,
    nombre_paralelo  VARCHAR(10) NOT NULL
);

-- ============================================================
--  MATERIAS
-- ============================================================
CREATE TABLE IF NOT EXISTS materias (
    id_materia      SERIAL PRIMARY KEY,
    nombre_materia  VARCHAR(100) NOT NULL
);

-- ============================================================
--  AULAS
-- ============================================================
CREATE TABLE IF NOT EXISTS aulas (
    id_aula     SERIAL PRIMARY KEY,
    nombre_aula VARCHAR(100) NOT NULL,
    capacidad   INTEGER,
    tipo        VARCHAR(50)
);

-- ============================================================
--  TIPOS DE EVALUACIÓN  (Práctica, Examen, Proyecto, etc.)
-- ============================================================
CREATE TABLE IF NOT EXISTS tipos_evaluacion (
    id_tipo_evaluacion  SERIAL PRIMARY KEY,
    nombre_tipo         VARCHAR(100) NOT NULL UNIQUE
);

INSERT INTO tipos_evaluacion (nombre_tipo) VALUES
    ('Práctica'),
    ('Examen'),
    ('Proyecto'),
    ('Exposición'),
    ('Tarea')
ON CONFLICT DO NOTHING;

-- ============================================================
--  PROFESORES
-- ============================================================
CREATE TABLE IF NOT EXISTS profesores (
    id_profesor      SERIAL PRIMARY KEY,
    nombres          VARCHAR(100) NOT NULL,
    apellidos        VARCHAR(100) NOT NULL,
    ci               VARCHAR(20)  NOT NULL UNIQUE,
    fecha_nacimiento DATE,
    id_materia       INTEGER REFERENCES materias(id_materia),
    id_usuario       INTEGER REFERENCES usuarios(id_usuario) ON DELETE CASCADE,
    id_paralelo      INTEGER REFERENCES paralelos(id_paralelo),
    id_curso         INTEGER REFERENCES cursos(id_curso)
);

-- ============================================================
--  ESTUDIANTES
-- ============================================================
CREATE TABLE IF NOT EXISTS estudiantes (
    id_estudiante    SERIAL PRIMARY KEY,
    nombres          VARCHAR(100) NOT NULL,
    apellidos        VARCHAR(100) NOT NULL,
    ci               VARCHAR(20)  NOT NULL UNIQUE,
    fecha_nacimiento DATE,
    id_curso         INTEGER NOT NULL REFERENCES cursos(id_curso),
    id_paralelo      INTEGER NOT NULL REFERENCES paralelos(id_paralelo),
    id_usuario       INTEGER REFERENCES usuarios(id_usuario) ON DELETE CASCADE
);

-- ============================================================
--  ADMINISTRATIVOS
-- ============================================================
CREATE TABLE IF NOT EXISTS administrativos (
    id_administrativo  SERIAL PRIMARY KEY,
    nombres            VARCHAR(100) NOT NULL,
    apellidos          VARCHAR(100) NOT NULL,
    ci                 VARCHAR(20)  NOT NULL UNIQUE,
    cargo              VARCHAR(100),
    id_usuario         INTEGER REFERENCES usuarios(id_usuario) ON DELETE CASCADE
);

-- Usuario administrativo por defecto
INSERT INTO usuarios (nombre_usuario, password, id_rol) VALUES
    ('administrativo', 'admin', (SELECT id_rol FROM roles WHERE nombre_rol = 'ADMINISTRATIVO'))
ON CONFLICT DO NOTHING;

INSERT INTO administrativos (nombres, apellidos, ci, cargo, id_usuario) VALUES
    ('Personal', 'Administrativo', '0000000000', 'Secretaría',
     (SELECT id_usuario FROM usuarios WHERE nombre_usuario = 'administrativo'))
ON CONFLICT DO NOTHING;

-- ============================================================
--  RELACIÓN PROFESOR ↔ MATERIA  (varias materias por profesor)
-- ============================================================
CREATE TABLE IF NOT EXISTS profesor_materia (
    id_profesor  INTEGER NOT NULL REFERENCES profesores(id_profesor) ON DELETE CASCADE,
    id_materia   INTEGER NOT NULL REFERENCES materias(id_materia)   ON DELETE CASCADE,
    PRIMARY KEY (id_profesor, id_materia)
);

-- ============================================================
--  HORARIOS
-- ============================================================
CREATE TABLE IF NOT EXISTS horarios (
    id_horario   SERIAL PRIMARY KEY,
    id_profesor  INTEGER NOT NULL REFERENCES profesores(id_profesor) ON DELETE CASCADE,
    id_materia   INTEGER NOT NULL REFERENCES materias(id_materia),
    id_aula      INTEGER NOT NULL REFERENCES aulas(id_aula),
    id_curso     INTEGER NOT NULL REFERENCES cursos(id_curso),
    id_paralelo  INTEGER NOT NULL REFERENCES paralelos(id_paralelo),
    dia          VARCHAR(20) NOT NULL,
    hora_inicio  TIME NOT NULL,
    hora_fin     TIME NOT NULL
);

-- ============================================================
--  ACTIVIDADES  (evaluaciones creadas por el profesor)
--  Ej: "Práctica 1 de Matemáticas - 1er Trimestre"
-- ============================================================
CREATE TABLE IF NOT EXISTS actividades (
    id_actividad        SERIAL PRIMARY KEY,
    id_profesor         INTEGER NOT NULL REFERENCES profesores(id_profesor) ON DELETE CASCADE,
    id_materia          INTEGER NOT NULL REFERENCES materias(id_materia),
    id_tipo_evaluacion  INTEGER NOT NULL REFERENCES tipos_evaluacion(id_tipo_evaluacion),
    nombre              VARCHAR(200) NOT NULL,
    periodo             VARCHAR(50)  NOT NULL
        CHECK (periodo IN ('1er Trimestre', '2do Trimestre', '3er Trimestre'))
);

-- ============================================================
--  NOTAS
--  Cada nota está ligada a una actividad creada por el profesor.
--  Pesos: 1er Trimestre = 30 pts, 2do = 30 pts, 3er = 40 pts
--  Nota final = Σ (promedio_trimestre / 100 × peso_trimestre)
-- ============================================================
CREATE TABLE IF NOT EXISTS notas (
    id_nota             SERIAL PRIMARY KEY,
    id_estudiante       INTEGER NOT NULL REFERENCES estudiantes(id_estudiante) ON DELETE CASCADE,
    id_materia          INTEGER NOT NULL REFERENCES materias(id_materia),
    id_tipo_evaluacion  INTEGER NOT NULL REFERENCES tipos_evaluacion(id_tipo_evaluacion),
    nota                NUMERIC(5,2) NOT NULL CHECK (nota >= 0 AND nota <= 100),
    periodo             VARCHAR(50)  NOT NULL,
    id_actividad        INTEGER REFERENCES actividades(id_actividad) ON DELETE SET NULL
);

-- ============================================================
--  ÍNDICES útiles para consultas frecuentes
-- ============================================================
CREATE INDEX IF NOT EXISTS idx_notas_estudiante  ON notas(id_estudiante);
CREATE INDEX IF NOT EXISTS idx_notas_actividad   ON notas(id_actividad);
CREATE INDEX IF NOT EXISTS idx_actividades_prof  ON actividades(id_profesor);
CREATE INDEX IF NOT EXISTS idx_horarios_curso    ON horarios(id_curso, id_paralelo);
CREATE INDEX IF NOT EXISTS idx_est_curso         ON estudiantes(id_curso, id_paralelo);
