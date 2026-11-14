"""리요리요 방배동 카페 (2번 폴더, 2026-11-13 방문)."""
import base64, html, io, re
from pathlib import Path
from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "drafts"
COLORS = {"r": "#f12f22", "p": "#f02c8c", "g": "#00a350", "bl": "#0076c8", "o": "#ff9c23"}
ALIGN = "left"
LINE = 22
PHOTOS = ROOT / "photos" / "liyo" / "blur"
RESEARCH_DIR = str(ROOT / "data" / "research" / "liyo")
CROP = {"9677": 0.5, "9678": 0.45, "9679": 0.45, "9680": 0.6, "9681": 0.5, "9682": 0.5, "9691": 0.45, "9668": 0.4}
ROTATE = {}
NDS_QUERY = "리요리요"
CATEGORY = "먹보여행"
MAIN_KW = "이수역 카페"
SUB_KWS = ["방배동 카페", "애견동반 카페", "리요리요", "에그타르트", "시그니처라떼"]

TITLE = "[이수역 카페] 리요리요 방배동 애견동반 카페, 상주견 꿍치 만난 후기 ☕"

B = [
    ("img", ["9690"]),
    ("p", "목요일 오후, 책 한 권 들고 [[i:조용히 커피 마실 곳]]을 찾다가 방배동까지 걸어갔어요. 📖"),
    ("p", "이수역 카페 중에서 귀여운 상주견이 있다고 소문난 [[r:리요리요]]에 다녀왔어요! 😊", {"b": 1}),
    ("p", "반려견과 같이 갈 수 있는 애견동반 카페라 ✨강아지 좋아하는 분들✨께 특히 추천하고 싶은 곳이에요."),
    ("q", "상주견 꿍치가 반겨주는 카페 / 아이스 아메리카노 4,800원 / 매일 밤 10시까지 영업 🐶"),
    ("bubble", "사진 미리보기📷"),
    ("img", ["9690", "9681", "9675", "9666"]),

    ("h", "📍 이수역 카페 리요리요 위치 & 영업정보"),
    ("img", ["9666"]),
    ("p", "방배천로 상가 1층에 있고, 하얀 차양과 통유리창이 [[B:밖에서도 눈에 띄어요.]] 🤍"),
    ("img", ["9667"]),
    ("p", "입구 앞에는 자유의 여신상 일러스트가 들어간 간판이 서 있어요."),
    ("p", "방배동 카페 찾는 분들을 위해 방문 전에 알아두시면 좋은 정보부터 정리해 드릴게요!"),
    ("p", "🏠 상호명: 리요리요 (LiYO LiYO)", {"b": 1}),
    ("p", "🗺 주소: 서울 서초구 방배천로18길 11 아르떼상가 B동 104호", {"b": 1}),
    ("p", "🚇 대중교통: 4·7호선 이수역에서 걸어서 약 6분", {"b": 1}),
    ("p", "⏰ 영업시간: 월~토 12:00 ~ 22:00 / 일 13:00 ~ 22:00", {"b": 1}),
    ("p", "🚗 주차 정보: 상가 주차 가능 (방문 전 확인 추천)", {"b": 1}),
    ("p", "🐶 반려동물: [[r:반려견 동반 가능]]", {"b": 1}),
    ("p", "저는 평일 오후 3시쯤 갔는데 자리가 넉넉해서 창가에 바로 앉았어요. 👍"),
    ("img", ["9689"]),
    ("p", "유리문에도 'Every Day open' 문구가 적혀 있어서 휴무 걱정 없이 가기 좋아요."),

    ("h", "🐶 리요리요의 상주견, 꿍치"),
    ("img", ["9680"]),
    ("p", "문을 열자마자 흰색과 검은색 털이 섞인 강아지가 마중 나와 있었어요. 바로 상주견 [[r:꿍치]]예요! 🥰", {"b": 1}),
    ("img", ["9683.gif"]),
    ("p", "입구 매트 위를 총총 돌아다니는 모습이 너무 귀여웠어요."),
    ("p", "손님을 크게 경계하지 않고 자기 할 일 하듯 매장을 돌아다녀요."),
    ("img", ["9670"]),
    ("p", "테이블에는 꿍치를 예뻐해 줄 때 지켜야 할 안내문이 놓여 있어요."),
    ("p", "꿍치가 먼저 다가오면 [[B:손등을 내밀어 냄새를 맡게 한 뒤]] 인사해 주고, 쉬고 있을 땐 눈으로만 예뻐해 달라고 적혀 있었어요."),
    ("p", "나이가 들면서 예민해진 부분이 있다고 해서 저도 멀리서만 조용히 지켜봤어요. 🤍"),
    ("img", ["9668"]),
    ("p", "입구 유리문에는 반려동물 동반 안내도 따로 붙어 있어서 함께 오는 분들은 미리 읽어보시면 좋아요."),

    ("h", "🏪 빈티지한 매장 분위기"),
    ("img", ["9675"]),
    ("p", "매장 안은 둥근 테이블과 검은 의자가 놓인 [[g:모던하고 차분한]] 분위기예요."),
    ("img", ["9674"]),
    ("p", "벽에 걸린 패브릭 그림과 큰 스피커, 원목 의자가 빈티지한 느낌을 더해줘요. 🎶"),
    ("img", ["9678", "9679"]),
    ("p", "창가 선반에는 식물과 소품이 가득해서 구경하는 재미가 있었어요."),
    ("img", ["9676"]),
    ("p", "의자가 푹신해서 오래 앉아 책 읽기에도 편했어요."),
    ("p", "테이블 간격도 적당히 떨어져 있어서 대화 소리가 크게 울리지 않았어요."),
    ("p", "다만 주말에는 노트북 사용을 2시간 이내로 부탁한다는 안내가 있어요."),

    ("h", "💵 리요리요 메뉴 & 가격"),
    ("img", ["9671"]),
    ("p", "메뉴판은 카운터 위 화면에 떠 있어요. 커피, 시그니처라떼, 에이드, 디저트까지 종류가 다양해요. 😲"),
    ("menu", "☕ [[y:커피]] (매장 / 포장)", [
        ("[[p:아메리카노: 4,800원 / 3,800원]]", {"b": 1}),
        "카페라떼: 5,400원 / 4,400원", "바닐라라떼: 5,700원 / 4,700원", "아인슈페너: 6,500원 / 6,000원",
    ]),
    ("menu", "🌹 [[y:시그니처라떼]] (매장 / 포장)", [
        "시그니처라떼 1번·2번·3번·5번·7번: 각 5,900원 / 5,200원",
        "블루로즈 (아이스만): 7,000원",
    ]),
    ("menu", "🍃 [[y:논커피 & 티]]", [
        "복숭아아이스티: 5,500원", "말차라떼: 6,500원", "초코크림라떼: 6,700원", "애플레몬티: 6,500원",
    ]),
    ("menu", "🥐 [[y:디저트]]", [
        "에그타르트: 2,900원", "피자 타르트·버섯 크림 타르트: 각 3,900원",
        "유자 그릭요거트: 6,900원", "초이스 크로플 1조각: 9,000원",
    ]),
    ("p", "디카페인 변경은 700원 추가, 포장하면 1,000원 할인이에요."),
    ("p", "아메리카노가 4,800원이라 [[B:동네 카페치고는 살짝 있는 편]]이지만, 공간과 분위기를 생각하면 괜찮았어요."),
    ("p", "저는 기본에 충실하게 [[p:아이스 아메리카노]] 한 잔을 주문했어요! ☕", {"b": 1}),

    ("h", "😋 이수역 카페 리요리요 솔직 후기"),
    ("p", "오늘 주문한 메뉴는 [[p:아이스 아메리카노]] 한 잔이에요! 🧊", {"b": 1}),
    ("img", ["9681"]),
    ("p", "푸른 장미 로고가 찍힌 [[y:머그잔]]에 담겨 나와서 일회용 컵보다 훨씬 예뻤어요."),
    ("img", ["9682"]),
    ("p", "커다란 얼음이 듬뿍 들어 있어요. 🧊"),
    ("p", "한 모금 마셔보니 ✨산미가 적고 고소한 맛✨이라 누구나 편하게 마시기 좋았어요.", {"b": 1}),
    ("p", "쓴맛이 강하지 않아서 책 읽으면서 천천히 홀짝이기 딱 좋았어요."),
    ("img", ["9691"]),
    ("p", "창가에 앉아 커피 한 잔에 책 한 권, 이게 바로 [[r:혼자만의 힐링 시간]]이죠. 📖"),
    ("p", "음악도 너무 크지 않아서 집중이 잘 됐어요."),
    ("p", "창밖으로 지나가는 사람들과 가끔 꼬리를 흔들며 지나가는 꿍치를 보다 보니 시간이 금방 지나가더라고요."),
    ("p", "평일 오후라 손님이 많지 않아 혼자 와도 눈치 보이지 않는 분위기였어요."),
    ("img", ["9672"]),
    ("p", "카운터 옆 오븐 위에는 에그타르트(2,900원) 안내가 귀엽게 그려져 있었어요."),
    ("img", ["9673"]),
    ("p", "마침 갓 구운 [[y:에그타르트]]가 쟁반 가득 나와 있었는데, 고소한 냄새가 매장 안에 퍼지더라고요. 🤤"),
    ("p", "이번엔 커피만 마셨지만 다음엔 꼭 같이 먹어볼 거예요."),
    ("p", "포르투갈식 에그타르트에 한국식 차를 우려낸 크림을 넣었다고 메뉴판에 설명되어 있어서 더 궁금해졌어요."),

    ("h", "💡 리요리요 방문 꿀팁"),
    ("p", "직접 가보고 정리한 팁이에요."),
    ("p", "1️⃣ 처음이라면 별 세 개가 붙은 [[B:시그니처라떼 1번]]이 가장 인기 메뉴래요. 고소하고 묵직한 맛에 단맛을 살짝 더한 라떼예요."),
    ("p", "2️⃣ 크로플은 시럽과 토핑, 아이스크림을 직접 골라서 올릴 수 있는 초이스 메뉴예요."),
    ("p", "3️⃣ 포장하면 음료값에서 1,000원이 빠져서 테이크아웃도 괜찮아요."),
    ("p", "4️⃣ 꿍치를 만나고 싶다면 안내문을 먼저 읽고 천천히 다가가 주세요. 🐾"),
    ("p", "5️⃣ 밤 10시까지 열어서 이수역에서 저녁 먹고 2차 카페로 가기에도 좋아요."),
    ("p", "근처 방배동 카페골목에서 식사하고 디저트 코스로 묶어서 들르기 좋은 위치예요."),

    ("hr",),
    ("h", "📋 후기 종합"),
    ("p", "⭕ 좋았던 점", {"b": 1}),
    ("p", "[[bl:✨ 상주견 꿍치가 있어 강아지를 좋아하는 분들에게 힐링이 돼요.]]\n[[bl:✨ 반려견 동반이 가능한 애견동반 카페예요.]]\n[[bl:✨ 빈티지한 인테리어와 창가 자리 덕분에 오래 머물기 좋아요.]]\n[[bl:✨ 밤 10시까지 영업해서 저녁에도 들르기 좋아요.]]"),
    ("p", "❌ 아쉬웠던 점", {"b": 1}),
    ("p", "[[o:💵 아메리카노가 4,800원으로 가격대가 조금 있어요.]]\n[[o:💵 주말에는 노트북 사용 시간이 2시간으로 제한돼요.]]"),
    ("p", "🔄 재방문 의사: 🙆‍♀️🙆‍♀️🙆‍♀️🙆‍♀️", {"b": 1}),
    ("p", "👍 다음엔 시그니처라떼 1번과 갓 구운 에그타르트를 먹어볼 거예요!"),
    ("p", "🎯 추천대상", {"b": 1}),
    ("p", "🧡 이수역 카페 중 조용히 쉬어갈 곳을 찾으시는 분들\n🧡 반려견과 함께 갈 방배동 카페를 찾으시는 분들\n🧡 강아지를 보며 힐링하고 싶은 분들"),
    ("p", "🌈직접 마셔보고 느낀 그대로 솔직하게 작성한 이수역 카페 리요리요 후기입니다.", {"b": 1}),
    ("place", "리요리요", "방배천로18길"),
]

