def obtener_por_profesor(cur, id_profesor):
    cur.execute("""
        SELECT a.id_actividad, a.nombre, m.nombre_materia, t.nombre_tipo, a.periodo,
               a.id_materia, a.id_tipo_evaluacion
        FROM actividades a
        JOIN materias m            ON a.id_materia         = m.id_materia
        JOIN tipos_evaluacion t    ON a.id_tipo_evaluacion = t.id_tipo_evaluacion
        WHERE a.id_profesor = %s
        ORDER BY a.periodo, m.nombre_materia, a.id_actividad
    """, (id_profesor,))
    return cur.fetchall()


def obtener_por_id(cur, id_actividad):
    cur.execute("""
        SELECT id_actividad, nombre, id_materia, id_tipo_evaluacion, periodo, id_profesor
        FROM actividades WHERE id_actividad = %s
    """, (id_actividad,))
    return cur.fetchone()


def crear(cur, id_profesor, id_materia, id_tipo_evaluacion, nombre, periodo):
    cur.execute("""
        INSERT INTO actividades(id_profesor, id_materia, id_tipo_evaluacion, nombre, periodo)
        VALUES (%s, %s, %s, %s, %s)
    """, (id_profesor, id_materia, id_tipo_evaluacion, nombre, periodo))


def eliminar(cur, id_actividad):
    cur.execute("DELETE FROM actividades WHERE id_actividad = %s", (id_actividad,))
