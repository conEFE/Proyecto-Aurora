// Dibuja las flechas declaradas en window.FLECHAS y exporta cada diagrama HTML a PNG.
// Uso: node render.js <entrada.html> <salida.png> [ancho]
// FLECHAS: [{de, a, lado_de, lado_a, txt, estilo: "s"|"d"|"p", via: [[x,y],...]}]
const { chromium } = require('playwright');
const path = require('path');

const DIBUJAR = () => {
  const L = document.getElementById('lienzo');
  const r0 = L.getBoundingClientRect();
  const svg = document.createElementNS('http://www.w3.org/2000/svg', 'svg');
  svg.id = 'flechas'; svg.setAttribute('width', L.scrollWidth); svg.setAttribute('height', L.scrollHeight);
  svg.innerHTML = '<defs><marker id="pt" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0,0 L10,5 L0,10 z" fill="#374151"/></marker></defs>';
  const pt = (id, lado) => {
    const r = document.getElementById(id).getBoundingClientRect();
    const x = r.left - r0.left, y = r.top - r0.top, w = r.width, h = r.height;
    const [l, f] = (lado || 'c').split(':'); const k = f === undefined ? 0.5 : parseFloat(f);
    if (l === 't') return [x + w * k, y];
    if (l === 'b') return [x + w * k, y + h];
    if (l === 'l') return [x, y + h * k];
    if (l === 'r') return [x + w, y + h * k];
    return [x + w / 2, y + h / 2];
  };
  for (const f of (window.FLECHAS || [])) {
    const a = pt(f.de, f.lado_de), b = pt(f.a, f.lado_a);
    if (f.recto) b[0] = a[0];
    // Coordenada de ruta: número, null (= origen), 'b' (= destino) o '@id:lado:desplazamiento' (borde de una caja)
    const rel = (v, eje, o, d) => {
      if (v === null) return o; if (v === 'b') return d; if (typeof v === 'number') return v;
      const [id, lado, off] = v.slice(1).split(':');
      const r = document.getElementById(id).getBoundingClientRect();
      const base = { l: r.left - r0.left, r: r.right - r0.left, t: r.top - r0.top, b: r.bottom - r0.top,
                     cx: (r.left + r.right) / 2 - r0.left, cy: (r.top + r.bottom) / 2 - r0.top }[lado];
      return base + parseFloat(off || '0');
    };
    const pts = [a, ...(f.via || []).map(([vx, vy]) => [rel(vx, 'x', a[0], b[0]), rel(vy, 'y', a[1], b[1])]), b];
    const p = document.createElementNS('http://www.w3.org/2000/svg', 'polyline');
    p.setAttribute('points', pts.map(q => q.join(',')).join(' '));
    p.setAttribute('fill', 'none'); p.setAttribute('stroke', '#374151'); p.setAttribute('stroke-width', '1.6');
    if (f.estilo === 'd') p.setAttribute('stroke-dasharray', '6 4');
    if (f.estilo === 'p') p.setAttribute('stroke-dasharray', '2 3');
    p.setAttribute('marker-end', 'url(#pt)');
    if (f.doble) p.setAttribute('marker-start', 'url(#pt)');
    svg.appendChild(p);
    if (f.txt) {
      const i = Math.floor((pts.length - 1) / 2), m = pts[i], n = pts[i + 1];
      const t = document.createElementNS('http://www.w3.org/2000/svg', 'text');
      t.setAttribute('x', (m[0] + n[0]) / 2 + (f.dx || 4)); t.setAttribute('y', (m[1] + n[1]) / 2 + (f.dy || -4));
      t.setAttribute('class', 'et'); if (f.anchor) t.setAttribute('text-anchor', f.anchor);
      t.textContent = f.txt; svg.appendChild(t);
    }
  }
  L.appendChild(svg);
};

(async () => {
  const [inp, out, ancho] = process.argv.slice(2);
  const b = await chromium.launch();
  const p = await b.newPage({ viewport: { width: parseInt(ancho || '1600'), height: 900 }, deviceScaleFactor: 2 });
  await p.goto('file://' + path.resolve(inp));
  await p.evaluate(DIBUJAR);
  const el = await p.$('#lienzo');
  await el.screenshot({ path: out });
  await b.close();
})();
