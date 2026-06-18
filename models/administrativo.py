def contar(cur):
    cur.execute("SELECT COUNT(*) FROM administrativos")
    return cur.fetchone()[0]


def obtener_todos(cur):
    cur.execute("""
        SELECT id_administrativo, nombres, apellidos, ci, cargo
        FROM administrativos
        ORDER BY id_administrativo
    """)
    return cur.fetchall()


def obtener_por_id(cur, id_administrativo):
    cur.execute("""
        SELECT id_administrativo, nombres, apellidos, ci, cargo, id_usuario
        FROM administrativos WHERE id_administrativo=%s
    """, (id_administrativo,))
    return cur.fetchone()


def obtener_por_usuario(cur, id_usuario):
    cur.execute("""
        SELECT nombres, apellidos, ci, cargo
        FROM administrativos WHERE id_usuario=%s
    """, (id_usuario,))
    return cur.fetchone()


def crear(cur, nombres, apellidos, ci, cargo, id_usuario):
    cur.execute("""
        INSERT INTO administrativos(nombres, apellidos, ci, cargo, id_usuario)
        VALUES (%s,%s,%s,%s,%s)
    """, (nombres, apellidos, ci, cargo, id_usuario))


def editar(cur, id_administrativo, nombres, apellidos, ci, cargo):
    cur.execute("""
        UPDATE administrativos
        SET nombres=%s, apellidos=%s, ci=%s, cargo=%s
        WHERE id_administrativo=%s
    """, (nombres, apellidos, ci, cargo, id_administrativo))


def eliminar(cur, id_administrativo):
    cur.execute(
        "DELETE FROM administrativos WHERE id_administrativo=%s",
        (id_administrativo,)
    )
