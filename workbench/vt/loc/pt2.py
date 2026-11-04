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
          "wed2_chat_client.png": "chat_client", "scr_w47_sun_session_jessica.png": "session_accepted",
          "mon1_follow_up.png": "w47_mon1_follow_up", "tue1_habits_tab.png": "w47_tue1_habits_tab", "tue2_client_home.png": "client_habits",
          "thu1_sofia_workouts.png": "w47_thu1_sofia_workouts", "thu2_workout_phone.png": "w47_thu2_workout_phone",
          "scr_w47_fri_new_best.png": "newbest_client", "fri2_trophy_line.png": "w47_fri2_trophy_line",
          "sat1_colour_pick.png": "../H05/stills/w47_sat1_colour_pick", "sat2_colours_set.png": "../H05/stills/w47_sat2_colours_set"}
# line and still fixes (coordinator 2026-11-04 evening): the pt chat has no voice note; no workout still shows a trainer note,
# so pn05 shows the client's Home where the trainer's note sits on today's workout; Follow up reads "Acompanhar" in the pt app
PEOPLE_FIX = {
 "pn05": dict(vo={1: "Adicione uma nota a qualquer treino, e ela aparece bem ali no treino."}, screens=["client_nb"]),
 "pv_w47_wed": dict(vo={1: "O chat fica bem ao lado dos treinos dele."}, kicker="a conversa ao lado do treino"),
 "pv_w47_mon": dict(vo={1: "A seção Acompanhar na tela inicial mostra cada aluno que faltou, com um botão de mensagem."}, kicker="Acompanhar, na tela inicial"),
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
import pt2_ocr, re
HOWTO.update({
 "howto26": dict(take="H05", title="EXPORTAR PDF", cover="H05/stills/pdf_menu.png",
   segs=[[3.5, 9.0, 1.5], [95.5, 103.0, 1.3], [103.0, 113.5, 2.5], [113.5, 116.5, 1.5], [119.6, 134.0, 3.5]],
   vo=[(("o", 1.7), "Personal trainer, o aluno treina sozinho essa semana?"), (95.6, "Abra o treino, toque no menu e em Exportar PDF."),
       (119.6, "Envie ou imprima, e ele não fica na dúvida.")],
   note=("200 245 Exportar PDF", "toque"), chime=119.7),
 "howto27": dict(take="H03", title="MONTAR UM TREINO",
   segs=[[8.4, 14.2, 2.5], [14.2, 28.0, 4.0], [52.0, 61.0, 3.0], [86.5, 92.0, 1.5], [100.5, 130.0, 8.0], [201.5, 226.0, 6.0],
         [226.0, 256.0, 7.0], [299.0, 305.5, 2.0]],
   vo=[(("o", 1.7), "Personal trainer, montando o treino de hoje?"), (13.0, "Toque em Adicionar treino e depois em Montar treino do zero."),
       (52.0, "Defina o horário e dê um nome."), (201.6, "Busque o exercício e adicione."),
       (236.0, "Séries, repetições e carga no teclado numérico."), (299.5, "Pronto antes do aluno chegar.")],
   note=("220 709 Montar treino do zero", "toque"), chime=305.2),
 "howto28": dict(take="R-THROWAWAY_2", title="DESATIVAR ALUNO",
   segs=[[0.8, 3.8, 1.5], [3.8, 10.0, 2.0], [40.9, 44.3, 1.2], [44.3, 50.0, 2.5], [55.6, 60.5, 1.6], [69.8, 74.5, 1.2],
         [74.5, 83.6, 3.0], [83.6, 88.5, 1.0]],
   vo=[(("o", 1.7), "Personal trainer, o aluno encerrou com você?"), (4.0, "Abra o perfil dele, toque no menu e depois em Desativar aluno."),
       (70.6, "Ele para de contar no seu plano na hora."), (83.7, "E vai para a aba Desativados.")],
   note=("Mostrar menu", "toque"), chime=84.0),
})
# help videos 16 to 22 Nov: pt lines translated from the approved English narration (transcribed from posts/*-howto-help*/video.mp4),
# button names as the pt app shows them. Series bar "TUTORIAL | <title>", navy like the English.
HELP = {
 "help01": dict(day=20, take="H01", title="SUA TELA INICIAL", voice="Sadachbia", music="prettyjohn1-hip-hop-hip-hop-beat-525029.mp3",
   cover_txt=("Todo o seu dia", "numa tela só.", "hoje"),
   segs=[[1.0, 16.5, 1.38], [16.5, 29.0, 3.0], [38.5, 47.6, 2.07], [47.6, 57.0, 2.6], [57.0, 63.5, 1.5]],
   vo=[(("o", 1.7), "Personal trainer, a tela inicial mostra todo o seu dia de treinos assim que você abre o app."),
       (3.0, "Quando um aluno te manda mensagem, aparece bem no topo, para você nunca deixar ninguém esperando."),
       (16.6, "Hoje tem cada sessão da sua agenda, e os seus lembretes estão a um toque."),
       (40.0, "Acompanhar mostra quem faltou a um treino, para ninguém ficar para trás."),
       (47.5, "E a Atividade recente mostra o que os seus alunos andam fazendo.")],
   note=("Lembretes de hoje", "toque"), chime=57.2),
 "help03": dict(day=21, take="H03", title="MONTAR UM TREINO", voice="Orus", music="soundsurfer-hip-hop-beats-592991.mp3",
   cover_txt=("Monte um treino", "para qualquer aluno.", "monte"),
   segs=[[3.0, 8.4, 1.6], [8.4, 28.0, 3.6], [28.0, 61.0, 5.0], [86.5, 130.0, 10.0], [130.0, 154.0, 5.0], [154.0, 176.0, 4.0],
         [176.0, 201.5, 6.0], [201.5, 299.0, 16.0], [299.0, 305.5, 2.0], [305.5, 310.0, 1.0]],
   vo=[(("o", 1.7), "Personal trainer, veja como montar um treino para o aluno."),
       (6.0, "Abra o aluno, toque em Adicionar treino e depois em Montar treino do zero."),
       (40.0, "Escolha o dia e o horário, dê um título e toque em Adicionar."),
       (130.5, "Toque num exercício dos Mais usados, ou busque na biblioteca toda."),
       (154.0, "Digite a carga e as repetições, e você vê o que ele levantou da última vez."),
       (176.0, "Copiar última copia a série num toque."),
       (201.0, "Adicione o resto do mesmo jeito, toque em voltar e já está na agenda dele.")],
   note=("220 709 Montar treino do zero", "toque"), chime=305.2),
 "help05": dict(day=22, take="H05", title="TREINO POR EMAIL", voice="Aoede", music="soundsurfer-hip-hop-beats-592991.mp3",
   cover_txt=("Envie o treino", "por email.", "PDF"),
   segs=[[6.0, 9.5, 1.5], [9.5, 12.0, 1.5], [12.0, 36.0, 5.0], [36.0, 40.0, 1.5], [61.5, 64.0, 1.0], [64.0, 71.5, 2.2], [71.5, 80.0, 3.5],
         [80.0, 85.0, 1.2], [95.5, 103.0, 2.2], [103.0, 113.5, 4.0], [113.5, 116.5, 2.0], [119.6, 129.0, 3.5], [129.0, 137.0, 3.0]],
   vo=[(("o", 1.7), "Personal trainer, quer que o aluno receba o treino antes mesmo de chegar?"),
       (9.5, "É só mandar por email."), (24.0, "Vê as cores dos seus bi-sets?"), (36.0, "Elas vão junto."),
       (61.5, "Toque no menu e depois em Enviar ao cliente."), (78.0, "Toque em Enviar, e chega no email dele com o PDF anexado."),
       (95.5, "Quer uma cópia para você?"), (100.0, "Toque em Exportar PDF, depois em Pré-Visualização, e pronto."),
       (128.0, "Com as cores e tudo.")],
   note=("250 292 Enviar ao cliente", "toque"), chime=84.0),
 "help06": dict(day=18, take="H06", title="SEU PRÓPRIO EXERCÍCIO", voice="Algenib", music="prettyjohn1-hip-hop-hip-hop-beat-525029.mp3",
   cover_txt=("Adicione o seu", "próprio exercício.", "vídeo"),
   segs=[[2.0, 5.8, 1.5], [5.8, 11.0, 1.5], [11.0, 20.3, 2.5], [20.3, 32.5, 4.0], [32.5, 48.6, 6.0], [48.6, 64.0, 4.0], [64.0, 95.5, 7.0],
         [95.5, 103.3, 1.8], [103.3, 112.0, 2.5], [112.0, 135.0, 6.0], [135.0, 149.0, 4.0], [149.0, 164.5, 4.0], [164.5, 174.0, 1.3]],
   vo=[(("o", 1.7), "Personal trainer, tem um exercício que não está na biblioteca?"), (3.5, "Adicione você mesmo, com o seu próprio vídeo."),
       (5.0, "Toque em Adicionar exercício, depois em Meus e em Adicionar exercício personalizado."),
       (32.3, "Dê um nome e escolha o que você registra."), (64.0, "Depois a categoria, o músculo e o equipamento."),
       (95.5, "Tem um vídeo no YouTube?"), (100.0, "Cole o link aqui, ou toque em Adicionar um vídeo ou foto e escolha um clipe do celular."),
       (146.0, "Toque em Adicionar, e ele já está na sua biblioteca."), (164.0, "Abra, e lá está o seu vídeo, rodando dentro do app.")],
   note=("357 172 Meus", "toque"), chime=164.3),
 "help07": dict(day=17, take="H07", title="PROGRESSO DO ALUNO", voice="Aoede", music="soundsurfer-hip-hop-beats-592991.mp3",
   cover_txt=("Acompanhe a", "evolução do aluno.", "troféu"),
   segs=[[2.0, 6.6, 1.5], [6.6, 12.2, 1.8], [12.2, 19.4, 2.2], [19.4, 42.5, 4.5], [42.5, 46.0, 1.0], [46.0, 56.2, 2.5], [56.2, 65.4, 2.2],
         [65.4, 72.5, 1.6], [72.5, 78.0, 1.6], [78.0, 84.3, 1.8], [84.3, 90.0, 1.5], [96.5, 99.5, 1.0]],
   vo=[(("o", 1.7), "Personal trainer, quer a prova de que o aluno está ficando mais forte?"), (4.0, "Está tudo no histórico dele."),
       (6.6, "Abra o aluno e toque em Histórico para ver os treinos anteriores."), (40.0, "Vê o troféu?"), (42.6, "É um novo máximo."),
       (46.0, "Abra o treino, toque no menu de um exercício e depois em Detalhes."),
       (66.0, "Máximo atual é a maior carga que ele já levantou, e Tendência mostra a mudança desde a última vez."),
       (73.0, "O gráfico mostra cada sessão, para você ver a carga subir."),
       (78.5, "Role para ver cada vez que ele fez, e toque em uma para ver as séries.")],
   note=("Histórico", "toque"), chime=97.2),
 "help09": dict(day=19, take=[("H09_T", 0.0), ("H09_L3", 198.5333)], title="HÁBITOS DIÁRIOS", voice="Laomedeia",
   music="prettyjohn1-hip-hop-hip-hop-beat-525029.mp3", cover="H09_T/stills/cover.png",
   cover_txt=("Hábitos diários", "para os alunos.", "hábitos"),
   ocr_extra=[("H09_T", r"23h|cama|até", 24.0, 39.5)],
   segs=[[0.5, 8.5, 0.667], [199.0, 207.5, 1.7], [8.8, 17.0, 2.1], [17.0, 41.0, 5.7], [41.0, 117.2, 11.2], [117.2, 138.2, 4.0],
         [138.2, 158.0, 4.4], [158.0, 178.5, 2.8]],
   vo=[(("o", 1.7), "Personal trainer, com os hábitos, você ajuda seus alunos a criar bons hábitos e acompanha tudo, todo dia."),
       (4.0, "Um hábito é uma pequena meta diária, como beber 8 copos de água ou caminhar."),
       (199.0, "O aluno vê os hábitos todo dia no app dele e marca conforme cumpre."),
       (9.0, "Para adicionar, abra o aluno e toque em Hábitos."),
       (17.2, "Toque em Adicionar e escolha um hábito da lista, ou crie o seu."),
       (41.5, "Escolha um ícone e um horário de lembrete, se quiser que o celular dele avise."),
       (117.3, "Conforme ele marca, você vê como está a semana dele bem aqui."),
       (140.0, "Se ele falhar 3 dias seguidos, aparece em Acompanhar na sua tela inicial."),
       (160.0, "Indo bem? Toque em Bom trabalho, porque o que ele faz entre as sessões importa tanto quanto a sessão.")],
   note=("Hábitos", "toque"), chime=170.6),
 "help08": dict(day=16, take="H08/phone", title="PLANEJE NO NOTEBOOK", voice="Orus", music="soundsurfer-hip-hop-beats-592991.mp3",
   cover_txt=("Planeje no", "seu notebook.", "mais rápido"),
   web_segs=[[0.5, 4.5, 2.4], [4.5, 12.0, 4.0], [12.0, 17.5, 2.4], [17.5, 34.0, 8.0], [34.0, 40.0, 2.4], [40.0, 56.0, 5.6], [56.0, 62.0, 2.4], [62.0, 77.0, 6.4], [77.0, 86.5, 4.0], [86.5, 95.0, 3.2], [95.0, 116.0, 8.0], [116.0, 127.0, 4.0], [127.0, 137.0, 3.2], [137.0, 196.0, 14.4], [196.0, 212.5, 6.4]],
   phone_segs=[[3.0, 16.0, 4.0], [16.0, 40.5, 8.0], [40.5, 44.5, 1.0]],
   vo=[(("o", 1.7), "Personal trainer, vai escrever os treinos da próxima semana? É mais rápido no notebook."),
       (("w", 4.5), "Abra a Agenda, clique num dia e depois em Adicionar treino."),
       (("w", 40.0), "Escolha o aluno, dê um título, e já está na agenda dele."),
       (("w", 86.5), "Abra, digite um exercício e aperte Enter."),
       (("w", 115.5), "Digite a carga e as repetições, e Copiar última preenche as próximas séries."),
       (("w", 126.0), "Aperte Enter para salvar, e você já passa para o próximo exercício."),
       (("w", 160.0), "O último treino do aluno fica bem ao lado, para você saber onde ele parou."),
       (("p", 3.0), "E quando você pega o celular, já está lá.")]),
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
        f = f"/home/claude/loc/ocr/{t.replace('/', '_')}.json"
        if not os.path.exists(f): raise SystemExit(f"OCR scan missing for {t}: run pt2_ocr.py {t} 2")
        hits += [[h[0] + off] + h[1:] for h in json.load(open(f))]
    for t, pat, t0, t1 in it.get("ocr_extra", []):
        off = dict(tk)[t]
        hits += [[h[0] + off] + h[1:] + ["extra"] for h in pt2_ocr.scan(NT + t + "/take_p6.mp4", 4, pat, t0, t1, 2, f"{t.replace('/', '_')}_extra_{t0}")]
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
        spec = json.load(open(f"{V}/cfg/coverspec_{item}_pt.json"))
    src = NT + it.get("cover", takes_of(it)[0][0] + "/stills/cover.png")
    os.makedirs(f"{OUT}/proxy", exist_ok=True); red, n = redact_png(src, f"{OUT}/proxy/{item}_cover_still.png")
    im = Image.open(red).convert("RGB")
    a = f"_loc_{item}_v2.png"; lum = np.asarray(im.convert("L")).mean()
    if it.get("wide_cover"):  # laptop still: draw it on a laptop as the cover photo
        ph = laptop_photo(im); ph.save(f"{TPL}/assets/{a}"); spec.pop("note", None)
        spec.update({"photo": a, "ph": ph.height, "kicker": it["cover_txt"][2], "label": "TUTORIAL"})
    else:
        im.resize((560, round(560 * im.height / im.width)), Image.LANCZOS).save(f"{TPL}/assets/{a}")
        spec["screen"] = a
        if not it.get("help"): spec["bg"] = "paper" if lum < 110 else "navy"
        else: spec["bg"] = "paper" if lum < 110 else "navy"
    sp = f"{V}/cfg/coverspec_{item}_pt_v2.json"; json.dump(spec, open(sp, "w"), ensure_ascii=False)
    out = f"{V}/cfg/cover_{item}_pt_v2.png"
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
    hits = pt2_ocr.scan(web, 1, pt2_ocr.EMAIL + r"|Copy|of Treino", 0, 234, 1, "H08_web_full")
    sc = 1000 / 2880; hits = [[h[0], h[1] * sc, h[2] * sc, (max(h[3], 330) if "Copy" in h[5] else h[3]) * sc, h[4] * sc, h[5]] for h in hits]  # widen "Copy" to the whole "Copy of Treino Completo" chip
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
    it = HOWTO[item]; old = None if it.get("help") else json.load(open(f"{V}/cfg/{item}_pt.json"))
    bg = "navy" if it.get("help") else old["bg"]
    C = {"name": f"{item}_pt_v2", "bg": bg, "hook_secs": H,
         "series": "TUTORIAL" if it.get("help") else old["series"], "title": it["title"],
         "voice": it["voice"] if it.get("help") else old["voice"], "music": MUSIC + it["music"] if it.get("help") else old["music"], "lang": LANG,
         "end_vo": END_VO, "end_card": f"{V}/endcard_pt.png", "out": f"{OUT}/{item}_pt_v2.mp4",
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
        C["sfx"] = sfx + [[round(pmap(43.8), 2), "chime"]]; C["notes"] = []
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
    old = json.load(open(f"{V}/cfg/{item}_pt.json")); C = json.loads(json.dumps(old))
    C["name"] = f"{item}_pt_v2"; C["out"] = f"{OUT}/{item}_pt_v2.mp4"; C["cover"] = f"{V}/cfg/cover_{item}_pt.png"; C["cap_gap"] = 0.07
    C["phone"]["screens"] = [[t, ST + SCREEN[os.path.basename(p)] + ".png"] for t, p in old["phone"]["screens"]]
    fx = PEOPLE_FIX.get(item, {})
    for i, t in fx.get("vo", {}).items(): C["vo"][i][2] = t
    for i, n in enumerate(fx.get("screens", [])): C["phone"]["screens"][i][1] = ST + n + ".png"
    if fx.get("kicker"):
        spec = json.load(open(f"{V}/cfg/coverspec_{item}_pt.json")); spec["kicker"] = fx["kicker"]
        sp = f"{V}/cfg/coverspec_{item}_pt_v2.json"; json.dump(spec, open(sp, "w"), ensure_ascii=False)
        C["cover"] = f"{V}/cfg/cover_{item}_pt_v2.png"
        subprocess.run(["python3", f"{TPL}/render_cover.py", sp, C["cover"]], check=True, capture_output=True, cwd=TPL)
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
