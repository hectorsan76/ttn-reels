# Measures headline (ink/coral) and teal rows of tip images, used to match tip.html to the 2026-11 tips: python3 tip_measure.py a.jpg b.jpg
from PIL import Image
import numpy as np, sys
def groups(r):
  if len(r)==0: return []
  g=[];s=r[0];p=r[0]
  for x in r[1:]:
    if x>p+3: g.append((int(s),int(p))); s=x
    p=x
  g.append((int(s),int(p))); return g
for f in sys.argv[1:]:
  a=np.array(Image.open(f).convert('RGB')).astype(int)
  dark=(a.sum(2)<450)&~((a[:,:,0]<120)&(a[:,:,1]>90))
  teal=(abs(a[:,:,0]-14)<35)&(abs(a[:,:,1]-122)<35)&(abs(a[:,:,2]-111)<35)
  out=[]
  for g in groups(np.where(dark[:,140:1000].sum(1)>3)[0]):
    c=np.where(dark[g[0]:g[1]+1].any(0))[0]; out.append((g,int(c.min()),int(c.max())))
  tg=[]
  for g in groups(np.where(teal[:,140:1000].sum(1)>3)[0]):
    c=np.where(teal[g[0]:g[1]+1].any(0))[0]; tg.append((g,int(c.min()),int(c.max())))
  print(f.split('/')[-2]); print('  dark',out); print('  teal',tg)
