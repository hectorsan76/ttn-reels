"""Native pt-BR v2 videos built from the native app recordings (native_takes/pt, 2026-11-04).
python3 pt2.py howto <item> [...]   how-to from a take: segs and lines in take (proxy) seconds, taps and note from the tap log
python3 pt2.py people <item> [...]  people video: English phone stills swapped for the pt stills
Outputs /home/claude/loc/out_v2/<item>_pt_v2.mp4, cfg/<item>_pt_v2.json, cfg/cover_<item>_pt_v2.png.
Proxy time = tap log time (+0.05 s), checked 2026-11-04 against screen-change onsets."""
import json, os, sys, subprocess, math
V = "/root/ttn-reels/workbench/vt"; TPL = "/root/ttn-reels/workbench/templates"
sys.path.insert(0, V); sys.path.insert(0, V + "/loc")
import reel2
from PIL import Image, ImageDraw, ImageFont
import numpy as np
NT = "/mnt/user-data/uploads/TTN Reels/04 Working files/native_takes/pt/"
ST = NT + "stills/"
OUT = "/home/claude/loc/out_v2"; os.makedirs(OUT, exist_ok=True)
H = 1.6
LANG = "pt-BR"
END_VO = "The Training Notebook One. Software para personal trainers, feito para treinadores. Teste grátis por 7 dias."

