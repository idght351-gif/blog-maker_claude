// 발행된 글의 수정 화면 구조 확인 (읽기만, 아무것도 바꾸지 않음)
// 사용법: node probe_update.js <logNo>
const { chromium } = require('playwright');
const S = require('path').join(__dirname, '../..', '.state');
const sleep = ms => new Promise(r => setTimeout(r, ms));
(async () => {
  const b = await chromium.launch();
  const ctx = await b.newContext({ storageState: S + '/naver-state.json', locale: 'ko-KR', viewport: { width: 1400, height: 1000 } });
  const page = await ctx.newPage(); page.on('dialog', d => { console.log('대화상자:', d.message().slice(0, 60)); d.dismiss(); });
  await page.goto(`https://blog.naver.com/PostUpdateForm.naver?blogId=seoeunjin13&logNo=${process.argv[2]}`, { waitUntil: 'domcontentloaded', timeout: 60000 });
  await sleep(10000);
  console.log('URL', page.url(), 'frames', page.frames().map(f => f.name()).join(','));
  const fr = page.frame('mainFrame') || page.mainFrame();
  const popup = await fr.locator('.se-popup-button-cancel').count();
  console.log('이어쓰기 창:', popup ? '있음 (손대지 않음)' : '없음');
  const title = await fr.locator('.se-title-text').first().innerText().catch(() => '(제목 없음)');
  console.log('제목:', title.trim().slice(0, 60));
  console.log('앞부분:', JSON.stringify(await fr.evaluate(() => [...document.querySelectorAll('.se-component')].filter(c => !c.classList.contains('se-documentTitle')).slice(0, 5)
    .map(c => (c.className.match(/se-(image|custom|text|quotation|imageGroup|placesMap|oglink|material)\b/) || [, c.className.slice(0, 40)])[1]))));
  console.log('대표:', JSON.stringify(await fr.evaluate(() => [...document.querySelectorAll('.se-component.se-image')].map((c, i) => { const bt = c.querySelector('.se-set-rep-image-button'); return bt && bt.className.includes('se-is-selected') ? i : null; }).filter(x => x !== null))));
  console.log('상단 버튼:', JSON.stringify(await fr.evaluate(() => [...document.querySelectorAll('[data-click-area^="tpb"]')].map(e => e.getAttribute('data-click-area') + ':' + e.innerText.trim().replace(/\s+/g, ' ')))));
  await page.screenshot({ path: S + '/shots/update_probe.png' });
  await b.close();
})().catch(e => { console.log('오류', e.message); process.exit(1); });
