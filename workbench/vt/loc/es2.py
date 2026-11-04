"""Native es-MX v2 videos built from the native app recordings (native_takes/es, 2026-11-04/05). Copy of pt2.py.
python3 es2.py howto <item> [...]   how-to from a take: segs and lines in take (proxy) seconds, taps and note from the tap log
python3 es2.py people <item> [...]  people video: English phone stills swapped for the es stills
Outputs /home/claude/loc/out_es_v2/<item>_es_v2.mp4, cfg/<item>_es_v2.json, cfg/cover_<item>_es_v2.png.
Proxy time = tap log time (+0.05 s), checked 2026-11-04 against screen-change onsets."""
import json, os, sys, subprocess, math
V = "/root/ttn-reels/workbench/vt"; TPL = "/root/ttn-reels/workbench/templates"
sys.path.insert(0, V); sys.path.insert(0, V + "/loc")
import reel2
from PIL import Image, ImageDraw, ImageFont
import numpy as np
NT = "/mnt/user-data/uploads/TTN Reels/04 Working files/native_takes/es/"
ST = NT + "stills/"
OUT = "/home/claude/loc/out_es_v2"; os.makedirs(OUT, exist_ok=True)
H = 1.6
LANG = "es-US"  # es-MX copy; Google Chirp3-HD has no es-MX voice (400), es-US is the Latin American voice the es v1 set used
END_VO = "The Training Notebook One. Software para entrenadores personales, hecho para entrenadores. Pruébenlo gratis 7 días."

# how-to specs: take, segs [[a, b, speed]] in take seconds, vo [(anchor, text)] anchor = take seconds or ("o", output s),
# note (tap label, text), chime (take s). Lines naming buttons use the app's es-MX labels as seen on screen (glossary_es.csv).
# es takes (native_takes_es_A.md, _B.md) run on their own clock, so every seg below is set from the es tap logs and contact sheets.
# Night time rule: the es-MX 12 hour wheels show "a. m." beside an hour row; any wheel frame where a 10 p. m. to 5 a. m. row or
# selection is on screen is cut (R-DATE wheel 10:34 p. m., H03 wheel 12:03 a. m., the 6 p. m. settings where "05 59 a. m." sits above).
HOWTO = {
 "howto02": dict(take="R-INVITE", title="REENVIAR INVITACIÓN",
   segs=[[1.5, 4.9, 1.5], [4.9, 9.2, 1.5], [9.2, 12.8, 1.5], [26.8, 29.5, 1.0], [37.8, 39.4, 1.0], [41.6, 45.8, 1.0]],
   vo=[(("o", 1.7), "Entrenadores personales, ¿su cliente perdió su invitación?"), (7.0, "Abran su perfil."),
       (26.9, "Toquen el menú y luego Enviar invitación."), (41.7, "Listo. Ya va en camino.")],
   note=("Mostrar menú", "toquen"), chime=41.9),
 "howto31": dict(take="R-INVITE", title="REVISEN EL CORREO",
   segs=[[5.4, 9.2, 1.5], [9.2, 12.8, 1.5], [20.4, 24.5, 1.2], [25.0, 29.5, 1.2], [37.8, 39.4, 1.0], [41.6, 45.8, 1.0]],
   vo=[(("o", 1.7), "Entrenadores personales, ¿a su cliente nunca le llegó la invitación?"), (9.4, "Abran su perfil, toquen Editar datos y revisen el correo."),
       (25.5, "Luego toquen el menú y Enviar invitación."), (41.7, "Una invitación nueva va en camino.")],
   note=("Editar datos", "revisen"), chime=41.9),
 "howto25": dict(take="R-BOOK", title="AGENDAR SESIÓN",
   segs=[[1.2, 7.0, 2.0], [7.0, 11.6, 2.0], [11.6, 16.5, 1.6], [16.5, 25.0, 3.0], [32.3, 39.6, 2.0], [44.6, 47.0, 1.0],
         [50.8, 55.0, 1.4], [60.8, 66.0, 2.0], [66.0, 116.0, 6.0], [116.0, 119.5, 1.0]],
   vo=[(("o", 1.7), "Entrenadores personales, agenden una sesión directo desde su calendario."), (5.0, "Toquen el día y elijan al cliente."),
       (17.9, "Pónganle nombre a la rutina."), (32.5, "Pongan la hora."), (51.0, "Ya está en el calendario."),
       (61.3, "Ábranla y agreguen los ejercicios."), (116.1, "Agendada y armada.")],
   note=("135 757 Lucía López", "elijan"), chime=116.4),
 "howto24": dict(take="R-TEMPLATE", title="PLANTILLA DE PROGRAMA",
   segs=[[0.5, 6.0, 1.5], [9.0, 16.5, 2.2], [24.5, 52.0, 7.0], [55.0, 60.5, 2.0], [65.8, 91.0, 6.5], [96.8, 117.0, 5.0],
         [123.4, 170.0, 8.0], [170.0, 176.0, 1.0]],
   vo=[(("o", 1.7), "Entrenadores personales, armen un programa una vez y úsenlo con todos sus clientes."),
       (3.3, "Abran Plantillas de programa y toquen el más."), (24.6, "Pónganle nombre y elijan los días de entrenamiento."),
       (66.0, "Definan el objetivo y el nivel."), (97.3, "Agreguen la primera rutina."), (123.8, "Luego agreguen los ejercicios."),
       (165.0, "La primera semana está lista. Asígnenla a cualquier cliente.")],
   note=("Nueva plantilla de programa", "más"), chime=168.5),
 "howto18": dict(take="R-TIMED", title="SERIES POR TIEMPO",
   segs=[[2.0, 7.0, 1.5], [7.0, 19.0, 4.0], [19.0, 55.5, 8.0], [55.5, 60.3, 2.0], [60.3, 64.5, 1.5], [64.5, 73.2, 3.0],
         [73.2, 76.5, 1.5], [76.5, 143.5, 10.0], [143.5, 154.8, 3.0], [154.8, 158.5, 1.5], [158.5, 178.4, 4.0],
         [178.4, 201.9, 6.0], [201.9, 218.4, 4.0], [218.4, 233.0, 3.0]],
   vo=[(("o", 1.7), "Entrenadores personales, ¿hay cardio en el plan?"), (11.0, "Busquen el remo."), (60.3, "Pongan los minutos. Sin repeticiones."),
       (73.0, "Ahí está."), (143.3, "¿Sprints? Segundos por serie."), (209.5, "¿Correr? Agreguen la distancia."),
       (226.0, "Tiempo y distancia, ahí mismo en la rutina.")],
   note=("74 808 Min", "minutos"), chime=230.0),
 "howto29": dict(take="R-DATE", title="AGREGAR FECHA",
   # renamed copy from 58.8 s ("Copy of Cuerpo Total" shows 23.5 to 58.7 s); the time wheel (10:34 p. m., then rows beside "a. m.")
   # from 99.75 s to Listo at 134.05 s is cut: the line names the step, the result shows 6:30 p. m.
   segs=[[58.8, 67.3, 2.0], [67.3, 92.8, 5.0], [92.8, 99.6, 2.0], [134.6, 141.0, 1.0]],
   vo=[(("o", 1.7), "Entrenadores personales, ¿rutina sin fecha todavía?"), (67.1, "Toquen Agregar fecha y elijan el día."),
       (93.0, "Luego Agregar hora y elijan la hora."), (134.7, "Listo, agendada con fecha y hora.")],
   note=("Agregar fecha", "toquen"), chime=134.7, cover="R-DATE/stills/cover.png"),
 "howto30": dict(take="R-RENAME", title="RENOMBRAR RUTINA",
   segs=[[2.0, 8.1, 2.5], [8.1, 10.4, 1.2], [10.4, 20.5, 3.0], [25.8, 31.4, 1.0]],  # page loads blank before 1.8 s
   vo=[(("o", 1.7), "Entrenadores personales, ¿el nombre de la rutina no quedó bien?"), (7.9, "Toquen el título y escriban el nombre nuevo."),
       (26.5, "Guarden. Listo.")],
   note=("Cuerpo Total", "toquen"), chime=26.8),
 "howto32": dict(take="R-THROWAWAY_1", title="FORMULARIO DE INGRESO",
   segs=[[0.5, 5.3, 2.0], [5.3, 30.5, 8.0], [30.5, 38.5, 3.0], [38.5, 73.0, 12.0], [73.0, 78.5, 2.0], [78.5, 102.0, 10.0],
         [102.0, 110.8, 3.0], [110.8, 119.5, 4.0], [119.5, 129.3, 4.0], [129.3, 136.4, 1.0]],
   vo=[(("o", 1.7), "Entrenadores personales, esto es lo que ve su cliente nuevo."), (1.0, "Abre su invitación y empieza el formulario de ingreso."),
       (5.4, "Nombre, cumpleaños, objetivos y experiencia."), (110.9, "Unas preguntas de salud, luego Enviar."),
       (130.0, "Queda en su perfil antes de la primera sesión.")],
   note=("218 746 Enviar", "toca"), chime=129.3),
 "howto33": dict(take="R-SETTINGS", title="SUS AJUSTES",
   segs=[[0.8, 1.9, 1.0], [1.9, 7.5, 2.5], [7.5, 13.5, 1.5], [13.5, 19.7, 1.5], [19.7, 24.8, 1.2]],
   vo=[(("o", 1.7), "Entrenadores personales, abran el menú y luego Ajustes."), (8.0, "Elijan su idioma y sus unidades."),
       (10.5, "Apariencia Claro, Oscuro o Libreta."), (19.0, "Y qué avisos reciben.")],
   note=("Abrir menú", "toquen"), chime=21.5),
}

