// 유입분석: 월별로 유입 경로와 검색어를 모은다.
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
  // 응답 구조 확인
  const sample = await get(`https://blog.stat.naver.com/api/blog/user/referer/total?timeDimension=MONTH&startDate=2026-10-01&exclude=&_=${Date.now()}`);
  for (const d of sample.result.statDataList) console.log('dataId', d.dataId, 'columns', d.data.columnInfo, 'rows', (Object.values(d.data.rows)[0] || []).length);
  const out = {};
  for (const m of ['2026-05-01','2026-06-01','2026-07-01','2026-08-01','2026-09-01','2026-10-01','2026-11-01']) {
    const j = await get(`https://blog.stat.naver.com/api/blog/user/referer/total?timeDimension=MONTH&startDate=${m}&exclude=&_=${Date.now()}`);
    out[m] = j?.result?.statDataList || null;
  }
  fs.writeFileSync(require('path').join(__dirname, '..', 'data', '')+'referer_raw.json', JSON.stringify(out));
  await b.close();
})();
