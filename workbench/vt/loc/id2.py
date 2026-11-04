"""Native id-ID v2 videos built from the native app recordings (native_takes/id, 2026-11-05). Copy of es2.py.
python3 id2.py howto <item> [...]   how-to from a take: segs and lines in take (proxy) seconds, taps and note from the tap log
python3 id2.py people <item> [...]  people video: English phone stills swapped for the id stills
Outputs /home/claude/loc/out_id_v2/<item>_id_v2.mp4, cfg/<item>_id_v2.json, cfg/cover_<item>_id_v2.png.
Proxy time = tap log time (+0.05 s), checked 2026-11-05 against screen-change onsets (R-INVITE, R-DATE, R-BOOK, H05, H09_T)."""
import json, os, sys, subprocess, math
V = "/root/ttn-reels/workbench/vt"; TPL = "/root/ttn-reels/workbench/templates"
sys.path.insert(0, V); sys.path.insert(0, V + "/loc")
import reel2
from PIL import Image, ImageDraw, ImageFont
import numpy as np
NT = "/mnt/user-data/uploads/TTN Reels/04 Working files/native_takes/id/"
ST = NT + "stills/"
OUT = "/home/claude/loc/out_id_v2"; os.makedirs(OUT, exist_ok=True)
H = 1.6
LANG = "id-ID"  # Google Chirp3-HD id-ID voices (same family and names as the id v1 set and the es/pt v2 sets)
END_VO = "The Training Notebook One. Software untuk personal trainer, dibuat untuk pelatih. Coba gratis 7 hari."

