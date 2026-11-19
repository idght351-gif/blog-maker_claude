"""유튜브 인기 영상 댓글 수집(무료 YouTube Data API v3, 키는 프록시가 X-Goog-Api-Key로 주입).
사용: python3 yt_comments.py "SCHD 배당" [영상수=4] → ../etf/data/yt_<검색어>.json 저장 + 공감순 상위 댓글 요약 출력
할당량: 검색 100 + 영상정보 1 + 댓글 영상당 1~2 (하루 무료 10,000)"""
import json, sys, ssl, urllib.request, urllib.parse, html, re, os
ctx = ssl.create_default_context(cafile=os.environ.get("SSL_CERT_FILE", "/root/.ccr/ca-bundle.crt"))
API = "https://www.googleapis.com/youtube/v3/"
def get(ep, **p):
    with urllib.request.urlopen(API + ep + "?" + urllib.parse.urlencode(p), context=ctx, timeout=30) as r: return json.load(r)
# --- 사용량 관리: 무료 한도는 '하루' 10,000단위(미국 태평양 시간 자정 초기화). 계획 = 하루 글 3편 × 글당 최대 150단위 ---
import datetime, zoneinfo
LOG = "../etf/data/yt_quota.json"; DAY_POSTS = 3; POST_UNITS = 150
today = datetime.datetime.now(zoneinfo.ZoneInfo("America/Los_Angeles")).date().isoformat()
log = json.load(open(LOG)) if os.path.exists(LOG) else {}
used = log.get(today, {"posts": 0, "units": 0})
if used["posts"] >= DAY_POSTS and "--force" not in sys.argv:
    sys.exit(f"오늘 이미 {used['posts']}편 수집({used['units']}단위). 하루 {DAY_POSTS}편 계획 초과 → 내일 하거나 --force")
args = [a for a in sys.argv[1:] if a != "--force"]
q = args[0]; n = min(int(args[1]) if len(args) > 1 else 4, 4)
ids = [i["id"]["videoId"] for i in get("search", part="id", q=q, type="video", order="viewCount", regionCode="KR", relevanceLanguage="ko", maxResults=15)["items"]]
vids = get("videos", part="snippet,statistics", id=",".join(ids))["items"]
vids = [v for v in vids if re.search(r"[가-힣]", v["snippet"]["title"]) and int(v["statistics"].get("commentCount", 0)) >= 100]
vids = sorted(vids, key=lambda v: -int(v["statistics"]["commentCount"]))[:n]
out = []
for v in vids:
    t = get("commentThreads", part="snippet", videoId=v["id"], order="relevance", maxResults=100, textFormat="plainText")
    for it in t.get("items", []):
        s = it["snippet"]["topLevelComment"]["snippet"]
        out.append({"video": v["snippet"]["title"][:40], "likes": s.get("likeCount", 0), "replies": it["snippet"].get("totalReplyCount", 0), "text": html.unescape(s["textDisplay"]).replace("\n", " ")})
safe = re.sub(r"\W+", "_", q)
json.dump({"query": q, "videos": [(v["snippet"]["title"], int(v["statistics"]["viewCount"]), int(v["statistics"]["commentCount"])) for v in vids], "comments": out},
          open(f"../etf/data/yt_{safe}.json", "w"), ensure_ascii=False, indent=1)
units = 100 + 1 + len(vids)
used = {"posts": used["posts"] + 1, "units": used["units"] + units}; log[today] = used
json.dump(dict(sorted(log.items())[-60:]), open(LOG, "w"), indent=1)
print(f"사용량: 이번 {units}단위 · 오늘 {used['posts']}편 {used['units']}단위 / 무료 10,000 (하루 {DAY_POSTS}편 계획)")
print("영상:", [(v["snippet"]["title"][:25], v["statistics"]["viewCount"]) for v in vids])
for c in sorted(out, key=lambda c: -(c["likes"] + 3 * c["replies"]))[:35]:
    print(f'{c["likes"]:>5} ♥ {c["replies"]:>3}↩ | {c["text"][:90]}')
