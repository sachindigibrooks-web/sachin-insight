// Exports every .ab artboard and checks the banner-design rules on it.
const { chromium } = require('playwright');
const { execFileSync } = require('child_process');
(async () => {
  const [file, outdir] = process.argv.slice(2);
  const b = await chromium.launch(); const p = await b.newPage({ viewport: { width: 1400, height: 2000 } });
  await p.goto('file://' + file, { waitUntil: 'networkidle' }); await p.evaluate(() => document.fonts.ready); await p.waitForTimeout(800);
  const errs = await p.evaluate(() => [...document.fonts].filter(f => f.status === 'error').map(f => f.family));
  if (errs.length) console.log('FONT LOAD ERRORS', errs);
  const ids = await p.$$eval('.ab', as => as.map(a => a.id));
  const report = {};
  for (const id of ids) {
    await p.locator('#' + id).screenshot({ path: `${outdir}/${id}.png` });
    report[id] = await p.evaluate((id) => {
      const ab = document.getElementById(id), R = ab.getBoundingClientRect();
      const W = R.width, H = R.height, story = ab.classList.contains('story');
      const m = { l: W * .1, r: W * .1, t: story ? 250 : H * .1, b: story ? 340 : H * .1 };
      const items = [], fonts = new Set(); let textArea = 0;
      for (const el of ab.querySelectorAll('.t')) {
        const r = el.getBoundingClientRect(), x = r.left - R.left, y = r.top - R.top;
        const cs = getComputedStyle(el), isLogo = el.classList.contains('logo');
        const box = { x, y, w: r.width, h: r.height };
        const safe = x >= m.l - .5 && y >= m.t - .5 && x + r.width <= W - m.r + .5 && y + r.height <= H - m.b + .5;
        let lines = [];
        if (!isLogo) {
          fonts.add(cs.fontFamily.split(',')[0].replace(/["']/g, ''));
          // words per rendered line
          const rng = document.createRange(), words = [];
          const walk = document.createTreeWalker(el, NodeFilter.SHOW_TEXT);
          let n; while ((n = walk.nextNode())) { const re = /\S+/g; let mm; while ((mm = re.exec(n.data))) { rng.setStart(n, mm.index); rng.setEnd(n, mm.index + mm[0].length); words.push(Math.round(rng.getBoundingClientRect().top)); } }
          const byLine = {}; words.forEach(t => byLine[t] = (byLine[t] || 0) + 1); lines = Object.values(byLine);
          textArea += r.width * r.height;
        }
        items.push({ tag: isLogo ? 'logo' : (el.classList.contains('cta') ? 'cta' : 'text'), txt: el.textContent.trim().slice(0, 40), box, safe, size: parseFloat(cs.fontSize), color: cs.color, bg: el.classList.contains('cta') ? cs.backgroundColor : null, lines });
      }
      return { W, H, fonts: [...fonts], textRatio: textArea / (W * H), items };
    }, id);
  }
  // background-only render for contrast sampling
  await p.evaluate(() => document.body.classList.add('notext'));
  for (const id of ids) await p.locator('#' + id).screenshot({ path: `${outdir}/_bg_${id}.png` });
  await b.close();
  require('fs').writeFileSync(`${outdir}/_qa.json`, JSON.stringify(report, null, 1));
})();
