import json, numpy as np, matplotlib, os
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import font_manager as fm
from matplotlib.colors import LinearSegmentedColormap
from PIL import Image
for f in os.listdir("../brand/fonts/suit"):
    if f.endswith(".ttf"): fm.fontManager.addfont("../brand/fonts/suit/" + f)
plt.rcParams.update({"font.family": "SUIT", "figure.facecolor": "white"})
S = json.load(open("data/stats.json")); C = np.array(S["corr"]); L = ["SCHD", "S&P500", "장기채", "금", "비트코인"]; n = 5
INK = "#191f28"; INK2 = "#6b7684"
cm = LinearSegmentedColormap.from_list("rb", ["#e34948", "#f7f7f7", "#2a78d6"])   # 0=빨강(따로) 0.5=흰색 1=파랑(같이)
fig, ax = plt.subplots(figsize=(9, 9.6))
for i in range(n):
    for j in range(n):
        y = n - 1 - i
        if i == j:
            ax.add_patch(plt.Rectangle((j, y), 0.96, 0.96, color="#eceef1")); ax.text(j + .48, y + .48, "1.00", ha="center", va="center", fontsize=20, color=INK2); continue
        v = C[i, j]; col = cm(min(1, max(0, v)))
        ax.add_patch(plt.Rectangle((j, y), 0.96, 0.96, color=col))
        dark = v > 0.7 or v < 0.15
        ax.text(j + .48, y + .48, f"{v:.2f}", ha="center", va="center", fontsize=27 if (i == 0 or j == 0) else 23,
                fontweight="bold" if (i == 0 or j == 0) else "normal", color="white" if dark else INK)
for k in range(n):
    ax.text(-0.12, n - 1 - k + .48, L[k], ha="right", va="center", fontsize=22, color="#2a78d6" if k == 0 else INK, fontweight="bold" if k == 0 else "normal")
    ax.text(k + .48, -0.12, L[k], ha="center", va="top", fontsize=20, color="#2a78d6" if k == 0 else INK, fontweight="bold" if k == 0 else "normal")
ax.add_patch(plt.Rectangle((-0.02, n - 1 - 0.02), n, 1.0, fill=False, ec=INK, lw=2.5))
ax.set_xlim(-1.75, n); ax.set_ylim(-0.9, n + 0.8); ax.set_aspect("equal"); ax.axis("off")
ax.text(-1.75, n + 0.55, "자산끼리 함께 움직이는 정도", fontsize=28, fontweight="bold", color=INK)
# 범례 막대
for k in range(50):
    ax.add_patch(plt.Rectangle((0.5 + k * 0.07, n + 0.12), 0.07, 0.18, color=cm(k / 49), lw=0))
ax.text(0.45, n + 0.21, "0 따로", ha="right", va="center", fontsize=17, color=INK2); ax.text(4.05, n + 0.21, "1 같이", ha="left", va="center", fontsize=17, color=INK2)
ax.text(-1.75, -0.8, "월간 수익률 상관계수 · 2014.10~2026.11 · 테두리 = SCHD 줄", fontsize=15, color=INK2)
fig.savefig("out/_h.png", dpi=100, bbox_inches="tight", pad_inches=0.2); plt.close(fig)
Image.open("out/_h.png").convert("RGB").save("out/m-schd-correlation.webp", "WEBP", quality=88, method=6); os.remove("out/_h.png")
