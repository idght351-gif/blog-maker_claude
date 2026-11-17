// 글 제목만 바꾼다 (본문은 그대로). 임시저장 글은 다시 저장, 발행 글은 수정 발행.
// 사용법:
//   node automation/retitle.js draft <지금 제목에 있는 문구> "<새 제목>" [--dry]
//   node automation/retitle.js post  <지금 제목에 있는 문구> "<새 제목>" [--dry]
//   --dry: 글 찾기·열기·제목 바꾸기까지만 하고 저장/발행하지 않음
// 안전장치: 제목에 문구가 없으면 멈춤. 발행 글은 제목이 문구에 맞는 글이 정확히 1개일 때만.
//          바꾼 뒤 제목이 새 제목과 다르거나 본문(글자 수·부품 수)이 바뀌었으면 저장/발행하지 않음.
//          "이어서 쓸까요?" 창에서 '취소'는 절대 누르지 않음 (누르면 그 글이 지워짐).
const { chromium } = require('playwright');
const path = require('path');
const fs = require('fs');
const S = process.env.NAVER_STATE_DIR || path.join(__dirname, '..', '.state');
const BLOG = 'seoeunjin13';
const args = process.argv.slice(2);
const DRY = args.includes('--dry');
const [MODE, OLD, NEW] = args.filter(a => a !== '--dry');
const sleep = ms => new Promise(r => setTimeout(r, ms));
const norm = s => (s || '').replace(/\s+/g, '');
if (!['draft', 'post'].includes(MODE) || !OLD || !NEW) { console.log('사용법: node automation/retitle.js <draft|post> <문구> "<새 제목>" [--dry]'); process.exit(1); }
fs.mkdirSync(S + '/shots', { recursive: true });

async function findPost(q) {
  const hits = [];
  for (let page = 1; page <= 20; page++) {
    const r = await fetch(`https://m.blog.naver.com/api/blogs/${BLOG}/post-list?categoryNo=0&itemCount=30&page=${page}`, { headers: { Referer: `https://m.blog.naver.com/${BLOG}`, 'User-Agent': 'Mozilla/5.0' } });
    const items = ((await r.json()).result || {}).items || [];
    if (!items.length) break;
    for (const it of items) if (norm(it.titleWithInspectMessage).includes(norm(q))) hits.push({ logNo: String(it.logNo), title: it.titleWithInspectMessage });
  }
  return hits;
}

