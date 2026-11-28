"""박가네들깨칼국수 (7번 폴더, 11/14 토 점심, 남편과, 세 번째 방문). 내돈내산(영수증 리뷰 등록함, 카드는 사용자가 직접). 템플릿 T4.
사진 자르지 않음, 장소 지도 없음 (사용자 지시 2026-11-28)."""
import base64, html, io, re
from pathlib import Path
from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "drafts"
COLORS = {"r": "#f12f22", "p": "#f02c8c", "g": "#00a350", "bl": "#0076c8", "o": "#ff9c23"}
ALIGN = "left"
LINE = 22
PHOTOS = ROOT / "photos" / "parkga" / "blur"
RESEARCH_DIR = str(ROOT / "data" / "research" / "parkga")
CROP, NOCROP, ROTATE = {}, set(), {}
NDS_QUERY = ""
CATEGORY = "먹보여행"
NO_PLACE = True
TEMPLATE_ID = "T4"
LENGTH = "짧게"
STORE = "박가네들깨칼국수"
MEMO = {"동행": "남편과", "계기": "저번에 우연히 갔다가 지금 3번째 가는 중, 너무 맛있어서. 차 타고 30분 거리", "최고": ["들깨칼국수"],
        "들깨": "국물이 진하고 고소함, 자극적이지 않고 속 편함", "바지락": "바지락이 푸짐함", "셀프": "보리밥 비빔이 별미, 김치가 맛있음",
        "가격": "이 맛이면 만족", "붐빔": "거의 만석(토 12:30)", "분위기": "동네 맛집 느낌", "아쉬움": "주차", "재방문": "무조건, 또 들깨칼국수",
        "한마디": "30분 걸려도 갈 만한 집"}
MAIN_KW = "오목교역 맛집"
SUB_KWS = ["박가네들깨칼국수", "목동 들깨칼국수", "신정동 칼국수"]

TITLE = "[오목교역 맛집 박가네들깨칼국수] 차로 30분 걸려도 또 가는 들깨칼국수! 주차 팁"

