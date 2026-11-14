"""bhc치킨 이수역점 (1번 폴더, 2026-11-13 방문)."""
import base64, html, io, re
from pathlib import Path
from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "drafts"
COLORS = {"r": "#f12f22", "p": "#f02c8c", "g": "#00a350", "bl": "#0076c8", "o": "#ff9c23"}
ALIGN = "left"
LINE = 22
PHOTOS = ROOT / "photos" / "bhc" / "blur"
RESEARCH_DIR = str(ROOT / "data" / "research" / "bhc")
CROP = {"9709": 0.5, "9710": 0.45, "9711": 0.45, "9719": 0.5, "9726": 0.5, "9727": 0.55, "9728": 0.6, "9729": 0.5, "9734": 0.5, "9706": 0.4, "9698": 0.5, "9699": 0.5}
ROTATE = {}
NDS_QUERY = "bhc"
CATEGORY = "제품리뷰"   # 대형 프랜차이즈 메뉴 리뷰 (사용자 지시 2026-11-12)
MAIN_KW = "이수역 치킨"
SUB_KWS = ["bhc 이수역점", "양념킹", "뿌링핫도그", "이수역 맛집", "치맥"]

TITLE = "[이수역 치킨] bhc 이수역점 양념킹 반반·뿌링핫도그 치맥 솔직후기 🍗"

