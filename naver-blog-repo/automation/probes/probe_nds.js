// 내돈내산 버튼 창 확인 (아무것도 추가하지 않음, 저장 안 함)
const { chromium } = require('playwright');
const S = process.env.NAVER_STATE_DIR || require('path').join(__dirname, __dirname.endsWith('probes') ? '../..' : '..', '.state');
const sleep = ms => new Promise(r => setTimeout(r, ms));
(async () => {
  const b = await chromium.launch(); const ctx = await b.newContext({ storageState: S + '/naver-state.json', locale: 'ko-KR', viewport: { width: 1400, height: 1000 } });
  const page = await ctx.newPage(); page.on('dialog', d => d.dismiss());
  await page.goto('https://blog.naver.com/seoeunjin13?Redirect=Write&', { waitUntil: 'domcontentloaded', timeout: 60000 }); await sleep(10000);
  const fr = page.frame('mainFrame');
  if (await fr.locator('.se-popup-button-cancel').count()) { console.log('이어쓰기 창 있음 → 중단'); await b.close(); return; }
  const help = fr.locator('.se-help-panel-close-button'); if (await help.count()) await help.first().click().catch(() => {});
  await fr.evaluate(() => { const b = [...document.querySelectorAll('button')].find(e => /^내돈내산/.test(e.innerText.trim())); b && b.click(); });
  await sleep(4000);
  await page.screenshot({ path: S + '/shots/nds.png' });
  for (const f of page.frames()) {
    const t = await f.evaluate(() => document.body ? document.body.innerText.replace(/\s+/g, ' ') : '').catch(() => '');
    const i = t.indexOf('내돈내산'); if (i >= 0 && f !== page.mainFrame()) console.log('[' + (f.name() || f.url().slice(0, 50)) + ']', t.slice(Math.max(0, i - 50), i + 600));
  }
  await page.keyboard.press('Escape'); await b.close();
})();
