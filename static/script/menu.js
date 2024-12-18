document.addEventListener("DOMContentLoaded", function() {
    const bar = document.getElementById('bar');
    const close = document.getElementById('close');
    const nav = document.getElementById('navbar');

    if (bar) {
        bar.addEventListener('click', () => {
            nav.classList.add('active');
        });
    }
    if (close) {
        close.addEventListener('click', () => {
            nav.classList.remove('active');
        });
    }

    // Cerrar menú al hacer clic fuera de él
    document.addEventListener('click', (event) => {
        if (!nav.contains(event.target) && !bar.contains(event.target) && nav.classList.contains('active')) {
            nav.classList.remove('active');
        }
    });
});
