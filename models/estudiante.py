def contar(cur):
    cur.execute("SELECT COUNT(*) FROM estudiantes")
    return cur.fetchone()[0]


def obtener_todos(cur):
    cur.execute("""
        SELECT e.id_estudiante, e.nombres, e.apellidos, e.ci,
               e.fecha_nacimiento, c.nombre_curso, p.nombre_paralelo,
               e.id_curso, e.id_paralelo, e.id_usuario
        FROM estudiantes e
        JOIN cursos c ON e.id_curso = c.id_curso
        JOIN paralelos p ON e.id_paralelo = p.id_paralelo
        ORDER BY e.id_estudiante
    """)
    return cur.fetchall()


def obtener_por_id(cur, id_estudiante):
    cur.execute("""
        SELECT id_estudiante, nombres, apellidos, ci,
               fecha_nacimiento, id_curso, id_paralelo, id_usuario
        FROM estudiantes WHERE id_estudiante=%s
    """, (id_estudiante,))
    return cur.fetchone()


def obtener_por_usuario(cur, id_usuario):
    cur.execute("""
        SELECT e.nombres, e.apellidos, e.ci, e.fecha_nacimiento,
               c.nombre_curso, p.nombre_paralelo, e.id_curso, e.id_paralelo
        FROM estudiantes e
        JOIN cursos c ON e.id_curso = c.id_curso
        JOIN paralelos p ON e.id_paralelo = p.id_paralelo
        WHERE e.id_usuario=%s
    """, (id_usuario,))
    return cur.fetchone()


def obtener_por_profesor(cur, id_profesor):
    cur.execute("""
        SELECT e.id_estudiante, e.nombres, e.apellidos, e.ci,
               e.fecha_nacimiento, c.nombre_curso, pa.nombre_paralelo
        FROM estudiantes e
        JOIN cursos c     ON e.id_curso    = c.id_curso
        JOIN paralelos pa ON e.id_paralelo = pa.id_paralelo
        JOIN profesores p ON p.id_curso = e.id_curso AND p.id_paralelo = e.id_paralelo
        WHERE p.id_profesor = %s
        ORDER BY e.apellidos, e.nombres
    """, (id_profesor,))
    return cur.fetchall()


def obtener_id_por_usuario(cur, id_usuario):
    cur.execute("SELECT id_estudiante FROM estudiantes WHERE id_usuario=%s", (id_usuario,))
    row = cur.fetchone()
    return row[0] if row else None


def crear(cur, nombres, apellidos, ci, fecha, id_curso, id_paralelo, id_usuario):
    cur.execute("""
        INSERT INTO estudiantes(nombres, apellidos, ci, fecha_nacimiento,
                                id_curso, id_paralelo, id_usuario)
        VALUES (%s,%s,%s,%s,%s,%s,%s)
    """, (nombres, apellidos, ci, fecha, id_curso, id_paralelo, id_usuario))


def editar(cur, id_estudiante, nombres, apellidos, fecha, id_curso, id_paralelo):
    cur.execute("""
        UPDATE estudiantes
        SET nombres=%s, apellidos=%s, fecha_nacimiento=%s,
            id_curso=%s, id_paralelo=%s
        WHERE id_estudiante=%s
    """, (nombres, apellidos, fecha, id_curso, id_paralelo, id_estudiante))


def eliminar(cur, id_estudiante):
    cur.execute("DELETE FROM estudiantes WHERE id_estudiante=%s", (id_estudiante,))
