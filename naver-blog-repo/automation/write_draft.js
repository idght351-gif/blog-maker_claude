// 초안을 네이버 스마트에디터에 입력하고 '저장'(임시저장)만 누른다. 발행은 하지 않는다.
// 사용법: node write_draft.js <spec.json>
const { chromium } = require('playwright');
const fs = require('fs');
const S = process.env.NAVER_STATE_DIR || require('path').join(__dirname, __dirname.endsWith('probes') ? '../..' : '..', '.state');
const spec = JSON.parse(fs.readFileSync(process.argv[2], 'utf8'));
const sleep = ms => new Promise(r => setTimeout(r, ms));
(async () => {
  const b = await chromium.launch();
  const ctx = await b.newContext({ storageState: S + '/naver-state.json', locale: 'ko-KR', viewport: { width: 1400, height: 1000 },
    userAgent: 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36' });
  const page = await ctx.newPage();
  page.on('dialog', d => { console.log('대화상자:', d.message().slice(0, 80)); d.dismiss(); });
  await page.goto('https://blog.naver.com/seoeunjin13?Redirect=Write&', { waitUntil: 'domcontentloaded', timeout: 60000 });
  await sleep(10000);
  const fr = page.frame('mainFrame');
  // 이전 작성글 이어쓰기 팝업 → 취소, 도움말 닫기
  const cancel = fr.locator('.se-popup-button-cancel'); if (await cancel.count()) { await cancel.first().click(); console.log('이어쓰기 팝업 취소'); await sleep(1000); }
  const help = fr.locator('.se-help-panel-close-button'); if (await help.count()) { await help.first().click().catch(() => {}); await sleep(500); }
  const draftsBefore = (await fr.locator('button:has-text("저장")').first().innerText()).replace(/\D/g, '');
  // 제목
  await fr.locator('.se-title-text').first().click(); await page.keyboard.insertText(spec.title); await sleep(500);
  // 본문 시작 + 가운데 정렬
  await fr.locator('.se-component.se-text .se-text-paragraph').first().click(); await sleep(500);
  try {
    await fr.locator('button[data-name="align-drop-down-with-justify"], button:has-text("정렬")').first().click(); await sleep(600);
    await fr.locator('button[data-value="center"], button:has-text("가운데 정렬")').first().click(); console.log('가운데 정렬 설정');
  } catch (e) { console.log('정렬 설정 실패:', e.message.slice(0, 80)); }
  await sleep(500);
  let imgCount = 0, n = 0;
  for (const blk of spec.blocks) {
    n++;
    if (blk.t === 'text') {
      for (const [txt, bold] of blk.segs) {
        if (bold) await page.keyboard.press('Control+B');
        const parts = txt.split('\n');
        for (let i = 0; i < parts.length; i++) { if (parts[i]) await page.keyboard.insertText(parts[i]); if (i < parts.length - 1) await page.keyboard.press('Enter'); }
        if (bold) await page.keyboard.press('Control+B');
      }
      await page.keyboard.press('Enter');
      if (blk.gap) await page.keyboard.press('Enter');
    } else if (blk.t === 'img') {
      const before = await fr.locator('.se-image-resource').count();
      const [chooser] = await Promise.all([page.waitForEvent('filechooser', { timeout: 15000 }),
        fr.locator('button.se-image-toolbar-button, button[data-name="image"]').first().click()]);
      await chooser.setFiles(blk.files);
      await sleep(2500);
      if (blk.files.length > 1) {   // 여러 장: 콜라주 선택 창이 뜨면 콜라주
        const col = fr.locator('button:has-text("콜라주"), label:has-text("콜라주")');
        if (await col.count()) { await col.first().click().catch(() => {}); console.log('콜라주 선택'); await sleep(1500); }
      }
      for (let t = 0; t < 60; t++) { if ((await fr.locator('.se-image-resource').count()) >= before + blk.files.length) break; await sleep(1000); }
      imgCount += blk.files.length;
      await sleep(800);
    }
    if (n % 15 === 0) { console.log(`진행 ${n}/${spec.blocks.length} (사진 ${imgCount})`); await page.screenshot({ path: `${S}/shots/write_${n}.png` }); }
  }
  console.log('입력 완료, 사진', await fr.locator('.se-image-resource').count(), '장');
  await page.screenshot({ path: S + '/shots/write_end.png' });
  // 임시저장
  await fr.locator('button:has-text("저장")').first().click();
  await sleep(4000);
  const draftsAfter = (await fr.locator('button:has-text("저장")').first().innerText()).replace(/\D/g, '');
  console.log(`임시저장 완료: 임시저장 글 수 ${draftsBefore} → ${draftsAfter}`);
  await page.screenshot({ path: S + '/shots/saved.png' });
  await ctx.storageState({ path: S + '/naver-state.json' });
  await b.close();
})().catch(e => { console.log('오류: ' + e.message.slice(0, 300)); process.exit(1); });
