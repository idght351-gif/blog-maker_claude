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
    if (!t.includes('쿠로카메') && !body.includes('쿠로카메') && !['제목', ''].includes(t)) { console.log('중단: 다른 글 →', t.slice(0, 30)); await b.close(); return; }
    await fr.locator('.se-title-text').first().click(); await page.keyboard.press('Control+A'); await page.keyboard.press('Delete');
    await fr.locator(BODY).first().click(); await page.keyboard.press('Control+A'); await page.keyboard.press('Delete');
  }
  const help = fr.locator('.se-help-panel-close-button'); if (await help.count()) await help.first().click().catch(() => {});
  await fr.locator(BODY).first().click();
  await fr.locator('button.se-map-toolbar-button, button:has-text("장소")').first().click(); await sleep(2500);
  const inp = fr.locator('input.react-autosuggest__input').first();
  await inp.click(); await page.keyboard.type('쿠로카메 라멘 본점', { delay: 80 }); await sleep(1500); await page.keyboard.press('Enter'); await sleep(3500);
  await page.screenshot({ path: S + '/shots/place_search.png' });
  console.log('결과 버튼:', (await fr.evaluate(() => [...document.querySelectorAll('.se-popup button, [class*="place"] button')].filter(b => b.offsetParent).map(b => (b.innerText || b.getAttribute('aria-label') || '').trim() + ':' + b.className.slice(0, 40)).slice(0, 15))).join(' | '));
  console.log('결과 항목:', (await fr.evaluate(() => [...document.querySelectorAll('.se-popup li, [class*="place_list"] li, [class*="list"] li')].filter(l => l.offsetParent).map(l => l.innerText.replace(/\s+/g, ' ').slice(0, 60)).slice(0, 5))).join(' | '));
  await page.keyboard.press('Escape');
  await fr.locator(BODY).first().click(); await page.keyboard.press('Control+A'); await page.keyboard.press('Delete');
  await b.close();
})().catch(e => { console.log('오류: ' + e.message.slice(0, 200)); process.exit(1); });
