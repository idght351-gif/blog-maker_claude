import json, numpy as np, pandas as pd, matplotlib, io, os
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import font_manager as fm
from matplotlib.colors import LinearSegmentedColormap
from PIL import Image
FD="../brand/fonts/suit"
for f in os.listdir(FD):
    if f.endswith(".ttf"): fm.fontManager.addfont(f"{FD}/{f}")
S=json.load(open("data/stats.json")); PR=json.load(open("data/SCHD_profile.json"))
SURF="#ffffff"; INK="#1C283A"; INK2="#52514e"; GRID="#e6e5e0"
BLUE="#2a78d6"; ORANGE="#eb6834"; AQUA="#1baf7a"; YEL="#eda100"; RED="#e34948"; GRAY="#9a9890"
plt.rcParams.update({"font.family":"SUIT","font.size":13,"axes.edgecolor":GRID,"axes.labelcolor":INK2,"xtick.color":INK2,"ytick.color":INK2,
 "axes.spines.top":False,"axes.spines.right":False,"axes.spines.left":False,"axes.grid":True,"axes.grid.axis":"y","grid.color":GRID,"grid.linewidth":.8,
 "figure.facecolor":SURF,"axes.facecolor":SURF,"axes.titlesize":19,"axes.titleweight":"bold","axes.titlelocation":"left","axes.titlecolor":INK,"axes.titlepad":16})
TK=os.environ.get("TICKER","SCHD").lower()
ASOF=S["SCHD"]["end"]
SRC=f"출처: Yahoo Finance · Alpha Vantage · 기준일 {ASOF} · 배당 재투자 기준"
NAMES={"01_top10":"top10-holdings","02_sector":"sector-weights","03_corr":"correlation","04_peers":"vs-vym-dgro-spy","05_growth_mdd":"growth-drawdown","06_annual":"annual-returns-vs-sp500","07_dividend":"dividend-growth","08_montecarlo":"30-year-dca-simulation","09_portfolio":"portfolio-backtest"}
def save(fig,name,src=SRC):
    fig.text(.012,.012,src,color=INK2,fontsize=10.5); fig.tight_layout(rect=(0,.035,1,1))
    b=io.BytesIO(); fig.savefig(b,format="png",dpi=100); plt.close(fig)
    im=Image.open(b).convert("RGB"); q=88
    while True:
        fn=f"out/{TK}-{NAMES[name]}.webp"; im.save(fn,"WEBP",quality=q,method=6)
        if os.path.getsize(fn)<100_000 or q<50: break
        q-=6
def rd(t):
    s=pd.read_csv(f"data/{t}.csv",index_col=0)["Close"]; s.index=pd.to_datetime([x[:10] for x in s.index]); return s[~s.index.duplicated()]
pct=lambda v,p=None:f"{v:.0f}%"

# 1 상위 10 종목
fig,ax=plt.subplots(figsize=(12,6.6)); t=PR["top10"][::-1]
ax.barh([f"{n} ({s})" for s,n,w in t],[w*100 for s,n,w in t],color=BLUE,height=.6); ax.grid(axis="x",color=GRID); ax.grid(axis="y",visible=False)
for i,(s,n,w) in enumerate(t): ax.text(w*100+.06,i,f"{w*100:.1f}%",va="center",color=INK,fontsize=12,fontweight="bold")
top=sum(w for *_,w in PR["top10"])*100
ax.set_title(f"상위 10종목 비중 합계 {top:.0f}%, 한 종목 최대 5% 이하"); ax.set_xlim(0,5.8); ax.xaxis.set_major_formatter(lambda v,p:f"{v:.0f}%"); ax.tick_params(axis="y",length=0)
save(fig,"01_top10",f"출처: Alpha Vantage (2026-11-13 기준) · 총 {PR['holdings_count']}여 종목")

# 2 섹터 도넛
fig,ax=plt.subplots(figsize=(12,6.6)); sec=PR["sectors"]; lab=list(sec); val=[sec[k]*100 for k in lab]
cols=[BLUE,ORANGE,AQUA,YEL,"#e87ba4","#008300","#6250d6",RED,GRAY]
w,_=ax.pie(val,colors=cols,startangle=90,counterclock=False,wedgeprops=dict(width=.38,edgecolor=SURF,linewidth=2.5),radius=1.0,center=(-0.6,0))
ax.text(-0.6,0.08,"섹터",ha="center",fontsize=15,color=INK2); ax.text(-0.6,-0.14,"9개",ha="center",fontsize=24,fontweight="bold",color=INK)
for i,(l,v) in enumerate(zip(lab,val)):
    y=0.9-i*0.22; ax.add_patch(plt.Rectangle((0.75,y-0.06),0.12,0.12,color=cols[i])); ax.text(0.95,y,l,va="center",fontsize=14,color=INK); ax.text(2.35,y,f"{v:.1f}%",va="center",ha="right",fontsize=14,fontweight="bold",color=INK)
ax.set_xlim(-1.75,2.5); ax.set_ylim(-1.15,1.15); ax.set_aspect("equal"); ax.axis("off")
ax.set_title("필수소비재·헬스케어·에너지가 절반, 기술주는 12%")
save(fig,"02_sector","출처: Alpha Vantage (2026-11-13 기준)")

