// 검색 유입 검색어: 월간 + 주간(월요일 시작)으로 받아 검색어별 유입수를 합친다.
const { chromium } = require('playwright');
const fs = require('fs');
const S = process.env.NAVER_STATE_DIR || require('path').join(__dirname, __dirname.endsWith('probes') ? '../..' : '..', '.state');
(async () => {
  const b = await chromium.launch(); const ctx = await b.newContext({ storageState: S + '/naver-state.json', locale: 'ko-KR' });
  const page = await ctx.newPage();
  await page.goto('https://admin.blog.naver.com/seoeunjin13/stat/referer', { waitUntil: 'domcontentloaded', timeout: 60000 });
  await page.waitForTimeout(8000);
  const fr = page.frames().find(f => f.url().includes('blog.stat.naver.com'));
  const get = u => fr.evaluate(async u => { const r = await fetch(u, { credentials: 'include' }); try { return await r.json(); } catch { return null; } }, u);
  const res = { month: {}, week: {} };
  const first = await get(`https://blog.stat.naver.com/api/blog/user/referer/search?timeDimension=MONTH&startDate=2026-10-01&exclude=&_=${Date.now()}`);
  for (const d of first.result.statDataList) console.log('dataId', d.dataId, d.data?.columnInfo);
  for (const m of ['2026-05-01','2026-06-01','2026-07-01','2026-08-01','2026-09-01','2026-10-01','2026-11-01'])
    res.month[m] = (await get(`https://blog.stat.naver.com/api/blog/user/referer/search?timeDimension=MONTH&startDate=${m}&exclude=&_=${Date.now()}`))?.result?.statDataList;
  for (let d = new Date('2026-05-25'); d <= new Date('2026-11-09'); d.setDate(d.getDate() + 7)) {
    const w = d.toISOString().slice(0, 10);
    res.week[w] = (await get(`https://blog.stat.naver.com/api/blog/user/referer/search?timeDimension=WEEK&startDate=${w}&exclude=&_=${Date.now()}`))?.result?.statDataList;
  }
  fs.writeFileSync(require('path').join(__dirname, '..', 'data', '')+'search_kw_raw.json', JSON.stringify(res));
  console.log('주간', Object.keys(res.week).length, '월간', Object.keys(res.month).length);
  await b.close();
})();
