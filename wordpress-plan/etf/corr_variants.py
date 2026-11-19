import json, numpy as np, matplotlib, os
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import font_manager as fm
from matplotlib.colors import LinearSegmentedColormap
for f in os.listdir("../brand/fonts/suit"):
    if f.endswith(".ttf"): fm.fontManager.addfont("../brand/fonts/suit/" + f)
plt.rcParams.update({"font.family": "SUIT", "figure.facecolor": "white", "axes.facecolor": "white"})
S = json.load(open("data/stats.json")); C = np.array(S["corr"]); L = ["SCHD", "S&P500", "장기채", "금", "비트코인"]
INK = "#191f28"; INK2 = "#6b7684"
cm = LinearSegmentedColormap.from_list("b", ["#ffffff", "#2a78d6"])
# C: 반쪽 히트맵 (아래 삼각형), 큰 글씨
fig, ax = plt.subplots(figsize=(9, 8.6))
n = 5
for i in range(n):
    for j in range(n):
        if j >= i: continue
        v = C[i, j]; ax.add_patch(plt.Rectangle((j, n - 1 - i), 0.96, 0.96, color=cm(min(1, max(0, v))), ec="white"))
        hi = (j == 0)
        ax.text(j + 0.48, n - 1 - i + 0.48, f"{v:.2f}", ha="center", va="center", fontsize=30 if hi else 25,
                fontweight="bold" if hi else "normal", color="white" if v > 0.6 else INK)
for i in range(1, n): ax.text(-0.12, n - 1 - i + 0.48, L[i], ha="right", va="center", fontsize=24, color=INK)
for j in range(n - 1): ax.text(j + 0.48, n - 0.75, L[j], ha="center", va="bottom", fontsize=23, color=INK if j else "#2a78d6", fontweight="bold" if j == 0 else "normal")
ax.add_patch(plt.Rectangle((0, 0), 0.96, n - 1 - 0.04, fill=False, ec="#2a78d6", lw=3))
ax.set_xlim(-1.9, n - 0.9); ax.set_ylim(-0.4, n + 0.1); ax.axis("off")
ax.text(-1.9, n + 0.05, "자산끼리 함께 움직이는 정도", fontsize=28, fontweight="bold", color=INK, va="bottom")
ax.text(-1.9, -0.35, "1에 가까울수록 같이 움직임 · 파란 테두리 = SCHD 기준 · 월간 수익률 2014~", fontsize=16, color=INK2)
fig.savefig("out/m-schd-correlation-heatmap.png", dpi=100, bbox_inches="tight"); plt.close(fig)
from PIL import Image
im = Image.open("out/m-schd-correlation-heatmap.png").convert("RGB"); im.save("out/m-schd-correlation-heatmap.webp", "WEBP", quality=86, method=6)
a = Image.open("out/m-schd-correlation.webp").convert("RGB"); b = im
a = a.resize((390, int(a.height * 390 / a.width))); b = b.resize((390, int(b.height * 390 / b.width)))
s = Image.new("RGB", (800, max(a.height, b.height) + 40), "white"); s.paste(a, (0, 40)); s.paste(b, (410, 40))
from PIL import ImageDraw, ImageFont
d = ImageDraw.Draw(s); f = ImageFont.truetype("../brand/fonts/suit/SUIT-Bold.ttf", 20)
d.text((10, 8), "A. 가로 막대 (지금)", font=f, fill=INK); d.text((420, 8), "B. 반쪽 히트맵 (박스형 개선)", font=f, fill=INK)
s.save("out/corr-compare.png")