(async () => {
  let logNo;
  if (MODE === 'post') {
    const hits = await findPost(OLD);
    console.log('찾은 글:', JSON.stringify(hits.map(h => `${h.logNo} ${h.title.slice(0, 40)}`)));
    if (hits.length !== 1) { console.log(hits.length ? '중단: 글이 여러 개' : '중단: 글이 없음'); process.exit(2); }
    logNo = hits[0].logNo;
  }
  const b = await chromium.launch();
  const ctx = await b.newContext({ storageState: S + '/naver-state.json', locale: 'ko-KR', viewport: { width: 1400, height: 1000 } });
  const page = await ctx.newPage(); page.on('dialog', d => { console.log('대화상자:', d.message().slice(0, 60)); d.accept(); });
  const quit = async (msg, code) => { console.log(msg); await page.screenshot({ path: S + '/shots/retitle_stop.png' }).catch(() => {}); await b.close(); process.exit(code); };

  if (MODE === 'post') {
    await page.goto(`https://blog.naver.com/PostUpdateForm.naver?blogId=${BLOG}&logNo=${logNo}`, { waitUntil: 'domcontentloaded', timeout: 60000 }); await sleep(10000);
  } else {
    await page.goto(`https://blog.naver.com/${BLOG}?Redirect=Write&`, { waitUntil: 'domcontentloaded', timeout: 60000 }); await sleep(10000);
  }
  const fr = page.frame('mainFrame') || page.mainFrame();
  if (MODE === 'post') {
    if (await fr.locator('.se-popup-button-cancel').count()) await quit('중단: 이어쓰기 창이 떴음 (손대지 않음)', 3);
  } else {
    let needList = true;
    if (await fr.locator('.se-popup-button-cancel').count()) {
      await fr.locator('.se-popup-button-confirm').first().click(); await sleep(5000);   // '확인' = 이어서 쓰기 (지우지 않음)
      needList = !norm(await fr.locator('.se-title-text').first().innerText()).includes(norm(OLD));
    }
    if (needList) {
      const h = fr.locator('.se-help-panel-close-button'); if (await h.count()) { await h.first().click().catch(() => {}); await sleep(800); }
      await fr.locator('[data-click-area="tpb*s.count"]').evaluate(e => e.click()); await sleep(2500);
      const item = fr.locator('li', { has: fr.locator('button[class*="article_button"]') }).filter({ hasText: OLD });
      if ((await item.count()) !== 1) await quit(`중단: 임시저장 목록에서 "${OLD}" 글이 ${await item.count()}개`, 2);
      await item.first().locator('button[class*="article_button"]').click(); await sleep(7000);
    }
  }
  const help = fr.locator('.se-help-panel-close-button'); if (await help.count()) await help.first().click().catch(() => {});
  const titleEl = fr.locator('.se-title-text').first();
  const before = (await titleEl.innerText()).trim();
  if (!norm(before).includes(norm(OLD))) await quit('중단: 열린 글 제목이 다름 → ' + before.slice(0, 40), 4);
  console.log('지금 제목:', before);
  const body = () => fr.evaluate(() => {
    const cs = [...document.querySelectorAll('.se-component')].filter(c => !c.classList.contains('se-documentTitle'));
    // 편집 도구 버튼(사진 편집·삭제 등) 글자는 빼고 실제 글자 + 사진 수만 비교
    const part = c => [...c.querySelectorAll('.se-module-text, .se-module-oglink, .se-module-map-text')].map(e => e.innerText).join('') + '|img' + c.querySelectorAll('img').length;
    return { n: cs.length, parts: cs.map(part) };
  });
  const b0 = await body();

  // 제목 칸 끝을 클릭 → 제목 칸 안에서 전체 선택 → 새 제목을 한 글자씩 입력
  const box = await titleEl.boundingBox(); const fb = await page.locator('#mainFrame').boundingBox().catch(() => null) || { x: 0, y: 0 };
  const inFrame = !!(await page.locator('#mainFrame').count());
  await page.mouse.click((inFrame ? fb.x : 0) + box.x + box.width - 5, (inFrame ? fb.y : 0) + box.y + box.height / 2); await sleep(500);
  await page.keyboard.press('Control+A'); await sleep(300);
  await page.keyboard.type(NEW, { delay: 30 }); await sleep(1000);
  const after = (await titleEl.innerText()).trim();
  const b1 = await body();
  console.log('바꾼 제목:', after);
  if (after !== NEW.trim()) await quit('중단: 제목이 새 제목과 다름 → 저장/발행 안 함', 5);
  const diff = b0.parts.map((p, i) => p !== b1.parts[i] ? i + ': ' + JSON.stringify(p.slice(0, 80)) + ' → ' + JSON.stringify((b1.parts[i] || '').slice(0, 80)) : null).filter(Boolean);
  if (b1.n !== b0.n || diff.length) await quit(`중단: 본문이 달라짐 (부품 ${b0.n}→${b1.n}) ${diff.join(' | ')} → 저장/발행 안 함`, 6);
  if (DRY) { console.log('확인 모드: 저장/발행하지 않고 닫음'); await b.close(); return; }

  if (MODE === 'draft') {
    await fr.locator('[data-click-area="tpb.save"]').click(); await sleep(4000);
    console.log('임시저장 완료');
  } else {
    await fr.locator('[data-click-area="tpb.publish"]').click(); await sleep(2500);
    const confirm = fr.locator('[data-click-area="tpb*i.publish"], button[class*="confirm_btn"]').first();
    if (!(await confirm.count())) await quit('중단: 발행 확인 버튼을 못 찾음', 7);
    await confirm.click(); await sleep(6000);
    const view = await ctx.newPage();
    await view.goto(`https://m.blog.naver.com/${BLOG}/${logNo}`, { waitUntil: 'domcontentloaded' }); await sleep(4000);
    const ok = await view.evaluate(t => document.body.innerText.replace(/\s+/g, '').includes(t), norm(NEW));
    console.log(ok ? `수정 발행 완료 (logNo ${logNo})` : '⚠️ 발행 글에서 새 제목을 확인하지 못함');
  }
  await ctx.storageState({ path: S + '/naver-state.json' });
  await b.close();
})().catch(e => { console.log('오류: ' + e.message.slice(0, 300)); process.exit(1); });
