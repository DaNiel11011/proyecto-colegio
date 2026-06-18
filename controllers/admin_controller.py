from flask import Blueprint, render_template, request, redirect, session
from db import conectar
from models import (estudiante, profesor, paralelo, curso,
                    materia, aula, administrativo, usuario,
                    horario, nota, profesor_materia)

admin_bp = Blueprint("admin", __name__)


# ── PANEL ADMIN ──────────────────────────────────────────────
@admin_bp.route("/admin")
def admin():
    if session.get("rol") != "ADMIN":
        return redirect("/")
    conn = conectar()
    cur = conn.cursor()

    total_estudiantes = estudiante.contar(cur)
    total_profesores  = profesor.contar(cur)
    total_materias    = materia.contar(cur)
    total_admin       = administrativo.contar(cur)
    total_aulas       = aula.contar(cur)
    total_horarios    = horario.contar(cur)
    total_notas       = nota.contar(cur)

    profesores    = profesor.obtener_todos(cur)
    estudiantes   = estudiante.obtener_todos(cur)
    administrativos = administrativo.obtener_todos(cur)
    materias      = materia.obtener_todas(cur)
    aulas         = aula.obtener_todas(cur)
    cursos        = curso.obtener_todos(cur)
    paralelos     = paralelo.obtener_todos(cur)
    horarios      = horario.obtener_todos(cur)
    notas         = nota.obtener_todas(cur)
    tipos_evaluacion = nota.obtener_tipos(cur)

    # Materias asignadas a cada profesor (relación N:M)
    materias_por_profesor = {}
    for p in profesores:
        materias_por_profesor[p[0]] = profesor_materia.obtener_por_profesor(cur, p[0])

    cur.close()
    conn.close()

    # Resumen de notas: estudiante → materia → periodos con promedio
    # notas: [0]=id [1]=estudiante [2]=materia [3]=tipo [4]=nota [5]=periodo
    PESOS = {'1er Trimestre': 30, '2do Trimestre': 30, '3er Trimestre': 40}
    resumen_notas = {}
    for n in notas:
        est, mat, per = n[1], n[2], n[5]
        nota_val = float(n[4])
        if est not in resumen_notas:
            resumen_notas[est] = {}
        if mat not in resumen_notas[est]:
            resumen_notas[est][mat] = {'periodos': {}, 'nota_final': 0.0}
        if per not in resumen_notas[est][mat]['periodos']:
            resumen_notas[est][mat]['periodos'][per] = {'suma': 0.0, 'count': 0}
        resumen_notas[est][mat]['periodos'][per]['suma']  += nota_val
        resumen_notas[est][mat]['periodos'][per]['count'] += 1
    for est in resumen_notas:
        for mat in resumen_notas[est]:
            nota_final = 0.0
            for per, d in resumen_notas[est][mat]['periodos'].items():
                d['promedio'] = round(d['suma'] / d['count'], 2)
                peso = PESOS.get(per, 0)
                d['peso'] = peso
                d['contribucion'] = round(d['promedio'] / 100 * peso, 2)
                nota_final += d['contribucion']
            resumen_notas[est][mat]['nota_final'] = round(nota_final, 2)

    # Tabla plana: est → mat → {trim1, trim2, trim3, nota_final}
    tabla_notas = {}
    for est, mats in resumen_notas.items():
        tabla_notas[est] = {}
        for mat, md in mats.items():
            p = md['periodos']
            tabla_notas[est][mat] = {
                'trim1':      p.get('1er Trimestre', {}).get('contribucion', 0),
                'trim2':      p.get('2do Trimestre', {}).get('contribucion', 0),
                'trim3':      p.get('3er Trimestre', {}).get('contribucion', 0),
                'nota_final': md['nota_final'],
            }

    return render_template(
        "dashboard_admin.html",
        total_estudiantes=total_estudiantes,
        total_profesores=total_profesores,
        total_materias=total_materias,
        total_admin=total_admin,
        total_aulas=total_aulas,
        total_horarios=total_horarios,
        total_notas=total_notas,
        estudiantes=estudiantes,
        profesores=profesores,
        administrativos=administrativos,
        materias=materias,
        aulas=aulas,
        cursos=cursos,
        paralelos=paralelos,
        horarios=horarios,
        notas=notas,
        tipos_evaluacion=tipos_evaluacion,
        materias_por_profesor=materias_por_profesor,
        resumen_notas=resumen_notas,
        tabla_notas=tabla_notas,
        es_admin=True,
    )


