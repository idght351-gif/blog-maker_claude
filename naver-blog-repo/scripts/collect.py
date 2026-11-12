"""네이버 블로그 RSS의 글을 모두 받아 구조화된 JSON/Markdown으로 저장한다.

사용법: python3 -I scripts/collect.py <blogId>
"""
import json, re, sys, time, urllib.request, xml.etree.ElementTree as ET
from pathlib import Path
from bs4 import BeautifulSoup

BLOG = sys.argv[1] if len(sys.argv) > 1 else "seoeunjin13"
ROOT = Path(__file__).resolve().parent.parent
RAW, OUT = ROOT / "raw", ROOT / "posts"
RAW.mkdir(exist_ok=True); OUT.mkdir(exist_ok=True)
UA = "Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 Mobile/15E148"


def get(url):
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=30) as r:
        return r.read().decode("utf-8", "replace")


def parse(html):
    soup = BeautifulSoup(html, "html.parser")
    blocks, tags = [], []
    for comp in soup.select("div.se-main-container > div.se-component"):
        cls = comp.get("class", [])
        kind = next((c[3:] for c in cls if c.startswith("se-") and c != "se-component"), "?")
        if kind == "text":
            for p in comp.select("p.se-text-paragraph"):
                hashes = [h.get_text() for h in p.select(".__se-hash-tag")]
                if hashes:
                    tags += hashes
                    continue
                text = p.get_text().replace("​", "")
                align = next((c.split("-")[-1] for c in p.get("class", []) if "align" in c), "")
                fs = sorted({c for s in p.select("span") for c in s.get("class", []) if c.startswith("se-fs-")})
                bold = bool(p.select("b, strong, .se-bold"))
                blocks.append({"t": "text", "text": text, "align": align, "fs": fs, "bold": bold})
        elif kind in ("image", "imageStrip", "imageGroup"):
            n = len(comp.select("img.se-image-resource")) or 1
            cap = comp.select_one(".se-caption")
            blocks.append({"t": kind, "count": n, "caption": cap.get_text(" ", strip=True) if cap else ""})
        elif kind == "quotation":
            style = next((c for c in cls if c.startswith("se-l-")), "")
            blocks.append({"t": "quote", "style": style, "text": comp.get_text("\n", strip=True)})
        elif kind == "places":
            blocks.append({"t": "place", "text": comp.get_text(" ", strip=True)[:200]})
        elif kind in ("sticker",):
            blocks.append({"t": "sticker"})
        elif kind in ("horizontalLine",):
            blocks.append({"t": "hr", "style": " ".join(c for c in cls if c.startswith("se-l-"))})
        elif kind not in ("documentTitle",):
            blocks.append({"t": kind, "text": comp.get_text(" ", strip=True)[:200]})
    return blocks, tags


def to_md(post):
    lines = [f"# {post['title']}", f"카테고리: {post['category']} | {post['date']}", ""]
    for b in post["blocks"]:
        if b["t"] == "text":
            mark = []
            if b["align"] and b["align"] != "justify": mark.append(b["align"])
            mark += [f.replace("se-fs-", "") for f in b["fs"] if f != "se-fs-fs15"]
            if b["bold"]: mark.append("bold")
            lines.append((f"[{','.join(mark)}] " if mark else "") + b["text"])
        elif b["t"] in ("image", "imageStrip", "imageGroup"):
            lines.append(f"[사진 {b['count']}장{' - ' + b['caption'] if b['caption'] else ''}]")
        elif b["t"] == "quote":
            lines.append(f"[인용구 {b['style']}] " + b["text"].replace("\n", " / "))
        elif b["t"] == "place":
            lines.append(f"[지도] {b['text']}")
        else:
            lines.append(f"[{b['t']}] {b.get('text', '')}")
    lines += ["", "태그: " + " ".join(post["tags"])]
    return "\n".join(lines)


SPONSOR_MARKERS = ("reviewnote.cloud", "cloudfront.net/contract/track", "dinnerqueen.net", "revu.net",
                   "popomon.com", "stylec.co.kr")
SPONSOR_TEXT = ("제공받아 작성",)


def sponsor_of(html):
    """체험단 배너(글 앞뒤 3개 컴포넌트의 외부 이미지)나 고지 문구가 있으면 그 출처를 돌려준다."""
    comps = BeautifulSoup(html, "html.parser").select("div.se-main-container > div.se-component")
    for comp in comps[:3] + comps[-3:]:
        for img in comp.select("img"):
            src = img.get("data-lazy-src") or img.get("src") or ""
            hit = next((m for m in SPONSOR_MARKERS if m in src), "")
            if hit:
                return hit
    text = " ".join(c.get_text(" ") for c in comps)
    return next((t for t in SPONSOR_TEXT if t in text), "")


def post_list():
    H = {"User-Agent": UA, "Referer": f"https://m.blog.naver.com/{BLOG}"}
    out, page = [], 1
    while True:
        url = f"https://m.blog.naver.com/api/blogs/{BLOG}/post-list?categoryNo=0&itemCount=30&page={page}"
        req = urllib.request.Request(url, headers=H)
        items = json.load(urllib.request.urlopen(req, timeout=30))["result"]["items"]
        if not items:
            return out
        out += items
        page += 1
        time.sleep(1)


def main():
    index = []
    for it in post_list():
        no = str(it["logNo"])
        html_path = RAW / f"{no}.html"
        if not html_path.exists():
            html_path.write_text(get(f"https://m.blog.naver.com/PostView.naver?blogId={BLOG}&logNo={no}"))
            time.sleep(1.5)
        html = html_path.read_text()
        blocks, tags = parse(html)
        date = time.strftime("%Y-%m-%d", time.localtime(it["addDate"] / 1000))
        title = it["titleWithInspectMessage"].replace("​", "").strip()
        post = {"logNo": no, "title": title, "category": str(it["categoryNo"]), "date": date,
                "blocks": blocks, "tags": tags}
        (OUT / f"{no}.json").write_text(json.dumps(post, ensure_ascii=False, indent=1))
        (OUT / f"{no}.md").write_text(to_md(post))
        n_img = sum(b.get("count", 0) for b in blocks)
        n_chr = sum(len(b.get("text", "")) for b in blocks if b["t"] == "text")
        index.append({"logNo": no, "title": title, "date": date, "sponsor": sponsor_of(html),
                      "likes": it["sympathyCnt"], "comments": it["commentCnt"],
                      "views": None, "images": n_img, "chars": n_chr, "tags": len(tags)})
    (OUT / "index.json").write_text(json.dumps(index, ensure_ascii=False, indent=1))
    print(len(index), "posts,", sum(1 for x in index if x["sponsor"]), "sponsored")


main()
