"""붙여넣기 도우미 페이지: build 파일 + 업로드용 사진 → 휴대폰에서 '글 복사 / 사진 저장'하며 네이버 앱에 직접 입력하는 페이지.
사용법: python3 scripts/make_helper_page.py drafts/build_<가게>.py drafts/<가게>_upload <출력폴더>
출력: <출력폴더>/index.html + <출력폴더>/p/ (사진·GIF). Artifact로 올릴 때 index.html + files{p/..}."""
import html, importlib.util, json, re, shutil, sys
from pathlib import Path

spec = importlib.util.spec_from_file_location("post", sys.argv[1]); m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
UP, OUT = Path(sys.argv[2]), Path(sys.argv[3]); (OUT / "p").mkdir(parents=True, exist_ok=True)
FIX = lambda t: t.replace("⭕", "👍").replace("❌", "💦")   # 광고 티 특수문자 금지 (STYLE)
plain = lambda t: FIX(m.plain(t))
COL = {"r": "var(--c-r)", "p": "var(--c-p)", "g": "var(--c-g)", "bl": "var(--c-bl)", "o": "var(--c-o)"}

def rich(t):
    out, pos = [], 0
    for x in m.INLINE.finditer(t):
        out.append(html.escape(t[pos:x.start()])); k, s = x.group(1), html.escape(x.group(2))
        out.append({"B": f"<b>{s}</b>", "i": f"<i>{s}</i>", "u": s, "y": f'<mark>{s}</mark>'}.get(k) or f'<span style="color:{COL[k]}">{s}</span>')
        pos = x.end()
    out.append(html.escape(t[pos:])); return FIX("".join(out)).replace("\n", "<br>")

chunks, cur, n_img = [], None, 0
def flush():
    global cur
    if cur and cur["lines"]: chunks.append(cur)
    cur = None
def text(line_html, line_plain, kind="p"):
    global cur
    if cur is None: cur = {"t": "text", "lines": [], "copy": []}
    cur["lines"].append((kind, line_html)); cur["copy"].append(line_plain)

for b in m.B:
    k = b[0]
    if k == "img":
        flush(); files = []
        for n in b[1]:
            n_img += 1; src = UP / (f"IMG_{n}" if "." in n else f"IMG_{n}.jpg")
            name = f"{n_img:02d}_{src.name}"; shutil.copy(src, OUT / "p" / name); files.append(name)
        chunks.append({"t": "img", "files": files, "first": n_img - len(files) + 1})
    elif k == "p":
        if "[광고 링크 필요]" in b[1]: flush(); chunks.append({"t": "ad"}); continue
        bold = len(b) > 2 and b[2].get("b")
        for line in b[1].split("\n"):
            h = rich(line); text(f"<b>{h}</b>" if bold else h, plain(line))
    elif k == "menu":
        rows = [b[1]] + [it[0] if isinstance(it, tuple) else it for it in b[2]]
        for i, r in enumerate(rows): text(f"<b>{rich(r)}</b>" if i == 0 else rich(r), plain(r))
        text("", "")
    elif k in ("h", "hq", "hl", "hb", "q", "bubble"):
        label = {"h": "소제목 · 밑줄 인용구", "hq": "소제목 · 기본 인용구", "hl": "소제목 · 세로선 인용구", "hb": "소제목 · 굵게", "q": "인용구", "bubble": "말풍선 인용구"}[k]
        flush(); parts = [x.strip() for x in b[1].split("/")] if k in ("q", "hq") else [b[1]]
        chunks.append({"t": "quote", "label": label, "html": "<br>".join(rich(x) for x in parts), "copy": "\n".join(plain(x) for x in parts)})
    elif k == "hr": flush()
    elif k == "place":
        flush(); chunks.append({"t": "place", "name": b[1]})
flush()
chunks.append({"t": "tags", "copy": m.TAGS})

def btn(label, data): return f'<button type="button" class="copy" data-copy="{html.escape(data)}">{label}</button>'
body = []
for i, c in enumerate(chunks):
    if c["t"] == "text":
        lines = "".join(f"<p>{h or '&nbsp;'}</p>" for _, h in c["lines"])
        body.append(f'<section class="blk text"><div class="bar"><span class="tag">글</span>{btn("글 복사", chr(10).join(c["copy"]))}</div><div class="prose">{lines}</div></section>')
    elif c["t"] == "quote":
        body.append(f'<section class="blk quote"><div class="bar"><span class="tag">{c["label"]}</span>{btn("복사", c["copy"])}</div><div class="qt">{c["html"]}</div></section>')
    elif c["t"] == "img":
        figs = "".join(f'<figure><img src="p/{f}" alt="사진 {c["first"]+j}" loading="lazy"><figcaption><span>사진 {c["first"]+j}</span><button type="button" class="save" data-file="p/{f}" hidden>저장</button></figcaption></figure>' for j, f in enumerate(c["files"]))
        lab = f'사진 {c["first"]}' + (f'~{c["first"]+len(c["files"])-1} · 묶음(콜라주)' if len(c["files"]) > 1 else "")
        body.append(f'<section class="blk imgs"><div class="bar"><span class="tag">{lab}</span></div><div class="grid n{min(len(c["files"]),2)}">{figs}</div></section>')
    elif c["t"] == "ad":
        body.append('<section class="blk note"><b>광고 링크 자리</b><p>체험단 URL을 맨 위에 붙여 넣어 주세요.</p></section>')
    elif c["t"] == "place":
        body.append(f'<section class="blk note"><b>장소 지도</b><p>앱에서 <b>장소</b> 버튼 → “{html.escape(c["name"])}” 검색 → 추가</p>{btn("가게 이름 복사", c["name"])}</section>')
    elif c["t"] == "tags":
        body.append(f'<section class="blk text"><div class="bar"><span class="tag">해시태그</span>{btn("태그 복사", c["copy"])}</div><div class="prose"><p class="tags">{html.escape(c["copy"])}</p></div></section>')

TITLE = FIX(m.TITLE)
page = open(Path(__file__).with_name("helper_template.html")).read()
page = page.replace("{{STORE}}", html.escape(getattr(m, "STORE", "") or TITLE.split("]")[0].split()[-1])).replace("{{TITLE}}", html.escape(TITLE)).replace("{{TITLE_ATTR}}", html.escape(TITLE)).replace("{{N_IMG}}", str(n_img)).replace("{{BODY}}", "\n".join(body))
(OUT / "index.html").write_text(page)
print("ok", OUT / "index.html", "사진", n_img, "덩어리", len(chunks))
