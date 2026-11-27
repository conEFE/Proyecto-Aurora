// Exporta un SVG local a PNG con Chromium (Playwright). Uso: node svg_a_png.cjs <in.svg> <out.png> [escala]
const { chromium } = require('playwright');
const fs = require('fs');
(async () => {
  const [, , inp, out, sc] = process.argv;
  const svg = fs.readFileSync(inp, 'utf8');
  const b = await chromium.launch();
  const p = await b.newPage({ deviceScaleFactor: +(sc || 2) });
  await p.setContent(`<html><body style="margin:0;background:#fff">${svg}</body></html>`);
  await (await p.$('svg')).screenshot({ path: out });
  await b.close();
})();
