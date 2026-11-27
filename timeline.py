"""Timeline for the MyHeritage 2D explainer (Bahasa Indonesia).

Cues are built from MEASURED voice durations (audio/lines.json):
shot start + 0.3 s, then each line + 0.26 s gap; voiceless chapter cards 1.5 s.
"""
import json, os

BASE = os.path.dirname(os.path.abspath(__file__))
A = os.path.join(BASE, "audio")
LINES = json.load(open(os.path.join(A, "lines.json")))

# (kind, arg, line keys) — kinds are implemented in scenes.py
SEQ = [
    ("email",   None,                        ["n1", "n2", "n3", "n4"]),   # cold open: 2am email
    ("swab",    None,                        ["n5", "n6", "n7"]),          # top-down DNA swab table
    ("card",    "Ini kisah MyHeritage",      ["n8"]),                       # black card, typed line
    ("card",    "Bab 1 · Anak 13 Tahun",     []),                           # voiceless chapter card
    ("gilad",   None,                        ["n9", "n10", "n11", "n12"]), # young Gilad at computer
    ("skit1",   None,                        ["d1", "i1", "d2", "i2"]),    # Dimas + Ibu living room
    ("card",    "Bab 2 · Tes DNA",           []),
    ("dna",     None,                        ["n13", "n14", "n15"]),       # lab / swab close, counter
    ("map",     None,                        ["n16", "n17", "n18"]),       # ancestor map
    ("card",    "Bab 3 · Arsip Raksasa",     []),
    ("archive", None,                        ["n19", "n20", "n21", "n22"]),# documents wall + counter
    ("tree",    None,                        ["n23", "n24"]),              # Smart Matches tree diagram
    ("skit2",   None,                        ["d3", "r1", "d4", "r2"]),    # Dimas + Rani
    ("card",    "Bab 4 · Dari Ruang Tamu ke Dunia", []),
    ("world",   None,                        ["n25", "n26", "n27", "n28", "n29"]),
    ("phone",   None,                        ["n30", "d5", "i3"]),         # Dimas calls Ibu
    ("polaroid", None,                       ["n31", "n32", "n33"]),       # family-tree polaroid ending
]

CUE = {}
SHOTS = []
cur = 0.0
for kind, arg, keys in SEQ:
    s0 = cur
    cur += 0.3
    if not keys:
        cur += 1.5
    for k in keys:
        CUE[k] = round(cur, 3)
        cur += LINES[k]["dur"] + 0.26
    cur += 0.12
    cur = round(cur * 30) / 30
    SHOTS.append(dict(kind=kind, arg=arg, keys=keys, s0=s0, s1=cur))

END = SHOTS[-1]["s1"] + 0.5
SHOT_T = {f"{i:02d}_{s['kind']}": (s["s0"], s["s1"]) for i, s in enumerate(SHOTS)}
FLASH = SHOTS[-1]["s0"] + 1.2  # polaroid freeze moment (n31 area)

if __name__ == "__main__":
    print("END", round(END, 2), "s =", round(END / 60, 2), "min")
    print("voice total", round(sum(v["dur"] for v in LINES.values()), 2))
    for i, s in enumerate(SHOTS):
        print(f"{i:02d} {s['kind']:9s} {s['s0']:6.2f}-{s['s1']:6.2f}  {s['arg'] or ''} {s['keys']}")
    for k, t in CUE.items():
        print(k, t, round(t + LINES[k]["dur"], 2))