# English phone still -> es still (stills folder, same names as pt; the colour stills are in stills/ for es).
SCREEN = {"workout_dark.png": "workout_dark", "home_dark.png": "home_dark", "intake_nb.png": "intake_nb", "cal_nb.png": "cal_nb",
          "client_nb.png": "client_nb", "timed32.png": "pv10_timed32", "timed28.png": "pv10_timed28",
          "assessments_dark.png": "assessments_dark", "photo_compare_dark.png": "photo_compare_dark",
          "client_list_dark.png": "client_list_dark", "client_profile_dark.png": "client_profile_dark",
          "program_templates_dark.png": "program_templates_dark", "wed1_chat_trainer.png": "chat_trainer",
          "wed2_chat_client.png": "chat_client", "scr_w47_sun_session_jessica.png": "session_accepted",
          "mon1_follow_up.png": "w47_mon1_follow_up", "tue1_habits_tab.png": "w47_tue1_habits_tab", "tue2_client_home.png": "client_habits",
          "thu1_sofia_workouts.png": "w47_thu1_sofia_workouts", "thu2_workout_phone.png": "w47_thu2_workout_phone",
          "scr_w47_fri_new_best.png": "newbest_client", "fri2_trophy_line.png": "w47_fri2_trophy_line",
          "sat1_colour_pick.png": "w47_sat1_colour_pick", "sat2_colours_set.png": "w47_sat2_colours_set"}
