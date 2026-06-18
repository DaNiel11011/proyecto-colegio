def contar(cur):
    cur.execute("SELECT COUNT(*) FROM profesores")
    return cur.fetchone()[0]


def obtener_todos(cur):
    cur.execute("""
        SELECT p.id_profesor, p.nombres, p.apellidos, p.ci,
               p.fecha_nacimiento, m.nombre_materia,
               p.id_materia, p.id_usuario,
               pa.nombre_paralelo, p.id_paralelo,
               c.nombre_curso,   p.id_curso
        FROM profesores p
        LEFT JOIN materias m   ON p.id_materia  = m.id_materia
        LEFT JOIN paralelos pa ON p.id_paralelo = pa.id_paralelo
        LEFT JOIN cursos c     ON p.id_curso    = c.id_curso
        ORDER BY p.id_profesor
    """)
    return cur.fetchall()


def obtener_por_id(cur, id_profesor):
    cur.execute("""
        SELECT id_profesor, nombres, apellidos, ci, fecha_nacimiento,
               id_materia, id_usuario, id_paralelo, id_curso
        FROM profesores WHERE id_profesor=%s
    """, (id_profesor,))
    return cur.fetchone()


def obtener_por_usuario(cur, id_usuario):
    cur.execute("""
        SELECT p.nombres, p.apellidos, p.ci, p.fecha_nacimiento,
               m.nombre_materia
        FROM profesores p
        LEFT JOIN materias m ON p.id_materia = m.id_materia
        WHERE p.id_usuario=%s
    """, (id_usuario,))
    return cur.fetchone()


def obtener_id_por_usuario(cur, id_usuario):
    cur.execute("SELECT id_profesor FROM profesores WHERE id_usuario=%s", (id_usuario,))
    row = cur.fetchone()
    return row[0] if row else None


def crear(cur, nombres, apellidos, ci, fecha, id_materia, id_usuario,
          id_paralelo=None, id_curso=None):
    cur.execute("""
        INSERT INTO profesores(nombres, apellidos, ci, fecha_nacimiento,
                               id_materia, id_usuario, id_paralelo, id_curso)
        VALUES (%s,%s,%s,%s,%s,%s,%s,%s)
    """, (nombres, apellidos, ci, fecha, id_materia, id_usuario,
          id_paralelo, id_curso))


def editar(cur, id_profesor, nombres, apellidos, fecha, id_materia,
           id_paralelo=None, id_curso=None):
    cur.execute("""
        UPDATE profesores
        SET nombres=%s, apellidos=%s, fecha_nacimiento=%s,
            id_materia=%s, id_paralelo=%s, id_curso=%s
        WHERE id_profesor=%s
    """, (nombres, apellidos, fecha, id_materia,
          id_paralelo, id_curso, id_profesor))


def eliminar(cur, id_profesor):
    cur.execute("DELETE FROM profesores WHERE id_profesor=%s", (id_profesor,))
