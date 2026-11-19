"""휴대폰용 차트(가로 900px, 글자 크게). 출력: out/m-<ticker>-*.webp"""
import json, io, os, numpy as np, pandas as pd, matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import font_manager as fm
from PIL import Image
FD = "../brand/fonts/suit"
for f in os.listdir(FD):
    if f.endswith(".ttf"): fm.fontManager.addfont(f"{FD}/{f}")
S = json.load(open("data/stats.json")); PR = json.load(open("data/SCHD_profile.json")); ASOF = S["SCHD"]["end"]
INK = "#191f28"; INK2 = "#6b7684"; GRID = "#eceef1"; W = "#ffffff"
C = {"SCHD": "#2a78d6", "DGRO": "#1baf7a", "VYM": "#eb6834", "SPY": "#8b95a1", "안정형": "#6250d6", "성장형": "#008300", "RED": "#e34948"}
plt.rcParams.update({"font.family": "SUIT", "font.size": 24, "axes.edgecolor": GRID, "xtick.color": INK2, "ytick.color": INK2,
    "xtick.labelsize": 22, "ytick.labelsize": 22, "axes.spines.top": False, "axes.spines.right": False, "axes.spines.left": False,
    "axes.grid": True, "axes.grid.axis": "y", "grid.color": GRID, "grid.linewidth": 1.2, "figure.facecolor": W, "axes.facecolor": W,
    "axes.titlesize": 28, "axes.titleweight": "bold", "axes.titlelocation": "left", "axes.titlecolor": INK, "axes.titlepad": 22})
def rd(t):
    s = pd.read_csv(f"data/{t}.csv", index_col=0)["Close"]; s.index = pd.to_datetime([x[:10] for x in s.index]); return s[~s.index.duplicated()]
def save(fig, name, src):
    fig.text(0.02, 0.012, src, color=INK2, fontsize=16); fig.tight_layout(rect=(0, 0.035, 1, 1))
    b = io.BytesIO(); fig.savefig(b, format="png", dpi=100); plt.close(fig)
    im = Image.open(b).convert("RGB"); q = 86; fn = f"out/m-schd-{name}.webp"
    while True:
        im.save(fn, "WEBP", quality=q, method=6)
        if os.path.getsize(fn) < 100_000 or q < 50: break
        q -= 6
SRC = f"Yahoo Finance · 기준일 {ASOF} · 배당 재투자"

# 1 배당 성장
D = S["div_annual"]; ys = list(D); v = [D[y] for y in ys]
fig, ax = plt.subplots(figsize=(9, 8.2)); bars = ax.bar(range(len(ys)), v, color=C["SCHD"], width=0.66)
for i in [0, 4, 8, len(ys) - 1]:
    ax.text(i, v[i] + 0.025, f"${v[i]:.2f}", ha="center", fontsize=23, fontweight="bold", color=INK)
ax.set_xticks(range(0, len(ys), 2), [f"'{y[2:]}" for y in ys[::2]])
ax.yaxis.set_major_formatter(lambda x, p: f"${x:.1f}"); ax.set_ylim(0, max(v) * 1.42); ax.set_yticks([0, 0.5, 1.0])
ax.text(0.09, 0.92, f"13년 동안 {v[-1]/v[0]:.1f}배", transform=ax.transAxes, fontsize=34, fontweight="bold", color=C["SCHD"])
ax.text(0.09, 0.84, f"한 번도 줄지 않음 · 연 {S['div_cagr']*100:.0f}% 성장", transform=ax.transAxes, fontsize=22, color=INK2)
ax.set_title("SCHD 주당 연간 배당금")
save(fig, "dividend-growth", "주당 연간 배당금 합계(분할 반영) · Yahoo Finance")

# 2 연도별 수익률 (최근 8년)
A = S["annual"]; ys = [y for y in A if y >= "2019"]; x = np.arange(len(ys))
fig, ax = plt.subplots(figsize=(9, 8.6))
for off, k, nm in [(-0.2, "SCHD", "SCHD"), (0.2, "SPY", "S&P500")]:
    vals = [A[y][k] * 100 for y in ys]; ax.bar(x + off, vals, 0.38, color=C[k], label=nm)
    for xi, val in zip(x + off, vals):
        ax.text(xi, val + (1.2 if val >= 0 else -1.2), f"{val:.0f}", ha="center", va="bottom" if val >= 0 else "top", fontsize=18, color=C[k] if k == "SCHD" else INK2, fontweight="bold" if k == "SCHD" else "normal")
i0 = ys.index("2023"); ax.axvspan(i0 - 0.5, i0 + 2.5, color="#f7f8fa", zorder=0)
ax.text(i0 + 1, 38, "3년 연속 뒤처짐", ha="center", fontsize=22, fontweight="bold", color=INK)
ax.set_xticks(x, [f"'{y[2:]}" if y != "2026" else "'26*" for y in ys]); ax.axhline(0, color=INK2, lw=1)
ax.set_ylim(-24, 44); ax.yaxis.set_major_formatter(lambda v, p: f"{v:.0f}%")
ax.legend(frameon=False, loc="lower left", fontsize=22, ncol=1)
ax.set_title("연도별 수익률 (%)")
save(fig, "annual-returns", "*2026년은 연초~기준일 · 숫자 = 수익률(%) · Yahoo Finance")

