const { chromium } = require('playwright');
const S = process.env.NAVER_STATE_DIR || require('path').join(__dirname, __dirname.endsWith('probes') ? '../..' : '..', '.state');
(async () => {
  const b = await chromium.launch(); const ctx = await b.newContext({ storageState: S + '/naver-state.json', locale: 'ko-KR', viewport: { width: 1280, height: 1100 } });
  const page = await ctx.newPage();
  ctx.on('request', r => { const u = r.url(); if (u.includes('blog.stat.naver.com/api')) console.log('REQ', u.slice(0, 200)); });
  await page.goto('https://admin.blog.naver.com/seoeunjin13/stat/referer', { waitUntil: 'domcontentloaded', timeout: 60000 });
  await page.waitForTimeout(8000);
  const fr = page.frames().find(f => f.url().includes('blog.stat.naver.com'));
  await fr.getByText('월간', { exact: true }).first().click().catch(e => console.log('월간 클릭 실패'));
  await page.waitForTimeout(4000);
  await fr.getByText('검색 유입', { exact: true }).first().click().catch(e => console.log('검색 유입 클릭 실패'));
  await page.waitForTimeout(5000);
  console.log('화면:', (await fr.evaluate(() => document.body.innerText)).replace(/\s+/g, ' ').slice(0, 900));
  await b.close();
})();
