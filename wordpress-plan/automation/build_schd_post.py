"""SCHD 글을 워드프레스에 임시저장(draft). 이미지 업로드 → 본문 HTML → 글 생성."""
import json, os
from wp import call, upload_media
OUT = "../etf/out"; S = json.load(open("../etf/data/stats.json"))
ASOF = S["SCHD"]["end"]; TODAY = "2026-11-19"
IMG = {  # 파일: alt
 "schd-thumbnail.webp": "SCHD 배당률·배당금·단점 총정리 썸네일. 총보수 0.06%, 분기 배당, 30년 시뮬레이션",
 "schd-dividend-growth.webp": "SCHD 주당 연간 배당금 막대그래프. 2012년 0.27달러에서 2025년 1.05달러로 매년 증가",
 "schd-top10-holdings.webp": "SCHD 상위 10종목 비중. 텍사스 인스트루먼트 4.8%, P&G 4.3%, 코카콜라 4.2% 순",
 "schd-sector-weights.webp": "SCHD 섹터 비중 도넛 차트. 필수소비재 20.4%, 헬스케어 18.9%, 에너지 14.7%",
 "schd-growth-drawdown.webp": "SCHD 상장 이후 1,000만 원 누적 성장과 고점 대비 하락폭 그래프",
 "schd-annual-returns-vs-sp500.webp": "SCHD와 S&P500 연도별 수익률 비교 막대그래프, 2023~2025년 SCHD 부진",
 "schd-correlation.webp": "SCHD와 S&P500, 장기채, 금, 비트코인 월간 수익률 상관계수 히트맵",
 "schd-vs-vym-dgro-spy.webp": "2014년부터 SCHD, VYM, DGRO, SPY 1,000만 원 누적 성장 비교",
 "schd-30-year-dca-simulation.webp": "SCHD 매달 50만 원 30년 적립식 몬테카를로 1,000회 시뮬레이션 팬 차트",
 "schd-portfolio-backtest.webp": "SCHD 단독, 안정형(SCHD 60+IEF 40), 성장형(SCHD 50+QQQ 50) 백테스트 비교",
}
U = {}
for f, alt in IMG.items():
    m = upload_media(os.path.join(OUT, f), alt); U[f] = (m["id"], m["source_url"], alt)
face = upload_media(os.path.join(OUT, "baekho_face.webp"), "백호 캐릭터 얼굴")["source_url"]

def fig(f, cap=""):
    i, src, alt = U[f]
    c = f'<figcaption style="font-size:13px;color:#55626f">{cap}</figcaption>' if cap else ""
    return f'<figure class="wp-block-image"><img src="{src}" alt="{alt}" class="wp-image-{i}" loading="lazy" style="border-radius:12px;border:1px solid #dbe7ee"/>{c}</figure>'
def baekho(t):
    return (f'<div style="display:flex;gap:12px;align-items:flex-start;background:#e2f2f9;border-radius:16px;padding:14px 16px;margin:22px 0">'
            f'<img src="{face}" alt="" style="width:48px;height:48px;border-radius:50%;flex:none;margin:0"/>'
            f'<div><strong style="display:block;font-size:13px;color:#2a78d6">백호 한마디</strong>{t}</div></div>')
def box(title, items):
    li = "".join(f"<li>{x}</li>" for x in items)
    return f'<div style="background:#f5fafc;border:1px solid #dbe7ee;border-radius:14px;padding:16px 20px;margin:16px 0"><strong>{title}</strong><ul style="margin:8px 0 0">{li}</ul></div>'
def table(head, rows, me=None):
    th = "".join(f"<th>{h}</th>" for h in head) if head else ""
    tr = "".join("<tr>" + "".join((f"<td><strong>{c}</strong></td>" if r[0] == me else f"<td>{c}</td>") for c in r) + "</tr>" for r in rows)
    return f'<figure class="wp-block-table"><table>{"<thead><tr>"+th+"</tr></thead>" if th else ""}<tbody>{tr}</tbody></table></figure>'
P = lambda x: f"{x*100:.1f}%"
s, pe, pf, mc, ml = S["SCHD"], S["peers"], S["portfolios"], S["mc_monthly"], S["mc_lump"]
A = S["annual"]; D = S["div_annual"]; ok = lambda v: f"{v/1e4:.1f}억"
kpi = "".join(f'<div style="flex:1 1 120px;background:#fff;border:1px solid #dbe7ee;border-radius:14px;padding:12px 8px;text-align:center"><b style="display:block;font-size:22px">{v}</b><span style="font-size:13px;color:#55626f">{k}</span></div>'
              for v, k in [("0.06%", "총보수"), ("약 3.0%", "배당률(최근 1년)"), (P(s["cagr"]), "연평균 수익률"), (P(s["mdd"]), "최대 낙폭")])

