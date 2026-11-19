"""성천막국수 강남(논현)점 (1번 폴더, 11/17 화 저녁, 남편과). 내돈내산 → 영수증 리뷰 + 카드. 템플릿 T2(이야기·데이트)."""
import base64, html, io, re
from pathlib import Path
from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "drafts"
COLORS = {"r": "#f12f22", "p": "#f02c8c", "g": "#00a350", "bl": "#0076c8", "o": "#ff9c23"}
ALIGN = "left"
LINE = 22
PHOTOS = ROOT / "photos" / "sungcheon" / "blur"
RESEARCH_DIR = str(ROOT / "data" / "research" / "sungcheon")
CROP = {"9976": 0.45, "9943": 0.5, "9960": 0.5, "9961": 0.5, "9967": 0.55, "9968": 0.5, "9969": 0.5, "9970": 0.5}
NOCROP = {"9947", "9949", "9972", "9974", "9973"}   # 안내문·메뉴판·배너는 자르지 않음
ROTATE = {"9952": 270}
NDS_QUERY = ""   # 카드는 영수증 리뷰 후 add_nds.js로
CATEGORY = "먹보여행"
TEMPLATE_ID = "T2"
LENGTH = "보통"
STORE = "성천막국수"
MEMO = {"동행": "남편과 데이트", "최고": ["비빔막국수", "면수"], "비빔": "기대 이상, 달달고소", "대기": "바로 입장, 한산(화 17시)",
        "제육": "부드럽고 잡내 없음", "아쉬움": "주차장 없음, 걸어서 10분 공영주차장", "재방문": "무조건",
        "한마디": "막국수 중에 이정도 탄력은 태어나서 처음이다. 그리고 아래 들기름이 완전 많이 들어서 엄청나게 맛있다. 미쳤다."}
MAIN_KW = "논현역 맛집"
SUB_KWS = ["성천막국수", "비빔막국수", "논현역 막국수"]

TITLE = "[논현역 맛집 성천막국수] 60년 노포 비빔막국수 탄력 미쳤다! 제육·주차 팁"