# 3 몬테카를로
V = np.load("data/mc_monthly.npy") / 1e4; t = np.arange(V.shape[1]) / 12; mc = S["mc_monthly"]
fig, ax = plt.subplots(figsize=(9, 8.6))
for lo, hi, al in [(5, 95, .14), (25, 75, .30)]: ax.fill_between(t, np.percentile(V, lo, 0), np.percentile(V, hi, 0), color=C["SCHD"], alpha=al, lw=0)
sp = rd("SPY")[pd.Timestamp(S["SCHD"]["start"]):].resample("ME").last().pct_change().dropna().values[1:]
SS = np.random.default_rng(2026).choice(sp, (1000, 360)); Vs = np.zeros((1000, 361))
for k in range(360): Vs[:, k + 1] = Vs[:, k] * (1 + SS[:, k]) + 50
ms = np.median(Vs, 0) / 1e4; ax.plot(t, ms, color=C["SPY"], lw=2.6)
ax.text(30.6, ms[-1], f"S&P500\n중앙값 {ms[-1]:.1f}억", va="center", fontsize=20, color=C["SPY"], fontweight="bold")
ax.plot(t, np.median(V, 0), color=C["SCHD"], lw=3.5); inv = np.arange(V.shape[1]) * 50 / 1e4; ax.plot(t, inv, color=INK2, lw=2, ls="--")
for val, lab, big in [(mc["p95"], "상위 5%", 0), (mc["median"], "SCHD 중앙값", 1), (mc["p5"], "하위 5%", 0)]:
    ax.text(30.6, val / 1e4, f"{lab}\n{val/1e4:.1f}억", va="center", fontsize=25 if big else 21, fontweight="bold" if big else "normal", color=C["SCHD"] if big else INK)
ax.text(1, 4, f"낸 원금 {inv[-1]:.1f}억", fontsize=20, color=INK2)
ax.set_xlim(0, 37); ax.set_ylim(0, mc["p95"] / 1e4 * 1.08); ax.set_xticks([0, 10, 20, 30], ["0년", "10년", "20년", "30년"])
ax.yaxis.set_major_formatter(lambda v, p: f"{v:.0f}억"); ax.set_title("매달 50만 원 × 30년, 1,000번 결과")
save(fig, "dca-30y", "과거 월간 수익률 무작위 추출 · 세전·물가 미반영 · 미래 보장 아님")

# 4 상관계수 (가로 막대)
co = S["corr"][0][1:]; names = ["S&P500", "장기채", "금", "비트코인"]; o = np.argsort(co)
fig, ax = plt.subplots(figsize=(9, 6.4)); ax.grid(axis="x", color=GRID); ax.grid(axis="y", visible=False); ax.set_axisbelow(True)
ax.barh([names[i] for i in o], [co[i] for i in o], color=[C["SCHD"] if co[i] > 0.5 else "#b9d3f2" for i in o], height=0.6)
for k, i in enumerate(o): ax.text(co[i] + 0.02, k, f"{co[i]:.2f}", va="center", fontsize=26, fontweight="bold", color=INK)
ax.set_xlim(0, 1.05); ax.tick_params(axis="y", labelsize=24, length=0); ax.set_xticks([0, 0.5, 1], ["0 무관", "0.5", "1 같이 움직임"])
ax.set_title("SCHD와 함께 움직이는 정도")
p = S["corr_period"]; save(fig, "correlation", f"월간 수익률 상관계수 · {p[0][:7]}~{p[1][:7]}")

# 5 예시 조합
PF = pd.read_csv("data/portfolios.csv", index_col=0, parse_dates=True) * 1000; fig, ax = plt.subplots(figsize=(9, 8.2))
lab = []
for k, c, nm in [("안정형 (SCHD 60 + IEF 40)", C["안정형"], "안정형"), ("성장형 (SCHD 50 + QQQ 50)", C["성장형"], "성장형"), ("SCHD 단독", C["SCHD"], "SCHD")]:
    s = PF[k]; ax.plot(s.index, s, color=c, lw=3.4 if nm == "SCHD" else 2.6); lab.append((s.iloc[-1], nm, c))
spm = rd("SPY").resample("ME").last(); spm = spm[(spm.index >= PF.index[0] - pd.Timedelta(days=40)) & (spm.index <= PF.index[-1])]
spv = spm / spm.iloc[0] * 1000 * (PF.iloc[0, 0] / 1000); ax.plot(spv.index, spv, color=C["SPY"], lw=2.2); lab.append((spv.iloc[-1], "S&P500", C["SPY"]))
lab.sort(); yy = [l[0] for l in lab]
for k in range(1, len(yy)): yy[k] = max(yy[k], yy[k - 1] + 900)
lab = [(y, nm, c, v0) for (v0, nm, c), y in zip(lab, yy)]
for y, nm, c, val in lab: ax.text(PF.index[-1] + pd.Timedelta(days=90), y, f"{nm}\n{val/1000:.1f}배", va="center", fontsize=21, fontweight="bold", color=c)
if False:
  for val, nm, c in lab: ax.text(PF.index[-1] + pd.Timedelta(days=90), val, f"{nm}\n{val/1000:.1f}배", va="center", fontsize=22, fontweight="bold", color=c)
