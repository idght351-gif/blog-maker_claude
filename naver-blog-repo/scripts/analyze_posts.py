"""다른 블로그 글을 받아 구조 지표를 뽑는다. 사용법: python3 analyze_posts.py <search.json> <출력폴더>"""
import json, re, sys, time, urllib.request
from pathlib import Path
from bs4 import BeautifulSoup
UA = "Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 Mobile/15E148"
EMO = re.compile(r'(?:[\U0001F300-\U0001FAFF☀-➿⭐⭕⌚-⏿](?:️)?(?:‍[\U0001F300-\U0001FAFF☀-➿](?:️)?)*)')
SPON = re.compile(r'제공받|협찬|원고료|체험단|지원받|소정의')

def get(u, ref=None):
    h = {"User-Agent": UA}
    if ref: h["Referer"] = ref
    return urllib.request.urlopen(urllib.request.Request(u, headers=h), timeout=30).read().decode("utf-8", "replace")

def engagement(bid, no):
    for page in range(1, 8):
        try:
            d = json.loads(get(f"https://m.blog.naver.com/api/blogs/{bid}/post-list?categoryNo=0&itemCount=30&page={page}", "https://m.blog.naver.com/"))
        except Exception:
            return None
        items = d["result"]["items"]
        if not items: return None
        for i in items:
            if str(i["logNo"]) == no: return i["sympathyCnt"], i["commentCnt"]
        time.sleep(0.5)
    return None

def feats(html, kw):
    s = BeautifulSoup(html, "html.parser")
    main = s.select_one("div.se-main-container")
    if not main: return None
    comps = main.select(":scope > div.se-component")
    kinds = {}
    for c in comps:
        k = next((x[3:] for x in c.get("class", []) if x.startswith("se-") and x not in ("se-component",) and not x.startswith("se-l-") and not x.startswith("se-component")), "?")
        kinds[k] = kinds.get(k, 0) + 1
    paras = [p.get_text().replace("​", "").strip() for p in main.select("div.se-text p.se-text-paragraph")]
    lines = [p for p in paras if p and not p.startswith("#")]
    body = "\n".join(lines)
    imgs = main.select("img.se-image-resource")
    gif = sum(1 for i in imgs if ".gif" in (i.get("data-lazy-src") or i.get("src") or "").lower())
    spans = main.select("div.se-text span")
    colored = sum(1 for sp in spans if re.search(r'(?<!background-)color:\s*#(?!000000|333333)', sp.get("style", "")))
    bg = sum(1 for sp in spans if "background-color" in sp.get("style", ""))
    bold = len(main.select("div.se-text b"))
    center = sum(1 for p in main.select("div.se-text p.se-text-paragraph") if "align-center" in " ".join(p.get("class", [])))
    tags = re.findall(r"#[^\s#]+", " ".join(h.get_text() for h in main.select(".__se-hash-tag"))) or re.findall(r"#[^\s#<]+", s.select_one("div.post_tag, .post_tag") .get_text() if s.select_one("div.post_tag, .post_tag") else "")
    title = (s.select_one(".se-title-text") or s.select_one("title")).get_text(" ", strip=True)
    kwc = kw.replace(" ", "")
    head = " ".join(lines[:6])
    return {
        "title": title, "title_len": len(title),
        "chars": len(body), "lines": len(lines), "avg_line": round(len(body) / max(1, len(lines)), 1),
        "images": len(imgs), "gif": gif, "video": kinds.get("video", 0) + kinds.get("oembed", 0),
        "sticker": kinds.get("sticker", 0), "quote": kinds.get("quotation", 0), "oglink": kinds.get("oglink", 0),
        "map": kinds.get("placesMap", 0) + kinds.get("map", 0), "table": kinds.get("table", 0), "hr": kinds.get("horizontalLine", 0),
        "bold": bold, "colored": colored, "bg": bg, "center_ratio": round(center / max(1, len(paras)), 2),
        "emoji": sum(len(EMO.findall(l)) for l in lines), "emoji_line_ratio": round(sum(1 for l in lines if EMO.search(l)) / max(1, len(lines)), 2),
        "kw_in_title": kwc in title.replace(" ", ""), "kw_count_body": body.replace(" ", "").count(kwc),
        "tags": len(tags), "sponsored": bool(SPON.search(body)),
        "summary_top": bool(re.search(r"(요약|한줄평|한 줄 평|총평|정리|TL;DR|미리보기)", head)),
        "first_lines": lines[:3],
    }

if __name__ == "__main__":
    search = json.load(open(sys.argv[1])); out = Path(sys.argv[2]); out.mkdir(exist_ok=True)
    rows = []
    for kw, links in search.items():
        for rank, (bid, no) in enumerate(links, 1):
            f = out / f"{bid}_{no}.html"
            if not f.exists():
                f.write_text(get(f"https://m.blog.naver.com/PostView.naver?blogId={bid}&logNo={no}")); time.sleep(1.2)
            r = feats(f.read_text(), kw)
            if not r: continue
            e = engagement(bid, no)
            r.update({"kw": kw, "rank": rank, "blog": bid, "logNo": no, "likes": e[0] if e else None, "comments": e[1] if e else None})
            rows.append(r); print(kw, rank, bid, r["chars"], r["images"], e)
    json.dump(rows, open(out / "features.json", "w"), ensure_ascii=False, indent=1)
