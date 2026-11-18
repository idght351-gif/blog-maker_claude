import pandas as pd, numpy as np, json
def rd(t):
    s=pd.read_csv(f"data/{t}.csv",index_col=0)["Close"]; s.index=pd.to_datetime([x[:10] for x in s.index]); return s[~s.index.duplicated()]
P={t:rd(t) for t in ["SCHD","VYM","DGRO","SPY","TLT","GLD","BTC-USD","IEF","QQQ","KRW=X"]}
M=pd.DataFrame({t:s.resample("ME").last() for t,s in P.items()})
R=M.pct_change()
out={}
def stats(d):  # daily series
    yrs=(d.index[-1]-d.index[0]).days/365.25; cagr=(d.iloc[-1]/d.iloc[0])**(1/yrs)-1
    m=d.resample("ME").last().pct_change().dropna(); vol=m.std()*12**.5
    dd=d/d.cummax()-1; i=dd.idxmin(); peak=d[:i].idxmax()
    rec=d[i:][d[i:]>=d[peak]]; rec=rec.index[0] if len(rec) else None
    return dict(start=str(d.index[0].date()),end=str(d.index[-1].date()),years=round(yrs,1),cagr=cagr,vol=vol,mdd=dd.min(),
                mdd_peak=str(peak.date()),mdd_trough=str(i.date()),mdd_recover=str(rec.date()) if rec is not None else None,mult=d.iloc[-1]/d.iloc[0])
s=P["SCHD"]; out["SCHD"]=stats(s)
fx=P["KRW=X"].reindex(s.index).ffill(); out["SCHD_KRW"]=stats(s*fx)
# 연도별
Y=pd.DataFrame({t:P[t].resample("YE").last() for t in ["SCHD","SPY"]}).pct_change()
first=P["SCHD"].iloc[0]; Y.loc[Y.index[0],"SCHD"]=np.nan
out["annual"]={str(i.year):{k:(None if pd.isna(v) else round(v,4)) for k,v in r.items()} for i,r in Y.iterrows() if i.year>=2012}
# 비교 (DGRO 상장 이후 공통 기간)
st=P["DGRO"].index[0]
out["peers"]={t:stats(P[t][st:]) for t in ["SCHD","VYM","DGRO","SPY"]}
for t in ["SCHD","VYM","DGRO"]:
    dv=pd.read_csv(f"data/{t}_div.csv",index_col=0)["Dividends"]; dv.index=pd.to_datetime([x[:10] for x in dv.index])
    ttm=dv[dv.index>P[t].index[-1]-pd.Timedelta(days=365)].sum(); out["peers"][t]["yield_ttm"]=ttm/P[t].iloc[-1]
    if t=="SCHD":
        a=dv.groupby(dv.index.year).sum(); a=a[(a.index>=2012)&(a.index<=2025)]
        out["div_annual"]={str(k):round(v,4) for k,v in a.items()}; out["div_cagr"]=(a.iloc[-1]/a.iloc[0])**(1/(len(a)-1))-1
# 상관 (BTC 포함 공통기간, 월간)
c=R[["SCHD","SPY","TLT","GLD","BTC-USD"]].dropna(); out["corr"]=c.corr().round(2).values.tolist(); out["corr_period"]=[str(c.index[0].date()),str(c.index[-1].date()),len(c)]
# 포트폴리오 (연 1회 리밸런싱, 월간)
def port(w):
    r=R[list(w)].dropna(); r=r[r.index>"2011-10-31"]; v=1.0; cur=dict(w); vals=[]
    for d,row in r.iterrows():
        tot=sum(cur[k]*(1+row[k]) for k in w); cur={k:cur[k]*(1+row[k])/tot*1 for k in w}; v*=tot
        if d.month==12: cur=dict(w)
        vals.append(v)
    return pd.Series(vals,index=r.index)
PF={"SCHD 단독":port({"SCHD":1.0}),"안정형 (SCHD 60 + IEF 40)":port({"SCHD":.6,"IEF":.4}),"성장형 (SCHD 50 + QQQ 50)":port({"SCHD":.5,"QQQ":.5})}
def mstats(v):
    yrs=len(v)/12; return dict(cagr=v.iloc[-1]**(1/yrs)-1,vol=v.pct_change().fillna(v.iloc[0]-1).std()*12**.5,mdd=(v/v.cummax()-1).min(),mult=v.iloc[-1])
out["portfolios"]={k:mstats(v) for k,v in PF.items()}
pd.DataFrame(PF).to_csv("data/portfolios.csv")
# 몬테카를로: SCHD 월간 수익률 부트스트랩, 1000회 x 360개월
rng=np.random.default_rng(2026); r=R["SCHD"].dropna().values; r=r[1:]
S=rng.choice(r,(1000,360),replace=True)
def mc(init,monthly):
    v=np.zeros((1000,361)); v[:,0]=init; inv=np.zeros(361); inv[0]=init
    for m in range(360): v[:,m+1]=v[:,m]*(1+S[:,m])+monthly; inv[m+1]=inv[m]+monthly
    # 경로별 MDD: 납입 영향 제외한 수익률 지수 기준
    idx=np.cumprod(1+S,1); mdd=(idx/np.maximum.accumulate(idx,1)-1).min(1)
    f=v[:,-1]; return v,dict(invested=inv[-1],p5=np.percentile(f,5),p25=np.percentile(f,25),median=np.median(f),mean=f.mean(),p75=np.percentile(f,75),p95=np.percentile(f,95),max=f.max(),min=f.min(),
        mdd_median=np.median(mdd),mdd_p5=np.percentile(mdd,5),loss_prob=(f<inv[-1]).mean())
v1,out["mc_monthly"]=mc(0,50); v2,out["mc_lump"]=mc(1000,0)   # 단위: 만 원
np.save("data/mc_monthly.npy",v1)
json.dump(out,open("data/stats.json","w"),ensure_ascii=False,indent=1,default=float)
def p(x): return f"{x*100:.1f}%"
print("SCHD",{k:(p(v) if k in("cagr","vol","mdd") else v) for k,v in out["SCHD"].items()})
print("KRW cagr",p(out["SCHD_KRW"]["cagr"]))
for t,d in out["peers"].items(): print(t,p(d["cagr"]),p(d["vol"]),p(d["mdd"]),round(d["mult"],2),p(d.get("yield_ttm",0)))
print("div",out["div_annual"],"cagr",p(out["div_cagr"]))
print("corr",out["corr_period"],out["corr"][0])
for k,d in out["portfolios"].items(): print(k,p(d["cagr"]),p(d["vol"]),p(d["mdd"]),round(d["mult"],2))
for k in ["mc_monthly","mc_lump"]: print(k,{a:(round(b) if abs(b)>2 else round(b,3)) for a,b in out[k].items()})
print("annual",{y:(d["SCHD"],d["SPY"]) for y,d in out["annual"].items()})
