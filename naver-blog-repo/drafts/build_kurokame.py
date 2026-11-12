"""쿠로카메 리뷰 완성본: 사진이 들어간 미리보기 HTML과 Markdown을 만든다.

블록 형식
  ("img", [사진번호...])          사진 (여러 장이면 묶음)
  ("p", 텍스트, 옵션)             문단. 옵션: b=굵게, fs=24/19, c=확인 필요(노란 표시)
  ("q", 텍스트)                   기본 인용구(❝ ❞), "/"는 줄바꿈
  ("bubble", 텍스트)              말풍선 인용구
  ("h", 텍스트)                   밑줄 인용구 소제목
  ("hr",)                         구분선

문장 안 서식 (STYLE.md 5-2)
  [[r:…]] 빨강  [[p:…]] 분홍  [[y:…]] 노란 배경  [[g:…]] 초록
  [[bl:…]] 파랑  [[o:…]] 주황  [[B:…]] 굵게
"""
import base64, html, io, re
from pathlib import Path
from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
PHOTOS = ROOT / "photos" / "kurokame" / "jpg"   # Drive 사진을 decode_drive.py로 변환해 둔 폴더 (깃에는 안 올림)
OUT = ROOT / "drafts"
RESEARCH_DIR = str(ROOT / "data" / "research" / "kurokame")

# 세로 사진 → 가로 4:3으로 자를 때 주요 대상의 세로 위치(0=위, 1=아래)
CROP = {"9563": 0.40, "9588": 0.5, "9590": 0.5, "9594": 0.68, "9596": 0.62, "9597": 0.42}

COLORS = {"r": "#f12f22", "p": "#f02c8c", "g": "#00a350", "bl": "#0076c8", "o": "#ff9c23"}

NDS_QUERY = "쿠로카메"   # 내돈내산 방문 인증에서 찾을 가게 이름
MAIN_KW = "마곡 맛집"
SUB_KWS = ["양천향교역", "돈코츠라멘", "쿠로카메", "서울식물원"]
ALIGN = "left"     # 2026-11-12 사용자 지시: 본문은 왼쪽 정렬, 소제목(밑줄 인용구)만 가운데
LINE = 22          # 가운데 정렬일 때 한 줄 최대 글자 수

TITLE = "[마곡 맛집] 쿠로카메 라멘, 양천향교역 흑돼지 돈코츠라멘 만 원 솔직후기 🍜"

