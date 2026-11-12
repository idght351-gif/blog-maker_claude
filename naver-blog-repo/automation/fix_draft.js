// 저장된 시험 글을 열어 정렬과 장소 지도만 보정하고 다시 저장한다.
// 사용법: node fix_draft.js <제목 문구> <장소 검색어> <장소 주소 일부> <해시태그 첫 단어>
const { chromium } = require('playwright');
const S = process.env.NAVER_STATE_DIR || require('path').join(__dirname, __dirname.endsWith('probes') ? '../..' : '..', '.state');
const [OWN, QUERY, ADDR, TAG] = process.argv.slice(2);
const sleep = ms => new Promise(r => setTimeout(r, ms));
const BODY = '.se-component.se-text .se-text-paragraph';
(async () => {
  const b = await chromium.launch();
  const ctx = await b.newContext({ storageState: S + '/naver-state.json', locale: 'ko-KR', viewport: { width: 1400, height: 1000 } });
  const page = await ctx.newPage(); page.on('dialog', d => { console.log('대화상자:', d.message().slice(0, 60)); d.accept(); });
  await page.goto('https://blog.naver.com/seoeunjin13?Redirect=Write&', { waitUntil: 'domcontentloaded', timeout: 60000 }); await sleep(10000);
  const fr = page.frame('mainFrame');
  if (await fr.locator('.se-popup-button-cancel').count()) { await fr.locator('.se-popup-button-confirm').first().click(); await sleep(4000); }
  else {   // 임시저장 목록에서 열기
    await fr.locator('[data-click-area="tpb*s.count"]').click(); await sleep(2500);
    await fr.locator('li', { has: fr.locator('button[class*="article_button"]') }).filter({ hasText: OWN }).first().locator('button[class*="article_button"]').click(); await sleep(6000);
  }
  const help = fr.locator('.se-help-panel-close-button'); if (await help.count()) await help.first().click().catch(() => {});
  const title = (await fr.locator('.se-title-text').first().innerText()).trim();
  if (!title.includes(OWN)) { console.log('중단: 열린 글이 시험 글이 아님 →', title.slice(0, 40)); await b.close(); return; }
  console.log('열린 글:', title.slice(0, 40));
  const clickByText = async text => fr.evaluate(t => { const el = [...document.querySelectorAll('button')].find(e => e.innerText.trim() === t); if (el) el.click(); return !!el; }, text);
  const align = async which => {
    const opened = await fr.evaluate(() => { const b = [...document.querySelectorAll('button')].find(e => /정렬 열기/.test(e.innerText)); if (b) b.click(); return !!b; });
    await sleep(600); const ok = await clickByText(which); await sleep(600); return opened && ok;
  };
  const alignStats = () => fr.evaluate(() => { const c = {}; document.querySelectorAll('.se-component .se-text-paragraph').forEach(p => { const a = (p.className.match(/align-(\w+)/) || [, '기본'])[1]; c[a] = (c[a] || 0) + 1; }); return c; });
  console.log('정렬 전:', JSON.stringify(await alignStats()));

  // 1) 장소 지도: 해시태그 문단 바로 위 빈 줄에 삽입
  if (!(await fr.locator('.se-component.se-placesMap').count())) {
    const tagP = fr.locator(BODY).filter({ hasText: TAG }).last();
    await tagP.click(); await page.keyboard.press('Home'); await page.keyboard.press('ArrowUp'); await sleep(400);
    await fr.locator('button.se-map-toolbar-button, button:has-text("장소")').first().click(); await sleep(2500);
    await fr.locator('input.react-autosuggest__input').first().click();
    await page.keyboard.type(QUERY, { delay: 80 }); await sleep(2000);
    // ① 추천어 목록에서 가게 선택
    const sug = await fr.evaluate(q => { const el = [...document.querySelectorAll('.react-autosuggest__suggestion, li[role="option"]')].find(e => e.offsetParent && e.innerText.replace(/\s+/g, '').includes(q.replace(/\s+/g, ''))); if (!el) return null; el.click(); return el.innerText.replace(/\s+/g, ' ').slice(0, 60); }, QUERY);
    console.log('추천어 선택:', sug);
    if (!sug) { await page.keyboard.press('Enter'); }
    // ② 왼쪽 결과 목록에서 주소가 맞는 항목 선택
    let picked = null;
    for (let t = 0; t < 15 && !picked; t++) {
      await sleep(1000);
      picked = await fr.evaluate(addr => {
        const cands = [...document.querySelectorAll('li')].filter(e => e.offsetParent && !e.matches('.react-autosuggest__suggestion') && e.innerText.replace(/\s+/g, '').includes(addr.replace(/\s+/g, '')));
        if (!cands.length) return null; const el = cands[0]; (el.querySelector('button, a') || el).click(); return el.innerText.replace(/\s+/g, ' ').slice(0, 60);
      }, ADDR);
    }
    console.log('장소 선택:', picked); await sleep(1500);
    const added = await fr.evaluate(addr => {
      const li = [...document.querySelectorAll('li')].find(e => e.offsetParent && e.innerText.replace(/\s+/g, '').includes(addr.replace(/\s+/g, '')) && !e.matches('.react-autosuggest__suggestion'));
      const btn = li && [...li.querySelectorAll('button')].find(b => b.innerText.replace(/\s+/g, '').endsWith('추가'));
      if (btn) btn.click(); return !!btn; }, ADDR);
    console.log('추가 버튼:', added); await sleep(1500);
    await page.screenshot({ path: S + '/shots/fix_place.png' });
    const conf = fr.locator('.se-popup-button-confirm:visible:not([disabled])'); if (await conf.count()) { await conf.first().click(); await sleep(2500); }
    const close = fr.locator('.se-popup-close-button:visible'); if (await close.count()) await close.first().click().catch(() => {});
  }
  const placeN = await fr.locator('.se-component.se-placesMap').count();
  console.log('장소 지도:', placeN ? '있음' : '없음');

  // 2) 정렬: 인용구 밖 가운데 문단 → 하나씩 왼쪽, 인용구 → 하나씩 가운데
  const outside = fr.locator('.se-component.se-text .se-text-paragraph.se-text-paragraph-align-center');
  let fixed = 0;
  for (let guard = 0; guard < 80 && await outside.count(); guard++) {
    await outside.first().click(); await sleep(250);
    if (!await align('왼쪽 정렬')) break; fixed++;
  }
  console.log('본문 가운데 → 왼쪽:', fixed, '문단');
  const nq = await fr.locator('.se-component.se-quotation').count();
  let qc = 0;
  for (let i = 0; i < nq; i++) {
    const q = fr.locator('.se-component.se-quotation').nth(i);
    const ps = q.locator('.se-text-paragraph');
    for (let j = 0; j < await ps.count(); j++) {
      if (/align-center/.test(await ps.nth(j).getAttribute('class'))) continue;
      await ps.nth(j).click(); await sleep(250); await align('가운데 정렬');
    }
    const allC = await q.evaluate(e => [...e.querySelectorAll('.se-text-paragraph')].every(p => /align-center/.test(p.className)));
    if (allC) qc++;
  }
  const st = await alignStats();
  console.log('정렬 후:', JSON.stringify(st), '/ 가운데 정렬된 인용구', qc, '/', nq, '/ 본문 가운데 남음', await outside.count());
  await page.screenshot({ path: S + '/shots/fix_end.png' });

  if (placeN && qc === nq && !(await outside.count())) {
    await fr.locator('[data-click-area="tpb.save"]').click(); await sleep(4000);
    console.log('저장 완료 (임시저장 글 수', (await fr.locator('[data-click-area="tpb*s.count"]').innerText()).trim() + ')');
  } else console.log('보정 결과가 기준에 못 미쳐 저장하지 않음');
  await ctx.storageState({ path: S + '/naver-state.json' });
  await b.close();
})().catch(e => { console.log('오류: ' + e.message.slice(0, 300)); process.exit(1); });