# ── ESTUDIANTES ───────────────────────────────────────────────
@admin_bp.route("/crear_estudiante", methods=["POST"])
def crear_estudiante():
    if session.get("rol") != "ADMIN":
        return redirect("/")
    nombres     = request.form["nombres"]
    apellidos   = request.form["apellidos"]
    ci          = request.form["ci"]
    fecha       = request.form["fecha_nacimiento"]
    id_curso    = request.form["curso"]
    id_paralelo = request.form["paralelo"]

    conn = conectar()
    cur = conn.cursor()
    id_us = usuario.crear_usuario(cur, ci, ci, 3)
    estudiante.crear(cur, nombres, apellidos, ci, fecha, id_curso, id_paralelo, id_us)
    conn.commit()
    cur.close()
    conn.close()
    return redirect("/admin?seccion=estudiantes")


@admin_bp.route("/actualizar_estudiante/<int:id>", methods=["POST"])
def actualizar_estudiante(id):
    if session.get("rol") != "ADMIN":
        return redirect("/")
    nombres     = request.form["nombres"]
    apellidos   = request.form["apellidos"]
    fecha       = request.form["fecha_nacimiento"]
    id_curso    = request.form["curso"]
    id_paralelo = request.form["paralelo"]

    conn = conectar()
    cur = conn.cursor()
    estudiante.editar(cur, id, nombres, apellidos, fecha, id_curso, id_paralelo)
    conn.commit()
    cur.close()
    conn.close()
    return redirect("/admin?seccion=estudiantes")


@admin_bp.route("/eliminar_estudiante/<int:id>")
def eliminar_estudiante(id):
    if session.get("rol") != "ADMIN":
        return redirect("/")
    conn = conectar()
    cur = conn.cursor()
    datos = estudiante.obtener_por_id(cur, id)
    id_us = datos[7] if datos else None
    cur.execute("DELETE FROM notas WHERE id_estudiante=%s", (id,))
    estudiante.eliminar(cur, id)
    if id_us:
        usuario.eliminar_usuario(cur, id_us)
    conn.commit()
    cur.close()
    conn.close()
    return redirect("/admin?seccion=estudiantes")


# ── PROFESORES ────────────────────────────────────────────────
@admin_bp.route("/crear_profesor", methods=["POST"])
def crear_profesor():
    if session.get("rol") != "ADMIN":
        return redirect("/")
    nombres    = request.form["nombres"]
    apellidos  = request.form["apellidos"]
    ci         = request.form["ci"]
    fecha      = request.form["fecha_nacimiento"]
    id_mat     = request.form["id_materia"]
    id_par     = request.form.get("id_paralelo") or None
    id_cur     = request.form.get("id_curso") or None

    conn = conectar()
    cur = conn.cursor()
    id_us = usuario.crear_usuario(cur, ci, ci, 2)
    profesor.crear(cur, nombres, apellidos, ci, fecha, id_mat, id_us, id_par, id_cur)
    cur.execute("SELECT id_profesor FROM profesores WHERE id_usuario=%s", (id_us,))
    id_prof = cur.fetchone()[0]
    profesor_materia.asignar(cur, id_prof, id_mat)
    conn.commit()
    cur.close()
    conn.close()
    return redirect("/admin?seccion=profesores")


@admin_bp.route("/actualizar_profesor/<int:id>", methods=["POST"])
def actualizar_profesor(id):
    if session.get("rol") != "ADMIN":
        return redirect("/")
    nombres   = request.form["nombres"]
    apellidos = request.form["apellidos"]
    fecha     = request.form["fecha_nacimiento"]
    id_mat    = request.form["id_materia"]
    id_par    = request.form.get("id_paralelo") or None
    id_cur    = request.form.get("id_curso") or None

    conn = conectar()
    cur = conn.cursor()
    profesor.editar(cur, id, nombres, apellidos, fecha, id_mat, id_par, id_cur)
    conn.commit()
    cur.close()
    conn.close()
    return redirect("/admin?seccion=profesores")


@admin_bp.route("/eliminar_profesor/<int:id>")
def eliminar_profesor(id):
    if session.get("rol") != "ADMIN":
        return redirect("/")
    conn = conectar()
    cur = conn.cursor()
    datos = profesor.obtener_por_id(cur, id)
    id_us = datos[6] if datos else None
    cur.execute("DELETE FROM profesor_materia WHERE id_profesor=%s", (id,))
    cur.execute("DELETE FROM horarios WHERE id_profesor=%s", (id,))
    profesor.eliminar(cur, id)
    if id_us:
        usuario.eliminar_usuario(cur, id_us)
    conn.commit()
    cur.close()
    conn.close()
    return redirect("/admin?seccion=profesores")


