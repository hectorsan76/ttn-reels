"""id: night time / e-mail / "Copy of" OCR over the H08 web take at full size (2880x1800), only the seconds help08 uses, 1 fps.
python3 id2_webcheck.py -> prints hits"""
import sys, os, re, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import id2_ocr, id2
web = id2.NT + "H08/web/take_cfr60.mp4"; segs = id2.HOWTO["help08"]["web_segs"]
pat = r"^(2[23]|0[0-5])[.:][0-5]\d|Sekarang|Copy|@|support"
hits = id2_ocr.scan(web, 1, pat, segs[0][0], segs[-1][1], 1, "H08_web_night")
print(len(hits)); [print(h) for h in hits]
