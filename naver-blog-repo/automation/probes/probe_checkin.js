// MY플레이스 리뷰 쓰기(/my/checkin) 화면 구조 확인. 클릭 순서를 인자로 받아 따라가며 매 단계 스크린샷.
// 사용법: node probe_checkin.js ["버튼글자1" "버튼글자2" ...]   (등록·완료 버튼은 누르지 않음)
const { chromium, devices } = require('playwright');
const S = require('path').join(__dirname, '../..', '.state');
(async () => {
  const b = await chromium.launch();
  const ctx = await b.newContext({ ...devices['iPhone 13'], storageState: S + '/naver-state.json', locale: 'ko-KR' });
  const page = await ctx.newPage();
  await page.goto('https://m.place.naver.com/my/checkin', { waitUntil: 'domcontentloaded' });
  await page.waitForTimeout(4000);
  const dump = async tag => {
    await page.screenshot({ path: `${S}/shots/checkin_${tag}.png` });
    const items = await page.$$eval('a, button, input, label, [role=button]', es => es.filter(e => e.offsetParent || e.type === 'file').map(e => `${e.tagName}${e.type ? '[' + e.type + ']' : ''} ${(e.innerText || e.getAttribute('aria-label') || e.getAttribute('accept') || '').trim().replace(/\s+/g, ' ').slice(0, 60)}`).filter(t => t.trim().length > 3).slice(0, 40));
    console.log(`== ${tag} ${page.url()}\n ` + items.join('\n '));
  };
  await dump('0');
  let i = 1;
  for (const t of process.argv.slice(2)) {
    if (/등록|완료|올리기/.test(t)) { console.log('등록 버튼은 누르지 않음:', t); break; }
    await page.getByText(t, { exact: false }).first().click();
    await page.waitForTimeout(3000);
    await dump(String(i++));
  }
  await b.close();
})().catch(e => { console.log('오류', e.message); process.exit(1); });
