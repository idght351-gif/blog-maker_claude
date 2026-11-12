// 리뷰 쓰기 화면의 별점 구조 확인 + 여러 방식으로 눌러 보기 (등록은 하지 않음)
const { chromium, devices } = require('playwright');
const S = require('path').join(__dirname, '../..', '.state');
(async () => {
  const b = await chromium.launch();
  const ctx = await b.newContext({ ...devices['iPhone 13'], storageState: S + '/naver-state.json', locale: 'ko-KR' });
  const page = await ctx.newPage();
  await page.goto(process.argv[2], { waitUntil: 'domcontentloaded' });
  await page.waitForTimeout(4000);
  const web = page.locator('button').filter({ hasText: '모바일 웹으로 볼게요' });
  if (await web.count()) await web.first().click().catch(() => {});
  const html = await page.evaluate(() => { const b = [...document.querySelectorAll('button')].find(e => e.textContent.trim() === '5점'); return b ? b.parentElement.outerHTML.slice(0, 1500) : 'none'; });
  console.log(html);
  const st = page.locator('button').filter({ hasText: /^\s*5점\s*$/ }).first();
  const box1 = await st.boundingBox(); console.log('box', JSON.stringify(box1));
  await st.evaluate(e => e.scrollIntoView({ block: 'center' })); await page.waitForTimeout(800);
  const box = await st.boundingBox(); console.log('box after center', JSON.stringify(box));
  await page.touchscreen.tap(box.x + box.width / 2, box.y + box.height / 2); await page.waitForTimeout(1000);
  const pressed = await page.evaluate(() => [...document.querySelectorAll('button')].filter(e => /^[1-5]점$/.test(e.textContent.trim())).map(e => e.textContent.trim() + ':' + e.className + ':' + e.getAttribute('aria-pressed')).join(' | '));
  console.log('after tap', pressed);
  await page.screenshot({ path: S + '/shots/star.png' });
  await b.close();
})().catch(e => { console.log('오류', e.message); process.exit(1); });