# same fixes as pt: the es chat has no voice note; no workout still shows a trainer note, so pn05 shows the client's Home
# ("Nota de tu coach" on today's workout); Follow up reads "Seguimiento" and Home "Inicio" in the es app
PEOPLE_FIX = {
 "pn05": dict(vo={1: "Agreguen una nota a cualquier rutina, y aparece justo ahí en la rutina."}, screens=["client_nb"]),
 "pv_w47_wed": dict(vo={1: "El chat está justo al lado de sus rutinas."}, kicker="la conversación junto a la rutina"),
 "pv_w47_mon": dict(vo={1: "Seguimiento en Inicio muestra a cada cliente que faltó, con un botón de mensaje."}, kicker="Seguimiento, directo en Inicio"),
}
WAITING = {}

def dur(p): return float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", p], capture_output=True, text=True).stdout)

def omap(segs, p):
    """output time of source time p; segments may come out of source order (two takes joined)"""
    t = H; nxt = None
    for a, b, s in segs:
        if a <= p <= b: return t + (p - a) / s
        if p < a and (nxt is None or a < nxt[0]): nxt = (a, t)
        t += (b - a) / s
    return nxt[1] if nxt else t

def takes_of(it):
    t = it["take"]; return t if isinstance(t, list) else [(t, 0.0)]

def taps(take, off=0.0):
    J = json.load(open(NT + take + "/take_taplog.json")); out = []
    for e in J.get("events", []):
        if e.get("kind") != "tap" or "seen_t" not in e: continue
        out.append((e["seen_t"] + 0.05 + off, e["label"], e.get("x_pt"), e.get("y_pt")))
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

