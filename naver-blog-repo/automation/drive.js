// Google Drive 폴더 관리 (Drive API, 외부 패키지 없음 — Node 18+ fetch 사용)
//
// 폴더 이름 = "<번호>_빈폴더" 또는 "<번호>_<가게이름>"  (사용자 지시 2026-11-12: 번호로 부르기)
//   사용자: "2번 사진 업로드"  → claim 2 <가게이름>   : 2_빈폴더 → 2_<가게이름>, 바로 글쓰기 시작
//   임시저장 끝나면            → done 2               : 3일 뒤 자동 정리 예약
//   사용자: "1번 블로그 등록"  → clear 1              : 블로그에 발행된 것 확인(RSS) → 사진·영상 휴지통 → 1_빈폴더
//   매일 (작업 스케줄러)        → cleanup              : 예약일이 지났고 발행이 확인된 폴더를 clear 와 같이 정리
//   폴더에 영수증만 있을 때     → receipt 3 <가게>     : 3_<가게>, 영수증 리뷰 + 예전 글에 영수증 인증 카드 추가(edit_nds.js) 후 "등록했어요" 보고
//   사용자가 피드백을 주면      → feedback 3           : 그날부터 3일 뒤 자동으로 비움 (이미 발행된 글이라 발행 확인 생략)
//
// 사용법
//   node automation/drive.js auth                   처음 한 번: 브라우저로 구글 로그인 → 토큰 저장
//   node automation/drive.js init [개수]             1_빈폴더 ~ N_빈폴더 준비 (기본 5, 이미 있는 번호는 건너뜀)
//   node automation/drive.js status                 번호별 상태와 파일 수
//   node automation/drive.js claim <번호> <가게이름>  <번호>_빈폴더 → <번호>_<가게이름>
//   node automation/drive.js download <번호> <받을곳> 폴더 안 파일 전부 받기 (5MB 제한 없음)
//   node automation/drive.js done <번호> [제목문구]   임시저장 완료 기록 + 3일 뒤 정리 예약
//   node automation/drive.js clear <번호> [--force]  발행 확인 후 비우고 <번호>_빈폴더 (--force: 확인 없이)
//   node automation/drive.js receipt <번호> <가게>    영수증만 있는 폴더: <번호>_<가게> (작업 종류 receipt)
//   node automation/drive.js feedback <번호>         피드백 받은 날 기록 → 3일 뒤 정리 예약
//   node automation/drive.js cleanup                예약일이 지난 폴더 정리 (발행 확인된 것만)
//
// 필요한 파일 (.state/ 는 깃에 올리지 않음)
//   .state/google-credentials.json   구글 클라우드 콘솔 → OAuth 클라이언트(데스크톱 앱) → JSON
//   .state/google-token.json         auth 가 만듦
//   .state/drive_jobs.json           번호별 작업 기록
const fs = require('fs');
const path = require('path');
const http = require('http');
const { execFile } = require('child_process');

const S = process.env.NAVER_STATE_DIR || path.join(__dirname, '..', '.state');
const CRED = path.join(S, 'google-credentials.json');
const TOKEN = path.join(S, 'google-token.json');
const JOBS = path.join(S, 'drive_jobs.json');
const BLOG_ID = 'seoeunjin13';
const EMPTY = '빈폴더';
const KEEP_DAYS = 3;
const FOLDER = 'application/vnd.google-apps.folder';
const API = 'https://www.googleapis.com/drive/v3';

fs.mkdirSync(S, { recursive: true });
const readJson = (f, d) => (fs.existsSync(f) ? JSON.parse(fs.readFileSync(f, 'utf8')) : d);
const writeJson = (f, o) => fs.writeFileSync(f, JSON.stringify(o, null, 2));
const log = (...a) => console.log(...a);

function client() {
  if (!fs.existsSync(CRED)) throw new Error(`${CRED} 가 없습니다. README의 "구글 드라이브 연결"을 따라 OAuth 클라이언트 JSON을 저장하세요.`);
  const c = readJson(CRED);
  return c.installed || c.web;
}

