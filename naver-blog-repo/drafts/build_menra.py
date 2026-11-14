"""멘라(MENRA) 마곡 돈코츠라멘 (6번 폴더). 영수증 리뷰는 사용자가 직접 등록함 → 내돈내산 카드만."""
import base64, html, io, re
from pathlib import Path
from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "drafts"
COLORS = {"r": "#f12f22", "p": "#f02c8c", "g": "#00a350", "bl": "#0076c8", "o": "#ff9c23"}
ALIGN = "left"
LINE = 22
PHOTOS = ROOT / "photos" / "menra" / "blur"
RESEARCH_DIR = str(ROOT / "data" / "research" / "menra")
CROP = {"9379": 0.5, "9380": 0.45, "9382": 0.45, "9386": 0.45, "9392": 0.5, "9395": 0.5}
NOCROP = {"9387", "9389"}   # 키오스크 메뉴 화면은 자르지 않음
ROTATE = {}
NDS_QUERY = ""   # 카드는 저장 후 add_nds.js로 넣음
CATEGORY = "먹보여행"
MAIN_KW = "마곡 라멘"
SUB_KWS = ["마곡역 맛집", "멘라", "돈코츠라멘", "매운돈코츠라멘"]

TITLE = "[마곡 라멘] 멘라 매운돈코츠라멘 11,000원, 공깃밥 무료 솔직후기 🍜"

