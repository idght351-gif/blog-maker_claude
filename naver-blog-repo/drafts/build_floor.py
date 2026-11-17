"""일쩜오플로어(1.5floor) 연남동 롤크레이프 (1번 폴더, 2026-11-16 포장)."""
import base64, html, io, re
from pathlib import Path
from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "drafts"
COLORS = {"r": "#f12f22", "p": "#f02c8c", "g": "#00a350", "bl": "#0076c8", "o": "#ff9c23"}
ALIGN = "left"
LINE = 22
PHOTOS = ROOT / "photos" / "floor" / "blur"
RESEARCH_DIR = str(ROOT / "data" / "research" / "floor")
CROP = {"9839": 0.4, "9841": 0.45, "9845": 0.55, "9846": 0.55, "9847": 0.55, "9848": 0.55,
        "9852": 0.5, "9857": 0.6, "9900": 0.5, "9901": 0.5, "9903": 0.5, "9904": 0.5, "9906": 0.5}
NOCROP = {"9840", "9842", "9844", "9854"}
ROTATE = {}
NDS_QUERY = ""   # 영수증 리뷰 후 add_nds.js로 넣음
CATEGORY = "먹보여행"
MAIN_KW = "연남동 롤크레이프"
SUB_KWS = ["일쩜오플로어", "연남동 디저트", "홍대 케이크", "후르츠롤", "체리쇼콜라롤"]

TITLE = "[연남동 롤크레이프] 일쩜오플로어 후르츠롤·체리쇼콜라롤 포장 후기 🍰"

