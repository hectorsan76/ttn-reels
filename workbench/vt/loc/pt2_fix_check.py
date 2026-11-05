"""pt "Copy of" fix checks (copy of id2_check.py): format (1080x1920, 30 fps, AAC) and an OCR pass at 2 fps over each rebuilt video,
full frame and (how-tos) the phone screen enlarged, for "Copy of", times between 22:00 and 06:00 (pt 24 hour "18:00"), English words
and e-mail addresses. python3 pt2_fix_check.py item [...] -> /home/claude/loc/out_pt_fix/<item>_check.json"""
import sys, os, re, json, subprocess, tempfile, shutil
from concurrent.futures import ThreadPoolExecutor
OUT = "/home/claude/loc/out_pt_fix"
EN = r"\b(Copy|of|Add|Edit|Settings|Send|Invite|Workout|Workouts|Client|Clients|Follow|Today|Home|Calendar|Done|Save|Cancel|Delete|Export|Email|History|Details|Habits|Reminder|Reminders|Search|Exercise|Exercises|Clone|Last|Dead|Sprints|Rowing|Run|Machine|Kettlebell|Light|Dark|Notebook|Profile|Messages|Template|Program|Now|week|minutes|Training|The|One|Store|Google|Play|Upper|Body|Basics|Full|Sets|Reps|Weight|Next|Back|Schedule|Date|Time)\b"
COPY = re.compile(r"Copy\s*of|Copy", re.I)
T24 = re.compile(r"(?<![\d,.:])([01]?\d|2[0-3])[:h]([0-5]\d)(?![\d,:])")
MAIL = re.compile(r"support\+\S*|\S*anasouza\S*|\S*beatrizcosta\S*|showcase\.\S*|\S*@thetrain\S*|\S+@\S+\.\S+", re.I)
def probe(p):
    j = json.loads(subprocess.run(["ffprobe", "-v", "error", "-show_streams", "-of", "json", p], capture_output=True, text=True).stdout)
    v = [s for s in j["streams"] if s["codec_type"] == "video"][0]; a = [s for s in j["streams"] if s["codec_type"] == "audio"]
    return v["width"], v["height"], v["r_frame_rate"], a[0]["codec_name"] if a else None
def night(h): h = int(h); return h >= 22 or h < 6
def scan(p, fps=2, full=True):
    td = tempfile.mkdtemp()
    vf = f"fps={fps},scale=2160:-2" if full else f"fps={fps},crop=600:1304:240:610,scale=1200:-2"
    subprocess.run(["ffmpeg", "-v", "error", "-i", p, "-vf", vf, f"{td}/f%05d.png"], check=True)
    def one(fn):
        t = (int(fn[1:6]) - 1) / fps
        txt = subprocess.run(["tesseract", f"{td}/{fn}", "-", "--psm", "11"], capture_output=True, text=True).stdout
        n = [m.group(0) for m in T24.finditer(txt) if night(m.group(1))]
        e = sorted(set(re.findall(EN, txt))) + ["COPY:" + m.group(0) for m in COPY.finditer(txt)] + ["MAIL:" + m.group(0) for m in MAIL.finditer(txt)]
        return t, n, e
    fs = sorted(os.listdir(td))
    with ThreadPoolExecutor(2) as ex: res = list(ex.map(one, fs))
    shutil.rmtree(td, ignore_errors=True); return res
if __name__ == "__main__":
    for item in sys.argv[1:]:
        p = f"{OUT}/{item}_pt_fix.mp4"; w, h, r, a = probe(p); rep = dict(item=item, fmt=[w, h, r, a])
        for mode in (["full", "phone"] if item.startswith("howto") else ["full"]):
            res = scan(p, full=mode == "full"); en = {}
            for t, n, e in res:
                for x in e: en.setdefault(x, []).append(t)
            rep[mode] = dict(night=[(t, n) for t, n, e in res if n], english={k: [v[0], v[-1], len(v)] for k, v in en.items()})
        json.dump(rep, open(f"{OUT}/{item}_check.json", "w"), ensure_ascii=False)
        print(json.dumps(rep, ensure_ascii=False))