B = [
    ("img", ["9400"]),
    ("p", "진하고 뽀얀 국물이 당기는 날, 마곡역 근처 [[i:라멘집]]을 찾아갔어요. 🍜"),
    ("p", "하카타식 돈코츠라멘으로 소문난 마곡 라멘 맛집 [[r:멘라(MENRA)]] 후기예요! 😊", {"b": 1}),
    ("p", "8시간 우린 돈사골 육수에 ✨공깃밥까지 무료✨라 든든하게 한 끼 먹기 좋은 곳이었어요."),
    ("q", "매운돈코츠라멘 11,000원 / 공깃밥 무료 / 마곡역 3번 출구 도보 5분 🍜"),
    ("bubble", "사진 미리보기📷"),
    ("img", ["9400", "9405", "9384", "9379"]),

    ("h", "📍 마곡 라멘 멘라 위치 & 영업정보"),
    ("img", ["9379"]),
    ("p", "건물 1층 복도 안쪽에 있고, 라멘 그릇 로고가 그려진 하얀 간판이 걸려 있어요."),
    ("img", ["9382"]),
    ("p", "유리문에 영업시간과 브레이크타임이 크게 적혀 있어서 [[B:가기 전에 한 번 더 확인]]하기 좋아요."),
    ("p", "마곡역 맛집 찾는 분들을 위해 방문 전에 알아두시면 좋은 정보부터 정리해 드릴게요!"),
    ("p", "🏠 상호명: 멘라 (MENRA TONKOTSU RAMEN)", {"b": 1}),
    ("p", "🗺 주소: 서울 강서구 마곡중앙6로 21 1층 128호", {"b": 1}),
    ("p", "🚇 대중교통: 5호선 마곡역 3번 출구에서 걸어서 약 5분", {"b": 1}),
    ("p", "⏰ 영업시간: 평일 11:00 ~ 21:00 / 토 11:00 ~ 15:00", {"b": 1}),
    ("p", "☕ 브레이크타임: 15:00 ~ 17:00 (라스트오더 20:30)", {"b": 1}),
    ("p", "📅 휴무: [[r:매주 일요일]]", {"b": 1}),
    ("p", "🚗 주차 정보: 건물 주차장 이용 (방문 전 확인 추천)", {"b": 1}),
    ("img", ["9381"]),
    ("p", "입구에는 식약처 [[g:음식점 위생등급 매우 우수]] 인증 스티커가 붙어 있어서 믿음이 갔어요. ⭐"),

    ("h", "🏪 바 테이블 위주의 매장 분위기"),
    ("img", ["9384"]),
    ("p", "매장 안은 원목 바 테이블이 길게 이어진 [[g:일본 라멘집 같은]] 구조예요."),
    ("img", ["9383"]),
    ("p", "주방을 바라보며 앉는 자리라 혼밥하기에도 전혀 어색하지 않았어요. 🙋‍♀️"),
    ("p", "의자 간격도 넉넉해서 옆 사람과 팔이 부딪히지 않고 편하게 먹을 수 있었어요."),
    ("img", ["9385"]),
    ("p", "오픈 주방이라 커다란 육수 솥이 그대로 보여요. 깔끔하게 정돈되어 있어서 기분 좋게 먹었어요."),
    ("img", ["9393", "9395"]),
    ("p", "자리마다 물컵과 수저가 준비되어 있고, 차가운 보리차를 셀프로 따라 마실 수 있어요."),
    ("img", ["9392"]),
    ("p", "노란 단무지도 통에 넉넉하게 담겨 있어서 원하는 만큼 덜어 먹으면 돼요."),
    ("img", ["9394"]),
    ("p", "선반에는 [[B:공깃밥(무료) 추가는 말씀해 달라]]는 안내가 붙어 있어요. 국물에 밥 말아 먹을 분들은 꼭 챙기세요! 🍚"),

    ("h", "💵 멘라 메뉴 & 가격"),
    ("img", ["9386"]),
    ("p", "주문은 입구 옆 키오스크에서 해요. 😊"),
    ("img", ["9387"]),
    ("p", "라멘은 딱 세 가지라 고민할 필요 없이 금방 고를 수 있어요."),
    ("menu", "🍜 [[y:라멘]]", [
        "돈코츠라멘: 10,500원",
        ("[[p:매운돈코츠라멘: 11,000원]]", {"b": 1}),
        "고카이돈코츠라멘: 11,000원",
    ]),
    ("menu", "🥚 [[y:토핑 추가]]", [
        "차슈 추가(1장)·계란 추가(1개): 각 1,000원",
        "목이버섯·파 추가: 각 500원", "면 추가: 2,000원",
    ]),
    ("menu", "🥤 [[y:음료]]", [
        "콜라·제로콜라·펩시제로·스프라이트: 각 2,000원",
        "카스 병맥주: 4,000원", "기린 병맥주: 6,500원",
    ]),
    ("img", ["9380"]),
    ("p", "입구 배너에는 메뉴 설명도 있어요. 고카이돈코츠라멘은 돼지 육수에 매콤한 비법 가루를 넣어 칼칼하고 시원한 라멘이래요."),
    ("img", ["9389"]),
    ("p", "저는 [[p:매운돈코츠라멘]]을 골랐어요! 매운 단계는 덜맵게·보통·더맵게·아주맵게 중에서 고를 수 있어요. 🌶", {"b": 1}),
    ("img", ["9390"]),
    ("p", "네이버 지도 리뷰를 쓰면 탄산음료를 서비스로 주는 이벤트도 하고 있었어요."),

    ("h", "😋 마곡 라멘 멘라 매운돈코츠라멘 솔직 후기"),
    ("p", "오늘 주문한 메뉴는 [[p:매운돈코츠라멘]] 한 그릇이에요! 🍜", {"b": 1}),
    ("img", ["9398"]),
    ("p", "라멘이 나오기 전에 단무지부터 접시에 덜어뒀어요."),
    ("img", ["9399"]),
    ("p", "드디어 나온 매운돈코츠라멘! 그릇 가장자리에 용 무늬가 그려져 있어서 [[B:비주얼부터 일본 라멘집 감성]]이에요. 😍", {"b": 1}),
    ("img", ["9401.gif"]),
    ("p", "차슈 두 장, 반숙 계란 두 개, 목이버섯과 송송 썬 파가 듬뿍 올라가 있어요."),
    ("p", "국물 가운데 빨간 양념 가루가 콕 올라가 있는데, 풀어서 섞어 먹으면 돼요."),
    ("img", ["9403.gif"]),
    ("p", "국물을 한 숟갈 떠보니 ✨진하고 크리미한 돈코츠 국물✨에 칼칼함이 살짝 더해진 맛이에요.", {"b": 1}),
    ("p", "돈코츠 특유의 묵직함이 있는데 매운 양념 덕분에 끝맛은 깔끔했어요."),
    ("p", "돼지 냄새 같은 잡내가 전혀 없어서 돈코츠를 처음 먹는 분들도 부담 없이 드실 수 있을 것 같아요."),
    ("img", ["9405"]),
    ("p", "면은 하카타식답게 [[y:얇은 직면]]이라 국물이 잘 묻어나요."),
    ("img", ["9404.gif"]),
    ("p", "후루룩 넘어가는 식감이라 정신없이 먹었어요. 🤤"),
    ("p", "면이 얇아서 오래 두면 금방 퍼지니까, 나오자마자 먼저 면부터 먹는 걸 추천해요. 면이 부족하면 2,000원에 면 추가도 할 수 있어요."),
    ("img", ["9406"]),
    ("p", "반숙 계란은 노른자가 [[r:주황빛으로 촉촉하게]] 익어 있어서 국물이랑 같이 먹으니 고소함이 두 배였어요."),
    ("img", ["9407"]),
    ("p", "차슈는 겉을 불맛 나게 그을려서 나와요. 두툼한데도 부드럽게 찢어졌어요."),
    ("img", ["9408"]),
    ("p", "면을 다 먹고 공깃밥을 부탁드렸더니, 밥 위에 [[B:차슈 조각까지 올려서]] 주셨어요. 🍚"),
    ("img", ["9409"]),
    ("p", "남은 국물에 밥을 말아 먹으니 돈코츠 국밥처럼 든든했어요."),
    ("img", ["9410"]),
    ("p", "단무지 하나 올려서 마지막 한 숟갈까지 싹 비웠어요. 🙌"),
    ("p", "국물이 진한데도 마지막까지 느끼하지 않았던 건 매운 양념과 단무지 덕분인 것 같아요."),
    ("p", "라멘 한 그릇에 밥까지 먹으니 11,000원으로 배부르게 먹은 기분이었어요."),

    ("h", "💡 멘라 방문 꿀팁"),
    ("p", "직접 가보고 정리한 팁이에요."),
    ("p", "1️⃣ 공깃밥은 무료라서 면을 다 먹은 뒤 말씀드리면 돼요. [[B:국물에 말아 먹는 게 필수 코스]]예요."),
    ("p", "2️⃣ 매운 걸 잘 못 드시면 매운돈코츠라멘을 '덜맵게'로 고르거나 기본 돈코츠라멘을 추천해요."),
    ("p", "3️⃣ 브레이크타임(15:00~17:00)과 토요일 오후 3시 마감, 일요일 휴무를 꼭 확인하세요."),
    ("p", "4️⃣ 바 테이블 위주라 혼밥하기 좋아요. 점심시간엔 근처 직장인들이 많으니 조금 일찍 가면 여유로워요."),
    ("p", "5️⃣ 네이버 지도 리뷰를 쓰면 탄산음료 서비스 이벤트도 있어요."),

    ("hr",),
    ("h", "📋 후기 종합"),
    ("p", "⭕ 좋았던 점", {"b": 1}),
    ("p", "[[bl:✨ 8시간 우린 진한 돈코츠 국물이 크리미하고 깊어요.]]\n[[bl:✨ 공깃밥이 무료라 국물까지 든든하게 먹을 수 있어요.]]\n[[bl:✨ 차슈 두 장에 반숙 계란 두 개까지 토핑이 넉넉해요.]]\n[[bl:✨ 바 테이블이라 혼밥하기 편해요.]]"),
    ("p", "❌ 아쉬웠던 점", {"b": 1}),
    ("p", "[[o:⏰ 토요일은 오후 3시까지만 하고 일요일은 쉬어요.]]\n[[o:🪑 바 테이블 위주라 여러 명이 마주 앉기는 어려워요.]]"),
    ("p", "🔄 재방문 의사: 🙆‍♀️🙆‍♀️🙆‍♀️🙆‍♀️", {"b": 1}),
    ("p", "👍 다음엔 칼칼하다는 고카이돈코츠라멘도 먹어볼 거예요!"),
    ("p", "🎯 추천대상", {"b": 1}),
    ("p", "🧡 마곡 라멘 맛집을 찾으시는 분들\n🧡 진한 돈코츠 국물을 좋아하시는 분들\n🧡 마곡역 근처에서 혼밥할 곳을 찾으시는 분들"),
    ("p", "🌈직접 먹어보고 느낀 그대로 솔직하게 작성한 마곡 라멘 멘라 후기입니다.", {"b": 1}),
    ("place", "멘라", "마곡중앙6로"),
]

