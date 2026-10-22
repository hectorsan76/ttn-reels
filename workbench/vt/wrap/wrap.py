import json, subprocess, sys, re
sys.path.insert(0, "/home/claude/howto")
from howto import sub_png, chunks
def run(*a): subprocess.run(list(a), check=True)
body_src, cut, out = sys.argv[1], float(sys.argv[2]), sys.argv[3]
MUS = "/mnt/user-data/uploads/TTN Reels/03 Music/All platforms/Instrumental.mp3"
D = "/home/claude/demo"
# body without the trial card
run("ffmpeg","-v","error","-y","-i",body_src,"-t",f"{cut}","-af",f"afade=t=out:st={cut-0.4}:d=0.4","-c:v","libx264","-crf","19","-r","30","-c:a","aac","-ar","44100","-ac","2","body.mp4")
# intro: frozen first frame 7 s with music
IN = 6.6
run("ffmpeg","-v","error","-y","-ss","0.05","-i",body_src,"-frames:v","1","first.png")
run("ffmpeg","-v","error","-y","-loop","1","-t",f"{IN}","-i","first.png","-i",MUS,"-filter_complex",
    f"[1:a]atrim=0:{IN},volume=0.35,afade=t=out:st={IN-0.4}:d=0.4[a]","-map","0:v","-map","[a]","-r","30","-c:v","libx264","-crf","19","-pix_fmt","yuv420p","-c:a","aac","-ar","44100","-ac","2","intro_m.mp4")
json.dump({"voice":{"am_fenrir":0.7,"am_michael":0.3},"lines":[{"at":0.3,"text":"Welcome to The Training Notebook One.","speed":0.95},{"at":2.8,"text":"Thanks for your patience while we moved your account.","speed":0.95}]},open("intro.json","w"))
rep = subprocess.run(["python3",f"{D}/ttn_voiceover.py","intro.json","intro_m.mp4","intro_v.mp4","--models",D],check=True,capture_output=True,text=True).stdout
print(rep)
items=[]
for line in rep.splitlines():
    mm=re.match(r"\s*([\d.]+) to\s+([\d.]+)\s+(.*)",line)
    if not mm: continue
    a,b,t=float(mm[1]),float(mm[2]),mm[3]; cs=chunks(t); tot=sum(len(c)+3 for c in cs); s=a
    for c in cs:
        e=s+(b-a)*(len(c)+3)/tot; items.append((c,s,e)); s=e
ins=[]; g=""
for i,(c,s,e) in enumerate(items):
    p=f"s{i}.png"; sub_png(p,c); ins+=["-loop","1","-i",p]
    g+=f"{'[0:v]' if i==0 else f'[o{i}]'}[{i+1}:v]overlay=0:1765:enable='between(t,{s:.2f},{e+0.08:.2f})':shortest=1[o{i+1}];"
g+=f"[o{len(items)}]format=yuv420p[v]"
run("ffmpeg","-v","error","-y","-i","intro_v.mp4",*ins,"-filter_complex",g,"-map","[v]","-map","0:a","-c:v","libx264","-crf","19","-c:a","aac","-ar","44100","-ac","2","intro.mp4")
# outro
OU=4.8
run("ffmpeg","-v","error","-y","-loop","1","-t",f"{OU}","-i","/home/claude/howto/cta/email_end.png","-i",MUS,"-filter_complex",
    f"[1:a]atrim=20:{20+OU},asetpts=PTS-STARTPTS,volume=0.35,afade=t=in:d=0.3,afade=t=out:st={OU-1}:d=1[a]","-map","0:v","-map","[a]","-r","30","-c:v","libx264","-crf","19","-pix_fmt","yuv420p","-c:a","aac","-ar","44100","-ac","2","outro_m.mp4")
json.dump({"voice":{"am_fenrir":0.7,"am_michael":0.3},"lines":[{"at":0.3,"text":"If you need more help, just reply to this email.","speed":0.95}]},open("outro.json","w"))
print(subprocess.run(["python3",f"{D}/ttn_voiceover.py","outro.json","outro_m.mp4","outro.mp4","--models",D],check=True,capture_output=True,text=True).stdout)
open("list.txt","w").write("file 'intro.mp4'\nfile 'body.mp4'\nfile 'outro.mp4'\n")
run("ffmpeg","-v","error","-y","-f","concat","-safe","0","-i","list.txt","-c:v","libx264","-crf","19","-r","30","-c:a","aac","-b:a","128k",out)
print("done", out)
