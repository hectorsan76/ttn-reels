import sys
sys.path.insert(0,'/root/ttn-reels/workbench/vt'); sys.path.insert(0,'/root/ttn-reels/workbench/vt/loc')
from PIL import ImageFont, ImageDraw, Image
from loc_data import ITEMS, LANGS
F900='/root/ttn-reels/workbench/vt/fonts/Montserrat-900.ttf'
dd=ImageDraw.Draw(Image.new('RGB',(1,1)))
def nlines(text):
    text=text.upper().rstrip('.'); size=92
    while True:
        f=ImageFont.truetype(F900,size); ws=text.split(); lines=['']
        for w in ws:
            t=(lines[-1]+' '+w).strip()
            if dd.textlength(t,font=f)<=880: lines[-1]=t
            else: lines.append(w)
        if len(lines)<=2 or size<=56: break
        size-=4
    return len(lines),size
for k,it in ITEMS.items():
    if it['kind']!='people': continue
    for l in ('pt','es','id'):
        co=LANGS[l]['callout']
        for i,t in enumerate(it[l]['vo']):
            tt=t[len(co):].strip() if t.lower().startswith(co.lower()) else t
            n,s=nlines(tt)
            if n>=3: print(k,l,i,n,s,len(tt),tt)
