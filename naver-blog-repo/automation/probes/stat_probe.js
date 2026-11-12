const { chromium } = require('playwright');
const S = process.env.NAVER_STATE_DIR || require('path').join(__dirname, __dirname.endsWith('probes') ? '../..' : '..', '.state');
(async () => {
  const b = await chromium.launch();
  const ctx = await b.newContext({ storageState: S + '/naver-state.json', locale: 'ko-KR', viewport: { width: 1280, height: 1000 },
    userAgent: 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36' });
  const page = await ctx.newPage();
  ctx.on('response', async r => {
    const u = r.url(); if (!/stat\.naver|api/.test(u) || /veta|nelo|lcs|gfp/.test(u)) return;
    const ct = r.headers()['content-type'] || ''; if (!ct.includes('json')) return;
    try { console.log('API', u.slice(0, 200), '\n   ', (await r.text()).slice(0, 250).replace(/\s+/g, ' ')); } catch {}
  });
  await page.goto('https://admin.blog.naver.com/seoeunjin13/stat/today', { waitUntil: 'domcontentloaded', timeout: 60000 });
  await page.waitForTimeout(8000);
  console.log('PAGE', page.url());
  for (const f of page.frames()) {
    console.log(' frame', f.url().slice(0, 120));
    const links = await f.$$eval('a', as => as.map(a => a.innerText.trim() + ' ' + a.href).filter(t => /순위|rank|게시물/i.test(t))).catch(() => []);
    for (const l of [...new Set(links)].slice(0, 10)) console.log('   LINK', l.replace(/\s+/g, ' ').slice(0, 160));
  }
  await page.screenshot({ path: S + '/shots/stat_today.png', fullPage: true });
  await b.close();
})();
