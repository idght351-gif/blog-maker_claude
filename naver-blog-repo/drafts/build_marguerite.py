"""마가렛 Marguerite 마곡 (5번 폴더, 11/20 목 저녁, 남편과). 체험단 협찬 → 영수증 리뷰·카드 없음, URL은 사용자가 맨 위에. 템플릿 T4(메뉴 시식 집중).
사진·영상 자리만 표시하고 사용자가 직접 넣는 시험 글 (올릴순서 폴더와 번호 일치)."""
import base64, html, io, re
from pathlib import Path
from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "drafts"
COLORS = {"r": "#f12f22", "p": "#f02c8c", "g": "#00a350", "bl": "#0076c8", "o": "#ff9c23"}
ALIGN = "left"
LINE = 22
PHOTOS = ROOT / "photos" / "marguerite" / "blur"
RESEARCH_DIR = str(ROOT / "data" / "research" / "marguerite")
CROP = {"0101": 0.5, "0102": 0.5, "0103": 0.5, "0106": 0.5, "0124": 0.5, "0130": 0.5, "0131": 0.5}
NOCROP = {"0104", "0105", "0110", "0112", "0114", "0119f", "0120f"}
ROTATE = {}
NDS_QUERY = ""
CATEGORY = "먹보여행"
SPONSORED = True
TEMPLATE_ID = "T1"
LENGTH = "보통"
STORE = "마가렛"
MEMO = {"동행": "남편과 데이트", "메뉴": "문어와 알감자 + 홍새우파스타 + 밤크림 뇨끼 (69,000원, 체험단 60,000원 지원)",
        "최고": ["문어와 알감자", "식전빵"], "문어": "문어 부드러움, 알감자 포슬, 소스 맛있음", "파스타·뇨끼": "파스타가 더 나음",
        "대기": "바로 입장, 한산(목 18시)", "아쉬움": "없음", "재방문": "비바나폴리랑 같은 사장님 가게라서 비바나폴리 피자도 같이 시킬 수 있어. 다음엔 다른 메뉴 먹으러 꼭 방문"}
MAIN_KW = "마곡역 맛집 양식"   # 체험단 필수 키워드
SUB_KWS = ["마가렛", "마곡 맛집 데이트", "뇨끼"]

TITLE = "[마곡역 맛집 양식 마가렛] 문어와 알감자 미쳤다! 비바나폴리 피자까지, 주차 팁"

