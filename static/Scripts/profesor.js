function mostrar(seccion) {
    document.querySelectorAll('.section').forEach(s => s.classList.remove('active'));
    document.querySelectorAll('.sidebar-nav a[id]').forEach(a => a.classList.remove('active'));
    document.getElementById('sec-' + seccion).classList.add('active');
    document.getElementById('nav-' + seccion).classList.add('active');
}

function toggleNotas(id) {
    var el = document.getElementById(id);
    el.style.display = el.style.display === 'none' ? 'block' : 'none';
}

function toggleEditNota(id) {
    var el = document.getElementById('edit-nota-' + id);
    el.style.display = el.style.display === 'none' ? 'table-row' : 'none';
}

function filtrarPorEstudiante(input) {
    var q = input.value.toLowerCase();
    document.querySelectorAll('.est-card').forEach(function(card) {
        card.style.display = card.dataset.est.includes(q) ? '' : 'none';
    });
}

window.addEventListener('DOMContentLoaded', function () {
    var p = new URLSearchParams(window.location.search);
    mostrar(p.get('seccion') || 'inicio');
});