# ── ADMINISTRATIVOS ───────────────────────────────────────────
@admin_bp.route("/crear_administrativo", methods=["POST"])
def crear_administrativo():
    if session.get("rol") != "ADMIN":
        return redirect("/")
    nombres   = request.form["nombres"]
    apellidos = request.form["apellidos"]
    ci        = request.form["ci"]
    cargo     = request.form["cargo"]

    conn = conectar()
    cur = conn.cursor()
    id_us = usuario.crear_usuario(cur, ci, ci, 4)
    administrativo.crear(cur, nombres, apellidos, ci, cargo, id_us)
    conn.commit()
    cur.close()
    conn.close()
    return redirect("/admin?seccion=administrativos")


@admin_bp.route("/actualizar_administrativo/<int:id>", methods=["POST"])
def actualizar_administrativo(id):
    if session.get("rol") != "ADMIN":
        return redirect("/")
    nombres   = request.form["nombres"]
    apellidos = request.form["apellidos"]
    ci        = request.form["ci"]
    cargo     = request.form["cargo"]

    conn = conectar()
    cur = conn.cursor()
    administrativo.editar(cur, id, nombres, apellidos, ci, cargo)
    conn.commit()
    cur.close()
    conn.close()
    return redirect("/admin?seccion=administrativos")


@admin_bp.route("/eliminar_administrativo/<int:id>")
def eliminar_administrativo(id):
    if session.get("rol") != "ADMIN":
        return redirect("/")
    conn = conectar()
    cur = conn.cursor()
    datos = administrativo.obtener_por_id(cur, id)
    id_us = datos[5] if datos else None
    administrativo.eliminar(cur, id)
    if id_us:
        usuario.eliminar_usuario(cur, id_us)
    conn.commit()
    cur.close()
    conn.close()
    return redirect("/admin?seccion=administrativos")


# ── MATERIAS ──────────────────────────────────────────────────
@admin_bp.route("/crear_materia", methods=["POST"])
def crear_materia():
    if session.get("rol") != "ADMIN":
        return redirect("/")
    nombre = request.form["nombre_materia"]
    conn = conectar()
    cur = conn.cursor()
    materia.crear(cur, nombre)
    conn.commit()
    cur.close()
    conn.close()
    return redirect("/admin?seccion=materias")


@admin_bp.route("/actualizar_materia/<int:id>", methods=["POST"])
def actualizar_materia(id):
    if session.get("rol") != "ADMIN":
        return redirect("/")
    nombre = request.form["nombre_materia"]
    conn = conectar()
    cur = conn.cursor()
    materia.editar(cur, id, nombre)
    conn.commit()
    cur.close()
    conn.close()
    return redirect("/admin?seccion=materias")


@admin_bp.route("/eliminar_materia/<int:id>")
def eliminar_materia(id):
    if session.get("rol") != "ADMIN":
        return redirect("/")
    conn = conectar()
    cur = conn.cursor()
    cur.execute("DELETE FROM notas WHERE id_materia=%s", (id,))
    cur.execute("DELETE FROM horarios WHERE id_materia=%s", (id,))
    cur.execute("DELETE FROM profesor_materia WHERE id_materia=%s", (id,))
    materia.eliminar(cur, id)
    conn.commit()
    cur.close()
    conn.close()
    return redirect("/admin?seccion=materias")


# ── AULAS ─────────────────────────────────────────────────────
@admin_bp.route("/crear_aula", methods=["POST"])
def crear_aula():
    if session.get("rol") != "ADMIN":
        return redirect("/")
    nombre    = request.form["nombre_aula"]
    capacidad = request.form.get("capacidad") or None
    tipo      = request.form["tipo"]
    conn = conectar()
    cur = conn.cursor()
    aula.crear(cur, nombre, capacidad, tipo)
    conn.commit()
    cur.close()
    conn.close()
    return redirect("/admin?seccion=aulas")