B = [
    ("img", ["0123"]),
    ("q", "부드러운 문어와 포슬한 알감자 / 비바나폴리 화덕피자까지 한 번에! / 마곡역 3번 출구 이탈리안 데이트 맛집"),
    ("bubble", "사진 미리보기📷"),
    ("img", ["0123", "0124", "0127", "0101"]),
    ("p", "안녕하세요!! 은똥잉이에요 😄"),
    ("p", "이번엔 [[r:마곡역 맛집 양식]] 찾다가 요즘 계속 눈에 밟히던 이탈리안 레스토랑에 다녀왔어요."),
    ("p", "마곡역 화덕피자로 유명한 [[B:비바나폴리 사장님이 2호점으로 낸 곳]]이라는 얘기를 듣고, 남편이랑 목요일 저녁 마곡 맛집 데이트 장소로 바로 찜했답니다 🤍", {"b": 1}),
    ("p", "이번엔 체험단으로 초대받아 다녀왔는데요, 문어 요리 하나 때문에 벌써 재방문 각이 섰다는 거..! 😳"),

    ("h", "📍 마곡역 맛집 양식 마가렛 매장 정보 & 이용 팁 / (위치·주차·예약)"),
    ("img", ["0101", "0102"]),
    ("p", "🏡 상호: 마가렛 Marguerite (비바나폴리 2호점)", {"b": 1}),
    ("p", "🗺 주소: 서울 강서구 마곡중앙6로 10 1층 115호 (마곡역센트럴푸르지오시티)", {"b": 1}),
    ("p", "🚃 위치: 마곡역 [[r:3번 출구 2~3분]], 나와서 왼쪽으로 몇 걸음이면 남색 타일 외관이 바로 보여요!", {"b": 1}),
    ("p", "⏰ 영업시간: 11:30~21:30 (브레이크 15:00~17:00, 라스트오더 20:30 / 11월 방문 기준)", {"b": 1}),
    ("p", "📅 휴무: [[r:매주 화요일]] 정기휴무", {"b": 1}),
    ("p", "🚗 주차 꿀팁: 건물 지하주차장 이용하면 [[r:주차 지원]]이 돼서 자차 방문도 걱정 없음", {"b": 1}),
    ("img", ["0103"]),
    ("p", "⏰ 웨이팅 정보: 목요일 저녁 6시쯤 방문했는데 바로 입장, 매장도 한산했어요", {"b": 1}),
    ("p", "📝 예약: 네이버 예약이 되니까 주말 저녁이나 연말 모임이면 예약하고 가는 게 마음 편해요", {"b": 1}),
    ("p", "가게 앞에는 파라솔 테라스석도 쭉 놓여 있어서 날 풀리면 여기서 와인 한 잔 하기 딱 좋겠더라고요 🍷 해 지고 나서 노란 조명이 켜지니까 완전 유럽 골목 식당 같은 분위기였어요!"),

    ("h", "🏠 매장 내부 & 분위기 (오픈 키친·테이블 구성)"),
    ("img", ["0106", "0121"]),
    ("p", "안으로 들어가면 하얀 벽돌 벽에 나무 바닥, 벽에 걸린 액자들까지 깔끔한 이탈리안 비스트로 느낌이에요 🤍 조명도 은은해서 사진이 진짜 예쁘게 나오더라고요. 테이블 간격도 넉넉해서 옆 테이블 신경 안 쓰고 둘이 얘기하기 딱 좋았답니다."),
    ("img", ["0122", "0120f"]),
    ("p", "🪑 매장 구조: 창가 자리와 4인 테이블 위주라 데이트는 물론 가족·연말 모임으로도 좋아요", {"b": 1}),
    ("img", ["0115", "0116"]),
    ("img", ["0119f"]),
    ("p", "오픈 키친 위에 [[B:'PASTA IS A GOOD IDEA']] 간판이 걸려 있는데 보자마자 웃음이 나왔어요 🤭"),
    ("p", "주방이 훤히 보여서 믿음이 가는 것도 장점이랍니다 👨‍🍳 요리하시는 모습을 구경하는 재미도 쏠쏠했어요!"),
    ("img", ["0107"]),
    ("p", "테이블마다 Marguerite 로고 냅킨과 소금·후추가 세팅돼 있어서 작은 디테일까지 정성이 느껴지더라고요."),

    ("h", "📋 마가렛 전체 메뉴 & 가격표 (비바나폴리 메뉴까지)"),
    ("img", ["0104"]),
    ("p", "메뉴판 보고 진짜 깜짝 놀랐답니다! 왼쪽은 마가렛 메뉴, 오른쪽은 [[p:비바나폴리 메뉴]]예요.", {"b": 1}),
    ("p", "같은 사장님 가게라서 [[B:비바나폴리 화덕피자도 여기서 같이 주문]]할 수 있답니다 🍕 다음엔 파스타랑 피자를 같이 시켜서 먹어 볼 생각이에요!"),
    ("img", ["0105"]),
    ("img", ["0110", "0112", "0114"]),
    ("p", "주문은 테이블 태블릿으로 하면 되고, 메뉴 사진이 다 나와 있어서 고르기 편하더라고요 📱 처음 가는 분들도 사진 보고 고르면 실패할 일은 없겠죠?"),
    ("menu", "🦑 [[y:안티(전채)]]", [("[[p:문어와 알감자: 21,000원]]", {"b": 1}), "아란치니: 13,000원", "카넬로니: 19,000원", "트러플 감자튀김: 11,000원"]),
    ("menu", "🥔 [[y:뇨끼]]", ["트러플 뇨끼: 28,000원", ("[[p:밤크림 뇨끼: 24,000원]]", {"b": 1}), "고르곤졸라 뇨끼: 21,000원", "시즌 뇨끼: 24,000원"]),
    ("menu", "🍝 [[y:파스타]]", ["클래식 까르보나라·트러플 알프레도: 39,000원", "봉골레: 22,000원", ("[[p:홍새우파스타: 24,000원]]", {"b": 1}), "버섯크림리조또: 23,000원"]),
    ("menu", "🥩 [[y:스테이크·디저트]]", ["채끝 스테이크: 58,000원", "티라미수: 10,000원"]),
    ("p", "🏷️ 원산지: 쌀·쇠고기 국내산, 새우 아르헨티나산 (메뉴판 표기)", {"b": 1}),
    ("p", "마곡역 맛집 양식 데이트로 저희는 문어와 알감자, 홍새우파스타, 밤크림 뇨끼까지 세 가지를 골라 [[B:총 69,000원]]이었어요. 메뉴당 2만 원대라 가격대는 있는 편이지만 둘이 데이트로 먹기엔 딱 알맞은 양이었답니다."),

    ("h", "😋 오늘 주문한 메뉴 솔직 시식 / (문어와 알감자·홍새우파스타·밤크림 뇨끼)"),
    ("p", "오늘 주문한 메뉴는 [[p:문어와 알감자, 홍새우파스타, 밤크림 뇨끼]]예요!", {"b": 1}),
    ("p", "🥖 [[y:식전빵]]", {"b": 1}),
    ("img", ["0117", "0118"]),
    ("p", "식사 전에 따끈한 식전빵이 먼저 나와요. 스프레드를 듬뿍 발라 먹었는데 이게 진짜 맛있더라고요!"),
    ("p", "솔직히 이번 방문에서 제일 맛있었던 걸 꼽으라면 ✨문어랑 이 식전빵✨이에요 💛", {"b": 1}),
    ("img", ["0136", "0137"]),
    ("p", "피클이랑 당근 라페도 같이 나와서 중간중간 입가심하기 좋았답니다 🥕 새콤한 피클 덕분에 크림 메뉴도 끝까지 부담 없었죠!"),

    ("p", "🐙 [[y:문어와 알감자]] (21,000원)", {"b": 1}),
    ("img", ["0123", "0125"]),
    ("p", "드디어 오늘의 주인공! 문어 다리가 통으로 올라가고 옆에 알감자가 함께 나와요."),
    ("p", "[여기에 동영상 넣기: 문어 썰어 먹는 영상 — 발행 전 이 줄은 지우기]"),
    ("p", "한 입 먹자마자 ✨문어가 정말 부드러워서✨ 깜짝 놀랐어요! 질기다는 느낌이 하나도 없었답니다 😍", {"b": 1}),
    ("img", ["0129", "0134", "0135"]),
    ("p", "가까이서 보면 문어 위에 고소한 토핑이 솔솔 뿌려져 있고, 알감자는 반으로 갈라 소스를 듬뿍 얹어 먹게 나와요. 한 접시 안에 식감이 이렇게 다양하다니, 먹는 내내 즐거웠답니다 🤭"),
    ("p", "알감자는 포슬포슬해서 문어랑 같이 먹으니 식감이 딱 맞더라고요 🥔"),
    ("p", "그리고 아래 깔린 [[r:소스가 진짜 맛있어서]] 소스 때문에라도 또 오고 싶어요.", {"b": 1}),
    ("p", "문어+알감자+소스 한 번에 올려서 먹으면 후..🤦‍♀️👍"),
    ("p", "마곡역 맛집 양식 찾으시는 분들이라면 이건 무조건 시켜야 하는 메뉴랍니다! 정말 강력 추천해요 👍"),

    ("p", "🦐 [[y:홍새우파스타]] (24,000원)", {"b": 1}),
    ("img", ["0124", "0130"]),
    ("p", "통통한 홍새우가 올라가고 위에 초록 루꼴라가 수북하게 얹어진 파스타예요. 비주얼부터 완전 상큼하죠? 사진 찍는 손이 바빴답니다 📸"),
    ("img", ["0131"]),
    ("p", "면을 집게로 쭉 들어 올려 보니 소스가 골고루 잘 배어 있더라고요 🍝"),
    ("p", "뇨끼랑 비교하면 저희는 [[B:이 파스타가 더 좋았어요]]. 둘 중 하나만 고른다면 파스타 쪽을 추천할게요!", {"b": 1}),

    ("p", "🌰 [[y:밤크림 뇨끼]] (24,000원)", {"b": 1}),
    ("img", ["0127", "0128"]),
    ("p", "하얀 크림 위에 바삭한 토핑이 올라간 밤크림 뇨끼랍니다. 마가렛이 뇨끼로도 유명해서 메뉴판에 뇨끼만 네 종류가 있더라고요!"),
    ("img", ["0132.gif"]),
    ("p", "숟가락으로 크림을 듬뿍 떠서 뇨끼랑 같이 먹으면 돼요. 뇨끼 하나하나에 크림이 넉넉하게 묻어 나온답니다."),
    ("img", ["0133"]),
    ("p", "뇨끼도 무난하게 맛있었는데, 다른 두 메뉴가 워낙 강해서 상대적으로 덜 기억에 남았어요 😅 크림 좋아하시는 분들은 한 번 드셔 볼 만해요."),

    ("h", "✨ 마가렛 솔직 총평"),
    ("p", "📌 좋았던 점", {"b": 1}),
    ("p", "[[bl:✔️ 질기지 않고 정말 부드러운 문어와 포슬한 알감자, 맛있는 소스]]\n[[bl:✔️ 스프레드 듬뿍 발라 먹는 식전빵이 최고]]\n[[bl:✔️ 비바나폴리 화덕피자까지 같이 주문 가능]]\n[[bl:✔️ 마곡역 3번 출구 2~3분, 건물 주차 지원]]"),
    ("p", "📌 아쉬운 점", {"b": 1}),
    ("p", "[[o:✔️ 딱히 없었어요. 굳이 꼽자면 메뉴당 2만 원대라 여러 개 시키면 가격이 올라가는 정도]]"),
    ("p", "📌 재방문 의사 및 총평: 🙆‍♀️🙆‍♀️🙆‍♀️🙆‍♀️", {"b": 1}),
    ("p", "✔️ 부드러운 문어 하나로 마곡 데이트 코스 확정! 다음엔 다른 메뉴 먹으러 꼭 다시 올 거예요."),
    ("p", "마곡역 근처에서 분위기 좋은 양식 데이트 장소 찾으신다면, 혹은 파스타랑 화덕피자를 한 번에 먹고 싶은 날이라면 마가렛에서 문어와 알감자 꼭 드셔 보세요 🫶 오늘도 끝까지 읽어 주셔서 감사해요!"),
    ("place", "마가렛", "마곡중앙6로"),
]

