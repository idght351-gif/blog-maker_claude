const { chromium } = require('playwright');
const S = process.env.NAVER_STATE_DIR || require('path').join(__dirname, __dirname.endsWith('probes') ? '../..' : '..', '.state');
(async () => {
  const ctx = await chromium.launchPersistentContext(S + '/naver-profile', { locale: 'ko-KR' });
  const ck = await ctx.cookies('https://www.naver.com');
  console.log('쿠키:', ck.filter(c => c.name.startsWith('NID')).map(c => `${c.name}(만료:${c.expires > 0 ? new Date(c.expires*1000).toISOString().slice(0,10) : '세션'})`).join(', ') || '없음');
  await ctx.close();
})();
