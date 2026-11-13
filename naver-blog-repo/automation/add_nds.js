// 이미 임시저장된 글을 열어 '내돈내산 방문 인증' 카드를 글 맨 위에 넣고 다시 저장한다.
// 사용법: node automation/add_nds.js <제목 문구> <영수증 가게 이름>
//   예: node automation/add_nds.js 쿠로카메 쿠로카메
// 안전장치: 열린 글 제목에 <제목 문구>가 없으면 아무것도 바꾸지 않고 멈춤. 카드가 맨 위가 아니면 넣은 카드를 지우고 저장하지 않음.
//          "이어서 쓸까요?" 창에서 '취소'는 절대 누르지 않음 (누르면 그 글이 지워짐).
const { chromium } = require('playwright');
const S = process.env.NAVER_STATE_DIR || require('path').join(__dirname, '..', '.state');
const [OWN, QUERY] = process.argv.slice(2);
const sleep = ms => new Promise(r => setTimeout(r, ms));
const NDS = '.se-component.se-custom';   // 내돈내산 카드는 se-custom 컴포넌트로 들어감 (2026-11-12 확인)

(async () => {
  const b = await chromium.launch();
  const ctx = await b.newContext({ storageState: S + '/naver-state.json', locale: 'ko-KR', viewport: { width: 1400, height: 1000 } });
  const page = await ctx.newPage(); page.on('dialog', d => { console.log('대화상자:', d.message().slice(0, 60)); d.accept(); });
  await page.goto('https://blog.naver.com/seoeunjin13?Redirect=Write&', { waitUntil: 'domcontentloaded', timeout: 60000 }); await sleep(10000);
  const fr = page.frame('mainFrame');
  let needList = true;
  if (await fr.locator('.se-popup-button-cancel').count()) {   // '이어서 쓸까요?' → 취소는 글을 지우므로 확인(이어쓰기)만. 다른 글이면 목록에서 다시 고름
    await fr.locator('.se-popup-button-confirm').first().click(); await sleep(5000);
    needList = !(await fr.locator('.se-title-text').first().innerText()).includes(OWN);
  }
  if (needList) {
    await page.screenshot({ path: S + '/shots/nds_0_open.png' });
    const help0 = fr.locator('.se-help-panel-close-button'); if (await help0.count()) { await help0.first().click().catch(() => {}); await sleep(800); }
    await fr.locator('[data-click-area="tpb*s.count"]').evaluate(e => e.click()); await sleep(2500);
    await fr.locator('li', { has: fr.locator('button[class*="article_button"]') }).filter({ hasText: OWN }).first().locator('button[class*="article_button"]').click(); await sleep(7000);
  }
  const help = fr.locator('.se-help-panel-close-button'); if (await help.count()) await help.first().click().catch(() => {});
  const title = (await fr.locator('.se-title-text').first().innerText()).trim();
  if (!title.includes(OWN)) { console.log('중단: 열린 글이 대상 글이 아님 →', title.slice(0, 40)); await b.close(); return; }
  console.log('열린 글:', title.slice(0, 50));
  const order = () => fr.evaluate(() => [...document.querySelectorAll('.se-component')].filter(c => !c.classList.contains('se-documentTitle')).slice(0, 4).map(c => c.className.replace(/se-component|se-l-\S+|se-section\S*/g, '').trim().slice(0, 40)));
  console.log('앞부분(전):', JSON.stringify(await order()));
  if (await fr.locator(NDS).count()) {
    const first = await fr.evaluate(sel => { const cs = [...document.querySelectorAll('.se-component')].filter(c => !c.classList.contains('se-documentTitle')); return cs[0] && cs[0].matches(sel); }, NDS);
    if (first) { await fr.locator('[data-click-area="tpb.save"]').click(); await sleep(4000); console.log('이미 맨 위에 카드가 있음 → 저장만 함'); }
    else console.log('카드가 이미 있지만 맨 위가 아님 → 손대지 않음');
    await b.close(); return;
  }

  // 커서를 본문 맨 앞으로: 첫 컴포넌트가 사진이면 그 아래에 들어가므로, 제목 끝에서 Enter로 사진 위에 빈 줄을 만든다
  await fr.locator('.se-title-text').first().click(); await page.keyboard.press('End'); await sleep(300);
  await page.keyboard.press('Enter'); await sleep(1000);
  console.log('Enter 후 앞부분:', JSON.stringify(await order()));

  const nBefore = await fr.locator('.se-component').count();
  await fr.evaluate(() => { const b = [...document.querySelectorAll('button')].find(e => /^내돈내산/.test(e.innerText.trim())); b && b.click(); }); await sleep(3000);
  await page.screenshot({ path: S + '/shots/nds_1_popup.png' });
  await fr.evaluate(() => { const b = [...document.querySelectorAll('button')].find(e => e.innerText.trim() === '방문'); b && b.click(); }); await sleep(2000);
  // 목록 카드(가게 이름 + "영수증")를 실제 마우스로 클릭하면 바로 본문에 들어간다
  const card = fr.locator('li, [class*="item"]').filter({ hasText: QUERY }).filter({ hasText: '영수증' }).last();
  const found = (await card.count()) ? (await card.innerText()).replace(/\s+/g, ' ').slice(0, 80) : null;
  console.log('방문 인증 항목:', found || '없음');
  if (!found) { console.log('중단: 목록에 영수증 인증이 없음'); await b.close(); return; }
  await card.click(); await sleep(3000);
  await page.screenshot({ path: S + '/shots/nds_2_pick.png' });
  const ok = fr.locator('.se-popup-button-confirm:visible:not([disabled])').first();
  if (await ok.count()) { await ok.click({ timeout: 5000 }).catch(() => {}); await sleep(3000); }
  const close = fr.locator('.se-popup-close-button:visible'); if (await close.count()) await close.first().click().catch(() => {});
  const nAfter = await fr.locator('.se-component').count();
  const ord = await order();
  console.log('컴포넌트 수', nBefore, '→', nAfter, '/ 앞부분(후):', JSON.stringify(ord));
  await page.screenshot({ path: S + '/shots/nds_3_after.png' });

  const ndsIdx = await fr.evaluate(sel => { const cs = [...document.querySelectorAll('.se-component')].filter(c => !c.classList.contains('se-documentTitle')); const n = document.querySelector(sel); return n ? cs.indexOf(n) : -1; }, NDS);
  console.log('내돈내산 카드 위치:', ndsIdx);
  // 제목에서 만든 빈 줄 자리에 카드가 들어가므로 컴포넌트 수는 그대로일 수 있음 → 위치와 개수로만 판단
  if (ndsIdx === 0 && (await fr.locator(NDS).count()) === 1) {
    await fr.locator('[data-click-area="tpb.save"]').click(); await sleep(4000);
    console.log('저장 완료');
  } else {
    console.log('카드가 맨 위가 아니거나 못 찾음 → 되돌리고 저장하지 않음');
    for (let i = 0; i < nAfter - nBefore; i++) { await page.keyboard.press('Control+Z'); await sleep(500); }
  }
  await ctx.storageState({ path: S + '/naver-state.json' });
  await b.close();
})().catch(e => { console.log('오류: ' + e.message.slice(0, 300)); process.exit(1); });
