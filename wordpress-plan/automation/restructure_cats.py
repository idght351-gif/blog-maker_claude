from wp import call
call("POST", "/settings", {"default_category": 2})
call("POST", "/categories/2", {"name": "배당 ETF", "slug": "dividend", "description": "배당·배당성장·월배당·커버드콜 ETF 리포트"})
call("POST", "/categories/3", {"name": "성장 ETF", "slug": "growth", "description": "지수·기술주·테마 등 성장형 ETF 리포트"})
call("POST", "/categories/4", {"name": "안전자산 ETF", "slug": "safe-asset", "description": "채권·금·원자재 ETF 리포트"})
for mid in (17, 18, 19, 20): call("DELETE", f"/menu-items/{mid}?force=true")
for cid in (5, 6, 7, 1): call("DELETE", f"/categories/{cid}?force=true")
tags = {}
for name, slug in [("미국상장","us-listed"),("국내상장","kr-listed"),("연금저축","pension-savings"),("ISA","isa"),("IRP","irp"),
                   ("월배당","monthly-dividend"),("커버드콜","covered-call"),("채권","bond"),("금","gold"),("원자재","commodity")]:
    tags[slug] = call("POST", "/tags", {"name": name, "slug": slug})["id"]
call("POST", "/menu-items/16", {"title": "안전자산 ETF", "menu_order": 3})
call("POST", "/menu-items", {"title": "국내상장 ETF", "menus": 8, "menu_order": 4, "status": "publish",
                             "type": "taxonomy", "object": "post_tag", "object_id": tags["kr-listed"]})
call("POST", "/menu-items/21", {"menu_order": 5})
print("cats", [(c["id"], c["name"]) for c in call("GET", "/categories")])
print("tags", tags)
print("menu", [(i["title"]["rendered"], i["parent"]) for i in call("GET", "/menu-items?menus=8&per_page=50&orderby=menu_order&order=asc")])
