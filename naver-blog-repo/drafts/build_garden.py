"""더 리버사이드 호텔 더가든키친 뷔페 (7번 폴더, 2026-07-31 평일 런치)."""
import base64, html, io, re
from pathlib import Path
from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "drafts"
COLORS = {"r": "#f12f22", "p": "#f02c8c", "g": "#00a350", "bl": "#0076c8", "o": "#ff9c23"}
ALIGN = "left"
LINE = 22
PHOTOS = ROOT / "photos" / "garden" / "blur"
RESEARCH_DIR = str(ROOT / "data" / "research" / "garden")
CROP = {"121846": 0.45, "121913": 0.5, "121935": 0.5, "122651": 0.55, "123035": 0.55, "123103": 0.5,
        "123141": 0.55, "123207": 0.5, "124055": 0.55, "124244": 0.5, "124448": 0.5, "130812": 0.5,
        "131137": 0.6, "132429": 0.45, "133457": 0.5, "133600": 0.5, "133947": 0.5, "134416": 0.45,
        "140059": 0.6, "140120": 0.6, "140153": 0.65, "140305": 0.6, "140531": 0.5, "123341": 0.6,
        "124048": 0.55, "130123": 0.5, "123159": 0.55}
NOCROP = set()
ROTATE = {}
NDS_QUERY = ""   # 영수증 리뷰 후 add_nds.js로 넣음
CATEGORY = "먹보여행"
MAIN_KW = "신사역 호텔뷔페"
SUB_KWS = ["더가든키친", "리버사이드호텔 뷔페", "서울 호텔뷔페", "평일 런치"]

TITLE = "[신사역 호텔뷔페] 리버사이드호텔 더가든키친 평일 런치 와인 무제한 후기 🥂"

