// 이미 발행된 글의 썸네일(맨 위 첫 사진)을 지우고 새 썸네일을 넣어 대표 사진으로 지정한 뒤 수정 발행한다.
// 사용법: node automation/edit_thumb.js <가게 이름(제목에서 찾을 글자)> <새 썸네일.jpg> [--dry] [--category 먹보여행|제품리뷰]
//   --dry: 바꾸기·대표 지정·발행 설정 창 확인까지만 (발행 안 함, 수정 내용 버림)
// 안전장치: 제목이 다르면 멈춤. 첫 컴포넌트가 사진이 아니면 멈춤. 새 사진이 맨 위·대표가 아니면 발행하지 않음.
const { chromium } = require('playwright');
const path = require('path');
const S = process.env.NAVER_STATE_DIR || path.join(__dirname, '..', '.state');
const BLOG = 'seoeunjin13';
const args = process.argv.slice(2);
const DRY = args.includes('--dry');
const ci = args.indexOf('--category'); const CATEGORY = ci >= 0 ? args[ci + 1] : null;
const [STORE, THUMB] = args.filter((a, i) => !a.startsWith('--') && !(ci >= 0 && i === ci + 1));
const sleep = ms => new Promise(r => setTimeout(r, ms));
const norm = s => (s || '').replace(/\s+/g, '');
const { selectCategory } = require('./category');

async function findPost(store) {
  const hits = [];
  for (let page = 1; page <= 20; page++) {
    const r = await fetch(`https://m.blog.naver.com/api/blogs/${BLOG}/post-list?categoryNo=0&itemCount=30&page=${page}`, { headers: { Referer: `https://m.blog.naver.com/${BLOG}`, 'User-Agent': 'Mozilla/5.0' } });
    const items = ((await r.json()).result || {}).items || [];
    if (!items.length) break;
    for (const it of items) if (norm(it.titleWithInspectMessage).includes(norm(store))) hits.push({ logNo: String(it.logNo), title: it.titleWithInspectMessage });
  }
  return hits;
}

