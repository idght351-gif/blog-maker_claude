// 임시저장된 글을 열어 본문 문구를 바꾸고 다시 저장한다 (서식은 그대로 두고 글자만 바꿈).
// 사용법: node automation/replace_text.js <제목 문구> '[["바꿀 문구","새 문구"], ...]'
// 안전장치: 제목이 다르면 멈춤. 바꿀 문구가 본문에 정확히 1번 있을 때만 바꿈. 하나라도 실패하면 저장하지 않음.
//          "이어서 쓸까요?" 창에서 '취소'는 절대 누르지 않음 (누르면 그 글이 지워짐).
const { chromium } = require('playwright');
const path = require('path');
const S = process.env.NAVER_STATE_DIR || path.join(__dirname, '..', '.state');
const [OWN, PAIRS] = process.argv.slice(2);
const pairs = JSON.parse(PAIRS);
const sleep = ms => new Promise(r => setTimeout(r, ms));
(async () => {
  const b = await chromium.launch();
  const ctx = await b.newContext({ storageState: S + '/naver-state.json', locale: 'ko-KR', viewport: { width: 1400, height: 1000 } });
  const page = await ctx.newPage(); page.on('dialog', d => { console.log('대화상자:', d.message().slice(0, 60)); d.accept(); });
  await page.goto('https://blog.naver.com/seoeunjin13?Redirect=Write&', { waitUntil: 'domcontentloaded', timeout: 60000 }); await sleep(10000);
  const fr = page.frame('mainFrame');
  let needList = true;
  if (await fr.locator('.se-popup-button-cancel').count()) {
    await fr.locator('.se-popup-button-confirm').first().click(); await sleep(5000);
    needList = !(await fr.locator('.se-title-text').first().innerText()).includes(OWN);
  }
  if (needList) {
    const h = fr.locator('.se-help-panel-close-button'); if (await h.count()) { await h.first().click().catch(() => {}); await sleep(800); }
    await fr.locator('[data-click-area="tpb*s.count"]').evaluate(e => e.click()); await sleep(2500);
    await fr.locator('li', { has: fr.locator('button[class*="article_button"]') }).filter({ hasText: OWN }).first().locator('button[class*="article_button"]').click(); await sleep(7000);
  }
  const h2 = fr.locator('.se-help-panel-close-button'); if (await h2.count()) await h2.first().click().catch(() => {});
  const title = (await fr.locator('.se-title-text').first().innerText()).trim();
  if (!title.includes(OWN)) { console.log('중단: 열린 글이 대상 글이 아님 →', title.slice(0, 40)); await b.close(); process.exit(2); }
  console.log('열린 글:', title.slice(0, 50));
  for (const [from, to] of pairs) {
    // 바꿀 문구가 들어 있는 글자 조각(text node)을 찾아 그 부분만 선택
    const found = await fr.evaluate(from => {
      const nodes = []; const w = document.createTreeWalker(document.querySelector('.se-content') || document.body, NodeFilter.SHOW_TEXT);
      while (w.nextNode()) if (w.currentNode.nodeValue.includes(from)) nodes.push(w.currentNode);
      if (nodes.length !== 1 || nodes[0].nodeValue.split(from).length !== 2) return nodes.length;
      const n = nodes[0], i = n.nodeValue.indexOf(from);
      n.parentElement.scrollIntoView({ block: 'center' });
      const r = document.createRange(); r.setStart(n, i); r.setEnd(n, i + from.length);
      r.collapse(true); const rc = r.getBoundingClientRect();
      return { x: rc.left, y: rc.top + rc.height / 2 };
    }, from);
    if (typeof found !== 'object') { console.log(`중단: "${from}" 이(가) ${found}곳에서 발견됨 (1곳이어야 함) → 저장 안 함`); await b.close(); process.exit(3); }
    // 에디터가 알아듣도록 실제 마우스 클릭으로 커서를 놓고 Shift+→로 선택한 뒤 타이핑
    const fb = await page.locator('#mainFrame').boundingBox() || { x: 0, y: 0 };
    await page.mouse.click(fb.x + found.x + 1, fb.y + found.y); await sleep(400);
    for (let k = 0; k < [...from].length; k++) await page.keyboard.press('Shift+ArrowRight');
    await sleep(300);
    await page.keyboard.type(to, { delay: 30 }); await sleep(800);
    const ok = await fr.evaluate(([from, to]) => { const t = (document.querySelector('.se-content') || document.body).innerText; return t.includes(to) && !t.includes(from) || from.includes(to); }, [from, to]);
    console.log(ok ? `바꿈: "${from}" → "${to}"` : `확인 실패: "${from}"`);
    if (!ok) { await page.screenshot({ path: S + '/shots/replace_fail.png' }); await b.close(); process.exit(4); }
  }
  await fr.locator('[data-click-area="tpb.save"]').click(); await sleep(4000);
  console.log('저장 완료');
  await b.close();
})().catch(e => { console.log('오류: ' + e.message.slice(0, 200)); process.exit(1); });