async function auth() {
  const c = client();
  const server = http.createServer();
  await new Promise(r => server.listen(0, '127.0.0.1', r));
  const redirect = `http://127.0.0.1:${server.address().port}`;
  const url = 'https://accounts.google.com/o/oauth2/v2/auth?' + new URLSearchParams({
    client_id: c.client_id, redirect_uri: redirect, response_type: 'code', access_type: 'offline', prompt: 'consent',
    scope: 'https://www.googleapis.com/auth/drive',   // 휴대폰에서 올린 파일의 이름 변경·삭제까지 하려면 전체 권한 필요
  });
  log('브라우저에서 구글 로그인을 진행하세요. 안 열리면 아래 주소를 직접 여세요:\n' + url);
  execFile('rundll32', ['url.dll,FileProtocolHandler', url]);
  const code = await new Promise((resolve, reject) => {
    server.on('request', (req, res) => {
      const q = new URL(req.url, redirect).searchParams;
      res.writeHead(200, { 'Content-Type': 'text/html; charset=utf-8' });
      res.end(q.get('code') ? '연결됐어요. 이 창은 닫아도 됩니다.' : '연결 실패: ' + q.get('error'));
      server.close();
      q.get('code') ? resolve(q.get('code')) : reject(new Error(q.get('error')));
    });
  });
  const t = await tokenRequest({ code, client_id: c.client_id, client_secret: c.client_secret, redirect_uri: redirect, grant_type: 'authorization_code' });
  writeJson(TOKEN, t);
  log('토큰 저장 완료:', TOKEN);
}

async function tokenRequest(body) {
  const r = await fetch('https://oauth2.googleapis.com/token', { method: 'POST', body: new URLSearchParams(body) });
  const j = await r.json();
  if (!r.ok) throw new Error('토큰 오류: ' + JSON.stringify(j));
  j.expires_at = Date.now() + (j.expires_in - 60) * 1000;
  return j;
}

async function accessToken() {
  let t = readJson(TOKEN);
  if (!t) throw new Error('먼저 "node automation/drive.js auth" 를 실행하세요.');
  if (Date.now() > t.expires_at) {
    const c = client();
    const n = await tokenRequest({ refresh_token: t.refresh_token, client_id: c.client_id, client_secret: c.client_secret, grant_type: 'refresh_token' });
    t = { ...t, ...n };
    writeJson(TOKEN, t);
  }
  return t.access_token;
}

async function api(method, p, body, raw) {
  const r = await fetch(API + p, {
    method, headers: { Authorization: 'Bearer ' + (await accessToken()), ...(body ? { 'Content-Type': 'application/json' } : {}) },
    body: body ? JSON.stringify(body) : undefined,
  });
  if (!r.ok) throw new Error(`${method} ${p} → ${r.status} ${await r.text()}`);
  return raw ? r : r.json();
}

async function list(q) {
  const out = []; let page;
  do {
    const j = await api('GET', '/files?' + new URLSearchParams({
      q: q + ' and trashed = false', pageSize: '1000', fields: 'nextPageToken, files(id,name,mimeType,size,createdTime)',
      ...(page ? { pageToken: page } : {}),
    }));
    out.push(...j.files); page = j.nextPageToken;
  } while (page);
  return out;
}
const folders = () => list(`mimeType = '${FOLDER}' and 'root' in parents`);
const filesIn = id => list(`'${id}' in parents and mimeType != '${FOLDER}'`);
const rename = (id, name) => api('PATCH', `/files/${id}`, { name });
async function findFolder(name) {
  const f = (await folders()).filter(x => x.name === name);
  if (!f.length) throw new Error(`폴더 "${name}" 를 찾지 못했습니다.`);
  if (f.length > 1) throw new Error(`"${name}" 폴더가 ${f.length}개 있습니다. 하나만 남겨 주세요.`);
  return f[0];
}
// 번호 폴더: "3_빈폴더", "3_쿠로카메"
const numOf = name => { const m = name.match(/^(\d+)_(.+)$/); return m ? { n: Number(m[1]), rest: m[2] } : null; };
async function numbered() {
  const out = {};
  for (const f of await folders()) { const p = numOf(f.name); if (p) (out[p.n] = out[p.n] || []).push({ ...f, rest: p.rest }); }
  return out;
}
async function byNum(n) {
  const all = (await numbered())[n] || [];
  if (!all.length) throw new Error(`${n}번 폴더가 없습니다.`);
  if (all.length > 1) throw new Error(`${n}번 폴더가 ${all.length}개 있습니다: ${all.map(f => f.name).join(', ')}`);
  return all[0];
}
const jobOf = (jobs, n) => jobs.find(j => j.n === Number(n) && !j.cleaned);

