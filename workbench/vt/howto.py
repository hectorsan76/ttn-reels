"""TTN One how-to video builder. One JSON per video -> finished 1080x1920 mp4.
config: {"src", "segs": [[a,b,speed]], "end_image": path|null, "end_secs", "caps": [[a,b,kicker|null,text]],
         "vo": [[out_time, text]], "music", "out"}
caps times are SOURCE seconds; a cap time >= src_end+0.001 is read as "end image" time offset with prefix "E+x".
"""
import json, os, re, subprocess, sys
from PIL import Image, ImageDraw, ImageFont, ImageFilter
D = "/home/claude/demo"; H = "/home/claude/howto"
F800 = f"{D}/Montserrat-800.ttf"
TEAL, INK, ORANGE = (14, 122, 111), (26, 26, 26), (238, 120, 104)
PH = 1560; PW = 718; PX = (1080 - PW) // 2; PY = 320

def run(*a): subprocess.run(list(a), check=True)

def text_png(path, kicker, line, w=1080, h=300):
    im = Image.new("RGBA", (w, h), (0, 0, 0, 0)); d = ImageDraw.Draw(im); y = 0
    if kicker:
        f = ImageFont.truetype(F800, 40); tw = d.textlength(kicker, font=f)
        d.rounded_rectangle(((w - tw) / 2 - 22, 20, (w + tw) / 2 + 22, 78), 12, fill=ORANGE)
        d.text((w / 2, 49), kicker, font=f, fill=INK, anchor="mm"); y = 90
    size = 72
    def wrap(f):
        lines = [""]
        for wd in line.split():
            t = (lines[-1] + " " + wd).strip()
            if d.textlength(t, font=f) > w - 120: lines.append(wd)
            else: lines[-1] = t
        return lines
    f = ImageFont.truetype(F800, size); lines = wrap(f)
    while len(lines) > 2:
        size -= 4; f = ImageFont.truetype(F800, size); lines = wrap(f)
    lh = size * 1.15; top = y + (h - y - lh * len(lines)) / 2
    for i, l in enumerate(lines): d.text((w / 2, top + lh * i + lh / 2), l, font=f, fill="white", anchor="mm")
    im.save(path)

def sub_png(path, text):
    F = ImageFont.truetype(F800, 66); d = ImageDraw.Draw(Image.new("RGBA", (1, 1)))
    tw = d.textlength(text, font=F); pad = 34
    im = Image.new("RGBA", (1080, 130), (0, 0, 0, 0)); dr = ImageDraw.Draw(im); x0 = (1080 - tw) / 2 - pad
    dr.rounded_rectangle((x0, 10, x0 + tw + 2 * pad, 120), 26, fill=(26, 26, 26, 235))
    dr.text((540, 65), text, font=F, fill="white", anchor="mm"); im.save(path)

def chunks(text):
    out = []
    for sent in re.findall(r"[^.?!,]+[.?!,]?", text):
        w = sent.split()
        while w:
            n = 3 if len(w) != 4 else 2
            out.append(" ".join(w[:n])); w = w[n:]
    return [c.rstrip(",.") if not c.endswith("?") else c for c in out if c]

