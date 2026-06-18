function mostrar(seccion) {
    document.querySelectorAll('.section').forEach(s => s.classList.remove('active'));
    document.querySelectorAll('.sidebar-nav a[id]').forEach(a => a.classList.remove('active'));
    document.getElementById('sec-' + seccion).classList.add('active');
    document.getElementById('nav-' + seccion).classList.add('active');
}

window.addEventListener('DOMContentLoaded', function () {
    var p = new URLSearchParams(window.location.search);
    mostrar(p.get('seccion') || 'panel');
});
