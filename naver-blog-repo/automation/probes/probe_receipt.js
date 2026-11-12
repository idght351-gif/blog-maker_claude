// 영수증 리뷰 화면 찾기 (모바일 화면 흉내). 쓰기는 하지 않고 버튼·주소만 기록한다.
const { chromium, devices } = require('playwright');
const S = require('path').join(__dirname, '../..', '.state');
const Q = process.argv[2] || '쿠로카메 마곡';
(async () => {
  const b = await chromium.launch();
  const ctx = await b.newContext({ ...devices['iPhone 13'], storageState: S + '/naver-state.json', locale: 'ko-KR' });
  const page = await ctx.newPage();
  await page.goto('https://m.search.naver.com/search.naver?query=' + encodeURIComponent(Q), { waitUntil: 'domcontentloaded' });
  await page.waitForTimeout(3000);
  const links = await page.$$eval('a[href*="place.naver.com"]', as => [...new Set(as.map(a => a.href))].slice(0, 8));
  console.log('PLACE LINKS\n ' + links.join('\n '));
  const id = (links.join(' ').match(/place\.naver\.com\/(?:restaurant|place)\/(\d+)/) || [])[1];
  console.log('ID', id);
  if (!id) return b.close();
  await page.goto(`https://m.place.naver.com/restaurant/${id}/review/visitor`, { waitUntil: 'domcontentloaded' });
  await page.waitForTimeout(4000);
  await page.screenshot({ path: S + '/shots/place_review.png' });
  const btns = await page.$$eval('a, button', es => es.map(e => (e.innerText || '').trim().replace(/\s+/g, ' ') + ' | ' + (e.getAttribute('href') || '')).filter(t => /리뷰|영수증|인증|쓰기/.test(t)).slice(0, 30));
  console.log('BUTTONS\n ' + btns.join('\n '));
  await b.close();
})().catch(e => { console.log('오류', e.message); process.exit(1); });
