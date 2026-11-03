"""TTN One people video builder (style lock 2026-10-21, people footage version 2026-10-28).
python3 people.py cfg.json -> 1080x1920 mp4
Timeline: designed cover hook (hook_secs) -> full screen graded gym shots joined by a whip pan
(slide with motion blur + whoosh) -> upper third captions timed to the Chirp 3 HD voice -> K05 end card.
cfg: name, cover, shots [[path, speed]], voice, vo [[shot_index, offset, text]], music, out, hook_secs, end_secs"""
import json, os, subprocess, sys
from PIL import Image, ImageDraw, ImageFont, ImageFilter
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import reel2
from reel2 import tts, lufs, chunks, F900, FS, V, phone_pngs, PADX
reel2.PW = PW = 780; reel2.SW = SW = PW - 2 * PADX; PX = (1080 - PW) // 2; PY = 600
import soundfile as sf

def run(*a): subprocess.run(list(a), check=True)
def dur(p): return float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", p], capture_output=True, text=True).stdout)

def cap_png(path, text):
    label = None
    if text.lower().startswith("personal trainers, "):
        label = "PERSONAL TRAINERS,"; text = text[len("personal trainers, "):]; text = text[0].upper() + text[1:]
    if label:
        tmp = path + ".main.png"; cap_png(tmp, text); main = Image.open(tmp)
        fs = ImageFont.truetype(FS, 44); dd = ImageDraw.Draw(Image.new("RGB", (1, 1))); w = int(dd.textlength(label, font=fs)) + 48
        bb = main.getbbox() or (0, 0, 1080, 240); top = bb[1]
        out = Image.new("RGBA", (1080, 330), (0, 0, 0, 0)); pill = Image.new("RGBA", (w, 76), (14, 122, 111, 255))
        ImageDraw.Draw(pill).text((24, 38), label, font=fs, fill=(248, 243, 232), anchor="lm")
        out.alpha_composite(pill, ((1080 - w) // 2, 0)); out.alpha_composite(main.crop((0, top, 1080, 240)), (0, 92)); out.save(path); return
    text = text.upper().rstrip("."); size = 92; dd = ImageDraw.Draw(Image.new("RGB", (1, 1)))
    while True:
        f = ImageFont.truetype(F900, size); ws = text.split(); lines = [""]
        for w in ws:
            t = (lines[-1] + " " + w).strip()
            if dd.textlength(t, font=f) <= 880: lines[-1] = t
            else: lines.append(w)
        if len(lines) <= 2 or size <= 56: break
        size -= 4
    if len(lines) == 2 and len(lines[1].split()) == 1 and len(lines[0].split()) > 2:  # no single orphan word
        a = lines[0].split(); lines = [" ".join(a[:-1]), a[-1] + " " + lines[1]]
    lh = int(size * 1.05); h = lh * len(lines) + 40
    im = Image.new("RGBA", (1080, 240), (0, 0, 0, 0)); d = ImageDraw.Draw(im); y0 = (240 - lh * len(lines)) // 2 + lh // 2
    for i, l in enumerate(lines): d.text((540, y0 + i * lh), l, font=f, fill=(0, 0, 0, 210), anchor="mm")
    sh = im.filter(ImageFilter.GaussianBlur(10)); sh2 = im.filter(ImageFilter.GaussianBlur(3))
    out = Image.new("RGBA", im.size, (0, 0, 0, 0)); out.alpha_composite(sh); out.alpha_composite(sh); out.alpha_composite(sh2); d = ImageDraw.Draw(out)
    for i, l in enumerate(lines): d.text((540, y0 + i * lh), l, font=f, fill=(255, 255, 255, 255), anchor="mm")
    out.save(path)

BW = ",hue=s=0.12,eq=contrast=1.12:brightness=-0.01"

def build(cfg):
    C = json.load(open(cfg)); wd = f"{V}/work/{C['name']}"; os.makedirs(wd, exist_ok=True)
    H = C.get("hook_secs", 1.6); E = C.get("end_secs", 3.6); X = 0.22
    shots = [(p, s, dur(p) / s) for p, s in C["shots"]]
    starts = []; t = H
    for i, (p, s, d) in enumerate(shots):
        starts.append(t); t += d - (X if i < len(shots) - 1 else 0)
    M = t - H; T = H + M + E
    # voice
    vo = []; cys = []
    for item in C["vo"]:
        si, off, text = item[:3]; cy = item[3] if len(item) > 3 else None
        p, d = tts(text, C["voice"], C.get("rate", 1.0)); tt = starts[si] + off
        if vo: tt = max(tt, vo[-1][0] + vo[-1][3] + 0.15)
        if tt + d > H + M + 0.05: print(f"WARNING past footage: {text!r} ends {tt + d:.2f} > {H + M:.2f}")
        vo.append((tt, text, p, d)); cys.append(cy)
    ep, ed = tts(C.get("end_vo", "Try The Training Notebook One free for 7 days."), C["voice"], C.get("rate", 1.0))
    E = max(E, 0.35 + ed + 0.6); T = H + M + E  # never cut the end line
    vo_end_at = H + M + 0.35
    caps = []
    for i, (tt, text, p, d) in enumerate(vo):
        e = tt + d + 0.35
        if i + 1 < len(vo): e = min(e, vo[i + 1][0] - 0.02)
        else: e = H + M - 0.05
        caps.append((text, tt - 0.05, e, cys[i]))
    # footage chain with whip pans
    inp = []; g = []
    for i, (p, s, d) in enumerate(shots):
        inp += ["-i", p]; g.append(f"[{i}:v]setpts=(PTS-STARTPTS)/{s},fps=30{BW if C.get('bw') else ''},format=yuv444p,settb=1/30[v{i}]")
    cur = "v0"; acc = shots[0][2]
    for i in range(1, len(shots)):
        g.append(f"[{cur}][v{i}]xfade=transition=slideleft:duration={X}:offset={acc - X:.3f}[x{i}]"); cur = f"x{i}"; acc += shots[i][2] - X
    n = len(shots)
    # motion blur around each cut
    blur = "+".join(f"between(t,{starts[i] - H + 0.04:.2f},{starts[i] - H + X + 0.02:.2f})" for i in range(1, n))
    g.append(f"[{cur}]split[a][b];[b]avgblur=sizeX=36:sizeY=1[bb];[a][bb]overlay=enable='{blur}',crop=1068:1920:6:0,scale=1080:1920,format=yuv420p,setpts=PTS+{H}/TB[foot]")
    inp += ["-f", "lavfi", "-t", f"{T:.2f}", "-i", "color=c=0x0B0F19:s=1080x1920:r=30", "-loop", "1", "-t", f"{H:.2f}", "-i", C["cover"]]
    bgi, cvi = n, n + 1
    g.append(f"[{bgi}:v][foot]overlay=0:0:eof_action=pass[b0]")
    k = 0; nin = n + 2
    PH = C.get("phone")
    if PH:
        sh_h = phone_pngs(wd); t0 = PH["t0"]
        dim = Image.new("RGBA", (1080, 1920), (0, 0, 0, int(255 * PH.get("dim", 0.38)))); dim.save(f"{wd}/dim.png")
        inp += ["-loop", "1", "-i", f"{wd}/dim.png", "-loop", "1", "-i", f"{wd}/bezel.png"]
        g.append(f"[b{k}][{nin}:v]overlay=0:0:enable='gte(t,{t0 - 0.1:.2f})'[b{k + 1}]"); nin += 1; k += 1
        yexp = f"{PY}+(1920-{PY})*pow(max(0\\,1-(t-{t0})/0.42)\\,3)"
        g.append(f"[b{k}][{nin}:v]overlay=x={PX - 30}:y='{yexp}-20':enable='gte(t,{t0})'[b{k + 1}]"); nin += 1; k += 1
        m = Image.open(f"{wd}/mask.png")
        scr = PH["screens"]
        for i, (ts, png) in enumerate(scr):
            te = scr[i + 1][0] if i + 1 < len(scr) else T
            im = Image.open(png).convert("RGBA").resize((SW, sh_h), Image.LANCZOS); im.putalpha(m); im.save(f"{wd}/scr{i}.png")
            inp += ["-loop", "1", "-i", f"{wd}/scr{i}.png"]
            g.append(f"[b{k}][{nin}:v]overlay=x={PX + PADX}:y='{yexp}':enable='between(t,{max(ts, t0):.2f},{te:.2f})'[b{k + 1}]"); nin += 1; k += 1
    for i, (c, s0, e, cy) in enumerate(caps):
        pth = f"{wd}/c{i}.png"; cap_png(pth, c); inp += ["-loop", "1", "-i", pth]
        g.append(f"[b{k}][{nin}:v]overlay=0:{cy if cy is not None else (300 if c.lower().startswith('personal trainers, ') else 345)}:enable='between(t,{s0:.2f},{e:.2f})'[b{k + 1}]"); nin += 1; k += 1
    g.append(f"[{cvi}:v]scale=1080:1920,zoompan=z='1+0.0006*on':d=1:s=1080x1920:fps=30,trim=0:{H},setpts=PTS-STARTPTS[hk]")
    g.append(f"[b{k}][hk]overlay=0:0:enable='lt(t,{H})'[b{k + 1}]"); k += 1
    inp += ["-loop", "1", "-i", C.get("end_card", f"{V}/endcard.png")]
    g.append(f"[b{k}][{nin}:v]overlay=0:0:enable='gte(t,{H + M:.2f})'[b{k + 1}]"); k += 1
    g.append(f"[b{k}]format=yuv420p[vout]")
    silent = f"{wd}/silent.mp4"
    run("ffmpeg", "-v", "error", "-y", *inp, "-filter_complex", ";".join(g), "-map", "[vout]", "-t", f"{T:.2f}", "-r", "30", "-c:v", "libx264", "-preset", "medium", "-crf", "19", silent)
    # audio: same mix as reel2 (voice -16 LUFS, music 19 dB under speech, 8 dB in gaps, 0.3 s ramps, -14 LUFS out)
    hi, lo, r = C.get("music_gap_db", -8.0), C.get("music_under_db", -19.0), 0.3
    wins = [(tt - 0.15, tt + d + 0.2) for tt, _, _, d in vo] + [(vo_end_at - 0.15, vo_end_at + ed + 0.2)]
    W = "0"
    for a, b in wins: W = f"max({W},clip((t-{a - r:.2f})/{r},0,1)*clip(({b + r:.2f}-t)/{r},0,1))"
    mg = -16.0 - lufs(C["music"], 60); ms = C.get("music_start", 0)
    ainp = ["-i", silent, "-ss", str(ms), "-i", C["music"]]
    ag = f"[1:a]atrim=0:{T},asetpts=PTS-STARTPTS,aformat=channel_layouts=stereo,volume={mg:.2f}dB,volume='pow(10,({hi}-({hi - lo})*{W})/20)':eval=frame,afade=t=in:st=0:d=0.3,afade=t=out:st={T - 1.2:.2f}:d=1.2[mu]"
    labels = ["[mu]"]; j = 2
    sounds = [(tt, p, 10 ** ((-16.0 - lufs(p)) / 20)) for tt, _, p, _ in vo] + [(vo_end_at, ep, 10 ** ((-16.0 - lufs(ep)) / 20))]
    sounds += [(starts[i] - 0.08, f"{V}/sfx/whoosh.wav", 0.4) for i in range(1, n)]
    if PH: sounds += [(PH["t0"] - 0.05, f"{V}/sfx/swipe.wav", 0.5)] + [(ts - 0.05, f"{V}/sfx/tap.wav", 0.45) for ts, _ in PH["screens"][1:]]
    sounds += [(H - 0.25, f"{V}/sfx/whoosh.wav", 0.5), (H + M + 0.05, f"{V}/sfx/whoosh.wav", 0.45)]
    for tt, p, vol in sounds:
        ainp += ["-i", p]; ag += f";[{j}:a]aresample=44100,aformat=channel_layouts=stereo,volume={vol},adelay={int(tt * 1000)}|{int(tt * 1000)}[x{j}]"; labels.append(f"[x{j}]"); j += 1
    ag += ";" + "".join(labels) + f"amix=inputs={len(labels)}:normalize=0:duration=first,loudnorm=I=-14:TP=-1.5:LRA=11[aout]"
    run("ffmpeg", "-v", "error", "-y", *ainp, "-filter_complex", ag, "-map", "0:v", "-map", "[aout]", "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-t", f"{T:.2f}", C["out"])
    print(C["name"], f"{T:.1f}s", "->", C["out"]); return caps

if __name__ == "__main__":
    for c in sys.argv[1:]: build(c)
