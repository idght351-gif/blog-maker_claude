"""하늘초밥 본점(서대문점) 이대역 판초밥 (3번 폴더, 2026-10-09 한글날 방문)."""
import base64, html, io, re
from pathlib import Path
from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "drafts"
COLORS = {"r": "#f12f22", "p": "#f02c8c", "g": "#00a350", "bl": "#0076c8", "o": "#ff9c23"}
ALIGN = "left"
LINE = 22
PHOTOS = ROOT / "photos" / "sky" / "blur"
RESEARCH_DIR = str(ROOT / "data" / "research" / "sky")
CROP = {"122748": 0.55, "122831": 0.5, "124807": 0.45, "124509": 0.4, "124558": 0.6,
        "125728": 0.5, "125853": 0.5, "130310": 0.5, "130007": 0.45, "130147": 0.45, "130748": 0.45,
        "125825": 0.5, "124554": 0.5, "131019": 0.5, "133101": 0.5, "124517": 0.45, "124535": 0.45}
NOCROP = {"124020", "133213", "124614"}   # 안내문·메뉴판은 자르지 않음
ROTATE = {}
NDS_QUERY = ""          # 영수증 사진 없음 → 영수증 리뷰·내돈내산 카드 생략
CATEGORY = "먹보여행"
MAIN_KW = "이대 초밥"
SUB_KWS = ["이대역 맛집", "신촌 맛집", "하늘초밥", "욕심쟁이", "판초밥"]

TITLE = "[이대 초밥] 하늘초밥 본점 욕심쟁이 32피스, 한글날 웨이팅 후기 🍣"

