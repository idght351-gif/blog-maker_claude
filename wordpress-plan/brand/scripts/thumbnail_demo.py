from PIL import Image, ImageDraw, ImageFont, ImageFilter
U="/root/.claude/uploads/de66fc0b-3a6e-5802-9d8c-596b6428ddeb/"
W,H=1200,630; INK=(28,40,58); YEL=(255,222,110); WHITE=(255,255,255); PINK=(242,140,160)
F=lambda w,s: ImageFont.truetype(f"fonts/Pretendard-{w}.otf",s)
def base():
    bg=Image.new("RGB",(W,H)); d=ImageDraw.Draw(bg)
    for y in range(H):
        t=y/(H-1); d.line([(0,y),(W,y)],fill=tuple(int(a+(b-a)*t) for a,b in zip((170,218,235),(199,232,244))))
    return bg
def char(bg,f,x):
    im=Image.open(U+f).convert("RGB"); s=H/im.height; im=im.resize((int(im.width*s),H),Image.LANCZOS)
    m=Image.new("L",im.size,255); d=ImageDraw.Draw(m); fe=60
    for i in range(fe):
        v=int(255*i/fe); d.line([(i,0),(i,H)],fill=v); d.line([(im.width-1-i,0),(im.width-1-i,H)],fill=v)
    bg.paste(im,(x,0),m)
def hl(d,xy,text,font,pad=(14,4)):
    x,y=xy; b=d.textbbox((x,y),text,font=font)
    d.rounded_rectangle([b[0]-pad[0],b[1]+(b[3]-b[1])*0.45,b[2]+pad[0],b[3]+pad[1]],8,fill=YEL)
    d.text((x,y),text,font=font,fill=INK)
def pill(d,xy,text,font,fill=INK,fg=WHITE):
    x,y=xy; b=d.textbbox((x,y),text,font=font); d.rounded_rectangle([b[0]-18,b[1]-10,b[2]+18,b[3]+10],40,fill=fill); d.text((x,y),text,font=font,fill=fg)
def chip(d,x,y,big,small):
    w=max(d.textlength(big,font=F("Bold",34)),d.textlength(small,font=F("SemiBold",20)))+40
    d.rounded_rectangle([x,y,x+w,y+96],18,fill=WHITE); d.text((x+20,y+12),small,font=F("SemiBold",20),fill=(90,100,115)); d.text((x+20,y+42),big,font=F("Bold",34),fill=INK); return x+w+14
def tag(d): d.text((W-150,H-34),"디자인 시안",font=F("Regular",16),fill=(90,110,130))

# A 분석형
bg=base(); char(bg,"2375b749-image.png",760); d=ImageDraw.Draw(bg)
pill(d,(78,70),"ETF 완전분석",F("Bold",26))
d.text((70,120),"SCHD",font=F("Bold",170),fill=INK)
hl(d,(78,330),"배당 ETF의 정석일까?",F("Bold",58))
x=72
for big,small in [("0.06%","총보수"),("분기","배당 주기"),("30년","시뮬레이션")]: x=chip(d,x,450,big,small)
tag(d); bg.save("thumb_A.png")

# B 숫자형
bg=base(); char(bg,"2a2ca392-image.png",780); d=ImageDraw.Draw(bg)
pill(d,(78,70),"SCHD 30년 시뮬레이션",F("Bold",26))
d.text((70,125),"1,000만 원 넣고",font=F("Bold",72),fill=INK)
d.text((70,215),"30년 두면",font=F("Bold",72),fill=INK)
d.rounded_rectangle([62,320,700,500],28,fill=WHITE)
d.text((92,335),"얼마 될까?",font=F("Bold",118),fill=(214,74,98))
d.text((78,530),"1,000번 돌려 본 최고·최악·중앙값",font=F("SemiBold",32),fill=INK)
tag(d); bg.save("thumb_B.png")

# C 비교형
bg=base(); char(bg,"b2186317-image.png",790); d=ImageDraw.Draw(bg)
pill(d,(78,70),"배당 ETF 비교",F("Bold",26))
d.text((70,125),"SCHD",font=F("Bold",130),fill=INK)
cx,cy=545,205; d.ellipse([cx-58,cy-58,cx+58,cy+58],fill=(214,74,98)); d.text((cx,cy),"VS",font=F("Bold",50),fill=WHITE,anchor="mm")
d.text((70,280),"VYM",font=F("Bold",130),fill=INK)
hl(d,(78,470),"뭐 살지 한 번에 정리",F("Bold",54))
tag(d); bg.save("thumb_C.png")

# 3장 묶어서 한 장으로 (폰에서 보기 쉽게) + 작은 크기 미리보기
sheet=Image.new("RGB",(W,H*3+40),(245,245,245))
for i,n in enumerate("ABC"): sheet.paste(Image.open(f"thumb_{n}.png"),(0,i*(H+20)))
sheet.save("thumbs_sheet.png")
