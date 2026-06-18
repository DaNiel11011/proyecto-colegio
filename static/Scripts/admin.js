function mostrar(seccion) {
    document.querySelectorAll('.section').forEach(s => s.classList.remove('active'));
    document.querySelectorAll('.sidebar-nav a[id]').forEach(a => a.classList.remove('active'));
    document.getElementById('sec-' + seccion).classList.add('active');
    document.getElementById('nav-' + seccion).classList.add('active');
}

function buscar(input, tablaId) {
    const q = input.value.toLowerCase();
    document.querySelectorAll('#' + tablaId + ' tbody tr').forEach(row => {
        row.style.display = row.textContent.toLowerCase().includes(q) ? '' : 'none';
    });
}

function filtrarEstNotas(input) {
    var q = input.value.toLowerCase();
    document.querySelectorAll('.est-nota-card').forEach(function(card) {
        card.style.display = card.dataset.est.includes(q) ? '' : 'none';
    });
}

function cerrarEdit(panelId) {
    document.getElementById(panelId).style.display = 'none';
}
function abrirEdit(panelId) {
    document.getElementById(panelId).style.display = 'block';
    document.getElementById(panelId).scrollIntoView({ behavior: 'smooth' });
}

function editProfesorBtn(btn) {
    var d = btn.dataset;
    document.getElementById('ep-nombres').value   = d.nombres;
    document.getElementById('ep-apellidos').value = d.apellidos;
    document.getElementById('ep-fecha').value     = d.fecha;
    document.getElementById('ep-materia').value   = d.materia;
    document.getElementById('ep-curso').value     = parseInt(d.curso) || '';
    document.getElementById('ep-paralelo').value  = parseInt(d.paralelo) || '';
    document.getElementById('form-edit-profesor').action = '/actualizar_profesor/' + d.id;
    abrirEdit('edit-panel-profesor');
}

function autocompletarHorario(sel) {
    var opt = sel.options[sel.selectedIndex];
    var mat = opt.dataset.materia, cur = opt.dataset.curso, par = opt.dataset.paralelo;
    var selMat = document.getElementById('nh-materia');
    var selCur = document.getElementById('nh-curso');
    var selPar = document.getElementById('nh-paralelo');
    if (mat) selMat.value = mat; else selMat.selectedIndex = 0;
    if (cur) selCur.value = cur; else selCur.selectedIndex = 0;
    if (par) selPar.value = par; else selPar.selectedIndex = 0;
}

function editEstudiante(id, nombres, apellidos, fecha, idCurso, idParalelo) {
    document.getElementById('ee-nombres').value   = nombres;
    document.getElementById('ee-apellidos').value = apellidos;
    document.getElementById('ee-fecha').value     = fecha;
    document.getElementById('ee-curso').value     = idCurso;
    document.getElementById('ee-paralelo').value  = idParalelo;
    document.getElementById('form-edit-estudiante').action = '/actualizar_estudiante/' + id;
    abrirEdit('edit-panel-estudiante');
}

function editAdmin(id, nombres, apellidos, ci, cargo) {
    document.getElementById('ea-nombres').value   = nombres;
    document.getElementById('ea-apellidos').value = apellidos;
    document.getElementById('ea-ci').value        = ci;
    document.getElementById('ea-cargo').value     = cargo;
    document.getElementById('form-edit-admin').action = '/actualizar_administrativo/' + id;
    abrirEdit('edit-panel-admin');
}

function editMateria(id, nombre) {
    document.getElementById('em-nombre').value = nombre;
    document.getElementById('form-edit-materia').action = '/actualizar_materia/' + id;
    abrirEdit('edit-panel-materia');
}

function editAula(id, nombre, capacidad, tipo) {
    document.getElementById('eau-nombre').value    = nombre;
    document.getElementById('eau-capacidad').value = capacidad;
    document.getElementById('eau-tipo').value      = tipo;
    document.getElementById('form-edit-aula').action = '/actualizar_aula/' + id;
    abrirEdit('edit-panel-aula');
}

function editCurso(id, nombre) {
    document.getElementById('ec-nombre').value = nombre;
    document.getElementById('form-edit-curso').action = '/actualizar_curso/' + id;
    abrirEdit('edit-panel-curso');
}

function editParalelo(id, nombre) {
    document.getElementById('epa-nombre').value = nombre;
    document.getElementById('form-edit-paralelo').action = '/actualizar_paralelo/' + id;
    abrirEdit('edit-panel-paralelo');
}

function editHorario(id, idProfesor, idMateria, idAula, idCurso, idParalelo, dia, horaInicio, horaFin) {
    document.getElementById('eh-profesor').value    = idProfesor;
    document.getElementById('eh-materia').value     = idMateria;
    document.getElementById('eh-aula').value        = idAula;
    document.getElementById('eh-curso').value       = idCurso;
    document.getElementById('eh-paralelo').value    = idParalelo;
    document.getElementById('eh-dia').value         = dia;
    document.getElementById('eh-hora-inicio').value = horaInicio;
    document.getElementById('eh-hora-fin').value    = horaFin;
    document.getElementById('form-edit-horario').action = '/actualizar_horario/' + id;
    abrirEdit('edit-panel-horario');
}

window.addEventListener('DOMContentLoaded', function () {
    var p = new URLSearchParams(window.location.search);
    mostrar(p.get('seccion') || 'inicio');
    if (p.get('error') === 'conflicto') {
        var alerta = document.getElementById('alerta-conflicto');
        if (alerta) { alerta.style.display = 'block'; mostrar('horarios'); }
    }
});
