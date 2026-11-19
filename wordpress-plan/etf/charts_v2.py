"""휴대폰용 차트 v2 (토스풍: 축·눈금선 최소, 둥근 막대, 값 직접 표기, 제목=결론). 출력 out/m-schd-*.webp"""
import json, io, os, numpy as np, pandas as pd, matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import font_manager as fm
from matplotlib.patches import FancyBboxPatch
from PIL import Image
FD = "../brand/fonts/suit"
for f in os.listdir(FD):
    if f.endswith(".ttf"): fm.fontManager.addfont(f"{FD}/{f}")
plt.rcParams.update({"font.family": "SUIT", "figure.facecolor": "white", "axes.facecolor": "white"})
S = json.load(open("data/stats.json")); PR = json.load(open("data/SCHD_profile.json")); ASOF = S["SCHD"]["end"]
INK, INK2, LINE = "#191f28", "#8b95a1", "#f2f4f6"
C = {"SCHD": "#3182f6", "SPY": "#b0b8c1", "SPYBAR": "#d1d6db", "DGRO": "#12936a", "VYM": "#e8590c", "SAFE": "#7048e8", "GROW": "#20a464", "RED": "#f04452"}
def rd(t):
    s = pd.read_csv(f"data/{t}.csv", index_col=0)["Close"]; s.index = pd.to_datetime([x[:10] for x in s.index]); return s[~s.index.duplicated()]
def frame(title, sub, legend=None, h=9.4):
    fig = plt.figure(figsize=(9, h)); top = 1 - 0.62 / h
    fig.text(0.055, top, title, fontsize=30, fontweight="bold", color=INK, va="top")
    fig.text(0.055, top - 0.55 / h, sub, fontsize=20, color=INK2, va="top")
    if legend:
        x = 0.055
        for name, col in legend:
            fig.text(x, top - 1.05 / h, "●", fontsize=18, color=col, va="top"); fig.text(x + 0.035, top - 1.05 / h, name, fontsize=19, color=INK, va="top", fontweight="bold")
            x += 0.05 + 0.024 * len(name) + 0.04
    ax = fig.add_axes([0.07, 0.09, 0.86, top - (1.75 if legend else 1.3) / h - 0.09])
    for sp in ax.spines.values(): sp.set_visible(False)
    ax.tick_params(length=0, labelsize=18, colors=INK2); return fig, ax
def save(fig, name, src):
    fig.text(0.055, 0.025, src, fontsize=14, color=INK2)
    b = io.BytesIO(); fig.savefig(b, format="png", dpi=100); plt.close(fig)
    im = Image.open(b).convert("RGB"); q = 86; fn = f"out/m-schd-{name}.webp"
    while True:
        im.save(fn, "WEBP", quality=q, method=6)
        if os.path.getsize(fn) < 100_000 or q < 50: break
        q -= 6
def rbar(ax, x, y0, w, h, col, asp):
    ax.add_patch(FancyBboxPatch((x - w / 2, y0), w, h, boxstyle=f"round,pad=0,rounding_size={w*0.28}", mutation_aspect=asp, fc=col, ec="none"))
def hgrid(ax, vals, fmt):
    for v in vals:
        ax.axhline(v, color=LINE, lw=1.4, zorder=0); ax.text(ax.get_xlim()[0], v, fmt(v), fontsize=16, color=INK2, va="bottom", ha="left")
    ax.set_yticks([])

# 1 배당 성장
D = S["div_annual"]; ys = list(D); v = [D[y] for y in ys]
fig, ax = frame(f"배당금 13년 동안 {v[-1]/v[0]:.1f}배", f"SCHD 주당 연간 배당금 · 한 번도 줄지 않음 (연 {S['div_cagr']*100:.0f}% 증가)")
ax.set_xlim(-0.7, len(ys) - 0.3); ax.set_ylim(0, max(v) * 1.2); asp = (max(v) * 1.2) / len(ys) * 1.1
for i, val in enumerate(v): rbar(ax, i, 0, 0.62, val, C["SCHD"] if i == len(v) - 1 else "#c9dcfb", asp)
for i in [0, len(v) - 1]: ax.text(i, v[i] + max(v) * 0.03, f"${v[i]:.2f}", ha="center", fontsize=22, fontweight="bold", color=C["SCHD"] if i else INK)
ax.set_xticks(range(0, len(ys), 3), [f"'{y[2:]}" for y in ys[::3]]); ax.set_yticks([])
save(fig, "dividend-growth", "주당 연간 배당금 합계(분할 반영) · Yahoo Finance")

