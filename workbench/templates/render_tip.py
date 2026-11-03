"""Render TTN One trainer tip images (1080x1350 JPG) with tip.html.
Usage: python3 render_tip.py tips.json out_dir
tips.json: [{"slug":"warm-up-sets","hd":"BLACK PART","em":"CORAL PART.","hand":"Teal handwritten<br>why line."}, ...]
Writes out_dir/<slug>/tip.jpg. Rebuilt 2026-11-03 to match the 2026-11 tips (film squat, one cue, rep range)."""
import json, sys, os, urllib.parse
from playwright.sync_api import sync_playwright
from PIL import Image
tips = json.load(open(sys.argv[1])); out = sys.argv[2]
here = os.path.dirname(os.path.abspath(__file__))
with sync_playwright() as pw:
    b = pw.chromium.launch(); p = b.new_page(viewport={'width': 1080, 'height': 1350})
    for t in tips:
        p.goto('file://' + os.path.join(here, 'tip.html') + '?c=' + urllib.parse.quote(json.dumps(t)))
        p.wait_for_selector('body[data-done]', state='attached'); p.wait_for_timeout(150)
        d = os.path.join(out, t['slug']); os.makedirs(d, exist_ok=True)
        png = d + '/tip.png'; p.screenshot(path=png, clip={'x': 0, 'y': 0, 'width': 1080, 'height': 1350})
        Image.open(png).convert('RGB').save(d + '/tip.jpg', quality=92); os.remove(png)
        print(t['slug'], 'font', p.evaluate('document.body.dataset.fs'), 'lines', p.evaluate('document.body.dataset.lines'), 'hand', p.evaluate('document.body.dataset.hand'))
    b.close()