B = [
    ("img", ["9768"]),
    ("p", "차로 30분이나 걸리는데 벌써 세 번째 찾아간 칼국수집이 있답니다! 🚗 바로 오목교역 맛집으로 소문난 [[r:박가네들깨칼국수]]랍니다. 🍜", {"keep": 1}),
    ("p", "안녕하세요, 은똥잉이에요! 🙋‍♀️ 처음엔 정말 우연히 들어갔는데 들깨칼국수 맛에 반해서, 그 뒤로 남편이랑 생각날 때마다 달려가는 곳이죠. 💛 토요일 점심에도 어김없이 다녀왔죠! 😋", {"keep": 1}),

    ("hl", "📍 오목교역 맛집 박가네들깨칼국수 위치·영업시간"),
    ("img", ["9740", "9741"]),
    ("p", "오목교역 6번 출구에서 걸어서 5~7분 정도 가면 신정동 골목에 노란 간판이 보여요. 🚶‍♀️ 간판에 들깨칼국수랑 바지락칼국수가 크게 적혀 있어서 처음 가도 찾기 쉽답니다. 신정동 칼국수 집 중에선 여기가 제 원픽이랍니다! 👍", {"keep": 1}),
    ("img", ["9742", "9743"]),
    ("p", "창가에는 칼국수 사진이 큼직하게 붙어 있고, 입구 옆에는 양천구 [[B:모범음식점]] 표지판도 걸려 있더라고요. 🏅", {"keep": 1}),
    ("img", ["9744", "9745"]),
    ("p", "🏠 상호: 박가네들깨칼국수", {"b": 1}),
    ("p", "🗺 주소: 서울 양천구 신정동 117-20 1층 (영수증 기준)", {"b": 1}),
    ("p", "🚇 위치: 오목교역 6번 출구에서 걸어서 5~7분", {"b": 1}),
    ("p", "⏰ 영업: 11:00~21:00 (라스트오더 20:30 / 11월 방문 기준, 방문 전 확인 추천)", {"b": 1}),
    ("p", "📅 휴무: [[r:매주 월요일]]", {"b": 1}),
    ("p", "🚗 주차: 매장 앞 주차 공간이 있긴 한데 넉넉하진 않아요", {"b": 1}),
    ("p", "토요일 12시 반쯤 갔더니 매장이 [[B:거의 만석]]이었어요. 😲 오목교역 맛집답게 주말 점심엔 사람이 정말 많더라고요. 주말에 가실 거면 조금 일찍 가시는 걸 추천해요! ⏰", {"keep": 1}),

    ("hl", "🏪 정겨운 동네 맛집 분위기"),
    ("img", ["9747", "9748"]),
    ("img", ["9749f"]),
    ("p", "안은 원목 칸막이 테이블이 쭉 놓인 넓은 식당이더라고요. 🪑 화려하진 않아도 딱 [[B:동네 맛집]] 느낌이라 괜히 마음이 편해지더라고요. 점심시간이라 테이블이 거의 다 차 있었답니다. 👀", {"keep": 1}),
    ("img", ["9746", "9778"]),
    ("p", "벽에는 만두전골 포스터랑 포장 가능 안내도 붙어 있더라고요. 🥟 포장도 된다니 집에서 먹고 싶을 때 딱이겠죠?", {"keep": 1}),
    ("img", ["9777", "9779"]),
    ("img", ["9750"]),
    ("p", "테이블마다 양념통이 놓여 있어서 취향껏 넣어 먹으면 된답니다. 🧂", {"keep": 1}),

    ("hl", "💵 박가네 들깨칼국수 메뉴 & 가격"),
    ("img", ["9751", "9752"]),
    ("img", ["9756"]),
    ("menu", "🍜 [[y:칼국수·수제비]]", [("[[p:들깨칼국수: 11,000원]]", {"b": 1}), "들깨수제비: 11,000원", "들깨칼제비: 22,000원 (2인분 이상)", ("[[p:바지락칼국수: 10,000원]]", {"b": 1}), "얼큰수제비: 10,000원", "보리비빔밥: 9,000원"]),
    ("menu", "🥟 [[y:만두·별미]]", ["만두전골: 1인분 15,000원 (2인분부터)", "만두 6알: 10,000원 / 전병 4줄: 12,000원", "팥칼국수: 11,000원 / 팥옹심이: 12,000원"]),
    ("menu", "👫 [[y:2인 세트]]", ["들깨칼국수 2 + 만두 2알: 25,000원", "바지락칼국수 2 + 만두 2알: 23,000원"]),
    ("p", "저희는 들깨칼국수랑 바지락칼국수를 하나씩 시켜서 총 21,000원이 나왔답니다. 칼국수 한 그릇에 만 원 넘는 게 싸다고는 못 하지만, 이 맛이면 저는 충분히 만족한답니다! 💳", {"keep": 1}),

    ("hl", "😋 오늘 주문한 메뉴 솔직 후기"),
    ("p", "오늘 주문한 메뉴는 [[p:들깨칼국수, 바지락칼국수]]예요!", {"b": 1}),
    ("h", "1. 셀프 보리밥 & 김치"),
    ("img", ["9753", "9754"]),
    ("p", "칼국수가 나오기 전에 셀프 코너부터 들러요. 보리밥이랑 김치, 열무김치를 원하는 만큼 덜어 올 수 있답니다. 🙌 세 번째 오니까 이제 자리에 앉자마자 남편이랑 셀프 코너로 직행하게 되더라고요.", {"keep": 1}),
    ("img", ["9755", "9776"]),
    ("img", ["9759", "9760"]),
    ("p", "김치가 진짜 맛있어서 칼국수 나오기 전부터 손이 계속 가더라고요. 😆 칼국수엔 역시 김치죠! 🥬", {"keep": 1}),
    ("img", ["9761", "9762"]),
    ("img", ["9763", "9764"]),
    ("p", "보리밥에 열무김치를 올리고 고추장이랑 참기름을 쭉 둘러서 쓱쓱 비벼 먹었죠. 🥄 이 보리밥 비빔이 완전 별미랍니다! 칼국수 먹기 전에 입맛을 확 살려 준답니다. 🍚", {"keep": 1}),

    ("h", "2. 들깨칼국수 (11,000원)"),
    ("img", ["9765", "9767"]),
    ("p", "드디어 나온 들깨칼국수! 하얀 그릇에 뽀얀 들깨 국물이 가득 담겨 나와요. 🥣 목동 들깨칼국수 찾으시는 분들은 이 비주얼 보고 바로 오셔야 해요!", {"keep": 1}),
    ("img", ["9769.gif"]),
    ("p", "한 숟갈 떠먹자마자 ✨국물이 진하고 고소해서✨ 역시 이 맛이지 싶더라고요. 😌", {"b": 1}),
    ("img", ["9770.gif"]),
    ("p", "면을 들어 올리면 들깨 국물이 면에 착 감겨서 같이 올라와요. 그런데도 자극적이지 않고 [[r:속이 편해서]] 먹고 나서도 부담이 없더라고요. 😊", {"keep": 1}),
    ("img", ["9768"]),
    ("p", "제가 차로 30분을 달려서라도 또 오는 건 바로 이 들깨칼국수 때문이에요. 세 번째 먹는데도 여전히 맛있었답니다! 🤤 진한 들깨 국물이 부담스러울까 걱정하시는 분들도 계실 텐데, 여기는 고소함은 진하면서 맛이 순해서 끝까지 술술 넘어가요.", {"keep": 1}),

    ("h", "3. 바지락칼국수 (10,000원)"),
    ("img", ["9771", "9772"]),
    ("p", "바지락칼국수도 하나 시켰답니다. 🍜 맑은 국물에 애호박이랑 바지락이 듬뿍 들어가 있네요. 🦪", {"keep": 1}),
    ("img", ["9774f", "9773"]),
    ("img", ["9775.gif"]),
    ("p", "바지락이 정말 [[B:푸짐하게]] 들어 있었어요. 😍 들깨칼국수가 고소한 맛이라면 바지락은 깔끔한 맛이라 둘이 하나씩 시켜서 나눠 먹기 딱 좋답니다! 👫", {"keep": 1}),

    ("hr",),
    ("hl", "📋 박가네들깨칼국수 총평"),
    ("p", "[[bl:- 좋았던 점: 진하고 고소한데 자극적이지 않아 속 편한 들깨칼국수, 푸짐한 바지락, 별미인 셀프 보리밥 비빔과 맛있는 김치까지!]]"),
    ("p", "[[o:- 아쉬웠던 점: 주차가 넉넉하지 않아서 주말엔 조금 신경 써야 해요.]]"),
    ("p", "- 재방문의사: 무조건! 다음에도 또 들깨칼국수 먹으러 갈 거랍니다. 🙆‍♀️🙆‍♀️🙆‍♀️🙆‍♀️"),
    ("p", "오목교역 맛집, 그중에서도 들깨칼국수 맛집 찾으신다면 여기 꼭 가 보세요. 저한테는 정말 [[r:30분 걸려도 갈 만한 집]]이랍니다! 🫶", {"keep": 1}),
]

