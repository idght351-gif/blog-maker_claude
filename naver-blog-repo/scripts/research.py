import json, re, sys, time, urllib.request, urllib.parse
from pathlib import Path
from bs4 import BeautifulSoup
UA = "Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 Mobile/15E148"
def get(u):
    return urllib.request.urlopen(urllib.request.Request(u, headers={"User-Agent": UA}), timeout=30).read().decode("utf-8","replace")
q, out = sys.argv[1], Path(sys.argv[2]); out.mkdir(parents=True, exist_ok=True)
seen, res = [], []
for start in (1, 16, 31):
    h = get("https://m.search.naver.com/search.naver?where=m_blog&query="+urllib.parse.quote(q)+f"&start={start}")
    for b, n in re.findall(r"blog\.naver\.com/([A-Za-z0-9_\-]+)/(\d{9,})", h):
        if (b, n) not in seen and b != "seoeunjin13": seen.append((b, n))
    if len(seen) >= 14: break
for b, n in seen[:14]:
    try:
        s = BeautifulSoup(get(f"https://m.blog.naver.com/{b}/{n}"), "html.parser")
        main = s.select_one("div.se-main-container")
        if not main: continue
        t = (s.select_one(".se-title-text") or s.select_one("title")).get_text(" ", strip=True)
        body = "\n".join(p.get_text().replace("​","").strip() for p in main.select("p.se-text-paragraph"))
        sp = bool(re.search(r"제공받|협찬|원고료|체험단|지원받|소정의", body))
        (out/f"{b}_{n}.txt").write_text(t+"\n\n"+body)
        res.append({"blog": b, "logNo": n, "title": t, "sponsored": sp, "chars": len(body)})
        print(b, n, sp, len(body), t[:60])
    except Exception as e:
        print("err", b, n, e)
    time.sleep(0.4)
    if len([r for r in res if not r["sponsored"]]) >= 10: break
json.dump(res, open(out/"top10.json","w"), ensure_ascii=False, indent=1)