TAGS = "#마곡라멘 #멘라 #멘라라멘 #마곡역맛집 #마곡맛집 #마곡라멘맛집 #돈코츠라멘 #매운돈코츠라멘 #하카타라멘 #마곡점심 #마곡혼밥 #마곡역라멘 #마곡나루맛집 #발산역맛집 #강서구맛집 #강서구라멘 #일본라멘 #라멘맛집 #공깃밥무료 #마곡저녁 #서울라멘맛집 #돈코츠 #고카이돈코츠라멘 #마곡동맛집 #혼밥맛집"

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
    return f"""<title>멘라 초안</title>
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
            out.append(" ".join(f"![IMG_{n}](../photos/menra/blur/IMG_{n}.jpg)" for n in blk[1]))
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
    (OUT / "menra.html").write_text(build_html())
    (OUT / "menra.md").write_text(build_md())
    lines = [l for b in B if b[0] == "p" for l in plain(b[1]).split("\n")]
    print("ok", (OUT / "menra.html").stat().st_size // 1024, "KB",
          "| emoji", sum(len(EMO.findall(l)) for l in lines),
          "| lines w/ emoji %.0f%%" % (100 * sum(1 for l in lines if EMO.search(l)) / len(lines)),
          "| chars", sum(len(plain(b[1])) for b in B if b[0] == "p"))
