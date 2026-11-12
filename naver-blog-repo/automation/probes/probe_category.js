// 임시저장 글을 열어 발행 설정 창의 카테고리 구조를 확인만 한다 (발행·저장 안 함).
// 사용법: node automation/probes/probe_category.js <제목 문구>
const { chromium } = require('playwright');
const path = require('path');
const S = process.env.NAVER_STATE_DIR || path.join(__dirname, '../..', '.state');
const [OWN] = process.argv.slice(2);
const sleep = ms => new Promise(r => setTimeout(r, ms));
(async () => {
  const b = await chromium.launch();
  const ctx = await b.newContext({ storageState: S + '/naver-state.json', locale: 'ko-KR', viewport: { width: 1400, height: 1000 } });
  const page = await ctx.newPage(); page.on('dialog', d => d.accept());
  await page.goto('https://blog.naver.com/seoeunjin13?Redirect=Write&', { waitUntil: 'domcontentloaded', timeout: 60000 }); await sleep(10000);
  const fr = page.frame('mainFrame');
  if (await fr.locator('.se-popup-button-cancel').count()) { await fr.locator('.se-popup-button-confirm').first().click(); await sleep(5000); }
  else {
    const h = fr.locator('.se-help-panel-close-button'); if (await h.count()) { await h.first().click().catch(() => {}); await sleep(800); }
    await fr.locator('[data-click-area="tpb*s.count"]').evaluate(e => e.click()); await sleep(4000);
    await page.screenshot({ path: S + '/shots/cat_0_list.png' });
    console.log('목록:', JSON.stringify((await fr.locator('li', { has: fr.locator('button[class*="article_button"]') }).allInnerTexts()).map(t => t.replace(/\s+/g, ' ').slice(0, 40))));
    await fr.locator('li', { has: fr.locator('button[class*="article_button"]') }).filter({ hasText: OWN }).first().locator('button[class*="article_button"]').click(); await sleep(7000);
  }
  const h2 = fr.locator('.se-help-panel-close-button'); if (await h2.count()) await h2.first().click().catch(() => {});
  console.log('열린 글:', (await fr.locator('.se-title-text').first().innerText()).trim().slice(0, 50));
  await fr.locator('[data-click-area="tpb.publish"]').click(); await sleep(2500);
  await page.screenshot({ path: S + '/shots/cat_1_layer.png' });
  const items = await fr.evaluate(() => [...document.querySelectorAll('[class*="layer_publish"] *, [class*="publish_layer"] *')]
    .filter(e => e.children.length === 0 && e.innerText && e.innerText.trim()).map(e => `${e.tagName}.${(e.className || '').toString().slice(0, 60)} | ${e.getAttribute('data-click-area') || ''} | ${e.innerText.trim().slice(0, 30)}`).slice(0, 80));
  console.log(items.join('\n'));
  const cat = fr.locator('[data-click-area*="category"], button[class*="selectbox_button"]').first();
  if (await cat.count()) { await cat.click(); await sleep(1500); await page.screenshot({ path: S + '/shots/cat_2_open.png' });
    console.log('--- 목록'); console.log((await fr.evaluate(() => [...document.querySelectorAll('[class*="option_list"] li, [class*="select_option"] li, [role=option]')]
      .map(e => `${(e.className||'').toString().slice(0,40)} | ${e.getAttribute('data-click-area')||''} | ${e.innerText.trim().slice(0,30)}`))).join('\n')); }
  await b.close();   // 저장하지 않고 닫음
})().catch(e => { console.log('오류: ' + e.message.slice(0, 300)); process.exit(1); });