# 2 연도별 수익률
A = S["annual"]; ys = [y for y in A if y >= "2019"]
fig, ax = frame("3년 연속 S&P500에 밀렸다", "연도별 수익률 (%)", [("SCHD", C["SCHD"]), ("S&P500", C["SPYBAR"])], h=9.6)
ax.set_xlim(-0.6, len(ys) - 0.4); ax.set_ylim(-26, 44); asp = 70 / len(ys) * 1.1
i0 = ys.index("2023"); ax.add_patch(FancyBboxPatch((i0 - 0.48, -25), 2.96, 68, boxstyle="round,pad=0,rounding_size=0.2", mutation_aspect=asp, fc="#fff0f1", ec="none", zorder=0))
ax.text(i0 + 1, 39.5, "3년 연속 뒤처짐", ha="center", fontsize=19, fontweight="bold", color=C["RED"])
for k, y in enumerate(ys):
    for off, key, col, fs, fw in [(-0.19, "SCHD", C["SCHD"], 19, "bold"), (0.19, "SPY", C["SPYBAR"], 15, "normal")]:
        val = A[y][key] * 100; rbar(ax, k + off, min(0, val), 0.34, abs(val), col, asp)
        ax.text(k + off, val + (1.5 if val >= 0 else -1.5), f"{val:.0f}", ha="center", va="bottom" if val >= 0 else "top", fontsize=fs, fontweight=fw, color=C["SCHD"] if key == "SCHD" else INK2)
ax.axhline(0, color="#e5e8eb", lw=1.5); ax.set_yticks([])
ax.set_xticks(range(len(ys)), [f"'{y[2:]}" + ("*" if y == "2026" else "") for y in ys])
save(fig, "annual-returns", "*2026년은 연초~기준일 · Yahoo Finance · 배당 재투자")

# 3 몬테카를로
V = np.load("data/mc_monthly.npy") / 1e4; t = np.arange(V.shape[1]) / 12; mc = S["mc_monthly"]
sp = rd("SPY")[pd.Timestamp(S["SCHD"]["start"]):].resample("ME").last().pct_change().dropna().values[1:]
SS = np.random.default_rng(2026).choice(sp, (1000, 360)); Vs = np.zeros((1000, 361))
for k in range(360): Vs[:, k + 1] = Vs[:, k] * (1 + SS[:, k]) + 50
ms = np.median(Vs, 0) / 1e4
fig, ax = frame(f"30년 뒤 중앙값 {mc['median']/1e4:.1f}억", "매달 50만 원씩 적립 · 1,000번 시뮬레이션", [("SCHD", C["SCHD"]), ("S&P500", C["SPY"])], h=9.6)
ax.fill_between(t, np.percentile(V, 5, 0), np.percentile(V, 95, 0), color=C["SCHD"], alpha=.10, lw=0)
ax.fill_between(t, np.percentile(V, 25, 0), np.percentile(V, 75, 0), color=C["SCHD"], alpha=.20, lw=0)
ax.plot(t, ms, color=C["SPY"], lw=3); ax.plot(t, np.median(V, 0), color=C["SCHD"], lw=4)
inv = np.arange(V.shape[1]) * 50 / 1e4; ax.plot(t, inv, color=INK2, lw=1.6, ls=(0, (4, 4)))
ax.set_xlim(0, 39); top = mc["p95"] / 1e4 * 1.05; ax.set_ylim(0, top)
for y_, txt, col, fw, fs in [(mc["p95"] / 1e4, f"상위 5%\n{mc['p95']/1e4:.1f}억", INK2, "normal", 17), (ms[-1] + 1.2, f"S&P500\n{ms[-1]:.1f}억", "#6b7684", "bold", 19),
                             (mc["median"] / 1e4 - 1.2, f"SCHD\n{mc['median']/1e4:.1f}억", C["SCHD"], "bold", 22), (mc["p5"] / 1e4 - 1, f"하위 5%\n{mc['p5']/1e4:.1f}억", INK2, "normal", 17)]:
    ax.text(30.8, y_, txt, va="center", fontsize=fs, fontweight=fw, color=col)
