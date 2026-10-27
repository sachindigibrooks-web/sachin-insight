const { chromium } = require('playwright');
const path = require('path'), fs = require('fs');
(async () => {
  const [fmt, outdir, t0s, t1s, step] = process.argv.slice(2);
  const W = fmt === 'v' ? 1080 : 1920, H = fmt === 'v' ? 1920 : 1080;
  fs.mkdirSync(outdir, { recursive: true });
  const b = await chromium.launch({ args: ['--allow-file-access-from-files'] });
  const p = await b.newPage({ viewport: { width: W, height: H } });
  const errs = []; p.on('pageerror', e => errs.push(e.message)); p.on('console', m => { if (m.type() === 'error') errs.push(m.text()); });
  await p.goto('file://' + path.resolve(__dirname, 'index.html') + '?fmt=' + fmt);
  await p.evaluate(() => window.ready);
  if (errs.length) console.log('ERR', errs);
  const FPS = 30, t0 = +t0s, t1 = +t1s, st = +(step || 1);
  for (let f = Math.round(t0 * FPS); f < Math.round(t1 * FPS); f += st) {
    await p.evaluate(t => window.renderAt(t), f / FPS);
    await p.screenshot({ path: `${outdir}/${String(f).padStart(5, '0')}.png`, omitBackground: true, clip: { x: 0, y: 0, width: W, height: H } });
  }
  await b.close();
})();
