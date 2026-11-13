"""베코(BECCO) 부천 신중동 리뷰 초안 (4번 폴더, 2026-11-07 방문). 블록 형식은 build_kurokame.py 참고."""
import base64, html, io, re
from pathlib import Path
from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
PHOTOS = ROOT / "photos" / "becco" / "blur"
OUT = ROOT / "drafts"
RESEARCH_DIR = str(ROOT / "data" / "research" / "becco")

CROP = {"9526": 0.45, "9527": 0.5, "9537": 0.45, "9513": 0.3}
ROTATE = {"9521": 90, "9522": 90, "9523": 90}   # 반시계 방향 각도. 옆으로 찍힌 메뉴판
COLORS = {"r": "#f12f22", "p": "#f02c8c", "g": "#00a350", "bl": "#0076c8", "o": "#ff9c23"}

NDS_QUERY = "베코"
CATEGORY = "먹보여행"   # 매장 방문기
MAIN_KW = "신중동 맛집"
SUB_KWS = ["부천 화덕피자", "부천 데이트", "신중동역", "쉬림프 엔쵸비", "마르게리따"]
ALIGN = "left"
LINE = 22

TITLE = "[신중동 맛집] 베코 부천 화덕피자 마르게리따·쉬림프 엔쵸비 솔직후기 🍕"