# 3 상관계수
fig,ax=plt.subplots(figsize=(12,7.2)); L=["SCHD","S&P500\n(SPY)","장기채\n(TLT)","금\n(GLD)","비트코인"]; C=np.array(S["corr"])
cm=LinearSegmentedColormap.from_list("d",[BLUE,"#f0efec",ORANGE]); D=C.copy(); np.fill_diagonal(D,np.nan)
ax.imshow(D,cmap=cm,vmin=-1,vmax=1); ax.grid(False)
for i in range(5): ax.add_patch(plt.Rectangle((i-.5,i-.5),1,1,color="#e6e5e0"))
ax.set_xticks(range(5),L); ax.set_yticks(range(5),[l.replace("\n"," ") for l in L]); ax.tick_params(length=0,labelsize=13)
for i in range(5):
    for j in range(5): ax.text(j,i,"—" if i==j else f"{C[i,j]:.2f}",ha="center",va="center",color=INK,fontsize=15,fontweight="bold" if (i==0 or j==0) and i!=j else "normal")
for sp in ax.spines.values(): sp.set_visible(False)
ax.set_title("S&P500과는 함께 움직이고(0.82), 채권·금과는 거의 따로 논다")
p=S["corr_period"]; save(fig,"03_corr",f"월간 수익률 상관계수 · {p[0][:7]}~{p[1][:7]} ({p[2]}개월, 비트코인 상장 이후 공통 기간) · 1에 가까울수록 같이 움직임")

# 4 유사 ETF 비교 (DGRO 상장 이후)
fig,ax=plt.subplots(figsize=(12,6.6)); st=pd.Timestamp("2014-06-12")
lab=[]
for tk,c,lw in [("SPY",YEL,1.8),("VYM",ORANGE,1.8),("DGRO",AQUA,1.8),("SCHD",BLUE,2.8)]:
    s=rd(tk)[st:]; s=s/s.iloc[0]*1000; ax.plot(s.index,s,color=c,lw=lw); lab.append([s.iloc[-1],tk,s.index[-1]])
lab.sort(); ys=[l[0] for l in lab]
for i in range(1,len(ys)): ys[i]=max(ys[i],ys[i-1]+230)
for (v,tk,d),y in zip(lab,ys): ax.text(d+pd.Timedelta(days=60),y,f"{tk} {v:,.0f}만",color=INK,va="center",fontsize=12.5,fontweight="bold" if tk=="SCHD" else "normal")
ax.set_xlim(st,pd.Timestamp("2028-09-01")); ax.yaxis.set_major_formatter(lambda v,p:f"{v:,.0f}만")
ax.set_title("1,000만 원을 2014년에 넣었다면? 네 ETF가 4천만 원 안팎으로 비슷")
save(fig,"04_peers","2014-06-12(DGRO 상장일)~"+ASOF+" · 배당 재투자 · 환율 미반영(달러 기준 상대 비교)")

# 5 누적 성장 + 낙폭
s=rd("SCHD"); g=s/s.iloc[0]*1000; dd=(s/s.cummax()-1)*100
fig,(a1,a2)=plt.subplots(2,1,figsize=(12,8.4),sharex=True,gridspec_kw=dict(height_ratios=[2.2,1]))
a1.plot(g.index,g,color=BLUE,lw=2.4); a1.text(g.index[-1],g.iloc[-1]*1.06,f"{g.iloc[-1]:,.0f}만 원",ha="right",fontsize=14,fontweight="bold",color=INK)
a1.yaxis.set_major_formatter(lambda v,p:f"{v:,.0f}만"); a1.set_title(f"상장 때 1,000만 원 → 지금 {g.iloc[-1]/1000:.1f}배, 최대 -{-dd.min():.0f}% 하락도 6개월 만에 회복")
a2.fill_between(dd.index,dd,0,color=RED,alpha=.18,lw=0); a2.plot(dd.index,dd,color=RED,lw=1.3)
i=dd.idxmin(); a2.annotate(f"코로나 {dd.min():.1f}%",(i,dd.min()),xytext=(12,4),textcoords="offset points",fontsize=12.5,fontweight="bold",color=INK)
a2.yaxis.set_major_formatter(lambda v,p:f"{v:.0f}%"); a2.set_ylabel("고점 대비 하락",fontsize=12)
save(fig,"05_growth_mdd","2011-10-20~"+ASOF+" · 배당 재투자 · 달러 기준")

