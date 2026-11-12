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
  if (await fr.locator('.se-popup-button-cancel').count()) { await fr.locator('.se-popup-button-confirm').first().click(); await sleep(5000); }
  else {
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

  // 1) 제목 끝에서 Enter → 맨 위에 빈 줄 → 그 자리에 사진 넣기 (이미 사진·카드 순서면 건너뜀: 자동 저장으로 남은 경우)
  const pre = await order();
  if (pre[0] === 'image' && pre[1] === 'custom') console.log('맨 위에 이미 사진이 있음 → 넣기 건너뜀');
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
  if (ord[0] !== 'image' || ord[1] !== 'custom') {
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
  const rep = first.locator('button').filter({ hasText: '대표' }).first();
  if (await rep.count()) { await rep.click({ force: true }); await sleep(1000); }
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
