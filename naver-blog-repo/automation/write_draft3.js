// 3차 입력기 (STYLE.md 5-0 사용자 서식 지시 반영)
// - 제목: 한 글자씩 입력 / 본문: 서식 있는 붙여넣기 / 사진: 업로드
// - 소제목·후킹 문구·미리보기: 네이버 인용구(4=밑줄, 1=기본, 3=말풍선) + 가운데 정렬, 본문은 왼쪽 정렬
// - 맨 아래 장소 지도, 해시태그
// - 초안의 모든 줄이 '순서대로' 들어갔고 인용구 수가 맞을 때만 '저장'(임시저장). 발행은 하지 않음
// - 저장 후 예전 쿠로카메 시험 글(가장 최신 1개 제외)을 임시저장 목록에서 삭제
// 사용법: node write_draft3.js <spec3.json> <예전 시험 글 제목 문구>
const { chromium } = require('playwright');
const fs = require('fs');
const S = process.env.NAVER_STATE_DIR || require('path').join(__dirname, __dirname.endsWith('probes') ? '../..' : '..', '.state');
const spec = JSON.parse(fs.readFileSync(process.argv[2], 'utf8'));
const OWN = process.argv[3] || '쿠로카메';
const sleep = ms => new Promise(r => setTimeout(r, ms));
const norm = s => s.replace(/[\s​ ]/g, '');
const BODY = '.se-component.se-text .se-text-paragraph';