(async () => {
  const hits = await findPost(STORE);
  console.log('찾은 글:', JSON.stringify(hits.map(h => `${h.logNo} ${h.title.slice(0, 40)}`)));
  if (hits.length !== 1) { console.log('중단: 글이 1개가 아님'); process.exit(2); }
  const { logNo } = hits[0];
  const b = await chromium.launch();
  const ctx = await b.newContext({ storageState: S + '/naver-state.json', locale: 'ko-KR', viewport: { width: 1400, height: 1000 } });
  const page = await ctx.newPage(); page.on('dialog', d => { console.log('대화상자:', d.message().slice(0, 60)); d.accept(); });
  await page.goto(`https://blog.naver.com/PostUpdateForm.naver?blogId=${BLOG}&logNo=${logNo}`, { waitUntil: 'domcontentloaded', timeout: 60000 });
  await sleep(10000);
  const fr = page.frame('mainFrame') || page.mainFrame();
  if (await fr.locator('.se-popup-button-cancel').count()) { console.log('중단: 이어쓰기 창이 떴음 (손대지 않음)'); await b.close(); process.exit(3); }
  const help = fr.locator('.se-help-panel-close-button'); if (await help.count()) await help.first().click().catch(() => {});
  const title = (await fr.locator('.se-title-text').first().innerText()).trim();
  if (!norm(title).includes(norm(STORE))) { console.log('중단: 제목이 다름 →', title.slice(0, 40)); await b.close(); process.exit(4); }
  console.log('수정 화면:', title.slice(0, 50));
  const order = () => fr.evaluate(() => [...document.querySelectorAll('.se-component')].filter(c => !c.classList.contains('se-documentTitle')).slice(0, 4)
    .map(c => (c.className.match(/se-(image|custom|text|quotation|imageGroup|placesMap)\b/) || [, '?'])[1]));
  const before = await order(); console.log('앞부분(전):', JSON.stringify(before));
  if (before[0] !== 'image') { console.log('중단: 맨 위가 사진이 아님'); await b.close(); process.exit(5); }
  const n0 = await fr.locator('.se-component').count();

  // 1) 기존 썸네일 삭제: 첫 사진 선택 → 사진 도구막대의 '삭제'
  const first = fr.locator('.se-component.se-image').first();
  await first.scrollIntoViewIfNeeded(); await first.click({ position: { x: 200, y: 200 } }); await sleep(800);
  await first.hover(); await sleep(500);
  const clicked = await first.evaluate(c => { const d = c.querySelector('.se-image-delete-button'); if (d) { d.click(); return true; } return false; });
  if (!clicked) { const tb = fr.locator('.se-delete-toolbar-button:visible').first(); if (await tb.count()) await tb.click(); }
  await sleep(1500);
  if ((await fr.locator('.se-component').count()) === n0) {   // 버튼이 안 먹으면: 사진 선택 상태에서 Delete 키
    await first.click({ position: { x: 200, y: 200 } }); await sleep(600);
    const tb = fr.locator('.se-delete-toolbar-button:visible').first();
    if (await tb.count()) await tb.click(); else await page.keyboard.press('Delete');
    await sleep(1500);
  }
  const afterDel = await order(); console.log('삭제 후:', JSON.stringify(afterDel));
  if ((await fr.locator('.se-component').count()) !== n0 - 1) { console.log('중단: 삭제 결과가 이상함'); await b.close(); process.exit(6); }

  // 2) 제목 끝 Enter → 맨 위 빈 줄 → 새 사진
  await fr.locator('.se-title-text').first().click(); await page.keyboard.press('End'); await sleep(300);
  await page.keyboard.press('Enter'); await sleep(1000);
  const [chooser] = await Promise.all([page.waitForEvent('filechooser', { timeout: 15000 }),
    fr.locator('button.se-image-toolbar-button, button[data-name="image"]').first().click()]);
  await chooser.setFiles(path.resolve(THUMB)); await sleep(7000);
  const ord = await order(); console.log('새 사진 후:', JSON.stringify(ord));
  if (ord[0] !== 'image' || ord[1] !== before[1]) { console.log('중단: 새 썸네일이 맨 위에 들어가지 않음 → 발행 안 함'); await page.screenshot({ path: S + '/shots/edit_thumb_fail.png' }); await b.close(); process.exit(7); }

  // 3) 대표 지정
  const nf = fr.locator('.se-component.se-image').first();
  await nf.scrollIntoViewIfNeeded(); await nf.hover(); await sleep(800);
  const rep = nf.locator('button').filter({ hasText: '대표' }).first();
  if (await rep.count()) { await rep.click({ force: true }); await sleep(1000); }
  const repState = await fr.evaluate(() => [...document.querySelectorAll('.se-component.se-image')].map((c, i) => {
    const btn = [...c.querySelectorAll('button')].find(e => /대표/.test(e.innerText)); return btn && /se-is-selected/.test(btn.className) ? i : null; }).filter(x => x !== null));
  console.log('대표 사진 위치:', JSON.stringify(repState));
  if (JSON.stringify(repState) !== '[0]') { console.log('중단: 대표 지정 실패 → 발행 안 함'); await b.close(); process.exit(8); }
  await page.screenshot({ path: S + '/shots/edit_thumb_1.png' });

  // 4) 발행 설정 창 → (카테고리) → 발행
  await fr.locator('[data-click-area="tpb.publish"]').click(); await sleep(2500);
  const cat = await selectCategory(fr, page, CATEGORY, S);
  console.log('카테고리:', cat);
  await page.screenshot({ path: S + '/shots/edit_thumb_2_layer.png' });
  if (CATEGORY && cat !== CATEGORY) { console.log('중단: 카테고리 설정 실패 → 발행 안 함'); await b.close(); process.exit(9); }
  if (DRY) { console.log('확인 모드: 발행하지 않고 닫음 (수정 내용 버림)'); await b.close(); return; }
  const confirm = fr.locator('[data-click-area="tpb*i.publish"], button[class*="confirm_btn"]').first();
  await confirm.click(); await sleep(7000);
  console.log('발행 후 주소:', page.url());
  await ctx.storageState({ path: S + '/naver-state.json' });
  await b.close();
  console.log(`완료: logNo ${logNo} 썸네일 교체·수정 발행`);
})().catch(e => { console.log('오류: ' + e.message.slice(0, 300)); process.exit(1); });