async function init(count = 5) {
  const have = await numbered();
  for (let i = 1; i <= Number(count); i++) {
    if (have[i]) { log('있음:', have[i].map(f => f.name).join(', ')); continue; }
    await api('POST', '/files', { name: `${i}_${EMPTY}`, mimeType: FOLDER, parents: ['root'] });
    log('만듦:', `${i}_${EMPTY}`);
  }
}

async function status() {
  const jobs = readJson(JOBS, []);
  const all = await numbered();
  for (const n of Object.keys(all).map(Number).sort((a, b) => a - b)) for (const f of all[n]) {
    const cnt = (await filesIn(f.id)).length;
    const j = jobOf(jobs, n);
    const st = f.rest === EMPTY ? '비어 있음'
      : j && j.kind === 'receipt' ? (j.deleteAfter ? `영수증 등록 완료 · 정리 예정 ${j.deleteAfter.slice(0, 10)}` : '영수증 등록 · 피드백 기다림')
      : j && j.deleteAfter ? `임시저장 완료 · 정리 예정 ${j.deleteAfter.slice(0, 10)}` : '작성 중';
    log(`${f.name.padEnd(16)} 파일 ${String(cnt).padStart(3)}개  ${st}`);
  }
}

async function claim(n, store, kind = 'post') {
  if (!n || !store) throw new Error(`사용법: ${kind === 'receipt' ? 'receipt' : 'claim'} <번호> <가게이름>`);
  const f = await byNum(n);
  if (f.rest !== EMPTY) throw new Error(`${f.name} 은 빈 폴더가 아닙니다.`);
  const cnt = (await filesIn(f.id)).length;
  if (!cnt) throw new Error(`${f.name} 에 사진이 없습니다.`);
  const jobs = readJson(JOBS, []);
  jobs.push({ n: Number(n), store, kind, folderId: f.id, claimedAt: new Date().toISOString() });
  writeJson(JOBS, jobs);
  await rename(f.id, `${n}_${store}`);
  log(`${f.name} → ${n}_${store} (파일 ${cnt}개)`);
}