B = [
    ("img", ["9967"]),
    ("p", "안녕하세요, 은똥잉이에요! 🙋‍♀️ 화요일 저녁, 남편이랑 오랜만에 둘이서 논현역 맛집 데이트를 했답니다. 막국수는 여름 음식이라고만 생각했는데, 11월에 먹는 막국수는 또 어떨까 싶어서 진짜 궁금했거든요!", {"keep": 1}),
    ("p", "바로 1966년부터 3대째 이어 온 [[r:성천막국수]]예요. 🍜 중소벤처기업부에서 [[B:백년가게]]로도 뽑힌 곳이라니, 들어가기 전부터 완전 설레더라고요. ✨", {"keep": 1}),

    ("hb", "📍 논현역 막국수 맛집, 5번 출구 골목 노란 간판"),
    ("img", ["9976"]),
    ("p", "논현역 5번 출구로 나와서 골목으로 몇 분만 걸으면 노란 간판이 바로 보이는데, 여기가 바로 요즘 논현역 막국수로 제일 많이 찾는 집이죠. 간판이 워낙 쨍해서 처음 가도 헤맬 일은 없겠더라고요! 👀 영수증에는 '강남점', 가게 안 메뉴판에는 '논현점'이라고 적혀 있는데 같은 곳이니 헷갈리지 마세요. 😉", {"keep": 1}),
    ("img", ["9974"]),
    ("p", "🏠 상호: 성천막국수 (논현점·강남점)", {"b": 1}),
    ("p", "🗺 주소: 서울 서초구 강남대로 545-12 1층", {"b": 1}),
    ("p", "🚇 위치: 논현역 5번 출구에서 걸어서 3~4분", {"b": 1}),
    ("p", "⏰ 영업: 평일 11:30~21:00 / 토 11:30~19:00 (11월 방문 기준, 방문 전 확인 추천)", {"b": 1}),
    ("p", "☕ 쉬는 시간: 15:00~17:00 / 주문 마감 평일 14:30·20:30, 토 18:30", {"b": 1}),
    ("p", "📅 휴무: [[r:일요일·공휴일]] (재료 소진 시 일찍 마감)", {"b": 1}),
    ("p", "🚗 주차: [[r:전용 주차장 없음]], 걸어서 10분쯤 거리 공영주차장 이용", {"b": 1}),
    ("p", "저희는 화요일 오후 5시 조금 넘어서 갔는데, 쉬는 시간 끝나자마자라 그런지 [[B:바로 들어가서 한산하게]] 먹었답니다. 점심엔 웨이팅이 생긴다는 얘기가 많으니, 논현역 맛집 중에서도 여긴 저녁 오픈 시간을 노리는 게 무조건 이득이에요! ⏰", {"keep": 1}),

    ("hb", "🏪 소박해서 더 정겨운 노포 분위기"),
    ("img", ["9943", "9944"]),
    ("p", "매장은 테이블이 쭉 놓인 아담한 식당이에요. 주황색 의자에 나무 테이블, 벽에 붙은 메뉴판까지 딱 오래된 국숫집 감성이라 괜히 마음이 편해지더라고요. 🪑 화려하진 않아도 이런 집이 진짜 맛집인 거, 다들 아시죠?", {"keep": 1}),
    ("img", ["9950", "9945"]),
    ("p", "혼자 와서 드시는 분들도 꽤 계셨는데요, 혼밥 1인 메뉴가 따로 있어서 혼밥하기에도 부담 없어 보였답니다. 🍜", {"keep": 1}),
    ("img", ["9947"]),
    ("p", "벽에는 성천막국수의 유래가 적혀 있는데, 이거 꼭 읽어 보세요! 평안남도 성천군이 고향인 창업주께서 1966년에 답십리에서 시작하셨고, 지금 논현점은 손자분이 같은 재료와 같은 맛 그대로 2019년에 열었다고 해요. 60년 가까이 된 맛이라니, 먹기 전부터 괜히 경건해지는 기분이었죠. 🙏", {"keep": 1}),
    ("img", ["9951", "9948"]),
    ("p", "제육은 삼겹살 부위 한판을 [[B:국내산 생고기]]로만 쓴다고 크게 붙어 있었어요. 🐷 벽에 걸린 초록 앞치마도 정겹죠?", {"keep": 1}),
    ("img", ["9946"]),
    ("p", "물은 셀프고, 면수는 말씀드리면 가져다주세요. (이 면수가 나중에 진짜 반전이었답니다..!) 💧", {"keep": 1}),

    ("hb", "💵 메뉴는 딱 막국수와 제육"),
    ("img", ["9949"]),
    ("p", "메뉴는 아주 단출하답니다. 막국수 두 가지에 제육, 그리고 혼밥 메뉴가 전부라서 고민할 틈이 없답니다! 📋", {"keep": 1}),
    ("menu", "🍜 [[y:막국수]]", ["물막국수: 9,000원 (곱빼기 10,000원)", ("[[p:비빔막국수: 9,000원 / 곱빼기 10,000원]]", {"b": 1})]),
    ("menu", "🥩 [[y:제육]]", [("[[p:제육 한 접시 160g: 13,000원]]", {"b": 1}), "제육 반 접시 80g: 6,500원"]),
    ("menu", "🍚 [[y:혼밥 1인 메뉴]]", ["물·비빔막국수 + 제육 40g: 각 11,000원"]),
    ("menu", "🍶 [[y:주류·음료]]", ["소주·맥주: 각 5,000원 / 막걸리 4,000원 / 음료수 2,000원"]),
    ("img", ["9972"]),
    ("p", "비빔막국수는 맵기를 고를 수 있어요. 기본맛, 1단계(열라면 정도), 2단계(불닭볶음 정도)라고 적혀 있으니 매운 거 좋아하시면 참고하세요! 🌶️", {"keep": 1}),
    ("p", "저희는 비빔막국수 하나, 비빔막국수 곱빼기 하나, 그리고 제육 한 접시를 시켜서 [[B:총 32,000원]] 나왔어요. 💳 둘이서 이렇게 먹으니 배가 아주 든든하더라고요!", {"keep": 1}),
    ("img", ["9952"]),
    ("p", "수저통에는 먹는 방법도 적혀 있었어요. 비빔은 양념장에 기름을 더한 맛이고, 숙성 무는 그대로 먹거나 양념장·겨자·식초를 곁들이면 되고, 제육이랑 싸 먹으면 더 맛있대요. 고기 육수는 쓰지 않는다는 문구도 눈에 띄더라고요. 📝", {"keep": 1}),

    ("hb", "😋 오늘 주문한 메뉴, 비빔막국수와 제육"),
    ("p", "오늘 주문한 메뉴는 [[p:비빔막국수, 비빔막국수 곱빼기, 제육 한 접시]]예요!", {"b": 1}),
    ("img", ["9953", "9954"]),
    ("p", "테이블 위에는 양념 3종(양념장·겨자·식초)이 기본 세팅이랍니다. 메뉴판에 적힌 꿀비율은 [[B:양념장 하나에 겨자·식초 반씩]]이라서 저도 그대로 따라 해 봤죠! 🥢", {"keep": 1}),
    ("img", ["9955"]),
    ("p", "직접 숙성시킨 무(짠지)도 같이 나오죠. 그대로 먹어도 되고, 양념을 살짝 곁들여도 된답니다. 🥒", {"keep": 1}),
    ("img", ["9957", "9958"]),
    ("p", "제육이 먼저 나왔답니다! 하얀 접시에 도톰하게 썰린 수육이 가지런히 담겨 나오는데, 한 점 집어 보니 정말 부드럽더라고요. 🥩", {"keep": 1}),
    ("img", ["9956.gif"]),
    ("p", "삼겹살 부위라 비계가 적당히 있는데도 🐖 [[r:잡내가 하나도 없어서]] 계속 손이 가더라고요. 막국수 나오기 전에 벌써 반 접시가 사라졌답니다. 😋", {"keep": 1}),
    ("img", ["9959"]),

    ("hb", "🍜 논현역 맛집 인정, 막국수 탄력 태어나서 처음"),
    ("img", ["9960", "9961"]),
    ("p", "드디어 비빔막국수 등장! 이 비주얼 보고 논현역 맛집 소리 듣는 이유를 바로 알겠더라고요. 👏 거뭇한 메밀면 위에 빨간 양념장이 동그랗게 올라가 있네요. 😍", {"keep": 1}),
    ("img", ["9962"]),
    ("p", "왼쪽이 곱빼기, 오른쪽이 보통인데 곱빼기 양이 확실히 넉넉하죠? 1,000원 차이면 곱빼기가 무조건 이득이에요! 👍", {"keep": 1}),
    ("img", ["9963.gif"]),
    ("p", "그런데 그릇 바닥을 보면 기름이 자작하게 깔려 있거든요? 이걸 양념이랑 같이 쓱쓱 비비면 향이 확 올라온답니다. 🤤", {"keep": 1}),
    ("img", ["9965.gif"]),
    ("p", "[여기에 동영상 넣기: IMG_9966 면 들어 올리는 영상 — 발행 전 이 줄은 지우기]"),
    ("img", ["9967", "9968"]),
    ("p", "한 젓가락 들어 올리는 순간부터 느낌이 달랐어요. 😮 진짜 ✨막국수 중에 이 정도 탄력은 태어나서 처음✨이에요!", {"b": 1}),
    ("p", "메밀면은 보통 툭툭 끊기는 맛인데, 여기는 쫀득하게 탱글거리면서 씹을수록 구수하더라고요. 😳 그리고 아래 들기름이 완전 많이 들어서 엄청나게 맛있어요. 솔직히 미쳤다는 말밖에 안 나오더라고요..! 🔥", {"keep": 1}),
    ("img", ["9969", "9970"]),
    ("p", "양념은 맵기보다 [[r:달달하고 고소한]] 쪽이라 기대 이상이었어요. 😋 제육 한 점 올려서 같이 먹으면 고기의 부드러움이랑 면의 탄력이 어우러져서 그 조합이 진짜 완벽했답니다. 둘 다 말없이 젓가락만 바빴던 건 안 비밀이에요. 🤭", {"keep": 1}),
    ("img", ["9964"]),
    ("p", "마지막은 면수로 마무리했어요. 메밀 삶은 물이라 구수하고 따뜻해서, 비빔막국수 먹고 난 입을 싹 정리해 주더라고요. 이게 또 진짜 별미예요! 꼭 달라고 하세요. 🍵", {"keep": 1}),
    ("img", ["9973"]),

    ("hr",),
    ("hb", "📌 은똥잉의 한 줄 정리"),
    ("p", "👍좋았던 점", {"b": 1}),
    ("p", "[[bl:✨ 탄력이 살아 있는 메밀면에 기름이 듬뿍, 비빔막국수가 정말 맛있어요.]]\n[[bl:✨ 제육이 부드럽고 잡내가 없어서 막국수랑 궁합이 좋아요.]]\n[[bl:✨ 구수한 면수로 마무리하는 맛이 있어요.]]\n[[bl:✨ 평일 저녁 5시쯤엔 한산해서 바로 앉았어요.]]"),
    ("p", "💦아쉬웠던 점", {"b": 1}),
    ("p", "[[o:🚗 전용 주차장이 없어서 걸어서 10분쯤 공영주차장에 세워야 해요.]]\n[[o:📅 일요일·공휴일엔 쉬어요.]]"),
    ("p", "💖재방문의사", {"b": 1}),
    ("p", "🙆‍♀️🙆‍♀️🙆‍♀️🙆‍♀️ 무조건! 다음엔 동치미 국물 물막국수도 꼭 먹어 볼 거예요."),
    ("p", "🎯추천대상", {"b": 1}),
    ("p", "🧡 논현역 근처에서 데이트 저녁 메뉴 고민하시는 분\n🧡 탄력 있는 메밀면 좋아하시는 분\n🧡 혼밥 메뉴 찾으시는 분"),
    ("place", "성천막국수", "강남대로"),
]