TAGS = "#오목교역맛집 #박가네들깨칼국수 #목동들깨칼국수 #신정동칼국수 #오목교칼국수 #목동맛집 #신정동맛집 #들깨칼국수 #바지락칼국수 #보리밥 #양천구맛집 #목동칼국수맛집 #칼국수맛집 #오목교역점심 #주말점심"

INLINE = re.compile(r"\[\[(r|p|y|g|bl|o|B|u|i):(.+?)\]\]", re.S)
EMO = re.compile(r'(?:[\U0001F300-\U0001FAFF☀-➿⭐⭕⌚-⏿](?:️)?(?:‍[\U0001F300-\U0001FAFF☀-➿](?:️)?)*)')


def plain(t):
    return INLINE.sub(lambda m: m.group(2), t)


def load(n):
    im = Image.open(PHOTOS / (f"IMG_{n}" if "." in n else f"IMG_{n}.jpg")).convert("RGB")
    if n in ROTATE:   # 내용이 옆으로 누운 사진(메뉴판 등)은 자르지 않고 사진 자체를 돌림 (사용자 지시 2026-11-13)
        return im.rotate(ROTATE[n], expand=True)
    return im   # 2026-11-28 사용자 지시: 사진은 자르지 않음 (옆으로 누운 사진만 ROTATE로 세움)


