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
  if (await fr.locator('.se-popup-button-cancel').count()) {   // '이어서 쓸까요?' → 취소는 글을 지우므로 '확인'(이어쓰기)만 누른다
    await fr.locator('.se-popup-button-confirm').first().click(); await page.waitForTimeout(5000);
    console.log('이어쓰기로 연 글:', (await fr.locator('.se-title-text').first().innerText()).trim().slice(0, 40));
  }
  const cnt = fr.locator('[data-click-area="tpb*s.count"]');
  const before = (await cnt.innerText()).trim();
  await cnt.click(); await page.waitForTimeout(2500);
  { const edit = fr.locator('button').filter({ hasText: /^편집$/ }).first(); if (await edit.count() && await edit.isVisible()) { await edit.click(); await page.waitForTimeout(1500); } }   // 삭제는 '편집' 모드에서
  // 지울 글이 지금 열린 글('작성중')이면 삭제 버튼이 없음 → 다른 임시저장 글을 열어(아무것도 고치지 않음) 목록을 다시 연다
  const openArts = fr.locator('li', { has: fr.locator('button[class*="article_button"]') });
  if (!(await fr.locator('li', { has: fr.locator('button[class*="delete_button"]') }).filter({ hasText: KEY }).count())
      && await openArts.filter({ hasText: KEY }).filter({ hasText: '작성중' }).count()) {
    const other = openArts.filter({ hasNotText: KEY }).first();
    if (await other.count()) {
      await other.locator('button[class*="article_button"]').click(); await page.waitForTimeout(7000);
      console.log('다른 글로 전환:', (await fr.locator('.se-title-text').first().innerText()).trim().slice(0, 30));
      await cnt.click(); await page.waitForTimeout(2500);
      const edit = fr.locator('button').filter({ hasText: /^편집$/ }).first(); if (await edit.count()) { await edit.click(); await page.waitForTimeout(1500); }
    }
  }
  // 2026-11 화면: '편집' → 글마다 체크박스 → '선택 삭제' (예전 화면: 글마다 삭제 버튼)
  const oldItems = fr.locator('li', { has: fr.locator('button[class*="delete_button"]') }).filter({ hasText: KEY });
  const newItems = fr.locator('li', { has: fr.locator('[class*="checkbox"]') }).filter({ hasText: KEY });
  const items = (await newItems.count()) ? newItems : oldItems;
  const n = await items.count();
  await page.screenshot({ path: S + '/shots/draft_list.png' });
  console.log(`'${KEY}' 포함 임시저장 글: ${n}개 (전체 ${before}개)`);
  if (n !== 1) { console.log('1개가 아니라서 지우지 않음'); await b.close(); return; }
  console.log('삭제 대상:', (await items.first().innerText()).replace(/\s+/g, ' ').slice(0, 100));
  if (items === oldItems) await items.first().locator('button[class*="delete_button"]').click();
  else {
    const box = await items.first().locator('[class*="checkbox"]').first().boundingBox();
    await page.mouse.click(box.x + box.width / 2, box.y + box.height / 2); await page.waitForTimeout(800);
    const sel = await fr.locator('text=/총\\s*\\d+개 선택됨/').first().innerText().catch(() => '');
    if (!/총\s*1개 선택됨/.test(sel.replace(/\s+/g, ' '))) { console.log('중단: 선택된 글이 1개가 아님 →', sel); await b.close(); return; }
    await fr.locator('button').filter({ hasText: /^선택 삭제$/ }).first().click();
  }
  await page.waitForTimeout(1500);
  const ok = fr.locator('button:has-text("확인"), button:has-text("삭제")').last(); if (await ok.count() && await ok.isVisible()) { await ok.click(); await page.waitForTimeout(2000); }
  await page.screenshot({ path: S + '/shots/after_delete.png' });
  await page.reload({ waitUntil: 'domcontentloaded' }); await page.waitForTimeout(9000);
  const fr2 = page.frame('mainFrame');
  console.log(`임시저장 글 수: ${before} → ${(await fr2.locator('[data-click-area="tpb*s.count"]').innerText()).trim()}`);
  await b.close();
})().catch(e => { console.log('오류: ' + e.message.slice(0, 200)); process.exit(1); });
