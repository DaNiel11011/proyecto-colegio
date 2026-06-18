def obtener_todos(cur):
    cur.execute("SELECT id_paralelo, nombre_paralelo FROM paralelos ORDER BY id_paralelo")
    return cur.fetchall()


def crear(cur, nombre):
    cur.execute(
        "INSERT INTO paralelos(nombre_paralelo) VALUES (%s)",
        (nombre,)
    )


def editar(cur, id_paralelo, nombre):
    cur.execute(
        "UPDATE paralelos SET nombre_paralelo=%s WHERE id_paralelo=%s",
        (nombre, id_paralelo)
    )


def eliminar(cur, id):
    cur.execute("DELETE FROM paralelos WHERE id_paralelo=%s", (id,))
