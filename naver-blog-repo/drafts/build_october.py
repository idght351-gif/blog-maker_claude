"""악토버 베이커리 이대 (5번 폴더, 2026-10-09 방문)."""
import base64, html, io, re
from pathlib import Path
from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "drafts"
COLORS = {"r": "#f12f22", "p": "#f02c8c", "g": "#00a350", "bl": "#0076c8", "o": "#ff9c23"}
ALIGN = "left"
LINE = 22
PHOTOS = ROOT / "photos" / "october" / "blur"
RESEARCH_DIR = str(ROOT / "data" / "research" / "october")
CROP = {"133425": 0.6, "133428": 0.6, "133437": 0.35, "133453": 0.6, "133506": 0.55, "133521": 0.5, "133531": 0.55, "133550": 0.5, "133605": 0.45, "133621": 0.5, "133654": 0.45, "133704": 0.42, "133812": 0.45, "133839": 0.5, "193707": 0.55, "193737": 0.6}
ROTATE = {}
NDS_QUERY = "악토버"
CATEGORY = "먹보여행"
MAIN_KW = "이대 빵집"
SUB_KWS = ["이대 카페", "악토버 베이커리", "샌드위치 맛집", "이대역", "라우겐"]

TITLE = "[이대 빵집] 악토버 베이커리 샌드위치·라우겐 맛집, 캐치테이블 웨이팅 후기 🥐"

