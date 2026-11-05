"""pt "Copy of" fix: point the four rebuilt items in /home/claude/loc/pt_v2_manifest.json at video_fix.mp4 / cover_fix.png.
Backs the manifest up first as pt_v2_manifest.before_fix.json (never overwrites a backup). Old media, cover, media_url go in "replaced";
"fix": "copy-of retake" is added. Captions and slot times are not touched. python3 pt2_fix_manifest.py"""
import json, os, shutil
M = "/home/claude/loc/pt_v2_manifest.json"; B = "/home/claude/loc/pt_v2_manifest.before_fix.json"
RAW = "https://raw.githubusercontent.com/hectorsan76/ttn-reels/main/"
ITEMS = ("howto18", "howto29", "pv10", "help08")
if not os.path.exists(B): shutil.copy2(M, B)
rows = json.load(open(M)); n = 0
for r in rows:
    if r["item"] not in ITEMS or r.get("fix"): continue
    d = os.path.dirname(r["media"])
    r["replaced"] = dict(media=r["media"], cover=r["cover"], media_url=r["media_url"])
    r["media"] = d + "/video_fix.mp4"; r["cover"] = d + "/cover_fix.png"; r["media_url"] = RAW + d + "/video_fix.mp4"
    r["fix"] = "copy-of retake"; n += 1
json.dump(rows, open(M, "w"), ensure_ascii=False, indent=1)
print("updated", n, "rows")
