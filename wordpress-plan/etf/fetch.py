import yfinance as yf, pandas as pd, time, sys
T=["SCHD","VYM","DGRO","SPY","TLT","GLD","BTC-USD","IEF","QQQ","KRW=X"]
for t in T:
    for k in range(4):
        try:
            d=yf.Ticker(t).history(period="max",interval="1d",auto_adjust=True)
            if len(d): d[["Close"]].to_csv(f"data/{t}.csv"); print(t,len(d),d.index[0].date(),d.index[-1].date()); break
        except Exception as e: print(t,"err",e); 
        time.sleep(5*(k+1))
    time.sleep(1)
s=yf.Ticker("SCHD"); s.dividends.to_csv("data/SCHD_div.csv"); print("div",len(s.dividends))