@admin_bp.route("/actualizar_aula/<int:id>", methods=["POST"])
def actualizar_aula(id):
    if session.get("rol") != "ADMIN":
        return redirect("/")
    nombre    = request.form["nombre_aula"]
    capacidad = request.form.get("capacidad") or None
    tipo      = request.form["tipo"]
    conn = conectar()
    cur = conn.cursor()
    aula.editar(cur, id, nombre, capacidad, tipo)
    conn.commit()
    cur.close()
    conn.close()
    return redirect("/admin?seccion=aulas")


@admin_bp.route("/eliminar_aula/<int:id>")
def eliminar_aula(id):
    if session.get("rol") != "ADMIN":
        return redirect("/")
    conn = conectar()
    cur = conn.cursor()
    aula.eliminar(cur, id)
    conn.commit()
    cur.close()
    conn.close()
    return redirect("/admin?seccion=aulas")


# ── CURSOS ────────────────────────────────────────────────────
@admin_bp.route("/crear_curso", methods=["POST"])
def crear_curso():
    if session.get("rol") != "ADMIN":
        return redirect("/")
    nombre = request.form["nombre_curso"]
    conn = conectar()
    cur = conn.cursor()
    curso.crear(cur, nombre)
    conn.commit()
    cur.close()
    conn.close()
    return redirect("/admin?seccion=settings")


@admin_bp.route("/actualizar_curso/<int:id>", methods=["POST"])
def actualizar_curso(id):
    if session.get("rol") != "ADMIN":
        return redirect("/")
    nombre = request.form["nombre_curso"]
    conn = conectar()
    cur = conn.cursor()
    curso.editar(cur, id, nombre)
    conn.commit()
    cur.close()
    conn.close()
    return redirect("/admin?seccion=settings")


@admin_bp.route("/eliminar_curso/<int:id>")
def eliminar_curso(id):
    if session.get("rol") != "ADMIN":
        return redirect("/")
    conn = conectar()
    cur = conn.cursor()
    curso.eliminar(cur, id)
    conn.commit()
    cur.close()
    conn.close()
    return redirect("/admin?seccion=settings")


# ── PARALELOS ─────────────────────────────────────────────────
@admin_bp.route("/crear_paralelo", methods=["POST"])
def crear_paralelo():
    if session.get("rol") != "ADMIN":
        return redirect("/")
    nombre = request.form["nombre_paralelo"]
    conn = conectar()
    cur = conn.cursor()
    paralelo.crear(cur, nombre)
    conn.commit()
    cur.close()
    conn.close()
    return redirect("/admin?seccion=settings")


@admin_bp.route("/actualizar_paralelo/<int:id>", methods=["POST"])
def actualizar_paralelo(id):
    if session.get("rol") != "ADMIN":
        return redirect("/")
    nombre = request.form["nombre_paralelo"]
    conn = conectar()
    cur = conn.cursor()
    paralelo.editar(cur, id, nombre)
    conn.commit()
    cur.close()
    conn.close()
    return redirect("/admin?seccion=settings")


@admin_bp.route("/eliminar_paralelo/<int:id>")
def eliminar_paralelo(id):
    if session.get("rol") != "ADMIN":
        return redirect("/")
    conn = conectar()
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM estudiantes WHERE id_paralelo=%s", (id,))
    if cur.fetchone()[0] > 0:
        cur.close()
        conn.close()
        return redirect("/admin?seccion=settings")
    cur.execute("UPDATE profesores SET id_paralelo=NULL WHERE id_paralelo=%s", (id,))
    cur.execute("DELETE FROM horarios WHERE id_paralelo=%s", (id,))
    paralelo.eliminar(cur, id)
    conn.commit()
    cur.close()
    conn.close()
    return redirect("/admin?seccion=settings")


# ── HORARIOS (asignación de aulas/laboratorios) ────────────────
@admin_bp.route("/crear_horario", methods=["POST"])
def crear_horario():
    if session.get("rol") != "ADMIN":
        return redirect("/")
    id_profesor = request.form["id_profesor"]
    id_materia  = request.form["id_materia"]
    id_aula     = request.form["id_aula"]
    id_curso    = request.form["id_curso"]
    id_paralelo = request.form["id_paralelo"]
    dia         = request.form["dia"]
    hora_inicio = request.form["hora_inicio"]
    hora_fin    = request.form["hora_fin"]

    conn = conectar()
    cur = conn.cursor()
    if horario.verificar_conflicto(cur, id_aula, dia, hora_inicio, hora_fin):
        cur.close()
        conn.close()
        return redirect("/admin?seccion=horarios&error=conflicto")
    horario.crear(cur, id_profesor, id_materia, id_aula, id_curso, id_paralelo, dia, hora_inicio, hora_fin)
    conn.commit()
    cur.close()
    conn.close()
    return redirect("/admin?seccion=horarios")


