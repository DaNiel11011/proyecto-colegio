def obtener_por_profesor(cur, id_profesor):
    cur.execute("""
        SELECT m.id_materia, m.nombre_materia
        FROM profesor_materia pm
        JOIN materias m ON pm.id_materia = m.id_materia
        WHERE pm.id_profesor=%s
        ORDER BY m.nombre_materia
    """, (id_profesor,))
    return cur.fetchall()


def asignar(cur, id_profesor, id_materia):
    cur.execute("""
        INSERT INTO profesor_materia(id_profesor, id_materia)
        VALUES (%s,%s)
        ON CONFLICT DO NOTHING
    """, (id_profesor, id_materia))


def quitar(cur, id_profesor, id_materia):
    cur.execute("""
        DELETE FROM profesor_materia
        WHERE id_profesor=%s AND id_materia=%s
    """, (id_profesor, id_materia))
