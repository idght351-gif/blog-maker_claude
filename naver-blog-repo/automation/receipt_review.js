// 네이버 MY플레이스 영수증 리뷰 등록 (모바일 웹 /my/checkin)
// 사용법: node automation/receipt_review.js <영수증.jpg> <가게이름> <리뷰글.txt> [음식사진.jpg ...] [--submit]
//   --submit 없이 실행하면 마지막 '등록' 직전까지만 진행하고 화면을 저장(.state/shots/rr_*.png)해서 확인용으로 쓴다.
//   사용자 지시(2026-11-12): 영수증 리뷰는 확인 없이 바로 등록 → 평소에는 --submit 으로 실행.
const { chromium, devices } = require('playwright');
const fs = require('fs');
const path = require('path');
const S = process.env.NAVER_STATE_DIR || path.join(__dirname, '..', '.state');
const args = process.argv.slice(2);
const SUBMIT = args.includes('--submit');
const [RECEIPT, STORE, TEXT_FILE, ...PHOTOS] = args.filter(a => a !== '--submit');
const TEXT = fs.readFileSync(TEXT_FILE, 'utf8').trim();
const sleep = ms => new Promise(r => setTimeout(r, ms));
let step = 0;

(async () => {
  const b = await chromium.launch();
  const ctx = await b.newContext({ ...devices['iPhone 13'], storageState: S + '/naver-state.json', locale: 'ko-KR', timezoneId: 'Asia/Seoul' });
  const page = await ctx.newPage();
  const dump = async tag => {
    const f = `${S}/shots/rr_${++step}_${tag}.png`;
    await page.screenshot({ path: f, fullPage: true });
    const items = await page.$$eval('a, button, input, textarea, label, [role=button]', es => es.filter(e => e.offsetParent || e.type === 'file')
      .map(e => `${e.tagName}${e.type ? '[' + e.type + ']' : ''} ${(e.innerText || e.placeholder || e.getAttribute('aria-label') || '').trim().replace(/\s+/g, ' ').slice(0, 50)}`)
      .filter(t => t.trim().length > 3 && !/^INPUT\[(radio|checkbox)\]\s*$/.test(t)).slice(0, 120));
    console.log(`== ${step} ${tag} ${page.url()}\n ` + items.join('\n '));
  };
  const clickText = async (re, timeout = 8000) => {
    const loc = page.locator('button, a, [role=button], label').filter({ hasText: re }).first();
    await loc.waitFor({ state: 'visible', timeout });
    await loc.click();
    await sleep(2500);
  };

  if (process.env.RR_URL) {   // 영수증 인증은 이미 됐고 리뷰 쓰기 화면부터 이어갈 때
    await page.goto(process.env.RR_URL, { waitUntil: 'domcontentloaded' }); await sleep(12000); await dump('resume');
  } else {
  // 1) 영수증 올리기
  await page.goto('https://m.place.naver.com/my/checkin', { waitUntil: 'domcontentloaded' });
  await sleep(4000);
  await page.locator('input[type=file]').first().setInputFiles(RECEIPT);
  await sleep(8000);   // OCR 인식 대기
  for (let i = 0; i < 20 && /status=scanning/.test(page.url()); i++) await sleep(2000);   // 인식이 늦으면 최대 40초 더 기다림
  await sleep(2000);
  await dump('after_receipt');
  const body = await page.innerText('body');
  if (!body.replace(/\s+/g, '').toLowerCase().includes(STORE.replace(/\s+/g, '').toLowerCase())) {   // 대소문자 무시 (BHC/bhc)
    console.log(`⚠️ 화면에서 "${STORE}"를 찾지 못했습니다. 인식 결과를 확인하세요.`);
    await b.close(); process.exit(2);
  }
  // 영수증에서 방문 시간을 못 읽으면 시간 칸이 비어 '맞아요'가 꺼져 있음 → RR_TIME(예: "12:08")으로 채움
  const tin = page.locator('input[type=time]').first();
  if (await tin.count() && !(await tin.inputValue())) {
    if (!process.env.RR_TIME) { console.log('⚠️ 방문 시간이 비어 있음 → RR_TIME="HH:MM" 필요'); await b.close(); process.exit(3); }
    await tin.fill(process.env.RR_TIME); await tin.dispatchEvent('change'); await sleep(1500);
    console.log('방문 시간 입력:', await tin.inputValue());
  }
  // 인식된 장소가 맞으면 '이 장소가 맞아요' (가게 이름 확인은 위에서 끝남)
  const yes = page.locator('button').filter({ hasText: '이 장소가 맞아요' });
  if (await yes.count()) { await yes.first().click(); await sleep(4000); await dump('place_ok'); console.log('RESUME_URL', page.url()); }
  }
  // 이후 단계는 화면 구조를 확인하며 채워 나간다 (아래 STEPS).
  // 앱 설치 안내가 뜨면 모바일 웹으로 계속
  const web = page.locator('button').filter({ hasText: '모바일 웹으로 볼게요' });
  if (await web.count() && await web.first().isVisible()) { await web.first().click(); await sleep(1000); }
  // 선택 항목: 글자가 정확히 같은 label/button 클릭 (방문 형태, 대기, 목적, 동행, 별점, 키워드)
  // 접힌 키워드 목록·앱 안내 창이 가려도 되도록 DOM에서 직접 click() 한다
  for (const t of JSON.parse(process.env.RR_PICK || '[]')) {
    const ok = await page.evaluate(t => {
      const norm = s => (s || '').replace(/\s+/g, '');
      const els = [...document.querySelectorAll('label, button')];
      const el = els.find(e => norm(e.textContent) === norm(t)) || els.find(e => norm(e.textContent).endsWith(norm(t)) && norm(e.textContent).length < norm(t).length + 6);
      if (!el) return false; el.click(); return true;
    }, t);
    if (!ok) console.log('선택 항목 없음:', t);
    await sleep(400);
  }
  // 별점(필수): DOM click()으로는 안 먹어서 실제 터치처럼 누른다
  const stars = process.env.RR_STARS || '5';
  const star = page.locator(`button[aria-label="${stars}점"]`).first();
  if (await star.count()) {
    await star.evaluate(e => e.scrollIntoView({ block: 'center' })); await sleep(800);   // 위에 고정되는 가게 이름 바에 가리지 않게 가운데로
    const bx = await star.boundingBox();
    await page.touchscreen.tap(bx.x + bx.width / 2, bx.y + bx.height / 2); await sleep(800);
  }
  else console.log('별점 버튼 없음');
  const STEPS = JSON.parse(process.env.RR_STEPS || '[]');   // 예: ["다음", "리뷰 쓰기"]
  for (const t of STEPS) {
    await page.evaluate(t => { const b = [...document.querySelectorAll('button')].find(e => new RegExp(t).test(e.textContent.trim())); b && b.click(); }, t);
    await sleep(3000); await dump(t.replace(/\W/g, '') || 'step');
  }

  // 리뷰 글 입력
  const ta = page.locator('textarea').first();
  if (await ta.count()) {
    await ta.fill(TEXT); await sleep(1000);   // 입력칸 위 안내 글자(label)가 클릭을 가려서 바로 채운다
    if (PHOTOS.length) {
      const fi = page.locator('input[type=file]');
      if (await fi.count()) { await fi.last().setInputFiles(PHOTOS); await sleep(5000); }
    }
    await dump('filled');
    if (SUBMIT) {
      await clickText(/^(등록|등록하기|완료)$/);
      await sleep(4000);
      await dump('submitted');
      console.log('등록 완료');
    } else console.log('확인 모드: 등록 버튼은 누르지 않았습니다.');
  } else console.log('리뷰 입력칸이 아직 안 보입니다. RR_STEPS로 다음 버튼을 지정하세요.');
  await ctx.storageState({ path: S + '/naver-state.json' });
  await b.close();
})().catch(e => { console.log('오류', e.message); process.exit(1); });
