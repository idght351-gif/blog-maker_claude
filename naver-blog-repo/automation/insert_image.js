// 임시저장된 글을 열어 지정한 문장 바로 아래에 사진/GIF를 넣거나, 파일 이름으로 기존 사진을 지운 뒤 저장한다.
// 사용법: node automation/insert_image.js <제목 문구> '<작업 JSON>'
//   작업 JSON 예: [{"after":"속살까지 잘 배어 있어요","file":"photos/bhc/blur/IMG_9731.gif"}, {"remove":"IMG_9702.gif"}]
//   - after: 이 문구가 들어간 문단(정확히 1곳) 바로 아래에 file을 넣음
//   - remove: 사진 주소(src)에 이 글자가 들어간 사진(정확히 1장)을 지움
// 안전장치: 제목이 다르면 멈춤. 문구/사진이 1곳이 아니거나 결과 확인이 안 되면 저장하지 않음.
//          "이어서 쓸까요?" 창에서 '취소'는 절대 누르지 않음 (누르면 그 글이 지워짐).
const { chromium } = require('playwright');
const path = require('path');
const S = process.env.NAVER_STATE_DIR || path.join(__dirname, '..', '.state');
const [OWN, OPS] = process.argv.slice(2);
const ops = JSON.parse(OPS);
const sleep = ms => new Promise(r => setTimeout(r, ms));
(async () => {
  const b = await chromium.launch();
  const ctx = await b.newContext({ storageState: S + '/naver-state.json', locale: 'ko-KR', viewport: { width: 1400, height: 1000 } });
  const page = await ctx.newPage(); page.on('dialog', d => { console.log('대화상자:', d.message().slice(0, 60)); d.accept(); });
  // POST_LOGNO=<글 번호>: 이미 발행된 글을 수정 화면으로 열고, 끝나면 '저장' 대신 수정 발행 (카테고리는 그대로)
  const LOGNO = process.env.POST_LOGNO;
  await page.goto(LOGNO ? `https://blog.naver.com/PostUpdateForm.naver?blogId=seoeunjin13&logNo=${LOGNO}` : 'https://blog.naver.com/seoeunjin13?Redirect=Write&', { waitUntil: 'domcontentloaded', timeout: 60000 }); await sleep(10000);
  const fr = page.frame('mainFrame') || page.mainFrame();
  let needList = !LOGNO;
  if (LOGNO && await fr.locator('.se-popup-button-cancel').count()) { console.log('중단: 수정 화면에 이어쓰기 창이 떴음 (손대지 않음)'); await b.close(); process.exit(7); }
  if (!LOGNO && await fr.locator('.se-popup-button-cancel').count()) {
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
  const fb = await page.locator('#mainFrame').boundingBox() || { x: 0, y: 0 };
  const imgCount = () => fr.locator('.se-component.se-image').count();

  for (const op of ops) {
    if (op.remove || op.removeAfter) {
      // removeAfter: 그 문구 문단 바로 다음에 있는 사진을 지움 (사진 주소는 화면에 보일 때만 채워져서 위치로 찾는 쪽이 확실함)
      const idx = op.removeAfter
        ? await fr.evaluate(anchor => {
            const comps = [...document.querySelectorAll('.se-component')];
            const hits = comps.map((c, i) => [...c.querySelectorAll('.se-text-paragraph')].some(p => p.innerText.includes(anchor)) ? i : -1).filter(i => i >= 0);
            if (hits.length !== 1 || !comps[hits[0] + 1] || !comps[hits[0] + 1].classList.contains('se-image')) return [];
            return [[...document.querySelectorAll('.se-component.se-image')].indexOf(comps[hits[0] + 1])];
          }, op.removeAfter)
        : await fr.evaluate(key => [...document.querySelectorAll('.se-component.se-image')].map((c, i) => ((c.querySelector('img') || {}).src || '').includes(key) ? i : -1).filter(i => i >= 0), op.remove);
      op.remove = op.remove || `"${op.removeAfter}" 아래 사진`;
      if (idx.length !== 1) { console.log(`중단: ${op.remove} 이(가) ${idx.length}장 (1장이어야 함) → 저장 안 함`); await b.close(); process.exit(3); }
      const n0 = await fr.locator('.se-component').count(); const i0 = await imgCount();
      const el = fr.locator('.se-component.se-image').nth(idx[0]);
      await el.scrollIntoViewIfNeeded(); await el.click({ position: { x: 150, y: 120 } }); await sleep(800); await el.hover(); await sleep(500);
      const ok = await el.evaluate(c => { const d = c.querySelector('.se-image-delete-button'); if (d) { d.click(); return true; } return false; });
      if (!ok) { const tb = fr.locator('.se-delete-toolbar-button:visible').first(); if (await tb.count()) await tb.click(); else await page.keyboard.press('Delete'); }
      await sleep(1500);
      for (let t = 0; t < 3 && (await imgCount()) === i0; t++) {   // 안 지워졌으면 다시 선택해서 도구막대 '삭제' 또는 Delete 키
        await el.scrollIntoViewIfNeeded(); await el.click({ position: { x: 200, y: 200 } }).catch(() => {}); await sleep(800);
        const tb = fr.locator('.se-delete-toolbar-button:visible').first();
        if (await tb.count()) await tb.click(); else await page.keyboard.press('Delete');
        await sleep(1500);
      }
      if ((await imgCount()) !== i0 - 1 || (await fr.locator('.se-component').count()) < n0 - 2) { await page.screenshot({ path: S + '/shots/remove_fail.png' }); console.log('개수', n0, await fr.locator('.se-component').count()); console.log(`중단: "${op.remove}" 삭제 확인 실패`); await b.close(); process.exit(4); }
      console.log(`지움: ${op.remove}`);
      continue;
    }
    // 1) 문구가 든 문단 끝을 실제 마우스로 클릭 → End → Enter 로 바로 아래 빈 줄 만들기
    const pos = await fr.evaluate(anchor => {
      const ps = [...document.querySelectorAll('.se-component .se-text-paragraph')].filter(p => p.innerText.includes(anchor));
      if (ps.length !== 1) return ps.length;
      const p = ps[0]; p.scrollIntoView({ block: 'center' });
      const w = document.createTreeWalker(p, NodeFilter.SHOW_TEXT); let last = null; while (w.nextNode()) if (w.currentNode.nodeValue.trim()) last = w.currentNode;
      const r = document.createRange(); r.setStart(last, last.nodeValue.length); r.collapse(true);
      const rc = r.getBoundingClientRect(); return { x: rc.left, y: rc.top + rc.height / 2 };
    }, op.after);
    if (typeof pos !== 'object') { console.log(`중단: "${op.after}" 문단이 ${pos}곳 (1곳이어야 함) → 저장 안 함`); await b.close(); process.exit(5); }
    const before = await imgCount();
    await page.mouse.click(fb.x + pos.x - 2, fb.y + pos.y); await sleep(400);
    await page.keyboard.press('End'); await sleep(200);
    await page.keyboard.press('Enter'); await sleep(800);
    // 2) 사진 버튼으로 파일 올리기
    const [chooser] = await Promise.all([page.waitForEvent('filechooser', { timeout: 15000 }),
      fr.locator('button.se-image-toolbar-button, button[data-name="image"]').first().click()]);
    await chooser.setFiles(path.resolve(op.file)); await sleep(12000);
    // 3) 확인: 사진이 1장 늘고, 문구 문단 바로 다음 컴포넌트가 사진이어야 함
    const check = await fr.evaluate(anchor => {
      const comps = [...document.querySelectorAll('.se-component')];
      const i = comps.findIndex(c => [...c.querySelectorAll('.se-text-paragraph')].some(p => p.innerText.includes(anchor)));
      if (i < 0) return 'anchor-lost';
      const paras = [...comps[i].querySelectorAll('.se-text-paragraph')];
      const lastIsAnchor = paras.length && paras[paras.length - 1].innerText.includes(anchor);
      const next = comps[i + 1];
      return lastIsAnchor && next && next.classList.contains('se-image') ? 'ok' : `next=${next ? next.className.slice(0, 40) : 'none'} lastIsAnchor=${lastIsAnchor}`;
    }, op.after);
    const after = await imgCount();
    console.log(`넣음: ${path.basename(op.file)} (사진 ${before}→${after}, 위치 ${check})`);
    if (after !== before + 1 || check !== 'ok') { await page.screenshot({ path: S + '/shots/insert_fail.png' }); console.log('중단: 위치 확인 실패 → 저장 안 함'); await b.close(); process.exit(6); }
  }
  if (LOGNO) {
    await fr.locator('[data-click-area="tpb.publish"]').click(); await sleep(2500);
    console.log('카테고리(그대로):', await require('./category').current(fr).catch(() => '?'));
    await fr.locator('[data-click-area="tpb*i.publish"], button[class*="confirm_btn"]').first().click(); await sleep(7000);
    console.log('수정 발행 완료:', page.url());
  } else {
    await fr.locator('[data-click-area="tpb.save"]').click(); await sleep(4000);
    console.log('저장 완료');
  }
  await b.close();
})().catch(e => { console.log('오류: ' + e.message.slice(0, 200)); process.exit(1); });
