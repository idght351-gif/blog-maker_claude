"""초안(build_*.py) → 네이버 에디터 입력 순서표(spec3.json).
STYLE.md 5-0 사용자 서식 지시를 적용한다.
사용법: python3 make_spec3.py <build_xxx.py> <업로드 사진 폴더> <출력 json>
"""
import html, importlib.util, json, re, sys
from pathlib import Path

spec_ = importlib.util.spec_from_file_location("post", sys.argv[1])
m = importlib.util.module_from_spec(spec_); spec_.loader.exec_module(m)
UP, OUT = Path(sys.argv[2]), Path(sys.argv[3])
COL = {"r": "#f12f22", "p": "#f02c8c", "g": "#00a350", "bl": "#0076c8", "o": "#ff9c23"}
EMPTY = "<p><br></p>"
QUOTE = {"q": 1, "bubble": 3, "h": 4}   # 인용구 스타일 번호 (4 = 밑줄 인용구)


def rich(t):
    out, pos = [], 0
    for mm in m.INLINE.finditer(t):
        out.append(html.escape(t[pos:mm.start()])); k, s = mm.group(1), html.escape(mm.group(2))
        out.append({"B": f"<b>{s}</b>", "u": f"<u>{s}</u>", "i": f"<i>{s}</i>",
                    "y": f'<span style="background-color:#f4d400">{s}</span>'}.get(k) or f'<span style="color:{COL[k]}">{s}</span>')
        pos = mm.end()
    out.append(html.escape(t[pos:]))
    return "".join(out)


def sentences(t):
    """문장 끝(. ! ?) 뒤 공백에서 나눈다. [[..]] 서식 안에서는 나누지 않고, 바로 뒤가 이모지면 이모지까지 한 문장."""
    out, cur, depth, i = [], "", 0, 0
    while i < len(t):
        if t.startswith("[[", i): depth += 1; cur += "[["; i += 2; continue
        if t.startswith("]]", i): depth -= 1; cur += "]]"; i += 2; continue
        ch = t[i]; cur += ch; i += 1
        if depth == 0 and ch in ".!?" and i < len(t) and t[i] == " ":
            # 뒤따르는 이모지·닫는 따옴표·물결은 같은 문장에 붙임
            j = i
            while j < len(t) and (t[j] == " " or ord(t[j]) > 0x2500 and not ("가" <= t[j] <= "힣")):
                j += 1
            nxt = t[i:j]
            if nxt.strip():
                cur += nxt.rstrip(); i = j
            if i < len(t) and not t[i:].startswith("[["):
                out.append(cur.strip()); cur = ""
    if cur.strip(): out.append(cur.strip())
    return [s for s in out if s]


def para(inner, bold=False, size=15):
    if bold: inner = f"<b>{inner}</b>"
    return f'<p><span style="font-size:{size}px">{inner}</span></p>'


ops, lines = [{"t": "nds", "query": getattr(m, "NDS_QUERY", "")}], []   # 맨 위: 내돈내산 장소 인증 (영수증 인증 내역이 있을 때만)


def add_html(h, plain):
    if ops and ops[-1]["t"] == "html": ops[-1]["html"] += h
    else: ops.append({"t": "html", "html": h})
    lines.extend(x for x in plain if x.strip())


prev = None
for blk in m.B:
    k = blk[0]
    if k == "img":
        if prev == "p": add_html(EMPTY * 3, [])          # 설명 글 아래 빈 줄 3개 (사용자 지시)
        ops.append({"t": "img", "files": [str((UP / (f"IMG_{n}" if "." in n else f"IMG_{n}.jpg")).resolve()) for n in blk[1]]})
    elif k == "p":
        o = blk[2] if len(blk) > 2 else {}
        if o.get("c"): prev = k; continue
        rows = []
        for line in blk[1].split("\n"):
            rows += sentences(line) if not re.match(r"^\W", m.plain(line)[:1]) or len(m.plain(line)) > 40 else [line]
        add_html("".join(para(rich(r), o.get("b")) for r in rows), [m.plain(r) for r in rows])
        label = re.match(r"^(⭕|❌|🔄|🎯)", m.plain(blk[1])) and len(m.plain(blk[1])) < 30 and "\n" not in blk[1]
        if prev != "img" and not label: add_html(EMPTY, [])   # 좋았던 점 같은 제목 줄 바로 아래는 띄우지 않음
    elif k == "menu":
        # 메뉴 묶음: 카테고리(굵게) 바로 아래 메뉴들을 빈 줄 없이 붙이고, 묶음 뒤에만 빈 줄 1개 (사용자 지시 2026-11-12)
        rows = [(blk[1], True)] + [(it[0], bool(it[1].get("b"))) if isinstance(it, tuple) else (it, False) for it in blk[2]]
        add_html("".join(para(rich(t), b) for t, b in rows) + EMPTY, [m.plain(t) for t, _ in rows])
        k = "p"   # 다음 사진 앞 간격은 일반 문단과 같게
    elif k in QUOTE:
        txt = blk[1]
        if k == "h": add_html(EMPTY * 4, [])               # 소제목 앞 빈 줄 (1줄은 인용구가 차지)
        else: add_html(EMPTY * 2, [])
        parts = [x.strip() for x in txt.split("/")] if k == "q" else [txt]
        ops.append({"t": "quote", "style": QUOTE[k], "center": True,
                    "html": "".join(para(rich(x), k == "h", 19) for x in parts)})   # 인용구 글자 19
        lines.extend(m.plain(x) for x in parts)
    elif k == "place":
        add_html(EMPTY * 2, [])
        ops.append({"t": "place", "query": blk[1]})
    elif k == "hr":
        add_html(EMPTY * 2, [])
    prev = k
# 맨 아래 해시태그
add_html(EMPTY * 2 + para(html.escape(" ".join(m.TAGS.split()))), [" ".join(m.TAGS.split())])
title = m.TITLE
OUT.write_text(json.dumps({"title": title, "category": getattr(m, "CATEGORY", "먹보여행"), "ops": ops, "lines": lines,
                           "n_quote": sum(1 for o in ops if o["t"] == "quote"),
                           "n_img": sum(len(o["files"]) for o in ops if o["t"] == "img")}, ensure_ascii=False))
print(f"작업 {len(ops)}개, 확인할 줄 {len(lines)}, 인용구 {sum(1 for o in ops if o['t']=='quote')}, 사진 {sum(len(o['files']) for o in ops if o['t']=='img')}")
for l in lines[:12]: print("  ", l)