TAGS = "#마곡역맛집양식 #마가렛 #마곡마가렛 #마가렛Marguerite #마곡맛집데이트 #마곡역맛집 #마곡양식 #마곡뇨끼 #문어와알감자 #홍새우파스타 #밤크림뇨끼 #마곡데이트 #비바나폴리 #마곡이탈리안 #마곡파스타 #마곡중앙6로맛집"

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
    return f"""<title>마가렛 초안</title>
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
<div class="meta">은똥잉 · 2026. 11. 20. 방문</div>
{chr(10).join(parts)}
<div class="tags">{tags}</div>
</div>"""


def build_md():
    out = [f"# {TITLE}", ""]
    for blk in B:
        k = blk[0]
        if k == "img":
            out.append(" ".join(f"![IMG_{n}](../photos/marguerite/blur/IMG_{n}.jpg)" for n in blk[1]))
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
    (OUT / "marguerite.html").write_text(build_html())
    (OUT / "marguerite.md").write_text(build_md())
    lines = [l for b in B if b[0] == "p" for l in plain(b[1]).split("\n")]
    print("ok", (OUT / "marguerite.html").stat().st_size // 1024, "KB",
          "| emoji", sum(len(EMO.findall(l)) for l in lines),
          "| lines w/ emoji %.0f%%" % (100 * sum(1 for l in lines if EMO.search(l)) / len(lines)),
          "| chars", sum(len(plain(b[1])) for b in B if b[0] == "p"))
