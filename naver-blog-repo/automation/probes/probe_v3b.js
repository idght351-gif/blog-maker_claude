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
    if (!t.includes('쿠로카메') && !body.includes('쿠로카메') && t !== '제목' && t !== '') { console.log('중단: 다른 글 →', t.slice(0, 30)); await b.close(); return; }
  }
  const help = fr.locator('.se-help-panel-close-button'); if (await help.count()) await help.first().click().catch(() => {});
  const paste = async h => { for (const f of page.frames()) { if (!f.name().startsWith('input_buffer')) continue;
      await f.evaluate(h => { const dt = new DataTransfer(); dt.setData('text/html', h); dt.setData('text/plain', h.replace(/<[^>]+>/g, '')); document.body.dispatchEvent(new ClipboardEvent('paste', { clipboardData: dt, bubbles: true, cancelable: true })); }, h); } await sleep(1200); };
  // 1) 제목: 한 글자씩
  await fr.locator('.se-title-text').first().click(); await page.keyboard.press('Control+A'); await page.keyboard.press('Delete');
  await page.keyboard.type('[마곡 라멘 맛집] 쿠로카메 시험 제목 🍜', { delay: 90 }); await sleep(800);
  console.log('제목:', (await fr.locator('.se-title-text').first().innerText()).trim());
  // 2) 본문 붙여넣기 (밑줄/기울임)
  await fr.locator(BODY).first().click(); await page.keyboard.press('Control+A'); await page.keyboard.press('Delete'); await sleep(500);
  await paste('<p>첫 문단 <u>밑줄글</u> 과 <i>기울임글</i> 😋</p><p>둘째 문단</p>');
  console.log('본문:', await fr.evaluate(s => [...document.querySelectorAll(s)].map(p => p.innerHTML.replace(/ (id|class)="[^"]*"/g, '').slice(0, 160)).join(' || '), BODY));
  // 3) 인용구4 삽입 후 붙여넣기, 빠져나오기
  await fr.locator(BODY).last().click(); await page.keyboard.press('End'); await page.keyboard.press('Enter');
  await fr.locator('button:has-text("인용구 선택")').first().click(); await sleep(700);
  console.log('인용구4 클릭:', await fr.evaluate(() => { const b = [...document.querySelectorAll('button')].find(b => b.innerText.trim() === '인용구4'); if (!b) return '없음'; b.click(); return b.outerHTML.slice(0, 150); }));
  await sleep(1500);
  await paste('<p>📍 인용구 소제목 시험</p>');
  for (let i = 0; i < 3; i++) await page.keyboard.press('ArrowDown');
  await paste('<p>인용구 다음 본문</p>');
  console.log('구조:', (await fr.evaluate(() => [...document.querySelectorAll('.se-component')].map(c => c.className.match(/se-(text|quotation|documentTitle)\b/)?.[0] + '/' + (c.className.match(/se-l-[\w_]+/)?.[0] || '') + ':' + c.innerText.replace(/\s+/g, ' ').slice(0, 30)))).join(' || '));
  await page.screenshot({ path: S + '/shots/probe_v3b.png' });
  // 4) 발행 설정 화면 열기만 (발행 안 함)
  await fr.locator('[data-click-area="tpb.publish"]').click(); await sleep(2500);
  console.log('발행 설정 항목:', (await fr.evaluate(() => { const l = document.querySelector('[class*="layer_publish"], [class*="publish_layer"], [class*="layer_post"]'); return (l ? l.innerText : document.body.innerText.slice(-1500)).replace(/\s+/g, ' ').slice(0, 700); })));
  await page.screenshot({ path: S + '/shots/publish_layer.png' });
  await page.keyboard.press('Escape'); await sleep(800);
  // 정리 (저장 안 함)
  await fr.locator('.se-title-text').first().click(); await page.keyboard.press('Control+A'); await page.keyboard.press('Delete');
  await fr.locator(BODY).first().click(); await page.keyboard.press('Control+A'); await page.keyboard.press('Delete');
  await b.close();
})().catch(e => { console.log('오류: ' + e.message.slice(0, 200)); process.exit(1); });
