// 시험: 새 글에 카테고리 '제품리뷰'를 고르고 임시저장 → 다시 열어 카테고리가 남는지 확인. (시험 글은 delete_draft.js로 지움)
const { chromium } = require('playwright');
const path = require('path');
const S = process.env.NAVER_STATE_DIR || path.join(__dirname, '../..', '.state');
const { selectCategory, current } = require('../category');
const T = '카테고리시험글';
const sleep = ms => new Promise(r => setTimeout(r, ms));
(async () => {
  const b = await chromium.launch();
  const ctx = await b.newContext({ storageState: S + '/naver-state.json', locale: 'ko-KR', viewport: { width: 1400, height: 1000 } });
  let page = await ctx.newPage(); page.on('dialog', d => d.accept());
  await page.goto('https://blog.naver.com/seoeunjin13?Redirect=Write&', { waitUntil: 'domcontentloaded', timeout: 60000 }); await sleep(10000);
  let fr = page.frame('mainFrame');
  if (await fr.locator('.se-popup-button-cancel').count()) { console.log('중단: 이어쓰기 창'); await b.close(); return; }
  const h = fr.locator('.se-help-panel-close-button'); if (await h.count()) await h.first().click().catch(() => {});
  await fr.locator('.se-title-text').first().click(); await page.keyboard.type(T, { delay: 120 }); await sleep(500);
  await fr.locator('[data-click-area="tpb.publish"]').click(); await sleep(2500);
  console.log('처음 카테고리:', await current(fr));
  console.log('고른 뒤:', await selectCategory(fr, page, '제품리뷰', S));
  await page.screenshot({ path: S + '/shots/catdraft_1.png' });
  await fr.locator('[data-click-area="tpb.publish"]').click().catch(() => {}); await sleep(1200);
  if (await fr.locator('[data-click-area="tpb*i.publish"]').isVisible().catch(() => false)) { await page.keyboard.press('Escape'); await sleep(800); }
  await fr.locator('[data-click-area="tpb.save"]').click(); await sleep(4000);
  console.log('저장함');
  await page.close();
  page = await ctx.newPage(); page.on('dialog', d => d.accept());
  await page.goto('https://blog.naver.com/seoeunjin13?Redirect=Write&', { waitUntil: 'domcontentloaded', timeout: 60000 }); await sleep(10000);
  fr = page.frame('mainFrame');
  if (await fr.locator('.se-popup-button-cancel').count()) { await fr.locator('.se-popup-button-confirm').first().click(); await sleep(5000); }
  else {
    await fr.locator('[data-click-area="tpb*s.count"]').evaluate(e => e.click()); await sleep(4000);
    await fr.locator('li', { has: fr.locator('button[class*="article_button"]') }).filter({ hasText: T }).first().locator('button[class*="article_button"]').click(); await sleep(7000);
  }
  console.log('다시 연 글:', (await fr.locator('.se-title-text').first().innerText()).trim());
  await fr.locator('[data-click-area="tpb.publish"]').click(); await sleep(2500);
  console.log('다시 연 뒤 카테고리:', await current(fr));
  await page.screenshot({ path: S + '/shots/catdraft_2.png' });
  await b.close();
})().catch(e => { console.log('오류: ' + e.message.slice(0, 300)); process.exit(1); });
