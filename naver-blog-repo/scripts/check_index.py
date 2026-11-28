"""최근 글들이 네이버 블로그 검색에 잡히는지 확인 (검색 누락 점검).
사용법: python3 scripts/check_index.py [글 개수=8]
각 글 본문에서 고유한 문장 하나를 골라 따옴표로 블로그 검색 → 내 글이 나오면 '잡힘'."""
import re, sys, time, urllib.parse, urllib.request, html as H
BLOG, N = "seoeunjin13", int(sys.argv[1]) if len(sys.argv) > 1 else 8
UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/130 Safari/537.36"}
get = lambda u: urllib.request.urlopen(urllib.request.Request(u, headers=UA), timeout=30).read().decode("utf-8", "replace")
rss = get(f"https://rss.blog.naver.com/{BLOG}.xml")
items = re.findall(r"<item>.*?<title><!\[CDATA\[(.*?)\]\]></title>.*?<link><!\[CDATA\[.*?/(\d{9,})\?.*?<pubDate>(.*?)</pubDate>", rss, re.S)[:N]
for title, no, date in items:
    page = get(f"https://blog.naver.com/PostView.naver?blogId={BLOG}&logNo={no}")
    body = re.sub(r"<[^>]+>", "\n", page.split('se-main-container', 1)[-1])
    lines = [H.unescape(l).strip() for l in body.split("\n")]
    cand = [l for l in lines if 18 <= len(l) <= 40 and re.search("[가-힣]{4}", l) and not re.search(r"[#:0-9]", l)]
    m = re.match(r"\[(.*?)\]\s*(.*)", title); store = m.group(1).split()[-1] if m else title.split()[0]
    words = [w for w in re.findall(r"[가-힣A-Za-z]{2,}", m.group(2) if m else title) if w not in ("솔직후기", "후기")][:2]
    qs = [" ".join([store] + words), store + " " + " ".join(words[:1])] + ([cand[len(cand) // 2]] if cand else [])
    ok = False
    for q in qs:   # 따옴표 없이 검색 (따옴표 검색은 잡힌 글도 놓침)
        res = get("https://search.naver.com/search.naver?where=blog&query=" + urllib.parse.quote(q))
        if f"{BLOG}/{no}" in res: ok = True; break
        time.sleep(1)
    print(f"{'✅ 잡힘' if ok else '❌ 누락'}  {date[5:16]}  {title[:38]}")
    time.sleep(1.5)
