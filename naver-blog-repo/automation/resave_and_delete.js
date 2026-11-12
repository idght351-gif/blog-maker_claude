// 이어쓰기 창의 글이 '새 글 제목'과 정확히 같을 때만: 저장 → 예전 시험 글(제목 문구 일치, 정확히 1개) 삭제
const { chromium } = require('playwright');
const S = process.env.NAVER_STATE_DIR || require('path').join(__dirname, __dirname.endsWith('probes') ? '../..' : '..', '.state');
const [NEW_TITLE, OLD_KEY] = process.argv.slice(2);
const sleep = ms => new Promise(r => setTimeout(r, ms));
(async () => {
  const b = await chromium.launch(); const ctx = await b.newContext({ storageState: S + '/naver-state.json', locale: 'ko-KR', viewport: { width: 1400, height: 1000 } });
  const page = await ctx.newPage(); page.on('dialog', d => { console.log('확인창:', d.message().slice(0, 60)); d.accept(); });
  await page.goto('https://blog.naver.com/seoeunjin13?Redirect=Write&', { waitUntil: 'domcontentloaded', timeout: 60000 }); await sleep(10000);
  const fr = page.frame('mainFrame');
  const cnt = fr.locator('[data-click-area="tpb*s.count"]');
  if (await fr.locator('.se-popup-button-cancel').count()) {
    await fr.locator('.se-popup-button-confirm').first().click(); await sleep(4000);
    const t = (await fr.locator('.se-title-text').first().innerText()).trim();
    if (t !== NEW_TITLE) { console.log('중단: 이어쓰기 글 제목이 다름 →', t.slice(0, 50)); await b.close(); return; }
    console.log('이어쓰기 글 = 새 쿠로카메 글 확인 → 다시 저장');
    await fr.locator('[data-click-area="tpb.save"]').click(); await sleep(4000);
  }
  await cnt.click(); await sleep(2500);
  const items = fr.locator('li', { has: fr.locator('button[class*="delete_button"]') }).filter({ hasText: OLD_KEY });
  const n = await items.count(); const total = (await cnt.innerText()).trim();
  console.log(`'${OLD_KEY}' 글: ${n}개 (전체 ${total}개)`);
  if (n === 1) {
    console.log('삭제:', (await items.first().innerText()).replace(/\s+/g, ' ').slice(0, 80));
    await items.first().hover(); await sleep(500); await items.first().locator('button[class*="delete_button"]').click({ force: true }); await sleep(1500);
    const ok = fr.locator('.se-popup-button-confirm:visible, button:has-text("확인"):visible').last(); if (await ok.count()) { await ok.click(); await sleep(2000); }
  } else console.log('정확히 1개가 아니라 지우지 않음');
  await page.reload({ waitUntil: 'domcontentloaded' }); await sleep(9000);
  const fr2 = page.frame('mainFrame');
  if (await fr2.locator('.se-popup-button-cancel').count()) console.log('(이어쓰기 창 다시 뜸 — 누르지 않음)');
  console.log('임시저장 글 수:', (await fr2.locator('[data-click-area="tpb*s.count"]').innerText()).trim());
  await ctx.storageState({ path: S + '/naver-state.json' }); await b.close();
})().catch(e => { console.log('오류: ' + e.message.slice(0, 200)); process.exit(1); });
