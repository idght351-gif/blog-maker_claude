const {chromium}=require('playwright');
(async()=>{const b=await chromium.launch();const p=await b.newPage({viewport:{width:390,height:844},deviceScaleFactor:1});
await p.goto('file://'+process.argv[2]);await p.waitForTimeout(800);
const r=await p.evaluate(()=>{
 const out=[];
 document.querySelectorAll('h1,h2,h3,p,li,.kpi span,.kpi i,td,.ans div,.lead,.sub,.baekho div').forEach(el=>{
  if(el.closest('.tbl')&&el.tagName!=='TD')return;
  const range=document.createRange(); const lines={};
  const walker=document.createTreeWalker(el,NodeFilter.SHOW_TEXT);
  let n; while(n=walker.nextNode()){for(let i=0;i<n.length;i++){range.setStart(n,i);range.setEnd(n,i+1);const rc=range.getBoundingClientRect();if(!rc.height)continue;const k=Math.round(rc.top);(lines[k]=lines[k]||[]).push(n.data[i]);}}
  const ks=Object.keys(lines).map(Number).sort((a,b)=>a-b); if(ks.length<2)return;
  const last=lines[ks[ks.length-1]].join('').trim();
  if(last.length<=6) out.push({tag:el.tagName+(el.className?'.'+el.className:''),lines:ks.length,last,top:Math.round(el.getBoundingClientRect().top+scrollY),text:el.innerText.slice(0,50)});
 });return out;});
console.log(JSON.stringify(r,null,0));await b.close();})();
