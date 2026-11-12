// 은똥이의 먹보여행 스타일 썸네일 만들기 (정사각형 1080px)
//   음식 사진 + 왼쪽 위 크림색 종이 위 손글씨 가게 이름♥ + 분홍 리본 부제 + 화살표 달린 손글씨 말풍선 + 반짝이 + 워터마크
//   (2026-11-12 기존 글 썸네일 40개 분석 결과를 따름)
// 사용법: node automation/make_thumb.js <설정.json> <출력.jpg>
// 설정 예: drafts/kurokame_thumb.json
//   photo: 사진 경로, crop: {x, y, size} 원본 픽셀 기준 정사각형 (생략 시 가운데)
//   title, subtitle, notes: [{text:"줄1\n줄2", x, y, w, rot, arrow:[x1,y1,cx,cy,x2,y2]}]  좌표는 1080 기준
//   sparkles: [[x,y,크기]], hearts: [[x,y,크기]]
const fs = require('fs');
const path = require('path');
const { chromium } = require('playwright');
const [specFile, out] = process.argv.slice(2);
const spec = JSON.parse(fs.readFileSync(specFile, 'utf8'));
const root = path.dirname(path.resolve(specFile));
const W = 1080;

(async () => {
  const b = await chromium.launch();
  const page = await b.newPage({ viewport: { width: W, height: W } });
  // 1) 원본을 정사각형으로 자르기 (브라우저 canvas 사용)
  const photo = fs.readFileSync(path.resolve(root, spec.photo)).toString('base64');
  const esc = s => s.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/\n/g, '<br>').replace(/♥/g, '<span class="hp">♥</span>');
  const notes = (spec.notes || []).map(n => `<div class="note" style="left:${n.x}px;top:${n.y}px;width:${n.w || 300}px;transform:rotate(${n.rot || 0}deg)">${esc(n.text)}</div>`).join('');
  const arrows = (spec.notes || []).filter(n => n.arrow).map(n => {
    const [x1, y1, cx, cy, x2, y2] = n.arrow;
    const ang = Math.atan2(y2 - cy, x2 - cx), L = 22;
    const h1 = [x2 - L * Math.cos(ang - 0.5), y2 - L * Math.sin(ang - 0.5)], h2 = [x2 - L * Math.cos(ang + 0.5), y2 - L * Math.sin(ang + 0.5)];
    const d = `M${x1},${y1} Q${cx},${cy} ${x2},${y2} M${h1} L${x2},${y2} L${h2}`;
    return `<path d="${d}" stroke="#4a3426" stroke-width="9" fill="none" stroke-linecap="round" stroke-linejoin="round" opacity=".35"/><path d="${d}" stroke="#fff" stroke-width="5" fill="none" stroke-linecap="round" stroke-linejoin="round"/>`;
  }).join('');
  const sparkle = (x, y, s) => `<path transform="translate(${x},${y}) scale(${s / 40})" d="M0,-40 C4,-8 8,-4 40,0 C8,4 4,8 0,40 C-4,8 -8,4 -40,0 C-8,-4 -4,-8 0,-40Z" fill="#fff" stroke="#4a3426" stroke-width="3"/>`;
  const heart = (x, y, s) => `<path transform="translate(${x},${y}) scale(${s / 40})" d="M0,14 C-30,-8 -22,-34 0,-18 C22,-34 30,-8 0,14Z" fill="#e8607e"/>`;
  const deco = (spec.sparkles || []).map(a => sparkle(...a)).join('') + (spec.hearts || []).map(a => heart(...a)).join('');
  const html = `<!doctype html><html><head><meta charset="utf-8">
<link href="https://fonts.googleapis.com/css2?family=Jua&family=Gaegu:wght@700&family=Gowun+Dodum&display=block" rel="stylesheet">
<style>
*{margin:0;box-sizing:border-box}
body{width:${W}px;height:${W}px;position:relative;overflow:hidden;font-family:'Gaegu',cursive}
#ph{position:absolute;inset:0;width:${W}px;height:${W}px;filter:saturate(1.08) contrast(1.03) brightness(1.03)}
.warm{position:absolute;inset:0;background:radial-gradient(ellipse at center,rgba(255,200,140,0) 55%,rgba(80,40,10,.18) 100%)}
.title{position:absolute;left:${spec.titleX ?? 48}px;top:${spec.titleY ?? 40}px;padding:22px 40px 26px 36px;background:rgba(255,248,236,.9);border-radius:28px 18px 30px 16px;
  box-shadow:0 4px 14px rgba(60,30,10,.18);transform:rotate(-2deg);font-family:'Jua',sans-serif;font-size:${spec.titleSize || 104}px;line-height:1;color:#3f2b20;letter-spacing:2px}
.title .hp{color:#e8607e;font-size:.6em;vertical-align:.45em;margin-left:10px}
.sub{position:absolute;left:${spec.subX ?? 150}px;top:${spec.subY ?? 186}px;padding:10px 30px 12px;background:rgba(253,226,222,.95);border-radius:12px;transform:rotate(-2deg);
  font-family:'Gowun Dodum',sans-serif;font-weight:700;font-size:${spec.subSize || 40}px;color:#4a3426;box-shadow:0 3px 10px rgba(60,30,10,.15)}
.note{position:absolute;padding:20px 26px;background:rgba(255,250,242,.86);border-radius:46% 40% 44% 38% / 40% 46% 38% 44%;
  font-size:${spec.noteSize || 40}px;line-height:1.18;letter-spacing:-2px;color:#3f2b20;text-align:center;box-shadow:0 3px 12px rgba(60,30,10,.16)}
.note .hp{color:#e8607e}
.wm{position:absolute;right:26px;bottom:20px;font-family:'Gowun Dodum',sans-serif;font-size:22px;color:rgba(255,255,255,.92);text-shadow:0 1px 3px rgba(0,0,0,.55)}
svg{position:absolute;inset:0}
</style></head><body>
<canvas id="ph" width="${W}" height="${W}"></canvas><div class="warm"></div>
<svg width="${W}" height="${W}">${arrows}${deco}</svg>
<div class="title">${esc(spec.title)}<span class="hp">♥</span></div>
${spec.subtitle ? `<div class="sub">${esc(spec.subtitle)}</div>` : ''}
${notes}
<div class="wm">${esc(spec.watermark || '@은똥이의먹보여행')}</div>
</body></html>`;
  await page.setContent(html, { waitUntil: 'networkidle' });
  await page.evaluate(async ({ photo, crop }) => {
    const img = new Image(); img.src = 'data:image/jpeg;base64,' + photo; await img.decode();
    const s = crop && crop.size || Math.min(img.width, img.height);
    const x = crop && crop.x != null ? crop.x : (img.width - s) / 2, y = crop && crop.y != null ? crop.y : (img.height - s) / 2;
    document.getElementById('ph').getContext('2d').drawImage(img, x, y, s, s, 0, 0, 1080, 1080);
    await document.fonts.ready;
  }, { photo, crop: spec.crop });
  await page.waitForTimeout(500);
  await page.screenshot({ path: out, type: 'jpeg', quality: 92 });
  await b.close();
  console.log('썸네일 저장:', out);
})().catch(e => { console.log('오류', e.message); process.exit(1); });
