"""비바나폴리(VIVA! NAPOLI) 마곡 화덕피자 (8번 폴더). 체험단 협찬 글 → 영수증 리뷰·내돈내산 카드 없음, 맨 위 광고 링크."""
import base64, html, io, re
from pathlib import Path
from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "drafts"
COLORS = {"r": "#f12f22", "p": "#f02c8c", "g": "#00a350", "bl": "#0076c8", "o": "#ff9c23"}
ALIGN = "left"
LINE = 22
PHOTOS = ROOT / "photos" / "vivanapoli" / "blur"
RESEARCH_DIR = str(ROOT / "data" / "research" / "vivanapoli")
CROP = {"9899": 0.45, "9858": 0.5, "9860": 0.45, "9881": 0.62, "9895": 0.55}
NOCROP = {"9865", "9867", "9869", "9871", "9872", "9873", "9874", "9875", "9898"}   # 메뉴 화면·안내 카드는 자르지 않음
ROTATE = {}
NDS_QUERY = ""   # 협찬 글: 내돈내산 카드 없음
CATEGORY = "먹보여행"
SPONSORED = True
MAIN_KW = "마곡역 맛집 피자"   # 체험단 필수 키워드
SUB_KWS = ["마곡 화덕피자", "비바나폴리", "마곡 데이트"]

TITLE = "[마곡역 맛집 피자 비바나폴리] 화덕 디아볼라·깔라마리, 역 바로 앞 🍕"

