"""사진 자리 번호 원고 + '올릴순서' 파일 만들기 (사용자가 사진을 직접 넣는 방식, 2026-11-21).
사용법: python3 scripts/make_numbered.py drafts/build_<가게>.py <출력폴더> [동영상 원본 경로]
- 본문의 사진 자리를 위에서부터 [사진 1], [사진 2~4 묶음], [GIF 7], [동영상 9] 로 표시한 원고(원고.txt)
- 같은 번호로 모자이크·자르기 끝난 파일: 01_사진.jpg, 07_GIF.gif, 09_동영상.mov
- 사진첩이 찍은 시간 순으로 정렬하므로 각 파일의 '찍은 시간'을 1번부터 1분 간격으로 다시 적는다
- 동영상 자리는 본문의 '[여기에 동영상 넣기' 줄 위치. 원본 동영상 경로를 세 번째 인자로 준다"""
import datetime, html, importlib.util, json, shutil, subprocess, sys
from pathlib import Path
from PIL import Image

spec = importlib.util.spec_from_file_location("post", sys.argv[1]); m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
OUT = Path(sys.argv[2]); FILES = OUT / "올릴순서"; FILES.mkdir(parents=True, exist_ok=True)
VIDEO = Path(sys.argv[3]) if len(sys.argv) > 3 else None
BASE = (datetime.datetime.utcnow() + datetime.timedelta(hours=9) - datetime.timedelta(hours=3)).replace(second=0, microsecond=0)   # 한국 시각 기준 3시간 전부터 → 사진첩 최근 쪽에 1번부터 줄 섬
FIX = lambda t: t.replace("⭕", "👍").replace("❌", "💦")
stamp = lambda i: (BASE + datetime.timedelta(minutes=i)).strftime("%Y:%m:%d %H:%M:%S")

COL = {"r": "#f12f22", "p": "#f02c8c", "g": "#00a350", "bl": "#0076c8", "o": "#ff9c23"}
def rich(t):
    out, pos = [], 0
    for x in m.INLINE.finditer(t):
        out.append(html.escape(t[pos:x.start()])); k, v = x.group(1), html.escape(x.group(2))
        out.append({"B": f"<b>{v}</b>", "i": f"<i>{v}</i>", "u": v, "y": f'<span style="background-color:#f4d400">{v}</span>'}.get(k) or f'<span style="color:{COL[k]}">{v}</span>')
        pos = x.end()
    out.append(html.escape(t[pos:])); return FIX("".join(out))
P_ = lambda inner, bold=False, align="left": f'<p style="text-align:{align};font-size:15px;margin:0">{("<b>" + inner + "</b>") if (bold and inner) else (inner or "<br>")}</p>'
MARK = lambda t: P_(f'<span style="background-color:#fff1b8;color:#5a4500"><b>{html.escape(t)}</b></span>')
H = []
lines, made, n = [], [], 0
def jpg(src_n, i):
    im = m.load(src_n); im.thumbnail((1600, 1600) if src_n not in m.NOCROP else (1600, 8000))
    ex = Image.Exif(); ex[306] = stamp(i); ex[0x8769] = {36867: stamp(i), 36868: stamp(i)}
    out = FILES / f"{i:02d}_사진.jpg"; im.save(out, "JPEG", quality=90, exif=ex.tobytes()); return out.name

for b in m.B:
    k = b[0]
    if k == "img":
        first = n + 1
        for src in b[1]:
            n += 1
            if src.endswith(".gif"):
                out = FILES / f"{n:02d}_GIF.gif"; shutil.copy(m.PHOTOS / f"IMG_{src}", out); made.append(out.name); kind = "GIF"
            else:
                made.append(jpg(src, n)); kind = "사진"
        mk = f"[{kind} {n}]" if len(b[1]) == 1 else f"[사진 {first}~{n} 묶음]"
        lines += [mk, ""]; H += [MARK(mk), P_("")]
    elif k == "p":
        if "[여기에 동영상 넣기" in b[1]:
            n += 1; lines += [f"[동영상 {n}]", ""]; H += [MARK(f"[동영상 {n}]"), P_("")]
            if VIDEO:
                out = FILES / f"{n:02d}_동영상{VIDEO.suffix.lower()}"
                when = (BASE + datetime.timedelta(minutes=n) - datetime.timedelta(hours=9)).strftime("%Y-%m-%dT%H:%M:%S.000000Z")
                subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(VIDEO), "-c", "copy", "-map_metadata", "-1", "-metadata", f"creation_time={when}", str(out)], check=True)
                made.append(out.name)
            continue
        bold = len(b) > 2 and b[2].get("b")
        for line in b[1].split("\n"): lines.append(FIX(m.plain(line))); H.append(P_(rich(line), bold))
        lines.append(""); H.append(P_(""))
    elif k == "menu":
        lines += [FIX(m.plain(b[1]))] + [FIX(m.plain(it[0] if isinstance(it, tuple) else it)) for it in b[2]] + [""]
        H += [P_(rich(b[1]), True)] + [P_(rich(it[0]), bool(it[1].get("b"))) if isinstance(it, tuple) else P_(rich(it)) for it in b[2]] + [P_("")]
    elif k in ("h", "hq", "hl", "hb", "q", "bubble"):
        parts = [x.strip() for x in b[1].split("/")] if k in ("q", "hq") else [b[1]]
        lines += ["", "", *[FIX(m.plain(x)) for x in parts], ""]
        inner = "".join(P_(rich(x), k in ("h", "hb", "bubble"), "left" if k == "hb" else "center") for x in parts)
        H += [P_(""), P_(""), inner if k == "hb" else f'<blockquote style="border-top:1px solid #333;border-bottom:1px solid #333;margin:8px 0;padding:8px">{inner}</blockquote>', P_("")]
    elif k == "place":
        lines += [f"[장소 지도: {b[1]} — 앱의 '장소' 버튼으로 추가]", ""]; H += [MARK(f"[장소 지도: {b[1]} — 앱의 '장소' 버튼으로 추가]"), P_("")]
lines += ["", m.TAGS]; H += [P_(""), P_(html.escape(m.TAGS))]
text = "\n".join(lines).strip() + "\n"
(OUT / "원고.txt").write_text(FIX(m.TITLE) + "\n\n" + text)
tpl = (Path(__file__).with_name("numbered_template.html")).read_text()
page = tpl.replace("{{STORE}}", html.escape(getattr(m, "STORE", ""))).replace("{{TITLE}}", html.escape(FIX(m.TITLE))) \
          .replace("{{N}}", str(n)).replace("{{TEXT}}", html.escape(text)).replace("{{TEXT_JSON}}", html.escape(json.dumps(text, ensure_ascii=False))) \
          .replace("{{RICH}}", "".join(H)).replace("{{FILES}}", "".join(f"<li>{html.escape(f)}</li>" for f in made))
(OUT / "index.html").write_text(page)
print("자리", n, "파일", len(made), "→", FILES)
