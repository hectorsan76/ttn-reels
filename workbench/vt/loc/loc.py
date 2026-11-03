"""Build the native language versions (pt, es, id) of the TTN One videos.
python3 loc.py cfg <item> <lang>     writes cfg/<item>_<lang>.json and the cover, picks a speaking rate so every line fits
python3 loc.py build <item> <lang>   cfg + build + checks (closing line, sheet)
Covers: the English cover's photo (people) or phone screen (how-to) is cropped from posts/*/cover.png and the cover is
re-rendered with render_cover.py and the translated words, so the picture stays identical."""
import json, os, sys, subprocess, re
V = "/root/ttn-reels/workbench/vt"; TPL = "/root/ttn-reels/workbench/templates"
sys.path.insert(0, V); sys.path.insert(0, V + "/loc")
from loc_data import ITEMS, LANGS
from PIL import Image
OUT = "/home/claude/loc/out"; os.makedirs(OUT, exist_ok=True)
MUSIC_FIX = {"Instrumental.mp3": "soundsurfer-hip-hop-beats-592991.mp3"}
PX = "/mnt/user-data/uploads/TTN Reels/_work/howto_p6/"
NOTEPOS = {"howto02": "left:20px;top:720px", "howto24": "left:10px;top:720px"}

def dur(p): return float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", p], capture_output=True, text=True).stdout)

def cover(item, k):
    it = ITEMS[item]; T = it[k]; L = LANGS[k]; en = Image.open(it["en_cover"]).convert("RGB")
    nav = en.getpixel((50, 50))[0] < 100; bg = "navy" if nav else "paper"
    a = f"_loc_{item}.png"; ap = f"{TPL}/assets/{a}"
    if it["kind"] == "people":
        ph = it["ph"]; en.crop((0, 1920 - ph, 1080, 1920)).save(ap)
        spec = {"bg": bg, "kind": "reel", "label": L["label"], "l1": T["cover"][0], "l2": T["cover"][1], "kicker": T["cover"][2], "photo": a, "ph": ph}
    else:
        c = en.crop((260, 773, 820, 1920)); full = Image.new("RGB", (560, 1218), c.getpixel((280, 1140))); full.paste(c, (0, 0)); full.save(ap)
        spec = {"bg": bg, "kind": "reel", "series": f"{L['series']} {it['n']}", "l1": T["cover"][0], "l2": T["cover"][1], "screen": a,
                "note": {"text": T["cover"][2], "pos": NOTEPOS.get(item, "left:40px;top:720px")}}
    sp = f"{V}/cfg/coverspec_{item}_{k}.json"; json.dump(spec, open(sp, "w"), ensure_ascii=False)
    out = f"{V}/cfg/cover_{item}_{k}.png"
    subprocess.run(["python3", f"{TPL}/render_cover.py", sp, out], check=True, capture_output=True, cwd=TPL)
    return out

def fit(C, kind):
    """speaking rate so no line runs past the footage (same timing rules as the builders)"""
    import reel2
    lang = C["lang"]; H = C.get("hook_secs", 1.6)
    if kind == "people":
        X = 0.22; shots = [dur(p) / s for p, s in C["shots"]]; starts = []; t = H
        for i, d in enumerate(shots): starts.append(t); t += d - (X if i < len(shots) - 1 else 0)
        M = t - H
    else:
        M = sum((b - a) / s for a, b, s in C["segs"])
    for rate in (1.0, 1.05, 1.1, 1.15, 1.2):
        end = 0; worst = -99; prev = None
        for item in C["vo"]:
            if kind == "people": si, off, text = item[:3]; tt = starts[si] + off; gap = 0.15
            else: tt, text = item; gap = 0.2
            p, d = reel2.tts(text, C["voice"], rate, lang)
            if prev is not None: tt = max(tt, prev + gap)
            prev = tt + d; worst = max(worst, prev - (H + M))
        if worst <= -0.1: return rate, worst, H + M
    return rate, worst, H + M

def make_cfg(item, k):
    it = ITEMS[item]; T = it[k]; L = LANGS[k]; C = json.load(open(it["src"]))
    for key in ("_note",): C.pop(key, None)
    name = f"{item}_{k}"; C["name"] = name; C["lang"] = L["lang"]; C["end_vo"] = L["end_vo"]
    C["end_card"] = f"{V}/endcard_{k}.png"; C["out"] = f"{OUT}/{name}.mp4"; C["cover"] = cover(item, k)
    assert len(C["vo"]) == len(T["vo"]), (item, k, len(C["vo"]), len(T["vo"]))
    for i, line in enumerate(T["vo"]):
        if it["kind"] == "people": C["vo"][i][2] = line
        else: C["vo"][i][1] = line
    m = C.get("music", ""); base = m.split("/")[-1]
    if base in MUSIC_FIX: C["music"] = m.replace(base, MUSIC_FIX[base])
    if it["kind"] == "people":
        C["callout"] = L["callout"]
    else:
        C["series"] = f"{L['series']} {it['n']}"; C["title"] = T["title"]
        assert len(C.get("notes", [])) == len(T["notes"]), (item, "notes")
        for i, n in enumerate(T["notes"]): C["notes"][i][2] = n
        src = C["src"].split("/")[-1].rsplit(".", 1)[0]; C["src"] = PX + src + ".mp4"; C["proxy"] = C["src"]
    rate, worst, fe = fit(C, it["kind"]); C["rate"] = rate
    p = f"{V}/cfg/{name}.json"; json.dump(C, open(p, "w"), ensure_ascii=False, indent=1)
    return p, rate, worst

def check(item, k):
    """closing line ends inside the file; contact sheet"""
    import reel2
    C = json.load(open(f"{V}/cfg/{item}_{k}.json")); T = dur(C["out"]); H = C.get("hook_secs", 1.6)
    if ITEMS[item]["kind"] == "people":
        shots = [dur(p) / s for p, s in C["shots"]]; M = sum(shots) - 0.22 * (len(shots) - 1)
    else: M = sum((b - a) / s for a, b, s in C["segs"])
    ep, ed = reel2.tts(C["end_vo"], C["voice"], C.get("rate", 1.0), C["lang"])
    margin = T - (H + M + 0.35 + ed)
    sheet = f"/home/claude/loc/sheets/{item}_{k}.jpg"; os.makedirs(os.path.dirname(sheet), exist_ok=True)
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", C["out"], "-vf", "fps=1,scale=160:-2,tile=12x3", "-frames:v", "1", sheet], check=True)
    return T, margin, sheet

if __name__ == "__main__":
    cmd, item, k = sys.argv[1:4]
    p, rate, worst = make_cfg(item, k); print("cfg", p, "rate", rate, "overrun", round(worst, 2))
    if cmd == "build":
        b = "people.py" if ITEMS[item]["kind"] == "people" else "reel2.py"
        r = subprocess.run(["python3", f"{V}/{b}", p], capture_output=True, text=True)
        print(r.stdout.strip()[-400:], r.stderr.strip()[-800:])
        T, margin, sheet = check(item, k); print(f"RESULT {item}_{k} {T:.1f}s closing margin {margin:.2f}s rate {rate} sheet {sheet}")