# ---------------------------------------------------------------- PART B (2026-11-04 evening): help videos, redaction
import es2_ocr as pt2_ocr, re
HOWTO.update({
 "howto26": dict(take="H05", title="EXPORTAR PDF", cover="H05/stills/pdf_menu.png",
   # Preview shows the cached pt PDF ("Ana Souza - Corpo inteiro A") 115.0 to 117.9 s: the PDF part starts at 118.2 s
   segs=[[3.5, 9.5, 1.5], [91.5, 98.5, 1.3], [98.5, 112.5, 2.5], [118.2, 140.0, 3.5]],
   vo=[(("o", 1.7), "Entrenadores personales, ¿su cliente va a entrenar solo esta semana?"), (91.6, "Abran la rutina, toquen el menú y luego Exportar PDF."),
       (118.3, "Mándenla o imprímanla, para que nunca ande adivinando.")],
   note=("Exportar PDF", "toquen"), chime=118.3),
 "howto27": dict(take="H03", title="ARMAR UNA RUTINA",
   # the time wheel (12:03 a. m., then night rows beside "a. m.") 46.5 to 89.6 s is cut; the form after it shows 6:00 p. m.
   segs=[[7.0, 16.9, 2.5], [16.9, 21.0, 1.5], [89.8, 95.0, 1.5], [95.0, 122.5, 7.0], [176.5, 206.0, 6.0], [206.0, 272.0, 7.0],
         [396.0, 402.0, 2.0]],
   vo=[(("o", 1.7), "Entrenadores personales, ¿armando la rutina de hoy?"), (12.0, "Toquen Agregar rutina y luego Armar rutina desde cero."),
       (90.0, "Pongan la hora y un nombre."), (176.8, "Busquen el ejercicio y agréguenlo."),
       (217.0, "Series, repeticiones y peso en el teclado numérico."), (396.5, "Lista antes de que llegue su cliente.")],
   note=("Armar rutina desde cero", "toquen"), chime=401.5),
 "howto28": dict(take="R-THROWAWAY_2", title="DESACTIVAR CLIENTE",
   segs=[[0.8, 2.6, 1.5], [2.6, 10.8, 2.0], [23.0, 25.0, 1.0], [25.0, 35.4, 2.5], [35.4, 40.0, 1.6], [45.5, 48.0, 1.2],
         [48.0, 54.5, 3.0], [54.5, 59.5, 1.0]],
   vo=[(("o", 1.7), "Entrenadores personales, ¿su cliente terminó con ustedes?"), (3.0, "Abran su perfil, toquen el menú y luego Desactivar cliente."),
       (46.0, "Deja de contar en su plan de inmediato."), (54.4, "Y pasa a la pestaña Desactivados.")],
   note=("Mostrar menú", "toquen"), chime=54.8),
})
# help videos 16 to 22 Nov: es lines translated from the approved English narration (same source as the pt lines),
# button names as the es app shows them. Series bar "TUTORIAL | <title>", navy like the English.
HELP = {
 "help01": dict(day=20, take="H01", title="SU PANTALLA DE INICIO", voice="Sadachbia", music="prettyjohn1-hip-hop-hip-hop-beat-525029.mp3",
   cover_txt=("Todo su día", "en una sola pantalla.", "hoy"),
   segs=[[1.0, 16.5, 1.38], [16.5, 21.0, 1.5], [21.0, 35.5, 5.0], [35.5, 42.5, 2.0], [42.5, 55.0, 4.0], [55.0, 73.8, 3.0],
         [73.8, 90.5, 2.6], [90.5, 99.0, 1.5]],
   vo=[(("o", 1.7), "Entrenadores personales, la pantalla de inicio les muestra todo su día de entrenamientos en cuanto abren la app."),
       (3.0, "Cuando un cliente les escribe, aparece hasta arriba, para que nunca dejen a nadie esperando."),
       (16.6, "Hoy tiene cada sesión de su agenda, y sus recordatorios están a un toque."),
       (57.5, "Seguimiento les muestra quién faltó a una rutina, para que nadie se quede atrás."),
       (73.7, "Y Actividad reciente muestra lo que andan haciendo sus clientes.")],
   note=("Recordatorios de hoy", "toquen"), chime=92.0),
 "help03": dict(day=21, take="H03", title="ARMAR UNA RUTINA", voice="Orus", music="soundsurfer-hip-hop-beats-592991.mp3",
   cover_txt=("Armen una rutina", "para cualquier cliente.", "armen"),
   # time wheel 46.5 to 89.6 s cut (12:03 a. m. and night rows); the Más usados chips ignored taps in the take, so the chip
   # row is shown and the add comes through search (dead taps 128 to 176 s cut)
   segs=[[3.0, 7.3, 1.6], [7.3, 20.8, 3.6], [20.8, 46.3, 5.0], [89.8, 122.5, 8.0], [122.5, 135.5, 2.5], [176.5, 206.0, 5.0],
         [206.0, 249.0, 4.0], [249.0, 272.0, 5.0], [272.0, 396.0, 16.0], [396.0, 409.6, 3.0], [409.6, 414.0, 1.0]],
   vo=[(("o", 1.7), "Entrenadores personales, así se arma una rutina para su cliente."),
       (6.0, "Abran al cliente, toquen Agregar rutina y luego Armar rutina desde cero."),
       (30.0, "Elijan el día y la hora, pónganle un título y toquen Agregar."),
       (122.6, "Toquen un ejercicio de los más usados, o busquen en toda la biblioteca."),
       (206.0, "Escriban el peso y las repeticiones, y ven lo que levantó la última vez."),
       (249.5, "Copiar la última copia la serie en un toque."),
       (272.5, "Agreguen el resto igual, toquen atrás y ya está en su agenda.")],
   note=("Armar rutina desde cero", "toquen"), chime=410.0),
 "help05": dict(day=22, take="H05", title="RUTINA POR CORREO", voice="Aoede", music="soundsurfer-hip-hop-beats-592991.mp3",
   cover_txt=("Manden la rutina", "por correo.", "PDF"),
   segs=[[5.0, 9.5, 1.5], [9.5, 12.0, 1.5], [12.0, 26.0, 5.0], [26.0, 30.0, 1.5], [47.0, 49.5, 1.0], [49.5, 60.8, 2.2], [60.8, 73.5, 3.5],
         [73.5, 79.0, 1.2], [91.5, 98.5, 2.2], [98.5, 112.5, 4.0], [118.2, 140.0, 4.0], [140.0, 150.0, 3.0]],
   vo=[(("o", 1.7), "Entrenadores personales, ¿quieren que su cliente tenga su rutina antes de llegar?"),
       (9.5, "Solo mándensela por correo."), (18.0, "¿Ven los colores de sus superseries?"), (26.5, "Se van con la rutina."),
       (47.3, "Toquen el menú y luego Enviar al cliente."), (68.0, "Toquen Enviar, y le llega a su correo con el PDF adjunto."),
       (91.6, "¿Quieren una copia para ustedes?"), (96.0, "Toquen Exportar PDF, luego Vista Previa, y listo."),
       (138.0, "Con los colores y todo.")],
   note=("Enviar al cliente", "toquen"), chime=77.0),
 "help06": dict(day=18, take="H06", title="SU PROPIO EJERCICIO", voice="Algenib", music="prettyjohn1-hip-hop-hip-hop-beat-525029.mp3",
   cover_txt=("Agreguen su", "propio ejercicio.", "video"),
   segs=[[2.0, 6.0, 1.5], [6.0, 17.0, 2.5], [17.0, 27.0, 2.5], [27.0, 38.0, 3.0], [38.0, 61.5, 6.0], [61.5, 63.0, 1.0], [77.5, 124.5, 7.0],
         [124.5, 135.7, 2.0], [135.7, 163.5, 6.0], [163.5, 183.0, 4.0], [183.0, 201.3, 4.0], [201.3, 212.0, 1.3]],
   vo=[(("o", 1.7), "Entrenadores personales, ¿tienen un movimiento que no está en la biblioteca?"), (3.5, "Agréguenlo ustedes, con su propio video."),
       (5.0, "Toquen Agregar ejercicio, luego Míos y Agregar ejercicio personalizado."),
       (37.3, "Pónganle nombre y elijan cómo se registra."), (89.3, "Luego la categoría, el músculo y el equipo."),
       (124.5, "¿Tienen un video en YouTube?"), (127.0, "Peguen el link aquí, o toquen Agregar un video o foto y elijan un clip del celular."),
       (180.0, "Toquen Agregar, y ya está en su biblioteca."), (200.5, "Ábranlo, y ahí está su video, corriendo dentro de la app.")],
   note=("357 170 Míos", "toquen"), chime=201.0),
 "help07": dict(day=17, take="H07", title="PROGRESO DEL CLIENTE", voice="Aoede", music="soundsurfer-hip-hop-beats-592991.mp3",
   cover_txt=("Sigan el progreso", "de su cliente.", "trofeo"),
   segs=[[2.0, 7.0, 1.5], [7.0, 16.6, 2.5], [16.6, 23.0, 2.2], [23.0, 53.0, 5.0], [53.0, 57.0, 1.0], [57.0, 69.0, 2.5], [69.0, 78.4, 2.2],
         [78.4, 85.4, 1.6], [85.4, 91.0, 1.6], [91.0, 101.6, 2.0], [101.6, 107.0, 1.5], [114.5, 117.5, 1.0]],
   vo=[(("o", 1.7), "Entrenadores personales, ¿quieren la prueba de que su cliente se está haciendo más fuerte?"), (4.0, "Todo está en su historial."),
       (7.0, "Abran al cliente y toquen Historial para ver sus rutinas anteriores."), (50.0, "¿Ven el trofeo?"), (53.1, "Es un nuevo récord personal."),
       (57.0, "Abran la rutina, toquen el menú de un ejercicio y luego Detalles."),
       (79.0, "Máximo actual es el peso más alto que ha levantado, y Tendencia muestra el cambio desde la última vez."),
       (86.0, "La gráfica muestra cada sesión, para que vean cómo sube el peso."),
       (91.0, "Bajen para ver cada vez que lo hizo, y toquen una para ver las series.")],
   note=("Historial", "toquen"), chime=115.0),
 "help09": dict(day=19, take=[("H09_T", 0.0), ("H09_L3", 189.4)], title="HÁBITOS DIARIOS", voice="Laomedeia",
   music="prettyjohn1-hip-hop-hip-hop-beat-525029.mp3", cover="H09_T/stills/cover.png",
   cover_txt=("Hábitos diarios", "para sus clientes.", "hábitos"),
   # the starter list's "Acostarse antes de las 11 pm" is app wording: blurred like pt's 23h row
   ocr_extra=[("H09_T", r"11 ?pm|Acostarse|antes", 34.0, 53.0)],
   segs=[[0.5, 8.5, 0.667], [189.9, 198.4, 1.7], [8.8, 17.0, 2.1], [17.0, 52.8, 5.7], [52.8, 96.0, 8.0], [96.0, 120.0, 4.0],
         [120.0, 142.0, 4.4], [142.0, 163.0, 4.4], [163.0, 180.0, 2.8]],
   vo=[(("o", 1.7), "Entrenadores personales, con los hábitos ayudan a sus clientes a crear buenos hábitos y siguen todo, todos los días."),
       (4.0, "Un hábito es una pequeña meta diaria, como tomar 8 vasos de agua o caminar."),
       (190.0, "Su cliente ve sus hábitos todos los días en su app y los marca cuando los cumple."),
       (9.0, "Para agregar uno, abran al cliente y toquen Hábitos."),
       (17.2, "Toquen Agregar y elijan un hábito de la lista, o creen el suyo."),
       (55.5, "Elijan un ícono y un recordatorio, si quieren que su celular le avise."),
       (96.3, "Conforme lo marca, ven cómo va su semana justo aquí."),
       (121.0, "Si falla 3 días seguidos, aparece en Seguimiento en su pantalla de inicio."),
       (142.5, "¿Va bien? Toquen Buen trabajo, porque lo que hace entre sesiones importa tanto como la sesión.")],
   note=("Hábitos", "toquen"), chime=168.2),
 "help08": dict(day=16, take="H08/phone", title="PLANEEN EN LA LAPTOP", voice="Orus", music="soundsurfer-hip-hop-beats-592991.mp3",
   cover_txt=("Planeen en", "su laptop.", "más rápido"),
   # web take starts on Inicio with the live line "Ahora, 12:34 a. m." until the Calendario click at 9.0 s: web part starts at 9.4 s
   web_segs=[[9.4, 17.0, 3.0], [17.0, 22.4, 2.4], [22.4, 27.4, 2.4], [27.4, 37.2, 3.0], [37.2, 53.3, 5.6], [53.3, 64.0, 4.0], [64.0, 70.8, 2.4],
             [70.8, 76.0, 2.4], [76.0, 104.0, 8.0], [104.0, 131.0, 8.0], [131.0, 145.0, 4.0], [145.0, 250.0, 16.0], [250.0, 266.0, 4.0], [266.0, 276.0, 3.0]],
   phone_segs=[[2.5, 11.0, 3.0], [11.0, 40.3, 8.0], [40.3, 44.5, 1.0]],
   vo=[(("o", 1.7), "Entrenadores personales, ¿van a escribir las rutinas de la próxima semana? Es más rápido en la laptop."),
       (("w", 9.5), "Abran el Calendario, den clic en un día y luego en Agregar rutina."),
       (("w", 31.6), "Elijan al cliente, pónganle un título, y ya está en su calendario."),
       (("w", 70.8), "Ábranla, escriban un ejercicio y presionen Enter."),
       (("w", 104.0), "Escriban el peso y las repeticiones, y Copiar la última llena las siguientes series."),
       (("w", 143.0), "Den clic en Guardar, y pasan al siguiente ejercicio."),
       (("w", 160.0), "La última rutina de su cliente queda justo al lado, para que sepan dónde se quedó."),
       (("p", 2.5), "Y cuando toman el celular, ya está ahí.")]),
}
for k, it in HELP.items(): it.setdefault("help", True)
HOWTO.update(HELP)
MUSIC = "/mnt/user-data/uploads/TTN Reels/03 Music/All platforms/"

