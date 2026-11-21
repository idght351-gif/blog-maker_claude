// 서식 원고(HTML)를 드라이브 번호 폴더 안에 구글 문서로 올린다 (휴대폰에서 문서 앱 → 모두 선택 → 복사).
// 사용법: node automation/upload_doc.js <번호> <원고.html> <문서 이름> [plain.txt]
const d = require('./drive.js'); const fs = require('fs');
const [, , num, file, name, txt] = process.argv;
(async () => {
  const f = await d.byNum(Number(num));
  const up = async (meta, type, buf) => {
    const B = 'xx' + Date.now();
    const body = Buffer.concat([Buffer.from(`--${B}\r\nContent-Type: application/json; charset=UTF-8\r\n\r\n${JSON.stringify(meta)}\r\n--${B}\r\nContent-Type: ${type}\r\n\r\n`), buf, Buffer.from(`\r\n--${B}--`)]);
    const r = await fetch('https://www.googleapis.com/upload/drive/v3/files?uploadType=multipart&fields=id,name,webViewLink', { method: 'POST', headers: { Authorization: 'Bearer ' + await d.accessToken(), 'Content-Type': `multipart/related; boundary=${B}` }, body });
    if (!r.ok) throw new Error(r.status + ' ' + (await r.text()).slice(0, 200)); return r.json();
  };
  for (const x of await d.list(`'${f.id}' in parents and (name = '${name}' or name = '${name} (글만)')`)) await d.api('PATCH', `/files/${x.id}`, { trashed: true });
  const a = await up({ name, parents: [f.id], mimeType: 'application/vnd.google-apps.document' }, 'text/html; charset=UTF-8', fs.readFileSync(file));
  console.log('문서:', a.name, a.webViewLink);
  if (txt) { const b = await up({ name: name + ' (글만)', parents: [f.id], mimeType: 'application/vnd.google-apps.document' }, 'text/plain; charset=UTF-8', fs.readFileSync(txt)); console.log('문서:', b.name, b.webViewLink); }
})().catch(e => console.log('ERR', e.message));
