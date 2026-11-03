"""Copy finished localized videos into posts/ and push. python3 push.py item_lang [item_lang ...] -> prints raw URLs"""
import sys, os, shutil, subprocess, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from loc_data import ITEMS
R = "/root/ttn-reels"; RAW = "https://raw.githubusercontent.com/hectorsan76/ttn-reels/main/"
def folder(item, lang):
    it = ITEMS[item]; d = it["day"]
    kind = "pv" if it["kind"] == "people" else "howto"
    return f"posts/2026-11-{d:02d}-{kind}-{it['slug']}-{lang}"
def run(*a): return subprocess.run(list(a), cwd=R, check=True, capture_output=True, text=True).stdout
if __name__ == "__main__":
    names = sys.argv[1:]; urls = {}
    for n in names:
        item, lang = n.rsplit("_", 1); f = folder(item, lang); os.makedirs(f"{R}/{f}", exist_ok=True)
        shutil.copy(f"/home/claude/loc/out/{n}.mp4", f"{R}/{f}/video.mp4")
        shutil.copy(f"{R}/workbench/vt/cfg/cover_{n}.png", f"{R}/{f}/cover.png")
        urls[n] = RAW + f + "/video.mp4"
    run("git", "pull", "-q", "--rebase", "--autostash")
    run("git", "add", "posts", "workbench/vt/cfg", "workbench/vt/loc", "workbench/vt/people.py", "workbench/vt/reel2.py",
        "workbench/vt/endcard_pt.png", "workbench/vt/endcard_es.png", "workbench/vt/endcard_id.png", "workbench/templates/cover.html",
        "workbench/templates/endcard_pt.html", "workbench/templates/endcard_es.html", "workbench/templates/endcard_id.html")
    st = run("git", "status", "--porcelain", "--untracked-files=no")
    if any(l[:1] in "MADR" for l in st.splitlines()):
        run("git", "commit", "-qm", f"Native language videos: {', '.join(names)}\n\nCo-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>\nClaude-Session: https://claude.ai/code/session_01EYnk4sh8wD24Nv5kCXczgJ")
        run("git", "push", "-q")
    for n, u in urls.items():
        code = subprocess.run(["curl", "-s", "-o", "/dev/null", "-w", "%{http_code}", "-I", u], capture_output=True, text=True).stdout
        print(n, code, u)