B = [
    ("img", ["9720"]),
    ("p", "금요일 저녁, 퇴근하고 [[i:치킨에 생맥주]] 한 잔이 너무 당기더라고요. 🍺"),
    ("p", "그래서 이수역 치킨집 중에 매장이 넓기로 유명한 [[r:bhc치킨 이수역점]]에 다녀왔어요! 😊", {"b": 1}),
    ("p", "후라이드랑 양념킹 반반에 뿌링핫도그까지, ✨치맥 풀코스✨로 먹고 온 후기 들려드릴게요."),
    ("q", "후라이드+양념킹 반반 22,900원 / 뿌링핫도그 3개 6,000원 / 생맥주 500cc 5,000원 🍗"),
    ("bubble", "사진 미리보기📷"),
    ("img", ["9720", "9734", "9727", "9707"]),

    ("h", "📍 이수역 치킨 bhc 이수역점 위치 & 영업정보"),
    ("img", ["9695"]),
    ("p", "노란 bhc 간판이 크게 걸려 있어서 골목 입구에서부터 [[B:한눈에 보여요.]] 🟡"),
    ("img", ["9698"]),
    ("p", "입구에 영업시간이 적혀 있는데 새벽 1시까지라 늦게 와도 여유로워요."),
    ("p", "이수역 맛집 찾는 분들께 참고가 되도록, 방문 전에 알아두시면 좋은 정보부터 정리해 드릴게요!"),
    ("p", "🏠 상호명: bhc치킨 이수역점", {"b": 1}),
    ("p", "🗺 주소: 서울 동작구 동작대로27길 16-4 1층 (사당동)", {"b": 1}),
    ("p", "🚇 대중교통: 4·7호선 총신대입구(이수)역 14번 출구에서 약 120m", {"b": 1}),
    ("p", "⏰ 영업시간: 매일 11:00 ~ 다음 날 01:00", {"b": 1}),
    ("p", "🚗 주차 정보: 전용 주차장은 없어서 근처 공영·유료 주차장 이용", {"b": 1}),
    ("p", "📞 전화: 02-532-0715", {"b": 1}),
    ("p", "💡 주문 팁: 자리마다 [[r:태블릿]]이 있어서 앉아서 바로 주문하면 돼요.", {"b": 1}),
    ("p", "저는 금요일 저녁 6시 반쯤 갔는데 매장이 넓어서 바로 앉을 수 있었어요. 👍"),

    ("h", "🏪 넓고 쾌적한 매장 분위기"),
    ("img", ["9696"]),
    ("p", "입구 쪽 'bhc chicken' 네온사인이 반짝여서 들어가기 전부터 기분이 좋아져요. ✨"),
    ("img", ["9707"]),
    ("p", "안으로 들어가면 테이블이 길게 이어진 [[g:넓은 홀]]이 나와요."),
    ("p", "벽면을 따라 크게 써 붙인 영어 문구와 주황 벽돌 타일이 어우러져서 밝은 치킨펍 같은 분위기예요. 🧡"),
    ("img", ["9700", "9701"]),
    ("p", "창가 쪽은 2인 테이블, 안쪽은 4인 이상 앉을 수 있는 긴 테이블이라 인원수에 맞춰 앉기 좋아요."),
    ("p", "혼자 와서 포장 기다리는 분들도 계셨어요."),
    ("img", ["9702.gif"]),
    ("p", "테이블 간격이 넉넉해서 옆 테이블 신경 쓰지 않고 이야기 나누기 좋았어요."),
    ("img", ["9708"]),
    ("p", "벽 한쪽에는 [[r:대형 스크린]]이 있어서 스포츠 경기 있는 날 단체로 보며 치맥하기 딱이에요. 📺", {"b": 1}),
    ("img", ["9709", "9718"]),
    ("p", "기본으로 치킨무가 나오고, 집게와 포크도 깔끔하게 챙겨주세요."),

    ("h", "💵 bhc 메뉴 & 가격"),
    ("img", ["9704"]),
    ("p", "bhc 치킨은 모든 메뉴에 [[B:100% 국내산 닭]]을 쓴다고 메뉴판에 적혀 있어요. 🐔"),
    ("menu", "🍗 [[y:치킨]]", [
        ("[[p:반반 (후라이드/양념킹): 22,900원]]", {"b": 1}),
        "뿌링클: 21,000원", "커링클·쏘이갈릭킹: 각 21,900원", "콰삭킹·핫후라이드: 각 21,000원",
        "콰삭톡: 23,000원", "콰삭모짜킹: 24,000원",
    ]),
    ("menu", "🌭 [[y:사이드 & 소스]]", [
        ("[[p:뿌링핫도그 (3개): 6,000원]]", {"b": 1}), ("[[p:뿌링뿌링소스: 2,500원]]", {"b": 1}),
    ]),
    ("menu", "🍺 [[y:음료 & 주류]]", [
        ("[[p:생맥주 500cc: 5,000원]]", {"b": 1}), ("[[p:제로콜라 1.25L: 5,000원]]", {"b": 1}),
    ]),
    ("img", ["9706"]),
    ("p", "요즘 밀고 있는 알싸킹 포스터도 크게 붙어 있었어요. 다음엔 이것도 궁금하더라고요. 🌶️"),
    ("img", ["9705"]),
    ("p", "사이드 메뉴와 소스 가격은 메뉴판 오른쪽에 따로 정리되어 있어요."),
    ("img", ["9697"]),
    ("p", "입구 입간판에는 떡볶이, 오징어 튀김 같은 술안주 메뉴도 소개되어 있었어요."),
    ("p", "치킨 한 마리가 2만 원 초반이라 [[B:배달 가격이랑 비슷한 수준]]이에요. 매장에서 갓 튀긴 걸 바로 먹는 게 장점이죠."),
    ("p", "저희는 [[p:후라이드+양념킹 반반]]에 [[p:뿌링핫도그]], 생맥주 두 잔을 주문했어요! 🍻", {"b": 1}),

    ("h", "😋 이수역 치킨 bhc 솔직 시식 후기"),
    ("p", "오늘 주문한 메뉴는 [[p:반반(후라이드/양념킹), 뿌링핫도그, 생맥주]]예요! 🍗", {"b": 1}),
    ("img", ["9710"]),
    ("p", "치킨 나오기 전에 시원한 생맥주로 먼저 짠! 🍺"),
    ("p", "잔이 꽁꽁 차가워서 첫 모금이 특히 시원했어요."),
    ("img", ["9711"]),
    ("p", "맥주 거품도 부드럽게 올라와서 치킨이랑 같이 먹기 좋았어요."),
    ("img", ["9720"]),
    ("p", "드디어 나온 [[y:후라이드+양념킹 반반]]! 바구니 한가득 담겨 나와서 양이 넉넉해 보였어요. 😲", {"b": 1}),
    ("img", ["9721"]),
    ("p", "후라이드는 튀김옷이 [[r:바삭바삭하게 부서지는]] 스타일이에요."),
    ("p", "갓 튀겨 나와서 겉은 바삭하고 속살은 촉촉했어요. 🤤"),
    ("img", ["9722"]),
    ("p", "[[y:양념킹]]은 윤기가 좌르르 흐르는 빨간 양념이 듬뿍 발라져 있어요."),
    ("img", ["9734"]),
    ("p", "한 입 베어 물면 ✨달콤하면서 살짝 매콤한 양념✨이 속살까지 잘 배어 있어요. 😋", {"b": 1}),
    ("p", "양념이 끈적하지 않고 적당히 묽어서 손에 덜 묻는 게 좋았어요."),
    ("img", ["9729"]),
    ("p", "후라이드 한 입, 양념 한 입 번갈아 먹으니 [[B:맥주가 술술]] 들어가더라고요. 🍻"),

    ("img", ["9716"]),
    ("p", "다음은 [[y:뿌링핫도그]]! 노란 뿌링클 시즈닝이 핫도그 겉면에 가득 묻어 있어요. 🌭", {"b": 1}),
    ("img", ["9726", "9727"]),
    ("p", "반으로 잘라보니 안에 [[r:통통한 소시지]]가 꽉 차 있었어요."),
    ("p", "겉은 바삭하고 속은 쫀득한 빵 식감이라 간식처럼 먹기 좋았어요. 🥰"),
    ("img", ["9717"]),
    ("p", "뿌링뿌링소스는 따로 2,500원에 추가했어요."),
    ("img", ["9719"]),
    ("p", "뚜껑을 열면 하얀 크림 소스가 가득 들어 있어요."),
    ("img", ["9728"]),
    ("p", "핫도그를 소스에 푹 찍어 먹으니 ✨달콤짭짤한 맛✨이 두 배가 됐어요! 이건 꼭 같이 시키세요. 😭", {"b": 1}),
    ("p", "핫도그 빵은 기름지지 않고 담백한 편이라 시즈닝의 단맛이 더 잘 느껴졌어요."),
    ("p", "식어도 눅눅해지지 않아서 마지막 한 조각까지 바삭함이 살아 있었어요."),
    ("p", "치킨이랑 핫도그까지 먹으니 둘이서 배부르게 먹기 딱 좋은 양이었어요."),

    ("h", "💡 bhc 이수역점 꿀팁"),
    ("p", "직접 가보고 정리한 팁이에요."),
    ("p", "1️⃣ 기프티콘(교환권)도 매장에서 쓸 수 있어요. 저도 일부는 교환권으로 결제했어요."),
    ("p", "2️⃣ 뿌링핫도그를 시킨다면 [[B:뿌링뿌링소스]]도 같이 시키는 걸 추천해요."),
    ("p", "3️⃣ 주차장이 따로 없으니 지하철로 가는 게 편해요. 🚇"),
    ("p", "4️⃣ 새벽 1시까지 영업해서 늦은 시간 2차 치맥 장소로도 좋아요."),
    ("p", "넓은 홀과 대형 스크린 덕분에 모임이나 회식 장소로도 괜찮겠더라고요."),

    ("hr",),
    ("h", "📋 후기 종합"),
    ("p", "⭕ 좋았던 점", {"b": 1}),
    ("p", "[[bl:✨ 갓 튀긴 후라이드가 바삭하고 속살이 촉촉해요.]]\n[[bl:✨ 양념킹은 달콤 매콤한 양념이 속까지 잘 배어 있어요.]]\n[[bl:✨ 뿌링핫도그는 뿌링뿌링소스와 같이 먹으면 꿀조합이에요.]]\n[[bl:✨ 매장이 넓고 대형 스크린이 있어 치맥 모임에 좋아요.]]"),
    ("p", "❌ 아쉬웠던 점", {"b": 1}),
    ("p", "[[o:💵 전용 주차장이 없어서 차로 가기엔 불편해요.]]\n[[o:💵 소스를 따로 사야 해서 사이드까지 시키면 금액이 꽤 나와요.]]"),
    ("p", "🔄 재방문 의사: 🙆‍♀️🙆‍♀️🙆‍♀️🙆‍♀️", {"b": 1}),
    ("p", "👍 다음엔 알싸킹이랑 콰삭킹을 먹어볼 거예요!"),
    ("p", "🎯 추천대상", {"b": 1}),
    ("p", "🧡 이수역 치킨집에서 넓게 치맥하고 싶으신 분들\n🧡 bhc 양념킹·뿌링핫도그가 궁금하신 분들\n🧡 스포츠 경기 보며 단체로 모일 곳을 찾으시는 분들"),
    ("p", "🌈직접 먹어보고 느낀 그대로 솔직하게 작성한 이수역 치킨 bhc 후기입니다.", {"b": 1}),
    ("place", "BHC치킨 이수역점", "동작대로27길"),
]

