// 임시저장된 글 최상단(내돈내산 카드보다 위)에 썸네일 사진을 넣고 대표 사진으로 지정한 뒤 저장한다.
// 사용법: node automation/add_thumb.js <제목 문구> <썸네일.jpg>
// 안전장치: 제목이 다르면 멈춤. 첫 컴포넌트가 새 사진이 아니거나 대표 지정이 안 되면 저장하지 않음.
//          "이어서 쓸까요?" 창에서 '취소'는 절대 누르지 않음 (누르면 그 글이 지워짐).
const { chromium } = require('playwright');
const path = require('path');
const S = process.env.NAVER_STATE_DIR || path.join(__dirname, '..', '.state');
const [OWN, THUMB] = process.argv.slice(2);
const sleep = ms => new Promise(r => setTimeout(r, ms));

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
    const help0 = fr.locator('.se-help-panel-close-button'); if (await help0.count()) { await help0.first().click().catch(() => {}); await sleep(800); }
    await fr.locator('[data-click-area="tpb*s.count"]').evaluate(e => e.click()); await sleep(2500);
    await fr.locator('li', { has: fr.locator('button[class*="article_button"]') }).filter({ hasText: OWN }).first().locator('button[class*="article_button"]').click(); await sleep(7000);
  }
  const help = fr.locator('.se-help-panel-close-button'); if (await help.count()) await help.first().click().catch(() => {});
  const title = (await fr.locator('.se-title-text').first().innerText()).trim();
  if (!title.includes(OWN)) { console.log('중단: 열린 글이 대상 글이 아님 →', title.slice(0, 40)); await b.close(); return; }
  console.log('열린 글:', title.slice(0, 50));
  const comps = () => fr.evaluate(() => [...document.querySelectorAll('.se-component')].filter(c => !c.classList.contains('se-documentTitle')));
  const order = () => fr.evaluate(() => [...document.querySelectorAll('.se-component')].filter(c => !c.classList.contains('se-documentTitle')).slice(0, 4)
    .map(c => (c.className.match(/se-(image|custom|text|quotation|imageGroup|placesMap)\b/) || [, '?'])[1]));
  const repInfo = () => fr.evaluate(() => [...document.querySelectorAll('.se-component')].filter(c => !c.classList.contains('se-documentTitle'))
    .map((c, i) => ({ i, rep: !!c.querySelector('.se-is-representative, [class*="representative"].se-is-selected, [class*="represent"][aria-pressed="true"]') || /대표/.test((c.querySelector('[class*="represent"]') || {}).innerText || '') && c.querySelector('[class*="represent"]').className.includes('selected') }))
    .filter(x => x.rep).map(x => x.i));
  console.log('앞부분(전):', JSON.stringify(await order()));

  // 0) THUMB_REPLACE=1: 썸네일을 먼저 넣은 뒤 내돈내산 카드를 넣어 [카드, 썸네일] 순서가 된 글 → 카드 아래 옛 썸네일을 지우고 다시 맨 위에 넣음
  if (process.env.THUMB_REPLACE) {
    const o = await order();
    if (o[0] !== 'custom' || o[1] !== 'image') { console.log('중단: [카드, 사진] 순서가 아님 →', JSON.stringify(o)); await b.close(); return; }
    const src = await fr.locator('.se-component.se-image').first().evaluate(c => ((c.querySelector('img') || {}).src || ''));
    if (!src.includes(process.env.THUMB_OLD || path.basename(THUMB))) { console.log('중단: 카드 아래 사진이 이 썸네일 파일이 아님 →', src.split('/').pop().slice(0, 50)); await b.close(); return; }
    const n0 = await fr.locator('.se-component').count();
    const old = fr.locator('.se-component.se-image').first();
    await old.scrollIntoViewIfNeeded(); await old.click({ position: { x: 200, y: 200 } }); await sleep(800); await old.hover(); await sleep(500);
    const ok = await old.evaluate(c => { const d = c.querySelector('.se-image-delete-button'); if (d) { d.click(); return true; } return false; });
    if (!ok) { const tb = fr.locator('.se-delete-toolbar-button:visible').first(); if (await tb.count()) await tb.click(); }
    await sleep(1500);
    if ((await fr.locator('.se-component').count()) === n0) {   // 버튼이 안 먹으면: 사진 선택 상태에서 도구막대 삭제 또는 Delete 키
      await old.click({ position: { x: 200, y: 200 } }); await sleep(600);
      const tb = fr.locator('.se-delete-toolbar-button:visible').first();
      if (await tb.count()) await tb.click(); else await page.keyboard.press('Delete');
      await sleep(1500);
    }
    if ((await fr.locator('.se-component').count()) !== n0 - 1) { console.log('중단: 옛 썸네일 삭제 실패', JSON.stringify(await order())); await page.screenshot({ path: S + '/shots/thumb_del_fail.png' }); await b.close(); return; }
    console.log('옛 썸네일 삭제 후:', JSON.stringify(await order()));
  }
  // 1) 제목 끝에서 Enter → 맨 위에 빈 줄 → 그 자리에 사진 넣기 (이미 사진·카드 순서면 건너뜀: 자동 저장으로 남은 경우)
  const pre = await order();
  if (pre[0] === 'image' && pre[1] === 'custom') console.log('맨 위에 이미 사진이 있음 → 넣기 건너뜀');   // (카드 없는 글은 아래 비교로 판단)
  else {
  await fr.locator('.se-title-text').first().click(); await page.keyboard.press('End'); await sleep(300);
  await page.keyboard.press('Enter'); await sleep(1000);
  console.log('Enter 후:', JSON.stringify(await order()));
  const [chooser] = await Promise.all([page.waitForEvent('filechooser', { timeout: 15000 }),
    fr.locator('button.se-image-toolbar-button, button[data-name="image"]').first().click()]);
  await chooser.setFiles(path.resolve(THUMB)); await sleep(6000);
  const ord = await order();
  console.log('사진 넣은 후:', JSON.stringify(ord));
  await page.screenshot({ path: S + '/shots/thumb_1_inserted.png' });
  if (ord[0] !== 'image' || ord[1] !== pre[0]) {   // 새 사진 바로 아래가 원래 첫 요소(카드 또는 첫 사진)여야 함
    console.log('중단: 썸네일이 맨 위에 들어가지 않음 → 되돌리고 저장 안 함');
    for (let i = 0; i < 3; i++) { await page.keyboard.press('Control+Z'); await sleep(500); }
    await b.close(); return;
  }
  }

  // 2) 대표 사진 지정: 첫 사진에 마우스를 올리면 왼쪽 위에 '대표' 버튼이 나타남
  const first = fr.locator('.se-component.se-image').first();
  await first.scrollIntoViewIfNeeded(); await first.hover(); await sleep(800);
  const repBtns = await first.evaluate(c => [...c.querySelectorAll('button, [role=button]')].map(e => `${e.className} | ${e.innerText.trim()} | ${e.getAttribute('aria-pressed')}`));
  console.log('첫 사진 버튼:', JSON.stringify(repBtns));
  for (let t = 0; t < 5; t++) {   // 막 올린 사진은 처리 중이라 '대표' 버튼이 늦게 생김 → 선택·마우스 올리기를 반복
    const rep = first.locator('button.se-set-rep-image-button, button').filter({ hasText: '대표' }).first();
    if (await rep.count()) { await rep.click({ force: true }); await sleep(1200);
      if (await first.locator('.se-set-rep-image-button.se-is-selected').count()) break; }
    await first.click({ position: { x: 200, y: 150 } }).catch(() => {}); await first.hover(); await sleep(2500);
  }
  await page.screenshot({ path: S + '/shots/thumb_2_rep.png' });
  const repState = await fr.evaluate(() => [...document.querySelectorAll('.se-component.se-image')].slice(0, 30).map((c, i) => {
    const btn = [...c.querySelectorAll('button')].find(e => /대표/.test(e.innerText)); return btn ? `${i}:${btn.className}` : null; }).filter(Boolean));
  console.log('대표 버튼 상태:', JSON.stringify(repState));
  const firstSelected = repState.length && /select|active|on|checked/i.test(repState[0].split(':')[1]) && repState[0].startsWith('0:');
  if (!firstSelected) { console.log('대표 지정 확인 실패 → 저장하지 않음 (화면 thumb_2_rep.png 확인)'); await b.close(); return; }
  await fr.locator('[data-click-area="tpb.save"]').click(); await sleep(4000);
  console.log('저장 완료');
  await ctx.storageState({ path: S + '/naver-state.json' });
  await b.close();
})().catch(e => { console.log('오류: ' + e.message.slice(0, 300)); process.exit(1); });
