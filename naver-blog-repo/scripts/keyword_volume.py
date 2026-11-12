"""키워드 월간 검색수 조회 (네이버 검색광고 API 키워드도구).

필요한 환경 변수 (클라우드 환경 설정 → 환경 변수에 추가):
  NAVER_AD_API_KEY      검색광고 > 도구 > API 사용 관리의 '엑세스라이선스'
  NAVER_AD_SECRET       같은 화면의 '비밀키'
  NAVER_AD_CUSTOMER_ID  같은 화면의 'CUSTOMER_ID'

키가 없으면 네이버 자동완성 순서만 보여준다 (검색량 숫자는 없음, 순서가 앞일수록 많이 찾는 검색어).

사용법: python3 keyword_volume.py "마곡 맛집" "양천향교역 맛집" "마곡 라멘"
"""
import base64, hashlib, hmac, json, os, sys, time, urllib.parse, urllib.request

UA = "Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 Mobile/15E148"


def autocomplete(q):
    u = "https://ac.search.naver.com/nx/ac?" + urllib.parse.urlencode({
        "q": q, "con": "1", "frm": "nv", "ans": "2", "r_format": "json", "r_enc": "UTF-8",
        "r_unicode": "0", "t_koreng": "1", "run": "2", "rev": "4", "q_enc": "UTF-8", "st": "100"})
    d = json.loads(urllib.request.urlopen(urllib.request.Request(u, headers={"User-Agent": UA}), timeout=20).read())
    return [i[0] for i in d["items"][0]] if d.get("items") else []


def searchad(hints):
    key, secret, cid = (os.environ.get(k) for k in ("NAVER_AD_API_KEY", "NAVER_AD_SECRET", "NAVER_AD_CUSTOMER_ID"))
    if not (key and secret and cid):
        return None
    path = "/keywordstool"
    ts = str(int(time.time() * 1000))
    sig = base64.b64encode(hmac.new(secret.encode(), f"{ts}.GET.{path}".encode(), hashlib.sha256).digest()).decode()
    qs = urllib.parse.urlencode({"hintKeywords": ",".join(h.replace(" ", "") for h in hints[:5]), "showDetail": "1"})
    req = urllib.request.Request(f"https://api.naver.com{path}?{qs}", headers={
        "X-Timestamp": ts, "X-API-KEY": key, "X-Customer": cid, "X-Signature": sig})
    rows = json.loads(urllib.request.urlopen(req, timeout=20).read())["keywordList"]

    def n(v):  # '< 10' 같은 값 처리
        return 5 if isinstance(v, str) else v
    for r in rows:
        r["total"] = n(r["monthlyPcQcCnt"]) + n(r["monthlyMobileQcCnt"])
    return sorted(rows, key=lambda r: -r["total"])


if __name__ == "__main__":
    kws = sys.argv[1:] or ["마곡 맛집"]
    rows = searchad(kws)
    if rows:
        print(f"{'키워드':24}{'PC':>8}{'모바일':>9}{'합계':>9}  경쟁도")
        for r in rows[:40]:
            print(f"{r['relKeyword']:24}{str(r['monthlyPcQcCnt']):>8}{str(r['monthlyMobileQcCnt']):>9}{r['total']:>9}  {r['compIdx']}")
    else:
        print("검색광고 API 키가 없어 자동완성 순서만 보여줍니다.\n")
        for k in kws:
            try:
                print(f"{k}: " + " > ".join(autocomplete(k)))
            except Exception as e:
                print(f"{k}: 조회 실패 ({e})")
            time.sleep(1)