# how-to specs: take, segs [[a, b, speed]] in take seconds, vo [(anchor, text)] anchor = take seconds or ("o", output s),
# note (tap label, text), chime (take s). Lines naming buttons use the app's id labels as seen on screen (glossary_id.csv).
# id takes (native_takes_id_A.md, _B.md) run on their own clock, so every seg below is set from the id tap logs and frame sheets.
# Night time rule (24 hour, "03.38"): every frame with an hour 22 to 05 on screen is cut; where a wheel keeps a squashed,
# unreadable sliver of the "22" row under "21" at its lower edge, that sliver is blurred (mask boxes, proxy pixels).
WHEEL_SLIVER = [250, 1222, 110, 20]  # x, y, w, h of the squashed row under "21" on the phone hour/minute wheel (p6 pixels)
HOWTO = {
 "howto31": dict(take="R-INVITE", title="CEK EMAIL",
   segs=[[5.2, 9.2, 1.5], [9.2, 12.9, 1.5], [12.9, 17.6, 1.3], [17.6, 20.6, 1.2], [20.6, 28.0, 3.0], [28.0, 32.3, 1.8], [32.3, 36.5, 1.0]],
   vo=[(("o", 1.7), "Personal trainer, klien tidak menerima undangannya?"), (9.2, "Buka profilnya, ketuk Edit detail, dan cek emailnya."),
       (17.6, "Lalu ketuk menu dan Kirim undangan."), (28.3, "Undangan baru sedang dikirim.")],
   note=("Edit detail", "cek"), chime=32.6),
 "howto25": dict(take="R-BOOK", title="JADWALKAN SESI",
   # the Day view of Fri 6 Nov opens scrolled to 16.00 to 23.00 ("22.00", "23.00" labels) from 5.5 s until the scroll ends at 16.2 s: cut
   segs=[[1.2, 5.3, 1.6], [16.3, 24.6, 3.0], [24.6, 29.6, 1.6], [29.6, 36.2, 3.0], [36.2, 48.8, 3.5], [48.8, 63.0, 3.5],
         [76.6, 80.5, 1.0], [80.5, 86.5, 2.0], [86.5, 143.6, 6.5], [143.6, 147.5, 1.0]],
   vo=[(("o", 1.7), "Personal trainer, jadwalkan sesi langsung dari kalender."), (24.0, "Ketuk harinya dan pilih klien."),
       (36.5, "Beri nama latihannya."), (49.3, "Atur jamnya."), (77.2, "Sudah ada di kalender."),
       (86.9, "Buka dan tambahkan gerakannya."), (143.7, "Terjadwal dan siap.")],
   note=("PA", "pilih"), chime=143.8),
 "howto24": dict(take="R-TEMPLATE", title="TEMPLATE PROGRAM",
   # the goal menu opened, closed with no change and reopened (95.9 to 116.2 s): cut
   segs=[[0.5, 6.8, 1.5], [6.8, 17.3, 2.5], [17.3, 62.8, 14.0], [62.8, 76.5, 3.0], [76.5, 95.8, 6.0], [116.2, 135.0, 3.5],
         [135.0, 168.0, 8.0], [168.0, 216.0, 8.0], [216.0, 221.0, 1.0]],
   vo=[(("o", 1.7), "Personal trainer, susun program sekali dan pakai untuk setiap klien."),
       (3.3, "Buka Template program dan ketuk tombol plus."), (17.5, "Beri nama dan pilih hari latihannya."),
       (116.3, "Atur tujuan dan levelnya."), (142.5, "Tambahkan latihan pertama."), (176.4, "Lalu tambahkan gerakannya."),
       (213.0, "Minggu pertama sudah jadi. Berikan ke klien mana pun.")],
   note=("Template program baru", "plus"), chime=214.6),
 "howto18": dict(take="R-TIMED", title="SET BERWAKTU",
   # the Cardio chip tap at 68.6 s was swallowed and the whole library scrolls until the retap at 97.9 s: 68.7 to 97.8 s cut
   segs=[[2.0, 8.3, 1.5], [8.3, 33.4, 8.0], [33.4, 43.6, 4.0], [43.6, 48.0, 1.5], [48.0, 54.5, 3.0], [54.5, 68.7, 5.0],
         [97.8, 117.3, 5.0], [117.3, 125.5, 4.0], [125.5, 130.0, 1.5], [130.0, 139.5, 4.0], [139.5, 150.5, 4.0],
         [150.5, 174.3, 8.0], [174.3, 193.2, 6.0], [193.2, 201.0, 2.5], [201.0, 207.0, 1.0]],
   vo=[(("o", 1.7), "Personal trainer, ada kardio di program?"), (11.0, "Cari mesin rowing."), (43.5, "Atur menitnya. Tanpa repetisi."),
       (54.0, "Itu dia."), (117.5, "Sprint? Detik per set."), (174.5, "Lari? Tambahkan jaraknya."),
       (201.1, "Waktu dan jarak, langsung di latihan.")],
   note=("74 808 Mnt", "menit"), chime=200.6),
 "howto29": dict(take="R-DATE", title="TAMBAH TANGGAL",
   # starts after the rename (the copy shows "Copy of Seluruh Badan" 12 to 50.5 s); the time wheel opened on 01.54 and rolled
   # 01, 00, 23, 22, 21 to 18 (90.2 to 124.2 s): cut; from 124.3 s the hour column sits on 18 (rows 15 to 21 plus the masked sliver)
   segs=[[51.5, 58.0, 2.0], [58.0, 88.3, 5.0], [88.3, 90.15, 1.0], [124.3, 142.5, 4.0], [142.5, 148.0, 1.0]],
   mask=[("R-DATE", 124.3, 143.2) + tuple(WHEEL_SLIVER)],
   vo=[(("o", 1.7), "Personal trainer, latihan belum ada tanggalnya?"), (58.1, "Ketuk Tambah tanggal dan pilih harinya."),
       (88.4, "Lalu Tambah jam dan atur jamnya."), (142.7, "Sudah terjadwal, tanggal dan jamnya.")],
   note=("Tambah tanggal", "ketuk"), chime=142.7, cover="R-DATE/stills/cover.png"),
 "howto30": dict(take="R-RENAME", title="GANTI NAMA LATIHAN",
   segs=[[4.0, 8.9, 2.5], [8.9, 11.0, 1.2], [11.0, 18.8, 4.0], [18.8, 27.0, 2.5], [27.0, 34.2, 4.0], [34.2, 40.0, 1.0]],  # page loads blank before 3.8 s
   vo=[(("o", 1.7), "Personal trainer, nama latihannya kurang pas?"), (8.7, "Ketuk judulnya dan ketik nama baru."),
       (34.3, "Simpan. Selesai.")],
   note=("Seluruh Badan", "ketuk"), chime=36.0),
 "howto32": dict(take="R-THROWAWAY_1", title="FORMULIR AWAL",
   segs=[[0.5, 5.3, 2.0], [5.3, 32.0, 8.0], [32.0, 55.8, 7.0], [55.8, 97.0, 12.0], [97.0, 122.4, 8.0], [122.4, 156.2, 9.0],
         [156.2, 179.0, 8.0], [179.0, 190.0, 3.0], [190.0, 231.5, 11.0], [231.5, 238.7, 3.0], [238.7, 243.5, 1.5], [243.5, 248.0, 1.0]],
   vo=[(("o", 1.7), "Personal trainer, ini yang dilihat klien baru kamu."), (1.0, "Dia membuka undanganmu dan mulai mengisi formulir awal."),
       (5.4, "Nama, tanggal lahir, tujuan, dan pengalaman."), (190.0, "Beberapa pertanyaan kesehatan, lalu Kirim."),
       (243.6, "Sudah ada di profilnya sebelum sesi pertama.")],
   note=("220 748 Kirim", "ketuk"), chime=243.0),
 "howto33": dict(take="R-SETTINGS", title="PENGATURAN KAMU",
   segs=[[1.5, 3.9, 1.0], [3.9, 10.6, 2.5], [10.6, 16.5, 1.5], [16.5, 22.0, 1.5], [22.0, 25.5, 1.2]],
   vo=[(("o", 1.7), "Personal trainer, buka menu, lalu Pengaturan."), (12.0, "Atur bahasa dan satuannya."),
       (14.5, "Tampilan Terang, Gelap, atau Notebook."), (18.0, "Dan pilih pemberitahuan yang kamu terima.")],
   note=("Buka menu", "ketuk"), chime=21.5),
}