B = [
    ("img", ["9578"]),
    ("p", "찬 바람이 불기 시작하니까 [[i:뜨끈하고 진한 국물 한 그릇]]이 자꾸만 생각나더라고요. 🥶"),
    ("p", "일요일 저녁, 동네에서 이미 입소문 난 마곡 맛집 [[r:쿠로카메 라멘]]에 드디어 다녀왔어요! 😊", {"b": 1}),
    ("p", "직접 먹어보고 느낀 그대로 ✨솔직하게 정리한 후기✨이니까 편하게 정독해 주세요. 😋", {"b": 1}),
    ("q", "가고시마 정통 흑돼지 돈코츠 / 라멘 한 그릇 10,000원! / 귀리밥 무한리필 셀프바까지 🍜"),
    ("bubble", "사진 미리보기📷"),
    ("img", ["9579", "9586", "9592", "9596"]),

    ("img", ["9596"]),
    ("p", "양천향교역 7번 출구 앞 보타닉파크프라자 1층, 따뜻한 조명이 새어 나오는 쿠로카메 입구예요. 서울식물원과도 가까워서 산책 전후로 들르기 좋은 양천향교역 맛집이에요. 🏮"),
    ("p", "가게 위쪽에 큰 간판이 없어서 처음 가면 지나치기 쉬운데요, 사피엔스커피 쪽으로 들어와 [[r:청춘옥과 부대찌개집 사이]]를 찾으시면 돼요!"),
    ("img", ["9597"]),
    ("p", "대신 출입문 옆에 붙은 동그란 [[B:KUROKAME RAMEN]] 로고가 길잡이 역할을 해줘요."),
    ("img", ["9598"]),
    ("p", "입구 앞 입간판에는 [[u:이 집의 자부심]]이 그대로 적혀 있었어요. 😲"),
    ("p", "\"정부가 특허한 토종 흑돼지 복원 품종을 사용합니다. '토종'이라는 이름을 붙일 수 있는 유일한 진짜 흑돼지입니다.\"", {"b": 1}),
    ("p", "흑돼지 뼈를 [[r:매장에서 오래 끓여낸 육수]]가 핵심인, 가고시마 스타일 돈코츠라멘 전문점이에요."),

    ("h", "📍 쿠로카메 라멘 위치 & 영업정보"),
    ("p", "방문 전에 알아두시면 좋은 정보부터 정리해 드릴게요! 😉"),
    ("p", "🏠 상호명: 쿠로카메 라멘 본점", {"b": 1}),
    ("p", "🗺 주소: 서울 강서구 마곡동로10길 46 1층 114호 (보타닉파크프라자)", {"b": 1}),
    ("p", "🚇 대중교통: 9호선 양천향교역 7번 출구에서 도보 약 3분", {"b": 1}),
    ("p", "⏰ 영업시간: 매일 11:00 ~ 21:00 (라스트오더 20:00, 브레이크타임 없음)", {"b": 1}),
    ("p", "🚗 주차 정보: 건물 지하주차장 [[r:1시간 무료]] (나갈 때 화면에 차량번호 입력)", {"b": 1}),
    ("p", "📞 전화: 0507-1467-2450", {"b": 1}),
    ("p", "💡 웨이팅 팁: 근처 직장인이 몰리는 [[r:평일 점심 피크엔 만석]]이에요. 대기는 매장 앞 화이트보드에 이름을 적는 방식이고, 회전이 빨라 오래 기다리진 않는 편이에요.", {"b": 1}),
    ("p", "저는 일요일 저녁 5시 반쯤 갔더니 다행히 빈자리가 넉넉해서 바로 앉을 수 있었어요. 👍"),

    ("h", "🏪 아담하고 깔끔한 매장 분위기"),
    ("img", ["9559"]),
    ("p", "들어서자마자 \"[[i:ようこそ、黒亀へ(어서 오세요, 쿠로카메에)]]\"라고 적힌 일본어 가렌이 반겨줘서 일본 동네 라멘집에 온 기분이었어요."),
    ("img", ["9560"]),
    ("p", "2인 테이블 몇 개와 바 좌석으로 이루어진 [[g:아담한 매장]]이에요. 테이블마다 주문용 태블릿이 놓여 있어요. 🪑"),
    ("img", ["9564"]),
    ("p", "벽을 따라 길게 이어진 바 좌석 덕분에 [[B:혼밥하기에도 전혀 부담 없는 구조]]였어요."),
    ("img", ["9563"]),
    ("p", "벽 고리에 앞치마가 걸려 있고, 자리마다 [[r:미니 선풍기와 머리끈]]까지 챙겨두셨더라고요. 뜨거운 라멘 먹을 때 은근 감동 포인트예요. 먹기 전 앞치마 준비완료🙆‍♀️🙆‍♀️"),
    ("img", ["9576"]),
    ("p", "테이블마다 S&B 이치미(고춧가루)와 테이블 후추, 소금이 놓여 있는데요, 이 후추가 나중에 아주 큰 역할을 한답니다. 😎"),

    ("h", "🍚 귀리밥 무한리필 & 셀프코너"),
    ("img", ["9561"]),
    ("p", "라멘집이라 반찬이 따로 나오지 않고, \"[[i:드실 만큼만 담아 주세요]]\"라고 적힌 셀프코너를 이용하면 돼요. 🙌"),
    ("img", ["9562"]),
    ("p", "다진 마늘, 초생강, 갓절임, 배추김치가 준비되어 있어요. 특히 초생강은 돈코츠 국물이랑 궁합이 좋아서 [[u:꼭 챙기시길 추천해요]]!"),
    ("img", ["9594"]),
    ("p", "밥솥에 붙은 '저속노화 귀리밥' 문구 보이시나요? 흰쌀밥이 아니라 귀리밥인데 [[r:무한리필]]이라니, 괜히 죄책감도 덜하고 더 건강해지는 기분이었어요. 🌾", {"b": 1}),
    ("p", "벽에는 이런 안내문도 붙어 있었어요."),
    ("p", "\"면을 다 드신 후, 밥과 갓절임을 같이 국물에 말아 드시면 맛있습니다.\"", {"b": 1}),
    ("p", "이 꿀팁은 아래에서 제가 직접 해봤어요! 💡"),

    ("h", "💵 쿠로카메 메뉴 & 가격"),
    ("p", "주문부터 결제까지 [[u:테이블 태블릿으로 한 번에]] 끝나서 직원분을 부를 필요가 없어요."),
    ("img", ["9566"]),
    ("p", "공지사항 탭에도 \"국물에 밥, 꼭 드셔보세요. 진한 돈코츠 육수와 환상의 조합입니다.\"라고 적혀 있을 만큼 사장님이 강력 추천하는 조합이에요. ✨"),
    ("img", ["9567", "9568"]),
    ("img", ["9569", "9570"]),
    # 메뉴 목록 (2026-11-12 사용자 지시): 카테고리 줄 바로 아래에 메뉴를 빈 줄 없이 붙여 쓰고, 카테고리가 바뀔 때만 빈 줄 1개
    ("menu", "🍜 [[y:라멘]]", [
        "쿠로부타 돈코츠 라멘: 10,000원 (BEST)",
        ("[[p:(매운) 쿠로부타 카라이 라멘: 10,000원 (신라면 정도)]]", {"b": 1}),   # 주문한 메뉴 = 분홍+굵게
        "(더 매운) 쿠로부타 게키카라 라멘: 10,000원 (열라면 정도)",
    ]),
    ("menu", "🥟 [[y:사이드 & 토핑]]", [
        "스이교자: 5,000원 (흑초소스+칠리오일)", "차슈: 3,000원 (국내산 흑돼지)", "멘마(죽순): 1,500원",
        "이즈니버터: 1,000원 (라멘국물+버터+밥=환상)", "숙주: 1,000원", "파: 500원", "사리: 3,500원 (육수도 같이 제공)",
    ]),
    ("img", ["9572", "9573", "9574"]),
    ("menu", "🍺 [[y:음료 & 주류]]", [
        "코카콜라: 2,000원", "산가리아 녹차 / 우롱차: 각 3,000원", "참이슬 후레쉬: 5,000원",
        "기린 / 삿포로 / 아사히 병맥주: 각 6,000원 (꽁꽁 언 냉동 유리잔 제공)",
    ]),
    ("p", "라멘 세 종류가 [[u:전부 10,000원]]이라 맵기만 취향대로 고르면 돼요. 요즘 라멘 한 그릇에 13,000~15,000원 하는 곳도 많은데, [[r:흑돼지 라멘이 만 원]]이면 가성비가 정말 좋아요. 👍", {"b": 1}),
    ("img", ["9575"]),
    ("p", "라멘을 고르면 차슈(+3,000원), 멘마(+1,500원), 파(+500원) 추가 토핑을 [[B:최대 3개]]까지 고를 수 있어요. 🏷️"),
    ("p", "저는 매콤한 국물을 좋아해서 [[p:(매운) 쿠로부타 카라이 라멘]]으로 주문했어요! 🌶️"),

    ("h", "😋 마곡 맛집 쿠로카메, 카라이 라멘 솔직 후기"),
    ("p", "오늘 주문한 메뉴는 [[p:(매운) 쿠로부타 카라이 라멘]] 한 그릇이에요! 🍜", {"b": 1}),
    ("img", ["9577"]),
    ("p", "기다리는 동안 셀프코너에서 [[i:김치와 초생강, 갓절임]]을 조금씩 담아왔어요. 🥢"),
    ("img", ["9578"]),
    ("p", "드디어 나온 [[y:쿠로부타 카라이 라멘]]! 주황빛 국물 위에 큼직한 차슈와 송송 썬 파, 깨, 불향 입힌 고기 토핑이 듬뿍 올라간 비주얼 좀 보세요. 🤤", {"b": 1}),
    ("img", ["9579"]),
    ("p", "가까이서 보면 차슈가 그릇 반을 덮을 만큼 넓적해요. 🧡"),
    ("img", ["9580"]),
    ("p", "국물부터 한 숟갈 떠먹었는데, 진한 흑돼지 육수에 고추기름의 칼칼함이 더해져서 묵직하면서도 [[r:잡내 없이 깔끔한 맛]]이었어요. 😋"),
    ("img", ["9582"]),
    ("p", "제가 제일 좋아했던 건 바로 이 ✨겉을 불에 그을린 고기 토핑✨이에요! 씹을 때마다 은은한 불맛이 올라와서 국물 전체에 풍미를 더해줘요. 😭", {"b": 1}),
    ("img", ["9583"]),
    ("p", "면은 [[i:얇은 호소멘]]인데 살짝 꼬들꼬들하게 삶아져 나와서, 끝까지 [[r:퍼지지 않고 탱탱한 식감]]이 살아 있었어요. 🍜"),
    ("img", ["9584"]),
    ("p", "흑돼지 차슈는 젓가락으로 들면 하늘하늘할 만큼 얇은데, 입에 넣으면 [[B:부드럽게 사르르 녹아요.]] 면에 돌돌 말아 한입에 먹는 조합이 최고였어요. 🥰"),
    ("img", ["9588"]),
    ("p", "중간쯤 셀프코너의 다진 마늘을 넣고 휘휘 섞어줬더니 [[r:감칠맛이 확 폭발]]하더라고요. 이건 꼭 해보세요! 🧄"),
    ("p", "맵기는 공지대로 [[B:딱 신라면 정도]]라 맵찔이도 충분히 즐길 수 있어요. 매운맛이 육수 맛을 덮지 않아서 마지막 한 숟갈까지 흑돼지 국물 맛이 또렷했어요. 🌶️"),

    ("h", "🎁 영수증 리뷰 이벤트 & 사쓰마아게"),
    ("img", ["9565"]),
    ("p", "테이블 태블릿에 [[r:네이버 영수증 리뷰 이벤트]] 안내가 떠 있어요. 리뷰를 남기면 가고시마 정통 사쓰마아게를 맛볼 수 있답니다. 🎁", {"b": 1}),
    ("img", ["9586"]),
    ("p", "가고시마 명물 [[y:사쓰마아게]](어묵 튀김)예요. 화려한 일본 전통 그릇에 담겨 나와서 플레이팅부터 예뻤어요. ✨", {"b": 1}),
    ("img", ["9587"]),
    ("p", "[[u:겉은 바삭하고 속은 탱글한]] 어묵이라, 함께 나온 노란 겨자를 살짝 찍어 먹으니 라멘 사이사이 입가심용으로 딱이었어요. 😋"),

    ("h", "💡 국물에 귀리밥 말아먹기 (강력 추천!)"),
    ("p", "면을 다 먹고 나서, 안내문대로 셀프코너에서 귀리밥을 퍼왔어요."),
    ("img", ["9589"]),
    ("p", "귀리가 톡톡 씹히는 [[g:고슬고슬한 귀리밥]]이라 그냥 먹어도 고소해요. 🌾"),
    ("img", ["9590"]),
    ("p", "남은 국물에 [[B:밥이랑 갓절임]]을 같이 넣고~ 🥄"),
    ("img", ["9591"]),
    ("p", "숟가락으로 꾹꾹 눌러서 국물을 충분히 적셔줘요."),
    ("img", ["9593"]),
    ("p", "마지막으로 테이블 후추를 톡톡 뿌려주면 완성! 😉"),
    ("img", ["9592"]),
    ("p", "진한 돈코츠 국물을 머금은 밥에 ✨불향 고기 토핑✨까지 한 숟갈에 올리면, 이게 진짜 마무리 코스더라고요. 😭", {"b": 1}),
    ("p", "면만 먹고 일어나면 이 집의 절반만 맛본 거예요. [[u:밥 말아먹기는 필수]]! 국물 한 방울 안 남기고 싹싹 긁어먹었어요🤭"),

    ("hr",),
    ("h", "📋 후기 종합"),
    ("p", "⭕ 좋았던 점", {"b": 1}),
    ("p", "[[bl:✨ 토종 흑돼지로 우려낸 진한 돈코츠 국물을 만 원에 즐길 수 있어요.]]\n[[bl:✨ 불향 입힌 고기 토핑과 살살 녹는 얇은 차슈가 끝까지 질리지 않아요.]]\n[[bl:✨ 귀리밥 무한리필과 셀프코너 덕분에 국물에 밥까지 든든하게 먹을 수 있어요.]]\n[[bl:✨ 바 좌석, 앞치마, 미니 선풍기까지 갖춰져 있어 혼밥하기 편해요.]]"),
    ("p", "❌ 아쉬웠던 점", {"b": 1}),
    ("p", "[[o:💵 매장이 아담해서 평일 점심 피크에는 금방 만석이 되고 웨이팅이 생겨요.]]\n[[o:💵 가게 위에 큰 간판이 없어서 처음 가면 지나치기 쉬워요.]]"),
    ("p", "🔄 재방문 의사: 🙆‍♀️🙆‍♀️🙆‍♀️🙆‍♀️", {"b": 1}),
    ("p", "👍 다음엔 사장님 추천 이즈니버터를 추가해서 국물+버터+밥 조합으로, 사이드로 스이교자까지 꼭 먹어볼 거예요!"),
    ("p", "🎯 추천대상", {"b": 1}),
    ("p", "🧡 진한 돈코츠라멘을 파는 마곡 맛집을 찾으시는 분들\n🧡 혼밥하기 편한 라멘집을 찾으시는 분들\n🧡 서울식물원 산책 전후로 든든한 한 끼가 필요하신 분들"),
    ("p", "🌈직접 먹어보고 느낀 그대로 솔직하게 작성한 마곡 맛집 쿠로카메 후기입니다.", {"b": 1}),
    ("place", "쿠로카메 라멘 본점"),
]

