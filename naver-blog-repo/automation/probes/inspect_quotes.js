const { chromium } = require('playwright');
const S = process.env.NAVER_STATE_DIR || require('path').join(__dirname, __dirname.endsWith('probes') ? '../..' : '..', '.state');
const sleep = ms => new Promise(r => setTimeout(r, ms));
(async () => {
  const b = await chromium.launch(); const ctx = await b.newContext({ storageState: S + '/naver-state.json', locale: 'ko-KR', viewport: { width: 1400, height: 1000 } });
  const page = await ctx.newPage(); page.on('dialog', d => d.accept());
  await page.goto('https://blog.naver.com/seoeunjin13?Redirect=Write&', { waitUntil: 'domcontentloaded', timeout: 60000 }); await sleep(10000);
  const fr = page.frame('mainFrame');
  if (await fr.locator('.se-popup-button-cancel').count()) { await fr.locator('.se-popup-button-confirm').first().click(); await sleep(4000); }
  console.log('제목:', (await fr.locator('.se-title-text').first().innerText()).trim().slice(0, 30));
  const q = await fr.evaluate(() => [...document.querySelectorAll('.se-component.se-quotation')].map((c, i) => i + ' ' + (c.className.match(/se-l-[\w_]+/) || [''])[0] + ' :: ' +
    [...c.querySelectorAll('.se-text-paragraph')].map(p => (p.className.match(/align-(\w+)/) || [, '기본'])[1] + '[' + p.innerText.replace(/\s+/g, ' ').slice(0, 20) + ']').join(' ')));
  console.log(q.join('\n'));
  console.log('장소:', await fr.locator('.se-component.se-placesMap').count());
  await b.close();
})();