def build(cfg_path):
    C = json.load(open(cfg_path)); name = os.path.splitext(os.path.basename(cfg_path))[0]
    wd = f"{H}/{name}"; os.makedirs(wd, exist_ok=True)
    segs = C["segs"]; src_total = sum((b - a) / s for a, b, s in segs)
    end_secs = C.get("end_secs", 0) if C.get("end_image") else 0
    cta = C.get("cta"); cta_secs = cta["secs"] if cta else 0
    total = src_total + end_secs + C.get("tail", 0.5) + cta_secs; cta_at = total - cta_secs
    def ot(t):
        if isinstance(t, str) and t.startswith("E+"): return src_total + float(t[2:])
        o = 0.0
        for a, b, s in segs:
            if t <= a: return o
            if t < b: return o + (t - a) / s
            o += (b - a) / s
        return o
    # proxy
    proxy = f"{wd}/proxy.mp4"
    if not os.path.exists(proxy):
        run("ffmpeg", "-v", "error", "-y", "-i", C["src"], "-vf", f"fps=30,scale={PW}:{PH}:flags=lanczos", "-an",
            "-c:v", "libx264", "-crf", "14", "-preset", "fast", proxy)
    # background + mask
    bg = Image.new("RGB", (1080, 1920), TEAL); sh = Image.new("RGBA", (1080, 1920), (0, 0, 0, 0))
    ImageDraw.Draw(sh).rounded_rectangle((PX - 4, PY + 14, PX + PW + 4, PY + PH + 18), 48, fill=(0, 0, 0, 110))
    sh = sh.filter(ImageFilter.GaussianBlur(18)); bg.paste(sh, (0, 0), sh); bg.save(f"{wd}/bg.png")
    m = Image.new("L", (PW, PH), 0); ImageDraw.Draw(m).rounded_rectangle((0, 0, PW - 1, PH - 1), 44, fill=255); m.save(f"{wd}/mask.png")
    inputs = ["-loop", "1", "-i", f"{wd}/bg.png", "-i", f"{wd}/mask.png"]
    for a, b, s in segs: inputs += ["-ss", f"{a}", "-t", f"{b-a}", "-i", proxy]
    nin = 2 + len(segs)
    g = ";".join(f"[{2+i}:v]setpts=(PTS-STARTPTS)/{s}[v{i}]" for i, (a, b, s) in enumerate(segs))
    parts = "".join(f"[v{i}]" for i in range(len(segs))); n = len(segs)
    if end_secs:
        ei = Image.open(C["end_image"]).convert("RGB"); r = PW / ei.width
        ei = ei.resize((PW, round(ei.height * r)), Image.LANCZOS)
        canvas = Image.new("RGB", (PW, PH), (255, 255, 255)); canvas.paste(ei.crop((0, 0, PW, min(PH, ei.height))), (0, 0))
        canvas.save(f"{wd}/end.png"); inputs += ["-loop", "1", "-t", str(end_secs), "-i", f"{wd}/end.png"]
        g += f";[{nin}:v]fps=30,format=yuv420p,setsar=1[ve]"; parts += "[ve]"; n += 1; nin += 1
    g += f";{parts}concat=n={n}:v=1:a=0,tpad=stop_mode=clone:stop_duration={C.get('tail', 0.5)}[ph]"
    g += ";[1:v]format=gray[m];[ph]format=yuva420p[pa];[pa][m]alphamerge[pm]"
    g += f";[0:v]trim=0:{total},setpts=PTS-STARTPTS[bg];[bg][pm]overlay={PX}:{PY}[b0]"
    k = 0
    for i, (a, b, kick, txt) in enumerate(C["caps"]):
        p = f"{wd}/cap{i}.png"; text_png(p, kick, txt); inputs += ["-loop", "1", "-i", p]
        ta, tb = ot(a), (total if i == len(C["caps"]) - 1 else ot(b))
        g += f";[b{k}][{nin}:v]overlay=0:20:enable='between(t,{ta:.2f},{tb:.2f})'[b{k+1}]"; nin += 1; k += 1
    if cta:
        inputs += ["-loop", "1", "-i", cta["img"]]
        g += f";[{nin}:v]format=rgba,fade=in:st={cta_at:.2f}:d=0.35:alpha=1[cta];[b{k}][cta]overlay=0:0:enable='gte(t,{cta_at:.2f})'[b{k+1}]"
        nin += 1; k += 1
    g += f";[b{k}]format=yuv420p[vout]"
    silent = f"{wd}/silent.mp4"
    run("ffmpeg", "-v", "error", "-y", *inputs, "-filter_complex", g, "-map", "[vout]", "-t", f"{total:.2f}",
        "-c:v", "libx264", "-preset", "medium", "-crf", "19", "-r", "30", silent)
    withm = f"{wd}/music.mp4"
    run("ffmpeg", "-v", "error", "-y", "-i", silent, "-i", C["music"], "-filter_complex",
        f"[1:a]atrim=0:{total},volume={C.get('music_vol', 0.55)},afade=t=out:st={total-1.2:.2f}:d=1.2[a]", "-map", "0:v", "-map", "[a]",
        "-c:v", "copy", "-c:a", "aac", "-shortest", withm)
    def vt(a):
        if isinstance(a, str) and a.startswith("S"): return round(ot(float(a[1:])), 2)
        if isinstance(a, str) and a.startswith("C+"): return round(cta_at + float(a[2:]), 2)
        return a
    js = f"{wd}/vo.json"
    json.dump({"voice": {"am_fenrir": 0.7, "am_michael": 0.3},
               "lines": [{"at": vt(a), "text": t, "speed": C.get("vo_speed", 1.04)} for a, t in C["vo"]]}, open(js, "w"))
    voiced = f"{wd}/voiced.mp4"
    rep = subprocess.run(["python3", f"{D}/ttn_voiceover.py", js, withm, voiced, "--models", D],
                         check=True, capture_output=True, text=True).stdout
    print(rep)
    items = []
    for line in rep.splitlines():
        mm = re.match(r"\s*([\d.]+) to\s+([\d.]+)\s+(.*)", line)
        if not mm: continue
        a, b, t = float(mm[1]), float(mm[2]), mm[3]; cs = chunks(t); tot = sum(len(c) + 3 for c in cs); s = a
        for c in cs:
            e = s + (b - a) * (len(c) + 3) / tot; items.append((c, s, e)); s = e
    inputs, g = [], ""
    items = [it for it in items if not cta or it[1] < cta_at - 0.05]
    for i, (c, s, e) in enumerate(items):
        p = f"{wd}/s{i}.png"; sub_png(p, c); inputs += ["-loop", "1", "-i", p]
        g += f"{'[0:v]' if i == 0 else f'[o{i}]'}[{i+1}:v]overlay=0:{C.get('sub_y', 1600)}:enable='between(t,{s:.2f},{e+0.08:.2f})':shortest=1[o{i+1}];"
    g += f"[o{len(items)}]format=yuv420p[v]"
    run("ffmpeg", "-v", "error", "-y", "-i", voiced, *inputs, "-filter_complex", g, "-map", "[v]", "-map", "0:a",
        "-c:v", "libx264", "-crf", "19", "-preset", "medium", "-c:a", "copy", C["out"])
    print(name, round(total, 1), "s ->", C["out"])

if __name__ == "__main__":
    for p in sys.argv[1:]: build(p)
