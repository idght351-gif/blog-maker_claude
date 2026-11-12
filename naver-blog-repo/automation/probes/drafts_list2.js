const { chromium } = require('playwright');
const S = process.env.NAVER_STATE_DIR || require('path').join(__dirname, __dirname.endsWith('probes') ? '../..' : '..', '.state');
(async () => {
  const b = await chromium.launch(); const ctx = await b.newContext({ storageState: S + '/naver-state.json', locale: 'ko-KR', viewport: { width: 1400, height: 1000 } });
  const page = await ctx.newPage(); page.on('dialog', d => d.dismiss());
  await page.goto('https://blog.naver.com/seoeunjin13?Redirect=Write&', { waitUntil: 'domcontentloaded', timeout: 60000 });
  await page.waitForTimeout(10000);
  const fr = page.frame('mainFrame');
  const cancel = fr.locator('.se-popup-button-cancel'); if (await cancel.count()) { await cancel.first().click(); await page.waitForTimeout(1000); }
  const help = fr.locator('.se-help-panel-close-button'); if (await help.count()) await help.first().click().catch(() => {});
  const btns = await fr.evaluate(() => [...document.querySelectorAll('[data-click-area^="tpb"]')].map(e => e.tagName + ' ' + e.getAttribute('data-click-area') + ' | ' + e.innerText.replace(/\s+/g, ' ')));
  console.log(btns.join('\n'));
  const cntBtn = fr.locator('[data-click-area="tpb*s.count"]').first();
  if (await cntBtn.count()) { await cntBtn.click(); await page.waitForTimeout(2500); }
  await page.screenshot({ path: S + '/shots/drafts_list.png' });
  const html = await fr.evaluate(() => { const l = [...document.querySelectorAll('li')].filter(li => /\d{4}\.\s?\d{1,2}\.\s?\d{1,2}|분 전|시간 전/.test(li.innerText)); return l.slice(0, 8).map(li => li.innerText.replace(/\s+/g, ' ').slice(0, 120) + '  ||  ' + [...li.querySelectorAll('button')].map(b => b.className + ':' + (b.innerText || b.getAttribute('aria-label') || '')).join(', ')); });
  console.log(html.join('\n'));
  await b.close();
})();