B = [
    ("img", ["124055"]),
    ("p", "가족들이랑 오랜만에 [[i:특별한 점심]]을 먹고 싶어서 호텔 뷔페를 예약했어요. 🍽"),
    ("p", "신사역 호텔뷔페로 유명한 [[r:더가든키친]] 평일 런치 후기예요! 리버사이드호텔 뷔페라고도 많이 불러요. 😊", {"b": 1}),
    ("p", "평일 런치에는 ✨스파클링 와인이 무제한✨이라 낮부터 기분 좋게 건배하고 왔어요."),
    ("q", "평일 런치 성인 70,000원 / 네이버 예약 61,200원 / 신사역 5번 출구 도보 5분 🥂"),
    ("bubble", "사진 미리보기📷"),
    ("img", ["124055", "122735", "122951", "133600"]),

    ("h", "📍 신사역 호텔뷔페 더가든키친 위치 & 이용정보"),
    ("img", ["121846"]),
    ("p", "더 리버사이드 호텔 주차장 쪽으로 들어가면 호텔 로비와 웨딩홀 안내판이 보여요."),
    ("img", ["121913"]),
    ("p", "나무 조명이 달린 입구를 지나 계단을 내려가면 호텔 1층으로 바로 연결돼요. 🌿"),
    ("img", ["121935"]),
    ("p", "로비 안내 화면에 [[B:뷔페 더 가든키친은 직진 후 뒤쪽 계단 1층]]이라고 적혀 있어서 헷갈리지 않았어요."),
    ("p", "신사역 호텔뷔페 찾는 분들을 위해 방문 전에 알아두시면 좋은 정보부터 정리해 드릴게요!"),
    ("p", "🏠 상호명: 더 리버사이드 호텔 더가든키친 (THE GARDEN KITCHEN)", {"b": 1}),
    ("p", "🗺 주소: 서울 서초구 강남대로107길 6 더 리버사이드 호텔 1층", {"b": 1}),
    ("p", "🚇 대중교통: 3호선·신분당선 신사역 5번 출구에서 걸어서 약 5분", {"b": 1}),
    ("p", "⏰ 이용시간: 평일 런치 11:30 ~ 14:30 / 디너 18:00 ~ 21:30", {"b": 1}),
    ("p", "🚗 주차 정보: 레스토랑 이용 시 [[r:3시간 무료]] (발렛 이용 시 별도 요금)", {"b": 1}),
    ("p", "📞 문의: 02-6710-1100", {"b": 1}),
    ("img", ["123341"]),
    ("p", "아기 의자와 옷걸이도 준비되어 있어서 아이와 함께 오는 가족 모임에도 편했어요. 👶"),

    ("h", "💵 더가든키친 가격 & 예약 꿀팁"),
    ("p", "더가든키친 가격은 시간대와 요일에 따라 달라요. 방문 당시 기준으로 정리해 드릴게요."),
    ("menu", "🍽 [[y:평일 런치]]", [
        "성인: 70,000원", "어린이: 35,000원",
    ]),
    ("menu", "🌙 [[y:디너 · 주말 · 공휴일]]", [
        "성인: 98,000원", "어린이: 49,000원",
    ]),
    ("p", "저희는 [[p:네이버 예약]]으로 성인 61,200원, 어린이 34,000원에 이용했어요! 💸", {"b": 1}),
    ("p", "현장 가격보다 성인 1인당 8,800원이 저렴해서 [[B:꼭 네이버 예약을 추천]]해요."),
    ("p", "가격은 시즌마다 바뀌니까 예약 전에 네이버 예약 페이지에서 한 번 더 확인해 주세요."),

    ("h", "🦀 서울 호텔뷔페다운 메뉴 구성"),
    ("img", ["122758"]),
    ("p", "입구 쪽에서는 [[r:통참치 카빙]]을 해주는데, 커다란 참치가 통째로 올라가 있어서 다들 사진부터 찍었어요. 🐟"),
    ("img", ["122735"]),
    ("p", "황제의 보양식이라고 소개된 [[y:베이징덕]] 코너도 있어요. 얇은 밀전병에 오이, 파와 함께 싸 먹으면 돼요."),
    ("img", ["122951"]),
    ("p", "양념게장과 간장게장이 큰 그릇에 가득 담겨 있어서 게장 좋아하는 가족들이 제일 좋아했어요. 🦀"),
    ("img", ["123141"]),
    ("p", "참치 페스티벌 기간이라 참치 통구이도 있었어요. 머리까지 통째로 구워 나와서 신기했어요."),
    ("img", ["123207", "123159"]),
    ("p", "LA갈비와 허니 글레이즈드 치킨 같은 고기 메뉴도 따뜻하게 계속 채워줘요."),
    ("img", ["123103"]),
    ("p", "윤기가 흐르는 중식 돼지고기 조림은 청경채와 함께 나와서 밥반찬으로 딱이었어요."),
    ("img", ["122823"]),
    ("p", "샤브샤브 재료를 골라 담으면 바로 끓여주는 코너도 있고, 물냉면과 유니짜장면도 있어요. 🍜"),
    ("img", ["122934"]),
    ("p", "트러플 크림 리조또와 해산물 요리가 있는 [[g:양식 코너]]도 따로 있어요."),
    ("img", ["140153"]),
    ("p", "화덕에서 바로 구워 나오는 피자 코너도 있어서 아이들이 좋아했어요. 🍕"),
    ("img", ["122910", "140120"]),
    ("p", "죽과 수프 종류도 여러 가지라 속을 편하게 달래기도 좋았어요."),

    ("h", "😋 더가든키친 평일 런치 솔직 후기"),
    ("p", "오늘 주문한 메뉴는 [[p:더가든키친 평일 런치 뷔페]]예요! 🥂", {"b": 1}),
    ("img", ["124448"]),
    ("p", "자리에 앉자마자 스파클링 와인부터 한 잔 받아왔어요. 달콤하고 톡 쏘는 맛이라 낮술로 부담 없었어요. 🍾"),
    ("img", ["124919.gif"]),
    ("p", "가족들이랑 다 같이 짠! 평일 런치 와인 무제한은 [[B:11시 40분부터 1시 30분까지]]라 조금 일찍 가는 게 좋아요."),
    ("img", ["124055"]),
    ("p", "첫 접시는 베이징덕 쌈, 참치회, 구운 채소로 담았어요."),
    ("p", "베이징덕은 껍질이 바삭하고 소스가 달큰해서 [[r:계속 손이 가는]] 맛이었어요. 😍"),
    ("img", ["124048"]),
    ("p", "두 번째 접시는 LA갈비 위주로! 달달한 양념이 잘 배어 있고 부드러워서 아이들도 잘 먹었어요."),
    ("img", ["130123"]),
    ("p", "육회와 튀김, 화덕 피자까지 한 접시에 골고루 담아봤어요."),
    ("img", ["124244"]),
    ("p", "초밥 코너에서 참치, 광어, 오징어, 계란 초밥도 가져왔어요. 🍣"),
    ("p", "참치 초밥은 방금 카빙한 참치라 [[y:빛깔부터 선명하고]] 신선했어요."),
    ("img", ["130812"]),
    ("p", "주문하면 따로 만들어주는 크림 수프는 고소하고 진해서 빵을 찍어 먹기 좋았어요."),
    ("img", ["131137", "133457"]),
    ("p", "생면 파스타도 즉석에서 만들어줘요. 토마토 파스타는 새콤하고, 라구 파스타는 고기가 듬뿍 들어 있어요. 🍝"),
    ("img", ["132429"]),
    ("p", "로스트비프와 함께 나오는 요크셔푸딩은 겉은 바삭하고 속은 텅 비어 있어서 재밌는 식감이었어요."),
    ("img", ["133947"]),
    ("p", "유니짜장면은 면이 쫄깃하고 소스가 진해서 [[B:한식 짜장면 맛 그대로]]라 반가웠어요."),

    ("h", "🍨 디저트도 놓칠 수 없죠"),
    ("img", ["122206"]),
    ("p", "젤라또는 흑임자, 청사과, 녹차, 레몬, 딸기, 인절미, 망고, 치즈까지 여덟 가지나 돼요. 🍦"),
    ("img", ["134416"]),
    ("p", "저는 [[p:흑임자 젤라또]]를 골랐는데 고소하고 많이 달지 않아서 마무리로 딱이었어요.", {"b": 1}),
    ("img", ["133600"]),
    ("p", "망고 빙수는 우유 얼음 위에 망고 퓨레와 망고 과육이 듬뿍 올라가 있어요. 🥭"),
    ("img", ["122651"]),
    ("p", "캐러멜을 입힌 바나나 디저트는 달콤한 향이 진해서 커피랑 같이 먹기 좋았어요."),
    ("img", ["140531"]),
    ("p", "코코넛 타르트와 카눌레 같은 구움과자도 있어서 디저트만 따로 한 접시 더 먹었어요. 😆"),

    ("h", "💡 더가든키친 방문 꿀팁"),
    ("p", "직접 가보고 정리한 팁이에요."),
    ("p", "1️⃣ 네이버 예약을 이용하면 현장가보다 저렴하게 먹을 수 있어요."),
    ("p", "2️⃣ 평일 런치 와인 무제한은 11:40 ~ 13:30이라 오픈 시간에 맞춰 가는 걸 추천해요."),
    ("p", "3️⃣ 통참치 카빙과 로스트비프는 운영 시간이 정해져 있어서 안내판을 먼저 확인하세요."),
    ("p", "4️⃣ 주차는 3시간까지 무료라 차로 오셔도 편해요."),
    ("p", "5️⃣ 파스타와 수프는 주문하면 만들어주니까 처음에 주문해 두고 다른 음식을 먹으면 좋아요."),

    ("hr",),
    ("h", "📋 후기 종합"),
    ("p", "⭕ 좋았던 점", {"b": 1}),
    ("p", "[[bl:✨ 평일 런치에도 스파클링 와인이 무제한이에요.]]\n[[bl:✨ 통참치 카빙, 베이징덕, 게장까지 메뉴가 다양해요.]]\n[[bl:✨ 파스타와 수프를 즉석에서 만들어줘요.]]\n[[bl:✨ 아기 의자가 있어서 가족 모임으로 가기 좋아요.]]"),
    ("p", "❌ 아쉬웠던 점", {"b": 1}),
    ("p", "[[o:💵 현장가는 부담스러운 편이라 예약 할인이 필수예요.]]\n[[o:⏰ 와인 무제한과 카빙 코너 운영 시간이 짧아요.]]"),
    ("p", "🔄 재방문 의사: 🙆‍♀️🙆‍♀️🙆‍♀️🙆‍♀️", {"b": 1}),
    ("p", "👍 다음엔 디너로 와서 로스트비프 카빙도 꼭 먹어볼 거예요!"),
    ("p", "🎯 추천대상", {"b": 1}),
    ("p", "🧡 신사역 호텔뷔페를 찾으시는 분들\n🧡 가족 모임이나 생일 모임 장소를 찾으시는 분들\n🧡 가성비 좋은 서울 호텔뷔페를 원하시는 분들"),
    ("p", "🌈직접 먹어보고 느낀 그대로 솔직하게 작성한 신사역 호텔뷔페 더가든키친 후기입니다.", {"b": 1}),
    ("place", "더가든키친", "강남대로107길"),
]

