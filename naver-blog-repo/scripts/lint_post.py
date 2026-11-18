"""초안이 STYLE.md 규칙을 지키는지 점검한다.
사용법: python3 lint_post.py <build_xxx.py 경로>
build 파일에 TITLE, B, TAGS, MAIN_KW, SUB_KWS가 있어야 한다."""
import importlib.util, re, sys
from collections import Counter

spec = importlib.util.spec_from_file_location("post", sys.argv[1])
m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
B, TITLE, TAGS = m.B, m.TITLE, m.TAGS
MAIN, SUBS = getattr(m, "MAIN_KW", ""), getattr(m, "SUB_KWS", [])
plain, EMO = m.plain, m.EMO
ns = lambda s: s.replace(" ", "")

paras = [b for b in B if b[0] == "p"]
lines = [l for b in paras for l in plain(b[1]).split("\n") if l.strip()]
body = "\n".join(lines)
text_first = next(plain(b[1]) for b in paras if not plain(b[1]).startswith("["))
imgs = [n for b in B if b[0] == "img" for n in b[1]]
heads = [b[1] for b in B if b[0] in ("h", "hq", "hl", "hb")]
emoji = sum(len(EMO.findall(l)) for l in lines)
emoji_ratio = sum(1 for l in lines if EMO.search(l)) / len(lines)
chars = len(body)
kw_count = ns(body).count(ns(MAIN)) if MAIN else 0
tags = TAGS.split()

# 섹션별 빨간색 개수
red_by_sec, sec = Counter(), "도입"
for b in B:
    if b[0] in ("h", "hq", "hl", "hb"): sec = b[1]
    if b[0] == "p": red_by_sec[sec] += b[1].count("[[r:")

# 같은 형용사·표현 반복 (3회 초과)
words = Counter(re.findall(r"[가-힣]{2,}(?:한|운|은)\b", body))
repeats = [w for w, c in words.items() if c > 3]


# (2026-11-18) AI 티 줄이기: 옛 글(사람이 쓴 글 133개)과 문체 비교 결과 (STYLE 'AI 티 줄이기')
_sents = [EMO.sub("", x).strip() for x in re.split(r"(?<=[.!?~])\s+|\n", body) if len(x.strip()) > 3 and not x.strip().startswith(("🏠", "🗺", "🚇", "⏰", "🚗", "📅", "☕", "✨", "💵", "🧡", "⏰", "🪑", "[", "#"))]
_core = [x.rstrip(".!?~ ").strip() for x in _sents]
_n = max(1, len(_core))
r_eoyo = sum(1 for x in _core if re.search(r"(어요|에요|예요|해요|돼요|아요)$", x)) / _n
r_other = sum(1 for x in _core if re.search(r"(답니다|더라고요|습니다|네요|거든요|죠|[^요]다)$", x)) / _n
r_excl = sum(1 for x in _sents if x.rstrip().endswith("!")) / _n
INTENS = ["정말", "진짜", "완전", "엄청", "너무", "무조건", "아주"]
n_int = sum(body.count(w) for w in INTENS)
TEMPLATE = ["직접 먹어보고 느낀 그대로", "직접 가보고 정리한", "정보부터 정리해", "알아두시면 좋은", "방문 전에 알아두"]
tmpl = [t for t in TEMPLATE if t in body]


# (2026-11-18) 글 템플릿: 최근 2개 글과 같은 템플릿 금지 (STYLE '글 템플릿 6종')
import json as _json
from pathlib import Path as _P
TID = getattr(m, "TEMPLATE_ID", "")
_log = _P(__file__).resolve().parent.parent / "data" / "template_log.json"
_recent = [x["template"] for x in (_json.loads(_log.read_text()) if _log.exists() else [])][-2:]
_store = getattr(m, "STORE", "")

