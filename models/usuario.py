def obtener_por_credenciales(cur, username, password):
    cur.execute("""
        SELECT r.nombre_rol, u.id_usuario
        FROM usuarios u
        INNER JOIN roles r ON u.id_rol = r.id_rol
        WHERE u.nombre_usuario=%s AND u.password=%s AND u.estado=TRUE
    """, (username, password))
    return cur.fetchone()


def crear_usuario(cur, nombre_usuario, password, id_rol):
    cur.execute("""
        INSERT INTO usuarios(nombre_usuario, password, id_rol)
        VALUES (%s,%s,%s)
        RETURNING id_usuario
    """, (nombre_usuario, password, id_rol))
    return cur.fetchone()[0]


def eliminar_usuario(cur, id_usuario):
    cur.execute("DELETE FROM usuarios WHERE id_usuario=%s", (id_usuario,))