ax.plot(30, mc["median"] / 1e4, "o", ms=11, color=C["SCHD"], mec="white", mew=2.5); ax.plot(30, ms[-1], "o", ms=9, color=C["SPY"], mec="white", mew=2)
ax.text(12, 3.2, f"낸 원금 {inv[-1]:.1f}억", fontsize=16, color=INK2)
ax.set_xlim(0, 39); hgrid(ax, [10, 20, 30, 40, 50], lambda v: f"{v:.0f}억")
ax.set_xticks([0, 10, 20, 30], ["0년", "10년", "20년", "30년"])
save(fig, "dca-30y", "과거 월간 수익률 무작위 추출 · 세전·물가 미반영 · 미래 보장 아님")

# 4 예시 조합
PF = pd.read_csv("data/portfolios.csv", index_col=0, parse_dates=True)
fig, ax = frame("성장주를 섞으면 9.8배", "2011년 말 1,000만 원이 지금 몇 배? (매년 리밸런싱)", [("성장형", C["GROW"]), ("SCHD", C["SCHD"]), ("안정형", C["SAFE"])], h=9.4)
lab = []
for k, c, nm, lw in [("안정형 (SCHD 60 + IEF 40)", C["SAFE"], "안정형", 2.6), ("성장형 (SCHD 50 + QQQ 50)", C["GROW"], "성장형", 2.8), ("SCHD 단독", C["SCHD"], "SCHD", 3.8)]:
    s = PF[k]; ax.plot(s.index, s, color=c, lw=lw); ax.plot(s.index[-1], s.iloc[-1], "o", ms=9, color=c, mec="white", mew=2); lab.append((s.iloc[-1], nm, c))
for val, nm, c in lab: ax.text(PF.index[-1] + pd.Timedelta(days=120), val, f"{val:.1f}배", va="center", fontsize=22, fontweight="bold", color=c)
ax.set_xlim(PF.index[0], pd.Timestamp("2029-06-01")); ax.set_ylim(0.5, 10.8); hgrid(ax, [2, 4, 6, 8, 10], lambda v: f"{v:.0f}배")
ax.set_xticks(pd.to_datetime(["2012", "2016", "2020", "2024"]), ["'12", "'16", "'20", "'24"])
save(fig, "portfolio", "월말 기준 · 과거 백테스트, 투자 권유 아님")

# 5 누적 + 낙폭
s = rd("SCHD"); g = s / s.iloc[0]; dd = (s / s.cummax() - 1) * 100
fig = plt.figure(figsize=(9, 10)); h = 10
fig.text(0.055, 1 - 0.62 / h, f"15년 동안 {g.iloc[-1]:.1f}배", fontsize=30, fontweight="bold", color=INK, va="top")
fig.text(0.055, 1 - 1.17 / h, "상장 때 넣은 돈의 변화와 고점 대비 하락폭", fontsize=20, color=INK2, va="top")
a1 = fig.add_axes([0.07, 0.36, 0.86, 0.46]); a2 = fig.add_axes([0.07, 0.09, 0.86, 0.22])
for a in (a1, a2):
    for sp_ in a.spines.values(): sp_.set_visible(False)
    a.tick_params(length=0, labelsize=18, colors=INK2)