B = [
    ("p", "[광고 링크 필요]"),
    ("img", ["9892"]),
    ("p", "월요일 저녁, 마곡역 3번 출구로 나오자마자 [[r:노란 불빛 테라스]]가 반겨주는 피자집에 다녀왔어요. 🍕"),
    ("p", "검색창에 마곡역 맛집 피자를 치면 꼭 나오던 곳, [[p:비바나폴리]]예요.", {"b": 1}),
    ("p", "나폴리 피자 장인 인증서가 걸린 화덕피자집이라 오기 전부터 기대가 컸답니다. ✨"),
    ("p", "피자, 튀김, 수프에 생맥주까지 골고루 먹어본 솔직한 후기 시작할게요! 😊"),
    ("q", "마곡역 3번 출구 바로 앞 / 화덕에서 구운 나폴리 피자 / 테라스까지 있는 마곡 데이트 코스 🇮🇹"),

    ("h", "📍 마곡역 맛집 피자 비바나폴리 위치"),
    ("img", ["9899"]),
    ("p", "힐스테이트 에코 마곡역 1층에 있고, 파란 줄무늬 차양이 멀리서도 잘 보여요. 👀"),
    ("p", "역에서 나오면 정말 몇 걸음이라 비 오는 날에도 부담 없이 갈 수 있겠더라고요."),
    ("img", ["9858"]),
    ("p", "가게 앞에는 파라솔을 펼친 테라스 자리가 따로 있어요."),
    ("img", ["9859"]),
    ("p", "11월이라 저녁엔 쌀쌀해서 저희는 안에 앉았지만, 날 풀리면 [[B:테라스에서 맥주 한잔]] 꼭 해보고 싶었어요. 🍺"),
    ("img", ["9860"]),
    ("p", "입구 위에 ANTICA PIZZERIA VIVA NAPOLI라고 적혀 있는데, 이탈리아 골목 가게에 온 기분이었어요."),
    ("p", "🏠 상호명: 비바나폴리 (VIVA! NAPOLI)", {"b": 1}),
    ("p", "🗺 주소: 서울 강서구 마곡중앙로 76 힐스테이트 에코 마곡역 1층 101호", {"b": 1}),
    ("p", "🚇 대중교통: 5호선 마곡역 3번 출구 바로 앞", {"b": 1}),
    ("p", "⏰ 영업시간: 11:30 ~ 21:30 (브레이크타임 15:00 ~ 17:00)", {"b": 1}),
    ("p", "📅 휴무: [[r:매주 화요일]]", {"b": 1}),
    ("p", "🚗 주차: 건물 지하주차장 이용", {"b": 1}),
    ("p", "주말 저녁엔 자리가 금방 찬다고 하니 네이버 예약을 하고 가는 게 마음 편해요. 😉"),

    ("h", "🏪 작은 나폴리 같은 매장 분위기"),
    ("img", ["9862"]),
    ("p", "하얀 테이블에 원목 테두리, 줄무늬 화병까지 놓여 있어서 사진이 잘 나와요. 📸"),
    ("img", ["9863"]),
    ("p", "테이블마다 QR 코드가 있어서 휴대폰으로 메뉴를 보고 주문할 수 있어요."),
    ("img", ["9880"]),
    ("p", "카운터 뒤로는 \"Dove nasce la pizza, inizia il vero gusto\"라는 문구가 걸려 있어요."),
    ("p", "피자가 태어나는 곳에서 진짜 맛이 시작된다는 뜻이래요. 🇮🇹"),
    ("img", ["9879"]),
    ("p", "벽에는 [[r:나폴리 피자 장인 협회]] 인증서 두 장이 나란히 걸려 있었어요."),
    ("img", ["9877", "9878"]),
    ("p", "냉장고에는 페로니, 메나브레아 같은 이탈리아 맥주와 레몬 음료가 가득했어요. 🍋"),
    ("p", "병맥주 라벨만 봐도 여행 온 기분이 들어서 괜히 한참 구경했어요."),
    ("img", ["9898"]),
    ("p", "자리에 놓인 안내 카드도 꼼꼼히 읽어봤어요. 📝"),
    ("p", "작은 매장이라 계산은 자리에서 직원분을 부르면 도와주신대요."),
    ("p", "피클이랑 타바스코, 페퍼론치노는 기본으로 나오지 않지만 말하면 가져다주신대요."),
    ("p", "예약이 이어질 땐 이용 시간이 [[B:1시간 30분]]으로 정해져 있다고 하니 참고하세요!"),

    ("h", "💵 비바나폴리 메뉴 & 가격"),
    ("img", ["9865", "9867"]),
    ("img", ["9869", "9871"]),
    ("p", "메뉴는 전채, 파누오쪼, 피자, 파스타, 와인까지 꽤 다양해요."),
    ("menu", "🥗 [[y:전채·프리타티네]]", [
        "부라타 샐러드: 18,000원",
        ("[[p:깔라마리: 16,000원]]", {"b": 1}),
        "폴포 마리나토: 19,000원",
        "프리타티네 바질·카르보나라: 각 10,000원",
        ("[[p:베이컨 포테이토 수프: 4,500원]]", {"b": 1}),
    ]),
    ("menu", "🍕 [[y:피자]]", [
        "마리나라 디 비바: 17,000원",
        "마르게리타: 22,000원",
        ("[[p:디아볼라: 21,000원]]", {"b": 1}),
        "비바 클라시카: 28,000원",
        "트러플 부라타: 39,000원",
        "부라타 추가: 6,500원",
    ]),
    ("menu", "🍺 [[y:주류]]", [
        ("[[p:페로니 생맥주 330ml: 8,500원]]", {"b": 1}),
        "와인 글라스: 11,000원",
    ]),
    ("p", "피자 한 판이 2만 원대라 [[o:가볍게 먹기엔 살짝 부담]]되는 가격이에요."),
    ("p", "그래도 화덕 나폴리 피자 전문점이라 이 정도면 납득이 갔어요. 👍"),
    ("p", "마곡 화덕피자 집 중에서도 메뉴 구성이 알찬 편이라 두세 명이 나눠 먹기 좋아요."),
    ("img", ["9872", "9873"]),
    ("img", ["9874", "9875"]),
    ("p", "저희는 수프, 깔라마리, 디아볼라에 페로니 생맥주 두 잔을 골랐어요."),

    ("h", "😋 베이컨 포테이토 수프 & 페로니 생맥주"),
    ("p", "오늘 주문한 메뉴는 [[p:베이컨 포테이토 수프, 깔라마리, 디아볼라, 페로니 생맥주]]예요!", {"b": 1}),
    ("img", ["9881"]),
    ("p", "음식 나오기 전에 페로니 생맥주로 먼저 짠! 🍻"),
    ("p", "거품이 쫀쫀하고 탄산이 시원해서 피자랑 먹기 딱 좋은 라거였어요."),
    ("img", ["9884"]),
    ("p", "수프는 강원도 두백감자로 끓였다고 해요."),
    ("img", ["9889.gif"]),
    ("p", "위에 크루통과 베이컨, 파슬리가 올라가 있어요."),
    ("img", ["9882.gif"]),
    ("p", "한 숟갈 떠먹어 보니 ✨감자가 곱게 갈려서 부드럽고 고소✨했어요.", {"b": 1}),
    ("img", ["9890"]),
    ("p", "4,500원이라 부담 없이 시키기 좋은데, 양이 적은 편이라 한 사람당 하나씩 시켜도 좋겠어요. 🥣"),
    ("p", "따뜻한 수프로 속을 먼저 데우니 쌀쌀한 날씨에 딱이었어요."),

    ("h", "🦑 세몰리나로 튀긴 나폴리식 깔라마리"),
    ("img", ["9885"]),
    ("p", "메뉴판에 BEST라고 붙어 있던 깔라마리예요."),
    ("p", "이탈리아 밀가루인 세몰리나로 튀겨서 레몬, 소스와 같이 나와요."),
    ("img", ["9883.gif"]),
    ("p", "튀김옷이 얇고 [[r:바삭바삭]]해서 기름진 느낌이 덜했어요. 😋"),
    ("img", ["9887.gif"]),
    ("p", "주황빛 소스에 콕 찍어 먹으니 새콤하면서 살짝 매콤했어요. 🌶️"),
    ("img", ["9888"]),
    ("p", "오징어 몸통이 두툼해서 쫄깃하게 씹히는 맛이 좋았답니다. 🦑"),
    ("img", ["9891.gif"]),
    ("p", "레몬즙을 뿌리면 훨씬 상큼해져서 맥주 안주로 [[B:손이 계속 가요]]."),

    ("h", "🍕 매콤한 화덕피자, 디아볼라"),
    ("img", ["9893"]),
    ("p", "드디어 메인인 디아볼라가 나왔어요! 🔥"),
    ("p", "살라미와 하얀 모차렐라가 듬뿍 올라간 이탈리아식 매운 피자예요. 🍅"),
    ("img", ["9894.gif"]),
    ("p", "가장자리 코르니초네가 봉긋하게 부풀어 있고, 화덕에 그을린 [[r:까만 점]]이 군데군데 있어요."),
    ("img", ["9895"]),
    ("p", "한 조각 들어 올리니 치즈가 쭉 늘어나요. 🤤"),
    ("img", ["9896"]),
    ("p", "도우 끝은 겉이 살짝 바삭하고 속은 ✨쫄깃하고 촉촉✨했어요.", {"b": 1}),
    ("img", ["9897"]),
    ("p", "살라미는 짭조름하면서 끝에 매콤함이 올라오는데, 맵찔이도 먹을 만한 정도였어요."),
    ("p", "도우가 얇아서 둘이서 한 판은 금방 비우게 돼요. 배가 많이 고프다면 피자 두 판을 추천해요! 🍕"),
    ("p", "마곡역 맛집 피자 찾는 분들께 첫 피자로는 디아볼라를 자신 있게 추천할게요."),
    ("p", "매콤한 피자 한 입, 시원한 생맥주 한 모금 조합이 정말 잘 어울렸어요. 🍻"),
    ("p", "식사 마치고 나오니 테라스 조명이 더 예뻐져 있어서, 마곡 데이트 코스로도 손색없겠다 싶었어요. 🌙"),

    ("hr",),
    ("h", "📋 비바나폴리 후기 종합"),
    ("p", "⭕ 좋았던 점", {"b": 1}),
    ("p", "[[bl:✨ 마곡역 3번 출구 바로 앞이라 찾아가기 쉬워요.]]\n[[bl:✨ 화덕에 구운 도우가 쫄깃하고 불향이 살아 있어요.]]\n[[bl:✨ 깔라마리가 바삭해서 맥주 안주로 최고예요.]]\n[[bl:✨ 테라스와 소품 덕분에 데이트 분위기가 나요.]]"),
    ("p", "❌ 아쉬웠던 점", {"b": 1}),
    ("p", "[[o:💵 피자 한 판에 2만 원대라 가격대가 있는 편이에요.]]\n[[o:⏰ 예약이 이어지면 이용 시간이 1시간 30분이에요.]]"),
    ("p", "🔄 재방문 의사: 🙆‍♀️🙆‍♀️🙆‍♀️🙆‍♀️", {"b": 1}),
    ("p", "👍 다음엔 테라스에서 마르게리타랑 와인 한 잔 할래요!"),
    ("p", "🎯 추천대상", {"b": 1}),
    ("p", "🧡 마곡역 맛집 피자를 찾는 분들\n🧡 화덕 나폴리 피자를 좋아하는 분들\n🧡 분위기 좋은 마곡 데이트 장소가 필요한 분들"),
    ("p", "🌈직접 먹어보고 느낀 그대로 솔직하게 작성한 마곡 비바나폴리 후기입니다.", {"b": 1}),
    ("place", "비바나폴리", "마곡중앙로"),
]

