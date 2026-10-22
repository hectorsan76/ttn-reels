"""TTN One reel builder, approved style (VIDEO_AND_GRID_STYLE_LOCK.md, 2026-10-21).
python3 reel2.py config.json  ->  1080x1920 mp4
Timeline: cover hook (hook_secs) -> phone rises over paper or navy with series bar, upper third captions,
Kalam notes, voice (Google Chirp 3 HD), music, sfx -> navy end card with voice line.
config keys: name, src, segs [[a,b,speed]], bg (paper|navy), cover (png 1080x1920), hook_secs, series, title,
voice, vo [[t,text]] (output seconds), notes [[t0,t1,text,x,y,side]], sfx [[t,name]], music, music_vol, end_secs, out"""
import json, os, re, subprocess, sys, base64, hashlib, urllib.request
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import soundfile as sf
V = os.path.dirname(os.path.abspath(__file__))
F900, F800, FK, FS = [f"{V}/fonts/{n}" for n in ("Montserrat-900.ttf", "Montserrat-800.ttf", "Kalam-700.ttf", "SpaceMono-700.ttf")]
NAVY, PAPER, INK, TEAL, CREAM, ORANGE, YELLOW, CORAL = (11, 15, 25), (246, 241, 228), (26, 26, 26), (14, 122, 111), (248, 243, 232), (238, 120, 104), (245, 200, 76), (185, 77, 63)
KEY = open("/mnt/user-data/uploads/TTN Reels/04 Working files/video_tools/google_tts_key.txt").read().strip()
PW, PADX = 640, 20; SW = PW - 2 * PADX; PX = (1080 - PW) // 2; PY = 610

def run(*a): subprocess.run(list(a), check=True)

_L = {}
def lufs(path, secs=None):
    k = (path, secs)
    if k not in _L:
        a = ["ffmpeg", "-hide_banner", "-nostats", "-i", path] + (["-t", str(secs)] if secs else []) + ["-af", "ebur128", "-f", "null", "-"]
        out = subprocess.run(a, capture_output=True, text=True).stderr
        _L[k] = float(re.findall(r"I:\s+(-?[\d.]+) LUFS", out)[-1])
    return _L[k]

def tts(text, voice, rate=1.0):
    os.makedirs(f"{V}/tts", exist_ok=True)
    h = hashlib.md5(f"{voice}|{rate}|{text}".encode()).hexdigest()[:12]; p = f"{V}/tts/{h}.wav"
    if not os.path.exists(p):
        body = json.dumps({"input": {"text": text}, "voice": {"languageCode": "en-US", "name": f"en-US-Chirp3-HD-{voice}"},
                           "audioConfig": {"audioEncoding": "LINEAR16", "sampleRateHertz": 24000, "speakingRate": rate}}).encode()
        req = urllib.request.Request(f"https://texttospeech.googleapis.com/v1/text:synthesize?key={KEY}", body, {"Content-Type": "application/json"})
        open(p, "wb").write(base64.b64decode(json.load(urllib.request.urlopen(req))["audioContent"]))
        run("ffmpeg", "-v", "error", "-y", "-i", p, "-af", "silenceremove=start_periods=1:start_threshold=-45dB,areverse,silenceremove=start_periods=1:start_threshold=-45dB,areverse", "-ar", "44100", "-ac", "1", p + ".t.wav")
        os.replace(p + ".t.wav", p)
    return p, sf.info(p).duration

def bg_png(path, kind):
    if kind == "navy": Image.new("RGB", (1080, 1920), NAVY).save(path); return
    im = Image.new("RGB", (1080, 1920), PAPER); d = ImageDraw.Draw(im)
    for y in range(66, 1920, 69): d.rectangle((0, y, 1080, y + 2), fill=(196, 208, 220))
    d.rectangle((96, 0, 100, 1920), fill=(225, 158, 150)); im.save(path)

