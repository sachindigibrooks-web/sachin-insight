const { chromium } = require('playwright');
const path = require('path');
(async () => {
  const [file, outdir] = process.argv.slice(2);
  const b = await chromium.launch();
  const p = await b.newPage({ viewport: { width: 1300, height: 1000 }, deviceScaleFactor: 1 });
  await p.goto('file://' + path.resolve(file), { waitUntil: 'networkidle' });
  await p.evaluate(() => document.fonts.ready); await p.waitForTimeout(800);
  const bad = await p.evaluate(() => [...document.fonts].filter(f => f.status !== 'loaded').map(f => f.family));
  if (bad.length) console.log('FONTS NOT LOADED', bad);
  const ids = await p.$$eval('.ab', els => els.map(e => e.id));
  for (const id of ids) { await (await p.$('#' + id)).screenshot({ path: `${outdir}/${id}.png` }); }
  // overflow check: text running outside artboard or overlapping right edge
  const issues = await p.$$eval('.ab', abs => abs.map(ab => { const r = ab.getBoundingClientRect(); const out = []; ab.querySelectorAll('.h,.sub,.chip,.tag,.logo,.lbl').forEach(el => { const q = el.getBoundingClientRect(); if (q.right > r.right - 20 || q.bottom > r.bottom - 20 || q.left < r.left + 20 || q.top < r.top + 20) out.push(el.className + ':' + Math.round(q.right - r.left) + 'x' + Math.round(q.bottom - r.top)); }); return [ab.id, out]; }).filter(x => x[1].length));
  console.log(JSON.stringify(issues));
  await b.close();
})();
