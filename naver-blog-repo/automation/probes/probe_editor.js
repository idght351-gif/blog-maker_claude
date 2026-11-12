const { chromium } = require('playwright');
const S = process.env.NAVER_STATE_DIR || require('path').join(__dirname, __dirname.endsWith('probes') ? '../..' : '..', '.state');
(async () => {
  const b = await chromium.launch(); const ctx = await b.newContext({ storageState: S + '/naver-state.json', locale: 'ko-KR', viewport: { width: 1400, height: 1000 },
    userAgent: 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36' });
  const page = await ctx.newPage();
  await page.goto('https://blog.naver.com/seoeunjin13?Redirect=Write&', { waitUntil: 'domcontentloaded', timeout: 60000 });
  await page.waitForTimeout(10000);
  console.log('PAGE', page.url());
  for (const f of page.frames()) console.log(' frame', f.name(), f.url().slice(0, 120));
  const fr = page.frame('mainFrame') || page.mainFrame();
  const info = await fr.evaluate(() => {
    const pick = sel => [...document.querySelectorAll(sel)].slice(0, 6).map(e => (e.className + ' | ' + (e.innerText || e.getAttribute('aria-label') || '')).slice(0, 90));
    return { buttons: [...document.querySelectorAll('button')].map(b => (b.innerText || b.getAttribute('aria-label') || b.className).trim()).filter(Boolean).slice(0, 60),
             title: pick('.se-title-text, .se-documentTitle'), popups: pick('[class*="popup"], [class*="layer"]') };
  });
  console.log(JSON.stringify(info, null, 1).slice(0, 2500));
  await page.screenshot({ path: S + '/shots/editor.png' });
  await b.close();
})();