B = [
    ("img", ["9533"]),
    ("p", "토요일 점심, [[i:쫄깃한 화덕피자]]가 너무 당겨서 부천 신중동까지 다녀왔어요. 🍕"),
    ("p", "부천 화덕피자로 이름난 신중동 맛집 [[r:베코(BECCO)]] 후기 바로 들려드릴게요! 😊", {"b": 1}),
    ("p", "나폴리 피자협회 인증 화덕에서 굽는 피자라고 해서 ✨기대가 컸던 곳✨이에요."),
    ("q", "나폴리 화덕에 구운 마르게리따 2만 원 / 베스트 메뉴 쉬림프 엔쵸비 19,500원 / 둘이서 피자+파스타 42,500원 🍝"),
    ("bubble", "사진 미리보기📷"),
    ("img", ["9534", "9528", "9536", "9517"]),

    ("h", "📍 신중동 맛집 베코 위치 & 영업정보"),
    ("img", ["9517"]),
    ("p", "밝은 우드톤 테이블과 하얀 타일 벽이라 들어서자마자 [[g:깔끔하고 아늑한]] 느낌이었어요. 🪑"),
    ("p", "안쪽은 오픈 키친이라 화덕에서 피자가 구워지는 모습을 자리에서 구경할 수 있어요."),
    ("p", "테이블 간격도 넉넉한 편이라 옆 테이블 신경 쓰지 않고 이야기 나누기 좋았어요."),
    ("p", "신중동 맛집 베코, 방문 전에 알아두시면 좋은 정보부터 정리해 드릴게요!"),
    ("p", "🏠 상호명: 베코 (BECCO)", {"b": 1}),
    ("p", "🗺 주소: 경기 부천시 원미구 중동로248번길 45 센트럴파크리움 1층 108호", {"b": 1}),
    ("p", "🚇 대중교통: 7호선 신중동역에서 걸어서 갈 수 있는 거리", {"b": 1}),
    ("p", "⏰ 영업시간: 화~일 11:30 ~ 21:30 (브레이크타임 15:00~17:00, 라스트오더 20:00, [[r:월요일 휴무]])", {"b": 1}),
    ("p", "🚗 주차 정보: 건물 지하주차장 이용 가능", {"b": 1}),
    ("p", "💡 웨이팅 팁: 주말 피크 시간엔 자리가 금방 차요. [[r:네이버 예약]]을 해두거나 입구 테이블링으로 순서를 등록해 두세요.", {"b": 1}),
    ("p", "저는 토요일 12시쯤 들어갔는데 다행히 바로 앉을 수 있었어요. 👍"),
    ("p", "참고로 BECCO라는 이름은 이탈리아어 '부리'에서 따왔다고 해요. 🐦"),

    ("h", "💵 베코 메뉴 & 가격"),
    ("img", ["9513"]),
    ("p", "입구 쪽에도 메뉴판이 붙어 있어서 들어가기 전에 미리 고를 수 있어요. 샐러드, 리조또, 파스타, 피자, 스테이크까지 구성이 알차요. 😲"),
    ("img", ["9521"]),
    ("menu", "🥗 [[y:안티파스토]]", ["베코 샐러드: 13,000원", "시저 샐러드: 16,000원"]),
    ("menu", "🍝 [[y:파스타]]", [
        ("[[p:쉬림프 엔쵸비 (Oil, 링귀니): 19,500원 (BEST)]]", {"b": 1}),
        "봉골레 (Oil, 링귀니): 19,500원", "페스카토레 (Tomato, 스파게티니): 19,500원",
        "비프 라구 (Tomato, 링귀니): 22,000원 (BEST)", "화이트 라구 (Cream, 링귀니): 22,000원",
        "스테이크 포르치니 (Cream): 21,000원", "까르보나라: 19,000원", "쉬림프 로제: 19,000원",
    ]),
    ("menu", "🍚 [[y:리조또]]", ["스테이크 포르치니 (Cream): 21,000원", "페스카토레 (Tomato): 19,500원"]),
    ("img", ["9522"]),
    ("menu", "🍕 [[y:피자]]", [
        ("[[p:마르게리따: 20,000원]]", {"b": 1}),
        "멜란자네·콰트로 포르마지·머쉬룸 치즈(BEST): 각 23,900원", "디아볼라: 22,900원",
        "루꼴라 감베리·스피나치(BEST): 각 25,900원",
    ]),
    ("menu", "🥩 [[y:스테이크]]", ["수비드 와규 플랭크 200g: 39,000원 (BEST)", "찹스테이크: 28,000원"]),
    ("img", ["9523"]),
    ("menu", "🍷 [[y:와인 & 음료]]", [
        "하우스 와인 레드·화이트: 글라스 7,000원 / 보틀 29,000원",
        "레몬·라임 비터스 460ml: 9,500원 (시그니처 칵테일)", "테라 생맥주 400ml: 4,500원",
        ("[[p:코카콜라·제로·스프라이트 355ml: 각 3,000원]]", {"b": 1}), "콜키지: 보틀당 15,000원",
    ]),
    ("p", "파스타는 2만 원 안팎, 피자는 2만~2만 6천 원대라 [[B:가볍게 먹기엔 조금 있는 편]]이에요. 대신 메뉴판에 Best 표시가 있어서 고르기는 쉬웠어요."),
    ("p", "저희는 베스트 메뉴 [[p:쉬림프 엔쵸비]]랑 기본 중의 기본 [[p:마르게리따]], 그리고 콜라를 주문했어요! 🍕", {"b": 1}),

    ("h", "😋 신중동 맛집 베코 솔직 시식 후기"),
    ("p", "오늘 주문한 메뉴는 [[p:쉬림프 엔쵸비, 마르게리따, 콜라]]예요! 🍝", {"b": 1}),
    ("img", ["9524"]),
    ("p", "주문하면 [[y:식전빵]]이 먼저 나와요. 피자 도우를 화덕에 한 번 구운 빵이라 겉에 까만 점이 송송 박혀 있어요. 🥖"),
    ("img", ["9526"]),
    ("p", "포크로 쭉 찢으니 속이 [[g:하얗고 폭신폭신]]했어요."),
    ("p", "겉면은 살짝 탄 듯 고소하고, 속은 공기가 많이 들어가 가벼운 식감이었어요."),
    ("p", "같이 나온 오일에 찍어 먹으니 짭조름하니 입맛이 확 돌더라고요. 😋"),
    ("img", ["9537"]),
    ("p", "콜라는 캔째로 얼음컵이랑 같이 나와요. 피자엔 역시 콜라죠! 🥤"),
    ("p", "빨간 줄무늬 종이 빨대까지 꽂아주셔서 사진이 귀엽게 나왔어요."),

    ("img", ["9527"]),
    ("p", "먼저 나온 [[y:쉬림프 엔쵸비]] 파스타! 링귀니 위로 루꼴라가 수북하고, [[B:큼직한 새우가 통째로]] 올라가 있어요. 🦐", {"b": 1}),
    ("img", ["9528"]),
    ("p", "엔쵸비 페스토에 마늘, 호박, 올리브가 들어간 오일 파스타예요."),
    ("p", "소스가 자작하게 남아 있어서 면이 마지막까지 촉촉했어요."),
    ("p", "링귀니라 면이 납작하고 두께감이 있어서 오일 소스가 잘 묻어나요."),
    ("img", ["9530"]),
    ("p", "한 입 먹자마자 ✨엔쵸비의 짭조름한 감칠맛✨이 확 올라와요! 😭", {"b": 1}),
    ("p", "일반 알리오올리오보다 훨씬 깊은 맛이라 왜 베스트 메뉴인지 알겠더라고요. 루꼴라의 쌉싸름함이 느끼함을 잡아줘요."),
    ("img", ["9531"]),
    ("p", "파스타 양도 넉넉해서 한 접시를 둘이 나눠 먹어도 충분했어요."),
    ("p", "새우는 머리까지 달린 큰 새우라 [[r:탱글탱글한 식감]]이 제대로였어요. 🧡"),

    ("img", ["9533"]),
    ("p", "다음은 화덕에서 바로 나온 [[y:마르게리따]]! 가장자리가 [[B:빵빵하게 부풀고 군데군데 그을린]] 나폴리 피자 비주얼이에요. 🍕", {"b": 1}),
    ("img", ["9534"]),
    ("p", "토마토소스 위에 피오르디라테 치즈와 바질이 올라가 있어요. 치즈가 녹아서 하얀 웅덩이처럼 퍼져 있는 게 군침 돌았어요. 🤤"),
    ("img", ["9536"]),
    ("p", "한 조각 들어 올리니 가운데는 촉촉하고 끝은 쫄깃했어요. 토마토소스가 [[r:새콤하고 신선해서]] 계속 손이 갔어요. 😋"),
    ("img", ["9538"]),
    ("p", "특히 도우 가장자리(코르니치오네)가 [[B:겉은 바삭, 속은 쫄깃]]해서 빵만 따로 먹어도 맛있었어요. 🥰"),
    ("p", "둘이서 피자 한 판에 파스타 하나면 딱 배부르게 먹기 좋은 양이었어요."),
    ("p", "짭조름한 엔쵸비 파스타와 담백한 마르게리따를 번갈아 먹으니 질리지 않았어요."),
    ("p", "신중동 맛집 중에서도 화덕피자만큼은 여기를 먼저 추천하고 싶어요."),

    ("h", "💡 베코 방문 꿀팁"),
    ("p", "직접 가보고 정리한 팁이에요."),
    ("p", "1️⃣ 주말 점심·저녁은 대기가 생기니 [[B:네이버 예약]]을 추천해요."),
    ("p", "2️⃣ 메뉴판의 Best 표시(쉬림프 엔쵸비, 비프 라구, 머쉬룸 치즈, 스피나치)를 참고하면 실패가 적어요."),
    ("p", "3️⃣ 차로 간다면 건물 지하주차장을 이용하세요."),
    ("p", "4️⃣ 와인을 가져가면 콜키지는 보틀당 15,000원이에요. 🍷"),
    ("p", "5️⃣ 월요일은 휴무, 평일 15~17시는 브레이크타임이니 시간 확인은 필수예요."),
    ("p", "현대백화점 중동점 쇼핑 전후로 들르기 좋아서 부천 데이트 코스로도 괜찮겠더라고요."),

    ("hr",),
    ("h", "📋 후기 종합"),
    ("p", "⭕ 좋았던 점", {"b": 1}),
    ("p", "[[bl:✨ 화덕에 구운 마르게리따 도우가 겉은 바삭하고 속은 쫄깃해요.]]\n[[bl:✨ 쉬림프 엔쵸비는 짭조름한 감칠맛에 큰 새우까지 들어 있어요.]]\n[[bl:✨ 식전빵까지 화덕에 구워 나와서 시작부터 만족스러워요.]]\n[[bl:✨ 밝고 깔끔한 분위기라 데이트나 모임 장소로 좋아요.]]"),
    ("p", "❌ 아쉬웠던 점", {"b": 1}),
    ("p", "[[o:💵 파스타·피자가 2만 원 안팎이라 가격대가 있는 편이에요.]]\n[[o:💵 주말엔 대기가 생겨서 예약 없이 가면 기다릴 수 있어요.]]"),
    ("p", "🔄 재방문 의사: 🙆‍♀️🙆‍♀️🙆‍♀️🙆‍♀️", {"b": 1}),
    ("p", "👍 다음엔 베스트 메뉴인 머쉬룸 치즈 피자랑 비프 라구 파스타를 먹어볼 거예요!"),
    ("p", "🎯 추천대상", {"b": 1}),
    ("p", "🧡 부천 화덕피자 맛집을 찾으시는 분들\n🧡 신중동역 근처에서 부천 데이트 장소를 찾으시는 분들\n🧡 피자와 파스타를 같이 즐기고 싶으신 분들"),
    ("p", "🌈직접 먹어보고 느낀 그대로 솔직하게 작성한 신중동 맛집 베코 후기입니다.", {"b": 1}),
    ("place", "베코 부천"),
]

