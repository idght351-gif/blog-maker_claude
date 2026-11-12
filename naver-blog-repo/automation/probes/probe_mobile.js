const { chromium, devices } = require('playwright');
const S = process.env.NAVER_STATE_DIR || require('path').join(__dirname, __dirname.endsWith('probes') ? '../..' : '..', '.state');
const sleep = ms => new Promise(r => setTimeout(r, ms));
(async () => {
  const b = await chromium.launch();
  const ctx = await b.newContext({ ...devices['iPhone 13'], storageState: S + '/naver-state.json', locale: 'ko-KR' });
  const page = await ctx.newPage(); page.on('dialog', d => { console.log('대화상자:', d.message().slice(0, 60)); d.dismiss(); });
  for (const u of ['https://m.blog.naver.com/seoeunjin13?Redirect=Write', 'https://m.blog.naver.com/PostWriteForm.naver?blogId=seoeunjin13']) {
    await page.goto(u, { waitUntil: 'domcontentloaded', timeout: 60000 }).catch(e => console.log('goto', e.message.slice(0, 60)));
    await sleep(9000);
    console.log('URL', page.url());
    const txt = [];
    for (const f of page.frames()) txt.push(await f.evaluate(() => document.body ? document.body.innerText.replace(/\s+/g, ' ').slice(0, 300) : '').catch(() => ''));
    console.log('화면:', txt.filter(Boolean).join(' / ').slice(0, 500));
    const hasLoc = (await Promise.all(page.frames().map(f => f.locator('text=위치 추가').count().catch(() => 0)))).some(n => n > 0);
    console.log('위치 추가 버튼:', hasLoc ? '있음' : '없음');
    await page.screenshot({ path: S + '/shots/mobile_write.png' });
    if (hasLoc) break;
  }
  await b.close();
})();