TAGS = "#이수역치킨 #bhc #bhc이수역점 #bhc치킨 #양념킹 #bhc양념킹 #뿌링핫도그 #bhc뿌링핫도그 #뿌링뿌링소스 #이수역맛집 #이수역치킨집 #이수역치킨맛집 #사당동치킨 #사당치킨 #동작구치킨 #이수역치맥 #치맥 #후라이드치킨 #반반치킨 #bhc신메뉴 #이수역술집 #총신대입구역맛집 #남성사계시장맛집 #치킨맛집 #bhc후기"

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
    return f"""<title>bhc 이수역점 초안</title>
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
            out.append(" ".join(f"![IMG_{n}](../photos/bhc/blur/IMG_{n}.jpg)" for n in blk[1]))
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
    (OUT / "bhc.html").write_text(build_html())
    (OUT / "bhc.md").write_text(build_md())
    lines = [l for b in B if b[0] == "p" for l in plain(b[1]).split("\n")]
    print("ok", (OUT / "bhc.html").stat().st_size // 1024, "KB",
          "| emoji", sum(len(EMO.findall(l)) for l in lines),
          "| lines w/ emoji %.0f%%" % (100 * sum(1 for l in lines if EMO.search(l)) / len(lines)),
          "| chars", sum(len(plain(b[1])) for b in B if b[0] == "p"))
