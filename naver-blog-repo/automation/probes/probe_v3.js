// v3 기능 시험 (저장 안 함): 제목 붙여넣기, 밑줄·기울임, 인용구(밑줄) 소제목, 위치 추가, 장소 버튼
const { chromium } = require('playwright');
const S = process.env.NAVER_STATE_DIR || require('path').join(__dirname, __dirname.endsWith('probes') ? '../..' : '..', '.state');
const sleep = ms => new Promise(r => setTimeout(r, ms));
const BODY = '.se-component.se-text .se-text-paragraph';
(async () => {
  const b = await chromium.launch(); const ctx = await b.newContext({ storageState: S + '/naver-state.json', locale: 'ko-KR', viewport: { width: 1400, height: 1000 } });
  const page = await ctx.newPage(); page.on('dialog', d => d.dismiss());
  await page.goto('https://blog.naver.com/seoeunjin13?Redirect=Write&', { waitUntil: 'domcontentloaded', timeout: 60000 }); await sleep(10000);
  const fr = page.frame('mainFrame');
  if (await fr.locator('.se-popup-button-cancel').count()) {
    await fr.locator('.se-popup-button-confirm').first().click(); await sleep(4000);
    const t = (await fr.locator('.se-title-text').first().innerText()).trim();
    const body = await fr.evaluate(s => [...document.querySelectorAll(s)].map(p => p.innerText).join(' '), BODY);
    if (!t.includes('쿠로카메') && !body.includes('쿠로카메')) { console.log('중단: 다른 글 이어쓰기 →', t.slice(0, 30)); await b.close(); return; }
    console.log('이전 시험 글 → 비움');
    await fr.locator('.se-title-text').first().click(); await page.keyboard.press('Control+A'); await page.keyboard.press('Delete');
    await fr.locator(BODY).first().click(); await page.keyboard.press('Control+A'); await page.keyboard.press('Delete'); await sleep(1000);
  }
  const help = fr.locator('.se-help-panel-close-button'); if (await help.count()) await help.first().click().catch(() => {});
  const paste = async h => { for (const f of page.frames()) { if (!f.name().startsWith('input_buffer')) continue;
      await f.evaluate(h => { const dt = new DataTransfer(); dt.setData('text/html', h); dt.setData('text/plain', h.replace(/<[^>]+>/g, '')); document.body.dispatchEvent(new ClipboardEvent('paste', { clipboardData: dt, bubbles: true, cancelable: true })); }, h); } await sleep(1200); };
  // 1) 제목 붙여넣기
  await fr.locator('.se-title-text').first().click(); await paste('[마곡 라멘 맛집] 쿠로카메 시험 제목 🍜');
  console.log('제목:', (await fr.locator('.se-title-text').first().innerText()).trim());
  // 2) 본문: 밑줄/기울임/blockquote 붙여넣기
  await fr.locator(BODY).first().click();
  await paste('<p>밑줄 <u>밑줄글</u> 기울임 <i>기울임글</i></p><blockquote>인용구 붙여넣기 시험</blockquote><p>다음 문단</p>');
  const comps = await fr.evaluate(() => [...document.querySelectorAll('.se-component')].map(c => c.className.replace(/\s+/g, ' ').slice(0, 80)));
  console.log('컴포넌트:', comps.join(' || '));
  console.log('u/i:', await fr.evaluate(() => [document.querySelectorAll('.se-component.se-text u').length, document.querySelectorAll('.se-component.se-text i').length].join('/')));
  // 3) 인용구 드롭다운 옵션
  const qd = fr.locator('button:has-text("인용구 선택")').first();
  if (await qd.count()) { await qd.click(); await sleep(800);
    console.log('인용구 옵션:', (await fr.evaluate(() => [...document.querySelectorAll('button')].filter(b => /인용구\d/.test(b.innerText)).map(b => b.innerText + ':' + (b.getAttribute('data-value') || b.className).slice(0, 50)))).join(' | '));
    await page.keyboard.press('Escape'); }
  // 4) 제목 영역 위치 추가 버튼 찾기
  console.log('제목 근처 버튼:', (await fr.evaluate(() => [...document.querySelectorAll('.se-documentTitle button, [class*="location"] button, button[class*="location"], [class*="place"] button')].map(b => (b.innerText || b.getAttribute('aria-label') || '') + ':' + b.className.slice(0, 50)))).join(' | ') || '없음');
  // 5) 장소 버튼 → 대화상자
  await fr.locator(BODY).last().click();
  await fr.locator('button:has-text("장소")').first().click(); await sleep(2500);
  await page.screenshot({ path: S + '/shots/place_dialog.png' });
  console.log('장소 입력창:', (await fr.evaluate(() => [...document.querySelectorAll('input')].filter(i => i.offsetParent).map(i => (i.placeholder || i.name) + ':' + i.className.slice(0, 40)))).join(' | '));
  await page.keyboard.press('Escape'); await sleep(500);
  await page.screenshot({ path: S + '/shots/probe_v3.png' });
  // 정리: 제목·본문 비움 (저장 안 함)
  await fr.locator('.se-title-text').first().click(); await page.keyboard.press('Control+A'); await page.keyboard.press('Delete');
  await fr.locator(BODY).first().click(); await page.keyboard.press('Control+A'); await page.keyboard.press('Delete');
  await b.close();
})().catch(e => { console.log('오류: ' + e.message.slice(0, 200)); process.exit(1); });