html = f"""
<p style="font-size:13px;color:#55626f">이 글은 공개 데이터를 직접 계산한 정보 글이며, 특정 상품의 매수·매도를 권하지 않습니다. 데이터 기준일 {ASOF}.</p>
<div style="display:flex;flex-wrap:wrap;gap:10px;margin:20px 0">{kpi}</div>
<p>SCHD는 "배당 ETF 하나만 고르라면"이라는 질문에 가장 자주 나오는 이름입니다. 저도 아직 SCHD를 사지 않았고, 사기 전에 직접 확인해 보려고 15년 치 주가와 배당 데이터를 내려받아 계산했습니다. 배당률과 배당금, 연평균 수익률은 물론이고 남들이 잘 말하지 않는 <strong>단점</strong>과 <strong>매달 적립식으로 30년 투자했을 때의 결과</strong>까지 숫자로 정리했어요.</p>

<h2>SCHD는 어떤 ETF인가: 운용사·상장일·총보수</h2>
<p>정식 이름은 <strong>Schwab U.S. Dividend Equity ETF</strong>입니다. 미국 찰스 슈왑의 자산운용사가 2011년 10월 20일에 상장했고, <strong>다우존스 미국 배당 100 지수</strong>를 따라갑니다. 10년 이상 배당을 줬고 재무가 탄탄한 미국 기업 100곳을 골라 담는 구조예요.</p>
{table(None, [["운용사","Schwab Asset Management"],["상장일","2011년 10월 20일"],["추종 지수","Dow Jones U.S. Dividend 100"],["총보수","연 0.06%"],["순자산","약 1,211억 달러"],["배당 주기","분기 (3·6·9·12월)"],["보유 종목 수","약 100개 (연 1회 교체)"],["참고","2024년 10월 3:1 주식 분할"]])}
<p>총보수 0.06%는 1,000만 원을 넣었을 때 1년 비용이 6천 원이라는 뜻입니다. 오래 들고 갈수록 이 차이가 커져요.</p>

<h2>SCHD 배당금·배당률·배당일</h2>
<p>최근 1년(4회) 동안 받은 주당 배당금은 <strong>약 1.06달러</strong>이고, 기준일 주가(34.70달러)로 나누면 <strong>배당률은 약 3.0%</strong>입니다. 배당락일은 보통 <strong>3·6·9·12월 하순</strong>이고, 실제 지급은 그 며칠 뒤에 이뤄집니다.</p>
{table(["배당락일","주당 배당금"], [["2025-12-10","$0.278"],["2026-03-25","$0.257"],["2026-06-24","$0.253"],["2026-09-23","$0.267"]])}
{fig("schd-dividend-growth.webp")}
<p>제가 SCHD에 계속 관심이 가는 이유는 이 그래프 때문입니다. 주당 연간 배당금이 2012년 ${D["2012"]:.2f}에서 2025년 ${D["2025"]:.2f}로 <strong>13년 동안 한 번도 줄지 않고 3.9배</strong>가 됐어요. 연 {S["div_cagr"]*100:.0f}%씩 늘어난 셈이라, 오래 들고 있을수록 처음 산 가격 대비 배당률이 계속 올라갑니다.</p>
{baekho("주가가 쉬는 해에도 배당은 꾸준히 커졌어. 이게 SCHD를 오래 들고 가는 이유야.")}

<h2>SCHD 구성 종목과 섹터 비중</h2>
{fig("schd-top10-holdings.webp")}
<p>상위 10종목을 합쳐도 41%이고, 가장 큰 종목도 5%를 넘지 않습니다. 텍사스 인스트루먼트, P&amp;G, 코카콜라, 셰브론처럼 이름만 들어도 아는 배당 기업들이 고르게 들어 있어요.</p>
{fig("schd-sector-weights.webp")}
<p>섹터를 보면 성격이 더 분명해집니다. <strong>필수소비재·헬스케어·에너지가 절반 이상</strong>이고 정보기술은 12% 정도예요. 경기가 나빠도 사람들이 계속 쓰는 물건과 서비스를 파는 기업이 중심이라는 뜻이고, 반대로 AI·빅테크가 시장을 끌어올릴 때는 덜 오를 수밖에 없는 구조입니다.</p>

<h2>SCHD 연평균 수익률과 10년 수익률</h2>
{fig("schd-growth-drawdown.webp")}
{table(None, [["연평균 수익률 (상장 이후, 달러·배당 재투자)", P(s["cagr"])],["최근 10년 연평균 수익률","13.1% (같은 기간 S&amp;P500 14.6%)"],["연평균 수익률 (원화 환산)", P(S["SCHD_KRW"]["cagr"])],["배당세 15% 차감 시 (대략)", f"약 {(s['cagr']-0.0045)*100:.1f}%"],["연 변동성", P(s["vol"])],["최대 낙폭", f"{P(s['mdd'])} (2020.1~2020.3)"],["회복까지 걸린 기간","약 6개월 (2020.9 회복)"]])}
<p>상장 때 넣은 1,000만 원은 지금 약 {s["mult"]*1000:,.0f}만 원이 됐습니다. 원화 수익률이 더 높은 건 같은 기간 달러 환율이 올랐기 때문이에요. 반대로 환율이 내리면 원화 수익률이 깎일 수 있습니다.</p>

<h2>SCHD 단점: 3년 연속 S&amp;P500에 밀린 이유</h2>
{fig("schd-annual-returns-vs-sp500.webp")}
<p>솔직히 제가 가장 아쉬웠던 부분이 여기예요. <strong>2023~2025년 3년 연속 S&amp;P500에 크게 밀렸습니다.</strong> 2023년에는 S&amp;P500이 {A["2023"]["SPY"]*100:.0f}% 오를 때 SCHD는 {A["2023"]["SCHD"]*100:.1f}%에 그쳤어요. 기술주 비중이 12%뿐이라 AI 랠리를 거의 못 탔기 때문입니다.</p>
<p>대신 금리 충격이 컸던 2022년에는 S&amp;P500이 {A["2022"]["SPY"]*100:.0f}%일 때 {A["2022"]["SCHD"]*100:.0f}%로 버텼고, 2026년 들어서는 기준일까지 SCHD {A["2026"]["SCHD"]*100:.0f}%, S&amp;P500 {A["2026"]["SPY"]*100:.0f}%로 반대로 앞서고 있어요. 시장 분위기에 따라 성적표가 뒤집히는 ETF라는 걸 기억해 두면 좋습니다.</p>
{box("SCHD 단점 정리", ["기술주 비중이 낮아 성장장에서는 S&amp;P500보다 덜 오름","분기 배당이라 매달 현금흐름이 필요하면 아쉬움 (국내 상장 상품은 월분배)","미국 상장이라 환율과 배당세 15%를 함께 신경 써야 함"])}

<h2>SCHD와 S&amp;P500·채권·금·비트코인 상관계수</h2>
{fig("schd-correlation.webp")}
<p>상관계수는 두 자산이 얼마나 같은 방향으로 움직이는지를 -1에서 1 사이로 나타낸 값입니다. SCHD는 <strong>S&amp;P500과 0.82</strong>로 큰 흐름을 같이 타고, <strong>장기채(0.08)·금(0.12)과는 거의 따로</strong> 움직여요. 비트코인과는 0.25로 약하게만 연결돼 있습니다. 배당 ETF라고 하락장 방패가 되지는 않으니, 분산 효과를 원하면 채권이나 금을 섞어야 해요.</p>

<h2>SCHD vs DGRO·VYM·미국배당다우존스 비교</h2>
{fig("schd-vs-vym-dgro-spy.webp")}
<p>DGRO가 상장한 2014년 6월부터 똑같이 1,000만 원을 넣었다고 가정했습니다. 결과는 생각보다 비슷하고, 차이는 배당률과 흔들림에서 납니다.</p>
{table(["2014.6~"+ASOF[:7].replace("-","."),"연평균","최대 낙폭","배당률","총보수"],
 [["SCHD",P(pe["SCHD"]["cagr"]),P(pe["SCHD"]["mdd"]),P(pe["SCHD"]["yield_ttm"]),"0.06%"],
  ["DGRO (배당 성장)",P(pe["DGRO"]["cagr"]),P(pe["DGRO"]["mdd"]),P(pe["DGRO"]["yield_ttm"]),"0.08%"],
  ["VYM (고배당)",P(pe["VYM"]["cagr"]),P(pe["VYM"]["mdd"]),P(pe["VYM"]["yield_ttm"]),"0.06%"],
  ["SPY (S&amp;P500)",P(pe["SPY"]["cagr"]),P(pe["SPY"]["mdd"]),"-","-"]], me="SCHD")}
<p>SCHD는 셋 중 <strong>배당률이 가장 높으면서 수익률도 뒤지지 않는</strong> 쪽입니다. 배당보다 성장을 더 원하면 DGRO, 더 많은 종목에 넓게 나누고 싶으면 VYM이 대안이에요.</p>
{box("국내 상장 쌍둥이: 미국배당다우존스 ETF", ["TIGER·SOL·ACE 미국배당다우존스는 SCHD와 같은 지수를 따라갑니다.","연금저축·ISA·IRP 계좌에서 살 수 있습니다. 상품별 분배 주기와 총보수는 각 운용사 홈페이지에서 확인해 주세요.","상장 기간이 짧아 이 글의 장기 그래프에는 넣지 않았어요. 국내 상장 ETF 글은 <a href=\"/tag/kr-listed/\">국내상장 ETF 모음</a>에서 이어집니다."])}

<h2>SCHD 적립식 30년 투자하면 얼마? (몬테카를로 시뮬레이션)</h2>
<p>미래를 한 줄로 예측하는 대신, SCHD의 과거 월간 수익률 180여 개를 무작위로 다시 뽑아 30년(360개월) 경로를 1,000개 만들었습니다. 이런 방법을 몬테카를로 시뮬레이션이라고 해요.</p>
{fig("schd-30-year-dca-simulation.webp")}
{table(["30년 뒤 평가액","월 50만 원 적립","1,000만 원 거치"],
 [["낸 원금","1.8억","0.1억"],["최악 (1,000번 중 최저)",ok(mc["min"]),ok(ml["min"])],["하위 5%",ok(mc["p5"]),ok(ml["p5"])],
  ["중앙값",ok(mc["median"]),ok(ml["median"])],["평균",ok(mc["mean"]),ok(ml["mean"])],["상위 5%",ok(mc["p95"]),ok(ml["p95"])],
  ["예상 최대 낙폭 (중앙값 / 나쁜 5%)", f"{P(mc['mdd_median'])} / {P(mc['mdd_p5'])}", ""]], me="중앙값")}
<p>평균이 중앙값보다 높은 건 크게 성공한 몇몇 경우가 평균을 끌어올리기 때문이에요. 현실 감각에는 <strong>중앙값</strong>이 더 가깝습니다. 그리고 30년 동안 적어도 한 번은 고점에서 25~40% 빠지는 구간을 겪는다고 보는 게 맞아요.</p>
{box("이 숫자를 그대로 믿으면 안 되는 이유", ["지난 15년은 미국 주식이 특히 좋았던 기간이고, 그 수익률을 30년에 반복한 결과입니다.","세금, 물가, 환율은 빠져 있습니다.","보수적으로 연 8%만 가정하면 같은 적립식의 30년 결과는 약 7.5억입니다."])}

<h2>SCHD를 섞은 예시 조합 2가지 (백테스트)</h2>
{fig("schd-portfolio-backtest.webp")}
{table(["2011.11~"+ASOF[:7].replace("-","."),"연평균","변동성","최대 낙폭*"],
 [[k,P(v["cagr"]),P(v["vol"]),P(v["mdd"])] for k,v in pf.items()], me="SCHD 단독")}
<p style="font-size:13px;color:#55626f">* 월말 가격 기준이라 일별 기준({P(s['mdd'])})보다 작게 나옵니다. 매년 말 리밸런싱, 배당 재투자 기준의 과거 백테스트이며 투자 권유가 아닙니다.</p>
<p>제가 가장 관심 있게 본 건 <strong>성장형 조합</strong>이에요. SCHD가 약했던 2023~2025년을 QQQ가 메워 줬고, 변동성은 SCHD 단독과 거의 같았습니다. 반대로 성장주를 이미 갖고 있다면 SCHD를 섞어 배당과 안정감을 더하는 용도로 쓰기 좋아요. 다만 QQQ가 유난히 좋았던 기간이라 앞으로도 같은 결과가 나온다는 보장은 없습니다.</p>
{baekho("나는 성장주에 SCHD를 섞는 쪽이 끌려. 서로 약한 해를 메워 주거든!")}

<h2>정리: SCHD는 이런 분께 맞아요</h2>
{box("한눈에 정리", ["<strong>잘 맞는 분</strong>: 배당이 해마다 늘어나는 걸 보며 오래 모을 분, 성장주 위주 계좌에 안정감을 더하고 싶은 분","<strong>아쉬울 수 있는 분</strong>: 기술주 랠리를 다 따라가고 싶은 분, 매달 현금흐름이 필요한 분","<strong>기억할 숫자</strong>: 총보수 0.06%, 배당률 약 3.0%, 배당 13년 연속 증가, 최대 낙폭 -33%"])}
<p>저는 이번에 데이터를 뽑아 보고 "SCHD 하나로 끝"보다는 <strong>성장주 옆에 두는 분산용</strong>이 더 맞다는 생각이 들었어요. 다른 배당 ETF 분석은 <a href="/category/dividend/">배당 ETF</a> 카테고리에서 이어집니다.</p>

<h2>자주 묻는 질문</h2>
<h3>SCHD로 월 배당 100만 원 받으려면 얼마가 필요한가요?</h3>
<p>세후 월 100만 원은 1년에 1,200만 원입니다. 배당률 3.0%에 미국 배당세 15%를 빼면 실제로 받는 비율은 약 2.6%라서, <strong>약 4.6억 원</strong>이 필요합니다. 다만 배당금이 해마다 늘어 왔기 때문에 일찍 사서 오래 들고 있으면 필요한 원금은 더 적어집니다. 환율에 따라 원화 금액은 달라집니다.</p>
<h3>SCHD 배당락일과 배당 지급일은 언제인가요?</h3>
<p>분기마다 한 번, 보통 3·6·9·12월 하순에 배당락이 되고 며칠 뒤 지급됩니다. 배당락일 전날까지 보유해야 그 분기 배당을 받습니다. 정확한 날짜는 운용사 공지에서 확인하세요.</p>
<h3>연금저축이나 ISA로 SCHD를 살 수 있나요?</h3>
<p>SCHD는 미국 상장 ETF라 연금저축·ISA·IRP 계좌에서 직접 살 수 없습니다. 같은 지수를 따르는 국내 상장 <strong>미국배당다우존스 ETF</strong>(TIGER·SOL·ACE 등)로 대신 투자할 수 있어요.</p>
<h3>SCHD 배당금에 세금은 얼마나 붙나요?</h3>
<p>일반 해외 주식 계좌라면 미국에서 배당금의 15%를 떼고 입금됩니다. 국내 배당소득세율(15.4%)과 비슷해 보통 추가로 내는 세금은 없지만, 이자·배당 등 금융소득이 연 2,000만 원을 넘으면 종합과세 대상이 됩니다. 개인 상황에 따라 다를 수 있으니 필요하면 세무 전문가와 상담하세요.</p>

<div style="display:flex;gap:14px;align-items:center;border:1px solid #dbe7ee;border-radius:16px;padding:16px;margin:36px 0 16px;background:#fff">
<img src="{face}" alt="직장인 백호 프로필" style="width:56px;height:56px;border-radius:50%;flex:none;margin:0"/>
<div style="font-size:14px;line-height:1.6"><strong><a href="/author-profile/">직장인 백호</a></strong><br>5년 넘게 주식·ETF에 투자해 온 직장인 개인 투자자. ETF를 직접 계산한 데이터로 소개합니다.<br><span style="color:#55626f">작성일 {TODAY} · 데이터 기준일 {ASOF} · 다음 업데이트: 다음 분기 배당 반영 시</span></div></div>
<p style="font-size:13px;color:#55626f;line-height:1.7"><strong>출처</strong>: Schwab Asset Management 공식 상품 페이지(<a href="https://www.schwabassetmanagement.com/products/schd" target="_blank" rel="noopener">schwabassetmanagement.com</a>), 가격·배당 Yahoo Finance, 구성 종목·섹터 Alpha Vantage(2026-11-13 기준). 모든 수익률은 배당 재투자 기준으로 직접 계산했습니다.<br><strong>면책</strong>: 이 글은 정보 제공 목적이며 투자 권유가 아닙니다. 과거 수익률과 시뮬레이션 결과는 미래 수익을 보장하지 않습니다. 자세한 내용은 <a href="/disclaimer/">면책 고지</a>를 확인하세요.</p>
"""
html = "\n".join(l for l in html.splitlines() if l.strip())
post = call("POST", "/posts", {
    "title": "SCHD 배당률·배당금·단점 총정리 (2026) | 적립식 30년 투자하면 얼마?",
    "slug": "schd", "status": "draft", "content": html,
    "excerpt": f"SCHD 배당률 약 3.0%, 연평균 수익률 {P(s['cagr'])}, 최대 낙폭 {P(s['mdd'])}. 배당금·배당일, 3년 연속 S&P500에 밀린 단점, DGRO·VYM 비교, 월 50만 원 적립식 30년 시뮬레이션까지 직접 계산한 데이터로 정리했습니다.",
    "categories": [2], "tags": [9], "featured_media": U["schd-thumbnail.webp"][0], "comment_status": "open"})
json.dump({"post_id": post["id"], "media": {k: v[0] for k, v in U.items()}}, open("../etf/data/wp_schd.json", "w"))
print(post["id"], post["status"], post["link"], len(html))
