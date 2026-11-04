"""Find e-mail addresses (or another pattern) on screen in a take. Hits are in the source video's own pixels.
python3 pt2_ocr.py <take> [fps]  -> /home/claude/loc/ocr/<take>.json [[t, x, y, w, h, word], ...] (take_p6.mp4)
scan(src, fps, pattern, t0, t1, up, name) for other sources (the web take's full-size file) or patterns."""
import sys, os, json, subprocess, tempfile, re, shutil
from concurrent.futures import ThreadPoolExecutor
NT = "/mnt/user-data/uploads/TTN Reels/04 Working files/native_takes/pt/"
OCR = "/home/claude/loc/ocr"
EMAIL = r"support|@thetrain|trainingnotebook\.c|anasouza|showcase|beatrizcosta|\+[a-z]+@"

def scan(src, fps, pattern, t0=None, t1=None, up=2, name=None):
    out_p = f"{OCR}/{name}.json" if name else None
    if out_p and os.path.exists(out_p): return json.load(open(out_p))
    td = tempfile.mkdtemp(); pat = re.compile(pattern, re.I)
    a = (["-ss", str(t0)] if t0 is not None else []) + ["-i", src] + (["-t", str(t1 - t0)] if t1 is not None else [])
    subprocess.run(["ffmpeg", "-v", "error", *a, "-vf", f"fps={fps},scale=iw*{up}:ih*{up}:flags=lanczos", f"{td}/f%05d.png"], check=True)
    base = t0 or 0
    def one(fn):
        i = int(fn[1:6]); t = base + (i - 1) / fps
        txt = subprocess.run(["tesseract", f"{td}/{fn}", "-", "--psm", "11", "tsv"], capture_output=True, text=True).stdout
        hits = []
        for line in txt.splitlines()[1:]:
            c = line.split("\t")
            if len(c) < 12 or not c[11].strip(): continue
            if pat.search(c[11]): hits.append([round(t, 2), int(c[6]) / up, int(c[7]) / up, int(c[8]) / up, int(c[9]) / up, c[11]])
        return hits
    fs = sorted(f for f in os.listdir(td) if f.endswith(".png"))
    with ThreadPoolExecutor(4) as ex: res = [h for r in ex.map(one, fs) for h in r]
    shutil.rmtree(td, ignore_errors=True)
    if out_p: os.makedirs(OCR, exist_ok=True); json.dump(res, open(out_p, "w"))
    return res

def scan_image(path, pattern=EMAIL, up=1):
    txt = subprocess.run(["tesseract", path, "-", "--psm", "11", "tsv"], capture_output=True, text=True).stdout
    pat = re.compile(pattern, re.I); hits = []
    for line in txt.splitlines()[1:]:
        c = line.split("\t")
        if len(c) >= 12 and c[11].strip() and pat.search(c[11]): hits.append([int(c[6]), int(c[7]), int(c[8]), int(c[9]), c[11]])
    return hits

if __name__ == "__main__":
    take = sys.argv[1]; fps = float(sys.argv[2]) if len(sys.argv) > 2 else 3
    res = scan(NT + take + "/take_p6.mp4", fps, EMAIL)
    os.makedirs(OCR, exist_ok=True); json.dump(res, open(f"{OCR}/{take.replace('/', '_')}.json", "w"))
    print(take, len(res), "hits", sorted({h[5] for h in res})[:12])
