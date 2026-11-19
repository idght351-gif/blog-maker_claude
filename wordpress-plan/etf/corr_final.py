import json, numpy as np, matplotlib, os
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import font_manager as fm
from matplotlib.colors import LinearSegmentedColormap
from matplotlib.patches import FancyBboxPatch
from PIL import Image, ImageDraw, ImageFont
FD = "../brand/fonts/suit"
for f in os.listdir(FD):
    if f.endswith(".ttf"): fm.fontManager.addfont(f"{FD}/{f}")
plt.rcParams.update({"font.family": "SUIT", "figure.facecolor": "white"})
S = json.load(open("data/stats.json")); C = np.array(S["corr"]); L = ["SCHD", "S&P500", "장기채", "금", "비트코인"]; n = 5
INK = "#191f28"; INK2 = "#8b95a1"; RED = "#f04452"; BLUE = "#3182f6"; MID = "#d1d6db"
grad = LinearSegmentedColormap.from_list("g", [RED, "#f7f7f7", BLUE])
def lvl(v): return RED if v < 0.3 else (MID if v < 0.6 else BLUE)
def draw(mode, fn):
    fig, ax = plt.subplots(figsize=(9, 10.2)); fig.subplots_adjust(0.02, 0.02, 0.98, 0.98)
    for i in range(n):
        for j in range(n):
            y = n - 1 - i
            if mode == "tri" and j > i: continue
            if i == j:
                ax.add_patch(FancyBboxPatch((j + .04, y + .04), .88, .88, boxstyle="round,pad=0,rounding_size=0.1", fc="#f2f4f6", ec="none"))
                ax.text(j + .48, y + .48, "1", ha="center", va="center", fontsize=20, color=INK2); continue
            v = C[i, j]
            if mode == "grad": col, tc = grad(min(1, v)), ("white" if v > .7 or v < .15 else INK)
            elif mode == "focus":
                on = (i == 0 or j == 0); col = lvl(v) if on else "#f2f4f6"; tc = ("white" if lvl(v) != MID else INK) if on else INK2
            else: col = lvl(v); tc = "white" if col != MID else INK
            ax.add_patch(FancyBboxPatch((j + .04, y + .04), .88, .88, boxstyle="round,pad=0,rounding_size=0.1", fc=col, ec="none"))
            big = (i == 0 or j == 0)
            ax.text(j + .48, y + .48, f"{v:.2f}", ha="center", va="center", fontsize=27 if big else 22, fontweight="bold" if big else "normal", color=tc)
    for k in range(n):
        c = BLUE if k == 0 else INK; w = "bold" if k == 0 else "normal"
        ax.text(-0.1, n - 1 - k + .48, L[k], ha="right", va="center", fontsize=22, color=c, fontweight=w)
        ax.text(k + .48, n + 0.08, L[k], ha="center", va="bottom", fontsize=20, color=c, fontweight=w)
    # 아래 범례
    yb = -0.75
    if mode == "grad":
        for k in range(60): ax.add_patch(plt.Rectangle((0.2 + k * 0.075, yb), 0.075, 0.28, color=grad(k / 59), lw=0))
        ax.text(0.2, yb - 0.12, "0  따로 움직임", fontsize=18, color=INK2, va="top"); ax.text(4.7, yb - 0.12, "같이 움직임  1", fontsize=18, color=INK2, va="top", ha="right")
    else:
        for k, (c, t) in enumerate([(RED, "0~0.3 따로"), (MID, "0.3~0.6 약하게"), (BLUE, "0.6~1 같이")]):
            x = -0.2 + k * 1.75
            ax.add_patch(FancyBboxPatch((x, yb), 0.32, 0.28, boxstyle="round,pad=0,rounding_size=0.06", fc=c, ec="none"))
            ax.text(x + 0.42, yb + 0.14, t, fontsize=18, color=INK, va="center")
    ax.set_xlim(-1.75, n); ax.set_ylim(-1.15, n + 0.6); ax.set_aspect("equal"); ax.axis("off")
    fig.savefig(fn, dpi=100, bbox_inches="tight", pad_inches=0.15); plt.close(fig)

draw("focus", "out/_f.png")
im = Image.open("out/_f.png").convert("RGB"); W, H = im.size
head = 120; canvas = Image.new("RGB", (W, H + head), "white"); canvas.paste(im, (0, head))
d = ImageDraw.Draw(canvas)
d.text((24, 14), "S&P500과는 함께, 채권·금과는 따로", font=ImageFont.truetype(f"{FD}/SUIT-ExtraBold.ttf", 34), fill=INK)
d.text((24, 64), "SCHD와 함께 움직이는 정도 (상관계수)", font=ImageFont.truetype(f"{FD}/SUIT-Regular.ttf", 22), fill=INK2)
foot = Image.new("RGB", (W, H + head + 40), "white"); foot.paste(canvas, (0, 0))
ImageDraw.Draw(foot).text((24, H + head + 6), "월간 수익률 · 2014.10~2026.11 · 회색 = 다른 자산끼리(참고)", font=ImageFont.truetype(f"{FD}/SUIT-Regular.ttf", 17), fill=INK2)
foot.save("out/m-schd-correlation.webp", "WEBP", quality=88, method=6); os.remove("out/_f.png")
print(foot.size)
