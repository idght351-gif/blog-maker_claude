// 블로그 통계 '조회수 순위'를 월 단위로 받아 글별 누적 조회수를 만든다.
const { chromium } = require('playwright');
const fs = require('fs');
const S = process.env.NAVER_STATE_DIR || require('path').join(__dirname, __dirname.endsWith('probes') ? '../..' : '..', '.state');
(async () => {
  const b = await chromium.launch();
  const ctx = await b.newContext({ storageState: S + '/naver-state.json', locale: 'ko-KR' });
  const page = await ctx.newPage();
  await page.goto('https://admin.blog.naver.com/seoeunjin13/stat/rank_pv', { waitUntil: 'domcontentloaded', timeout: 60000 });
  await page.waitForTimeout(8000);
  const months = ['2026-05-01','2026-06-01','2026-07-01','2026-08-01','2026-09-01','2026-10-01','2026-11-01'];
  const total = {}, perMonth = {};
  for (const m of months) {
    const url = `https://blog.stat.naver.com/api/blog/rank/cvContentPc?timeDimension=MONTH&startDate=${m}&exclude=&_=${Date.now()}`;
    const fr = page.frames().find(f => f.url().includes('blog.stat.naver.com'));
    if (!fr) { console.log('통계 프레임 없음'); break; }
    const j = await fr.evaluate(async u => { const r = await fetch(u, { credentials: 'include' }); const t = await r.text(); try { return JSON.parse(t); } catch { return { raw: r.status + ' ' + t.slice(0, 120) }; } }, url);
    const rows = j?.result?.statDataList?.[0]?.data?.rows;
    if (!rows) { console.log(m, '데이터 없음', JSON.stringify(j).slice(0, 150)); continue; }
    const n = rows.uri.length; perMonth[m] = n;
    for (let i = 0; i < n; i++) {
      const no = (rows.uri[i].match(/(\d{9,})/) || [])[1]; if (!no) continue;
      total[no] = total[no] || { title: rows.title[i], views: 0, created: rows.createDate[i] };
      total[no].views += rows.cv[i];
    }
    console.log(m, `글 ${n}개`, '1위:', rows.title[0]?.slice(0, 25), rows.cv[0]);
  }
  fs.writeFileSync(require('path').join(__dirname, '..', 'data', '')+'views.json', JSON.stringify(total, null, 1));
  console.log('글 수', Object.keys(total).length);
  await b.close();
})();
