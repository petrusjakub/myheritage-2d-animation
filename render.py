"""Render loop for the MyHeritage video: one MP4 per shot, or single PNG stills.

Usage:
  render.py all                render every shot to shots/NN_kind.mp4
  render.py 0 5 16             render only those shot indices
  render.py frames 0:0.5 5:0.7 render one still per spec (idx:fraction of shot)
                               into frames/sNN_f<frame>.png
"""
import sys, os, math, subprocess
import skia
from kit import *
from timeline import SHOTS, END, FLASH
from scenes import FN, VIG

BASE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(BASE, "shots")
FRAMES = os.path.join(BASE, "frames")


def render_shot(idx, only_frames=None, out_png=None):
    S = SHOTS[idx]
    kind = S["kind"]
    fn = FN[kind]
    s0, s1 = S["s0"], S["s1"]
    n0, n1 = int(round(s0 * FPS)), int(round(s1 * FPS))
    surf = skia.Surface(W, H); c = surf.getCanvas()
    proc = None
    if only_frames is None:
        tmp = f"{OUT}/{idx:02d}_{kind}.tmp.mp4"
        proc = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "bgra",
                                 "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
                                 "-c:v", "libx264", "-crf", "17", "-preset", "medium",
                                 "-pix_fmt", "yuv420p", tmp], stdin=subprocess.PIPE)
    for f in (range(n0, n1) if only_frames is None else only_frames):
        gt = f / FPS
        u = (f - n0) / max(n1 - n0 - 1, 1)
        e = ease(u)
        z = 1.0 + (0.03 if kind == 'card' else 0.07) * e
        rot = 1.6 * (e - .5) if kind in ('swab', 'dna', 'archive', 'tree') else 0
        c.clear(C((0, 0, 0)))
        c.save()
        c.translate(W / 2, H / 2); c.scale(z, z); c.rotate(rot); c.translate(-960, -545 if kind != 'card' else -540)
        fn(c, gt, S)
        c.restore()
        if kind != 'card':
            finish(surf, bloom=0.40); vignette(c, VIG.get(kind, .64))
        # polaroid freeze on the last shot
        if kind == 'polaroid' and gt >= FLASH:
            img = surf.makeImageSnapshot()
            c.clear(C((12, 12, 22)))
            k = ease_out((gt - FLASH) / .32)
            c.save(); c.translate(W / 2, H / 2 - 56 * k); c.rotate(-4.0 * k); sc = 1 - .33 * k; c.scale(sc, sc)
            c.drawRect(skia.Rect(-W / 2 - 30, -H / 2 - 30, W / 2 + 70, H / 2 + 200), fp((0, 0, 0), 120, blur=30))
            c.drawRect(skia.Rect(-W / 2 - 44, -H / 2 - 44, W / 2 + 44, H / 2 + 170), fp('#F7F2E6'))
            c.drawImageRect(img, skia.Rect(-W / 2, -H / 2, W / 2, H / 2), skia.SamplingOptions(skia.FilterMode.kLinear))
            c.drawRect(skia.Rect(-W / 2, -H / 2, W / 2, H / 2), ink(4, INK, 160))
            if gt > FLASH + .3:
                cu = min((gt - FLASH - .3) / .4, 1)
                ring = skia.Path(); ring.addArc(skia.Rect(-185, -190, 195, 175), -110, 352.0 * ease(cu)); c.drawPath(ring, ink(18, RED))
            if gt > FLASH + .68:
                a = min((gt - FLASH - .68) / .12, 1)
                label(c, "SIAPA YANG AKAN KAMU TEMUKAN?", -W / 2 + 40, H / 2 + 128, 84, RED, font=FONT_HAND, skew=0, alpha=a)
            c.restore()
            fl = max(0, 1 - (gt - FLASH) / .22)
            if fl > 0: c.drawRect(skia.Rect(0, 0, W, H), fp('#FFFFFF', 255 * fl))
        if proc:
            proc.stdin.write(surf.makeImageSnapshot().toarray(colorType=skia.kBGRA_8888_ColorType).tobytes())
        elif out_png:
            surf.makeImageSnapshot().save(out_png.format(f=f), skia.kPNG)
    if proc:
        proc.stdin.close()
        rc = proc.wait()
        if rc == 0:
            os.replace(tmp, tmp.replace(".tmp.mp4", ".mp4"))
        return rc
    return 0


if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True); os.makedirs(FRAMES, exist_ok=True)
    if sys.argv[1] == "frames":
        for spec in sys.argv[2:]:
            i, frac = spec.split(":"); i = int(i)
            S = SHOTS[i]
            f = int(round((S["s0"] + (S["s1"] - S["s0"]) * float(frac)) * FPS))
            render_shot(i, only_frames=[f], out_png=f"{FRAMES}/s{i:02d}_{{f}}.png")
            print("still", i, SHOTS[i]["kind"], "frame", f, flush=True)
    elif sys.argv[1] == "all":
        for i in range(len(SHOTS)):
            print("render", i, SHOTS[i]["kind"], render_shot(i), flush=True)
    else:
        for i in map(int, sys.argv[1:]):
            print("render", i, SHOTS[i]["kind"], render_shot(i), flush=True)
