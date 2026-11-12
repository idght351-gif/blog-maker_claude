// 네이버 로그인: 사람처럼 한 글자씩 입력하고, 로그인 상태(쿠키)를 프로필 폴더에 저장한다.
// 2단계 인증·새 기기 확인이 뜨면 최대 3분 동안 승인을 기다린다. 진행 화면은 shots/에 저장.
const { chromium } = require('playwright');
const fs = require('fs');
const PROFILE = process.env.NAVER_PROFILE || require('path').join(__dirname, '..', '.state', 'naver-profile');
const SHOTS = require('path').join(__dirname, '..', '.state', 'shots');
fs.mkdirSync(SHOTS, { recursive: true });
(async () => {
  const ctx = await chromium.launchPersistentContext(PROFILE, {
    viewport: { width: 1280, height: 900 }, locale: 'ko-KR', timezoneId: 'Asia/Seoul',
    userAgent: 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36',
  });
  const page = ctx.pages()[0] || await ctx.newPage();
  await page.goto('https://nid.naver.com/nidlogin.login?mode=form&url=https://www.naver.com', { waitUntil: 'domcontentloaded' });
  await page.waitForTimeout(1500);
  if (!page.url().includes('nidlogin')) { console.log('이미 로그인됨'); await ctx.close(); return; }
  await page.click('#id'); await page.keyboard.type(process.env.NAVER_ID, { delay: 120 });
  await page.waitForTimeout(700);
  await page.click('#pw'); await page.keyboard.type(process.env.NAVER_PW, { delay: 130 });
  await page.waitForTimeout(800);
  const keep = await page.$('#keep'); if (keep) await keep.check().catch(() => {});
  await page.keyboard.press('Enter');
  for (let i = 0; i < 36; i++) {            // 최대 3분
    await page.waitForTimeout(5000);
    const url = page.url();
    await page.screenshot({ path: `${SHOTS}/login_${String(i).padStart(2, '0')}.png` });
    console.log(i, url.replace(/([?&](token|key|session)[^&]*)/gi, ''));
    if (!url.includes('nid.naver.com')) { console.log('로그인 성공'); break; }
  }
  await ctx.close();
})().catch(e => { console.error('오류:', e.message); process.exit(1); });
