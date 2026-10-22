"""Render a TTN One cover in the approved style.
Usage: python3 render_cover.py spec.json out.png
spec: {"bg":"paper"|"navy","kind":"carousel"|"reel","l1":"...","l2":"...","series":"HOW TO 14" (optional),
       "screen":"dash_dark.png","note":{"text":"tap","pos":"left:40px;top:640px","flip":false} (optional)}
Rule: dark screens on paper, notebook and light screens on navy."""
import json, sys, os, urllib.parse
from playwright.sync_api import sync_playwright
spec = json.load(open(sys.argv[1])); out = sys.argv[2]
here = os.path.dirname(os.path.abspath(__file__))
url = 'file://' + os.path.join(here, 'cover.html') + '?c=' + urllib.parse.quote(json.dumps(spec))
w, h = 1080, (1920 if spec['kind'] == 'reel' else 1350)
with sync_playwright() as pw:
    b = pw.chromium.launch(); p = b.new_page(viewport={'width': w, 'height': h})
    p.goto(url); p.wait_for_selector('body[data-done]', state='attached'); p.wait_for_timeout(200)
    fs = p.evaluate('document.body.dataset.fs')
    p.screenshot(path=out, clip={'x': 0, 'y': 0, 'width': w, 'height': h}); b.close()
print(out, 'headline px', fs)
