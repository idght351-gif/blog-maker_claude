// 임시저장 목록 열기: 항목 제목과 삭제 버튼 구조를 확인한다 (지우지 않음).
const { chromium } = require('playwright');
const S = process.env.NAVER_STATE_DIR || require('path').join(__dirname, __dirname.endsWith('probes') ? '../..' : '..', '.state');
(async () => {
  const b = await chromium.launch(); const ctx = await b.newContext({ storageState: S + '/naver-state.json', locale: 'ko-KR', viewport: { width: 1400, height: 1000 } });
  const page = await ctx.newPage();
  page.on('dialog', d => d.dismiss());
  await page.goto('https://blog.naver.com/seoeunjin13?Redirect=Write&', { waitUntil: 'domcontentloaded', timeout: 60000 });
  await page.waitForTimeout(10000);
  const fr = page.frame('mainFrame');
  const cancel = fr.locator('.se-popup-button-cancel'); if (await cancel.count()) { await cancel.first().click(); console.log('이어쓰기 팝업 취소'); await page.waitForTimeout(1000); }
  const help = fr.locator('.se-help-panel-close-button'); if (await help.count()) await help.first().click().catch(() => {});
  const saveBtn = fr.locator('button:has-text("저장")').first();
  console.log('저장 버튼 HTML:', (await saveBtn.evaluate(e => e.outerHTML)).slice(0, 300));
  // 숫자 부분(목록 열기) 클릭
  const cnt = saveBtn.locator('span, em').last(); await cnt.click(); await page.waitForTimeout(2500);
  await page.screenshot({ path: S + '/shots/drafts_list.png' });
  const items = await fr.evaluate(() => [...document.querySelectorAll('[class*="temp"] li, [class*="list"] li')].map(li => li.innerText.replace(/\s+/g, ' ').slice(0, 120)).filter(t => t));
  console.log(JSON.stringify(items.slice(0, 12), null, 1));
  await b.close();
})();
