"""백호 머니 워드프레스 REST 도우미. 인증은 세션 프록시가 자동 주입(헤더 직접 넣지 않음)."""
import json, ssl, urllib.request, os, sys
BASE = "https://baekhomoney.com/wp-json/wp/v2"
_ctx = ssl.create_default_context(cafile=os.environ.get("SSL_CERT_FILE", "/root/.ccr/ca-bundle.crt"))

def call(method, path, data=None, raw=None, headers=None):
    url = path if path.startswith("http") else BASE + path
    h = dict(headers or {})
    body = None
    if raw is not None:
        body = raw
    elif data is not None:
        body = json.dumps(data).encode(); h["Content-Type"] = "application/json"
    req = urllib.request.Request(url, data=body, method=method, headers=h)
    try:
        with urllib.request.urlopen(req, context=_ctx, timeout=60) as r:
            return json.loads(r.read() or b"null")
    except urllib.error.HTTPError as e:
        raise SystemExit(f"{method} {path} -> {e.code} {e.read()[:300]!r}")

def upload_media(path, alt=""):
    name = os.path.basename(path)
    ct = {"webp": "image/webp", "png": "image/png", "jpg": "image/jpeg"}[name.rsplit(".", 1)[1]]
    m = call("POST", "/media", raw=open(path, "rb").read(),
             headers={"Content-Disposition": f"attachment; filename={name}", "Content-Type": ct})
    if alt: call("POST", f"/media/{m['id']}", {"alt_text": alt})
    return m

if __name__ == "__main__":
    print(json.dumps(call(sys.argv[1], sys.argv[2], json.loads(sys.argv[3]) if len(sys.argv) > 3 else None), ensure_ascii=False)[:800])