TAGS = "#마곡역맛집피자 #비바나폴리 #마곡비바나폴리 #마곡역맛집 #마곡맛집 #마곡화덕피자 #마곡피자맛집 #마곡데이트 #마곡역데이트 #나폴리피자 #화덕피자맛집 #디아볼라 #깔라마리 #마곡파스타 #강서구맛집 #힐스테이트에코마곡역 #마곡이탈리안 #페로니생맥주"

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
    return f"""<title>비바나폴리 초안</title>
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
<div class="meta">은똥잉 · 2026. 11. 16. 방문</div>
{chr(10).join(parts)}
<div class="tags">{tags}</div>
</div>"""


def build_md():
    out = [f"# {TITLE}", ""]
    for blk in B:
        k = blk[0]
        if k == "img":
            out.append(" ".join(f"![IMG_{n}](../photos/vivanapoli/blur/IMG_{n}.jpg)" for n in blk[1]))
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
    (OUT / "vivanapoli.html").write_text(build_html())
    (OUT / "vivanapoli.md").write_text(build_md())
    lines = [l for b in B if b[0] == "p" for l in plain(b[1]).split("\n")]
    print("ok", (OUT / "vivanapoli.html").stat().st_size // 1024, "KB",
          "| emoji", sum(len(EMO.findall(l)) for l in lines),
          "| lines w/ emoji %.0f%%" % (100 * sum(1 for l in lines if EMO.search(l)) / len(lines)),
          "| chars", sum(len(plain(b[1])) for b in B if b[0] == "p"))
