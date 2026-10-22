"""Render a full carousel: python3 render_post.py post.json out_dir
post.json: {"cover": {...cover spec, kind carousel...}, "slides": [ {...slide spec...}, ... ]}
Writes slide1.jpg (cover) .. slideN.jpg at 1080x1350."""
import json, sys, os, urllib.parse
from playwright.sync_api import sync_playwright
P = json.load(open(sys.argv[1])); out = sys.argv[2]; os.makedirs(out, exist_ok=True)
here = os.path.dirname(os.path.abspath(__file__))
pages = [('cover.html', P['cover'])] + [('slide.html', s) for s in P['slides']]
with sync_playwright() as pw:
    b = pw.chromium.launch(); p = b.new_page(viewport={'width': 1080, 'height': 1350})
    for i, (html, spec) in enumerate(pages, 1):
        p.goto('file://' + os.path.join(here, html) + '?c=' + urllib.parse.quote(json.dumps(spec)))
        p.wait_for_selector('body[data-done]', state='attached'); p.wait_for_timeout(150)
        png = f'{out}/slide{i}.png'; p.screenshot(path=png, clip={'x': 0, 'y': 0, 'width': 1080, 'height': 1350})
        from PIL import Image; Image.open(png).convert('RGB').save(f'{out}/slide{i}.jpg', quality=92); os.remove(png)
    b.close()
print('rendered', len(pages), 'to', out)