def img_b64(n, w):
    im = load(n)
    im.thumbnail((w, w))
    buf = io.BytesIO(); im.save(buf, "JPEG", quality=78)
    return base64.b64encode(buf.getvalue()).decode()


def rich(t):
    out, pos = [], 0
    for m in INLINE.finditer(t):
        out.append(html.escape(t[pos:m.start()]))
        k, s = m.group(1), html.escape(m.group(2))
        if k == "B": out.append(f"<b>{s}</b>")
        elif k == "u": out.append(f"<u>{s}</u>")
        elif k == "i": out.append(f"<i>{s}</i>")
        elif k == "y": out.append(f'<span class="hly">{s}</span>')
        else: out.append(f'<span style="color:{COLORS[k]}">{s}</span>')
        pos = m.end()
    out.append(html.escape(t[pos:]))
    return "".join(out).replace("\n", "<br>")


def wrap(t, n):
    """가운데 정렬용 줄바꿈: 띄어쓰기 단위로 n자 안팎에서 끊는다. [[..]] 서식 구간은 쪼개지 않는다."""
    if "\n" in t or len(plain(t)) <= n:
        return t
    toks = re.findall(r"\[\[[^\]]+\]\]\S*|\S+", t)
    out, cur = [], ""
    for tok in toks:
        cand = (cur + " " + tok).strip()
        if cur and len(plain(cand)) > n:
            out.append(cur); cur = tok
        else:
            cur = cand
    if cur: out.append(cur)
    return "\n".join(out)