@admin_bp.route("/actualizar_horario/<int:id>", methods=["POST"])
def actualizar_horario(id):
    if session.get("rol") != "ADMIN":
        return redirect("/")
    id_profesor = request.form["id_profesor"]
    id_materia  = request.form["id_materia"]
    id_aula     = request.form["id_aula"]
    id_curso    = request.form["id_curso"]
    id_paralelo = request.form["id_paralelo"]
    dia         = request.form["dia"]
    hora_inicio = request.form["hora_inicio"]
    hora_fin    = request.form["hora_fin"]

    conn = conectar()
    cur = conn.cursor()
    if horario.verificar_conflicto(cur, id_aula, dia, hora_inicio, hora_fin, excluir_id=id):
        cur.close()
        conn.close()
        return redirect("/admin?seccion=horarios&error=conflicto")
    horario.editar(cur, id, id_profesor, id_materia, id_aula, id_curso, id_paralelo, dia, hora_inicio, hora_fin)
    conn.commit()
    cur.close()
    conn.close()
    return redirect("/admin?seccion=horarios")


@admin_bp.route("/eliminar_horario/<int:id>")
def eliminar_horario(id):
    conn = conectar()
    cur = conn.cursor()
    horario.eliminar(cur, id)
    conn.commit()
    cur.close()
    conn.close()
    return redirect("/admin?seccion=horarios")


# ── NOTAS (evaluaciones: examenes, practicas, proyectos) ───────
@admin_bp.route("/crear_nota", methods=["POST"])
def crear_nota():
    if session.get("rol") != "ADMIN":
        return redirect("/")
    id_estudiante      = request.form["id_estudiante"]
    id_materia         = request.form["id_materia"]
    id_tipo_evaluacion = request.form["id_tipo_evaluacion"]
    valor_nota         = request.form["nota"]
    periodo            = request.form["periodo"]

    conn = conectar()
    cur = conn.cursor()
    nota.crear(cur, id_estudiante, id_materia, id_tipo_evaluacion, valor_nota, periodo)
    conn.commit()
    cur.close()
    conn.close()
    return redirect("/admin?seccion=notas")


@admin_bp.route("/actualizar_nota/<int:id>", methods=["POST"])
def actualizar_nota(id):
    if session.get("rol") != "ADMIN":
        return redirect("/")
    id_estudiante      = request.form["id_estudiante"]
    id_materia         = request.form["id_materia"]
    id_tipo_evaluacion = request.form["id_tipo_evaluacion"]
    valor_nota         = request.form["nota"]
    periodo            = request.form["periodo"]

    conn = conectar()
    cur = conn.cursor()
    nota.editar(cur, id, id_estudiante, id_materia, id_tipo_evaluacion, valor_nota, periodo)
    conn.commit()
    cur.close()
    conn.close()
    return redirect("/admin?seccion=notas")


@admin_bp.route("/eliminar_nota/<int:id>")
def eliminar_nota(id):
    if session.get("rol") != "ADMIN":
        return redirect("/")
    conn = conectar()
    cur = conn.cursor()
    nota.eliminar(cur, id)
    conn.commit()
    cur.close()
    conn.close()
    return redirect("/admin?seccion=notas")


# ── PROFESOR_MATERIA (materias dictadas por cada profesor) ─────
@admin_bp.route("/asignar_materia_profesor", methods=["POST"])
def asignar_materia_profesor():
    if session.get("rol") != "ADMIN":
        return redirect("/")
    id_profesor = request.form["id_profesor"]
    id_materia  = request.form["id_materia"]

    conn = conectar()
    cur = conn.cursor()
    profesor_materia.asignar(cur, id_profesor, id_materia)
    conn.commit()
    cur.close()
    conn.close()
    return redirect("/admin?seccion=profesores")


@admin_bp.route("/quitar_materia_profesor/<int:id_profesor>/<int:id_materia>")
def quitar_materia_profesor(id_profesor, id_materia):
    if session.get("rol") != "ADMIN":
        return redirect("/")
    conn = conectar()
    cur = conn.cursor()
    profesor_materia.quitar(cur, id_profesor, id_materia)
    conn.commit()
    cur.close()
    conn.close()
    return redirect("/admin?seccion=profesores")