# how-to specs: take, segs [[a, b, speed]] in take seconds, vo [(anchor, text)] anchor = take seconds or ("o", output s),
# note (tap label, text), chime (take s). Lines naming buttons use the app's pt labels as seen on screen.
HOWTO = {
 "howto02": dict(take="R-INVITE", title="REENVIAR CONVITE",
   segs=[[1.5, 4.9, 1.5], [4.9, 9.2, 1.5], [9.2, 12.8, 1.5], [32.3, 35.0, 1.0], [40.6, 42.2, 1.0], [45.2, 49.4, 1.0]],
   vo=[(("o", 1.7), "Personal trainer, o aluno perdeu o convite?"), (7.0, "Abra o perfil dele."),
       (32.4, "Toque no menu e depois em Enviar convite."), (45.3, "Pronto. Já está a caminho.")],
   note=("Mostrar menu", "toque"), chime=45.5),
 "howto31": dict(take="R-INVITE", title="CONFIRA O EMAIL",
   segs=[[5.4, 9.2, 1.5], [9.2, 12.8, 1.5], [20.6, 26.5, 1.2], [30.5, 35.0, 1.2], [40.6, 42.2, 1.0], [45.2, 49.4, 1.0]],
   vo=[(("o", 1.7), "Personal trainer, o aluno não recebeu o convite?"), (9.4, "Abra o perfil dele, toque em Editar dados e confira o email."),
       (31.5, "Depois toque no menu e em Enviar convite."), (45.3, "Um convite novo está a caminho.")],
   note=("Editar dados", "confira"), chime=45.5),
 "howto25": dict(take="R-BOOK", title="AGENDAR SESSÃO",
   segs=[[6.3, 9.95, 2.0], [9.95, 13.9, 1.6], [13.9, 20.3, 2.5], [42.2, 44.7, 1.5], [52.3, 69.5, 5.0], [74.4, 75.3, 1.0],
         [80.7, 85.5, 1.4], [90.5, 97.9, 3.0], [97.9, 113.0, 5.0], [146.6, 150.5, 1.0]],
   vo=[(("o", 1.7), "Personal trainer, agende uma sessão direto do calendário."), (9.8, "Toque no dia e escolha o aluno."),
       (15.8, "Dê um nome ao treino."), (52.4, "Defina o horário."), (81.0, "Está no calendário."),
       (90.8, "Abra e adicione os exercícios."), (146.7, "Agendado e montado.")],
   note=("AS", "escolha"), chime=146.8),
 "howto24": dict(take="R-TEMPLATE", title="MODELO DE PROGRAMA",
   segs=[[0.5, 6.5, 1.5], [9.0, 15.5, 2.2], [24.5, 46.5, 7.0], [52.8, 66.5, 3.5], [73.5, 102.0, 6.5], [103.0, 120.5, 5.0],
         [125.5, 160.5, 8.0], [160.5, 165.3, 1.0]],
   vo=[(("o", 1.7), "Personal trainer, monte um programa uma vez e use com todos os alunos."),
       (3.4, "Abra Modelos de programa e toque no mais."), (24.6, "Dê um nome e escolha os dias de treino."),
       (73.8, "Defina o objetivo e o nível."), (103.4, "Adicione o primeiro treino."), (125.8, "Depois adicione os exercícios."),
       (156.0, "A primeira semana está pronta. Passe a qualquer aluno.")],
   note=("Novo modelo de programa", "mais"), chime=159.0),
 "howto18": dict(take="R-TIMED", title="SÉRIES POR TEMPO",
   segs=[[2.5, 5.5, 1.5], [5.5, 23.0, 6.0], [23.0, 44.5, 7.0], [44.5, 47.0, 2.0], [63.3, 69.5, 2.5], [72.0, 96.0, 10.0],
         [146.5, 152.3, 3.0], [152.3, 172.5, 7.0], [172.5, 181.2, 4.0], [183.2, 196.3, 7.0], [208.0, 212.0, 3.0],
         [212.0, 233.0, 7.0], [233.0, 239.0, 3.0], [239.0, 243.0, 1.0]],
   vo=[(("o", 1.7), "Personal trainer, tem cardio no plano?"), (11.8, "Busque o remo."), (32.4, "Defina os minutos. Sem repetições."),
       (63.5, "Pronto, está aí."), (152.0, "Tiros? Segundos por série."), (211.0, "Corrida? Adicione a distância."),
       (236.0, "Tempo e distância, direto no treino.")],
   note=("73 808 Min", "minutos"), chime=240.0, cover="stills/pv10_timed28.png"),  # take cover shows the untranslated "Copy of" title
 "howto29": dict(take="R-DATE", title="ADICIONAR DATA",
   segs=[[22.6, 30.6, 2.5], [30.6, 48.6, 4.5], [48.6, 54.6, 2.5], [54.6, 87.6, 8.0], [87.6, 92.5, 1.0]],
   vo=[(("o", 1.7), "Personal trainer, treino ainda sem data?"), (30.0, "Toque em Adicionar data e escolha o dia."),
       (54.3, "Depois em Adicionar horário e escolha a hora."), (87.6, "Pronto, agendado com data e hora.")],
   note=("Adicionar data", "toque"), chime=87.5, cover="R-BOOK/stills/m_time.png"),  # R-DATE frames all show "Copy of"
 "howto30": dict(take="R-RENAME", title="RENOMEAR TREINO",
   segs=[[28.5, 38.2, 3.0], [38.2, 40.6, 1.2], [40.6, 52.0, 3.0], [55.8, 61.5, 1.0]],
   vo=[(("o", 1.7), "Personal trainer, o nome do treino não ficou bom?"), (37.9, "Toque no título e digite o nome novo."),
       (56.4, "Salve. Pronto.")],
   note=("Treino Completo", "toque"), chime=56.8),
 "howto32": dict(take="R-THROWAWAY_1", title="FICHA DE ANAMNESE",
   segs=[[2.95, 8.5, 2.0], [16.8, 18.5, 1.2], [108.5, 115.5, 2.5], [115.5, 125.0, 5.0], [143.0, 163.0, 8.0], [176.3, 218.0, 20.0],
         [236.0, 241.0, 4.0], [262.5, 271.0, 4.0], [293.4, 328.0, 20.0], [355.5, 441.0, 20.0], [470.5, 472.5, 1.0], [479.5, 485.0, 1.0]],
   vo=[(("o", 1.7), "Personal trainer, veja o que o seu aluno novo vê."), (4.0, "Ele abre o seu convite e começa a ficha de anamnese."),
       (108.6, "Nome, aniversário, objetivos e experiência."), (268.0, "Algumas perguntas de saúde, depois Enviar."),
       (480.0, "Fica no perfil dele antes da primeira sessão.")],
   note=("Enviar", "toque"), chime=481.0),
 "howto33": dict(take="R-SETTINGS", title="SUAS CONFIGURAÇÕES",
   segs=[[0.8, 2.0, 1.0], [2.0, 7.6, 2.5], [7.6, 13.0, 1.5], [18.3, 24.5, 1.5], [24.5, 29.0, 1.2]],
   vo=[(("o", 1.7), "Personal trainer, abra o menu e Configurações."), (8.0, "Escolha o idioma e as unidades."),
       (18.5, "Aparência Claro, Escuro ou Caderno."), (24.6, "E quais avisos você recebe.")],
   note=("Abrir menu", "toque"), chime=26.0),
}