B = [
    ("img", ["125728"]),
    ("p", "공휴일이었던 한글날, 초밥이 너무 먹고 싶어서 [[i:이대역까지]] 달려갔어요. 🚇"),
    ("p", "유튜브와 블로그에서 유명한 이대 초밥 맛집 [[r:하늘초밥 본점]]에 다녀왔어요! 🍣", {"b": 1}),
    ("p", "커다란 접시에 초밥이 가득 담겨 나오는 ✨판초밥✨으로 유명한 곳이라 꼭 한번 가보고 싶었거든요."),
    ("q", "욕심쟁이 32피스 판초밥 / 이대역 3번 출구 도보 3분 / 웨이팅 필수 🍣"),
    ("bubble", "사진 미리보기📷"),
    ("img", ["125728", "130147", "124807", "122831"]),

    ("h", "📍 이대 초밥 하늘초밥 위치 & 영업정보"),
    ("img", ["122748"]),
    ("p", "하얀 외관에 금색 테두리 문이 있고, 위쪽에 구름 모양 간판이 달려 있어요. ☁️"),
    ("img", ["122831"]),
    ("p", "입구 옆에는 커다란 강아지 풍선 인형이 앉아 있어서 [[B:멀리서도 바로 찾을 수 있어요.]] 🐶"),
    ("p", "이대역 맛집 찾는 분들을 위해 방문 전에 알아두시면 좋은 정보부터 정리해 드릴게요!"),
    ("p", "🏠 상호명: 하늘초밥 본점 (서대문점)", {"b": 1}),
    ("p", "🗺 주소: 서울 서대문구 이화여대2길 14 1층", {"b": 1}),
    ("p", "🚇 대중교통: 2호선 이대역 3번 출구에서 걸어서 약 3분", {"b": 1}),
    ("p", "⏰ 영업시간: 11:30 ~ 22:00 / 브레이크타임 오후 / 라스트오더 21:00", {"b": 1}),
    ("p", "📅 휴무: 매주 월요일", {"b": 1}),
    ("p", "🚗 주차 정보: 전용 주차장 없음 (근처 공영주차장 이용)", {"b": 1}),
    ("p", "📞 문의: 0507-1366-4573", {"b": 1}),
    ("p", "브레이크타임은 시기마다 조금씩 달라서 방문 전에 [[r:네이버 플레이스]]를 꼭 확인해 주세요."),

    ("h", "⏳ 하늘초밥 웨이팅 방법"),
    ("img", ["124020"]),
    ("p", "저는 낮 12시 반쯤 도착했는데, 입구에 재료 준비 시간이라 밖에서 기다려 달라는 안내문이 붙어 있었어요."),
    ("p", "대기 명단은 [[B:매장이 만석일 때만]] 사용하고, 오픈 시간에 맞춰 순서대로 안내해 준다고 적혀 있어요."),
    ("p", "공휴일이라 사람이 많을 줄 알았는데 다행히 20분 정도 기다리고 들어갔어요. 😊"),
    ("p", "다른 후기들을 보면 저녁 시간에는 [[o:1시간 넘게 웨이팅]]하는 경우도 많다고 해요."),
    ("p", "최신 소식은 인스타그램 @sorasky0616 계정에 올라와서 가기 전에 한번 확인해 보시면 좋아요."),

    ("h", "🏪 신촌 맛집다운 매장 분위기"),
    ("img", ["124807"]),
    ("p", "안으로 들어가면 원목 바 테이블 너머로 셰프님들이 초밥을 쥐는 모습이 보여요. 🍶"),
    ("p", "바 위에는 사케와 일본 소주병이 쭉 진열되어 있어서 [[g:이자카야 같은 분위기]]도 나요."),
    ("img", ["124509"]),
    ("p", "입구 쪽에는 생선을 숙성하는 냉장고가 있는데, 통생선이 그대로 걸려 있어서 신기했어요. 🐟"),
    ("img", ["124535", "124517"]),
    ("p", "사케 냉장고와 음료 냉장고도 따로 있어서 초밥에 술 한잔 곁들이기 좋은 신촌 맛집이에요."),
    ("img", ["124558"]),
    ("p", "테이블마다 초생강과 단무지가 넉넉하게 준비되어 있어서 [[B:마음껏 덜어 먹을 수 있어요.]]"),

    ("h", "💵 하늘초밥 메뉴 & 가격"),
    ("img", ["124614", "124657"]),
    ("p", "주문은 테이블마다 놓인 태블릿으로 해요. 판초밥 세트부터 1인 메뉴, 안주까지 종류가 다양해요. 😲"),
    ("menu", "🍣 [[y:판초밥 & 후토마끼]]", [
        "흑심: 57,000원", "피쉬맨: 62,000원", "세자매: 76,000원",
        "새우와친구들: 21,000원", "회듬뿍 후토마끼: 32,000원", "바삭바삭 후토마끼: 30,000원",
    ]),
    ("menu", "🙋 [[y:1인 메뉴]]", [
        "후토마끼 반줄: 18,000원", "1인전용 특급열차: 33,000원", "1인전용 흑심: 30,000원",
    ]),
    ("menu", "🍤 [[y:안주]]", [
        "대가리구이: 16,000원", "갑오징어튀김: 13,000원", "타코와사비: 10,000원",
        "고로케 3pcs: 5,500원", "멘보샤 5pcs: 8,000원", "한치다리튀김: 13,000원",
    ]),
    ("img", ["133213"]),
    ("p", "포장 메뉴판도 따로 있어요. 포장 하늘초밥 14피스 26,000원, 포장 쩜초밥 26피스 51,000원이에요."),
    ("p", "[[p:포장 욕심쟁이 32피스는 59,000원]]이에요.", {"b": 1}),
    ("p", "포장한 초밥은 냉장 보관하지 말고 최대한 빨리 먹어 달라는 안내도 귀엽게 적혀 있었어요. 😆"),
    ("p", "저희는 고민 없이 가장 유명한 [[p:욕심쟁이]]를 주문했어요! 🍣", {"b": 1}),

    ("h", "😋 이대 초밥 하늘초밥 욕심쟁이 솔직 후기"),
    ("p", "오늘 주문한 메뉴는 [[p:욕심쟁이 32피스]] 판초밥이에요! 🍣", {"b": 1}),
    ("img", ["124554"]),
    ("p", "초밥이 나오기 전에 양배추 샐러드가 먼저 나와요. 🥗"),
    ("img", ["125825"]),
    ("p", "따끈한 미소된장국도 함께 나와서 속을 데우고 시작했어요."),
    ("img", ["125728"]),
    ("p", "드디어 나온 [[p:욕심쟁이 32피스]]! 접시를 보자마자 저도 모르게 '와' 소리가 나왔어요. 😍", {"b": 1}),
    ("p", "연어, 참치, 흰살생선, 새우, 단새우, 장어, 계란말이, 조개, 군함까지 [[B:종류가 정말 다양해요.]]"),
    ("img", ["125734"]),
    ("p", "김띠를 두른 단새우는 살이 통통하고 끈적할 만큼 달큰했어요. 🦐"),
    ("img", ["130147"]),
    ("p", "한입에 넣으면 ✨단새우 특유의 단맛✨이 입안 가득 퍼져요.", {"b": 1}),
    ("img", ["130748"]),
    ("p", "두툼하게 썬 연어는 기름기가 자르르 흘러서 부드럽게 녹아요."),
    ("img", ["125853"]),
    ("p", "하얀 오징어는 칼집이 촘촘하게 들어가 있어서 질기지 않고 쫀득했어요."),
    ("img", ["130310"]),
    ("p", "흰살생선 위에 새콤한 토핑을 올린 한 점은 상큼해서 중간에 입가심하기 좋았어요."),
    ("img", ["130007"]),
    ("p", "부추가 들어간 [[y:계란말이]]는 달달하고 폭신해서 디저트처럼 먹었어요. 🍳"),
    ("img", ["131019"]),
    ("p", "생와사비도 따로 나와서 취향껏 올려 먹으면 돼요. 저는 듬뿍 올리는 걸 좋아해서 한 번 더 받았어요."),
    ("p", "밥은 작고 회는 큼직해서 [[r:회 맛이 확실한]] 구성이었어요. 밥알도 간이 세지 않아서 생선 맛을 가리지 않았어요."),
    ("p", "두 명이서 32피스를 먹으니 배가 꽉 찼어요. 둘이서 욕심쟁이 하나면 딱 적당해요."),
    ("img", ["133101"]),
    ("p", "결국 접시에는 초생강만 남기고 싹 비웠어요. 🙌"),
    ("p", "가격이 저렴한 편은 아니지만, 이 정도 양과 신선도라면 충분히 만족스러운 한 끼였어요."),

    ("h", "💡 하늘초밥 방문 꿀팁"),
    ("p", "직접 가보고 정리한 팁이에요."),
    ("p", "1️⃣ 오픈 시간이나 브레이크타임 직후에 맞춰 가면 웨이팅이 훨씬 짧아요."),
    ("p", "2️⃣ 처음이라면 다양한 초밥을 맛볼 수 있는 [[B:욕심쟁이 32피스]]를 추천해요. 2명이 먹기 딱 좋아요."),
    ("p", "3️⃣ 혼자라면 1인전용 특급열차나 1인전용 흑심 메뉴가 있어요."),
    ("p", "4️⃣ 주차장이 없어서 지하철로 가는 게 편해요. 이대역 3번 출구에서 가까워요."),
    ("p", "5️⃣ 포장한 초밥은 1~2시간 안에 먹어야 맛있다고 하니 바로 드세요."),
    ("p", "식사 후에는 이대 앞 카페 골목에서 디저트까지 즐기면 딱 좋은 코스예요."),

    ("hr",),
    ("h", "📋 후기 종합"),
    ("p", "⭕ 좋았던 점", {"b": 1}),
    ("p", "[[bl:✨ 32피스 판초밥 한 접시로 다양한 초밥을 맛볼 수 있어요.]]\n[[bl:✨ 회가 큼직하고 신선해서 만족도가 높아요.]]\n[[bl:✨ 초생강, 단무지, 생와사비를 넉넉하게 먹을 수 있어요.]]\n[[bl:✨ 사케와 술 종류가 많아 저녁 술자리로도 좋아요.]]"),
    ("p", "❌ 아쉬웠던 점", {"b": 1}),
    ("p", "[[o:⏳ 웨이팅이 길 때가 많아서 시간 여유를 두고 가야 해요.]]\n[[o:🚗 전용 주차장이 없어요.]]"),
    ("p", "🔄 재방문 의사: 🙆‍♀️🙆‍♀️🙆‍♀️🙆‍♀️🙆‍♀️", {"b": 1}),
    ("p", "👍 다음엔 회듬뿍 후토마끼와 멘보샤도 꼭 먹어볼 거예요!"),
    ("p", "🎯 추천대상", {"b": 1}),
    ("p", "🧡 이대 초밥 맛집을 찾으시는 분들\n🧡 가성비 좋은 판초밥을 푸짐하게 먹고 싶은 분들\n🧡 신촌·이대에서 데이트나 술자리 장소를 찾으시는 분들"),
    ("p", "🌈직접 먹어보고 느낀 그대로 솔직하게 작성한 이대 초밥 하늘초밥 본점 후기입니다.", {"b": 1}),
    ("place", "하늘초밥 본점", "이화여대2길"),
]

