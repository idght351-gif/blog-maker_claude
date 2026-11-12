const { chromium } = require('playwright');
const S = process.env.NAVER_STATE_DIR || require('path').join(__dirname, __dirname.endsWith('probes') ? '../..' : '..', '.state');
(async () => {
  const b = await chromium.launch(); const ctx = await b.newContext({ storageState: S + '/naver-state.json', locale: 'ko-KR', viewport: { width: 1280, height: 1100 } });
  const page = await ctx.newPage();
  ctx.on('response', async r => { const u = r.url(); if (!u.includes('blog.stat.naver.com/api')) return;
    try { console.log('API', u.slice(0, 220), '\n   ', (await r.text()).slice(0, 400).replace(/\s+/g, ' ')); } catch {} });
  await page.goto('https://admin.blog.naver.com/seoeunjin13/stat/referer', { waitUntil: 'domcontentloaded', timeout: 60000 });
  await page.waitForTimeout(9000);
  const fr = page.frames().find(f => f.url().includes('blog.stat.naver.com'));
  if (fr) console.log('화면:', (await fr.evaluate(() => document.body.innerText)).replace(/\s+/g, ' ').slice(0, 700));
  await b.close();
})();