TAGS = "#신중동맛집 #베코 #부천베코 #신중동베코 #베코부천 #부천맛집 #부천화덕피자 #부천화덕피자맛집 #신중동역맛집 #부천신중동맛집 #부천데이트 #부천데이트맛집 #부천파스타맛집 #부천피자맛집 #중동맛집 #부천이탈리안 #화덕피자맛집 #나폴리피자 #마르게리따 #쉬림프엔쵸비 #엔쵸비파스타 #부천양식 #현대백화점중동점맛집 #부천맛집추천 #신중동맛집추천"

INLINE = re.compile(r"\[\[(r|p|y|g|bl|o|B|u|i):(.+?)\]\]", re.S)
EMO = re.compile(r'(?:[\U0001F300-\U0001FAFF☀-➿⭐⭕⌚-⏿](?:️)?(?:‍[\U0001F300-\U0001FAFF☀-➿](?:️)?)*)')


def plain(t):
    return INLINE.sub(lambda m: m.group(2), t)


def load(n):
    im = Image.open(PHOTOS / (f"IMG_{n}" if "." in n else f"IMG_{n}.jpg")).convert("RGB")
    if n in ROTATE:   # 내용이 옆으로 누운 사진(메뉴판 등)은 자르지 않고 사진 자체를 돌림 (사용자 지시 2026-11-13)
        return im.rotate(ROTATE[n], expand=True)
    w, h = im.size
    if h > w:  # 세로 사진 → 가로 4:3
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
    return f"""<title>베코 초안</title>
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
<div class="meta">은똥잉 · 2026. 11. 7. 방문</div>
{chr(10).join(parts)}
<div class="tags">{tags}</div>
</div>"""


def build_md():
    out = [f"# {TITLE}", ""]
    for blk in B:
        k = blk[0]
        if k == "img":
            out.append(" ".join(f"![IMG_{n}](../photos/becco/blur/IMG_{n}.jpg)" for n in blk[1]))
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
    (OUT / "becco.html").write_text(build_html())
    (OUT / "becco.md").write_text(build_md())
    lines = [l for b in B if b[0] == "p" for l in plain(b[1]).split("\n")]
    print("ok", (OUT / "becco.html").stat().st_size // 1024, "KB",
          "| emoji", sum(len(EMO.findall(l)) for l in lines),
          "| lines w/ emoji %.0f%%" % (100 * sum(1 for l in lines if EMO.search(l)) / len(lines)),
          "| chars", sum(len(plain(b[1])) for b in B if b[0] == "p"))
