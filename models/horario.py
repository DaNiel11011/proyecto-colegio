def contar(cur):
    cur.execute("SELECT COUNT(*) FROM horarios")
    return cur.fetchone()[0]


def obtener_todos(cur):
    cur.execute("""
        SELECT h.id_horario,
               p.nombres || ' ' || p.apellidos AS profesor,
               m.nombre_materia, a.nombre_aula,
               c.nombre_curso, pa.nombre_paralelo,
               h.dia, h.hora_inicio, h.hora_fin,
               h.id_profesor, h.id_materia, h.id_aula, h.id_curso, h.id_paralelo
        FROM horarios h
        JOIN profesores p ON h.id_profesor = p.id_profesor
        JOIN materias m   ON h.id_materia  = m.id_materia
        JOIN aulas a      ON h.id_aula     = a.id_aula
        JOIN cursos c     ON h.id_curso    = c.id_curso
        JOIN paralelos pa ON h.id_paralelo = pa.id_paralelo
        ORDER BY h.id_horario
    """)
    return cur.fetchall()


def obtener_por_profesor(cur, id_profesor):
    cur.execute("""
        SELECT h.id_horario, m.nombre_materia, a.nombre_aula,
               c.nombre_curso, pa.nombre_paralelo,
               h.dia, h.hora_inicio, h.hora_fin
        FROM horarios h
        JOIN materias m   ON h.id_materia  = m.id_materia
        JOIN aulas a      ON h.id_aula     = a.id_aula
        JOIN cursos c     ON h.id_curso    = c.id_curso
        JOIN paralelos pa ON h.id_paralelo = pa.id_paralelo
        WHERE h.id_profesor=%s
        ORDER BY h.dia, h.hora_inicio
    """, (id_profesor,))
    return cur.fetchall()


def verificar_conflicto(cur, id_aula, dia, hora_inicio, hora_fin, excluir_id=None):
    if excluir_id:
        cur.execute("""
            SELECT COUNT(*) FROM horarios
            WHERE id_aula=%s AND dia=%s
              AND hora_inicio < %s AND hora_fin > %s
              AND id_horario != %s
        """, (id_aula, dia, hora_fin, hora_inicio, excluir_id))
    else:
        cur.execute("""
            SELECT COUNT(*) FROM horarios
            WHERE id_aula=%s AND dia=%s
              AND hora_inicio < %s AND hora_fin > %s
        """, (id_aula, dia, hora_fin, hora_inicio))
    return cur.fetchone()[0] > 0


def obtener_por_estudiante(cur, id_curso, id_paralelo):
    cur.execute("""
        SELECT h.dia, h.hora_inicio, h.hora_fin,
               m.nombre_materia, a.nombre_aula,
               pr.nombres || ' ' || pr.apellidos AS profesor
        FROM horarios h
        JOIN materias m    ON h.id_materia  = m.id_materia
        JOIN aulas a       ON h.id_aula     = a.id_aula
        JOIN profesores pr ON h.id_profesor = pr.id_profesor
        WHERE h.id_curso=%s AND h.id_paralelo=%s
        ORDER BY h.dia, h.hora_inicio
    """, (id_curso, id_paralelo))
    return cur.fetchall()


def crear(cur, id_profesor, id_materia, id_aula, id_curso, id_paralelo, dia, hora_inicio, hora_fin):
    cur.execute("""
        INSERT INTO horarios(id_profesor, id_materia, id_aula, id_curso,
                              id_paralelo, dia, hora_inicio, hora_fin)
        VALUES (%s,%s,%s,%s,%s,%s,%s,%s)
    """, (id_profesor, id_materia, id_aula, id_curso, id_paralelo, dia, hora_inicio, hora_fin))


def editar(cur, id_horario, id_profesor, id_materia, id_aula, id_curso, id_paralelo, dia, hora_inicio, hora_fin):
    cur.execute("""
        UPDATE horarios
        SET id_profesor=%s, id_materia=%s, id_aula=%s, id_curso=%s,
            id_paralelo=%s, dia=%s, hora_inicio=%s, hora_fin=%s
        WHERE id_horario=%s
    """, (id_profesor, id_materia, id_aula, id_curso, id_paralelo, dia, hora_inicio, hora_fin, id_horario))


def eliminar(cur, id_horario):
    cur.execute("DELETE FROM horarios WHERE id_horario=%s", (id_horario,))
