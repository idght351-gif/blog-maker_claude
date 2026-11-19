"""PC 붙여넣기 페이지: 본문 전체(서식+사진)를 버튼 하나로 복사해 네이버 PC 에디터에 붙여 보는 페이지.
사용법: python3 scripts/make_pc_page.py drafts/build_<가게>.py drafts/<가게>_upload <출력.html>
사진은 data URI로 페이지에 넣는다 (페이지 16MB 한도 → 1000px로 줄임). GIF는 크기 때문에 자리 표시만 하고 따로 저장."""
import base64, html, importlib.util, io, sys
from pathlib import Path
from PIL import Image

spec = importlib.util.spec_from_file_location("post", sys.argv[1]); m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
UP, OUT = Path(sys.argv[2]), Path(sys.argv[3])
FIX = lambda t: t.replace("⭕", "👍").replace("❌", "💦")
COL = {"r": "#f12f22", "p": "#f02c8c", "g": "#00a350", "bl": "#0076c8", "o": "#ff9c23"}

def rich(t):
    out, pos = [], 0
    for x in m.INLINE.finditer(t):
        out.append(html.escape(t[pos:x.start()])); k, s = x.group(1), html.escape(x.group(2))
        out.append({"B": f"<b>{s}</b>", "i": f"<i>{s}</i>", "u": s, "y": f'<span style="background-color:#f4d400">{s}</span>'}.get(k) or f'<span style="color:{COL[k]}">{s}</span>')
        pos = x.end()
    out.append(html.escape(t[pos:])); return FIX("".join(out))

def para(inner, bold=False, align="left"):
    if bold: inner = f"<b>{inner}</b>"
    return f'<p style="text-align:{align};font-size:15px;margin:0">{inner or "<br>"}</p>'

def datauri(n):
    src = UP / (f"IMG_{n}" if "." in n else f"IMG_{n}.jpg")
    im = Image.open(src).convert("RGB"); im.thumbnail((1000, 6000))
    buf = io.BytesIO(); im.save(buf, "JPEG", quality=80)
    return "data:image/jpeg;base64," + base64.b64encode(buf.getvalue()).decode()

H, T, n_img, gifs = [], [], 0, []   # H: 붙여넣을 HTML, T: 글만(사진 자리 표시)
EMPTY = para("")
for b in m.B:
    k = b[0]
    if k == "img":
        first = n_img + 1; cells = []
        for n in b[1]:
            n_img += 1
            if n.endswith(".gif"):
                gifs.append((n_img, n)); cells.append(para(f"<b>[GIF {n_img} 여기에 넣기: IMG_{n}]</b>", align="center"))
            else:
                cells.append(f'<p style="text-align:center;margin:0"><img src="{datauri(n)}" alt="사진 {n_img}" style="max-width:100%;height:auto"></p>')
        H.append("".join(cells) + EMPTY)
        T.append(f"[사진 {first}]" if len(b[1]) == 1 else f"[사진 {first}~{n_img} 묶음]")
    elif k == "p":
        if "[광고 링크 필요]" in b[1]:
            H.append(para("<b>[여기에 체험단 광고 링크]</b>")); T.append("[여기에 체험단 광고 링크]"); continue
        bold = len(b) > 2 and b[2].get("b")
        for line in b[1].split("\n"):
            H.append(para(rich(line), bold)); T.append(FIX(m.plain(line)))
        H.append(EMPTY); T.append("")
    elif k == "menu":
        rows = [b[1]] + [it[0] if isinstance(it, tuple) else it for it in b[2]]
        for i, r in enumerate(rows):
            bold = i == 0 or (isinstance(b[2][i - 1], tuple) and b[2][i - 1][1].get("b"))
            H.append(para(rich(r), bold)); T.append(FIX(m.plain(r)))
        H.append(EMPTY); T.append("")
    elif k in ("h", "hq", "hl", "hb", "q", "bubble"):
        parts = [x.strip() for x in b[1].split("/")] if k in ("q", "hq") else [b[1]]
        inner = "".join(para(rich(x), k in ("h", "hb"), "center") for x in parts)
        if k == "hb":
            H.append(EMPTY * 3 + "".join(para(rich(x), True) for x in parts) + EMPTY)
        else:
            H.append(EMPTY * (3 if k.startswith("h") else 1) + f'<blockquote style="border-top:1px solid #333;border-bottom:1px solid #333;margin:8px 0;padding:8px">{inner}</blockquote>' + EMPTY)
        T += ["", *[FIX(m.plain(x)) for x in parts], ""]
    elif k == "place":
        H.append(para(f"<b>[장소 지도: {html.escape(b[1])} — 에디터의 '장소' 버튼으로 추가]</b>")); T.append(f"[장소 지도: {b[1]}]")
H.append(EMPTY + para(html.escape(m.TAGS))); T += ["", m.TAGS]

TITLE = FIX(m.TITLE); POST = "".join(H); TEXT = "\n".join(T)
gif_list = "".join(f'<li>GIF {i} (IMG_{n}) <button type="button" class="save" data-file="p/{i:02d}_IMG_{n}" hidden>저장</button></li>' for i, n in gifs)
tpl = open(Path(__file__).with_name("pc_template.html")).read()
store = getattr(m, "STORE", "") or TITLE.split("]")[0].split()[-1]
page = (tpl.replace("{{STORE}}", html.escape(store)).replace("{{TITLE}}", html.escape(TITLE)).replace("{{N_IMG}}", str(n_img))
        .replace("{{N_GIF}}", str(len(gifs))).replace("{{GIFS}}", gif_list).replace("{{POST}}", POST)
        .replace("{{TEXT_JSON}}", html.escape(__import__("json").dumps(TEXT, ensure_ascii=False))))
OUT.write_text(page)
print("ok", OUT, f"{OUT.stat().st_size/1e6:.1f}MB", "사진", n_img, "GIF", len(gifs))
