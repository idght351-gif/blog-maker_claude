// 타임라인에서 해당 가게의 '리뷰 쓰기'를 눌러 리뷰 작성 화면 주소만 출력 (등록하지 않음)
const { chromium, devices } = require('playwright');
const S = process.env.NAVER_STATE_DIR || require('path').join(__dirname, '../..', '.state'); const sleep=ms=>new Promise(r=>setTimeout(r,ms)); const K=process.argv[2];
(async()=>{
  const b=await chromium.launch(); const ctx=await b.newContext({storageState:S+'/naver-state.json',locale:'ko-KR',...devices['iPhone 13']});
  const page=await ctx.newPage();
  await page.goto('https://m.place.naver.com/my/timeline',{waitUntil:'domcontentloaded'}); await sleep(7000);
  for(let i=0;i<120;i++){ if((await page.innerText('body')).includes(K)) break; await page.mouse.wheel(0,2500); await sleep(1200); }
  const ok=await page.evaluate(k=>{ const btns=[...document.querySelectorAll('a,button')].filter(e=>/리뷰 쓰기/.test(e.innerText));
    const t=btns.find(e=>{let x=e; for(let i=0;i<8&&x;i++){ if(x.innerText.includes(k)&&x.innerText.length<500) return true; x=x.parentElement;} return false;}); if(!t) return false; t.click(); return true; },K);
  const pop=ctx.waitForEvent('page',{timeout:8000}).catch(()=>null);
  console.log('clicked',ok); await sleep(6000); const np=await pop; console.log('URL',page.url(), np?('NEWPAGE '+np.url()):'');
  console.log('HREFS', JSON.stringify(await page.evaluate(k=>[...document.querySelectorAll('a,button')].filter(e=>/리뷰 쓰기/.test(e.innerText)).slice(0,3).map(e=>e.outerHTML.slice(0,300)),K)));
  console.log((await page.innerText('body')).replace(/\s+/g,' ').slice(0,300));
  await b.close();
})();