def redact_boxes(hits, W, H_, pad=0.5, gap=16.0, hmul=2.6):
    """OCR hits -> blur boxes [t0, t1, x, y, w, h]: each hit +-pad, same spot bridged over gaps (dimmed dialogs), moves covered"""
    hits = sorted(hits); boxes = []
    def box(h): x, y, w, hh = h[1] - 8, h[2] - 8, h[3] + 16, h[4] * hmul + 16; return [x, y, w, hh]
    groups = {}
    for h in hits:
        k = None
        for g in groups:
            if abs(g[0] - h[1]) < 14 and abs(g[1] - h[2]) < 14: k = g; break
        groups.setdefault(k or (h[1], h[2]), []).append(h)
    for g, hs in groups.items():
        cur = None
        for h in hs:
            b = box(h)
            if cur and h[0] - cur[1] <= gap:
                cur[1] = h[0] + pad; x0 = min(cur[2], b[0]); y0 = min(cur[3], b[1]); x1 = max(cur[2] + cur[4], b[0] + b[2]); y1 = max(cur[3] + cur[5], b[1] + b[3])
                cur[2:] = [x0, y0, x1 - x0, y1 - y0]
            else:
                if cur: boxes.append(cur)
                cur = [h[0] - pad, h[0] + pad] + b
        if cur: boxes.append(cur)
    def at(t, h): return any(abs(x[0] - t) < 1e-3 and abs(x[1] - h[1]) < 14 and abs(x[2] - h[2]) < 14 for x in hits)
    for h1, h2 in zip(hits, hits[1:]):  # text moving between two samples (gone from its old spot): cover the union
        if 0 < h2[0] - h1[0] <= 0.6 and (abs(h1[1] - h2[1]) >= 14 or abs(h1[2] - h2[2]) >= 14) and not at(h2[0], h1) and not at(h1[0], h2):
            b1, b2 = box(h1), box(h2); x0 = min(b1[0], b2[0]); y0 = min(b1[1], b2[1])
            boxes.append([h1[0] - 0.1, h2[0] + 0.1, x0, y0, max(b1[0] + b1[2], b2[0] + b2[2]) - x0, max(b1[1] + b1[3], b2[1] + b2[3]) - y0])
    out = []
    for t0, t1, x, y, w, h in boxes:
        x, y = max(0, int(x)), max(0, int(y)); w, h = int(min(w, W - x)), int(min(h, H_ - y))
        out.append([round(t0, 2), round(t1, 2), x, y, w - w % 2, h - h % 2])
    return out

