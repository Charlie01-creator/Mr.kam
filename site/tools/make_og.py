"""Regenerates assets/og.png (1200x630 social sharing image). Needs Pillow; not part of the site build.
Run from site/:  python3 tools/make_og.py"""
from PIL import Image,ImageDraw,ImageFont
import os
G="/usr/share/fonts/truetype/google-fonts/"
NAVY,GOLD,GL,IV=(20,33,61),(182,138,72),(217,184,119),(244,239,228)
W,H=1200,630
im=Image.new("RGB",(W,H),NAVY);d=ImageDraw.Draw(im)
for x in range(0,W+1,60):d.line([(x,0),(x,H)],fill=(32,47,80),width=1)
for y in range(0,H+1,60):d.line([(0,y),(W,y)],fill=(32,47,80),width=1)
pts=[(x,int(600-((x-640)/540.0)**2*430)) for x in range(640,1181,6)]
d.line([(x,max(40,min(H-40,y))) for x,y in pts],fill=GOLD,width=3)
def F(n,s,i=0):
    try:
        if n=="lora":return ImageFont.truetype(G+"Lora-Variable.ttf",s)
        if n=="lorai":return ImageFont.truetype(G+"Lora-Italic-Variable.ttf",s)
        return ImageFont.truetype(G+"ofl/sourcesans3/SourceSans3[wght].ttf",s)
    except Exception:return ImageFont.load_default()
f=F("lora",92)
try:f.set_variation_by_axes([600])
except Exception:pass
fi=F("lorai",92)
try:fi.set_variation_by_axes([500])
except Exception:pass
fs=F("sans",30)
try:fs.set_variation_by_axes([700])
except Exception:pass
d.rectangle([0,0,W,H],outline=GOLD,width=0)
d.text((80,92),"MATHEMATICS EDUCATOR · TEXTBOOK AUTHOR",font=fs,fill=GL)
d.line([(80,150),(180,150)],fill=GOLD,width=3)
d.text((80,190),"Mr. Kamulegeya",font=f,fill=IV)
d.text((80,296),"Mubarak Kiggundu",font=fi,fill=GL)
def S(sz,w):
    x=F("sans",sz)
    try:x.set_variation_by_axes([w])
    except Exception:pass
    return x
d.text((80,470),"Kamulegeya Mathematics",font=S(34,600),fill=IV)
d.text((80,516),"Publications · Tutoring · Schools",font=S(28,400),fill=(195,202,216))
d.text((1010,300),"∑",font=F("lora",260),fill=(46,62,96))
im.save(os.path.join(os.path.dirname(__file__),"..","assets","og.png"),optimize=True)
print("og.png written")
