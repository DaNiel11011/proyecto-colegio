from flask import Blueprint, render_template, request, session, redirect
from db import conectar
from models import profesor, profesor_materia, horario, nota, estudiante, curso, paralelo, actividad

profesor_bp = Blueprint("profesor", __name__)


@profesor_bp.route("/profesor")
def panel_profesor():
    if session.get("rol") != "PROFESOR":
        return redirect("/")

    id_usuario = session.get("id_usuario")

    conn = conectar()
    cur = conn.cursor()
    datos = profesor.obtener_por_usuario(cur, id_usuario)
    id_profesor = profesor.obtener_id_por_usuario(cur, id_usuario)

    materias = profesor_materia.obtener_por_profesor(cur, id_profesor)
    mi_horario = horario.obtener_por_profesor(cur, id_profesor)
    estudiantes = estudiante.obtener_todos(cur)
    tipos_evaluacion = nota.obtener_tipos(cur)
    notas_alumnos = nota.obtener_por_profesor(cur, id_profesor)
    mis_estudiantes = estudiante.obtener_por_profesor(cur, id_profesor)
    mis_actividades = actividad.obtener_por_profesor(cur, id_profesor)
    notas_por_actividad = {act[0]: nota.obtener_por_actividad(cur, act[0]) for act in mis_actividades}

    cur.close()
    conn.close()

    # Agrupar: estudiante → periodo → lista de (nombre_actividad, nota|None)
    # [0]=estudiante [1]=curso [2]=paralelo [3]=nombre_actividad [4]=tipo [5]=nota [6]=periodo
    notas_por_estudiante = {}
    for n in notas_alumnos:
        est      = n[0]
        cur_n    = n[1]
        par_n    = n[2]
        act_nom  = n[3]
        nota_raw = n[5]
        nota_val = float(nota_raw) if nota_raw is not None else 0.0
        per      = n[6]

        if est not in notas_por_estudiante:
            notas_por_estudiante[est] = {'curso': cur_n, 'paralelo': par_n, 'periodos': {}, 'nota_final': 0.0}
        if per not in notas_por_estudiante[est]['periodos']:
            notas_por_estudiante[est]['periodos'][per] = {'notas': [], 'suma': 0.0}
        notas_por_estudiante[est]['periodos'][per]['notas'].append((act_nom, nota_val))
        notas_por_estudiante[est]['periodos'][per]['suma'] += nota_val

    PESOS = {'1er Trimestre': 30, '2do Trimestre': 30, '3er Trimestre': 40}
    for est in notas_por_estudiante:
        nota_final = 0.0
        for per in notas_por_estudiante[est]['periodos']:
            d = notas_por_estudiante[est]['periodos'][per]
            d['promedio'] = round(d['suma'] / len(d['notas']), 2)
            peso = PESOS.get(per, 0)
            d['peso'] = peso
            d['contribucion'] = round(d['promedio'] / 100 * peso, 2)
            nota_final += d['contribucion']
        notas_por_estudiante[est]['nota_final'] = round(nota_final, 2)

    return render_template(
        "dashboard_profesor.html",
        datos=datos,
        materias=materias,
        mi_horario=mi_horario,
        estudiantes=estudiantes,
        tipos_evaluacion=tipos_evaluacion,
        id_profesor=id_profesor,
        notas_alumnos=notas_alumnos,
        notas_por_estudiante=notas_por_estudiante,
        mis_estudiantes=mis_estudiantes,
        mis_actividades=mis_actividades,
        notas_por_actividad=notas_por_actividad,
    )


@profesor_bp.route("/profesor/editar_nota/<int:id_nota>", methods=["POST"])
def editar_nota_profesor(id_nota):
    if session.get("rol") != "PROFESOR":
        return redirect("/")
    valor_nota = request.form["nota"]
    conn = conectar()
    cur = conn.cursor()
    cur.execute("UPDATE notas SET nota=%s WHERE id_nota=%s", (valor_nota, id_nota))
    conn.commit()
    cur.close()
    conn.close()
    return redirect("/profesor?seccion=notas")


@profesor_bp.route("/profesor/eliminar_nota/<int:id_nota>")
def eliminar_nota_profesor(id_nota):
    if session.get("rol") != "PROFESOR":
        return redirect("/")
    conn = conectar()
    cur = conn.cursor()
    nota.eliminar(cur, id_nota)
    conn.commit()
    cur.close()
    conn.close()
    return redirect("/profesor?seccion=notas")


@profesor_bp.route("/profesor/crear_actividad", methods=["POST"])
def crear_actividad():
    if session.get("rol") != "PROFESOR":
        return redirect("/")

    id_usuario  = session.get("id_usuario")
    id_materia  = request.form["id_materia"]
    id_tipo     = request.form["id_tipo_evaluacion"]
    nombre      = request.form["nombre_actividad"]
    periodo     = request.form["periodo"]

    conn = conectar()
    cur = conn.cursor()
    id_prof = profesor.obtener_id_por_usuario(cur, id_usuario)
    actividad.crear(cur, id_prof, id_materia, id_tipo, nombre, periodo)
    conn.commit()
    cur.close()
    conn.close()
    return redirect("/profesor?seccion=notas")


@profesor_bp.route("/profesor/eliminar_actividad/<int:id_act>")
def eliminar_actividad(id_act):
    if session.get("rol") != "PROFESOR":
        return redirect("/")
    conn = conectar()
    cur = conn.cursor()
    cur.execute("DELETE FROM notas WHERE id_actividad = %s", (id_act,))
    actividad.eliminar(cur, id_act)
    conn.commit()
    cur.close()
    conn.close()
    return redirect("/profesor?seccion=notas")


@profesor_bp.route("/profesor/registrar_nota", methods=["POST"])
def registrar_nota():
    if session.get("rol") != "PROFESOR":
        return redirect("/")

    id_actividad  = request.form["id_actividad"]
    id_estudiante = request.form["id_estudiante"]
    valor_nota    = request.form["nota"]

    conn = conectar()
    cur = conn.cursor()
    act = actividad.obtener_por_id(cur, id_actividad)
    nota.crear(cur, id_estudiante, act[2], act[3], valor_nota, act[4], id_actividad)
    conn.commit()
    cur.close()
    conn.close()
    return redirect("/profesor?seccion=notas")