TAGS = "#신사역호텔뷔페 #더가든키친 #리버사이드호텔뷔페 #더리버사이드호텔 #서울호텔뷔페 #신사역맛집 #신사동맛집 #강남호텔뷔페 #호텔뷔페추천 #더가든키친평일런치 #더가든키친가격 #호텔뷔페런치 #와인무제한 #가족모임장소 #서울뷔페추천 #통참치카빙 #베이징덕 #간장게장 #가성비호텔뷔페 #강남뷔페 #신사역뷔페 #생일모임 #서초구맛집 #리버사이드호텔 #뷔페맛집"

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
    return f"""<title>더가든키친 초안</title>
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
            out.append(" ".join(f"![IMG_{n}](../photos/garden/blur/IMG_{n}.jpg)" for n in blk[1]))
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
    (OUT / "garden.html").write_text(build_html())
    (OUT / "garden.md").write_text(build_md())
    lines = [l for b in B if b[0] == "p" for l in plain(b[1]).split("\n")]
    print("ok", (OUT / "garden.html").stat().st_size // 1024, "KB",
          "| emoji", sum(len(EMO.findall(l)) for l in lines),
          "| lines w/ emoji %.0f%%" % (100 * sum(1 for l in lines if EMO.search(l)) / len(lines)),
          "| chars", sum(len(plain(b[1])) for b in B if b[0] == "p"))