checks = [
    ("메인 키워드 지정", bool(MAIN), MAIN or "없음"),
    ("제목 35~45자", 35 <= len(TITLE) <= 45, f"{len(TITLE)}자"),
    ("제목 앞 15자에 메인 키워드", ns(MAIN)[:4] in ns(TITLE[:15]), TITLE[:15]),
    ("첫 문장에 메인 키워드", ns(MAIN) in ns(text_first) or ns(MAIN) in ns(" ".join(lines[:3])), lines[1][:30] if len(lines) > 1 else ""),
    ("소제목 1곳 이상에 메인 키워드", any(ns(MAIN) in ns(h) for h in heads), ""),
    ("본문 메인 키워드 3~5회", 3 <= kw_count <= 5, f"{kw_count}회"),
    ("보조 키워드 본문 포함", all(ns(s) in ns(body + TITLE) for s in SUBS), ", ".join(s for s in SUBS if ns(s) not in ns(body + TITLE)) or "모두 포함"),
    ("태그 맨 앞 메인 키워드", tags and ns(MAIN) in tags[0], tags[0] if tags else ""),
    ("해시태그 15~30개", 15 <= len(tags) <= 30, f"{len(tags)}개"),
    ("본문 길이 (짧게 1,800~2,500 / 보통 2,800~3,800 / 길게 4,500~6,000)", (lambda r: r[0] <= chars <= r[1])({"짧게": (1800, 2500), "보통": (2800, 3800), "길게": (4500, 6000)}.get(getattr(m, "LENGTH", ""), (1800, 6000))), f"{chars:,}자 / {getattr(m, 'LENGTH', '지정 없음')}"),
    ("사진 25장 이상", len(set(imgs)) >= 25, f"{len(set(imgs))}장"),
    ("이모지 40~80개 (사용자: 기본 이모티콘 많이)", 40 <= emoji <= 80, f"{emoji}개"),
    ("이모지 문장 비율 40~70%", 0.4 <= emoji_ratio <= 0.7, f"{emoji_ratio:.0%}"),
    ("빨간색 섹션당 3곳 이하", max(red_by_sec.values() or [0]) <= 3, ", ".join(f"{k[:8]}:{v}" for k, v in red_by_sec.items() if v > 3) or "OK"),
    ("글자 크기 통일 (fs 지정 없음)", not any(len(b) > 2 and b[2].get("fs") for b in paras), ""),
    ("ㅎㅎ 2회 이하", body.count("ㅎㅎ") <= 2, f"{body.count('ㅎㅎ')}회"),
    ("같은 표현 3회 초과 반복 없음", not repeats, ", ".join(repeats) or "OK"),
    ("확인 필요 표시 1곳 이하", sum(1 for b in paras if len(b) > 2 and b[2].get("c")) <= 1, ""),
    ("좋았던 점 파랑 / 아쉬운 점 주황", "[[bl:" in str(B) and "[[o:" in str(B), ""),
    ("주문메뉴는 분홍색만 (⭐주문메뉴⭐ 없음)", "⭐주문메뉴⭐" not in str(B) and "[[p:" in str(B), ""),
    ("맛 후기 첫 줄에 주문 메뉴 재기재", "오늘 주문한 메뉴" in str(B), ""),
    ("장소 지도 블록", any(b[0] == "place" for b in B), ""),
    # 2026-11-12 사용자 지시: 광고 글에도 같은 틀을 쓰므로 '내돈내산'·대가 없음 표현 금지 (제목·본문·태그)
    ("'내돈내산'·'대가 없이'·'협찬 아님' 표현 없음",
     not re.search(r"내돈내산|대가\s*(없이|를\s*받지)|협찬(이나|을)?\s*(받지|없)", TITLE + body + TAGS + str(B)),
     ", ".join(sorted(set(re.findall(r"내돈내산|대가\s*없이|대가를\s*받지|협찬[^ ]*\s*받지", TITLE + body + TAGS + str(B))))) or "OK"),
]
# --- v3 추가 점검 (STYLE.md 5-1, 5-2, 6-2, 7) ---
first_is_img = B[0][0] == "img" or (B[0][0] == "p" and "광고" in B[0][1] and len(B) > 1 and B[1][0] == "img")  # 협찬 글은 광고 링크 다음 사진
# 상위 블로그 문장과 15자 이상 겹침
research = getattr(m, "RESEARCH_DIR", None)
copied = []
if research:
    from pathlib import Path
    ref = "".join(Path(f).read_text() for f in Path(research).glob("*.txt")).replace(" ", "")
    for l in lines:
        if l.startswith(('"', '🏠', '🗺', '🚇', '⏰', '🚗', '📞')) or l.strip().startswith('"'):
            continue  # 사진 속 안내문 직접 인용과 사실 정보 목록은 제외
        t = ns(l)
        for i in range(0, max(0, len(t) - 15)):
            if t[i:i + 16] in ref:
                copied.append(l[:20]); break
# 한 문장 이모지 2개 초과 (🙆‍♀️ 반복 제외)
over_emoji = [l[:15] for l in lines if len([e for e in EMO.findall(re.sub(r'✨[^✨]{2,30}✨', '✨', l)) if "🙆" not in e]) > 2 and not l.startswith(("✨", "💵", "🧡"))]
# 한 문단 색 1가지
INL = re.compile(r"\[\[(r|p|y|g|bl|o):")
multi_color = [plain(b[1])[:15] for b in paras if len(set(INL.findall(b[1]))) > 1]
# 빨강·초록 강조 구절 길이 (2~15자)
long_spans = [t for k, t in re.findall(r"\[\[(r|g):(.+?)\]\]", str([b[1] for b in paras])) if not 2 <= len(t) <= 15]
has_video = any(b[0] == "video" for b in B)

checks += [
    ("글이 사진으로 시작 (대표 사진)", first_is_img, ""),
    ("상위 블로그 문장 그대로 옮김 없음", bool(research) and not copied, ", ".join(copied[:3]) or ("조사 폴더 없음" if not research else "OK")),
    ("한 문장 이모지 2개 이하", not over_emoji, ", ".join(over_emoji[:3]) or "OK"),
    ("한 문단 색 1가지", not multi_color, ", ".join(multi_color[:3]) or "OK"),
    ("[AI티] ~어요/에요 어미 35% 이하", r_eoyo <= 0.35, f"{r_eoyo:.0%}"),
    ("[AI티] 답니다·더라고요·습니다·다 어미 15% 이상", r_other >= 0.15, f"{r_other:.0%}"),
    ("[AI티] 느낌표 문장 15% 이상", r_excl >= 0.15, f"{r_excl:.0%}"),
    ("[AI티] 정말·진짜·완전·엄청 등 6회 이상", n_int >= 6, f"{n_int}회"),
    ("[템플릿] T1~T6 지정, 최근 2개와 다름", bool(re.fullmatch(r"T[1-6]", TID)) and TID not in _recent, f"{TID or '없음'} / 최근 {_recent}"),
    ("[AI티] 템플릿 문구 없음", not tmpl, ", ".join(tmpl) or "OK"),
    ("빨강·초록 강조 2~15자", not long_spans, ", ".join(s[:12] for s in long_spans[:3]) or "OK"),
]
warns = [("클립 영상 1개 (사진 촬영 시 영상도 찍어야 함)", has_video)]

fails = 0
for name, ok in warns:
    print(f"{'✅' if ok else '⚠️ '} {name}")
for name, ok, info in checks:
    fails += not ok
    print(f"{'✅' if ok else '❌'} {name:28} {info}")
print(f"\n통과 {len(checks) - fails}/{len(checks)}")
sys.exit(1 if fails else 0)