def phone_pngs(wd):
    bez = Image.new("RGBA", (PW + 60, 1500), (0, 0, 0, 0)); sh = Image.new("RGBA", bez.size, (0, 0, 0, 0))
    ImageDraw.Draw(sh).rounded_rectangle((30, 40, 30 + PW, 1500), 70, fill=(0, 0, 0, 120)); sh = sh.filter(ImageFilter.GaussianBlur(22))
    bez.alpha_composite(sh); ImageDraw.Draw(bez).rounded_rectangle((30, 20, 30 + PW, 1500), 70, fill=(10, 10, 11, 255), outline=(58, 63, 74, 255), width=5)
    bez.save(f"{wd}/bezel.png")
    sh_h = round(SW * 2622 / 1206); m = Image.new("L", (SW, sh_h), 0); ImageDraw.Draw(m).rounded_rectangle((0, 0, SW - 1, sh_h - 1), 54, fill=255); m.save(f"{wd}/mask.png")
    return sh_h

def bar_png(path, series, title):
    f = ImageFont.truetype(FS, 40); d = ImageDraw.Draw(Image.new("RGB", (1, 1)))
    w1 = d.textlength(series, font=f) + 44; w2 = d.textlength(title, font=f) + 44; im = Image.new("RGBA", (int(w1 + w2), 76), (0, 0, 0, 0)); dr = ImageDraw.Draw(im)
    dr.rectangle((0, 0, w1, 76), fill=TEAL); dr.text((22, 38), series, font=f, fill=CREAM, anchor="lm")
    dr.rectangle((w1, 0, w1 + w2, 76), fill=CREAM); dr.text((w1 + 22, 38), title, font=f, fill=INK, anchor="lm"); im.save(path); return im.width

def cap_png(path, text, kind):
    col = (255, 255, 255) if kind == "navy" else INK; size = 96; text = text.upper()
    while True:
        f = ImageFont.truetype(F900, size); w = ImageDraw.Draw(Image.new("RGB", (1, 1))).textlength(text, font=f)
        if w <= 900 or size <= 50: break
        size -= 4
    im = Image.new("RGBA", (1080, 150), (0, 0, 0, 0)); ImageDraw.Draw(im).text((540, 75), text, font=f, fill=col, anchor="mm"); im.save(path)

