"""Slot list for the native language reels, nearest first. python3 schedule.py -> prints JSON rows."""
import datetime, json, sys
OFF = {"br": 11, "mx": 14, "id": 0}; LANGOF = {"br": "pt", "mx": "es", "id": "id"}
SLOT = {"video": (12, 0), "howto": (20, 30)}
DAYITEM = {3: (None, "howto02"), 4: ("pn04", "howto25"), 5: ("pn05", "howto24"), 6: ("pn06", "howto18"), 7: ("pv07", "howto06"),
           8: ("pv08", "howto26"), 9: ("pv09", "howto27"), 10: ("pv10", "howto28"), 11: ("pv11", "howto29"), 12: ("pv12", "howto30"),
           13: ("pv13", "howto31"), 14: ("pn07", "howto32"), 15: ("pn08", "howto33"),
           16: ("pv_w47_mon", "help08"), 17: ("pv_w47_tue", "help07"), 18: ("pv_w47_wed", "help06"), 19: ("pv_w47_thu", "help09"),
           20: ("pv_w47_fri", "help01"), 21: ("pv_w47_sat", "help03"), 22: ("pv_w47_sun", "help05")}
def rows():
    out = []
    for acc in ("br", "mx", "id"):
        for day, (pv, ht) in DAYITEM.items():
            if acc == "id" and day < 4: continue
            for kind, item in (("video", pv), ("howto", ht)):
                if not item: continue
                h, m = SLOT[kind]; t = datetime.datetime(2026, 11, day, h, m) + datetime.timedelta(hours=OFF[acc])
                out.append(dict(acc=acc, day=day, kind=kind, item=item, lang=LANGOF[acc], bali=t.strftime("%Y-%m-%dT%H:%M:00+08:00")))
    return sorted(out, key=lambda r: r["bali"])
if __name__ == "__main__":
    print(json.dumps(rows(), indent=0))