B = [
    ("img", ["9904"]),
    ("p", "주말 오후, 단게 너무 당겨서 [[i:연남동 디저트 맛집]]을 찾아 나섰어요. 🚶‍♀️"),
    ("p", "SNS에서 단면 사진으로 유명한 연남동 롤크레이프 맛집 [[r:일쩜오플로어]] 포장 후기예요! 😊", {"b": 1}),
    ("p", "얇은 크레이프 안에 ✨생과일이 가득 박힌✨ 롤케이크라 자르는 순간부터 감탄이 나와요."),
    ("q", "후르츠롤 11,500원 / 체리쇼콜라롤 13,900원 / 홍대입구역 3번 출구 도보 10분 🍰"),
    ("bubble", "사진 미리보기📷"),
    ("img", ["9904", "9901", "9845", "9839"]),

    ("h", "📍 연남동 롤크레이프 일쩜오플로어 위치 & 영업정보"),
    ("img", ["9839"]),
    ("p", "동교로 큰길에서 조금 들어가면 노란 계단이 있는 건물이 보여요. 매장은 [[B:이름처럼 1.5층]]에 있어요. 😆"),
    ("img", ["9841"]),
    ("p", "계단 옆 기둥에 노란 'Everyday 1.5floor' 포스터가 붙어 있어서 금방 찾았어요."),
    ("p", "연남동 디저트 카페 찾는 분들을 위해 방문 전에 알아두시면 좋은 정보부터 정리해 드릴게요!"),
    ("p", "🏠 상호명: 일쩜오플로어 (1.5floor)", {"b": 1}),
    ("p", "🗺 주소: 서울 마포구 동교로34길 21 2층", {"b": 1}),
    ("p", "🚇 대중교통: 홍대입구역 3번 출구에서 연남동 방향으로 걸어서 약 10분", {"b": 1}),
    ("p", "⏰ 영업시간: 13:00 ~ 21:00 (디저트 소진 시 마감)", {"b": 1}),
    ("p", "📅 휴무: [[r:매달 유동적]] (인스타그램 공지 확인)", {"b": 1}),
    ("p", "🚗 주차 정보: 전용 주차 불가", {"b": 1}),
    ("img", ["9840"]),
    ("p", "입구에는 카페 이용 안내문이 귀여운 캐릭터와 함께 붙어 있어요. 영업시간과 웨이팅 방법이 한눈에 정리되어 있어요."),
    ("img", ["9843"]),
    ("p", "모든 디자인은 직접 개발한 것이라 무단 도용을 금지한다는 안내문도 있어요. 그만큼 연남동 롤크레이프 원조라는 자부심이 느껴졌어요. ✨"),

    ("h", "🍰 일쩜오플로어 롤크레이프 라인업 & 가격"),
    ("img", ["9845", "9846"]),
    ("p", "쇼케이스 안에 롤크레이프가 종류별로 쭉 놓여 있어요. 하나하나 체크무늬 포장지에 싸여 있어서 [[g:선물하기에도 예뻐요.]] 🎁"),
    ("img", ["9847", "9848"]),
    ("p", "바나나 푸딩 롤, 얼그레이 무화과 롤처럼 계절마다 바뀌는 메뉴도 있어요."),
    ("img", ["9852"]),
    ("p", "제가 고른 [[p:후르츠롤]]은 위에 생크림과 과일이 소복하게 올라가 있었어요.", {"b": 1}),
    ("img", ["9849"]),
    ("p", "윗칸에는 일쩜오플로어의 또 다른 시그니처인 [[y:뚱카롱]]이 있어요."),
    ("img", ["9850"]),
    ("p", "필링이 두툼하게 들어간 뚱카롱이 알록달록 줄지어 있어서 구경하는 재미가 있어요. 🌈"),
    ("menu", "🍰 [[y:롤크레이프]] (방문 당시 기준)", [
        ("[[p:후르츠롤: 11,500원]]", {"b": 1}),
        ("[[p:체리쇼콜라롤: 13,900원]]", {"b": 1}),
        "바나나 푸딩 롤: 12,500원", "얼그레이 무화과 롤: 12,900원",
    ]),
    ("menu", "🍪 [[y:뚱카롱]]", [
        "피스타치오 라즈베리 · 리츠초코 · 흑임자 경단 · 블루베리 치즈: 각 3,500원",
    ]),
    ("img", ["9844"]),
    ("menu", "☕ [[y:음료]] (HOT / ICE)", [
        "아메리카노: 4,500원 / 5,000원", "카페라떼: 5,300원 / 5,800원",
        "생 레몬 에이드 · 제주한라봉 에이드: 각 6,800원", "얼그레이 밀크티: 5,800원",
    ]),
    ("img", ["9854"]),
    ("p", "롤크레이프는 [[r:한정 수량]]이라 메뉴별로 1인 1개씩만 살 수 있어요."),

    ("h", "📦 포장 꿀팁"),
    ("img", ["9842"]),
    ("p", "포장 안내문을 보면, 포장 시간이 1시간 넘게 걸리면 보냉백을 권장한다고 적혀 있어요."),
    ("p", "선물 포장은 롤 1개당 1,000원 추가이고, 6개·9개·12개 세트 포장도 가능해요. 🎀"),
    ("img", ["9857"]),
    ("p", "저는 두 개를 포장했는데 일쩜오플로어 캐릭터가 그려진 [[B:귀여운 상자]]에 담아주셨어요."),

    ("h", "😋 연남동 롤크레이프 솔직 후기"),
    ("p", "오늘 주문한 메뉴는 [[p:후르츠롤]]과 [[p:체리쇼콜라롤]]이에요! 🍰", {"b": 1}),
    ("img", ["9903"]),
    ("p", "집에 와서 꺼낸 후르츠롤! 귤, 청포도, 딸기가 위에 올라가 있어서 [[y:색감부터 화사했어요.]] 🍓"),
    ("img", ["9905.gif"]),
    ("p", "반으로 자르니 딸기, 키위, 청포도, 망고, 용과까지 ✨과일 단면이 꽉 차 있어요!✨", {"b": 1}),
    ("img", ["9904"]),
    ("p", "크레이프가 얇아서 과일 맛이 그대로 느껴지고, 생크림은 많이 달지 않아서 깔끔했어요."),
    ("img", ["9906"]),
    ("p", "포크로 크게 떠서 한 입 먹으니 상큼한 과일과 부드러운 크림이 같이 들어와서 계속 손이 갔어요. 😋"),
    ("img", ["9900"]),
    ("p", "다음은 [[p:체리쇼콜라롤]]! 위에 체리 두 알이 콕 올라가 있어서 비주얼이 정말 고급스러워요. 🍒", {"b": 1}),
    ("img", ["9902.gif"]),
    ("p", "단면에는 체리가 송송 박혀 있고, 초코 크림이 겹겹이 들어가 있어요."),
    ("img", ["9901"]),
    ("p", "초코 크림은 [[r:진하지만 텁텁하지 않고]], 체리가 새콤하게 맛을 잡아줘서 느끼하지 않았어요."),
    ("p", "커피랑 같이 먹으니 딱 블랙포레스트 케이크 같은 맛이었어요. ☕"),
    ("p", "초코 크레이프 사이사이에 초콜릿 칩도 들어 있어서 씹는 재미가 있었어요. 🍫"),
    ("p", "두 가지 중 하나만 고르라면 상큼한 걸 좋아하면 후르츠롤, 진한 초코를 좋아하면 체리쇼콜라롤을 추천해요."),
    ("p", "크기가 꽤 커서 하나를 둘이 나눠 먹어도 충분했어요."),
    ("p", "연남동 롤크레이프 중에서도 과일 양이 정말 넉넉한 편이라, 한 조각만 먹어도 과일을 한 접시 먹은 느낌이었어요. 🍇"),
    ("p", "냉장고에 넣어 두었다가 다음 날 먹어도 크레이프가 눅눅해지지 않고 크림도 그대로였어요."),
    ("p", "다만 과일이 많이 들어간 만큼 자를 때 모양이 무너지기 쉬워서, 칼을 따뜻한 물에 한 번 담갔다가 자르면 단면이 훨씬 예쁘게 나와요. 🔪"),

    ("h", "💡 일쩜오플로어 방문 꿀팁"),
    ("p", "직접 가보고 정리한 팁이에요."),
    ("p", "1️⃣ 휴무일이 매달 바뀌니까 방문 전에 인스타그램 공지를 꼭 확인하세요."),
    ("p", "2️⃣ 인기 메뉴는 금방 품절되니까 오픈 시간 즈음 가는 게 좋아요."),
    ("p", "3️⃣ 롤크레이프는 메뉴별로 1인 1개만 살 수 있어요."),
    ("p", "4️⃣ 포장해서 1시간 이상 이동한다면 보냉백을 꼭 챙기세요."),
    ("p", "5️⃣ 매장에서 먹을 때는 1인 1음료 주문이 필요해요."),

    ("hr",),
    ("h", "📋 후기 종합"),
    ("p", "⭕ 좋았던 점", {"b": 1}),
    ("p", "[[bl:✨ 생과일이 꽉 찬 단면이라 비주얼이 예뻐요.]]\n[[bl:✨ 크림이 많이 달지 않아서 부담 없이 먹을 수 있어요.]]\n[[bl:✨ 체리쇼콜라롤은 진한 초코와 체리 조합이 좋아요.]]\n[[bl:✨ 포장 상자가 귀여워서 선물하기 좋아요.]]"),
    ("p", "❌ 아쉬웠던 점", {"b": 1}),
    ("p", "[[o:💵 롤 하나에 1만 원이 넘어서 가격대가 있는 편이에요.]]\n[[o:📅 휴무일이 유동적이라 미리 확인해야 해요.]]"),
    ("p", "🔄 재방문 의사: 🙆‍♀️🙆‍♀️🙆‍♀️🙆‍♀️", {"b": 1}),
    ("p", "👍 다음엔 얼그레이 무화과 롤과 뚱카롱도 먹어볼 거예요!"),
    ("p", "🎯 추천대상", {"b": 1}),
    ("p", "🧡 연남동 디저트 카페를 찾으시는 분들\n🧡 생과일 가득한 홍대 케이크를 좋아하시는 분들\n🧡 예쁜 디저트 선물을 찾으시는 분들"),
    ("p", "🌈직접 먹어보고 느낀 그대로 솔직하게 작성한 연남동 롤크레이프 일쩜오플로어 후기입니다.", {"b": 1}),
    ("place", "일쩜오플로어", "동교로34길"),
]

