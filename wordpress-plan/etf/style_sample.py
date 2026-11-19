import json, numpy as np, matplotlib, os
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import font_manager as fm
from matplotlib.patches import FancyBboxPatch
from PIL import Image
for f in os.listdir("../brand/fonts/suit"):
    if f.endswith(".ttf"): fm.fontManager.addfont("../brand/fonts/suit/" + f)
plt.rcParams.update({"font.family": "SUIT", "figure.facecolor": "white", "axes.facecolor": "white"})
S = json.load(open("data/stats.json")); A = S["annual"]; ys = [y for y in A if y >= "2019"]
INK = "#191f28"; INK2 = "#8b95a1"; BLUE = "#3182f6"; GRAY = "#d1d6db"
fig = plt.figure(figsize=(9, 9.4)); ax = fig.add_axes([0.04, 0.10, 0.92, 0.62])
fig.text(0.05, 0.94, "SCHD, 3년 연속 S&P500에 밀렸다", fontsize=31, fontweight="bold", color=INK)
fig.text(0.05, 0.895, "연도별 수익률 (%)", fontsize=21, color=INK2)
fig.text(0.05, 0.845, "●", fontsize=20, color=BLUE); fig.text(0.085, 0.845, "SCHD", fontsize=20, color=INK, fontweight="bold")
fig.text(0.21, 0.845, "●", fontsize=20, color=GRAY); fig.text(0.245, 0.845, "S&P500", fontsize=20, color=INK2)
w = 0.36
def bar(x, v, c):
    h = abs(v); y0 = 0 if v >= 0 else v
    ax.add_patch(FancyBboxPatch((x - w / 2, y0), w, h, boxstyle="round,pad=0,rounding_size=0.12", mutation_aspect=8, fc=c, ec="none"))
i0 = ys.index("2023")
ax.add_patch(FancyBboxPatch((i0 - 0.5, -26), 3, 72, boxstyle="round,pad=0,rounding_size=0.25", mutation_aspect=10, fc="#fff1f1", ec="none", zorder=0))
ax.text(i0 + 1, 41, "3년 연속 뒤처짐", ha="center", fontsize=20, fontweight="bold", color="#e5484d")
for k, y in enumerate(ys):
    s, p = A[y]["SCHD"] * 100, A[y]["SPY"] * 100
    bar(k - 0.19, s, BLUE); bar(k + 0.19, p, GRAY)
    ax.text(k - 0.19, s + 1.6 if s >= 0 else s - 1.6, f"{s:.0f}", ha="center", va="bottom" if s >= 0 else "top", fontsize=19, fontweight="bold", color=BLUE)
    ax.text(k + 0.19, p + 1.6 if p >= 0 else p - 1.6, f"{p:.0f}", ha="center", va="bottom" if p >= 0 else "top", fontsize=16, color=INK2)
    ax.text(k, -27.5, f"'{y[2:]}" + ("*" if y == "2026" else ""), ha="center", va="top", fontsize=19, color=INK2)
ax.axhline(0, color="#e5e8eb", lw=1.5)
ax.set_xlim(-0.6, len(ys) - 0.4); ax.set_ylim(-26, 46); ax.axis("off")
fig.text(0.05, 0.035, "*2026년은 연초~기준일 · Yahoo Finance · 배당 재투자", fontsize=15, color=INK2)
fig.savefig("out/_s.png", dpi=100); plt.close(fig)
a = Image.open("out/m-schd-annual-returns.webp").convert("RGB"); b = Image.open("out/_s.png").convert("RGB")
a = a.resize((390, int(a.height * 390 / a.width))); b = b.resize((390, int(b.height * 390 / b.width)))
s = Image.new("RGB", (800, max(a.height, b.height)), "white"); s.paste(a, (0, 0)); s.paste(b, (410, 0)); s.save("out/style-compare.png"); os.remove("out/_s.png")