def build_html():
    parts = []
    for blk in B:
        k = blk[0]
        if k == "img":
            ns = blk[1]
            w = 900 if len(ns) == 1 else 600
            imgs = "".join(f'<img src="data:image/jpeg;base64,{img_b64(n, w)}" alt="IMG_{n}">' for n in ns)
            parts.append(f'<div class="ph n{len(ns)}">{imgs}</div>')
        elif k == "p":
            o = blk[2] if len(blk) > 2 else {}
            cls = ["p"] + (["b"] if o.get("b") else []) + ([f"fs{o['fs']}"] if o.get("fs") else []) + (["chk"] if o.get("c") else [])
            note = f'<span class="note">확인: {html.escape(o["c"])}</span>' if o.get("c") else ""
            txt = blk[1]
            if ALIGN == "center":
                cls.append("center")
                if not o.get("fs") and not re.match(r"^\W", plain(txt)[:1]):
                    txt = wrap(txt, LINE)
            parts.append(f'<p class="{" ".join(cls)}">{rich(txt)}{note}</p>')
        elif k == "menu":
            rows = [f'<b>{rich(blk[1])}</b>'] + [
                (f'<b>{rich(it[0])}</b>' if it[1].get("b") else rich(it[0])) if isinstance(it, tuple) else rich(it)
                for it in blk[2]]
            parts.append(f'<p class="p">{"<br>".join(rows)}</p>')
        elif k == "q":
            parts.append(f'<div class="q"><span class="mk">❝</span>{"<br>".join(rich(x.strip()) for x in blk[1].split("/"))}<span class="mk">❞</span></div>')
        elif k == "bubble":
            parts.append(f'<div class="bubble">{rich(blk[1])}</div>')
        elif k in ("h", "hl"):
            parts.append(f'<div class="h">{rich(blk[1])}</div>')
        elif k == "hq":
            parts.append(f'<div class="q"><span class="mk">❝</span>{"<br>".join(rich(x.strip()) for x in blk[1].split("/"))}<span class="mk">❞</span></div>')
        elif k == "hb":
            parts.append(f'<p class="p b" style="margin-top:36px">{rich(blk[1])}</p>')
        elif k == "hr":
            parts.append('<hr>')
        elif k == "place":
            parts.append(f'<div class="place">📍 {html.escape(blk[1])} (네이버 장소 지도)</div>')
    tags = "".join(f'<span class="tag">{t}</span>' for t in TAGS.split())
    lines = [l for b in B if b[0] == "p" for l in plain(b[1]).split("\n")]
    n_emoji = sum(len(EMO.findall(l)) for l in lines)
    n_img = sum(len(b[1]) for b in B if b[0] == "img")
    n_chr = sum(len(plain(b[1])) for b in B if b[0] == "p")
    n_chk = sum(1 for b in B if b[0] == "p" and len(b) > 2 and b[2].get("c"))
    return f"""<title>박가네 초안</title>
<meta name="claude:viewport-fit-sides" content="cover">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Gowun+Dodum&display=swap" rel="stylesheet">
<style>
/* 네이버 블로그 본문을 흉내 낸 한 장짜리 미리보기. 블로그와 같은 흰 배경 한 가지로 고정 */
:root{{--bg:#ffffff;--fg:#222222;--muted:#7a7f85;--line:#e6e8ea;--accent:#03c75a;--hl:#fff3b0;--hlnote:#8a5f00;--hly:#f4d400;--hlyfg:#222222;color-scheme:light}}
*{{box-sizing:border-box}}
body{{margin:0;background:var(--bg);color:var(--fg);font-family:'Gowun Dodum','Apple SD Gothic Neo','Malgun Gothic',sans-serif;font-size:16px;line-height:1.85}}
.wrap{{max-width:720px;margin:0 auto;padding-block:20px 60px;padding-left:max(16px,env(safe-area-inset-left,0px));padding-right:max(16px,env(safe-area-inset-right,0px))}}
.legend{{font-size:13px;color:var(--muted);border:1px solid var(--line);border-radius:10px;padding:10px 12px;margin-bottom:22px}}
.cat{{color:var(--accent);font-size:14px;margin-bottom:6px}}
h1{{font-size:22px;line-height:1.45;margin:0 0 10px;text-wrap:balance}}
.meta{{color:var(--muted);font-size:13px;border-bottom:1px solid var(--line);padding-bottom:16px;margin-bottom:24px}}
.p{{margin:0 0 14px;text-align:justify;word-break:keep-all}}
.b{{font-weight:700}}
.center{{text-align:center}}
.fs24{{font-size:21px;line-height:1.6}}
.fs19{{font-size:18px}}
.hly{{background:var(--hly);color:var(--hlyfg);padding:0 3px}}
.chk{{background:var(--hl);border-radius:4px;padding:2px 4px}}
.note{{display:block;font-size:12px;font-weight:400;color:var(--hlnote)}}
.ph{{display:grid;gap:4px;margin:22px 0 12px}}
.ph.n2,.ph.n4{{grid-template-columns:1fr 1fr}}.ph.n3{{grid-template-columns:1fr 1fr 1fr}}
.ph img{{width:100%;max-width:100%;height:auto;display:block;border-radius:2px}}
.ph.n2 img,.ph.n3 img,.ph.n4 img{{aspect-ratio:1;object-fit:cover}}
.q{{text-align:center;font-size:19px;font-weight:700;line-height:1.7;margin:30px 0;padding:6px 0}}
.q .mk{{display:block;font-size:34px;color:var(--muted);line-height:1}}
.bubble{{display:table;margin:26px auto 10px;padding:10px 22px;border:2px solid var(--fg);border-radius:22px;font-weight:700}}
.h{{font-size:18px;font-weight:700;margin:40px 0 18px;padding-bottom:8px;border-bottom:2px solid var(--fg);text-align:center}}
hr{{border:0;border-top:1px solid var(--line);margin:36px 0}}
.tags{{margin-top:28px;display:flex;flex-wrap:wrap;gap:6px}}
.tag{{color:var(--accent);font-size:14px}}
.place{{border:1px solid var(--line);border-radius:8px;padding:12px;margin:20px 0;color:var(--muted)}}
</style>
<div class="wrap">
<div class="legend">블로그에 올렸을 때 모습을 흉내 낸 미리보기입니다. 글자 색·크기·굵기는 실제 블로그에 적용할 서식 그대로입니다.<br>사진 {n_img}장 · 본문 약 {n_chr:,}자 · 이모지 {n_emoji}개 · 확인 필요 {n_chk}곳</div>
<div class="cat">먹보여행</div>
<h1>{html.escape(TITLE)}</h1>
<div class="meta">은똥잉 · 2026. 11. 14. 방문</div>
{chr(10).join(parts)}
<div class="tags">{tags}</div>
</div>"""


