// 로그인 유지: 저장된 쿠키로 네이버를 한 번 열고, 새로 받은 쿠키를 다시 저장한다.
// 컨테이너가 살아 있는 동안 주기적으로(예: 30분마다) 돌리면 세션이 만료되기 전에 갱신된다.
// 사용법: node automation/keep_alive.js   → LOGGED_IN / LOGGED_OUT 출력
const { chromium } = require('playwright');
const S = process.env.NAVER_STATE_DIR || require('path').join(__dirname, '..', '.state');
(async () => {
  const b = await chromium.launch();
  const ctx = await b.newContext({ storageState: S + '/naver-state.json', locale: 'ko-KR' });
  const p = await ctx.newPage();
  await p.goto('https://blog.naver.com/seoeunjin13?Redirect=Write&', { waitUntil: 'domcontentloaded', timeout: 60000 });
  await p.waitForTimeout(6000);
  if (/nidlogin/.test(p.url())) { console.log('LOGGED_OUT'); await b.close(); process.exit(2); }
  await ctx.storageState({ path: S + '/naver-state.json' });
  console.log('LOGGED_IN (쿠키 갱신 저장)');
  await b.close();
})().catch(e => { console.log('오류: ' + e.message.slice(0, 150)); process.exit(1); });
