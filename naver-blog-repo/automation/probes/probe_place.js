const { chromium } = require('/usr/local/lib/node_modules_global/playwright');
const S = process.env.NAVER_STATE_DIR || require('path').join(__dirname, '../..', '.state');
const Q = process.argv[2];
(async () => {
  const b = await chromium.launch(); const ctx = await b.newContext({ storageState: S + '/naver-state.json', locale: 'ko-KR', viewport: { width: 1400, height: 1000 } });
  const page = await ctx.newPage(); page.on('dialog', d => d.accept());
  await page.goto('https://blog.naver.com/seoeunjin13?Redirect=Write&', { waitUntil: 'domcontentloaded' }); await page.waitForTimeout(10000);
  const fr = page.frame('mainFrame');
  const pop = await fr.locator('.se-popup-button-cancel').count();
  if (pop) { await fr.locator('.se-popup-button-confirm').first().click(); await page.waitForTimeout(4000); }
  console.log('title:', (await fr.locator('.se-title-text').first().innerText()).trim().slice(0, 30));
  await fr.locator('button.se-map-toolbar-button, button:has-text("장소")').first().click(); await page.waitForTimeout(2500);
  await fr.locator('input.react-autosuggest__input').first().click();
  await page.keyboard.type(Q, { delay: 80 }); await page.waitForTimeout(2500);
  console.log('SUG:', JSON.stringify(await fr.evaluate(() => [...document.querySelectorAll('.react-autosuggest__suggestion, li[role="option"]')].filter(e => e.offsetParent).map(e => e.innerText.replace(/\s+/g, ' ').slice(0, 60)))));
  await page.keyboard.press("Enter"); await page.waitForTimeout(4000); console.log("RES2:", JSON.stringify(await fr.evaluate(() => [...document.querySelectorAll("li")].filter(e => e.offsetParent && /추가$/.test(e.innerText.trim())).map(e => e.innerText.replace(/\s+/g, " ").slice(0, 80)).slice(0, 8))));
  console.log('RES:', JSON.stringify(await fr.evaluate(() => [...document.querySelectorAll('li')].filter(e => e.offsetParent && /추가/.test(e.innerText)).map(e => e.innerText.replace(/\s+/g, ' ').slice(0, 80)).slice(0, 8))));
  await page.screenshot({ path: S + '/shots/place_probe.png' });
  await b.close();
})();
