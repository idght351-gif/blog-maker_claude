// 붙여넣기 시험: HTML(굵게·색·노란 배경·가운데 정렬)을 붙여넣고 에디터에 남은 서식을 확인한다. 저장하지 않음.
const { chromium } = require('playwright');
const S = process.env.NAVER_STATE_DIR || require('path').join(__dirname, __dirname.endsWith('probes') ? '../..' : '..', '.state');
(async () => {
  const b = await chromium.launch(); const ctx = await b.newContext({ storageState: S + '/naver-state.json', locale: 'ko-KR', viewport: { width: 1400, height: 1000 },
    permissions: ['clipboard-read', 'clipboard-write'] });
  const page = await ctx.newPage(); page.on('dialog', d => d.dismiss());
  await page.goto('https://blog.naver.com/seoeunjin13?Redirect=Write&', { waitUntil: 'domcontentloaded', timeout: 60000 });
  await page.waitForTimeout(10000);
  const fr = page.frame('mainFrame');
  if (await fr.locator('.se-popup-button-cancel').count()) { console.log('이어쓰기 창이 떠서 중단'); await b.close(); return; }
  await fr.locator('.se-component.se-text .se-text-paragraph').first().click();
  const html = '<p style="text-align:center">첫 줄 <b>굵은 글씨</b> 그리고 <span style="color:#f12f22">빨간 글씨</span> 😋</p>' +
               '<p style="text-align:center"><span style="background-color:#f4d400">노란 배경 메뉴명</span></p><p style="text-align:center">둘째 문단 한글이 빠지지 않는지 확인</p>';
  // 포커스된 요소(에디터 입력 버퍼 포함)에 paste 이벤트를 직접 보낸다
  const targets = [];
  for (const f of page.frames()) {
    const r = await f.evaluate(h => {
      const el = (document.activeElement && document.activeElement !== document.body && document.activeElement.tagName !== 'IFRAME') ? document.activeElement : (document.body.isContentEditable ? document.body : null); if (!el) return null;
      const dt = new DataTransfer(); dt.setData('text/html', h); dt.setData('text/plain', h.replace(/<[^>]+>/g, ' '));
      const ev = new ClipboardEvent('paste', { clipboardData: dt, bubbles: true, cancelable: true });
      el.dispatchEvent(ev); return el.tagName + '.' + (el.className || '').toString().slice(0, 40);
    }, html).catch(() => null);
    if (r) targets.push(f.name() + ':' + r);
  }
  console.log('paste 대상:', targets.join(' / '));
  await page.waitForTimeout(2500);
  const out = await fr.evaluate(() => [...document.querySelectorAll('.se-main-container .se-text-paragraph, .se-component.se-text .se-text-paragraph')].slice(0, 6).map(p => p.className.match(/align-\w+/)?.[0] + ' | ' + p.innerHTML.replace(/\s+/g, ' ').slice(0, 300)));
  console.log(out.join('\n'));
  await page.screenshot({ path: S + '/shots/paste_probe.png' });
  // 저장하지 않고 편집 내용 비우기: 전체 선택 후 삭제 (자동저장 흔적 방지)
  await page.keyboard.press('Control+A'); await page.keyboard.press('Delete');
  await b.close();
})().catch(e => { console.log('오류: ' + e.message.slice(0, 200)); process.exit(1); });