B = [
    ("img", ["133550"]),
    ("p", "한글날 연휴, 신촌에서 점심을 먹고 [[i:디저트 빵]]을 사러 이대 쪽으로 걸어갔어요. 🥐"),
    ("p", "샌드위치와 라우겐 빵이 맛있다고 소문난 이대 빵집 [[r:악토버 베이커리]] 후기예요! 😊", {"b": 1}),
    ("p", "예전 '원즈오운'이 이름을 바꿔 새로 문을 연 곳이라 ✨빵순이들 사이에서 유명한 곳✨이에요."),
    ("q", "이대역 3번 출구 도보 3분 / 라우겐 소금빵 3,300원 · 오믈렛 샌드위치 4,500원 / 캐치테이블 웨이팅 필수 🥖"),
    ("bubble", "사진 미리보기📷"),
    ("img", ["133550", "133654", "133621", "133425"]),

    ("h", "📍 이대 빵집 악토버 베이커리 위치 & 영업정보"),
    ("img", ["133425"]),
    ("p", "통유리창에 그려진 [[r:주황색 해님 그림]]이 이 집의 트레이드마크예요. ☀️", {"b": 1}),
    ("img", ["133428"]),
    ("p", "가게 앞 벤치에는 웨이팅하는 손님들이 앉아 있었어요."),
    ("p", "가을 햇살에 은행잎 그림자가 비쳐서 외관만 찍어도 사진이 예쁘게 나와요."),
    ("p", "입구 입간판에 샌드위치와 빵 그림이 귀엽게 그려져 있어요."),
    ("p", "방문 전에 알아두시면 좋은 정보부터 정리해 드릴게요!"),
    ("p", "🏠 상호명: 악토버 베이커리 (October Bakery)", {"b": 1}),
    ("p", "🗺 주소: 서울 서대문구 이화여대길 20 1층", {"b": 1}),
    ("p", "🚇 대중교통: 2호선 이대역 3번 출구에서 걸어서 약 3분", {"b": 1}),
    ("p", "⏰ 영업시간: 평일 10:00 ~ 20:00 / 주말 10:00 ~ 19:30", {"b": 1}),
    ("p", "🚗 주차 정보: [[r:주차 불가]] (대중교통 추천)", {"b": 1}),
    ("p", "💡 웨이팅 팁: 매장 앞 [[r:캐치테이블]] 기기로 대기를 걸고, 포장 손님은 등록 없이 바로 들어가면 돼요.", {"b": 1}),
    ("img", ["133437"]),
    ("p", "저는 오후 1시 반쯤 갔는데 매장 이용 대기가 3팀 있었어요. 포장이라 바로 들어갔답니다. 👍"),
    ("p", "홀 이용 손님은 두 번 호출할 때까지 오지 않으면 다음 순서로 넘어가니 근처에서 기다리는 게 좋아요."),

    ("h", "🏪 빈티지한 매장 분위기"),
    ("img", ["133441"]),
    ("p", "안쪽은 길쭉한 구조에 원목 바닥과 크림색 벽이 어우러진 [[g:따뜻한 분위기]]예요."),
    ("p", "벽에 걸린 커다란 그림이 매장 분위기를 확 살려줘요. 🎨"),
    ("p", "천장이 높아서 사람이 많아도 답답하지 않았어요."),
    ("img", ["133812"]),
    ("p", "벽면 원목 선반에는 깜빠뉴, 비스코티, 페스츄리 같은 빵들이 칸칸이 진열되어 있어요."),
    ("img", ["133839"]),
    ("p", "카운터 뒤로 빵을 굽고 샌드위치를 만드는 주방이 훤히 보여요."),
    ("p", "직원분들이 쉴 새 없이 바쁘게 움직이고 계셨어요."),
    ("p", "주문이 들어가면 바로 샌드위치를 만들어 주셔서, 샌드위치 맛집이라는 말이 괜히 나온 게 아니구나 싶었어요."),
    ("p", "매장 안은 2인 테이블 위주라 자리가 많지 않은 편이에요."),

    ("h", "🥖 악토버 베이커리 빵 구경 & 가격"),
    ("img", ["133453"]),
    ("p", "가운데 큰 테이블에 갓 나온 빵들이 쫙 깔려 있어서 [[B:빵 구경하는 재미]]가 쏠쏠해요. 🤤"),
    ("img", ["133531"]),
    ("p", "짙은 갈색 겉면에 굵은 소금이 콕콕 박힌 [[y:라우겐 소금빵]]이에요."),
    ("img", ["133521"]),
    ("p", "결결이 겹쳐진 [[y:라우겐 솔티 페스츄리]]도 인기 메뉴래요. 단골들이 최애빵으로 많이 꼽더라고요. ✨"),
    ("img", ["133605"]),
    ("p", "얇게 썬 감자에 고르곤졸라를 올린 포카치아는 꿀이 따로 들어 있어요. 🍯"),
    ("img", ["133621"]),
    ("p", "식사빵 코너에는 그린올리브 깜빠뉴와 호두 크랜베리 깜빠뉴가 있어요. 깜빠뉴는 반 개로도 살 수 있어요."),
    ("menu", "🥐 [[y:빵]]", [
        "라우겐 소금빵: 3,300원", "고르곤졸라 & 포테이토 포카치아: 5,700원",
        "그린 올리브 & 페퍼 깜빠뉴: 6,000원", "호두 크랜베리 깜빠뉴: 7,000원 (반 개 4,000원)",
    ]),
    ("img", ["133654"]),
    ("p", "냉장 쇼케이스에는 샌드위치가 가득해요. 두툼한 계란이 들어간 [[r:오믈렛 샌드위치]]가 단연 눈에 띄었어요.", {"b": 1}),
    ("img", ["133704"]),
    ("p", "기본 오믈렛 샌드위치(겨자마요)는 4,500원이고, 전자레인지에 20~30초 데워 먹으라는 스티커가 붙어 있어요."),
    ("menu", "🥪 [[y:샌드위치]]", [
        "햄 치즈 아보카도 오믈렛 샌드위치: 5,700원", "오믈렛 샌드위치 (겨자마요): 4,500원",
    ]),
    ("p", "빵이 3천 원대부터 시작해서 [[B:이대 앞 빵집치고 무난한 가격대]]였어요."),

    ("h", "😋 이대 빵집 악토버 베이커리 솔직 후기"),
    ("p", "오늘 주문한 메뉴는 포장해 온 [[p:라우겐 스콘]] 하나예요! 🥐", {"b": 1}),
    ("img", ["193707"]),
    ("p", "저녁에 집에서 접시에 꺼내 보니 겉면이 [[y:짙은 갈색으로 반질반질]]하게 구워져 있어요."),
    ("p", "위에 뿌려진 굵은 소금 알갱이가 반짝반짝 빛나요. ✨"),
    ("img", ["193721.gif"]),
    ("p", "손으로 반을 갈라보니 겉은 바삭하고 속은 [[r:포슬포슬 부드러운]] 식감이었어요."),
    ("img", ["193737"]),
    ("p", "단면을 보면 속이 촘촘하고 노란빛이 돌아요."),
    ("p", "버터 향이 은은하게 올라와서 따로 잼을 바르지 않아도 충분히 맛있었어요."),
    ("p", "한 입 먹으면 ✨겉의 짭짤함과 속의 고소함✨이 같이 느껴져서 계속 손이 갔어요. 😋", {"b": 1}),
    ("p", "시간이 지났는데도 눅눅하지 않아서, 포장해 와서 먹기에도 괜찮았어요."),
    ("p", "다음에는 꼭 매장에서 샌드위치를 먹어보고 싶어요. 🥪"),
    ("p", "라우겐 특유의 진한 갈색 껍질이 살짝 쫀득하면서도 바삭해서 일반 스콘과는 또 다른 식감이었어요."),
    ("p", "커피 없이 그냥 먹어도 짭짤해서 간식으로 딱이었어요."),
    ("p", "빵 크기도 손바닥만 해서 한 개를 둘이 나눠 먹기에도 적당했어요."),
    ("p", "에어프라이어에 1~2분 정도 데우면 겉이 다시 바삭해져서 더 맛있게 먹을 수 있어요."),

    ("h", "💡 악토버 베이커리 방문 꿀팁"),
    ("p", "직접 가보고 정리한 팁이에요."),
    ("p", "1️⃣ 매장에서 먹고 싶다면 도착 전에 캐치테이블로 미리 대기를 걸어두세요."),
    ("p", "2️⃣ 포장만 한다면 웨이팅 등록 없이 바로 들어가서 빵을 고르면 돼요."),
    ("p", "3️⃣ 샌드위치는 냉장 쇼케이스에 있으니 빵 테이블과 따로 꼭 확인하세요. 🥪"),
    ("p", "4️⃣ 깜빠뉴는 반 개씩도 팔아서 혼자 사기에도 부담이 없어요."),
    ("p", "5️⃣ 주말은 7시 반에 문을 닫으니 늦은 오후에 간다면 시간을 꼭 확인하세요."),
    ("p", "인기 빵은 오후가 되면 빠르게 빠지니, 원하는 빵이 있다면 이른 시간에 가는 걸 추천해요."),

    ("hr",),
    ("h", "📋 후기 종합"),
    ("p", "⭕ 좋았던 점", {"b": 1}),
    ("p", "[[bl:✨ 라우겐 빵과 깜빠뉴, 샌드위치까지 종류가 다양해요.]]\n[[bl:✨ 포장 손님은 웨이팅 없이 바로 들어갈 수 있어요.]]\n[[bl:✨ 빵 가격이 3천 원대부터라 부담이 적어요.]]\n[[bl:✨ 해님 그림이 그려진 외관과 빈티지한 내부가 예뻐요.]]"),
    ("p", "❌ 아쉬웠던 점", {"b": 1}),
    ("p", "[[o:💵 매장 자리가 많지 않아 매장 이용은 웨이팅이 있어요.]]\n[[o:💵 주차가 안 돼서 차로 가기 불편해요.]]"),
    ("p", "🔄 재방문 의사: 🙆‍♀️🙆‍♀️🙆‍♀️🙆‍♀️", {"b": 1}),
    ("p", "👍 다음엔 햄 치즈 아보카도 오믈렛 샌드위치를 매장에서 먹어볼 거예요!"),
    ("p", "🎯 추천대상", {"b": 1}),
    ("p", "🧡 이대 빵집·이대 카페를 찾으시는 분들\n🧡 라우겐 빵이나 샌드위치를 좋아하시는 분들\n🧡 신촌·이대 데이트 후 빵 포장해 가고 싶은 분들"),
    ("p", "🌈직접 먹어보고 느낀 그대로 솔직하게 작성한 이대 빵집 악토버 베이커리 후기입니다.", {"b": 1}),
    ("place", "악토버 베이커리", "이화여대길"),
]

