def contar(cur):
    cur.execute("SELECT COUNT(*) FROM aulas")
    return cur.fetchone()[0]


def obtener_todas(cur):
    cur.execute("""
        SELECT id_aula, nombre_aula, capacidad, tipo
        FROM aulas ORDER BY id_aula
    """)
    return cur.fetchall()


def crear(cur, nombre_aula, capacidad, tipo):
    cur.execute("""
        INSERT INTO aulas(nombre_aula, capacidad, tipo)
        VALUES (%s,%s,%s)
    """, (nombre_aula, capacidad, tipo))


def editar(cur, id_aula, nombre_aula, capacidad, tipo):
    cur.execute("""
        UPDATE aulas
        SET nombre_aula=%s, capacidad=%s, tipo=%s
        WHERE id_aula=%s
    """, (nombre_aula, capacidad, tipo, id_aula))


def eliminar(cur, id_aula):
    cur.execute("DELETE FROM aulas WHERE id_aula=%s", (id_aula,))
