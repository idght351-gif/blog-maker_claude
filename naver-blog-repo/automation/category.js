// 발행 설정 창(이미 열린 상태)에서 카테고리를 확인하고, want가 있으면 그 카테고리로 바꾼다. 현재 카테고리 이름을 돌려준다.
// 카테고리 규칙 (STYLE.md): 매장 방문기 = '먹보여행', 편의점·대형 프랜차이즈 신제품 리뷰 = '제품리뷰'
async function current(fr) {
  return fr.evaluate(() => {
    const btn = document.querySelector('[data-click-area="tpb*i.category"], button[class*="selectbox_button"]');
    return btn ? btn.innerText.trim() : null;
  });
}
async function selectCategory(fr, page, want, S) {
  let now = await current(fr);
  if (!want || now === want) return now;
  const btn = fr.locator('[data-click-area="tpb*i.category"], button[class*="selectbox_button"]').first();
  await btn.click(); await new Promise(r => setTimeout(r, 1200));
  if (S) await page.screenshot({ path: S + '/shots/category_open.png' });
  const opt = fr.locator('[class*="option_list"] li, [class*="select_option"] li, [role=option], label').filter({ hasText: new RegExp('^\\s*' + want + '\\s*$') }).first();
  if (await opt.count()) { await opt.click(); await new Promise(r => setTimeout(r, 1000)); }
  return current(fr);
}
module.exports = { selectCategory, current };
