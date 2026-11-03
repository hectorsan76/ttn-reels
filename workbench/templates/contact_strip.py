# Contact strip of slides: python3 contact_strip.py out.jpg scale img1 img2 ... (w47 review helper)
import sys
from PIL import Image
# usage: sheet.py out.jpg scale img1 img2 ...
out=sys.argv[1]; sc=float(sys.argv[2]); fs=sys.argv[3:]
W=int(1080*sc);H=int(1350*sc);g=8
s=Image.new('RGB',(len(fs)*(W+g)+g,H+2*g),(200,200,200))
for i,f in enumerate(fs): s.paste(Image.open(f).resize((W,H),Image.LANCZOS),(g+i*(W+g),g))
s.save(out,quality=88)