TAGS = "#연남동롤크레이프 #일쩜오플로어 #1점5플로어 #연남동디저트 #연남동카페 #홍대케이크 #홍대디저트 #연남동케이크 #롤크레이프 #후르츠롤 #체리쇼콜라롤 #과일케이크 #크레이프케이크 #뚱카롱 #연남동맛집 #홍대카페 #마포구카페 #케이크맛집 #디저트맛집 #연남동데이트 #과일롤케이크 #생과일케이크 #홍대입구역카페 #케이크포장 #디저트선물"

INLINE = re.compile(r"\[\[(r|p|y|g|bl|o|B|u|i):(.+?)\]\]", re.S)
EMO = re.compile(r'(?:[\U0001F300-\U0001FAFF☀-➿⭐⭕⌚-⏿](?:️)?(?:‍[\U0001F300-\U0001FAFF☀-➿](?:️)?)*)')


def plain(t):
    return INLINE.sub(lambda m: m.group(2), t)


def load(n):
    im = Image.open(PHOTOS / (f"IMG_{n}" if "." in n else f"IMG_{n}.jpg")).convert("RGB")
    if n in ROTATE:   # 내용이 옆으로 누운 사진(메뉴판 등)은 자르지 않고 사진 자체를 돌림 (사용자 지시 2026-11-13)
        return im.rotate(ROTATE[n], expand=True)
    w, h = im.size
    if h > w and n not in NOCROP:  # 세로 사진 → 가로 4:3
        nh = int(w * 3 / 4)
        top = max(0, min(h - nh, int(CROP.get(n, 0.5) * h - nh / 2)))
        im = im.crop((0, top, w, top + nh))
    return im


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
        elif k == "h":
            parts.append(f'<div class="h">{rich(blk[1])}</div>')
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
    return f"""<title>일쩜오플로어 초안</title>
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
<div class="meta">은똥잉 · 2026. 11. 13. 방문</div>
{chr(10).join(parts)}
<div class="tags">{tags}</div>
</div>"""


def build_md():
    out = [f"# {TITLE}", ""]
    for blk in B:
        k = blk[0]
        if k == "img":
            out.append(" ".join(f"![IMG_{n}](../photos/floor/blur/IMG_{n}.jpg)" for n in blk[1]))
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
        elif k == "h":
            out.append(f"### {blk[1]}")
        elif k == "hr":
            out.append("---")
        elif k == "place":
            out.append(f"[장소 지도: {blk[1]}]")
        out.append("")
    out.append(TAGS)
    return "\n".join(out)


if __name__ == "__main__":
    (OUT / "floor.html").write_text(build_html())
    (OUT / "floor.md").write_text(build_md())
    lines = [l for b in B if b[0] == "p" for l in plain(b[1]).split("\n")]
    print("ok", (OUT / "floor.html").stat().st_size // 1024, "KB",
          "| emoji", sum(len(EMO.findall(l)) for l in lines),
          "| lines w/ emoji %.0f%%" % (100 * sum(1 for l in lines if EMO.search(l)) / len(lines)),
          "| chars", sum(len(plain(b[1])) for b in B if b[0] == "p"))
