// 이미 발행된 글에 '내돈내산 방문 인증' 카드를 썸네일(첫 사진) 바로 아래에 넣고 수정 발행한다.
// 폴더에 영수증만 있을 때 쓰는 흐름 (사용자 지시 2026-11-12):
//   영수증 리뷰 등록(receipt_review.js) → 이 스크립트 → 사용자에게 "등록했어요" 보고 → 피드백 받은 날 + 3일 뒤 폴더 비우기
// 사용법: node automation/edit_nds.js <가게 이름(제목·영수증 목록에서 찾을 글자)> [--dry]
//   --dry: 글 찾기·수정 화면 열기·발행 창 확인까지만 (카드 넣기·발행 안 함)
// 안전장치: 제목에 가게 이름이 없으면 멈춤. 카드가 이미 있으면 멈춤. 카드가 두 번째 자리가 아니면 발행하지 않음.
const { chromium } = require('playwright');
const path = require('path');
const S = process.env.NAVER_STATE_DIR || path.join(__dirname, '..', '.state');
const BLOG = 'seoeunjin13';
const args = process.argv.slice(2);
const DRY = args.includes('--dry');
const [STORE] = args.filter(a => a !== '--dry');
const sleep = ms => new Promise(r => setTimeout(r, ms));
const norm = s => (s || '').replace(/\s+/g, '');

// 블로그 글 목록(모바일 API)에서 제목에 가게 이름이 들어간 글 찾기 (최신 글부터)
async function findPost(store) {
  const hits = [];
  for (let page = 1; page <= 20; page++) {
    const r = await fetch(`https://m.blog.naver.com/api/blogs/${BLOG}/post-list?categoryNo=0&itemCount=30&page=${page}`, { headers: { Referer: `https://m.blog.naver.com/${BLOG}`, 'User-Agent': 'Mozilla/5.0' } });
    const items = ((await r.json()).result || {}).items || [];
    if (!items.length) break;
    for (const it of items) if (norm(it.titleWithInspectMessage).includes(norm(store))) hits.push({ logNo: String(it.logNo), title: it.titleWithInspectMessage, date: it.addDate });
  }
  return hits;
}

(async () => {
  const hits = await findPost(STORE);
  console.log('찾은 글:', JSON.stringify(hits.map(h => `${h.logNo} ${h.title.slice(0, 40)}`)));
  if (hits.length !== 1) { console.log(hits.length ? '중단: 글이 여러 개라 어느 글인지 정해야 함' : '중단: 해당 가게 글이 없음'); process.exit(2); }
  const { logNo } = hits[0];

  const b = await chromium.launch();
  const ctx = await b.newContext({ storageState: S + '/naver-state.json', locale: 'ko-KR', viewport: { width: 1400, height: 1000 } });
  const page = await ctx.newPage(); page.on('dialog', d => { console.log('대화상자:', d.message().slice(0, 60)); d.accept(); });
  await page.goto(`https://blog.naver.com/PostUpdateForm.naver?blogId=${BLOG}&logNo=${logNo}`, { waitUntil: 'domcontentloaded', timeout: 60000 });
  await sleep(10000);
  const fr = page.frame('mainFrame') || page.mainFrame();
  if (await fr.locator('.se-popup-button-cancel').count()) { console.log('중단: 이어쓰기 창이 떴음 (취소 누르면 글이 지워질 수 있어 손대지 않음)'); await b.close(); process.exit(3); }
  const help = fr.locator('.se-help-panel-close-button'); if (await help.count()) await help.first().click().catch(() => {});
  const title = (await fr.locator('.se-title-text').first().innerText()).trim();
  if (!norm(title).includes(norm(STORE))) { console.log('중단: 제목이 다름 →', title.slice(0, 40)); await b.close(); process.exit(4); }
  console.log('수정 화면:', title.slice(0, 50));
  const order = () => fr.evaluate(() => [...document.querySelectorAll('.se-component')].filter(c => !c.classList.contains('se-documentTitle')).slice(0, 4)
    .map(c => (c.className.match(/se-(image|custom|text|quotation|imageGroup|placesMap)\b/) || [, '?'])[1]));
  const before = await order();
  console.log('앞부분(전):', JSON.stringify(before));
  if (await fr.locator('.se-component.se-custom').count()) { console.log('중단: 이미 내돈내산 카드가 있음'); await b.close(); process.exit(5); }

  if (!DRY) {
    // 첫 사진(썸네일)을 선택한 상태로 카드를 넣으면 그 바로 아래에 들어감 (2026-11-12 확인)
    const first = fr.locator('.se-component').filter({ hasNot: fr.locator('.se-title-text') }).nth(0);
    await fr.locator('.se-component.se-image').first().click({ position: { x: 200, y: 200 } }); await sleep(800);
    await fr.evaluate(() => { const b = [...document.querySelectorAll('button')].find(e => /^내돈내산/.test(e.innerText.trim())); b && b.click(); }); await sleep(3000);
    await fr.evaluate(() => { const b = [...document.querySelectorAll('button')].find(e => e.innerText.trim() === '방문'); b && b.click(); }); await sleep(2000);
    const card = fr.locator('li, [class*="item"]').filter({ hasText: STORE }).filter({ hasText: '영수증' }).last();
    if (!(await card.count())) { console.log('중단: 내돈내산 목록에 영수증 인증이 없음 (영수증 리뷰 먼저)'); await b.close(); process.exit(6); }
    console.log('방문 인증 항목:', (await card.innerText()).replace(/\s+/g, ' ').slice(0, 80));
    await card.click(); await sleep(3000);
    const after = await order();
    console.log('앞부분(후):', JSON.stringify(after));
    await page.screenshot({ path: S + '/shots/edit_nds_1.png' });
    if (!(after[0] === before[0] && after[1] === 'custom')) {
      console.log('중단: 카드가 썸네일 바로 아래가 아님 → 발행하지 않음 (수정 내용 버림)'); await b.close(); process.exit(7);
    }
  }

  // 수정 발행: 상단 '발행' → 발행 설정 창 → 아래쪽 '발행' 확인 버튼
  await fr.locator('[data-click-area="tpb.publish"]').click(); await sleep(2500);
  await page.screenshot({ path: S + '/shots/edit_nds_2_publish_layer.png' });
  const confirm = fr.locator('[data-click-area="tpb*i.publish"], button[class*="confirm_btn"]').first();
  console.log('발행 확인 버튼:', await confirm.count() ? (await confirm.innerText()).trim() : '못 찾음');
  if (DRY) { console.log('확인 모드: 발행하지 않고 닫음'); await b.close(); return; }
  if (!(await confirm.count())) { console.log('중단: 발행 확인 버튼을 못 찾음'); await b.close(); process.exit(8); }
  await confirm.click(); await sleep(6000);
  console.log('발행 후 주소:', page.url());
  await page.screenshot({ path: S + '/shots/edit_nds_3_done.png' });
  // 발행된 글에서 카드 확인
  const view = await ctx.newPage();
  await view.goto(`https://m.blog.naver.com/${BLOG}/${logNo}`, { waitUntil: 'domcontentloaded' }); await sleep(4000);
  const ok = await view.evaluate(() => /내돈내산/.test(document.body.innerText));
  console.log(ok ? `완료: 내돈내산 카드가 발행 글에 보임 (logNo ${logNo})` : '⚠️ 발행 글에서 카드를 확인하지 못함');
  await ctx.storageState({ path: S + '/naver-state.json' });
  await b.close();
})().catch(e => { console.log('오류: ' + e.message.slice(0, 300)); process.exit(1); });