def apply_redact(src, boxes, out):
    if not boxes: return src
    import hashlib
    out = out.replace(".mp4", "_" + hashlib.md5((src + json.dumps(boxes)).encode()).hexdigest()[:8] + ".mp4")
    if os.path.exists(out): return out
    n = len(boxes); g = [f"[0:v]split={n + 1}[base]" + "".join(f"[c{i}]" for i in range(n))]
    cur = "base"
    for i, (t0, t1, x, y, w, h) in enumerate(boxes):
        g.append(f"[c{i}]crop={w}:{h}:{x}:{y},gblur=sigma=14:steps=3[k{i}]")
        g.append(f"[{cur}][k{i}]overlay={x}:{y}:enable='between(t,{t0},{t1})'[o{i}]"); cur = f"o{i}"
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", src, "-filter_complex", ";".join(g), "-map", f"[{cur}]", "-an",
                    "-c:v", "libx264", "-crf", "14", "-preset", "veryfast", "-r", "30", out], check=True)
    return out

def take_proxy(item, it):
    """the take proxy (two takes joined if needed) with every e-mail address and any extra pattern blurred"""
    tk = takes_of(it); os.makedirs(f"{OUT}/proxy", exist_ok=True)
    if len(tk) == 1: src = NT + tk[0][0] + "/take_p6.mp4"
    else:
        src = f"{OUT}/proxy/{item}_joined.mp4"
        if not os.path.exists(src):
            ins = sum((["-i", NT + t + "/take_p6.mp4"] for t, _ in tk), [])
            subprocess.run(["ffmpeg", "-v", "error", "-y", *ins, "-filter_complex", "".join(f"[{i}:v]" for i in range(len(tk))) + f"concat=n={len(tk)}:v=1:a=0[v]",
                            "-map", "[v]", "-c:v", "libx264", "-crf", "14", "-preset", "fast", "-r", "30", src], check=True)
    hits = []
    for t, off in tk:
        f = f"/home/claude/loc/ocr_es/{t.replace('/', '_')}.json"
        if not os.path.exists(f): raise SystemExit(f"OCR scan missing for {t}: run es2_ocr.py {t} 2")
        hits += [[h[0] + off] + h[1:] for h in json.load(open(f))]
    for t, pat, t0, t1 in it.get("ocr_extra", []):
        off = dict(tk)[t]
        ex = pt2_ocr.scan(NT + t + "/take_p6.mp4", 4, pat, t0, t1, 2, f"{t.replace('/', '_')}_extra_{t0}")
        # es: widen each hit to the end of its row so "Acostarse antes de las 11 pm" is blurred whole (tesseract splits the words)
        hits += [[h[0] + off, h[1], h[2], max(h[3], 580 - h[1]), h[4], h[5], "extra"] for h in ex]
    hits = [h for h in hits if re.search(r"@|\+|support", h[5], re.I) or len(h) > 6]
    boxes = redact_boxes(hits, 600, 1304)
    json.dump(boxes, open(f"{OUT}/proxy/{item}_boxes.json", "w"))
    return apply_redact(src, boxes, f"{OUT}/proxy/{item}_redacted.mp4"), boxes

def redact_png(src, out):
    """blur every e-mail address OCR finds in a still"""
    im = Image.open(src).convert("RGB"); hits = pt2_ocr.scan_image(src)
    from PIL import ImageFilter
    for x, y, w, h, _ in hits:
        x0, y0, x1, y1 = max(0, x - 16), max(0, y - 16), min(im.width, x + w + 16), min(im.height, int(y + h * 2.6 + 16))
        im.paste(im.crop((x0, y0, x1, y1)).filter(ImageFilter.GaussianBlur(28)), (x0, y0))
    im.save(out); return out, len(hits)

def cover_howto(item, it, old):
    if it.get("help"):
        l1, l2, note = it["cover_txt"]
        spec = {"bg": "navy", "kind": "reel", "series": "TUTORIAL", "l1": l1, "l2": l2, "note": {"text": note, "pos": "left:40px;top:720px"}}
    else:
        spec = json.load(open(f"{V}/cfg/coverspec_{item}_es.json"))
    src = NT + it.get("cover", takes_of(it)[0][0] + "/stills/cover.png")
    os.makedirs(f"{OUT}/proxy", exist_ok=True); red, n = redact_png(src, f"{OUT}/proxy/{item}_cover_still.png")
    im = Image.open(red).convert("RGB")
    a = f"_loc_{item}_es_v2.png"; lum = np.asarray(im.convert("L")).mean()
    if it.get("wide_cover"):  # laptop still: draw it on a laptop as the cover photo
        ph = laptop_photo(im); ph.save(f"{TPL}/assets/{a}"); spec.pop("note", None)
        spec.update({"photo": a, "ph": ph.height, "kicker": it["cover_txt"][2], "label": "TUTORIAL"})
    else:
        im.resize((560, round(560 * im.height / im.width)), Image.LANCZOS).save(f"{TPL}/assets/{a}")
        spec["screen"] = a
        if not it.get("help"): spec["bg"] = "paper" if lum < 110 else "navy"
        else: spec["bg"] = "paper" if lum < 110 else "navy"
    sp = f"{V}/cfg/coverspec_{item}_es_v2.json"; json.dump(spec, open(sp, "w"), ensure_ascii=False)
    out = f"{V}/cfg/cover_{item}_es_v2.png"
    subprocess.run(["python3", f"{TPL}/render_cover.py", sp, out], check=True, capture_output=True, cwd=TPL)
    return out