ax.set_xlim(PF.index[0], pd.Timestamp("2030-03-01")); ax.yaxis.set_major_formatter(lambda v, p: f"{v/1000:.0f}배")
ax.set_xticks(pd.to_datetime(["2012", "2016", "2020", "2024"]), ["'12", "'16", "'20", "'24"]); ax.set_title("1,000만 원 넣었다면 지금 몇 배?")
save(fig, "portfolio", "2011.11~ 월말 · 매년 리밸런싱 · 과거 백테스트, 투자 권유 아님")

# 6 누적 + 낙폭
s = rd("SCHD"); g = s / s.iloc[0]; dd = (s / s.cummax() - 1) * 100
fig, (a1, a2) = plt.subplots(2, 1, figsize=(9, 9.4), sharex=True, gridspec_kw=dict(height_ratios=[2, 1]))
a1.plot(g.index, g, color=C["SCHD"], lw=3); a1.text(g.index[-1], g.iloc[-1] * 1.07, f"{g.iloc[-1]:.1f}배", ha="right", fontsize=30, fontweight="bold", color=C["SCHD"])
a1.yaxis.set_major_formatter(lambda v, p: f"{v:.0f}배"); a1.set_title("상장 이후 성장과 하락폭")
a2.fill_between(dd.index, dd, 0, color=C["RED"], alpha=.18, lw=0); a2.plot(dd.index, dd, color=C["RED"], lw=1.6)
i = dd.idxmin(); a2.text(i + pd.Timedelta(days=200), dd.min() + 2, f"코로나 {dd.min():.0f}%\n6개월 만에 회복", fontsize=20, fontweight="bold", color=INK, va="bottom")
a2.yaxis.set_major_formatter(lambda v, p: f"{v:.0f}%"); a2.set_xticks(pd.to_datetime(["2012", "2016", "2020", "2024"]), ["'12", "'16", "'20", "'24"])
save(fig, "growth-drawdown", SRC)

# 7 유사 ETF
st = pd.Timestamp("2014-06-12"); fig, ax = plt.subplots(figsize=(9, 8.2)); lab = []
for tk, lw in [("SPY", 2.2), ("VYM", 2.4), ("DGRO", 2.4), ("SCHD", 3.4)]:
    s = rd(tk)[st:]; s = s / s.iloc[0]; ax.plot(s.index, s, color=C[tk], lw=lw); lab.append([s.iloc[-1], tk])
lab.sort(); ys2 = [l[0] for l in lab]
for k in range(1, len(ys2)): ys2[k] = max(ys2[k], ys2[k - 1] + 0.32)
for (val, tk), y in zip(lab, ys2):
    ax.text(pd.Timestamp(ASOF) + pd.Timedelta(days=90), y, f"{'S&P500' if tk=='SPY' else tk} {val:.1f}배", va="center", fontsize=22, fontweight="bold", color=C[tk])
ax.set_xlim(st, pd.Timestamp("2030-06-01")); ax.set_yticks([1, 2, 3, 4, 5]); ax.yaxis.set_major_formatter(lambda v, p: f"{v:.0f}배")
ax.set_xticks(pd.to_datetime(["2016", "2020", "2024"]), ["'16", "'20", "'24"]); ax.set_title("2014년에 넣었다면 지금 몇 배?")
save(fig, "vs-peers", "2014.6(DGRO 상장)~ · " + SRC)

# 8 섹터 (가로 막대)
sec = {k: v for k, v in PR["sectors"].items() if v >= 0.01}; o = sorted(sec, key=sec.get)
fig, ax = plt.subplots(figsize=(9, 7.6)); ax.grid(axis="x", color=GRID); ax.grid(axis="y", visible=False); ax.set_axisbelow(True)
ax.barh(o, [sec[k] * 100 for k in o], color=[C["SCHD"] if k in ("필수소비재", "헬스케어", "에너지") else ("#e34948" if k == "정보기술" else "#c9d6e6") for k in o], height=0.62)
for i, k in enumerate(o): ax.text(sec[k] * 100 + 0.4, i, f"{sec[k]*100:.0f}%", va="center", fontsize=24, fontweight="bold", color=INK)
ax.tick_params(axis="y", labelsize=23, length=0); ax.set_xlim(0, 25); ax.xaxis.set_major_formatter(lambda v, p: f"{v:.0f}%")
ax.set_title("섹터 비중 · 기술주는 12%")
save(fig, "sectors", "Alpha Vantage (2026-11-13 기준)")
print(sorted((f, os.path.getsize("out/" + f) // 1024) for f in os.listdir("out") if f.startswith("m-")))
