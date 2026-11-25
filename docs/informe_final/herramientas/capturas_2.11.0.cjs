const { chromium } = require('playwright');
(async () => {
  const b = await chromium.launch();
  const tok = async (rut) => (await (await fetch('http://localhost:8000/auth/login', {method:'POST', headers:{'Content-Type':'application/json'}, body: JSON.stringify({rut, password:'Clave-Prueba-123'})})).json()).access_token;
  const shot = async (rut, url, out, wait) => {
    const p = await b.newPage({ viewport: { width: 1440, height: 900 }, deviceScaleFactor: 1 });
    const t = await tok(rut);
    await p.goto('http://localhost:5173/');
    await p.evaluate((t) => localStorage.setItem('auth_token', t), t);
    await p.goto('http://localhost:5173' + url, { waitUntil: 'networkidle' });
    if (wait) await wait(p);
    await p.waitForTimeout(1500);
    const h = await p.evaluate(() => document.documentElement.scrollHeight);
    await p.setViewportSize({ width: 1440, height: Math.max(900, h) });
    await p.waitForTimeout(500);
    await p.screenshot({ path: out, fullPage: true });
    console.log(out, await p.title());
    await p.close();
  };
  await shot('33333333-3', '/comparador-medicos', '/tmp/claude-0/inf/cap/09_comparador.png');
  await shot('44444444-4', '/administracion', '/tmp/claude-0/inf/cap/10_nuevo_usuario.png', async (p) => {
    await p.getByRole('button', { name: 'Nuevo usuario' }).click();
    await p.waitForTimeout(800);
    const sel = p.locator('select').first();
    try { await sel.selectOption({ label: 'Médico' }); } catch (e) { console.log('sin select rol', e.message.slice(0,80)); }
  });
  await b.close();
})();
