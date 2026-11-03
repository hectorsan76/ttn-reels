"""Publer payload for a native language reel. python3 book.py item_lang -> JSON post (account, caption, media, time, location)"""
import sys, os, json, datetime
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__))); sys.path.insert(0, "/home/claude/up"); sys.path.insert(0, "/home/claude/w47")
import schedule, loc_captions as LC
from push import folder, RAW
ACC = {"br": "6ae8eb6228608f1d16631e07", "mx": "6ae8eba84ab49876ff348182", "id": "6aea0a3328608f1d1665892d"}
LOC = {"br": "Sao Paulo, Brazil", "mx": "Mexico City, Mexico", "id": "Jakarta, Indonesia"}
HT = {"br": "#personaltrainer #educacaofisica #musculacao #treinamentofuncional #personaltrainerbrasil",
      "mx": "#entrenadorpersonal #entrenamientofuncional #fitnessmexico #coachfitness #entrenadorpersonalcdmx", "id": LC.ID_TAGS}
END = {"br": "Teste grátis por 7 dias. Link na bio.", "mx": "Prueba gratis 7 días. Link en la bio.", "id": LC.ID_END}
ns = {}; exec(open("/home/claude/up/gen.py").read().split("\ndef build")[0], ns); D = ns["D"]
import gen47
def caption(acc, day, kind):
    if acc == "id": t = LC.ID[(day, kind)]
    elif (day, kind) in LC.EXTRA_BRMX: t = LC.EXTRA_BRMX[(day, kind)][0 if acc == "br" else 1]
    elif day <= 15: t = [e for e in D[day] if e[0] == kind][0][2 if acc == "br" else 3]
    else: t = gen47.T[str(day)][kind][0 if acc == "br" else 1]
    return t + "\n\n" + END[acc] + "\n\n" + HT[acc]
def payload(name):
    item, lang = name.rsplit("_", 1); now = datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=8)))
    out = []
    for r in schedule.rows():
        if r["item"] != item or r["lang"] != lang: continue
        t = datetime.datetime.fromisoformat(r["bali"])
        p = {"account": ACC[r["acc"]], "platform": "instagram", "post_type": "reel", "caption": caption(r["acc"], r["day"], r["kind"]),
             "media_url": RAW + folder(item, lang) + "/video.mp4", "location": LOC[r["acc"]], "scheduled_for": r["bali"]}
        out.append(("PAST " if t <= now + datetime.timedelta(minutes=10) else "") + json.dumps(p, ensure_ascii=False))
    return out
if __name__ == "__main__":
    for n in sys.argv[1:]:
        for l in payload(n): print(l)
