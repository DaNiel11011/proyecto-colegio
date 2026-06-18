from flask import Blueprint, render_template, session, redirect
from db import conectar
from models import (estudiante, profesor, paralelo, curso,
                    materia, aula, administrativo, usuario,
                    horario, nota, profesor_materia)

administrativo_bp = Blueprint("administrativo", __name__)


@administrativo_bp.route("/administrativo")
def panel_administrativo():
    if session.get("rol") != "ADMINISTRATIVO":
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

    profesores_list   = profesor.obtener_todos(cur)
    estudiantes_list  = estudiante.obtener_todos(cur)
    administrativos   = administrativo.obtener_todos(cur)
    materias_list     = materia.obtener_todas(cur)
    aulas_list        = aula.obtener_todas(cur)
    cursos_list       = curso.obtener_todos(cur)
    paralelos_list    = paralelo.obtener_todos(cur)
    horarios_list     = horario.obtener_todos(cur)
    notas_list        = nota.obtener_todas(cur)
    tipos_evaluacion  = nota.obtener_tipos(cur)

    materias_por_profesor = {}
    for p in profesores_list:
        materias_por_profesor[p[0]] = profesor_materia.obtener_por_profesor(cur, p[0])

    cur.close()
    conn.close()

    PESOS = {'1er Trimestre': 30, '2do Trimestre': 30, '3er Trimestre': 40}
    resumen_notas = {}
    for n in notas_list:
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
                d['contribucion'] = round(d['promedio'] / 100 * peso, 2)
                nota_final += d['contribucion']
            resumen_notas[est][mat]['nota_final'] = round(nota_final, 2)

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
        estudiantes=estudiantes_list,
        profesores=profesores_list,
        administrativos=administrativos,
        materias=materias_list,
        aulas=aulas_list,
        cursos=cursos_list,
        paralelos=paralelos_list,
        horarios=horarios_list,
        notas=notas_list,
        tipos_evaluacion=tipos_evaluacion,
        materias_por_profesor=materias_por_profesor,
        resumen_notas=resumen_notas,
        tabla_notas=tabla_notas,
        es_admin=(session.get("rol") == "ADMIN"),
    )
