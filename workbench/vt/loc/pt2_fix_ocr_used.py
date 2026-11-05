"""pt "Copy of" fix: e-mail OCR scan limited to the take seconds a pt2_fix item uses (copy of id2_ocr_used.py, pt2_ocr's pattern).
python3 pt2_fix_ocr_used.py <take> [fps] -> /home/claude/loc/ocr_pt_fix/<take>.json (same shape as pt2_ocr.py)"""
import sys, os, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import pt2_ocr, pt2_fix
take = sys.argv[1]; fps = float(sys.argv[2]) if len(sys.argv) > 2 else 2
rng = []
for k, it in pt2_fix.HOWTO.items():
    tk = pt2_fix.takes_of(it)
    if take not in dict(tk): continue
    off = dict(tk)[take]; segs = it.get("phone_segs") if k == "help08" else it["segs"]
    for a, b, s in segs:
        a, b = a - off, b - off
        if b > 0 and (len(tk) == 1 or a < pt2_fix.dur(pt2_fix.NT + take + "/take_p6.mp4")): rng.append([max(0, a - 0.5), b + 0.5])
rng.sort(); m = []
for a, b in rng:
    if m and a <= m[-1][1]: m[-1][1] = max(m[-1][1], b)
    else: m.append([a, b])
hits = []
for a, b in m: hits += pt2_ocr.scan(pt2_fix.NT + take + "/take_p6.mp4", fps, pt2_ocr.EMAIL, round(a, 2), round(b, 2), 2)
os.makedirs(pt2_fix.OCRD, exist_ok=True); json.dump(hits, open(f"{pt2_fix.OCRD}/{take.replace('/', '_')}.json", "w"))
print(take, m, len(hits), "hits", sorted({h[5] for h in hits})[:8])
