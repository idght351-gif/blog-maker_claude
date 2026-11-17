const { chromium, devices } = require('playwright');
const S = process.env.NAVER_STATE_DIR || require('path').join(__dirname, '../..', '.state');
(async () => {
  const b = await chromium.launch();
  const ctx = await b.newContext({ ...devices['iPhone 13'], storageState: S + '/naver-state.json', locale: 'ko-KR', timezoneId: 'Asia/Seoul' });
  const p = await ctx.newPage();
  await p.goto(process.argv[2], { waitUntil: 'domcontentloaded' });
  await p.waitForTimeout(12000);
  const web = p.locator('button').filter({ hasText: '모바일 웹으로 볼게요' });
  if (await web.count() && await web.first().isVisible()) { await web.first().click(); await p.waitForTimeout(1500); }
  await p.screenshot({ path: process.argv[3], fullPage: true });
  console.log(p.url());
  console.log((await p.$$eval('label, button, textarea', es => es.map(e => (e.tagName + ' ' + (e.textContent || e.placeholder || e.getAttribute('aria-label') || '')).trim().replace(/\s+/g, ' ').slice(0, 60)))).join('\n'));
  await b.close();
})();
