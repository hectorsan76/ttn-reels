"""Copy the built pt v2 videos and covers into posts/*-pt-v2/ and push. python3 pt2_push.py item [item ...]"""
import sys, os, shutil, subprocess, glob
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from loc_data import ITEMS
R = "/root/ttn-reels"; V = R + "/workbench/vt"; RAW = "https://raw.githubusercontent.com/hectorsan76/ttn-reels/main/"
HELP = {"help08": (16, "help08-laptop"), "help07": (17, "help07-progress"), "help06": (18, "help06-own-exercise"), "help09": (19, "help09-habits"),
        "help01": (20, "help01-home"), "help03": (21, "help03-build"), "help05": (22, "help05-email")}
def folder(item):
    if item in HELP: d, slug = HELP[item]; return f"posts/2026-11-{d:02d}-howto-{slug}-pt-v2"
    it = ITEMS[item]; kind = "pv" if it["kind"] == "people" else "howto"
    return f"posts/2026-11-{it['day']:02d}-{kind}-{it['slug']}-pt-v2"
def run(*a): return subprocess.run(list(a), cwd=R, check=True, capture_output=True, text=True).stdout
if __name__ == "__main__":
    items = sys.argv[1:]; paths = []
    for item in items:
        f = folder(item); os.makedirs(f"{R}/{f}", exist_ok=True)
        shutil.copy(f"/home/claude/loc/out_v2/{item}_pt_v2.mp4", f"{R}/{f}/video.mp4")
        cov = f"{V}/cfg/cover_{item}_pt_v2.png"
        if not os.path.exists(cov): cov = f"{V}/cfg/cover_{item}_pt.png"  # people covers unchanged unless a v2 was rendered
        shutil.copy(cov, f"{R}/{f}/cover.png"); paths.append(f)
        paths += [os.path.relpath(p, R) for p in glob.glob(f"{V}/cfg/*{item}_pt_v2*")]
        paths += [os.path.relpath(p, R) for p in glob.glob(f"{R}/workbench/templates/assets/_loc_{item}_v2.png")]
    paths += ["workbench/vt/loc/pt2.py", "workbench/vt/loc/pt2_manifest.py", "workbench/vt/loc/pt2_push.py", "workbench/vt/loc/pt2_ocr.py", "workbench/vt/reel2.py"]
    run("git", "pull", "-q", "--rebase", "--autostash")
    run("git", "add", "-f", *paths)
    if run("git", "diff", "--cached", "--name-only").strip():
        run("git", "commit", "-qm", "Native pt-BR v2 videos from the native app recordings: " + ", ".join(items) +
            "\n\nCo-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>\nClaude-Session: https://claude.ai/code/session_01EYnk4sh8wD24Nv5kCXczgJ")
        run("git", "push", "-q")
    for item in items:
        u = RAW + folder(item) + "/video.mp4"
        code = subprocess.run(["curl", "-s", "-o", "/dev/null", "-w", "%{http_code}", "-I", u], capture_output=True, text=True).stdout
        print(item, code, u)
