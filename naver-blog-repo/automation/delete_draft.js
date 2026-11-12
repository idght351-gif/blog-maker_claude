// 임시저장 목록에서 제목에 주어진 문구가 들어간 글을 '정확히 1개'일 때만 삭제한다.
// 사용법: node delete_draft.js "<제목에 들어간 문구>"
const { chromium } = require('playwright');
const S = process.env.NAVER_STATE_DIR || require('path').join(__dirname, __dirname.endsWith('probes') ? '../..' : '..', '.state');
const KEY = process.argv[2];
(async () => {
  const b = await chromium.launch(); const ctx = await b.newContext({ storageState: S + '/naver-state.json', locale: 'ko-KR', viewport: { width: 1400, height: 1000 } });
  const page = await ctx.newPage(); page.on('dialog', d => { console.log('확인창:', d.message()); d.accept(); });
  await page.goto('https://blog.naver.com/seoeunjin13?Redirect=Write&', { waitUntil: 'domcontentloaded', timeout: 60000 });
  await page.waitForTimeout(10000);
  const fr = page.frame('mainFrame');
  if (await fr.locator('.se-popup-button-cancel').count()) { console.log('중단: 이어쓰기 창이 떠 있음 (취소를 누르면 글이 지워지므로 아무것도 누르지 않음)'); await b.close(); return; }
  const cnt = fr.locator('[data-click-area="tpb*s.count"]');
  const before = (await cnt.innerText()).trim();
  await cnt.click(); await page.waitForTimeout(2500);
  const items = fr.locator('li', { has: fr.locator('button[class*="delete_button"]') }).filter({ hasText: KEY });
  const n = await items.count();
  console.log(`'${KEY}' 포함 임시저장 글: ${n}개 (전체 ${before}개)`);
  if (n !== 1) { console.log('1개가 아니라서 지우지 않음'); await b.close(); return; }
  console.log('삭제 대상:', (await items.first().innerText()).replace(/\s+/g, ' ').slice(0, 100));
  await items.first().locator('button[class*="delete_button"]').click(); await page.waitForTimeout(1500);
  const ok = fr.locator('button:has-text("확인"), button:has-text("삭제")').last(); if (await ok.count() && await ok.isVisible()) { await ok.click(); await page.waitForTimeout(2000); }
  await page.screenshot({ path: S + '/shots/after_delete.png' });
  await page.reload({ waitUntil: 'domcontentloaded' }); await page.waitForTimeout(9000);
  const fr2 = page.frame('mainFrame');
  console.log(`임시저장 글 수: ${before} → ${(await fr2.locator('[data-click-area="tpb*s.count"]').innerText()).trim()}`);
  await b.close();
})().catch(e => { console.log('오류: ' + e.message.slice(0, 200)); process.exit(1); });