TAGS = "#논현역맛집 #성천막국수 #성천막국수논현점 #논현역막국수 #비빔막국수 #막국수맛집 #논현맛집 #논현역데이트 #신논현역맛집 #강남막국수 #제육 #수육맛집 #백년가게 #노포맛집 #논현역혼밥 #메밀국수 #면수 #강남대로맛집"

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
    return f"""<title>성천막국수 초안</title>
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
<div class="meta">은똥잉 · 2026. 11. 17. 방문</div>
{chr(10).join(parts)}
<div class="tags">{tags}</div>
</div>"""


def build_md():
    out = [f"# {TITLE}", ""]
    for blk in B:
        k = blk[0]
        if k == "img":
            out.append(" ".join(f"![IMG_{n}](../photos/sungcheon/blur/IMG_{n}.jpg)" for n in blk[1]))
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
    (OUT / "sungcheon.html").write_text(build_html())
    (OUT / "sungcheon.md").write_text(build_md())
    lines = [l for b in B if b[0] == "p" for l in plain(b[1]).split("\n")]
    print("ok", (OUT / "sungcheon.html").stat().st_size // 1024, "KB",
          "| emoji", sum(len(EMO.findall(l)) for l in lines),
          "| lines w/ emoji %.0f%%" % (100 * sum(1 for l in lines if EMO.search(l)) / len(lines)),
          "| chars", sum(len(plain(b[1])) for b in B if b[0] == "p"))