# 6 연도별 수익률 SCHD vs SPY
A=S["annual"]; ys=[y for y in A if A[y]["SCHD"] is not None]; x=np.arange(len(ys))
fig,ax=plt.subplots(figsize=(12,6.6))
ax.bar(x-.2,[A[y]["SCHD"]*100 for y in ys],.38,color=BLUE,label="SCHD"); ax.bar(x+.2,[A[y]["SPY"]*100 for y in ys],.38,color=YEL,label="S&P500 (SPY)")
ax.axhspan(-30,40,xmin=(ys.index("2023")-.5+.6)/(len(ys)+.2),xmax=(ys.index("2025")+.5+.6)/(len(ys)+.2),color="#e6e5e0",alpha=.5,zorder=0)
ax.text(ys.index("2024"),36,"3년 연속 뒤처짐",ha="center",fontsize=12.5,fontweight="bold",color=INK)
ax.set_xticks(x,[y if y!="2026" else "2026\n(연초~)" for y in ys]); ax.axhline(0,color=INK2,lw=.8); ax.set_ylim(-25,40); ax.set_xlim(-.6,len(ys)-.4)
ax.yaxis.set_major_formatter(lambda v,p:f"{v:.0f}%"); ax.legend(frameon=False,loc="upper left",ncol=2,fontsize=13)
ax.set_title("2023~2025년엔 S&P500에 크게 밀렸지만, 2022년·2026년엔 앞섰다")
save(fig,"06_annual")

# 7 배당 성장
D=S["div_annual"]; ys2=list(D); fig,ax=plt.subplots(figsize=(12,6.6))
ax.bar(ys2,[D[y] for y in ys2],color=BLUE,width=.62)
for y in [ys2[0],ys2[-1]]: ax.text(y,D[y]+.02,f"${D[y]:.2f}",ha="center",fontsize=13,fontweight="bold",color=INK)
ax.yaxis.set_major_formatter(lambda v,p:f"${v:.2f}"); ax.tick_params(axis="x",labelsize=11.5)
ax.set_title(f"주당 연간 배당금 {D[ys2[-1]]/D[ys2[0]]:.1f}배, 13년 동안 한 번도 줄지 않았다 (연 {S['div_cagr']*100:.0f}% 성장)")
save(fig,"07_dividend","주당 연간 배당금 합계 · 2024년 3:1 분할 반영(수정 기준) · 출처: Yahoo Finance")

# 8 몬테카를로
V=np.load("data/mc_monthly.npy")/1e4; t=np.arange(V.shape[1])/12; mc=S["mc_monthly"]
fig,ax=plt.subplots(figsize=(12,6.8))
for lo,hi,al in [(5,95,.16),(25,75,.32)]: ax.fill_between(t,np.percentile(V,lo,0),np.percentile(V,hi,0),color=BLUE,alpha=al,lw=0)
med=np.median(V,0); ax.plot(t,med,color=BLUE,lw=2.6)
inv=np.arange(V.shape[1])*50/1e4; ax.plot(t,inv,color=INK2,lw=1.4,ls="--")
for v,l,b in [(mc["p95"],"상위 5%",False),(mc["median"],"중앙값",True),(mc["p5"],"하위 5%",False)]:
    ax.text(30.4,v/1e4,f"{l}\n{v/1e4:.1f}억",va="center",fontsize=12.5 if b else 11.5,fontweight="bold" if b else "normal",color=INK)
ax.text(24,inv[-1*72]+1.2,f"낸 원금 (30년 {inv[-1]:.1f}억)",fontsize=11.5,color=INK2)
ax.set_xlim(0,34.5); ax.set_ylim(0,mc["p95"]/1e4*1.08); ax.set_xlabel("투자 기간 (년)",fontsize=12)
ax.yaxis.set_major_formatter(lambda v,p:f"{v:.0f}억")
ax.set_title(f"매달 50만 원씩 30년, 1,000번 돌리면 중앙값 {mc['median']/1e4:.1f}억")
save(fig,"08_montecarlo","SCHD 과거 월간 수익률(2011~2026)을 무작위로 다시 뽑는 방식 · 세전·물가 미반영 · 미래 수익 보장 아님")

# 9 예시 포트폴리오
PF=pd.read_csv("data/portfolios.csv",index_col=0,parse_dates=True)*1000; fig,ax=plt.subplots(figsize=(12,6.6))
for k,c,lw in [("안정형 (SCHD 60 + IEF 40)",AQUA,2),("성장형 (SCHD 50 + QQQ 50)",ORANGE,2),("SCHD 단독",BLUE,2.6)]:
    s=PF[k]; ax.plot(s.index,s,color=c,lw=lw); m=S["portfolios"][k]
    ax.text(s.index[-1]+pd.Timedelta(days=60),s.iloc[-1],f"{k.split(' (')[0]} {s.iloc[-1]:,.0f}만\n연 {m['cagr']*100:.1f}% · MDD {m['mdd']*100:.0f}%",va="center",fontsize=11.5,color=INK,fontweight="bold" if k=="SCHD 단독" else "normal")
ax.set_xlim(PF.index[0],pd.Timestamp("2030-06-01")); ax.yaxis.set_major_formatter(lambda v,p:f"{v:,.0f}만")
ax.set_title("예시 조합: 채권을 섞으면 덜 흔들리고, QQQ를 섞으면 더 컸다")
save(fig,"09_portfolio","2011-11~2026-11 월말 기준 · 매년 말 리밸런싱 · 배당 재투자 · 투자 권유 아님(과거 백테스트 예시)")
print(sorted((f,os.path.getsize('out/'+f)//1024) for f in os.listdir("out")))
