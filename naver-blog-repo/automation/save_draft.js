// 편집 중인 시험 글을 열어 제목·장소·본문 정렬을 확인한 뒤 '저장'만 누른다.
const { chromium } = require('playwright');
const S = process.env.NAVER_STATE_DIR || require('path').join(__dirname, __dirname.endsWith('probes') ? '../..' : '..', '.state');
const OWN = process.argv[2];
const sleep = ms => new Promise(r => setTimeout(r, ms));
(async () => {
  const b = await chromium.launch(); const ctx = await b.newContext({ storageState: S + '/naver-state.json', locale: 'ko-KR', viewport: { width: 1400, height: 1000 } });
  const page = await ctx.newPage(); page.on('dialog', d => d.accept());
  await page.goto('https://blog.naver.com/seoeunjin13?Redirect=Write&', { waitUntil: 'domcontentloaded', timeout: 60000 }); await sleep(10000);
  const fr = page.frame('mainFrame');
  if (!(await fr.locator('.se-popup-button-cancel').count())) { console.log('이어쓸 편집본 없음 → 중단'); await b.close(); return; }
  await fr.locator('.se-popup-button-confirm').first().click(); await sleep(4000);
  const t = (await fr.locator('.se-title-text').first().innerText()).trim();
  const st = await fr.evaluate(() => ({ place: document.querySelectorAll('.se-component.se-placesMap').length,
    bodyCenter: document.querySelectorAll('.se-component.se-text .se-text-paragraph-align-center').length,
    quote: document.querySelectorAll('.se-component.se-quotation').length, img: document.querySelectorAll('.se-component .se-image-resource').length }));
  console.log('제목:', t.slice(0, 40), '/', JSON.stringify(st));
  if (!t.includes(OWN) || !st.place || st.bodyCenter) { console.log('조건 불충족 → 저장 안 함'); await b.close(); return; }
  const cnt = fr.locator('[data-click-area="tpb*s.count"]'); const before = (await cnt.innerText()).trim();
  await fr.locator('[data-click-area="tpb.save"]').click(); await sleep(4000);
  console.log('임시저장 완료:', before, '→', (await cnt.innerText()).trim());
  await page.screenshot({ path: S + '/shots/final_saved.png' });
  await ctx.storageState({ path: S + '/naver-state.json' }); await b.close();
})();
