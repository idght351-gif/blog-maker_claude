// 2차 입력기: 서식 있는 글은 '붙여넣기'로, 사진은 업로드로 넣고,
// 에디터 글과 초안을 한 줄씩 비교해 빠진 줄이 0개일 때만 '저장'(임시저장)한다. 발행은 하지 않는다.
// 사용법: node write_draft2.js <spec2.json>
const { chromium } = require('playwright');
const fs = require('fs');
const S = process.env.NAVER_STATE_DIR || require('path').join(__dirname, __dirname.endsWith('probes') ? '../..' : '..', '.state');
const spec = JSON.parse(fs.readFileSync(process.argv[2], 'utf8'));
const sleep = ms => new Promise(r => setTimeout(r, ms));
const norm = s => s.replace(/[\s​ ]/g, '');
const BODY = '.se-component.se-text .se-text-paragraph';

(async () => {
  const b = await chromium.launch();
  const ctx = await b.newContext({ storageState: S + '/naver-state.json', locale: 'ko-KR', viewport: { width: 1400, height: 1000 },
    userAgent: 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36' });
  const page = await ctx.newPage();
  page.on('dialog', d => { console.log('대화상자:', d.message().slice(0, 80)); d.dismiss(); });
  await page.goto('https://blog.naver.com/seoeunjin13?Redirect=Write&', { waitUntil: 'domcontentloaded', timeout: 60000 });
  await sleep(10000);
  const fr = page.frame('mainFrame');
  // "이어서 쓸까요?" 창이 뜨면 다른 글이 지워질 수 있으므로 아무것도 누르지 않고 멈춘다
  if (await fr.locator('.se-popup-button-cancel').count()) {
    await fr.locator('.se-popup-button-confirm').first().click(); await sleep(4000);   // 이어쓰기로 열기 (삭제 없음)
    const t = (await fr.locator('.se-title-text').first().innerText()).trim();
    const body = await fr.evaluate(sel => [...document.querySelectorAll(sel)].map(p => p.innerText).join(' '), BODY);
    if (!t.includes('쿠로카메') && !body.includes('쿠로카메 라멘')) { console.log('중단: 이어쓰기 글이 다른 글임 →', t.slice(0, 40), '/', body.slice(0, 40)); await b.close(); return; }
    console.log('이전 시험 글 이어쓰기 → 내용 비우고 다시 입력');
    await fr.locator('.se-title-text').first().click(); await page.keyboard.press('Control+A'); await page.keyboard.press('Delete');
    await fr.locator(BODY).first().click(); await page.keyboard.press('Control+A'); await page.keyboard.press('Delete'); await sleep(1500);
  }
  const help = fr.locator('.se-help-panel-close-button'); if (await help.count()) { await help.first().click().catch(() => {}); await sleep(500); }
  const countBtn = fr.locator('[data-click-area="tpb*s.count"]');
  const before = (await countBtn.innerText()).trim();

  const paste = async html => {
    let done = false;
    for (const f of page.frames()) {
      if (!f.name().startsWith('input_buffer')) continue;
      done = await f.evaluate(h => {
        const el = document.body; if (!el) return false;
        const dt = new DataTransfer(); dt.setData('text/html', h); dt.setData('text/plain', h.replace(/<[^>]+>/g, ' '));
        el.dispatchEvent(new ClipboardEvent('paste', { clipboardData: dt, bubbles: true, cancelable: true })); return true;
      }, html).catch(() => false);
      if (done) break;
    }
    if (!done) throw new Error('붙여넣기 대상(입력 버퍼)을 찾지 못함');
    await sleep(1200);
  };

  // 제목
  await fr.locator('.se-title-text').first().click(); await page.keyboard.insertText(spec.title); await sleep(600);
  // 본문
  await fr.locator('.se-component.se-text .se-text-paragraph').first().click(); await sleep(600);
  let n = 0;
  for (const blk of spec.blocks) {
    n++;
    if (blk.t === 'html') await paste(blk.html);
    else {
      const beforeImg = await fr.locator('.se-image-resource').count();
      const [chooser] = await Promise.all([page.waitForEvent('filechooser', { timeout: 15000 }),
        fr.locator('button.se-image-toolbar-button, button[data-name="image"]').first().click()]);
      await chooser.setFiles(blk.files); await sleep(2500);
      if (blk.files.length > 1) { const col = fr.locator('button:has-text("콜라주"), label:has-text("콜라주")'); if (await col.count()) { await col.first().click().catch(() => {}); await sleep(1500); } }
      for (let t = 0; t < 60; t++) { if ((await fr.locator('.se-image-resource').count()) >= beforeImg + blk.files.length) break; await sleep(1000); }
      await sleep(800);
    }
    if (n % 10 === 0) console.log(`진행 ${n}/${spec.blocks.length}`);
  }
  // 전체 가운데 정렬
  try {
    await fr.locator(BODY).last().click(); await page.keyboard.press('Control+A'); await sleep(500);
    await fr.locator('button:has-text("정렬 열기")').first().click(); await sleep(700);
    await fr.locator('button:has-text("가운데 정렬")').first().click(); await sleep(800);
    await page.keyboard.press('ArrowDown');
    console.log('가운데 정렬 적용');
  } catch (e) { console.log('정렬 적용 실패:', e.message.slice(0, 80)); }

  // 검증: 초안의 모든 줄이 에디터에 있는지
  const editorText = norm(await fr.evaluate(() => [...document.querySelectorAll('.se-component.se-text .se-text-paragraph')].map(p => p.innerText).join('\n')));
  const missing = spec.lines.filter(l => norm(l) && !editorText.includes(norm(l)));
  const stats = await fr.evaluate(() => ({
    img: document.querySelectorAll('.se-component .se-image-resource').length,
    center: document.querySelectorAll('.se-component.se-text .se-text-paragraph-align-center').length,
    paras: document.querySelectorAll('.se-component.se-text .se-text-paragraph').length,
    fs19: document.querySelectorAll('.se-component.se-text .se-fs19').length,
    fs24: document.querySelectorAll('.se-component.se-text .se-fs24').length,
    colored: [...document.querySelectorAll('.se-component.se-text span[style*="color"]')].filter(s => !/rgb\(0, 0, 0\)/.test(s.style.color) && s.style.color).length,
    bold: document.querySelectorAll('.se-component.se-text b').length,
    highlight: document.querySelectorAll('.se-component.se-text .se-highlight').length,
    fs15: document.querySelectorAll('.se-component.se-text .se-fs15').length }));
  console.log('검증:', JSON.stringify(stats), `빠진 줄 ${missing.length}/${spec.lines.length}`);
  if (missing.length) console.log('빠진 줄 예:', missing.slice(0, 5).join(' | '));
  await page.screenshot({ path: S + '/shots/v2_end.png' });

  if (missing.length === 0) {
    await fr.locator('[data-click-area="tpb.save"]').click(); await sleep(4000);
    console.log(`임시저장 완료: 임시저장 글 수 ${before} → ${(await countBtn.innerText()).trim()}`);
    await page.screenshot({ path: S + '/shots/v2_saved.png' });
  } else {
    console.log('빠진 줄이 있어 저장하지 않음. 입력 내용 비움');
    await fr.locator('.se-component.se-text .se-text-paragraph').first().click(); await page.keyboard.press('Control+A'); await page.keyboard.press('Delete');
  }
  await ctx.storageState({ path: S + '/naver-state.json' });
  await b.close();
})().catch(e => { console.log('오류: ' + e.message.slice(0, 300)); process.exit(1); });