TAGS = "#마곡맛집 #쿠로카메 #쿠로카메라멘 #양천향교역맛집 #라멘맛집 #마곡라멘 #마곡라멘맛집 #마곡나루맛집 #마곡역맛집 #마곡나루역맛집 #발산역맛집 #발산맛집 #강서구맛집 #돈코츠라멘 #일본라멘 #라멘집 #양천향교맛집 #서울라멘맛집 #서울식물원맛집 #마곡점심맛집 #발산마곡맛집 #강서맛집 #흑돼지라멘 #가고시마라멘 #마곡혼밥 #보타닉파크맛집"

INLINE = re.compile(r"\[\[(r|p|y|g|bl|o|B|u|i):(.+?)\]\]", re.S)
EMO = re.compile(r'(?:[\U0001F300-\U0001FAFF☀-➿⭐⭕⌚-⏿](?:️)?(?:‍[\U0001F300-\U0001FAFF☀-➿](?:️)?)*)')


def plain(t):
    return INLINE.sub(lambda m: m.group(2), t)


def load(n):
    im = Image.open(PHOTOS / f"IMG_{n}.jpg")
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
    return f"""<title>쿠로카메 리뷰 초안</title>
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
<div class="meta">은똥잉 · 2026. 11. 8. 방문</div>
{chr(10).join(parts)}
<div class="tags">{tags}</div>
</div>"""


def build_md():
    out = [f"# {TITLE}", ""]
    for blk in B:
        k = blk[0]
        if k == "img":
            out.append(" ".join(f"![IMG_{n}](../photos/kurokame/jpg/IMG_{n}.jpg)" for n in blk[1]))
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
    (OUT / "kurokame.html").write_text(build_html())
    (OUT / "kurokame.md").write_text(build_md())
    lines = [l for b in B if b[0] == "p" for l in plain(b[1]).split("\n")]
    print("ok", (OUT / "kurokame.html").stat().st_size // 1024, "KB",
          "| emoji", sum(len(EMO.findall(l)) for l in lines),
          "| lines w/ emoji %.0f%%" % (100 * sum(1 for l in lines if EMO.search(l)) / len(lines)),
          "| chars", sum(len(plain(b[1])) for b in B if b[0] == "p"))
