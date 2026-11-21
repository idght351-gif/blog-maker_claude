// 올릴순서 파일을 드라이브 번호 폴더 안 "올릴순서" 하위 폴더에 올린다. 사용법: node automation/upload_order.js <번호> <올릴순서 폴더 경로>
const d = require(process.cwd() + '/automation/drive.js');
const fs = require('fs'), path = require('path');
const [, , num, dir] = process.argv;
(async () => {
  const f = await d.byNum(Number(num));
  const ex = await d.list(`'${f.id}' in parents and name = '올릴순서' and mimeType = 'application/vnd.google-apps.folder'`);
  const sub = ex[0] || await d.api('POST', '/files', { name: '올릴순서', mimeType: 'application/vnd.google-apps.folder', parents: [f.id] });
  const have = new Set((await d.list(`'${sub.id}' in parents`)).map(x => x.name));
  for (const name of fs.readdirSync(dir).sort()) {
    if (have.has(name)) continue;
    const buf = fs.readFileSync(path.join(dir, name));
    const type = name.endsWith('.jpg') ? 'image/jpeg' : name.endsWith('.gif') ? 'image/gif' : 'video/quicktime';
    const B = 'xx' + Date.now();
    const body = Buffer.concat([Buffer.from(`--${B}\r\nContent-Type: application/json; charset=UTF-8\r\n\r\n${JSON.stringify({ name, parents: [sub.id] })}\r\n--${B}\r\nContent-Type: ${type}\r\n\r\n`), buf, Buffer.from(`\r\n--${B}--`)]);
    const r = await fetch('https://www.googleapis.com/upload/drive/v3/files?uploadType=multipart', { method: 'POST', headers: { Authorization: 'Bearer ' + await d.accessToken(), 'Content-Type': `multipart/related; boundary=${B}` }, body });
    if (!r.ok) { console.log('실패', name, r.status, (await r.text()).slice(0, 200)); return; }
  }
  console.log(f.name + '/올릴순서', '파일', (await d.list(`'${sub.id}' in parents`)).length);
})().catch(e => console.log('ERR', e.message));
