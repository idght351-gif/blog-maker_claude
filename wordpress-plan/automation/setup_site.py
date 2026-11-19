from wp import call
# 사용자 표시 이름·소개, 작성자 주소에서 로그인 아이디 숨기기
call("POST", "/users/1", {"name": "직장인 백호", "nickname": "직장인 백호", "slug": "baekho", "url": "https://baekhomoney.com",
     "description": "5년 넘게 주식·ETF에 투자해 온 직장인 개인 투자자. ETF를 직접 계산한 데이터로 소개합니다."})
call("POST", "/settings", {"description": "데이터로 읽는 ETF 리포트"})
# 카테고리
call("POST", "/categories/1", {"name": "ETF 가이드", "slug": "guide", "description": "세금, 계좌, 차트 읽는 법 등 ETF 기초 지식"})
cats = {}
for name, slug, desc in [("배당 ETF","dividend","배당·배당성장·월배당·커버드콜 ETF 분석"),
                         ("성장 ETF","growth","지수·기술주 등 성장형 ETF 분석"),
                         ("채권·금리","bond","채권 ETF와 금리 관련 분석"),
                         ("금·원자재","commodity","금·원자재 ETF 분석"),
                         ("자산배분","allocation","포트폴리오 조합과 백테스트"),
                         ("연금저축·ISA","pension","국내 상장 ETF와 절세 계좌 활용")]:
    cats[slug] = call("POST", "/categories", {"name": name, "slug": slug, "description": desc})["id"]
# 주 메뉴
m = call("POST", "/menus", {"name": "주 메뉴", "locations": ["primary"]})["id"]
def item(title, order, parent=0, **kw):
    return call("POST", "/menu-items", {"title": title, "menus": m, "menu_order": order, "parent": parent, "status": "publish", **kw})["id"]
for i, slug in enumerate(["dividend","growth","bond","commodity","allocation","pension"], 1):
    item(None, i, type="taxonomy", object="category", object_id=cats[slug])
item(None, 7, type="taxonomy", object="category", object_id=1)
about = item(None, 8, type="post_type", object="page", object_id=10)
for i, pid in enumerate([11, 12, 3, 13], 9):
    item(None, i, parent=about, type="post_type", object="page", object_id=pid)
print("ok", cats, "menu", m)
