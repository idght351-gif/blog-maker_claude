// 캡차 대응 로그인: 캡차가 뜨면 화면을 저장하고, answer.txt에 사용자가 준 답이 들어올 때까지 기다렸다 입력한다.
const { chromium } = require('playwright');
const fs = require('fs');
const S = process.env.NAVER_STATE_DIR || require('path').join(__dirname, __dirname.endsWith('probes') ? '../..' : '..', '.state');
const PROFILE = S + '/naver-profile', SHOTS = S + '/shots', ANSWER = S + '/answer.txt';
fs.mkdirSync(SHOTS, { recursive: true }); try { fs.unlinkSync(ANSWER); } catch {}
const sleep = ms => new Promise(r => setTimeout(r, ms));
(async () => {
  const ctx = await chromium.launchPersistentContext(PROFILE, {
    viewport: { width: 1280, height: 900 }, locale: 'ko-KR', timezoneId: 'Asia/Seoul',
    userAgent: 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36' });
  const page = ctx.pages()[0] || await ctx.newPage();
  await page.goto('https://nid.naver.com/nidlogin.login?mode=form&url=https://www.naver.com', { waitUntil: 'domcontentloaded' });
  await sleep(1500);
  if (page.url().includes('nidlogin')) {
    await page.click('#id'); await page.keyboard.type(process.env.NAVER_ID, { delay: 120 });
    await sleep(700); await page.click('#pw'); await page.keyboard.type(process.env.NAVER_PW, { delay: 130 });
    await sleep(800); await page.keyboard.press('Enter');
  }
  for (let i = 0; i < 80; i++) {                       // 최대 약 7분
    await sleep(5000);
    const url = page.url();
    if (!url.includes('nid.naver.com')) { await page.screenshot({ path: SHOTS + '/done.png' }); console.log('로그인 성공'); break; }
    const cap = await page.$('input[placeholder*="정답"], #captcha, input[name="captcha"]');
    if (cap) {
      await page.screenshot({ path: SHOTS + '/captcha.png' });
      console.log('CAPTCHA 대기');
      while (!fs.existsSync(ANSWER)) await sleep(1000);
      const ans = fs.readFileSync(ANSWER, 'utf8').trim(); fs.unlinkSync(ANSWER);
      if (ans === 'REFRESH') { await page.click('button[class*="refresh"], button:has(svg)').catch(()=>{}); continue; }
      await cap.click(); await cap.fill(''); await page.keyboard.type(ans, { delay: 150 });
      // 캡차 단계에서 비밀번호를 다시 요구하면 채움
      const pw = await page.$('#pw'); if (pw && !(await pw.inputValue())) { await pw.click(); await page.keyboard.type(process.env.NAVER_PW, { delay: 130 }); }
      await sleep(500); await page.keyboard.press('Enter'); console.log('캡차 답 입력');
      continue;
    }
    await page.screenshot({ path: SHOTS + `/step_${String(i).padStart(2,'0')}.png` });
    console.log(i, '대기 중 (2단계 인증/기기 확인 가능)');
  }
  await ctx.close();
})().catch(e => { console.error('오류:', e.message); process.exit(1); });
