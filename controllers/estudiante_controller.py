from flask import Blueprint, render_template, session, redirect
from db import conectar
from models import estudiante, nota, horario

estudiante_bp = Blueprint("estudiante", __name__)


@estudiante_bp.route("/estudiante")
def panel_estudiante():
    if session.get("rol") != "ESTUDIANTE":
        return redirect("/")

    id_usuario = session.get("id_usuario")

    conn = conectar()
    cur = conn.cursor()
    datos = estudiante.obtener_por_usuario(cur, id_usuario)
    id_estudiante = estudiante.obtener_id_por_usuario(cur, id_usuario)
    mis_notas = nota.obtener_por_estudiante(cur, id_estudiante)
    mi_horario = []
    if datos:
        id_curso    = datos[6]
        id_paralelo = datos[7]
        mi_horario  = horario.obtener_por_estudiante(cur, id_curso, id_paralelo)
    cur.close()
    conn.close()

    # Agrupar: materia → periodo → lista (nombre_actividad, nota|None)
    # [0]=materia [1]=nombre_actividad [2]=nota [3]=periodo
    notas_por_materia = {}
    for n in mis_notas:
        mat      = n[0]
        act_nom  = n[1]
        nota_raw = n[2]
        nota_val = float(nota_raw) if nota_raw is not None else 0.0
        per      = n[3]

        if mat not in notas_por_materia:
            notas_por_materia[mat] = {'periodos': {}, 'nota_final': 0.0}
        if per not in notas_por_materia[mat]['periodos']:
            notas_por_materia[mat]['periodos'][per] = {'notas': [], 'suma': 0.0}
        notas_por_materia[mat]['periodos'][per]['notas'].append((act_nom, nota_val))
        notas_por_materia[mat]['periodos'][per]['suma'] += nota_val

    PESOS = {'1er Trimestre': 30, '2do Trimestre': 30, '3er Trimestre': 40}
    for mat in notas_por_materia:
        nota_final = 0.0
        for per in notas_por_materia[mat]['periodos']:
            d = notas_por_materia[mat]['periodos'][per]
            d['promedio'] = round(d['suma'] / len(d['notas']), 2)
            peso = PESOS.get(per, 0)
            d['peso'] = peso
            d['contribucion'] = round(d['promedio'] / 100 * peso, 2)
            nota_final += d['contribucion']
        notas_por_materia[mat]['nota_final'] = round(nota_final, 2)

    return render_template(
        "dashboard_estudiante.html",
        datos=datos,
        mis_notas=mis_notas,
        notas_por_materia=notas_por_materia,
        mi_horario=mi_horario,
    )
