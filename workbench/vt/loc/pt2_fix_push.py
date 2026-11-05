"""pt "Copy of" fix: copy the rebuilt videos and covers into their existing posts/*-pt-v2/ folders under NEW names
(video_fix.mp4, cover_fix.png; refuses to overwrite) and push. Copy of pt2_push.py. python3 pt2_fix_push.py item [item ...]"""
import sys, os, shutil, subprocess, glob
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from pt2_push import folder
R = "/root/ttn-reels"; V = R + "/workbench/vt"; RAW = "https://raw.githubusercontent.com/hectorsan76/ttn-reels/main/"
def run(*a): return subprocess.run(list(a), cwd=R, check=True, capture_output=True, text=True).stdout
if __name__ == "__main__":
    items = sys.argv[1:]; paths = []
    for item in items:
        f = folder(item); assert os.path.isdir(f"{R}/{f}"), f
        vid, cov = f"{R}/{f}/video_fix.mp4", f"{R}/{f}/cover_fix.png"
        for p in (vid, cov):
            if os.path.exists(p): raise SystemExit(f"exists, not overwriting: {p}")
        src_cov = f"{V}/cfg/cover_{item}_pt_fix.png"
        if not os.path.exists(src_cov): src_cov = f"{V}/cfg/cover_{item}_pt.png"  # people cover: no app screen, unchanged
        shutil.copy(f"/home/claude/loc/out_pt_fix/{item}_pt_fix.mp4", vid); shutil.copy(src_cov, cov)
        paths += [os.path.relpath(vid, R), os.path.relpath(cov, R)]
        paths += [os.path.relpath(p, R) for p in glob.glob(f"{V}/cfg/*{item}_pt_fix*")]
        paths += [os.path.relpath(p, R) for p in glob.glob(f"{R}/workbench/templates/assets/_loc_{item}_pt_fix.png")]
    paths += [f"workbench/vt/loc/{n}" for n in ("pt2_fix.py", "pt2_fix_ocr_used.py", "pt2_fix_check.py", "pt2_fix_push.py", "pt2_fix_manifest.py") if os.path.exists(f"{V}/loc/{n}")]
    run("git", "pull", "-q", "--rebase", "--autostash")
    run("git", "add", "-f", *paths)
    if run("git", "diff", "--cached", "--name-only").strip():
        run("git", "commit", "-qm", "pt-BR fix: rebuild " + ", ".join(items) + " from the Copy of retakes (video_fix.mp4, cover_fix.png)" +
            "\n\nCo-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>\nClaude-Session: https://claude.ai/code/session_01EYnk4sh8wD24Nv5kCXczgJ")
        run("git", "push", "-q")
    print(run("git", "rev-parse", "HEAD").strip())
    for item in items:
        for n in ("video_fix.mp4", "cover_fix.png"):
            u = RAW + folder(item) + "/" + n
            code = subprocess.run(["curl", "-s", "-o", "/dev/null", "-w", "%{http_code}", "-I", u], capture_output=True, text=True).stdout
            print(item, code, u)