a1.fill_between(g.index, g, 1, color=C["SCHD"], alpha=.08, lw=0); a1.plot(g.index, g, color=C["SCHD"], lw=3.2)
a1.plot(g.index[-1], g.iloc[-1], "o", ms=11, color=C["SCHD"], mec="white", mew=2.5)
a1.text(g.index[-1], g.iloc[-1] + 0.45, f"{g.iloc[-1]:.1f}배", ha="right", fontsize=26, fontweight="bold", color=C["SCHD"])
a1.set_ylim(0.6, 7.6); a1.set_xticks([]); hgrid(a1, [2, 4, 6], lambda v: f"{v:.0f}배")
a2.fill_between(dd.index, dd, 0, color=C["RED"], alpha=.16, lw=0); a2.plot(dd.index, dd, color=C["RED"], lw=1.4)
i = dd.idxmin(); a2.plot(i, dd.min(), "o", ms=9, color=C["RED"], mec="white", mew=2)
a2.text(i + pd.Timedelta(days=150), dd.min() + 1, f"코로나 {dd.min():.0f}%, 6개월 만에 회복", fontsize=18, fontweight="bold", color=INK, va="center")
a2.set_ylim(-38, 3); hgrid(a2, [-20], lambda v: f"{v:.0f}%"); a2.text(a2.get_xlim()[0], 0.5, "하락폭", fontsize=15, color=INK2)
for a in (a1, a2): a.set_xlim(g.index[0], g.index[-1] + pd.Timedelta(days=60))
a2.set_xticks(pd.to_datetime(["2012", "2016", "2020", "2024"]), ["'12", "'16", "'20", "'24"])
save(fig, "growth-drawdown", f"Yahoo Finance · 기준일 {ASOF} · 배당 재투자")

# 6 유사 ETF
st = pd.Timestamp("2014-06-12"); fig, ax = frame("배당 ETF 셋, 성적은 비슷", "2014년에 넣은 돈이 지금 몇 배?", [("SCHD", C["SCHD"]), ("DGRO", C["DGRO"]), ("VYM", C["VYM"]), ("S&P500", C["SPY"])], h=9.4)
lab = []
for tk, lw in [("SPY", 2.4), ("VYM", 2.4), ("DGRO", 2.4), ("SCHD", 3.8)]:
    s = rd(tk)[st:]; s = s / s.iloc[0]; ax.plot(s.index, s, color=C[tk], lw=lw); lab.append([s.iloc[-1], tk])
lab.sort(); yy = [l[0] for l in lab]
for k in range(1, len(yy)): yy[k] = max(yy[k], yy[k - 1] + 0.36)
for (val, tk), y in zip(lab, yy):
    ax.text(pd.Timestamp(ASOF) + pd.Timedelta(days=110), y, f"{val:.1f}배", va="center", fontsize=21 if tk == "SCHD" else 19, fontweight="bold", color=C[tk] if tk != "SPY" else "#6b7684")
ax.set_xlim(st, pd.Timestamp("2029-03-01")); ax.set_ylim(0.6, 5.4); hgrid(ax, [1, 2, 3, 4, 5], lambda v: f"{v:.0f}배")
ax.set_xticks(pd.to_datetime(["2016", "2020", "2024"]), ["'16", "'20", "'24"])
save(fig, "vs-peers", f"2014.6(DGRO 상장)~ · Yahoo Finance · 배당 재투자")

# 7 섹터
sec = {k: v for k, v in PR["sectors"].items() if v >= 0.01}; o = sorted(sec, key=sec.get)
fig, ax = frame("기술주는 12%뿐", "SCHD 섹터 비중", h=8.6)
ax.set_xlim(-6.5, 27); ax.set_ylim(-0.6, len(o) - 0.4); asp = (len(o)) / 33.5 * 1.25
for i, k in enumerate(o):
    col = C["RED"] if k == "정보기술" else (C["SCHD"] if k in ("필수소비재", "헬스케어", "에너지") else "#d1d6db")
    ax.add_patch(FancyBboxPatch((0, i - 0.3), sec[k] * 100, 0.6, boxstyle="round,pad=0,rounding_size=0.3", mutation_aspect=asp * 0.9, fc=col, ec="none"))
    ax.text(-0.6, i, k, ha="right", va="center", fontsize=20, color=INK, fontweight="bold" if col != "#d1d6db" else "normal")
    ax.text(sec[k] * 100 + 0.5, i, f"{sec[k]*100:.0f}%", va="center", fontsize=21, fontweight="bold", color=col if col != "#d1d6db" else INK2)
ax.set_xticks([]); ax.set_yticks([])
save(fig, "sectors", "Alpha Vantage (2026-11-13 기준)")
print("ok")