(async () => {
  const b = await chromium.launch();
  const ctx = await b.newContext({ storageState: S + '/naver-state.json', locale: 'ko-KR', viewport: { width: 1400, height: 1000 },
    userAgent: 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36' });
  const page = await ctx.newPage();
  page.on('dialog', d => { console.log('대화상자:', d.message().slice(0, 80)); d.accept(); });
  await page.goto('https://blog.naver.com/seoeunjin13?Redirect=Write&', { waitUntil: 'domcontentloaded', timeout: 60000 });
  await sleep(10000);
  const fr = page.frame('mainFrame');
  // 이어쓰기 창: 취소를 누르면 그 글이 지워지므로, 이어쓰기로 열어 내 시험 글인지 확인
  if (await fr.locator('.se-popup-button-cancel').count()) {
    await fr.locator('.se-popup-button-confirm').first().click(); await sleep(4000);
    const t = (await fr.locator('.se-title-text').first().innerText()).trim();
    const body = await fr.evaluate(s => [...document.querySelectorAll('.se-component')].map(p => p.innerText).join(' '), BODY);
    if (!t.includes(OWN) && !body.includes(OWN) && !['제목', ''].includes(t)) { console.log('중단: 이어쓰기 글이 다른 글 →', t.slice(0, 40)); await b.close(); return; }
    console.log('이전 시험 글 → 비우고 다시 입력');
    await fr.locator('.se-title-text').first().click(); await page.keyboard.press('Control+A'); await page.keyboard.press('Delete');
    await fr.locator(BODY).first().click(); await page.keyboard.press('Control+A'); await page.keyboard.press('Delete'); await sleep(1500);
  }
  const help = fr.locator('.se-help-panel-close-button'); if (await help.count()) { await help.first().click().catch(() => {}); await sleep(500); }
  const countBtn = fr.locator('[data-click-area="tpb*s.count"]');
  const before = (await countBtn.innerText()).trim();

  const paste = async h => {
    for (const f of page.frames()) {
      if (!f.name().startsWith('input_buffer')) continue;
      const ok = await f.evaluate(h => { const dt = new DataTransfer(); dt.setData('text/html', h); dt.setData('text/plain', h.replace(/<[^>]+>/g, ''));
        document.body.dispatchEvent(new ClipboardEvent('paste', { clipboardData: dt, bubbles: true, cancelable: true })); return true; }, h).catch(() => false);
      if (ok) { await sleep(1200); return; }
    }
    throw new Error('붙여넣기 대상 없음');
  };
  const clickByText = async (sel, text) => fr.evaluate(([sel, text]) => { const el = [...document.querySelectorAll(sel)].find(e => e.innerText.trim() === text); if (el) el.click(); return !!el; }, [sel, text]);
  const align = async which => {   // which: '왼쪽 정렬' | '가운데 정렬'
    await fr.locator('button:has-text("정렬 열기")').first().click(); await sleep(600);
    await clickByText('button', which); await sleep(600);
  };

  // 제목 (한 글자씩)
  await fr.locator('.se-title-text').first().click();
  await page.keyboard.type(spec.title, { delay: 90 }); await sleep(800);
  const gotTitle = (await fr.locator('.se-title-text').first().innerText()).trim();
  console.log('제목:', gotTitle === spec.title ? '정상' : '불일치 → ' + gotTitle);

  // 본문
  await fr.locator(BODY).first().click(); await sleep(500);
  await align('왼쪽 정렬');   // 새 글 기본 정렬이 가운데로 남아 있는 경우 대비
  let n = 0, placeOk = false;
  for (const op of spec.ops) {
    n++;
    if (op.t === 'html') await paste(op.html);
    else if (op.t === 'img') {
      const beforeImg = await fr.locator('.se-image-resource').count();
      const [chooser] = await Promise.all([page.waitForEvent('filechooser', { timeout: 15000 }),
        fr.locator('button.se-image-toolbar-button, button[data-name="image"]').first().click()]);
      await chooser.setFiles(op.files); await sleep(2500);
      if (op.files.length > 1) { const col = fr.locator('button:has-text("콜라주"), label:has-text("콜라주")'); if (await col.count()) { await col.first().click().catch(() => {}); await sleep(1500); } }
      for (let t = 0; t < 60; t++) { if ((await fr.locator('.se-image-resource').count()) >= beforeImg + op.files.length) break; await sleep(1000); }
      await sleep(800);
    } else if (op.t === 'quote') {
      await page.keyboard.press('ArrowUp'); await sleep(300);          // 인용구 뒤에 빈 문단이 남도록 한 줄 위에서 삽입
      await fr.locator('button:has-text("인용구 선택")').first().click(); await sleep(600);
      if (!await clickByText('button', '인용구' + op.style)) throw new Error('인용구 스타일 버튼 없음');
      await sleep(1200);
      await paste(op.html);
      for (let i = 0; i < 3; i++) await page.keyboard.press('ArrowDown');
      await sleep(400);
    } else if (op.t === 'place') {
      await page.keyboard.press('ArrowUp'); await sleep(300);
      try {
        await fr.locator('button.se-map-toolbar-button, button:has-text("장소")').first().click(); await sleep(2500);
        await fr.locator('input.react-autosuggest__input').first().click();
        await page.keyboard.type(op.query, { delay: 80 }); await sleep(2000);
        const sug = await fr.evaluate(q => { const el = [...document.querySelectorAll('.react-autosuggest__suggestion, li[role="option"]')].find(e => e.offsetParent && e.innerText.replace(/\s+/g, '').includes(q.replace(/\s+/g, ''))); if (!el) return null; el.click(); return el.innerText.slice(0, 40); }, op.query);
        if (!sug) await page.keyboard.press('Enter');
        let added = false;
        for (let t = 0; t < 15 && !added; t++) {
          await sleep(1000);
          added = await fr.evaluate(q => { const li = [...document.querySelectorAll('li')].find(e => e.offsetParent && !e.matches('.react-autosuggest__suggestion') && e.innerText.replace(/\s+/g, '').includes(q.replace(/\s+/g, '')));
            const btn = li && [...li.querySelectorAll('button')].find(b => b.innerText.replace(/\s+/g, '').endsWith('추가')); if (btn) btn.click(); return !!btn; }, op.query);
        }
        await sleep(1500);
        const conf = fr.locator('.se-popup-button-confirm:visible:not([disabled])'); if (await conf.count()) { await conf.first().click(); await sleep(2500); }
        placeOk = (await fr.locator('.se-component.se-placesMap').count()) > 0;
        console.log('장소 지도:', placeOk ? '추가됨' : '실패');
      } catch (e) { console.log('장소 지도 실패:', e.message.slice(0, 80)); }
      const close = fr.locator('.se-popup-close-button:visible'); if (await close.count()) { await close.first().click().catch(() => {}); await sleep(800); }
      await fr.locator(BODY).last().click(); await page.keyboard.press('End'); await sleep(300);   // 지도 아래 마지막 줄 → 해시태그
    } else if (op.t === 'nds') {
      if (!op.query) continue;
      try {
        await fr.evaluate(() => { const b = [...document.querySelectorAll('button')].find(e => /^내돈내산/.test(e.innerText.trim())); b && b.click(); }); await sleep(3000);
        await clickByText('button', '방문'); await sleep(1500);
        const found = await fr.evaluate(q => { const li = [...document.querySelectorAll('li, [class*="item"]')].find(e => e.offsetParent && e.innerText.includes(q) && /영수증/.test(e.innerText) && e.innerText.length < 150); if (!li) return null; (li.querySelector('button, label, input') || li).click(); return li.innerText.replace(/\s+/g, ' ').slice(0, 60); }, op.query);
        console.log('내돈내산 방문 인증:', found || '목록에 없음 (영수증 인증 전) → 건너뜀');
        if (found) { await sleep(1000); const ok = fr.locator('.se-popup-button-confirm:visible:not([disabled]), button:has-text("첨부"):visible, button:has-text("확인"):visible').first(); if (await ok.count()) { await ok.click(); await sleep(2500); } }
      } catch (e) { console.log('내돈내산 실패:', e.message.slice(0, 80)); }
      const close = fr.locator('.se-popup-close-button:visible, button:has-text("닫기"):visible'); if (await close.count()) { await close.first().click().catch(() => {}); await sleep(800); }
      await page.keyboard.press('Escape');
      await fr.locator(BODY).last().click(); await page.keyboard.press('End'); await sleep(300);
    }
    if (n % 15 === 0) console.log(`진행 ${n}/${spec.ops.length}`);
  }

  // 정렬: 인용구 밖 가운데 문단 → 왼쪽, 기본·말풍선 인용구 → 가운데 (밑줄 인용구는 스타일 고정)
  try {
    const outside = fr.locator('.se-component.se-text .se-text-paragraph.se-text-paragraph-align-center');
    for (let g = 0; g < 60 && await outside.count(); g++) { await outside.first().click(); await sleep(200); await align('왼쪽 정렬'); }
    const qs = fr.locator('.se-component.se-quotation:not(.se-l-quotation_underline)');
    for (let i = 0; i < await qs.count(); i++) { const ps = qs.nth(i).locator('.se-text-paragraph');
      for (let j = 0; j < await ps.count(); j++) { if (/align-center/.test(await ps.nth(j).getAttribute('class'))) continue; await ps.nth(j).click(); await sleep(200); await align('가운데 정렬'); } }
    console.log('정렬 완료');
  } catch (e) { console.log('정렬 실패:', e.message.slice(0, 80)); }

  // 검증
  const comps = await fr.evaluate(() => [...document.querySelectorAll('.se-component')].filter(c => !c.classList.contains('se-documentTitle')).map(c => c.innerText).join('\n'));
  const text = norm(comps);
  let pos = 0; const missing = [], outOfOrder = [];
  for (const l of spec.lines) { const k = norm(l); if (!k) continue; const i = text.indexOf(k, pos); if (i < 0) { (text.includes(k) ? outOfOrder : missing).push(l); } else pos = i + k.length; }
  const st = await fr.evaluate(() => ({
    img: document.querySelectorAll('.se-component .se-image-resource').length,
    quote: document.querySelectorAll('.se-component.se-quotation').length,
    quoteUnderline: document.querySelectorAll('.se-component.se-quotation.se-l-quotation_underline').length,
    place: document.querySelectorAll('.se-component.se-placesMap, .se-component[class*="map"]').length,
    bigFont: document.querySelectorAll('.se-component .se-fs19, .se-component .se-fs24, .se-component .se-fs16, .se-component .se-fs28').length,
    centerBody: document.querySelectorAll('.se-component.se-text .se-text-paragraph-align-center').length,
    u: document.querySelectorAll('.se-component u').length, i: document.querySelectorAll('.se-component i').length,
    quote19: document.querySelectorAll('.se-component.se-quotation .se-fs19').length,
    nds: document.querySelectorAll('.se-component[class*="material"], .se-component[class*="receipt"], .se-component[class*="review"]').length,
    placeBeforeTags: (() => { const cs = [...document.querySelectorAll('.se-component')]; const pi = cs.findIndex(c => c.classList.contains('se-placesMap')); const ti = cs.findIndex(c => c.innerText.includes('#')); return pi >= 0 && ti > pi; })() }));
  console.log('검증:', JSON.stringify(st), `빠진 줄 ${missing.length}, 순서 어긋남 ${outOfOrder.length} / ${spec.lines.length}`);
  if (missing.length) console.log('빠진 줄:', missing.slice(0, 5).join(' | '));
  if (outOfOrder.length) console.log('순서 어긋남:', outOfOrder.slice(0, 5).join(' | '));
  await page.screenshot({ path: S + '/shots/v3_end.png' });

  const ok = gotTitle === spec.title && !missing.length && !outOfOrder.length && st.quote === spec.n_quote && st.placeBeforeTags;
  if (!ok) {
    console.log('검증 실패 → 저장하지 않고 입력 내용 비움');
    await fr.locator('.se-title-text').first().click(); await page.keyboard.press('Control+A'); await page.keyboard.press('Delete');
    await fr.locator(BODY).first().click(); await page.keyboard.press('Control+A'); await page.keyboard.press('Delete');
    await ctx.storageState({ path: S + '/naver-state.json' }); await b.close(); return;
  }
  // 카테고리 (사용자 지시 2026-11-12): 매장 방문기 = 먹보여행, 편의점·대형 프랜차이즈 신제품 = 제품리뷰. 발행 설정 창에서 고르고 닫은 뒤 저장
  {
    const want = spec.category || '먹보여행';
    await fr.locator('[data-click-area="tpb.publish"]').click(); await sleep(2500);
    const got = await require('./category').selectCategory(fr, page, want, S);
    console.log('카테고리:', got, got === want ? '' : `⚠️ (원하는 값: ${want})`);
    await fr.locator('[data-click-area="tpb.publish"]').click().catch(() => {}); await sleep(1200);   // 발행하지 않고 창만 닫기
    if (await fr.locator('[data-click-area="tpb*i.publish"]').isVisible().catch(() => false)) { await page.keyboard.press('Escape'); await sleep(800); }
  }
  await fr.locator('[data-click-area="tpb.save"]').click(); await sleep(4000);
  console.log(`임시저장 완료: ${before} → ${(await countBtn.innerText()).trim()}`);

  // 예전 시험 글 삭제 (같은 문구가 들어간 글 중 가장 최신 1개만 남김)
  await countBtn.click(); await sleep(2500);
  const items = fr.locator('li', { has: fr.locator('button[class*="delete_button"]') }).filter({ hasText: OWN });
  const info = [];
  for (let i = 0; i < await items.count(); i++) {
    const t = (await items.nth(i).innerText()).replace(/\s+/g, ' ');
    const d = (t.match(/(\d{4})\.(\d{1,2})\.(\d{1,2})\.?\s*(\d{1,2}):(\d{2})/) || []).slice(1).map(Number);
    info.push({ i, t: t.slice(0, 60), key: d.length ? d[0] * 1e8 + d[1] * 1e6 + d[2] * 1e4 + d[3] * 100 + d[4] : 0 });
  }
  info.sort((a, b) => b.key - a.key);
  console.log('같은 제목 임시저장 글:', info.map(x => x.t).join(' / '));
  for (const x of info.slice(1).sort((a, b) => b.i - a.i)) {
    await items.nth(x.i).locator('button[class*="delete_button"]').click(); await sleep(1500);
    const conf = fr.locator('.se-popup-button-confirm, button:has-text("확인")').last(); if (await conf.count() && await conf.isVisible()) { await conf.click(); await sleep(1500); }
    console.log('예전 시험 글 삭제:', x.t);
  }
  await page.screenshot({ path: S + '/shots/v3_saved.png' });
  await ctx.storageState({ path: S + '/naver-state.json' });
  await b.close();
})().catch(e => { console.log('오류: ' + e.message.slice(0, 300)); process.exit(1); });