# ---- help08: laptop part (web take, full size file) then phone part, composed full frame
LAP = (40, 700, 1000, 624)  # screen x, y, w, h in the 1080x1920 frame
def laptop_png(path, bg=reel2.NAVY):
    im = Image.new("RGBA", (1080, 1920), (0, 0, 0, 0)); d = ImageDraw.Draw(im); x, y, w, h = LAP
    d.rounded_rectangle((x - 18, y - 18, x + w + 18, y + h + 18), 28, fill=(10, 10, 11, 255), outline=(58, 63, 74, 255), width=5)
    d.rounded_rectangle((x - 60, y + h + 18, x + w + 60, y + h + 46), 12, fill=(58, 63, 74, 255))
    d.rectangle((x + w // 2 - 70, y + h + 18, x + w // 2 + 70, y + h + 26), fill=(40, 44, 52, 255))
    im.save(path); return path

def laptop_photo(still):
    ph = Image.new("RGB", (1080, 1000), reel2.NAVY); lp = Image.open(laptop_png("/tmp/_lap.png")).crop((0, 600, 1080, 1600))
    ph.paste(lp, (0, 0), lp); x, y, w, h = LAP; ph.paste(still.resize((w, h), Image.LANCZOS), (x, y - 600)); return ph

def web_taps():
    J = json.load(open(NT + "H08/web/take_taplog.json"))
    return [(e["done_t"], e["label"]) for e in J["taps"] if e["kind"] in ("click", "key") and (e["kind"] == "click" or e["label"] == "Enter")]

def compose_help08(it):
    wd = f"{OUT}/proxy/help08"; os.makedirs(wd, exist_ok=True)
    web = NT + "H08/web/take_cfr60.mp4"; webp = f"{wd}/web_1000.mp4"
    if not os.path.exists(webp):
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", web, "-vf", "fps=30,scale=1000:624:flags=lanczos", "-an", "-c:v", "libx264", "-crf", "14", "-preset", "fast", webp], check=True)
    # blur anything the OCR finds on the web take (addresses, the untranslated "Copy of" recent title chip)
    hits = pt2_ocr.scan(web, 1, pt2_ocr.EMAIL + r"|Copy|of Cuerpo", 0, 276, 1, "H08_web_full")
    sc = 1000 / 2880; hits = [[h[0], h[1] * sc, h[2] * sc, (max(h[3], 330) if "Copy" in h[5] else h[3]) * sc, h[4] * sc, h[5]] for h in hits]  # widen "Copy" to the whole "Copy of ..." chip
    boxes = redact_boxes(hits, 1000, 624, pad=1.0, hmul=1.6); webr = apply_redact(webp, boxes, f"{wd}/web_red.mp4")
    phone, pboxes = take_proxy("help08", it)
    lap = laptop_png(f"{wd}/laptop.png"); reel2.PW, reel2.SW = 640, 600; sh_h = reel2.phone_pngs(wd)
    def piece(src, segs, kind, out):
        ins = []; g = []
        for i, (a, b, s) in enumerate(segs): ins += ["-ss", str(a), "-t", str(b - a), "-i", src]; g.append(f"[{i}:v]setpts=(PTS-STARTPTS)/{s},fps=30[s{i}]")
        n = len(segs); g.append("".join(f"[s{i}]" for i in range(n)) + f"concat=n={n}:v=1:a=0[c]")
        ins += ["-f", "lavfi", "-i", "color=c=0x0B0F19:s=1080x1920:r=30"]
        if kind == "web":
            ins += ["-loop", "1", "-i", lap]; x, y, w, h = LAP
            g.append(f"[{n}:v][{n + 1}:v]overlay=0:0[bg];[bg][c]overlay={x}:{y}:shortest=1[v]")
        else:
            ins += ["-loop", "1", "-i", f"{wd}/bezel.png", "-loop", "1", "-i", f"{wd}/mask.png"]
            g.append(f"[c]scale=600:{sh_h},format=yuva420p[ca];[{n + 2}:v]format=gray[m];[ca][m]alphamerge[cm];[{n}:v][{n + 1}:v]overlay=190:590[bg];[bg][cm]overlay=240:610:shortest=1[v]")
        D = sum((b - a) / s for a, b, s in segs)
        subprocess.run(["ffmpeg", "-v", "error", "-y", *ins, "-filter_complex", ";".join(g), "-map", "[v]", "-t", f"{D:.3f}", "-c:v", "libx264", "-crf", "15", "-preset", "fast", "-pix_fmt", "yuv420p", out], check=True)
        return out
    a = piece(webr, it["web_segs"], "web", f"{wd}/part_web.mp4"); b = piece(phone, it["phone_segs"], "phone", f"{wd}/part_phone.mp4")
    full = f"{wd}/full.mp4"
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", a, "-i", b, "-filter_complex", "[0:v][1:v]concat=n=2:v=1:a=0[v]", "-map", "[v]",
                    "-c:v", "libx264", "-crf", "15", "-preset", "fast", "-pix_fmt", "yuv420p", full], check=True)
    return full, dur(a), boxes, pboxes

