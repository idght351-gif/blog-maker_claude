const { chromium } = require('/usr/local/lib/node_modules_global/playwright');
const S = process.env.NAVER_STATE_DIR || require('path').join(__dirname, '../..', '.state');
(async () => {
  const b = await chromium.launch(); const ctx = await b.newContext({ storageState: S + '/naver-state.json', locale: 'ko-KR', viewport: { width: 1400, height: 1000 } });
  const page = await ctx.newPage(); page.on('dialog', d => d.accept());
  await page.goto('https://blog.naver.com/seoeunjin13?Redirect=Write&', { waitUntil: 'domcontentloaded' }); await page.waitForTimeout(10000);
  const fr = page.frame('mainFrame');
  if (await fr.locator('.se-popup-button-cancel').count()) { await fr.locator('.se-popup-button-confirm').first().click(); await page.waitForTimeout(5000); }
  console.log('열린 글:', (await fr.locator('.se-title-text').first().innerText()).trim().slice(0, 40));
  await fr.locator('[data-click-area="tpb*s.count"]').evaluate(e => e.click()); await page.waitForTimeout(3000);
  console.log(JSON.stringify((await fr.locator('li', { has: fr.locator('button[class*="article_button"]') }).allInnerTexts()).map(t => t.replace(/\s+/g, ' ').slice(0, 70)), null, 1));
  await b.close();
})();
