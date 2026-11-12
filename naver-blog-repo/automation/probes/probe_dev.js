const { chromium } = require('playwright');
const S = process.env.NAVER_STATE_DIR || require('path').join(__dirname, __dirname.endsWith('probes') ? '../..' : '..', '.state');
(async () => {
  const b = await chromium.launch(); const ctx = await b.newContext({ storageState: S + '/naver-state.json', locale: 'ko-KR' });
  const page = await ctx.newPage();
  await page.goto('https://admin.blog.naver.com/seoeunjin13/stat/rank_pv', { waitUntil: 'domcontentloaded', timeout: 60000 }); await page.waitForTimeout(8000);
  const fr = page.frames().find(f => f.url().includes('blog.stat.naver.com'));
  for (const ep of ['cvContentPc', 'cvContentMo', 'cvContentMobile', 'cvContent']) {
    const j = await fr.evaluate(async u => { const r = await fetch(u, { credentials: 'include' }); const t = await r.text(); try { return JSON.parse(t); } catch { return { raw: r.status } } },
      `https://blog.stat.naver.com/api/blog/rank/${ep}?timeDimension=MONTH&startDate=2026-08-01&exclude=&_=${Date.now()}`);
    const rows = j?.result?.statDataList?.[0]?.data?.rows;
    console.log(ep, rows ? `1위 ${rows.title[0].slice(0, 15)} ${rows.cv[0]} / 합계 ${rows.cv.reduce((a, c) => a + c, 0)}` : JSON.stringify(j).slice(0, 80));
  }
  // 화면의 기기 선택 옵션 텍스트
  const txt = await fr.evaluate(() => document.body.innerText.slice(0, 400));
  console.log('화면:', txt.replace(/\s+/g, ' '));
  await b.close();
})();