def build_md():
    out = [f"# {TITLE}", ""]
    for blk in B:
        k = blk[0]
        if k == "img":
            out.append(" ".join(f"![IMG_{n}](../photos/parkga/blur/IMG_{n}.jpg)" for n in blk[1]))
        elif k == "p":
            o = blk[2] if len(blk) > 2 else {}
            t = INLINE.sub(lambda m: f"**{m.group(2)}**" if m.group(1) == "B" else f"<{m.group(1)}>{m.group(2)}</{m.group(1)}>", blk[1]).replace("\n", "  \n")
            if o.get("b"): t = f"**{t}**"
            if o.get("fs"): t = f"[{o['fs']}] " + t
            if o.get("c"): t += f" *(확인: {o['c']})*"
            out.append(t)
        elif k == "menu":
            md = lambda s: INLINE.sub(lambda m: f"**{m.group(2)}**" if m.group(1) == "B" else f"<{m.group(1)}>{m.group(2)}</{m.group(1)}>", s)
            rows = [f"**{md(blk[1])}**"] + [
                (f"**{md(it[0])}**" if it[1].get("b") else md(it[0])) if isinstance(it, tuple) else md(it) for it in blk[2]]
            out.append("  \n".join(rows))
        elif k == "q":
            out.append("> ❝ " + " / ".join(x.strip() for x in blk[1].split("/")) + " ❞")
        elif k == "bubble":
            out.append(f"> 💬 {blk[1]}")
        elif k in ("h", "hq", "hl", "hb"):
            out.append(f"### {blk[1]}")
        elif k == "hr":
            out.append("---")
        elif k == "place":
            out.append(f"[장소 지도: {blk[1]}]")
        out.append("")
    out.append(TAGS)
    return "\n".join(out)


if __name__ == "__main__":
    (OUT / "parkga.html").write_text(build_html())
    (OUT / "parkga.md").write_text(build_md())
    lines = [l for b in B if b[0] == "p" for l in plain(b[1]).split("\n")]
    print("ok", (OUT / "parkga.html").stat().st_size // 1024, "KB",
          "| emoji", sum(len(EMO.findall(l)) for l in lines),
          "| lines w/ emoji %.0f%%" % (100 * sum(1 for l in lines if EMO.search(l)) / len(lines)),
          "| chars", sum(len(plain(b[1])) for b in B if b[0] == "p"))
