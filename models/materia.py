def contar(cur):
    cur.execute("SELECT COUNT(*) FROM materias")
    return cur.fetchone()[0]


def obtener_todas(cur):
    cur.execute("SELECT id_materia, nombre_materia FROM materias ORDER BY id_materia")
    return cur.fetchall()


def crear(cur, nombre_materia):
    cur.execute(
        "INSERT INTO materias(nombre_materia) VALUES (%s)",
        (nombre_materia,)
    )


def editar(cur, id_materia, nombre_materia):
    cur.execute(
        "UPDATE materias SET nombre_materia=%s WHERE id_materia=%s",
        (nombre_materia, id_materia)
    )


def eliminar(cur, id_materia):
    cur.execute("DELETE FROM materias WHERE id_materia=%s", (id_materia,))