TAGS = "#이대빵집 #악토버베이커리 #악토버베이커리이대 #이대카페 #이대역카페 #이대맛집 #이대샌드위치 #샌드위치맛집 #이대빵집추천 #신촌빵집 #신촌카페 #원즈오운 #라우겐소금빵 #라우겐 #소금빵맛집 #오믈렛샌드위치 #깜빠뉴 #포카치아 #서대문구빵집 #이화여대맛집 #이대역맛집 #신촌맛집 #빵지순례 #서울빵집 #캐치테이블"

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
    return f"""<title>악토버 베이커리 초안</title>
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
<div class="meta">은똥잉 · 2026. 10. 9. 방문</div>
{chr(10).join(parts)}
<div class="tags">{tags}</div>
</div>"""


def build_md():
    out = [f"# {TITLE}", ""]
    for blk in B:
        k = blk[0]
        if k == "img":
            out.append(" ".join(f"![IMG_{n}](../photos/october/blur/IMG_{n}.jpg)" for n in blk[1]))
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
    (OUT / "october.html").write_text(build_html())
    (OUT / "october.md").write_text(build_md())
    lines = [l for b in B if b[0] == "p" for l in plain(b[1]).split("\n")]
    print("ok", (OUT / "october.html").stat().st_size // 1024, "KB",
          "| emoji", sum(len(EMO.findall(l)) for l in lines),
          "| lines w/ emoji %.0f%%" % (100 * sum(1 for l in lines if EMO.search(l)) / len(lines)),
          "| chars", sum(len(plain(b[1])) for b in B if b[0] == "p"))
