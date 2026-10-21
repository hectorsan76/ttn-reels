import sys, subprocess, glob, os
from PIL import Image, ImageDraw
src, name, step = sys.argv[1], sys.argv[2], float(sys.argv[3]) if len(sys.argv) > 3 else 1
d = f"fr/{name}"; os.makedirs(d, exist_ok=True)
for f in glob.glob(f"{d}/*.jpg"): os.remove(f)
subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", src, "-vf", f"fps=1/{step},scale=150:-1", f"{d}/f_%03d.jpg"], check=True)
fs = sorted(glob.glob(f"{d}/f_*.jpg")); ims = [Image.open(f) for f in fs]; w, h = ims[0].size; cols = 12; rows = (len(ims) + cols - 1) // cols
g = Image.new("RGB", (w * cols, (h + 16) * rows), "white"); dr = ImageDraw.Draw(g)
for i, im in enumerate(ims):
    x = (i % cols) * w; y = (i // cols) * (h + 16); g.paste(im, (x, y + 16)); dr.text((x + 4, y + 2), f"{i*step:g}s", fill="red")
g.save(f"{d}/sheet.jpg", quality=80); print(len(ims), "frames", g.size)
