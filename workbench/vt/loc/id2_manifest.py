"""id-ID v2 manifest (copy of es2_manifest.py): every id video for the Indonesia account 4 to 22 Nov, its slot, media, caption\n(button names as the id app shows them, ID hashtags), status. python3 id2_manifest.py -> /home/claude/loc/id_v2_manifest.json"""
import json, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__))); sys.path.insert(0, "/home/claude/up"); sys.path.insert(0, "/home/claude/w47")
import schedule, book
from loc_data import ITEMS
import id2 as pt2
R = "/root/ttn-reels"; RAW = "https://raw.githubusercontent.com/hectorsan76/ttn-reels/main/"
HELP = {16: "help08-laptop", 17: "help07-progress", 18: "help06-own-exercise", 19: "help09-habits", 20: "help01-home", 21: "help03-build", 22: "help05-email"}
# caption fixes: English button names -> the id labels on screen (takes 2026-11-05) or in glossary_id.csv
FIX = {
 (5, "howto"): [("Buka Program templates, ketuk", "Buka Template program, ketuk")],
 (8, "howto"): [("lalu Export PDF.", "lalu Ekspor PDF.")],
 (9, "howto"): [("Ketuk Add workout, lalu Build from scratch.", "Ketuk Tambah latihan, lalu Susun latihan dari nol.")],
 (10, "howto"): [("lalu Deactivate.", "lalu Nonaktifkan klien."), ("ke tab Deactivated.", "ke tab Nonaktif.")],
 (11, "howto"): [("Ketuk Add date dan pilih harinya. Lalu Add time dan atur jamnya.", "Ketuk Tambah tanggal dan pilih harinya. Lalu Tambah jam dan atur jamnya.")],
 (13, "howto"): [("ketuk Edit details dan", "ketuk Edit detail dan"), ("ketuk menu dan Resend invite.", "ketuk menu dan Kirim undangan.")],
 (15, "howto"): [("Buka menu, lalu Settings. Atur bahasa dan satuan, pilih Light, Dark, atau Notebook, dan pilih notifikasi yang kamu terima.",
                  "Buka menu, lalu Pengaturan. Atur bahasa dan satuan, pilih tampilan Terang, Gelap, atau Notebook, dan pilih pemberitahuan yang kamu terima.")],
 (5, "video"): [("Tambahkan catatan di latihan mana pun, tepat di tempat kamu akan melihatnya.", "Tambahkan catatan di latihan mana pun, dan catatannya muncul langsung di latihan itu.")],
 (16, "video"): [("Follow up di Home menampilkan", "Tindak lanjut di Beranda menampilkan"), ("dengan tombol Message.", "dengan tombol Pesan.")],
 (18, "video"): [("Chat dan pesan suara ada tepat di samping latihannya.", "Chat ada tepat di samping latihannya.")],
 (16, "howto"): [("Buka Calendar,", "Buka Kalender,")],
 (17, "howto"): [("Buka History klien.", "Buka Riwayat klien."), ("Ketuk Details pada", "Ketuk Detail pada")],
 (20, "howto"): [("Personal trainer, Home menampilkan", "Personal trainer, Beranda menampilkan"), ("Today berisi", "Hari ini berisi"), ("Follow up menampilkan", "Tindak lanjut menampilkan")],
 (21, "howto"): [("dan Clone last menyalin", "dan Salin terakhir menyalin")],
 (22, "howto"): [("lalu Email to client.", "lalu Email ke klien.")],
}
WAIT_HOWTO = {"howto26": "help take H05 (PART B): Export PDF and Preview are cut from it",
              "howto27": "help take H03 (PART B): Build a workout is cut from it",
              "howto28": "R-THROWAWAY part 2 (PART B): deactivate Ana Souza"}

def caption(day, kind):
    c = book.caption("id", day, kind)
    for a, b in FIX.get((day, kind), []):
        assert a in c, (day, kind, a); c = c.replace(a, b)
    return c

def main():
    rows = []
    for r in schedule.rows():
        if r["acc"] != "id": continue
        day, kind, item = r["day"], r["kind"], r["item"]
        slot = "12:00" if kind == "video" else "20:30"
        if item.startswith("help"):
            folder = f"posts/2026-11-{day:02d}-howto-{HELP[day]}-id-v2"
        else:
            it = ITEMS[item]; folder = f"posts/2026-11-{day:02d}-{'pv' if kind == 'video' else 'howto'}-{it['slug']}-id-v2"
        row = dict(item=item, day=f"2026-11-{day:02d}", slot=f"{slot} local (Indonesia, Bali time WITA)", bali=r["bali"], kind=kind,
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
    json.dump(rows, open("/home/claude/loc/id_v2_manifest.json", "w"), ensure_ascii=False, indent=1)
    from collections import Counter
    print(Counter(r["status"] for r in rows))
    for r in rows: print(r["day"], r["kind"], r["item"], r["status"], r.get("waiting_on", ""))

if __name__ == "__main__":
    main()