async function download(n, dest) {
  const f = await byNum(n);
  fs.mkdirSync(dest, { recursive: true });
  const files = await filesIn(f.id);
  for (const x of files) {
    const out = path.join(dest, x.name.replace(/[\\/:*?"<>|]/g, '_'));
    if (fs.existsSync(out) && fs.statSync(out).size === Number(x.size)) { log('건너뜀(이미 있음):', x.name); continue; }
    const r = await api('GET', `/files/${x.id}?alt=media`, null, true);
    fs.writeFileSync(out, Buffer.from(await r.arrayBuffer()));
    log('받음:', x.name, Math.round(Number(x.size) / 1024) + 'KB');
  }
  log(`완료: ${files.length}개 → ${dest}`);
}

async function done(n, titleHint) {
  const jobs = readJson(JOBS, []);
  const j = jobOf(jobs, n);
  if (!j) throw new Error(`${n}번 작성 기록이 없습니다. (claim 을 먼저 했는지 확인)`);
  j.savedAt = new Date().toISOString();
  j.deleteAfter = new Date(Date.now() + KEEP_DAYS * 86400e3).toISOString();
  j.titleHint = titleHint || j.store;
  writeJson(JOBS, jobs);
  log(`${n}_${j.store}: 임시저장 완료 기록 · ${j.deleteAfter.slice(0, 10)} 이후 발행이 확인되면 자동으로 비웁니다.`);
}

// 영수증만 있던 폴더: 사용자가 피드백을 준 날로부터 3일 뒤에 비운다
async function feedback(n) {
  const jobs = readJson(JOBS, []);
  const j = jobOf(jobs, n);
  if (!j) throw new Error(`${n}번 작업 기록이 없습니다.`);
  j.feedbackAt = new Date().toISOString();
  j.deleteAfter = new Date(Date.now() + KEEP_DAYS * 86400e3).toISOString();
  writeJson(JOBS, jobs);
  log(`${n}_${j.store}: 피드백 받음 · ${j.deleteAfter.slice(0, 10)} 이후 자동으로 비웁니다.`);
}

// 블로그 확인: 로그인 없이 RSS(최근 발행 글)에서 제목 문구를 찾는다.
// 임시저장 목록은 보지 않음 — 글쓰기 화면의 "이어서 쓸까요?" 창에서 '취소'를 누르면 글이 지워지기 때문.
async function published(hint) {
  const r = await fetch(`https://rss.blog.naver.com/${BLOG_ID}.xml`);
  const xml = await r.text();
  const titles = [...xml.matchAll(/<title>(?:<!\[CDATA\[)?([\s\S]*?)(?:\]\]>)?<\/title>/g)].map(m => m[1]);
  const norm = s => s.replace(/\s+/g, '');
  return titles.find(t => norm(t).includes(norm(hint)));
}

async function clear(n, force) {
  const f = await byNum(n);
  if (f.rest === EMPTY) { log(`${f.name}: 이미 빈 폴더`); return; }
  const jobs = readJson(JOBS, []);
  const j = jobOf(jobs, n);
  const hint = (j && j.titleHint) || f.rest;
  if (j && j.kind === 'receipt') force = true;   // 이미 발행된 예전 글 → 발행 확인 생략
  const t = force ? null : await published(hint);
  if (!t && !force) { log(`${f.name}: 블로그에서 "${hint}" 발행 글을 아직 못 찾았어요 → 지우지 않음 (발행 직후면 몇 분 뒤 다시)`); return false; }
  log(`${f.name}: 발행 확인 "${t || '(확인 생략)'}"`);
  const files = await filesIn(f.id);
  for (const x of files) await api('PATCH', `/files/${x.id}`, { trashed: true });   // 휴지통으로 (30일 안에 복구 가능)
  await rename(f.id, `${n}_${EMPTY}`);
  if (j) { j.cleaned = new Date().toISOString(); writeJson(JOBS, jobs); }
  log(`${f.name}: 사진·영상 ${files.length}개 휴지통으로 → ${n}_${EMPTY}`);
  return true;
}

async function cleanup() {
  const jobs = readJson(JOBS, []);
  for (const j of jobs.filter(x => x.deleteAfter && !x.cleaned)) {
    if (Date.now() < Date.parse(j.deleteAfter)) { log(`${j.n}_${j.store}: 아직 ${j.deleteAfter.slice(0, 10)} 전`); continue; }
    await clear(j.n, false);
  }
}

module.exports = { api, list, folders, filesIn, rename, findFolder, published, byNum, numbered };
if (require.main !== module) return;
const [cmd, a, b] = process.argv.slice(2);
const run = {
  auth, init: () => init(a || 5), status, claim: () => claim(a, b), download: () => download(a, b),
  done: () => done(a, b), clear: () => clear(a, b === '--force'), cleanup,
  receipt: () => claim(a, b, 'receipt'), feedback: () => feedback(a),
}[cmd];
if (!run) { log(fs.readFileSync(__filename, 'utf8').split('\n').filter(l => l.startsWith('//')).join('\n')); process.exit(1); }
run().catch(e => { console.error('오류:', e.message); process.exit(1); });