TAGS = "#이수역카페 #리요리요 #리요리요커피 #방배동카페 #방배동카페골목 #애견동반카페 #서울애견동반카페 #이수역카페추천 #사당역카페 #방배카페 #서초구카페 #이수역애견동반카페 #상주견카페 #강아지카페 #반려견동반카페 #에그타르트 #시그니처라떼 #크로플맛집 #이수역카페늦게까지 #방배동디저트 #혼카페 #책읽기좋은카페 #이수역디저트 #방배역카페 #꿍치"

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
    return f"""<title>리요리요 초안</title>
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
            out.append(" ".join(f"![IMG_{n}](../photos/liyo/blur/IMG_{n}.jpg)" for n in blk[1]))
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
    (OUT / "liyo.html").write_text(build_html())
    (OUT / "liyo.md").write_text(build_md())
    lines = [l for b in B if b[0] == "p" for l in plain(b[1]).split("\n")]
    print("ok", (OUT / "liyo.html").stat().st_size // 1024, "KB",
          "| emoji", sum(len(EMO.findall(l)) for l in lines),
          "| lines w/ emoji %.0f%%" % (100 * sum(1 for l in lines if EMO.search(l)) / len(lines)),
          "| chars", sum(len(plain(b[1])) for b in B if b[0] == "p"))
