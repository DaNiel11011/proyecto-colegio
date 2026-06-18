def contar(cur):
    cur.execute("SELECT COUNT(*) FROM notas")
    return cur.fetchone()[0]


def obtener_todas(cur):
    cur.execute("""
        SELECT n.id_nota,
               e.nombres || ' ' || e.apellidos AS estudiante,
               m.nombre_materia, t.nombre_tipo,
               n.nota, n.periodo,
               n.id_estudiante, n.id_materia, n.id_tipo_evaluacion
        FROM notas n
        JOIN estudiantes e        ON n.id_estudiante = e.id_estudiante
        JOIN materias m            ON n.id_materia = m.id_materia
        JOIN tipos_evaluacion t     ON n.id_tipo_evaluacion = t.id_tipo_evaluacion
        ORDER BY n.id_nota
    """)
    return cur.fetchall()


def obtener_por_estudiante(cur, id_estudiante):
    # Todas las actividades del curso/paralelo del estudiante, con nota si existe
    cur.execute("""
        SELECT
            m.nombre_materia,
            a.nombre   AS nombre_actividad,
            n.nota,
            a.periodo
        FROM actividades a
        JOIN materias m    ON a.id_materia  = m.id_materia
        JOIN profesores p  ON a.id_profesor = p.id_profesor
        LEFT JOIN notas n  ON n.id_estudiante = %s
                          AND n.id_actividad  = a.id_actividad
        WHERE p.id_curso = (
            SELECT id_curso FROM estudiantes WHERE id_estudiante = %s
        )
        AND p.id_paralelo = (
            SELECT id_paralelo FROM estudiantes WHERE id_estudiante = %s
        )
        ORDER BY m.nombre_materia, a.periodo, a.id_actividad
    """, (id_estudiante, id_estudiante, id_estudiante))
    return cur.fetchall()


def obtener_por_profesor(cur, id_profesor):
    # CROSS JOIN: todos los estudiantes del profesor × todas sus actividades,
    # LEFT JOIN a notas para que aparezcan aunque no tengan nota aún.
    cur.execute("""
        SELECT
            e.nombres || ' ' || e.apellidos AS estudiante,
            c.nombre_curso,
            pa.nombre_paralelo,
            a.nombre           AS nombre_actividad,
            t.nombre_tipo,
            n.nota,
            a.periodo
        FROM (
            SELECT DISTINCT e2.id_estudiante, e2.nombres, e2.apellidos,
                            e2.id_curso, e2.id_paralelo
            FROM estudiantes e2
            JOIN profesores p ON p.id_curso    = e2.id_curso
                             AND p.id_paralelo = e2.id_paralelo
            WHERE p.id_profesor = %s
        ) e
        CROSS JOIN actividades a
        JOIN tipos_evaluacion t ON a.id_tipo_evaluacion = t.id_tipo_evaluacion
        JOIN cursos   c  ON e.id_curso    = c.id_curso
        JOIN paralelos pa ON e.id_paralelo = pa.id_paralelo
        LEFT JOIN notas n ON n.id_estudiante = e.id_estudiante
                         AND n.id_actividad  = a.id_actividad
        WHERE a.id_profesor = %s
        ORDER BY e.apellidos, e.nombres, a.periodo, a.id_actividad
    """, (id_profesor, id_profesor))
    return cur.fetchall()


def obtener_tipos(cur):
    cur.execute("SELECT id_tipo_evaluacion, nombre_tipo FROM tipos_evaluacion ORDER BY id_tipo_evaluacion")
    return cur.fetchall()


def obtener_por_actividad(cur, id_actividad):
    cur.execute("""
        SELECT n.id_nota, e.nombres || ' ' || e.apellidos AS estudiante, n.nota
        FROM notas n
        JOIN estudiantes e ON n.id_estudiante = e.id_estudiante
        WHERE n.id_actividad = %s
        ORDER BY e.apellidos, e.nombres
    """, (id_actividad,))
    return cur.fetchall()


def crear(cur, id_estudiante, id_materia, id_tipo_evaluacion, nota, periodo, id_actividad=None):
    cur.execute("""
        INSERT INTO notas(id_estudiante, id_materia, id_tipo_evaluacion, nota, periodo, id_actividad)
        VALUES (%s,%s,%s,%s,%s,%s)
    """, (id_estudiante, id_materia, id_tipo_evaluacion, nota, periodo, id_actividad))


def editar(cur, id_nota, id_estudiante, id_materia, id_tipo_evaluacion, nota, periodo):
    cur.execute("""
        UPDATE notas
        SET id_estudiante=%s, id_materia=%s, id_tipo_evaluacion=%s, nota=%s, periodo=%s
        WHERE id_nota=%s
    """, (id_estudiante, id_materia, id_tipo_evaluacion, nota, periodo, id_nota))


def eliminar(cur, id_nota):
    cur.execute("DELETE FROM notas WHERE id_nota=%s", (id_nota,))