# English phone still -> pt still (stills folder). Items whose stills come from PART B are not here.
SCREEN = {"workout_dark.png": "workout_dark", "home_dark.png": "home_dark", "intake_nb.png": "intake_nb", "cal_nb.png": "cal_nb",
          "client_nb.png": "client_nb", "timed32.png": "pv10_timed32", "timed28.png": "pv10_timed28",
          "assessments_dark.png": "assessments_dark", "photo_compare_dark.png": "photo_compare_dark",
          "client_list_dark.png": "client_list_dark", "client_profile_dark.png": "client_profile_dark",
          "program_templates_dark.png": "program_templates_dark", "wed1_chat_trainer.png": "chat_trainer",
          "wed2_chat_client.png": "chat_client", "scr_w47_sun_session_jessica.png": "session_accepted"}
WAITING = {"pv_w47_mon": "Follow up still from help take H01 (PART B)",
           "pv_w47_tue": "habits tab still from H09 and client_habits (PART B)",
           "pv_w47_thu": "phone stills from H08 (PART B)",
           "pv_w47_fri": "newbest_client and the trophy line from H07 (PART B)",
           "pv_w47_sat": "colour picker and colours set stills from H05 (PART B)"}

def dur(p): return float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", p], capture_output=True, text=True).stdout)

def omap(segs, p):
    t = H
    for a, b, s in segs:
        if p < a: return t
        if p <= b: return t + (p - a) / s
        t += (b - a) / s
    return t

def taps(take):
    J = json.load(open(NT + take + "/take_taplog.json")); out = []
    for e in J["events"]:
        if e.get("kind") != "tap" or "seen_t" not in e: continue
        out.append((e["seen_t"] + 0.05, e["label"], e.get("x_pt"), e.get("y_pt")))
    return out

def to_out_xy(x_pt, y_pt): return 240 + x_pt * 600 / 440, 610 + y_pt * 1304 / 956

