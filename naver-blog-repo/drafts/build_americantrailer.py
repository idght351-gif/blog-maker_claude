"""아메리칸트레일러 원그로브점 리뷰 초안 (3번 폴더, 2026-10-31 방문). 블록 형식은 build_kurokame.py 참고."""
import base64, html, io, re
from pathlib import Path
from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
PHOTOS = ROOT / "photos" / "americantrailer" / "blur"   # 얼굴 모자이크 끝난 사진 (깃 제외)
OUT = ROOT / "drafts"
RESEARCH_DIR = str(ROOT / "data" / "research" / "americantrailer")

CROP = {"9414": 0.5, "9421": 0.45, "9422": 0.55, "9424": 0.5}
COLORS = {"r": "#f12f22", "p": "#f02c8c", "g": "#00a350", "bl": "#0076c8", "o": "#ff9c23"}

NDS_QUERY = "아메리칸트레일러"
MAIN_KW = "원그로브 카페"
SUB_KWS = ["마곡 원그로브", "아메리칸트레일러 메뉴", "자몽주스", "착즙주스", "마곡역"]
ALIGN = "left"
LINE = 22

TITLE = "[원그로브 카페] 아메리칸트레일러 착즙 자몽주스 XL 6,990원 솔직후기 🍹"

B = [
    ("img", ["9422"]),
    ("p", "토요일 오후, 마곡 원그로브에서 장을 보다가 [[i:상큼한 게 너무 당기더라고요.]] 🍊"),
    ("p", "그래서 요즘 원그로브 카페 중에 줄이 끊이지 않는 [[r:아메리칸트레일러 원그로브점]]에 들러봤어요! 😊", {"b": 1}),
    ("p", "스타필드·용산 같은 큰 몰에서만 보던 착즙주스 브랜드가 마곡에도 생겨서 ✨궁금했던 곳✨이에요."),
    ("q", "눈앞에서 바로 짜주는 착즙주스 / 자몽주스 XL 한 컵 6,990원! / 유기농 사탕수수 시럽 사용 🍹"),
    ("bubble", "사진 미리보기📷"),
    ("img", ["9422", "9411", "9420", "9424"]),

    ("h", "📍 원그로브 카페 아메리칸트레일러 위치 & 영업정보"),
    ("img", ["9411"]),
    ("p", "원그로브몰 B동 1층에 있어서, 빨간 간판과 [[B:흑백 체크무늬 바닥]]이 멀리서도 바로 눈에 띄어요. 🚩"),
    ("p", "방문 전에 알아두시면 좋은 정보부터 정리해 드릴게요!"),
    ("p", "🏠 상호명: 아메리칸트레일러 원그로브점", {"b": 1}),
    ("p", "🗺 주소: 서울 강서구 공항대로 165 원그로브 B동 1층 119호", {"b": 1}),
    ("p", "🚇 대중교통: 5호선 마곡역 근처 원그로브몰 안", {"b": 1}),
    ("p", "⏰ 영업시간: 매일 10:30 ~ 22:00", {"b": 1}),
    ("p", "🚗 주차 정보: 원그로브몰 지하주차장 (몰 안에서 [[r:2만 원 이상 결제 시]] 1시간 무료)", {"b": 1}),
    ("p", "💡 주문 팁: 키오스크 없이 카운터에서 직원분께 바로 주문하고, 번호가 불리면 픽업대에서 받아요.", {"b": 1}),
    ("p", "저는 토요일 오후 2시쯤 갔는데 주문 줄은 짧았고, 음료도 금방 나왔어요. 👍"),

    ("h", "🏪 미국 감성 가득한 매장 분위기"),
    ("img", ["9420"]),
    ("p", "카운터 앞에 [[g:오렌지·레몬·자몽]]이 바구니마다 산처럼 쌓여 있어서 보기만 해도 상큼해지는 기분이에요. 🍋"),
    ("p", "과일 색이 워낙 쨍해서 사진이 저절로 예쁘게 나오더라고요."),
    ("img", ["9425.gif"]),
    ("p", "주문이 들어가면 카운터 안쪽 착즙기에서 [[r:바로바로 과일을 짜주는]] 모습을 볼 수 있어요. ✨", {"b": 1}),
    ("p", "기다리는 동안 구경하는 재미가 쏠쏠했답니다."),
    ("p", "음료 하나에 과일이 몇 개씩 들어가는지 직접 보니까 가격이 조금은 이해가 되더라고요."),
    ("p", "빨간 의자와 원형 테이블이 매장 앞에 놓여 있어서, 테이크아웃만 되는 다른 지점과 달리 [[B:앉아서 마시고 갈 수 있어요.]] 🪑"),

    ("h", "💵 아메리칸트레일러 메뉴 & 가격"),
    ("img", ["9414"]),
    ("p", "아메리칸트레일러 메뉴판은 노란 바탕에 빨간 글씨라 한눈에 들어와요."),
    ("p", "착즙주스, 에이드, 스무디, 커피까지 종류가 정말 많아서 처음 가면 한참 고민하게 돼요. 😲"),
    ("menu", "🍊 [[y:착즙 주스]] (XL / 트렌타)", [
        "오렌지 주스: 6,990원 / 12,990원",
        ("[[p:자몽 주스: 6,990원 / 12,990원]]", {"b": 1}),
        "트리플비타민주스: 7,490원 / 13,990원",
    ]),
    ("menu", "🍋 [[y:레몬에이드]] (XL / 트렌타)", [
        "레몬에이드: 5,990원 / 10,990원", "더블더블 레몬에이드: 7,990원 (XL)",
        "스트로베리·그린애플·체리 레몬에이드: 각 6,990원 / 12,990원",
    ]),
    ("menu", "🧊 [[y:티 & 에이드]]", [
        "레몬·복숭아 아이스티: 3,990원 / 5,490원 (샷 추가 500원)",
        "오미자 레몬티·체리콕: 각 4,990원", "진저에이드: 5,990원", "모히토: 6,990원",
    ]),
    ("menu", "🍌 [[y:바나나 스무디]] (XL)", [
        "망고바나나·딸기바나나: 6,490원", "케일 아몬드 바나나: 6,490원", "인삼 바나나: 6,990원",
    ]),
    ("menu", "🍶 [[y:보틀]]", [
        "디톡스워터 보틀 1L: 8,990원", "레몬보틀 X10: 9,900원", "레몬버킷 X100: 59,000원",
    ]),
    ("img", ["9415"]),
    ("p", "카운터 앞 POP에는 새로 나온 레몬에이드 \"FIVE\"와 바나나 주스가 크게 소개되어 있었어요. 🍹"),
    ("img", ["9418"]),
    ("p", "사과·비트·당근이 들어간 [[y:ABC 주스]] 시즌 안내도 있었는데, 집에서 만들기 번거로운 ABC주스를 한 컵에 사 먹을 수 있어서 좋겠더라고요. 🥕"),
    ("img", ["9419"]),
    ("p", "사이즈는 [[B:500ml 보틀, 1L 보틀, 24oz(XL), 30oz(트렌타)]] 네 가지예요. 📏"),
    ("p", "보틀에 받으면 음료값에 500ml는 3,000원, 1L는 3,500원 정도가 더해진다고 해요. 텀블러처럼 계속 쓸 수 있어서 보틀을 고르는 분들도 많더라고요."),
    ("p", "착즙 주스가 XL 기준 7천 원 안팎이라 [[B:싼 편은 아니지만]], 컵이 커서 둘이 나눠 마셔도 넉넉해요. 저는 [[p:자몽 주스 XL]]로 주문했어요! 🍊", {"b": 1}),

    ("h", "😋 원그로브 카페 자몽주스 솔직 후기"),
    ("p", "오늘 주문한 메뉴는 [[p:자몽 주스 XL]] 한 잔이에요! 🍹", {"b": 1}),
    ("img", ["9421"]),
    ("p", "성조기 무늬 'AT' 슬리브를 끼워주시는데, 컵이 손에 꽉 찰 만큼 커서 한 손으로 들기 묵직했어요. 🇺🇸"),
    ("img", ["9424"]),
    ("p", "투명한 컵 너머로 [[g:연한 핑크빛 자몽 과즙]]이 그대로 보여요. 얼음도 넉넉하게 들어 있어요. 🧊"),
    ("p", "한 모금 마시자마자 ✨생자몽 특유의 새콤쌉싸름한 맛✨이 확 퍼져요! 😋", {"b": 1}),
    ("p", "시판 주스처럼 달기만 한 맛이 아니라, 끝에 남는 [[r:은은한 쌉쌀함]]이 갓 짠 주스라는 걸 알려주더라고요."),
    ("p", "과육 알갱이도 조금씩 씹혀서 마시는 내내 과일을 먹는 느낌이 들었어요."),
    ("img", ["9417"]),
    ("p", "단맛은 [[B:유기농 사탕수수 시럽]]으로 맞춘다고 해요. 정제 과정을 거치지 않은 유기농 비정제 설탕이라는 안내문이 매장에 붙어 있었어요. 🌾"),
    ("p", "그래서인지 단맛이 튀지 않고 자몽 맛을 살짝 받쳐주는 정도였어요."),
    ("img", ["9416"]),
    ("p", "벽에는 1리터 레몬보틀(9,900원)과 레몬버킷(59,000원) 안내도 있었어요. 비타민C 레몬수로 물에 타 먹는 방법까지 적혀 있어요. 💡"),
    ("p", "양이 넉넉해서 원그로브 한 바퀴 다 돌 때까지 [[B:끝까지 시원하게]] 마셨답니다. 🥰"),
    ("p", "식사 후 커피 대신 입가심할 음료를 찾는다면, 원그로브 카페 중에서 이만한 선택지가 없을 것 같아요."),

    ("h", "💡 아메리칸트레일러 200% 즐기는 꿀팁"),
    ("p", "직접 가보고 알게 된 소소한 팁들을 모아봤어요!"),
    ("p", "1️⃣ 둘이 간다면 [[B:XL 한 잔 + 빨대 두 개]]로도 충분해요. 컵이 정말 커요."),
    ("p", "2️⃣ 텀블러가 필요했다면 보틀 옵션을 노려보세요. 음료를 담아 주는 보틀을 그대로 가져갈 수 있어요."),
    ("p", "3️⃣ 주차하셨다면 원그로브몰 다른 매장 영수증과 합산해서 무료 주차 시간을 챙기세요. 🚗"),
    ("p", "4️⃣ 과즙 맛을 제대로 느끼고 싶다면 오렌지·자몽·트리플비타민처럼 [[B:직접 착즙하는 메뉴]]를 고르세요."),
    ("p", "에이드나 티 종류보다 과일 맛이 훨씬 진하게 느껴져요."),
    ("p", "5️⃣ 아이와 함께라면 딸기바나나나 망고바나나처럼 우유가 들어간 스무디가 무난해요."),
    ("p", "주말 오후에는 매장 앞 테이블이 금방 차니까, 앉아서 마시고 싶다면 조금 이른 시간을 추천해요."),

    ("hr",),
    ("h", "📋 후기 종합"),
    ("p", "⭕ 좋았던 점", {"b": 1}),
    ("p", "[[bl:✨ 주문하면 눈앞에서 바로 착즙해줘서 과즙 맛이 살아 있어요.]]\n[[bl:✨ XL 사이즈가 커서 둘이 나눠 마셔도 넉넉해요.]]\n[[bl:✨ 유기농 사탕수수 시럽이라 단맛이 과하지 않아요.]]\n[[bl:✨ 원그로브 B동 1층이라 쇼핑하다 들르기 편해요.]]"),
    ("p", "❌ 아쉬웠던 점", {"b": 1}),
    ("p", "[[o:💵 착즙 주스가 XL 기준 7천 원 안팎이라 가격대가 있는 편이에요.]]\n[[o:💵 음료만 사면 주차 무료 기준(2만 원)에는 못 미쳐요.]]"),
    ("p", "🔄 재방문 의사: 🙆‍♀️🙆‍♀️🙆‍♀️", {"b": 1}),
    ("p", "👍 다음엔 베스트 메뉴인 트리플비타민주스를 마셔볼 거예요!"),
    ("p", "🎯 추천대상", {"b": 1}),
    ("p", "🧡 마곡 원그로브에서 커피 말고 상큼한 음료를 찾으시는 분들\n🧡 갓 짠 착즙주스를 좋아하시는 분들\n🧡 아이와 함께 마실 음료를 찾으시는 분들"),
    ("p", "🌈직접 마셔보고 느낀 그대로 솔직하게 작성한 원그로브 카페 아메리칸트레일러 후기입니다.", {"b": 1}),
    ("place", "아메리칸트레일러 원그로브점"),
]

