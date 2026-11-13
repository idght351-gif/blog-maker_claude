// QR코드 로그인: QR 화면을 캡처해 두고, 사용자가 네이버 앱으로 찍어 승인할 때까지 기다린다.
// QR은 약 3분마다 만료되므로 2분 50초마다 새 QR로 바꿔 qr.png를 갱신한다. 최대 9분.
const { chromium } = require('playwright');
const fs = require('fs');
const S = process.env.NAVER_STATE_DIR || require('path').join(__dirname, __dirname.endsWith('probes') ? '../..' : '..', '.state');
const PROFILE = S + '/naver-profile', SHOTS = S + '/shots';
fs.mkdirSync(SHOTS, { recursive: true });
const sleep = ms => new Promise(r => setTimeout(r, ms));
(async () => {
  const ctx = await chromium.launchPersistentContext(PROFILE, {
    headless: !process.env.HEADED,   // PC에서는 HEADED=1 로 실행하면 QR이 화면 창에 바로 뜸
    viewport: { width: 1000, height: 900 }, locale: 'ko-KR', timezoneId: 'Asia/Seoul',
    userAgent: 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36' });
  const page = ctx.pages()[0] || await ctx.newPage();
  for (let round = 1; round <= 3; round++) {
    await page.goto('https://nid.naver.com/nidlogin.login?mode=form&url=https://www.naver.com', { waitUntil: 'domcontentloaded', timeout: 60000 });
    await sleep(2000);
    if (!page.url().includes('nid.naver.com')) { console.log('이미 로그인됨'); break; }
    // '로그인 상태 유지'(nvlong=on)를 켜야 장기 쿠키가 발급됨. 안 켜면 세션 쿠키라 금방 풀림.
    // 체크박스는 ID 로그인 탭에만 있으므로 거기서 켜고, QR 탭 폼에도 nvlong=on을 넣어 보낸다.
    await page.locator('label.login_stay').click({ timeout: 3000 }).catch(() => {});
    await page.getByRole('link', { name: 'QR 코드 로그인' }).first().click();
    await page.waitForSelector('canvas, img[src*="qr"], [class*="qr"] img', { timeout: 15000 }).catch(() => {});
    const keep = await page.evaluate(() => {
      let n = 0;
      for (const f of document.querySelectorAll('form')) {
        let i = f.querySelector('input[name="nvlong"]');
        if (!i) { i = document.createElement('input'); i.type = 'hidden'; i.name = 'nvlong'; f.appendChild(i); }
        i.value = 'on'; if (i.type === 'checkbox') i.checked = true; n++;
      }
      return n;
    }).catch(() => 0);
    console.log('로그인 상태 유지 값 넣은 폼:', keep);
    await sleep(2500);
    await page.screenshot({ path: SHOTS + '/qr.png' });
    console.log(`QR 준비 ${round}`);
    for (let t = 0; t < 34; t++) {          // 약 2분 50초
      await sleep(5000);
      if (!page.url().includes('nid.naver.com')) break;
    }
    if (!page.url().includes('nid.naver.com')) {
      await sleep(2000); await page.screenshot({ path: SHOTS + '/done.png' });
      await ctx.storageState({ path: S + '/naver-state.json' });   // 세션 쿠키까지 저장 (민감 정보, 작업 공간 밖으로 내보내지 않음)
      console.log('로그인 성공 (상태 저장됨)');
      const aut = (await ctx.cookies()).find(c => c.name === 'NID_AUT');
      console.log('NID_AUT 만료:', aut && aut.expires > 0 ? new Date(aut.expires * 1000).toISOString() : '세션 쿠키(브라우저 닫으면 만료)');
      // 블로그 관리 화면에서 통계 메뉴 주소 찾기
      for (const u of ['https://admin.blog.naver.com/seoeunjin13', 'https://admin.blog.naver.com/AdminMain.naver?blogId=seoeunjin13']) {
        await page.goto(u, { waitUntil: 'networkidle' }).catch(() => {});
        await sleep(3000);
        console.log('PAGE', page.url());
        for (const f of page.frames()) {
          const links = await f.$$eval('a', as => as.map(a => (a.innerText.trim() + ' ' + a.href)).filter(t => /통계|stat/i.test(t))).catch(() => []);
          for (const l of [...new Set(links)].slice(0, 15)) console.log('  LINK', l.replace(/\s+/g, ' ').slice(0, 160));
        }
      }
      await page.screenshot({ path: SHOTS + '/admin.png' });
      break;
    }
    if (round === 3) { await page.screenshot({ path: SHOTS + '/qr_timeout.png' }); console.log('시간 초과'); }
  }
  await ctx.close();
})().catch(e => { console.log('오류: ' + e.message); process.exit(1); });
