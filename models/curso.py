def obtener_todos(cur):
    cur.execute("SELECT id_curso, nombre_curso FROM cursos ORDER BY id_curso")
    return cur.fetchall()


def crear(cur, nombre_curso):
    cur.execute(
        "INSERT INTO cursos(nombre_curso) VALUES (%s)",
        (nombre_curso,)
    )


def editar(cur, id_curso, nombre_curso):
    cur.execute(
        "UPDATE cursos SET nombre_curso=%s WHERE id_curso=%s",
        (nombre_curso, id_curso)
    )


def eliminar(cur, id_curso):
    cur.execute("DELETE FROM cursos WHERE id_curso=%s", (id_curso,))