def note_png(path, text, kind, side):
    col = YELLOW if kind == "navy" else TEAL; f = ImageFont.truetype(FK, 86)
    im = Image.new("RGBA", (420, 300), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    lines = text.split("|"); y = 10
    for l in lines: d.text((10 if side == "left" else 410, y), l, font=f, fill=col, anchor="la" if side == "left" else "ra"); y += 86
    # hand drawn arrow
    ax = [(20, y + 20), (90, y + 26), (160, y + 60), (215, y + 110)]
    if side != "left": ax = [(420 - x, yy) for x, yy in ax]
    d.line(ax, fill=col, width=9, joint="curve")
    hx, hy = ax[-1]; s = -1 if side == "left" else 1
    d.line([(hx + s * 40, hy - 4), (hx, hy), (hx + s * 8, hy - 40)], fill=col, width=9, joint="curve")
    im = im.rotate(6 if side == "left" else -6, resample=Image.BICUBIC, expand=True); im.save(path)

SMALL = {"a","an","the","to","of","and","in","on","it","your","is","for","at","with","that's","this","where"}
def chunks(text, maxc=16):
    out = []
    for sent in re.findall(r"[^.?!,]+[.?!,]?", text):
        ws = sent.split(); cur = []
        for i, w in enumerate(ws):
            t = " ".join(cur + [w])
            if len(t) > maxc and cur:
                carry = []
                while len(cur) > 1 and cur[-1].lower() in SMALL: carry.insert(0, cur.pop())
                out.append(" ".join(cur)); cur = carry + [w]
            else: cur.append(w)
        if cur:
            last = " ".join(cur)
            if out and len(cur) == 1 and len(out[-1]) + len(last) <= maxc + 6 and not re.search(r"[.?!]$", out[-1]): out[-1] += " " + last
            else: out.append(last)
    return [c.rstrip(",.") for c in out if c.strip()]

def build(cfg):
    C = json.load(open(cfg)); wd = f"{V}/work/{C['name']}"; os.makedirs(wd, exist_ok=True)
    kind = C["bg"]; H = C.get("hook_secs", 1.6); segs = C["segs"]; M = sum((b - a) / s for a, b, s in segs)
    E = C.get("end_secs", 3.6); T = H + M + E
    # assets
    bg_png(f"{wd}/bg.png", kind); sh_h = phone_pngs(wd)
    bw = bar_png(f"{wd}/bar.png", C["series"], C["title"]) if C.get("series") else 0
    proxy = f"{wd}/proxy.mp4"
    if not os.path.exists(proxy):
        run("ffmpeg", "-v", "error", "-y", "-i", C["src"], "-vf", f"fps=30,scale={SW}:{sh_h}:flags=lanczos", "-an", "-c:v", "libx264", "-crf", "14", "-preset", "fast", proxy)
    # voice
    vo = []
    for t, text in C["vo"]:
        p, d = tts(text, C["voice"], C.get("rate", 1.0))
        if vo: t = max(t, vo[-1][0] + vo[-1][3] + 0.2)  # never let two lines overlap
        if t + d > H + M + 0.1: print(f"WARNING: line runs past the footage: {text!r} ends {t + d:.2f} > {H + M:.2f}")
        vo.append((t, text, p, d))
    ep, ed = tts(C.get("end_vo", "Try The Training Notebook One free for 7 days."), C["voice"], C.get("rate", 1.0))
    vo_end_at = H + M + 0.35
    # caption chunks timed to voice
    caps = []
    for t, text, p, d in vo:
        cs = chunks(text); tot = sum(len(c) + 3 for c in cs); s = t
        for c in cs:
            e = s + d * (len(c) + 3) / tot; caps.append((c, s, e)); s = e
    # video graph
    inp = ["-loop", "1", "-t", f"{T:.2f}", "-i", f"{wd}/bg.png", "-loop", "1", "-t", f"{H:.2f}", "-i", C["cover"],
           "-loop", "1", "-i", f"{wd}/bezel.png", "-loop", "1", "-i", f"{wd}/mask.png"]
    n0 = 4
    for a, b, s in segs: inp += ["-ss", f"{a}", "-t", f"{b - a}", "-i", proxy]
    g = ";".join(f"[{n0 + i}:v]setpts=(PTS-STARTPTS)/{s}[s{i}]" for i, (a, b, s) in enumerate(segs))
    g += ";" + "".join(f"[s{i}]" for i in range(len(segs))) + f"concat=n={len(segs)}:v=1:a=0,tpad=stop_mode=clone:stop_duration={E + 1},setpts=PTS+{H}/TB[rec]"
    g += ";[3:v]format=gray[m];[rec]format=yuva420p[ra];[ra][m]alphamerge[recm]"
    yexp = f"{PY}+(1920-{PY})*pow(max(0\\,1-(t-{H})/0.42)\\,3)"
    g += f";[0:v][2:v]overlay=x={PX - 30}:y='{yexp}-20':enable='gte(t,{H})'[b0];[b0][recm]overlay=x={PX + PADX}:y='{yexp}':enable='gte(t,{H})'[b1]"
    k = 1; nin = n0 + len(segs)
    if bw:
        inp += ["-loop", "1", "-i", f"{wd}/bar.png"]; g += f";[b{k}][{nin}:v]overlay=x={(1080 - bw) // 2}:y=300:enable='gte(t,{H + 0.2})'[b{k + 1}]"; nin += 1; k += 1
    for i, (c, s, e) in enumerate(caps):
        pth = f"{wd}/c{i}.png"; cap_png(pth, c, kind); inp += ["-loop", "1", "-i", pth]
        g += f";[b{k}][{nin}:v]overlay=0:{410}:enable='between(t,{s:.2f},{e:.2f})'[b{k + 1}]"; nin += 1; k += 1
    for i, (t0, t1, text, x, y, side) in enumerate(C.get("notes", [])):
        pth = f"{wd}/n{i}.png"; note_png(pth, text, kind, side); inp += ["-loop", "1", "-i", pth]
        g += f";[b{k}][{nin}:v]overlay={x}:{y}:enable='between(t,{t0},{t1})'[b{k + 1}]"; nin += 1; k += 1
    # cover hook with slow push, then end card
    g += f";[1:v]scale=1080:1920,zoompan=z='1+0.0006*on':d=1:s=1080x1920:fps=30,trim=0:{H},setpts=PTS-STARTPTS[hk]"
    g += f";[b{k}][hk]overlay=0:0:enable='lt(t,{H})'[b{k + 1}]"; k += 1
    inp += ["-loop", "1", "-i", C.get("end_card", f"{V}/endcard.png")]
    g += f";[b{k}][{nin}:v]overlay=0:0:enable='gte(t,{H + M})'[b{k + 1}]"; nin += 1; k += 1
    g += f";[b{k}]format=yuv420p[vout]"
    silent = f"{wd}/silent.mp4"
    run("ffmpeg", "-v", "error", "-y", *inp, "-filter_complex", g, "-map", "[vout]", "-t", f"{T:.2f}", "-r", "30", "-c:v", "libx264", "-preset", "medium", "-crf", "19", silent)
    # audio
    # mix: voice clips each normalised to -16 LUFS; music normalised to -16 LUFS, then MUSIC_GAP dB in gaps
    # and ducked to MUSIC_UNDER dB while anyone speaks (guides: 15 to 20 dB under the voice, 0.3 s ramps)
    hi, lo, r = C.get("music_gap_db", -8.0), C.get("music_under_db", -19.0), 0.3
    wins = [(t - 0.15, t + d + 0.2) for t, _, _, d in vo] + [(vo_end_at - 0.15, vo_end_at + ed + 0.2)]
    W = "0"
    for a, b in wins: W = f"max({W},clip((t-{a - r:.2f})/{r},0,1)*clip(({b + r:.2f}-t)/{r},0,1))"
    mg = -16.0 - lufs(C["music"], 60)
    ainp = ["-i", C["music"]]; ag = f"[0:a]atrim=0:{T},aformat=channel_layouts=stereo,volume={mg:.2f}dB,volume='pow(10,({hi}-({hi - lo})*{W})/20)':eval=frame,afade=t=in:st=0:d=0.3,afade=t=out:st={T - 1.2:.2f}:d=1.2[mu]"; labels = ["[mu]"]; j = 1
    sounds = [(t, p, 10 ** ((-16.0 - lufs(p)) / 20)) for t, _, p, _ in vo] + [(vo_end_at, ep, 10 ** ((-16.0 - lufs(ep)) / 20))]
    sounds += [(t, f"{V}/sfx/{nm}.wav", 0.45) for t, nm in C.get("sfx", [])]
    sounds += [(H - 0.25, f"{V}/sfx/whoosh.wav", 0.5), (H + 0.05, f"{V}/sfx/swipe.wav", 0.5), (H + M + 0.05, f"{V}/sfx/whoosh.wav", 0.45)]
    if C.get("_mute") == "voice": sounds = [(t, p, 0.0) for t, p, v in sounds]
    if C.get("_mute") == "music": ag = ag.replace("[mu]", "[mu0];[mu0]volume=0[mu]", 1)
    if C.get("_mute") == "voice": sounds = [(t, p, 0.0) for t, p, v in sounds]
    if C.get("_mute") == "music": ag = ag.replace("[mu]", "[mu0];[mu0]volume=0[mu]", 1)
    for t, p, vol in sounds:
        ainp += ["-i", p]; ag += f";[{j}:a]aresample=44100,aformat=channel_layouts=stereo,volume={vol},adelay={int(t * 1000)}|{int(t * 1000)}[x{j}]"; labels.append(f"[x{j}]"); j += 1
    ag += ";" + "".join(labels) + f"amix=inputs={len(labels)}:normalize=0:duration=first," + ("anull" if C.get("_raw") else "loudnorm=I=-14:TP=-1.5:LRA=11") + "[aout]"
    run("ffmpeg", "-v", "error", "-y", "-i", silent, *ainp, "-filter_complex", ag.replace("[0:a]", "[1:a]").replace("[1:a]atrim", "[1:a]atrim", 1) if False else ag_fix(ag, len(sounds)), "-map", "0:v", "-map", "[aout]", "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-t", f"{T:.2f}", C["out"])
    print(C["name"], f"{T:.1f}s", "->", C["out"])
    return caps

def ag_fix(ag, n):
    # inputs are shifted by one because the silent video is input 0
    out = ag
    for j in range(n, -1, -1): out = out.replace(f"[{j}:a]", f"[{j + 1}:a]")
    return out

if __name__ == "__main__":
    for c in sys.argv[1:]: build(c)
