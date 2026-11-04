"""es-MX v2 manifest (copy of pt2_manifest.py): every es video for the México account 3 to 22 Nov, its slot, media, caption\n(button names as the es app shows them, MX hashtags), status. python3 es2_manifest.py -> /home/claude/loc/es_v2_manifest.json"""
import json, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__))); sys.path.insert(0, "/home/claude/up"); sys.path.insert(0, "/home/claude/w47")
import schedule, book
from loc_data import ITEMS
import es2 as pt2
R = "/root/ttn-reels"; RAW = "https://raw.githubusercontent.com/hectorsan76/ttn-reels/main/"
HELP = {16: "help08-laptop", 17: "help07-progress", 18: "help06-own-exercise", 19: "help09-habits", 20: "help01-home", 21: "help03-build", 22: "help05-email"}
# caption fixes: English button names -> the es labels on screen (takes 2026-11-04/05) or in glossary_es.csv
FIX = {
 (3, "howto"): [("luego Send invite", "luego Enviar invitación")],
 (5, "howto"): [("Abran Program templates", "Abran Plantillas de programa")],
 (8, "howto"): [("luego Export PDF", "luego Exportar PDF")],
 (9, "howto"): [("Toquen Add workout y luego Build from scratch", "Toquen Agregar rutina y luego Armar rutina desde cero")],
 (10, "howto"): [("luego Deactivate", "luego Desactivar cliente"), ("pestaña Deactivated", "pestaña Desactivados")],
 (11, "howto"): [("Toquen Add date y elijan el día. Luego Add time y pongan la hora.",
                  "Toquen Agregar fecha y elijan el día. Luego Agregar hora y pongan la hora.")],
 (13, "howto"): [("toquen Edit details", "toquen Editar datos"), ("y Resend invite", "y Enviar invitación")],
 (15, "howto"): [("luego Settings. Elijan su idioma y sus unidades, Light, Dark o Notebook, y qué notificaciones quieren recibir.",
                  "luego Ajustes. Elijan su idioma y sus unidades, la apariencia Claro, Oscuro o Libreta, y qué avisos quieren recibir.")],
 (5, "video"): [("Agreguen una nota a cualquier rutina, justo donde la van a ver.", "Agreguen una nota a cualquier rutina, y aparece justo ahí en la rutina.")],
 (16, "video"): [("Follow up en la pantalla de inicio", "Seguimiento en la pantalla de inicio")],
 (18, "video"): [("El chat y las notas de voz quedan justo al lado de sus rutinas.", "El chat queda justo al lado de sus rutinas.")],
 (20, "howto"): [("Follow up les muestra", "Seguimiento les muestra")],
 (21, "howto"): [("y Clone last copia", "y Copiar la última copia")],
 (22, "howto"): [("luego Email to client", "luego Enviar al cliente")],
}
WAIT_HOWTO = {"howto26": "help take H05 (PART B): Export PDF and Preview are cut from it",
              "howto27": "help take H03 (PART B): Build a workout is cut from it",
              "howto28": "R-THROWAWAY part 2 (PART B): deactivate Ana Souza"}

def caption(day, kind):
    c = book.caption("mx", day, kind)
    for a, b in FIX.get((day, kind), []):
        assert a in c, (day, kind, a); c = c.replace(a, b)
    return c

def main():
    rows = []
    for r in schedule.rows():
        if r["acc"] != "mx": continue
        day, kind, item = r["day"], r["kind"], r["item"]
        slot = "12:00" if kind == "video" else "20:30"
        if item.startswith("help"):
            folder = f"posts/2026-11-{day:02d}-howto-{HELP[day]}-es-v2"
        else:
            it = ITEMS[item]; folder = f"posts/2026-11-{day:02d}-{'pv' if kind == 'video' else 'howto'}-{it['slug']}-es-v2"
        row = dict(item=item, day=f"2026-11-{day:02d}", slot=f"{slot} local (Mexico City)", bali=r["bali"], kind=kind,
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
    json.dump(rows, open("/home/claude/loc/es_v2_manifest.json", "w"), ensure_ascii=False, indent=1)
    from collections import Counter
    print(Counter(r["status"] for r in rows))
    for r in rows: print(r["day"], r["kind"], r["item"], r["status"], r.get("waiting_on", ""))

if __name__ == "__main__":
    main()
