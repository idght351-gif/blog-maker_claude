// 새 글 화면에서 장소 검색 결과만 보고 닫음 (저장 안 함). 이어쓰기 창이 뜨면 확인(이어쓰기)만 누르고 아무것도 바꾸지 않음
const { chromium } = require('playwright');
const S = process.env.NAVER_STATE_DIR || require('path').join(__dirname, '../..', '.state'); const Q=process.argv[2]; const sleep=ms=>new Promise(r=>setTimeout(r,ms));
(async()=>{
  const b=await chromium.launch(); const ctx=await b.newContext({storageState:S+'/naver-state.json',locale:'ko-KR',viewport:{width:1400,height:1000}});
  const page=await ctx.newPage(); page.on('dialog',d=>d.dismiss());
  await page.goto('https://blog.naver.com/seoeunjin13?Redirect=Write&',{waitUntil:'domcontentloaded'}); await sleep(10000);
  const fr=page.frame('mainFrame');
  if(await fr.locator('.se-popup-button-cancel').count()){ await fr.locator('.se-popup-button-confirm').first().click(); await sleep(4000); }
  const h=fr.locator('.se-help-panel-close-button'); if(await h.count()) await h.first().click().catch(()=>{});
  await fr.locator('button.se-map-toolbar-button, button:has-text("장소")').first().click(); await sleep(2500);
  await fr.locator('input.react-autosuggest__input').first().click(); await page.keyboard.type(Q,{delay:80}); await sleep(2500);
  console.log('SUG',JSON.stringify(await fr.evaluate(()=>[...document.querySelectorAll('.react-autosuggest__suggestion, li[role="option"]')].filter(e=>e.offsetParent).map(e=>e.innerText.replace(/\s+/g,' ').slice(0,70)))));
  const s0=fr.locator('.react-autosuggest__suggestion').first(); if(await s0.count()) await s0.click(); else await page.keyboard.press('Enter'); await sleep(6000);
  console.log('LIST',JSON.stringify(await fr.evaluate(()=>[...document.querySelectorAll('li')].filter(e=>e.offsetParent&&!e.matches('.react-autosuggest__suggestion')&&/추가/.test(e.innerText)&&!/^(사진|MYBOX|동영상|스티커|인용구|구분선|링크|파일|일정|소스코드)/.test(e.innerText.trim())).map(e=>e.innerText.replace(/\s+/g,' ').slice(0,90)).slice(0,8))));
  const r=fr.locator('*',{hasText:'마곡중앙6로'}).last(); console.log('ITEM', await r.evaluate(e=>{let x=e; for(let i=0;i<4&&x.parentElement;i++) x=x.parentElement; return x.outerHTML.replace(/\s+/g,' ').slice(0,900);}));
  await r.hover(); await sleep(800); console.log('BTNS', JSON.stringify(await fr.evaluate(()=>[...document.querySelectorAll('button')].filter(b=>b.offsetParent&&/추가/.test(b.innerText)).map(b=>b.className+'|'+b.innerText.trim()))));
  await page.screenshot({path:S+'/shots/place_probe.png'});
  await b.close();
})();
