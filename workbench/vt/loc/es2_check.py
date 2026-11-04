"""es v2 checks (2026-11-05): format (1080x1920, 30 fps, AAC) and an OCR pass over every built video at 2 fps for
times between 22:00 and 06:00 (12 hour "h:mm a. m./p. m." and 24 hour) and for English words. python3 es2_check.py item [...]"""
import sys, os, re, json, subprocess, tempfile, shutil
from concurrent.futures import ThreadPoolExecutor
OUT = "/home/claude/loc/out_es_v2"
EN = r"\b(Copy|Add|Edit|Settings|Send|Invite|Workout|Workouts|Client|Clients|Follow|Today|Home|Calendar|Done|Save|Cancel|Delete|Export|Email|History|Details|Habits|Reminder|Reminders|Search|Exercise|Exercises|Clone|Last|Dead|Sprints|Kettlebell|Light|Dark|Notebook|Profile|Messages|Template|Program|Now|week|minutes)\b"
T12 = re.compile(r"\b(\d{1,2})[:.](\d{2})\s*([ap])\.?\s?m", re.I)
def probe(p):
    j = json.loads(subprocess.run(["ffprobe", "-v", "error", "-show_streams", "-of", "json", p], capture_output=True, text=True).stdout)
    v = [s for s in j["streams"] if s["codec_type"] == "video"][0]; a = [s for s in j["streams"] if s["codec_type"] == "audio"]
    return v["width"], v["height"], v["r_frame_rate"], a[0]["codec_name"] if a else None
def night(h, ap):
    h = int(h) % 12 + (12 if ap.lower() == "p" else 0)
    return h >= 22 or h < 6
def scan(p, fps=2, full=False):
    td = tempfile.mkdtemp()
    vf = f"fps={fps},scale=2160:-2" if full else f"fps={fps},crop=600:1304:240:610,scale=1200:-2"
    subprocess.run(["ffmpeg", "-v", "error", "-i", p, "-vf", vf, f"{td}/f%05d.png"], check=True)
    def one(fn):
        t = (int(fn[1:6]) - 1) / fps
        txt = subprocess.run(["tesseract", f"{td}/{fn}", "-", "--psm", "11"], capture_output=True, text=True).stdout
        n = [m.group(0) for m in T12.finditer(txt) if night(m.group(1), m.group(3))]
        e = sorted(set(re.findall(EN, txt)))
        return t, n, e
    fs = sorted(os.listdir(td))
    with ThreadPoolExecutor(2) as ex: res = list(ex.map(one, fs))
    shutil.rmtree(td, ignore_errors=True); return res
if __name__ == "__main__":
    for item in sys.argv[1:]:
        p = f"{OUT}/{item}_es_v2.mp4"; w, h, r, a = probe(p)
        res = scan(p, full=not item.startswith("howto") and item not in ("help01", "help03", "help05", "help06", "help07", "help09")); nights = [(t, n) for t, n, e in res if n]; en = {}
        for t, n, e in res:
            for x in e: en.setdefault(x, []).append(t)
        rep = dict(item=item, fmt=[w, h, r, a], night=nights, english={k: [v[0], v[-1], len(v)] for k, v in en.items()})
        json.dump(rep, open(f"{OUT}/{item}_check.json", "w"), ensure_ascii=False)
        print(json.dumps(rep, ensure_ascii=False))