TAGS = "#원그로브카페 #아메리칸트레일러 #아메리칸트레일러원그로브점 #아메리칸트레일러마곡 #아메리칸트레일러메뉴 #마곡원그로브 #마곡원그로브카페 #마곡카페 #마곡역카페 #마곡나루카페 #발산역카페 #강서구카페 #마곡카페추천 #원그로브 #원그로브몰 #착즙주스 #생과일주스 #자몽주스 #레몬에이드 #트리플비타민주스 #ABC주스 #마곡원그로브맛집 #원그로브맛집 #마곡데이트 #마곡아이랑"

INLINE = re.compile(r"\[\[(r|p|y|g|bl|o|B|u|i):(.+?)\]\]", re.S)
EMO = re.compile(r'(?:[\U0001F300-\U0001FAFF☀-➿⭐⭕⌚-⏿](?:️)?(?:‍[\U0001F300-\U0001FAFF☀-➿](?:️)?)*)')


def plain(t):
    return INLINE.sub(lambda m: m.group(2), t)


def load(n):
    im = Image.open(PHOTOS / (f"IMG_{n}" if "." in n else f"IMG_{n}.jpg")).convert("RGB")
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
    return f"""<title>아메리칸트레일러 초안</title>
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
<div class="meta">은똥잉 · 2026. 10. 31. 방문</div>
{chr(10).join(parts)}
<div class="tags">{tags}</div>
</div>"""


def build_md():
    out = [f"# {TITLE}", ""]
    for blk in B:
        k = blk[0]
        if k == "img":
            out.append(" ".join(f"![IMG_{n}](../photos/americantrailer/blur/IMG_{n}.jpg)" for n in blk[1]))
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
    (OUT / "americantrailer.html").write_text(build_html())
    (OUT / "americantrailer.md").write_text(build_md())
    lines = [l for b in B if b[0] == "p" for l in plain(b[1]).split("\n")]
    print("ok", (OUT / "americantrailer.html").stat().st_size // 1024, "KB",
          "| emoji", sum(len(EMO.findall(l)) for l in lines),
          "| lines w/ emoji %.0f%%" % (100 * sum(1 for l in lines if EMO.search(l)) / len(lines)),
          "| chars", sum(len(plain(b[1])) for b in B if b[0] == "p"))
