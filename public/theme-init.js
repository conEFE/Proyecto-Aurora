// Aplica el tema guardado antes del primer render para evitar el destello.
// Archivo propio (no inline) porque la CSP del sitio solo permite scripts de 'self'.
(function () {
  try {
    var saved = localStorage.getItem('aurora_theme');
    var dark = saved ? saved === 'dark' : window.matchMedia('(prefers-color-scheme: dark)').matches;
    if (dark) document.documentElement.classList.add('dark');
  } catch (e) {
    // Sin almacenamiento: se usa el tema claro
  }
})();
