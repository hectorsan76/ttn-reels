"""id: e-mail OCR scan limited to the take seconds any id v2 item uses (faster than a full-take scan on this 2 core box).
python3 id2_ocr_used.py <take> [fps] -> /home/claude/loc/ocr_id/<take>.json (same shape as id2_ocr.py)"""
import sys, os, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import id2_ocr, id2
take = sys.argv[1]; fps = float(sys.argv[2]) if len(sys.argv) > 2 else 2
rng = []
for k, it in id2.HOWTO.items():
    tk = id2.takes_of(it)
    if take not in dict(tk): continue
    off = dict(tk)[take]; segs = it.get("phone_segs") if k == "help08" else it["segs"]
    for a, b, s in segs:
        a, b = a - off, b - off
        if b > 0 and (len(tk) == 1 or a < id2.dur(id2.NT + take + "/take_p6.mp4")): rng.append([max(0, a - 0.5), b + 0.5])
rng.sort(); m = []
for a, b in rng:
    if m and a <= m[-1][1]: m[-1][1] = max(m[-1][1], b)
    else: m.append([a, b])
hits = []
for a, b in m: hits += id2_ocr.scan(id2.NT + take + "/take_p6.mp4", fps, id2_ocr.EMAIL, round(a, 2), round(b, 2), 2)
os.makedirs(id2_ocr.OCR, exist_ok=True); json.dump(hits, open(f"{id2_ocr.OCR}/{take.replace('/', '_')}.json", "w"))
print(take, m, len(hits), "hits", sorted({h[5] for h in hits})[:8])