# English phone still -> id still (stills folder, same names as es/pt). client_nb, client_nb_b, client_habits are the id B retakes
# (the client has a workout today); the *_restday.png files from id A are not used.
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
# same fixes as es/pt: the id chat has no voice note; no workout still shows a trainer note, so pn05 shows the client's Home
# ("Catatan dari coach kamu" on today's workout); Follow up reads "Tindak lanjut", Home "Beranda" and Message "Pesan" in the id app
PEOPLE_FIX = {
 "pn05": dict(vo={1: "Tambahkan catatan di latihan mana pun, dan catatannya muncul langsung di latihan itu."}, screens=["client_nb"]),
 "pv_w47_wed": dict(vo={1: "Chat ada tepat di samping latihannya."}, kicker="percakapan di samping latihan"),
 "pv_w47_mon": dict(vo={1: "Tindak lanjut di Beranda menampilkan klien yang bolos, dengan tombol Pesan."}, kicker="Tindak lanjut, di Beranda"),
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
import id2_ocr as pt2_ocr, re
HOWTO.update({
 "howto26": dict(take="H05", title="EKSPOR PDF", cover="H05/stills/pdf_menu.png",
   # dead stretch 79 to 133.3 s (swallowed menu taps; the first menu2/pdf_menu/share_sheet marks are not used); Preview shows the
   # cached es PDF ("Lucía López, Cuerpo completo A") 155.3 to 160.3 s: the PDF part starts at 161.5 s on Putri's PDF
   segs=[[3.0, 9.5, 1.5], [133.3, 141.4, 1.3], [141.4, 155.0, 2.5], [161.5, 185.0, 3.5]],
   vo=[(("o", 1.7), "Personal trainer, klien latihan sendiri minggu ini?"), (133.4, "Buka latihannya, ketuk menu, lalu Ekspor PDF."),
       (161.6, "Kirim atau cetak, supaya dia tidak perlu menebak.")],
   note=("204 247 Ekspor PDF", "ketuk"), chime=161.6),
 "howto27": dict(take="H03", title="SUSUN LATIHAN",
   # the time wheel opened on 02.58 and rolled 00, 22, 20 to 18 (44.75 to 50.8 s): cut; from 50.9 s the hour sits on 18 (sliver masked)
   segs=[[7.0, 15.2, 2.5], [15.2, 21.5, 1.5], [50.9, 66.5, 4.0], [66.5, 96.5, 9.0], [96.5, 112.9, 6.0], [112.9, 139.5, 6.0],
         [139.5, 168.0, 6.0], [168.0, 181.0, 3.0], [297.5, 304.5, 2.0]],
   mask=[("H03", 50.9, 65.2) + tuple(WHEEL_SLIVER)],
   vo=[(("o", 1.7), "Personal trainer, sedang menyusun latihan hari ini?"), (12.0, "Ketuk Tambah latihan, lalu Susun latihan dari nol."),
       (51.0, "Atur jamnya dan beri nama."), (112.9, "Cari gerakannya dan tambahkan."),
       (141.6, "Set, repetisi, dan beban lewat papan angka."), (298.7, "Siap sebelum klien datang.")],
   note=("Susun latihan dari nol", "ketuk"), chime=301.5),
 "howto28": dict(take="R-THROWAWAY_2", title="NONAKTIFKAN KLIEN",
   segs=[[1.0, 3.4, 1.5], [3.4, 12.0, 2.0], [12.0, 20.3, 4.0], [20.3, 23.0, 1.0], [23.0, 31.8, 4.5], [31.8, 35.0, 1.2],
         [35.0, 41.7, 3.5], [41.7, 46.0, 1.2], [46.0, 53.3, 3.0], [53.3, 57.5, 1.0]],
   vo=[(("o", 1.7), "Personal trainer, klien sudah selesai berlatih denganmu?"), (3.5, "Buka profilnya, ketuk menu, lalu Nonaktifkan klien."),
       (42.0, "Dia langsung tidak dihitung lagi di paket kamu."), (53.4, "Dan pindah ke tab Nonaktif.")],
   note=("412 88 Tampilkan menu", "ketuk"), chime=54.2),
})
# help videos 16 to 22 Nov: id lines translated from the approved English narration (same source as the es/pt lines),
# button names as the id app shows them. Series bar "TUTORIAL | <title>", navy like the English.
HELP = {
 "help01": dict(day=20, take="H01", title="BERANDA KAMU", voice="Sadachbia", music="prettyjohn1-hip-hop-hip-hop-beat-525029.mp3",
   cover_txt=("Seluruh harimu", "dalam satu layar.", "hari ini"),
   segs=[[1.0, 16.3, 1.38], [16.3, 20.5, 1.5], [20.5, 29.5, 4.0], [29.5, 33.4, 1.5], [33.4, 37.0, 1.2], [37.0, 46.5, 4.0],
         [46.5, 62.4, 3.0], [62.4, 78.5, 3.0], [78.5, 89.5, 2.0]],
   vo=[(("o", 1.7), "Personal trainer, Beranda menampilkan seluruh hari melatihmu begitu kamu membuka aplikasi."),
       (3.0, "Saat klien mengirim pesan, pesannya muncul paling atas, jadi tidak ada yang kamu biarkan menunggu."),
       (16.6, "Hari ini berisi setiap sesi di jadwal kamu, dan pengingatmu tinggal satu ketukan."),
       (50.0, "Tindak lanjut menampilkan siapa pun yang melewatkan latihan, jadi tidak ada klien yang tertinggal."),
       (62.5, "Dan Aktivitas terbaru menampilkan apa yang sedang dilakukan klien kamu.")],
   note=("Pengingat hari ini", "ketuk"), chime=88.0),
 "help03": dict(day=21, take="H03", title="SUSUN LATIHAN", voice="Orus", music="soundsurfer-hip-hop-beats-592991.mp3",
   cover_txt=("Susun latihan", "untuk klien mana pun.", "susun"),
   # app launch splash until the Home fills at 6.9 s skipped; time wheel 44.75 to 50.8 s cut (02.58 and night rows);
   # exercises come through Tambah gerakan search (ruling (b))
   segs=[[6.9, 7.3, 0.4], [7.3, 21.5, 3.6], [21.5, 44.7, 5.0], [50.9, 96.5, 8.0], [96.5, 116.3, 3.0], [116.3, 139.5, 5.0],
         [139.5, 162.0, 3.0], [162.0, 168.0, 2.0], [168.0, 298.5, 16.0], [298.5, 302.5, 2.0], [302.5, 305.5, 1.0]],
   mask=[("H03", 50.9, 65.2) + tuple(WHEEL_SLIVER)],
   vo=[(("o", 1.7), "Personal trainer, begini cara menyusun latihan untuk klien."),
       (6.0, "Buka kliennya, ketuk Tambah latihan, lalu Susun latihan dari nol."),
       (30.0, "Pilih hari dan jamnya, beri judul, lalu ketuk Tambah."),
       (113.0, "Ketuk gerakan yang sering dipakai, atau cari di seluruh library."),
       (141.5, "Ketik beban dan repetisinya, dan kamu bisa melihat angkatan terakhirnya."),
       (163.0, "Salin terakhir menyalin set dengan satu ketukan."),
       (180.0, "Tambahkan sisanya dengan cara yang sama, ketuk kembali, dan latihannya sudah ada di jadwal klien.")],
   note=("Susun latihan dari nol", "ketuk"), chime=302.0),
 "help05": dict(day=22, take="H05", title="LATIHAN LEWAT EMAIL", voice="Aoede", music="soundsurfer-hip-hop-beats-592991.mp3",
   cover_txt=("Kirim latihan", "lewat email.", "PDF"),
   # colour picker 35.3 to 50 s skipped (as es); dead stretch 79 to 133.3 s cut; cached es PDF in Preview 155.3 to 160.3 s cut
   segs=[[4.0, 9.0, 1.5], [9.0, 13.7, 1.5], [13.7, 32.5, 5.0], [32.5, 35.0, 1.5], [50.3, 55.6, 1.2], [55.6, 61.3, 1.5], [61.3, 72.0, 3.5],
         [72.0, 79.0, 1.2], [133.3, 141.4, 2.2], [141.4, 155.0, 3.0], [161.5, 185.0, 4.0], [185.0, 192.5, 2.5]],
   vo=[(("o", 1.7), "Personal trainer, mau klien sudah pegang latihannya sebelum datang?"),
       (9.2, "Cukup kirim lewat email."), (20.0, "Lihat warna superset kamu?"), (32.0, "Warnanya ikut terkirim."),
       (53.7, "Ketuk menu, lalu Email ke klien."), (68.0, "Ketuk Kirim, dan latihan masuk ke email klien dengan PDF terlampir."),
       (133.5, "Mau salinan untuk kamu sendiri?"), (141.5, "Ketuk Ekspor PDF, lalu Pratinjau, dan selesai."),
       (175.0, "Lengkap dengan warnanya.")],
   note=("250 287 Email ke klien", "ketuk"), chime=77.0),
 "help06": dict(day=18, take="H06", title="GERAKAN KAMU SENDIRI", voice="Algenib", music="prettyjohn1-hip-hop-hip-hop-beat-525029.mp3",
   cover_txt=("Tambahkan gerakan", "kamu sendiri.", "video"),
   segs=[[1.5, 5.2, 1.5], [5.2, 15.0, 2.5], [15.0, 21.0, 2.0], [21.0, 32.5, 3.0], [32.5, 48.4, 4.0], [48.4, 67.5, 3.0], [67.5, 74.7, 2.0],
         [74.7, 79.0, 1.2], [79.0, 97.5, 4.0], [97.5, 105.6, 2.5], [105.6, 121.5, 4.0], [121.5, 128.0, 1.5], [128.0, 140.0, 1.3]],
   vo=[(("o", 1.7), "Personal trainer, ada gerakan yang belum ada di library?"), (3.0, "Tambahkan sendiri, dengan video kamu sendiri."),
       (5.3, "Ketuk Tambah gerakan, lalu Custom, dan Tambah gerakan custom."),
       (21.0, "Beri nama dan pilih cara mencatatnya."), (49.8, "Lalu kategori, otot utama, dan alatnya."),
       (67.6, "Punya video di YouTube?"), (70.0, "Tempel linknya di sini, atau ketuk Tambah video atau foto dan pilih klip dari ponsel kamu."),
       (105.7, "Ketuk Tambah, dan gerakannya sudah ada di library kamu."), (121.6, "Buka, dan video kamu langsung diputar di dalam aplikasi.")],
   note=("357 170 Custom", "ketuk"), chime=122.0),
 "help07": dict(day=17, take="H07", title="PROGRES KLIEN", voice="Aoede", music="soundsurfer-hip-hop-beats-592991.mp3",
   cover_txt=("Pantau progres", "klien kamu.", "trofi"),
   segs=[[2.0, 6.6, 1.5], [6.6, 17.6, 2.5], [17.6, 22.3, 2.0], [22.3, 30.5, 3.0], [30.5, 34.0, 1.0], [34.0, 42.5, 2.5], [42.5, 49.5, 2.5],
         [49.5, 57.3, 1.8], [57.3, 64.8, 1.4], [64.8, 76.4, 2.5], [76.4, 81.0, 1.5], [81.0, 88.6, 2.5], [88.6, 92.0, 1.0]],
   vo=[(("o", 1.7), "Personal trainer, mau bukti klien kamu makin kuat?"), (4.0, "Semuanya ada di riwayatnya."),
       (6.7, "Buka kliennya dan ketuk Riwayat untuk melihat latihan sebelumnya."), (29.8, "Lihat trofinya?"), (31.5, "Itu rekor pribadi baru."),
       (38.6, "Buka latihannya, ketuk menu sebuah gerakan, lalu Detail."),
       (61.8, "Beban tertinggi adalah beban terberat yang pernah dia angkat, dan Tren menunjukkan perubahannya sejak terakhir kali."),
       (66.0, "Grafiknya menunjukkan setiap sesi, jadi kamu bisa melihat bebannya naik."),
       (70.0, "Scroll untuk melihat setiap kali dia melakukannya, dan ketuk salah satunya untuk melihat setnya.")],
   note=("220 228 Riwayat", "ketuk"), chime=89.5),
 "help09": dict(day=19, take=[("H09_T", 0.0), ("H09_L3", 139.4333)], title="KEBIASAAN HARIAN", voice="Laomedeia",
   music="prettyjohn1-hip-hop-hip-hop-beat-525029.mp3", cover="H09_T/stills/cover.png",
   cover_txt=("Kebiasaan harian", "untuk klien kamu.", "kebiasaan"),
   # the starter list's "Tidur sebelum jam 23.00" is app wording: blurred full row like es/pt; the reminder wheel opened on 07.00 with
   # "04" and "05" above (42.3 to 44.9 s): cut, from 45.0 s it sits on 09.00 with 06 to 12
   ocr_extra=[("H09_T", r"23[.:]?00|sebelum", 29.0, 42.3)],
   segs=[[0.5, 8.5, 0.667], [139.93, 148.93, 1.7], [9.0, 17.4, 2.1], [17.4, 42.3, 5.0], [45.0, 61.5, 4.0], [61.5, 78.0, 4.0],
         [78.0, 97.4, 4.4], [97.4, 119.0, 4.4], [119.0, 129.0, 2.8]],
   vo=[(("o", 1.7), "Personal trainer, dengan kebiasaan kamu membantu klien membangun kebiasaan baik dan memantau semuanya, setiap hari."),
       (4.0, "Kebiasaan adalah target kecil harian, seperti minum 8 gelas air atau jalan kaki."),
       (140.0, "Klien melihat kebiasaannya setiap hari di aplikasinya dan mencentangnya saat selesai."),
       (9.0, "Untuk menambahkan, buka kliennya dan ketuk Kebiasaan."),
       (29.7, "Ketuk Tambah dan pilih kebiasaan dari daftar, atau buat sendiri."),
       (45.0, "Pilih ikon dan pengingat, kalau kamu mau ponselnya memberi tahu dia."),
       (61.6, "Saat dia mencentang, kamu bisa melihat minggunya langsung di sini."),
       (80.5, "Kalau dia melewatkan 3 hari beruntun, dia muncul di Tindak lanjut di Beranda kamu."),
       (103.5, "Berjalan baik? Ketuk Kerja bagus, karena apa yang dia lakukan di antara sesi sama pentingnya dengan sesinya.")],
   note=("Kebiasaan", "ketuk"), chime=121.0),
 "help08": dict(day=16, take="H08/phone", title="RENCANAKAN DI LAPTOP", voice="Orus", music="soundsurfer-hip-hop-beats-592991.mp3",
   cover_txt=("Rencanakan di", "laptop kamu.", "lebih cepat"),
   # web take starts on Beranda with the live line "Sekarang, 03.3x" until about 8.5 s: web part starts at 8.6 s
   web_segs=[[8.6, 18.3, 3.0], [18.3, 22.7, 2.0], [22.7, 29.0, 2.4], [29.0, 32.1, 2.0], [32.1, 46.6, 4.5], [46.6, 52.4, 2.4],
             [52.4, 61.2, 2.4], [61.2, 78.0, 4.5], [78.0, 87.8, 3.0], [87.8, 104.3, 4.0], [104.3, 109.3, 2.0], [109.3, 145.4, 8.0],
             [145.4, 185.0, 10.0], [185.0, 197.3, 4.0], [197.3, 207.0, 3.0]],
   phone_segs=[[2.5, 13.7, 3.0], [13.7, 31.3, 6.0], [31.3, 38.0, 1.0]],
   vo=[(("o", 1.7), "Personal trainer, mau menulis latihan minggu depan? Lebih cepat di laptop."),
       (("w", 8.7), "Buka Kalender, klik satu hari, lalu Tambah latihan."),
       (("w", 26.0), "Pilih kliennya, beri judul, dan latihannya sudah ada di kalender."),
       (("w", 52.4), "Buka latihannya, ketik nama gerakan, lalu tekan Enter."),
       (("w", 87.9), "Ketik beban dan repetisinya, dan Salin terakhir mengisi set berikutnya."),
       (("w", 104.3), "Klik Simpan, lalu lanjut ke gerakan berikutnya."),
       (("w", 145.5), "Latihan terakhir klien ada tepat di sampingnya, jadi kamu tahu di mana dia berhenti."),
       (("p", 2.5), "Dan saat kamu ambil ponsel, latihannya sudah ada di sana.")]),
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
        f = f"/home/claude/loc/ocr_id/{t.replace('/', '_')}.json"
        if not os.path.exists(f): raise SystemExit(f"OCR scan missing for {t}: run id2_ocr.py {t} 2")
        hits += [[h[0] + off] + h[1:] for h in json.load(open(f))]
    for t, pat, t0, t1 in it.get("ocr_extra", []):
        off = dict(tk)[t]
        ex = pt2_ocr.scan(NT + t + "/take_p6.mp4", 4, pat, t0, t1, 2, f"{t.replace('/', '_')}_extra_{t0}")
        # id: widen each hit to the end of its row so "Tidur sebelum jam 23.00" is blurred whole (tesseract splits the words)
        hits += [[h[0] + off, 16, h[2], 568, h[4], h[5], "extra"] for h in ex]  # id: the full row, from the left margin
    hits = [h for h in hits if re.search(r"@|\+|support", h[5], re.I) or len(h) > 6]
    boxes = redact_boxes(hits, 600, 1304)
    for t, t0, t1, x, y, w, h in it.get("mask", []):  # id: fixed blur over the squashed "22" sliver at a wheel's lower edge
        off = dict(tk)[t]; boxes.append([round(t0 + off, 2), round(t1 + off, 2), x, y, w, h])
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
        spec = json.load(open(f"{V}/cfg/coverspec_{item}_id.json"))
    src = NT + it.get("cover", takes_of(it)[0][0] + "/stills/cover.png")
    os.makedirs(f"{OUT}/proxy", exist_ok=True); red, n = redact_png(src, f"{OUT}/proxy/{item}_cover_still.png")
    im = Image.open(red).convert("RGB")
    a = f"_loc_{item}_id_v2.png"; lum = np.asarray(im.convert("L")).mean()
    if it.get("wide_cover"):  # laptop still: draw it on a laptop as the cover photo
        ph = laptop_photo(im); ph.save(f"{TPL}/assets/{a}"); spec.pop("note", None)
        spec.update({"photo": a, "ph": ph.height, "kicker": it["cover_txt"][2], "label": "TUTORIAL"})
    else:
        im.resize((560, round(560 * im.height / im.width)), Image.LANCZOS).save(f"{TPL}/assets/{a}")
        spec["screen"] = a
        if not it.get("help"): spec["bg"] = "paper" if lum < 110 else "navy"
        else: spec["bg"] = "paper" if lum < 110 else "navy"
    sp = f"{V}/cfg/coverspec_{item}_id_v2.json"; json.dump(spec, open(sp, "w"), ensure_ascii=False)
    out = f"{V}/cfg/cover_{item}_id_v2.png"
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
    hits = pt2_ocr.scan(web, 1, pt2_ocr.EMAIL + r"|Copy|of Seluruh", 0, 207, 1, "H08_web_full")
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
    it = HOWTO[item]; old = None if it.get("help") else json.load(open(f"{V}/cfg/{item}_id.json"))
    bg = "navy" if it.get("help") else old["bg"]
    C = {"name": f"{item}_id_v2", "bg": bg, "hook_secs": H,
         "series": "TUTORIAL" if it.get("help") else old["series"], "title": it["title"],
         "voice": it["voice"] if it.get("help") else old["voice"], "music": MUSIC + it["music"] if it.get("help") else old["music"], "lang": LANG,
         "end_vo": END_VO, "end_card": f"{V}/endcard_id.png", "out": f"{OUT}/{item}_id_v2.mp4",
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
        C["sfx"] = sfx + [[round(pmap(35.0), 2), "chime"]]; C["notes"] = []
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
    old = json.load(open(f"{V}/cfg/{item}_id.json")); C = json.loads(json.dumps(old))
    C["name"] = f"{item}_id_v2"; C["out"] = f"{OUT}/{item}_id_v2.mp4"; C["cover"] = f"{V}/cfg/cover_{item}_id.png"; C["cap_gap"] = 0.07
    C["phone"]["screens"] = [[t, ST + SCREEN[os.path.basename(p)] + ".png"] for t, p in old["phone"]["screens"]]
    fx = PEOPLE_FIX.get(item, {})
    for i, t in fx.get("vo", {}).items(): C["vo"][i][2] = t
    for i, n in enumerate(fx.get("screens", [])): C["phone"]["screens"][i][1] = ST + n + ".png"
    if fx.get("kicker"):
        spec = json.load(open(f"{V}/cfg/coverspec_{item}_id.json")); spec["kicker"] = fx["kicker"]
        sp = f"{V}/cfg/coverspec_{item}_id_v2.json"; json.dump(spec, open(sp, "w"), ensure_ascii=False)
        C["cover"] = f"{V}/cfg/cover_{item}_id_v2.png"
        subprocess.run(["python3", f"{TPL}/render_cover.py", sp, C["cover"]], check=True, capture_output=True, cwd=TPL)
    if item == "pv13":  # s13a shows Hector's phone with the English Home from 1.6 s: keep 0 to 1.5 s, raise the drawn phone at the cut
        a = "/home/claude/loc/out_id_v2/s13a_0_1.5.mp4"
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
    C = json.load(open(f"{V}/cfg/{item}_id_v2.json")); s = f"/home/claude/loc/sheets_id_v2/{item}_id_v2.jpg"; os.makedirs(os.path.dirname(s), exist_ok=True)
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
        r = subprocess.run(["python3", "-c", f"import sys; sys.path.insert(0,'{V}'); sys.path.insert(0,'{V}/loc'); import id2, {mod}; {mod}.build('{p}')"],
                           capture_output=True, text=True, cwd=V)
        print(r.stdout.strip()[-300:], r.stderr.strip()[-600:])
        print("sheet", sheet(item), "dur", round(dur(C["out"]), 2))