TAGS = "#이대초밥 #하늘초밥 #하늘초밥본점 #이대역맛집 #이대맛집 #신촌맛집 #신촌초밥 #서대문초밥 #서대문구맛집 #판초밥 #욕심쟁이 #하늘초밥욕심쟁이 #이대초밥맛집 #이대역초밥 #신촌데이트 #이대데이트 #초밥맛집 #서울초밥맛집 #후토마끼 #단새우초밥 #연어초밥 #이대웨이팅맛집 #한글날 #사케맛집 #이대술집"

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
    return f"""<title>하늘초밥 초안</title>
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
            out.append(" ".join(f"![IMG_{n}](../photos/sky/blur/IMG_{n}.jpg)" for n in blk[1]))
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
    (OUT / "sky.html").write_text(build_html())
    (OUT / "sky.md").write_text(build_md())
    lines = [l for b in B if b[0] == "p" for l in plain(b[1]).split("\n")]
    print("ok", (OUT / "sky.html").stat().st_size // 1024, "KB",
          "| emoji", sum(len(EMO.findall(l)) for l in lines),
          "| lines w/ emoji %.0f%%" % (100 * sum(1 for l in lines if EMO.search(l)) / len(lines)),
          "| chars", sum(len(plain(b[1])) for b in B if b[0] == "p"))