def make_howto(item):
    it = HOWTO[item]; old = None if it.get("help") else json.load(open(f"{V}/cfg/{item}_es.json"))
    bg = "navy" if it.get("help") else old["bg"]
    C = {"name": f"{item}_es_v2", "bg": bg, "hook_secs": H,
         "series": "TUTORIAL" if it.get("help") else old["series"], "title": it["title"],
         "voice": it["voice"] if it.get("help") else old["voice"], "music": MUSIC + it["music"] if it.get("help") else old["music"], "lang": LANG,
         "end_vo": END_VO, "end_card": f"{V}/endcard_es.png", "out": f"{OUT}/{item}_es_v2.mp4",
         "end_secs": 3.6 if it.get("help") else old.get("end_secs", 3.6), "cap_gap": 0.07}
    if item == "help08":
        full, wdur, boxes, pboxes = compose_help08(it); D = dur(full)
        segs = [[0.0, round(D, 3), 1.0]]; C.update({"src": full, "proxy": full, "segs": segs, "full": True})
        wmap = lambda t: omap(it["web_segs"], t); pmap = lambda t: wdur + omap(it["phone_segs"], t)
        def anchor(a): return a[1] if a[0] == "o" else (wmap(a[1]) if a[0] == "w" else pmap(a[1]))
        C["vo"] = [[round(anchor(a), 2), text] for a, text in it["vo"]]
        sfx = [[round(wmap(t), 2), "tap"] for t, lab in web_taps() if any(a <= t <= b for a, b, s in it["web_segs"])]
        sfx += [[round(pmap(t), 2), "tap"] for t, lab, x, y in taps("H08/phone") if any(a <= t <= b for a, b, s in it["phone_segs"])]
        sfx = [x for i, x in enumerate(sfx) if i == 0 or x[0] - sfx[i - 1][0] > 0.3]
        C["sfx"] = sfx + [[round(pmap(43.6), 2), "chime"]]; C["notes"] = []
        it["wide_cover"] = True; it["cover"] = "H08/web/stills/cover.png"
        C["redact_boxes"] = len(boxes) + len(pboxes)
    else:
        segs = [list(s) for s in it["segs"]]
        px, boxes = take_proxy(item, it); C.update({"src": px, "proxy": px, "segs": segs}); C["redact_boxes"] = len(boxes)
        tl = sum((taps(t, off) for t, off in takes_of(it)), [])
        C["vo"] = [[a[1] if isinstance(a, tuple) else round(omap(segs, a), 2), text] for a, text in it["vo"]]
        sfx = []; last = -9
        for t, lab, x, y in sorted(tl, key=lambda e: omap(segs, e[0])):
            if any(a <= t <= b for a, b, s in segs):
                o = omap(segs, t)
                if o - last > 0.3: sfx.append([round(o, 2), "tap"]); last = o
        sfx.append([round(omap(segs, it["chime"]), 2), "chime"]); C["sfx"] = sfx; C["notes"] = []
        if it.get("note"):
            lab, word = it["note"]; hit = [e for e in tl if e[1] == lab and any(a <= e[0] <= b for a, b, s in segs)]
            t, _, x, y = hit[0]
            if x is None: x, y = map(float, lab.split()[:2])
            tx, ty = to_out_xy(x, y); side, nx, ny = note_place(word, tx, ty, bg); o = omap(segs, t)
            C["notes"] = [[round(max(H + 0.2, o - 1.4), 2), round(o + 0.15, 2), word, nx, ny, side]]
    C["cover"] = cover_howto(item, it, old)
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
    old = json.load(open(f"{V}/cfg/{item}_es.json")); C = json.loads(json.dumps(old))
    C["name"] = f"{item}_es_v2"; C["out"] = f"{OUT}/{item}_es_v2.mp4"; C["cover"] = f"{V}/cfg/cover_{item}_es.png"; C["cap_gap"] = 0.07
    C["phone"]["screens"] = [[t, ST + SCREEN[os.path.basename(p)] + ".png"] for t, p in old["phone"]["screens"]]
    fx = PEOPLE_FIX.get(item, {})
    for i, t in fx.get("vo", {}).items(): C["vo"][i][2] = t
    for i, n in enumerate(fx.get("screens", [])): C["phone"]["screens"][i][1] = ST + n + ".png"
    if fx.get("kicker"):
        spec = json.load(open(f"{V}/cfg/coverspec_{item}_es.json")); spec["kicker"] = fx["kicker"]
        sp = f"{V}/cfg/coverspec_{item}_es_v2.json"; json.dump(spec, open(sp, "w"), ensure_ascii=False)
        C["cover"] = f"{V}/cfg/cover_{item}_es_v2.png"
        subprocess.run(["python3", f"{TPL}/render_cover.py", sp, C["cover"]], check=True, capture_output=True, cwd=TPL)
    if item == "pv13":  # s13a shows Hector's phone with the English Home from 1.6 s: keep 0 to 1.5 s, raise the drawn phone at the cut
        a = "/home/claude/loc/out_es_v2/s13a_0_1.5.mp4"
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
    C = json.load(open(f"{V}/cfg/{item}_es_v2.json")); s = f"/home/claude/loc/sheets_es_v2/{item}_es_v2.jpg"; os.makedirs(os.path.dirname(s), exist_ok=True)
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
        r = subprocess.run(["python3", "-c", f"import sys; sys.path.insert(0,'{V}'); sys.path.insert(0,'{V}/loc'); import es2, {mod}; {mod}.build('{p}')"],
                           capture_output=True, text=True, cwd=V)
        print(r.stdout.strip()[-300:], r.stderr.strip()[-600:])
        print("sheet", sheet(item), "dur", round(dur(C["out"]), 2))
