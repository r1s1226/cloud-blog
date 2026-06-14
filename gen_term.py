# -*- coding: utf-8 -*-
"""실제 명령 실행 출력을 터미널 스크린샷(PNG)으로 렌더링.
사용: python gen_term.py spec.json   (spec = [{title,file,lines:[{t,s}]}...])
  t: cmd(명령) | out(출력) | ok(성공/녹색) | warn(노랑) | cmt(주석/회색)
"""
import json, sys, os
from PIL import Image, ImageDraw, ImageFont

FONT  = "C:/Windows/Fonts/consola.ttf"
FONTB = "C:/Windows/Fonts/malgun.ttf"   # 제목용(한글 지원)
OUTDIR = r"C:\Users\11093\Desktop\cloud-blog\assets\img"

BG=(13,17,23); BAR=(28,33,40); TITLE=(160,170,182)
CMD=(233,239,245); OUT=(150,161,173); PROMPT=(63,185,80)
CMT=(110,118,129); OKC=(63,185,80); WARNC=(214,160,46)
DOTS=[(255,95,86),(255,189,46),(39,201,63)]

FS=26; LH=37; PAD=30; BARH=54; WIDTH=1180

def wrap(d, items, f, maxw):
    out=[]
    cw=d.textlength("M", font=f) or 13
    maxchars=max(20, int(maxw/cw))
    for it in items:
        t=it["t"]; s=it["s"].replace("\t","    ")
        prefix="$ " if t=="cmd" else ("# " if t=="cmt" else "")
        full=prefix+s
        if len(full)<=maxchars:
            out.append((t,full)); continue
        first=True; cur=full
        while cur:
            chunk=cur[:maxchars]; cur=cur[maxchars:]
            out.append((t, chunk if first else "    "+chunk)); first=False
    return out

def render(spec, path):
    f=ImageFont.truetype(FONT, FS); fb=ImageFont.truetype(FONTB, 22)
    tmp=Image.new("RGB",(10,10)); d0=ImageDraw.Draw(tmp)
    lines=wrap(d0, spec["lines"], f, WIDTH-2*PAD)
    h=BARH+PAD*2+LH*len(lines)
    img=Image.new("RGB",(WIDTH,h),BG); d=ImageDraw.Draw(img)
    d.rectangle([0,0,WIDTH,BARH],fill=BAR)
    cx=24
    for c in DOTS:
        d.ellipse([cx,BARH//2-7,cx+14,BARH//2+7],fill=c); cx+=26
    title=spec.get("title","")
    tw=d.textlength(title,font=fb)
    d.text(((WIDTH-tw)/2, BARH//2-13), title, font=fb, fill=TITLE)
    y=BARH+PAD
    for t,s in lines:
        if t=="cmd" and s.startswith("$ "):
            d.text((PAD,y),"$ ",font=f,fill=PROMPT)
            d.text((PAD+d.textlength("$ ",font=f),y), s[2:], font=f, fill=CMD)
        else:
            col={"cmd":CMD,"cmt":CMT,"ok":OKC,"warn":WARNC}.get(t,OUT)
            d.text((PAD,y), s, font=f, fill=col)
        y+=LH
    os.makedirs(OUTDIR, exist_ok=True)
    img.save(path)

def txt_to_lines(path):
    """터미널 로그(.log) → lines. '$ '로 시작=명령, '# '=주석, 그 외=출력."""
    items=[]
    with open(path, encoding="utf-8", errors="replace") as fh:
        for raw in fh.read().splitlines():
            s=raw.rstrip("\r")
            if s.startswith("$ "):
                items.append({"t":"cmd","s":s[2:]})
            elif s.startswith("# "):
                items.append({"t":"cmt","s":s[2:]})
            else:
                items.append({"t":"out","s":s})
    return items

if __name__=="__main__":
    if sys.argv[1]=="--txt":
        _, _, logpath, outfile, title = sys.argv[:5]
        render({"title":title, "lines":txt_to_lines(logpath)}, os.path.join(OUTDIR, outfile))
        print("wrote", outfile)
    else:
        spec=json.load(open(sys.argv[1],encoding="utf-8"))
        panels=spec if isinstance(spec,list) else [spec]
        for p in panels:
            render(p, os.path.join(OUTDIR, p["file"]))
            print("wrote", p["file"])
