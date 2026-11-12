// 블로그 통계 화면을 열고, 화면이 불러오는 데이터 주소(API)를 기록한다.
const { chromium } = require('playwright');
const S = process.env.NAVER_STATE_DIR || require('path').join(__dirname, __dirname.endsWith('probes') ? '../..' : '..', '.state');
(async () => {
  const ctx = await chromium.launchPersistentContext(S + '/naver-profile', { viewport: { width: 1280, height: 1000 }, locale: 'ko-KR',
    userAgent: 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36' });
  const page = ctx.pages()[0] || await ctx.newPage();
  const seen = [];
  ctx.on('response', async r => {
    const u = r.url(); const ct = r.headers()['content-type'] || '';
    if (ct.includes('json') && /stat|rank|count/i.test(u)) { seen.push(u); try { const t = await r.text(); console.log('API', u.slice(0, 160), '\n   ', t.slice(0, 300).replace(/\s+/g, ' ')); } catch {} }
  });
  for (const u of ['https://admin.blog.naver.com/seoeunjin13/stat/today', 'https://admin.blog.naver.com/seoeunjin13/stat/rank']) {
    await page.goto(u, { waitUntil: 'networkidle' }).catch(e => console.log('goto', e.message));
    await page.waitForTimeout(4000);
    console.log('PAGE', page.url());
    await page.screenshot({ path: S + '/shots/stat_' + u.split('/').pop() + '.png' });
    for (const f of page.frames()) if (f.url() !== page.url()) console.log('  frame', f.url().slice(0, 150));
  }
  await ctx.close();
})();
