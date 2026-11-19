"""ETF 글 썸네일(A형, 1200x630). 사용: make_thumb('SCHD','배당 ETF 완전분석','배당 ETF의 정석일까?',[('3.0%','배당률'),...],'point-chart','out.webp')"""
import os
from PIL import Image, ImageDraw, ImageFont
HERE = os.path.dirname(os.path.abspath(__file__))
FD = os.path.join(HERE, "..", "fonts", "suit"); CH = os.path.join(HERE, "..", "character")
W, H = 1200, 630; INK = (28, 40, 58); YEL = (255, 222, 110); WHITE = (255, 255, 255); SUB = (90, 100, 115)
F = lambda w, s: ImageFont.truetype(os.path.join(FD, f"SUIT-{w}.ttf"), s)

def _bg():
    bg = Image.new("RGB", (W, H)); d = ImageDraw.Draw(bg)
    for y in range(H):
        t = y / (H - 1); d.line([(0, y), (W, y)], fill=tuple(int(a + (b - a) * t) for a, b in zip((170, 218, 235), (199, 232, 244))))
    return bg

def _char(bg, pose, x):
    im = Image.open(os.path.join(CH, f"{pose}.png")).convert("RGB"); s = H / im.height
    im = im.resize((int(im.width * s), H), Image.LANCZOS)
    m = Image.new("L", im.size, 255); d = ImageDraw.Draw(m); fe = 60
    for i in range(fe):
        v = int(255 * i / fe); d.line([(i, 0), (i, H)], fill=v); d.line([(im.width - 1 - i, 0), (im.width - 1 - i, H)], fill=v)
    bg.paste(im, (x, 0), m)

def make_thumb(ticker, label, headline, chips, pose, out, tick_size=160):
    bg = _bg(); _char(bg, pose, 760); d = ImageDraw.Draw(bg)
    f = F("Bold", 26); b = d.textbbox((78, 58), label, font=f)
    d.rounded_rectangle([b[0] - 18, b[1] - 10, b[2] + 18, b[3] + 10], 40, fill=INK); d.text((78, 58), label, font=f, fill=WHITE)
    d.text((70, 96), ticker, font=F("ExtraBold", tick_size), fill=INK)
    f = F("Bold", 54); b = d.textbbox((78, 304), headline, font=f)
    d.rounded_rectangle([b[0] - 12, b[1] + (b[3] - b[1]) * 0.45, b[2] + 12, b[3] + 4], 8, fill=YEL); d.text((78, 304), headline, font=f, fill=INK)
    w, gap, h, y = 212, 14, 150, 430
    for i, (big, small) in enumerate(chips):
        x = 66 + i * (w + gap); d.rounded_rectangle([x, y, x + w, y + h], 22, fill=WHITE)
        d.text((x + w / 2, y + 40), small, font=F("SemiBold", 26), fill=SUB, anchor="mm")
        bf = F("ExtraBold", 54 if len(big) <= 6 else 44)
        d.text((x + w / 2, y + 100), big, font=bf, fill=INK, anchor="mm")
    bg.save(out, "WEBP", quality=88, method=6) if out.endswith(".webp") else bg.save(out)
    return out

if __name__ == "__main__":
    make_thumb("SCHD", "배당 ETF 완전분석", "배당 ETF의 정석일까?",
               [("3.0%", "배당률"), ("연 11%", "배당 성장"), ("19.8억", "30년 적립 중앙값")], "point-chart",
               os.path.join(HERE, "..", "..", "etf", "out", "schd-thumbnail.webp"))
