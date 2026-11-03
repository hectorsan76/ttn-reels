"""Week review sheets (w47 helper): one contact sheet per day (tip + 5 carousel slides, buffered zone in blue,
IG grid crop in pink) and one grid check (newest first, middle 3:4 crop, grey tiles for videos).
Usage: python3 review_week.py build_dir out_dir   (build_dir holds tips/<slug>/tip.jpg and <carousel>/slideN.jpg)
Edit DAYS for a new week."""
import sys
from PIL import Image, ImageDraw, ImageFont
B, O = sys.argv[1], sys.argv[2]
F = '/root/ttn-reels/workbench/vt/fonts/Montserrat-800.ttf'
DAYS = [('16','Mon','warm-up-sets','n15_sameworkout','White'),('17','Tue','one-habit','n16_ownexercise','Notebook'),('18','Wed','same-day-replies','n17_clientsaday','Photo'),('19','Thu','four-week-blocks','n18_leticia','Quote'),('20','Fri','call-out-pb','n19_unpaidhours','Bold'),('21','Sat','pair-exercises','n20_first30','Bold'),('22','Sun','progress-photos','n21_everydevice','Black')]
W, H, g = 432, 540, 14
for d, dn, tip, car, tpl in DAYS:
    ims = [f'{B}/tips/{tip}/tip.jpg'] + [f'{B}/{car}/slide{i}.jpg' for i in range(1, 6)]
    s = Image.new('RGB', (g + 6 * (W + g), H + 2 * g + 70), (232, 232, 232)); dr = ImageDraw.Draw(s)
    dr.text((g, 18), f'{dn} {d} Nov 2026   1 AM tip: {tip}   |   9 PM carousel ({tpl}): {car}', font=ImageFont.truetype(F, 26), fill=(20, 20, 20))
    for i, f in enumerate(ims):
        x, y, k = g + i * (W + g), 70, W / 1080
        s.paste(Image.open(f).resize((W, H), Image.LANCZOS), (x, y))
        dr.rectangle([x + 150 * k, y + 150 * k, x + 930 * k, y + 1200 * k], outline=(0, 170, 255), width=1)
        dr.rectangle([x + 34 * k, y, x + 1046 * k, y + H - 1], outline=(255, 0, 180), width=1)
    s.save(f'{O}/day_{d}_{dn.lower()}_sheet.jpg', quality=88)
tiles = []
for d, dn, tip, car, tpl in DAYS:
    tiles += [('img', f'{B}/tips/{tip}/tip.jpg', f'{dn} tip'), ('ph', None, f'{dn} people video'), ('img', f'{B}/{car}/slide1.jpg', f'{dn} carousel'), ('ph', None, f'{dn} how-to')]
tiles = tiles[::-1]; TW, TH = 300, 400; rows = (len(tiles) + 2) // 3
G = Image.new('RGB', (3 * TW + 16, rows * TH + (rows + 1) * 4 + 60), (255, 255, 255)); dr = ImageDraw.Draw(G)
dr.text((8, 16), 'Grid check (newest first; grey = videos built elsewhere). Tiles show the middle 3:4 crop.', font=ImageFont.truetype(F, 15), fill=(0, 0, 0))
for i, (kind, f, lab) in enumerate(tiles):
    x, y = 4 + (i % 3) * (TW + 4), 64 + (i // 3) * (TH + 4)
    if kind == 'img': G.paste(Image.open(f).crop((34, 0, 1046, 1350)).resize((TW, TH), Image.LANCZOS), (x, y))
    else: dr.rectangle([x, y, x + TW, y + TH], fill=(205, 205, 205)); dr.text((x + 12, y + TH // 2 - 10), lab, font=ImageFont.truetype(F, 18), fill=(80, 80, 80))
G.save(f'{O}/grid_check_w47.jpg', quality=88)
