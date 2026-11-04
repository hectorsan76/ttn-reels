"""pt v2 manifest: every pt video for 3 to 22 Nov, its slot, media, caption (button names as the pt app shows them), status.
python3 pt2_manifest.py -> /home/claude/loc/pt_v2_manifest.json"""
import json, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__))); sys.path.insert(0, "/home/claude/up"); sys.path.insert(0, "/home/claude/w47")
import schedule, book
from loc_data import ITEMS
import pt2
R = "/root/ttn-reels"; RAW = "https://raw.githubusercontent.com/hectorsan76/ttn-reels/main/"
HELP = {16: "help08-laptop", 17: "help07-progress", 18: "help06-own-exercise", 19: "help09-habits", 20: "help01-home", 21: "help03-build", 22: "help05-email"}
# caption fixes: English button names -> the pt labels on screen (takes 2026-11-04) or in glossary_pt.csv where not filmed yet
FIX = {
 (3, "howto"): [("em Send invite", "em Enviar convite")],
 (5, "howto"): [("Abra Program templates", "Abra Modelos de programa")],
 (8, "howto"): [("em Export PDF", "em Exportar PDF")],
 (9, "howto"): [("Toque em Add workout e depois em Build from scratch", "Toque em Adicionar treino e depois em Montar treino do zero")],
 (10, "howto"): [("depois em Deactivate", "depois em Desativar aluno"), ("aba Deactivated", "aba Desativados")],
 (11, "howto"): [("Toque em Add date e escolha o dia. Depois Add time e defina o horário.",
                  "Toque em Adicionar data e escolha o dia. Depois em Adicionar horário e escolha a hora.")],
 (13, "howto"): [("toque em Edit details", "toque em Editar dados"), ("em Resend invite", "em Enviar convite")],
 (15, "howto"): [("depois Settings. Escolha o idioma e as unidades, Light, Dark ou Notebook, e quais notificações você quer receber.",
                  "depois Configurações. Escolha o idioma e as unidades, a aparência Claro, Escuro ou Caderno, e quais avisos você quer receber.")],
 (5, "video"): [("Adicione uma nota a qualquer treino, bem onde você vai ver.", "Adicione uma nota a qualquer treino, e ela aparece bem ali no treino.")],
 (16, "video"): [("O Follow up na tela inicial", "A seção Acompanhar na tela inicial")],
 (16, "howto"): [("Abra o Calendário,", "Abra a Agenda,")],
 (18, "video"): [("O chat e os áudios ficam bem ao lado dos treinos dele.", "O chat fica bem ao lado dos treinos dele.")],
 (20, "howto"): [("O Follow up mostra", "Acompanhar mostra")],
 (21, "howto"): [("e Clone last copia", "e Copiar última copia")],
 (22, "howto"): [("em Email to client", "em Enviar ao cliente")],
}
WAIT_HOWTO = {"howto26": "help take H05 (PART B): Export PDF and Preview are cut from it",
              "howto27": "help take H03 (PART B): Build a workout is cut from it",
              "howto28": "R-THROWAWAY part 2 (PART B): deactivate Ana Souza"}

def caption(day, kind):
    c = book.caption("br", day, kind)
    for a, b in FIX.get((day, kind), []):
        assert a in c, (day, kind, a); c = c.replace(a, b)
    return c

def main():
    rows = []
    for r in schedule.rows():
        if r["acc"] != "br": continue
        day, kind, item = r["day"], r["kind"], r["item"]
        slot = "12:00" if kind == "video" else "20:30"
        if item.startswith("help"):
            folder = f"posts/2026-11-{day:02d}-howto-{HELP[day]}-pt-v2"
        else:
            it = ITEMS[item]; folder = f"posts/2026-11-{day:02d}-{'pv' if kind == 'video' else 'howto'}-{it['slug']}-pt-v2"
        row = dict(item=item, day=f"2026-11-{day:02d}", slot=f"{slot} local (Sao Paulo)", bali=r["bali"], kind=kind,
                   media=folder + "/video.mp4", cover=folder + "/cover.png", media_url=RAW + folder + "/video.mp4", caption=None, status=None)
        if item == "howto06":
            row.update(status="dropped", why="Note to client was retired in build 45; not in the app any more", media=None, cover=None, media_url=None)
            rows.append(row); continue
        row["caption"] = caption(day, kind)
        built = os.path.exists(f"{R}/{folder}/video.mp4") and os.path.exists(f"{R}/{folder}/cover.png")
        if built: row["status"] = "built"
        elif item.startswith("help"): row.update(status="waiting", waiting_on="help take for " + item + " (PART B) and the help edit tool rebuild")
        elif item in pt2.WAITING: row.update(status="waiting", waiting_on=pt2.WAITING[item])
        elif item in WAIT_HOWTO: row.update(status="waiting", waiting_on=WAIT_HOWTO[item])
        else: row.update(status="waiting", waiting_on="not built yet")
        rows.append(row)
    json.dump(rows, open("/home/claude/loc/pt_v2_manifest.json", "w"), ensure_ascii=False, indent=1)
    from collections import Counter
    print(Counter(r["status"] for r in rows))
    for r in rows: print(r["day"], r["kind"], r["item"], r["status"], r.get("waiting_on", ""))

if __name__ == "__main__":
    main()