# notes: 'left'/'right' draw the arrow down to the target; '_up' variants put the word below and point up
def note_png(path, text, kind, side):
    col = reel2.YELLOW if kind == "navy" else reel2.TEAL; f = ImageFont.truetype(reel2.FK, 86)
    up = side.endswith("_up"); base = side.replace("_up", ""); s = -1 if base == "left" else 1
    lines = text.split("|"); im = Image.new("RGBA", (420, 330), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    if up:
        ax = [(20, 150), (90, 144), (160, 110), (215, 30)]; ty = 170
    else:
        ty = 10; y = 10 + 86 * len(lines); ax = [(20, y + 20), (90, y + 26), (160, y + 60), (215, y + 110)]
    if base != "left": ax = [(420 - x, yy) for x, yy in ax]
    edge = reel2.NAVY if kind == "navy" else reel2.PAPER  # outline so the word reads over a light or dark app screen
    hx, hy = ax[-1]
    head = [(hx + s * 40, hy + 4), (hx, hy), (hx + s * 8, hy + 40)] if up else [(hx + s * 40, hy - 4), (hx, hy), (hx + s * 8, hy - 40)]
    for w, c in ((17, edge), (9, col)):
        d.line(ax, fill=c, width=w, joint="curve"); d.line(head, fill=c, width=w, joint="curve")
    for l in lines:
        d.text((10 if base == "left" else 410, ty), l, font=f, fill=col, anchor="la" if base == "left" else "ra", stroke_width=5, stroke_fill=edge); ty += 86
    rot = 6 if base == "left" else -6
    im = im.rotate(-rot if up else rot, resample=Image.BICUBIC, expand=True); im.save(path)
    return im

def note_place(text, tx, ty, kind):
    base = "right" if tx >= 540 else "left"; side = base + ("_up" if ty < 1000 else "")  # word toward the nearer side margin
    im = note_png("/tmp/_note_probe.png", text, kind, side); a = np.asarray(im)[:, :, 3]; ys, xs = np.where(a > 128)
    i = ys.argmin() if side.endswith("_up") else ys.argmax(); px, py = xs[i], ys[i]
    dx = -22 if base == "left" else 22; dy = 18 if side.endswith("_up") else -18
    return side, int(tx + dx - px), int(ty + dy - py)

reel2.note_png = note_png

def cover_howto(item, it, old):
    spec = json.load(open(f"{V}/cfg/coverspec_{item}_pt.json"))
    im = Image.open(NT + it.get("cover", it["take"] + "/stills/cover.png")).convert("RGB")
    a = f"_loc_{item}_v2.png"; im.resize((560, round(560 * im.height / im.width)), Image.LANCZOS).save(f"{TPL}/assets/{a}")
    lum = np.asarray(im.convert("L")).mean(); spec["screen"] = a; spec["bg"] = "paper" if lum < 110 else "navy"
    sp = f"{V}/cfg/coverspec_{item}_pt_v2.json"; json.dump(spec, open(sp, "w"), ensure_ascii=False)
    out = f"{V}/cfg/cover_{item}_pt_v2.png"
    subprocess.run(["python3", f"{TPL}/render_cover.py", sp, out], check=True, capture_output=True, cwd=TPL)
    return out

def timing(C, kind, rate):
    """start, end of each line as the builders place them; footage end"""
    if kind == "people":
        X = 0.22; shots = [dur(p) / s for p, s in C["shots"]]; starts = []; t = H
        for i, d in enumerate(shots): starts.append(t); t += d - (X if i < len(shots) - 1 else 0)
        fe = t; gap = 0.15
    else:
        fe = H + sum((b - a) / s for a, b, s in C["segs"]); gap = 0.2
    out = []; prev = None
    for item in C["vo"]:
        if kind == "people": tt = starts[item[0]] + item[1]; text = item[2]
        else: tt, text = item
        p, d = reel2.tts(text, C["voice"], rate, LANG)
        if prev is not None: tt = max(tt, prev + gap)
        prev = tt + d; out.append((round(tt, 2), round(tt + d, 2), text))
    return out, fe

def fits(lines, fe): return all(e <= fe - 0.1 for _, e, _ in lines) and lines[-1][1] <= fe - 0.6

def make_howto(item):
    it = HOWTO[item]; old = json.load(open(f"{V}/cfg/{item}_pt.json")); take = it["take"]
    segs = [list(s) for s in it["segs"]]; px = NT + take + "/take_p6.mp4"; tl = taps(take)
    C = {"name": f"{item}_pt_v2", "src": px, "proxy": px, "segs": segs, "bg": old["bg"], "hook_secs": H,
         "series": old["series"], "title": it["title"], "voice": old["voice"], "music": old["music"], "lang": LANG,
         "end_vo": END_VO, "end_card": f"{V}/endcard_pt.png", "out": f"{OUT}/{item}_pt_v2.mp4", "end_secs": old.get("end_secs", 3.6), "cap_gap": 0.07}
    C["cover"] = cover_howto(item, it, old)
    C["vo"] = [[a[1] if isinstance(a, tuple) else round(omap(segs, a), 2), text] for a, text in it["vo"]]
    # taps inside the kept footage -> tap sfx; chime
    sfx = []; last = -9
    for t, lab, x, y in tl:
        if any(a <= t <= b for a, b, s in segs):
            o = omap(segs, t)
            if o - last > 0.3: sfx.append([round(o, 2), "tap"]); last = o
    sfx.append([round(omap(segs, it["chime"]), 2), "chime"]); C["sfx"] = sfx
    # note: points at the named tap, shown for 1.4 s before it
    lab, word = it["note"]; hit = [e for e in tl if e[1] == lab and any(a <= e[0] <= b for a, b, s in segs)]
    t, _, x, y = hit[0]
    if x is None: x, y = map(float, lab.split()[:2])
    tx, ty = to_out_xy(x, y); side, nx, ny = note_place(word, tx, ty, old["bg"]); o = omap(segs, t)
    C["notes"] = [[round(max(H + 0.2, o - 1.4), 2), round(o + 0.15, 2), word, nx, ny, side]]
    # speaking rate; then stretch the final hold if the closing line still needs room
    for rate in (1.0, 1.05, 1.1, 1.15):
        lines, fe = timing(C, "howto", rate)
        if fits(lines, fe): break
    C["rate"] = rate
    if not fits(lines, fe):
        need = lines[-1][1] - (fe - 0.65); a, b, s = segs[-1]; segs[-1] = [a, b, (b - a) / ((b - a) / s + need)]
        lines, fe = timing(C, "howto", rate)
    p = f"{V}/cfg/{C['name']}.json"; json.dump(C, open(p, "w"), ensure_ascii=False, indent=1)
    return p, C, lines, fe

def make_people(item):
    old = json.load(open(f"{V}/cfg/{item}_pt.json")); C = json.loads(json.dumps(old))
    C["name"] = f"{item}_pt_v2"; C["out"] = f"{OUT}/{item}_pt_v2.mp4"; C["cover"] = f"{V}/cfg/cover_{item}_pt.png"; C["cap_gap"] = 0.07
    C["phone"]["screens"] = [[t, ST + SCREEN[os.path.basename(p)] + ".png"] for t, p in old["phone"]["screens"]]
    if item == "pv13":  # s13a shows Hector's phone with the English Home from 1.6 s: keep 0 to 1.5 s, raise the drawn phone at the cut
        a = "/home/claude/loc/out_v2/s13a_0_1.5.mp4"
        if not os.path.exists(a):
            subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", old["shots"][0][0], "-t", "1.5", "-an", "-c:v", "libx264", "-crf", "14", "-preset", "fast", a], check=True)
        C["shots"][0][0] = a; C["phone"]["t0"] = 2.74; C["phone"]["screens"][0][0] = 2.74
        C["vo"][0] = [0, 0.2, C["vo"][0][2], 250]
    for rate in (C.get("rate", 1.0), 1.05, 1.1, 1.15):
        lines, fe = timing(C, "people", rate)
        if fits(lines, fe): break
    C["rate"] = rate
    p = f"{V}/cfg/{C['name']}.json"; json.dump(C, open(p, "w"), ensure_ascii=False, indent=1)
    return p, C, lines, fe

def sheet(item):
    C = json.load(open(f"{V}/cfg/{item}_pt_v2.json")); s = f"/home/claude/loc/sheets_v2/{item}_pt_v2.jpg"; os.makedirs(os.path.dirname(s), exist_ok=True)
    T = dur(C["out"]); n = int(T // 0.75) + 1
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", C["out"], "-vf", f"fps=4/3,scale=216:-2,tile=10x{math.ceil(n / 10)}", "-frames:v", "1", s], check=True)
    return s

if __name__ == "__main__":
    kind, items = sys.argv[1], [a for a in sys.argv[2:] if not a.startswith("--")]
    for item in items:
        p, C, lines, fe = (make_howto if kind == "howto" else make_people)(item)
        print(f"== {item} rate {C['rate']} footage end {fe:.2f} fits {fits(lines, fe)}")
        for s, e, t in lines: print(f"   {s:6.2f} {e:6.2f}  {t}")
        if "--cfg" in sys.argv: continue
        mod = "people" if kind == "people" else "reel2"  # importing people changes reel2's phone width, so never both
        r = subprocess.run(["python3", "-c", f"import sys; sys.path.insert(0,'{V}'); sys.path.insert(0,'{V}/loc'); import pt2, {mod}; {mod}.build('{p}')"],
                           capture_output=True, text=True, cwd=V)
        print(r.stdout.strip()[-300:], r.stderr.strip()[-600:])
        print("sheet", sheet(item), "dur", round(dur(C["out"]), 2))
