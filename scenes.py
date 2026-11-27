"""Shot functions for the MyHeritage 2D explainer (Bahasa Indonesia).

Style: flat ink-line paper, night lighting, camera push-in, pop labels, stamps,
counters, lower thirds, polaroid ending — per the aivxer skill style bible.
Characters are original inventions; Gilad Japhet is a generic puppet + name tag.
"""
import math, random, json, sys, os, subprocess
import numpy as np, skia
from kit import *
from timeline import CUE, LINES, SHOTS, END, FLASH

BASE = os.path.dirname(os.path.abspath(__file__))
A = os.path.join(BASE, "audio")

MOUTH = {}
for _k in ("d1", "d2", "d3", "d4", "d5", "i1", "i2", "i3", "r1", "r2"):
    MOUTH[_k] = mouth_track(f"{A}/{_k}.wav")

rng = random.Random(7)
STARS = [(rng.uniform(-200, W + 200), rng.uniform(-100, 760), rng.choice((1.6, 2.0, 2.6, 3.2)), rng.uniform(0, 6)) for _ in range(120)]
SPECK = [(rng.uniform(0, W), rng.uniform(70, 1010), rng.uniform(1.5, 4.5), rng.uniform(40, 110)) for _ in range(260)]


def speaking(key, gt):
    i = int(round((gt - CUE[key]) * FPS)); tr = MOUTH.get(key)
    if tr is None: return None
    return tr[i] if 0 <= i < len(tr) else None


def talk(key, gt, rest='smile'):
    """Return (mouth, bob) for a dialogue line key at global time gt."""
    m = speaking(key, gt)
    if m is None: return rest, 0
    return {'open': 'open', 'mid': 'mid', 'closed': rest}[m], (5 if m == 'open' else 2 if m == 'mid' else 0)


def poplabel(c, s, x, y, t, size=120, v=LIME, rot=-5, font=None, stroke=15):
    if t <= 0: return
    pu = pop(min(t / .3, 1)); c.save(); c.translate(x, y); c.rotate(rot); c.scale(pu, pu)
    label(c, s, 0, 0, size, v, font=font, align='center', stroke=stroke, skew=-0.14 if font is None else 0); c.restore()


def tag(c, s, u, x=70, y=H - 86):
    a = ease_out(u * 3)
    if a <= 0: return
    w = text_w(s, 44)
    c.save(); c.translate(-50 * (1 - a), 0)
    c.drawRRect(skia.RRect.MakeRectXY(skia.Rect(x, y - 52, x + w + 64, y + 18), 10, 10), fp((10, 12, 26), 205 * a))
    c.drawRect(skia.Rect(x, y - 52, x + 10, y + 18), fp(GOLD, 255 * a))
    label(c, s, x + 34, y, 44, CREAM, alpha=a, skew=-0.12)
    c.restore()


def lower_third(c, name, sub, u, x, y):
    a = back(min(u * 2.6, 1), 1.4)
    if u <= 0: return
    w = max(text_w(name, 76), 380)
    c.save(); c.translate(x, y); c.scale(a, a)
    rect(c, 0, -74, w + 84, 74, (12, 14, 28), LW * .8)
    c.drawRect(skia.Rect(3, -71, 19, 71), fp(GOLD))
    label(c, name, 44, 4, 76, CREAM, skew=-0.12)
    label(c, sub, 46, 54, 40, GOLD, skew=-0.12)
    c.restore()


def stamp(c, txt, x, y, u, rot=-10, size=150, v=RED):
    if u <= 0: return
    sc = 2.6 - 1.6 * ease_out(min(u * 5, 1))
    a = min(u * 8, 1)
    w = text_w(txt, size, MARKER)
    c.save(); c.translate(x, y); c.rotate(rot); c.scale(sc, sc)
    for inset, wd in ((0, 13), (18, 5)):
        c.drawRRect(skia.RRect.MakeRectXY(skia.Rect(-w / 2 - 50 + inset, -size * .98 + inset, w / 2 + 50 - inset, size * .36 - inset), 16, 16), ink(wd, v, 255 * a))
    label(c, txt, 0, 0, size, v, font=MARKER, align='center', skew=0, alpha=a)
    c.restore()


def sky(c, top='#0A1136', bot='#24338A', h=860):
    c.drawRect(skia.Rect(-2000, -1500, W + 2000, H + 1500), sp(linear(0, 0, 0, h, [hx(top), hx(bot)])))


def stars(c, t):
    for (sx, sy, r, ph) in STARS:
        c.drawCircle(sx, sy, r, fp('#E8ECFF', 150 + 90 * math.sin(t * 2.4 + ph)))


def moon(c, x, y, r=50):
    for k, a in ((3.0, 16), (2.2, 22), (1.55, 30)): c.drawCircle(x, y, r * k, fp('#C9D4FF', a))
    c.drawCircle(x, y, r, fp('#F3EDD3')); c.drawCircle(x - r * .3, y - r * .25, r * .16, fp('#D9D2B4')); c.drawCircle(x + r * .25, y + r * .3, r * .22, fp('#DDD6B8'))


def cloud(c, x, y, s, v='#2C3B80', a=255):
    p = skia.Path()
    for dx, dy, r in ((-70, 8, 34), (-30, -14, 46), (22, -6, 40), (64, 10, 30)): p.addCircle(x + dx * s, y + dy * s, r * s)
    p.addRect(skia.Rect(x - 100 * s, y + 8 * s, x + 92 * s, y + 40 * s))
    c.drawPath(p, fp(v, a))


def sleeve(c, x0, y0, x1, y1, width, v, cuff='#F4EFE2', skin='#E6BE8E', fingers=True, hand_r=None):
    ang = math.degrees(math.atan2(y1 - y0, x1 - x0)); L = math.hypot(x1 - x0, y1 - y0)
    hr = hand_r or width * .5
    c.save(); c.translate(x0, y0); c.rotate(ang)
    circ(c, L + hr * .55, 0, hr, skin, LW)
    if fingers:
        for k in (-.42, 0, .42): c.drawLine(L + hr * 1.2, k * hr, L + hr * 1.52, k * hr * 1.1, ink(LW * .8))
    rect(c, -200, -width / 2, L, width / 2, v, LW)
    rect(c, L - 34, -width / 2 - 5, L + 6, width / 2 + 5, cuff, LW)
    c.restore()


def table_base(c):
    c.drawRect(skia.Rect(-900, -700, W + 900, H + 700), fp('#E9DFBF'))
    c.drawRect(skia.Rect(-900, -700, W + 900, H + 700), sp(radial(960, 520, 1300, [hx('#F6EED4'), hx('#E6DBB8'), hx('#CDBF98')], [0, .6, 1])))
    for (sx, sy, r, a) in SPECK: c.drawCircle(sx, sy, r, fp('#9A8F6E', a))
    for (ya, yb) in ((-700, 64), (1016, H + 700)):
        c.drawRect(skia.Rect(-900, ya, W + 900, yb), fp('#2F6B45'))
    for yy in (64, 1016): line(c, -900, yy, W + 900, yy, LW)
    for yy in (78, 1002): line(c, -900, yy, W + 900, yy, 3, INK, 120)


def room_bg(c, t, gt, lamp_x=1690):
    """Living-room / bedroom interior at night (shared by email, gilad, skits, world)."""
    c.drawRect(skia.Rect(-900, -600, W + 900, 820), fp('#33524A'))
    for i in range(-14, 48): c.drawLine(i * 62, -600, i * 62, 650, ink(10, '#2A4C42'))
    c.drawRect(skia.Rect(-900, 650, W + 900, 820), fp('#4E3020'))
    for i in range(-5, 16): rect(c, i * 190 + 24, 676, i * 190 + 170, 796, '#462A1B', LW * .6)
    line(c, -900, 650, W + 900, 650, LW)
    c.drawRect(skia.Rect(-900, 820, W + 900, H + 600), fp('#6A4429'))
    for i in range(1, 9): c.drawLine(-900, 820 + i * i * 6.5, W + 900, 820 + i * i * 6.5, ink(3, '#553520'))
    line(c, -900, 820, W + 900, 820, LW)
    # window with night city
    x0, y0, x1, y1 = 150, 96, 800, 640
    c.save(); c.clipRect(skia.Rect(x0, y0, x1, y1))
    sky(c, '#0B1238', '#2A3A96', 640); stars(c, t); moon(c, 250, 180, 30)
    cloud(c, 380 + gt * 5, 250, .6)
    r = random.Random(5)
    for bx in range(0, 7):
        bw = r.uniform(70, 130); bh = r.uniform(90, 220); bx0 = 60 + bx * 100
        c.drawRect(skia.Rect(bx0, 640 - bh, bx0 + bw, 640), fp('#1A2560'))
        for j in range(int(bh // 50)):
            for i in range(int(bw // 40)):
                if r.random() < .35: c.drawRect(skia.Rect(bx0 + 10 + i * 40, 640 - bh + 14 + j * 50, bx0 + 22 + i * 40, 640 - bh + 34 + j * 50), fp('#E9CF86', 200))
    c.restore()
    for (a, b, cc, d) in ((x0 - 22, y0 - 22, x1 + 22, y0), (x0 - 22, y1, x1 + 22, y1 + 22), (x0 - 22, y0, x0, y1), (x1, y0, x1 + 22, y1)):
        rect(c, a, b, cc, d, '#3B2416', LW * .8)
    line(c, (x0 + x1) / 2, y0, (x0 + x1) / 2, y1, 14, INK); line(c, (x0 + x1) / 2, y0, (x0 + x1) / 2, y1, 7, '#3B2416')
    line(c, x0, 300, x1, 300, 14, INK); line(c, x0, 300, x1, 300, 7, '#3B2416')
    rect(c, x0 - 44, y1 + 22, x1 + 44, y1 + 48, '#5A3824', LW * .8)
    # curtains
    line(c, 40, 60, 930, 60, 12, INK); line(c, 40, 60, 930, 60, 6, '#C9A04A')
    for (cx0, cx1) in ((54, 136), (822, 912)):
        cu = poly(c, [(cx0, 60), (cx1, 60), (cx1 + 8, 700), (cx0 - 10, 700)], '#93222B', LW)
        for k in (1, 2, 3): c.drawLine(cx0 + k * (cx1 - cx0) / 4, 66, cx0 - 6 + k * (cx1 - cx0 + 14) / 4, 694, ink(4, '#6E151D'))
    # wall clock + framed family photo
    circ(c, 1330, 250, 62, '#F4EFE2', LW); line(c, 1330, 250, 1330, 208, LW * .8); line(c, 1330, 250, 1358, 262, LW * .8); c.drawCircle(1330, 250, 5, fp(INK))
    rect(c, 990, 190, 1160, 400, '#C39A45', LW); rect(c, 1008, 208, 1142, 382, '#EFE6CE', LW * .6)
    circ(c, 1062, 300, 26, '#E6BE8E', LW * .6); circ(c, 1108, 300, 26, '#EBC79C', LW * .6)
    poly(c, [(1016, 372), (1050, 300), (1076, 340), (1104, 280), (1134, 372)], '#9DB7A6', LW * .5)
    # desk + banker lamp + rug
    c.drawOval(skia.Rect(1160, 1030, 1900, 1090), fp((0, 0, 0), 70, blur=14))
    rect(c, 1230, 800, 1850, 1062, '#6E4426', LW)
    for (dx0, dx1) in ((1262, 1520), (1560, 1818)):
        rect(c, dx0, 836, dx1, 930, '#7C4E2C', LW * .7); circ(c, (dx0 + dx1) / 2, 883, 9, '#D0A548', LW * .6)
    rect(c, 1196, 770, 1884, 802, '#8E5C36', LW)
    oval(c, lamp_x - 58, 754, lamp_x + 58, 776, '#D0A548', LW * .8)
    line(c, lamp_x, 762, lamp_x, 652, 12, INK)
    sh = skia.Path(); sh.moveTo(lamp_x - 116, 658); sh.cubicTo(lamp_x - 96, 574, lamp_x + 96, 574, lamp_x + 116, 658); sh.close()
    shape(c, sh, '#2FA25E', LW)
    oval(c, lamp_x - 104, 648, lamp_x + 104, 670, '#FFF3B8', LW * .7)
    oval(c, 560, 930, 1360, 1070, '#7E2A30', LW * .8); c.drawOval(skia.Rect(600, 944, 1320, 1056), ink(6, '#C39A45'))


def room_night(c, lamp_x=1690):
    win = skia.Path(); win.addRect(skia.Rect(150, 96, 800, 640))
    spill = skia.Path.Polygon([(190, 700), (760, 700), (1040, 1090), (330, 1090)], True)
    night(c, [('pool', lamp_x, 720, 600, .95), ('pool', 1000, 560, 430, .92), ('oval', 1000, 1000, 380, 110, .7),
              ('path', win, .82, 10), ('path', spill, .36, 34)], '#4C5CA0')
    add_light(c, lamp_x, 690, 430, '#FFD98A', 70)
    add_light(c, lamp_x, 664, 120, '#FFF3C8', 150)


def closeup_bg(c, t, gt, dx):
    blur_begin(c, 13)
    c.save(); c.translate(dx, -200); c.scale(1.5, 1.5); room_bg(c, t, gt); c.restore()
    c.restore()
    night(c, [('pool', 960, 520, 900, .55)], '#4C5CA0')


def sh_card(c, gt, S):
    c.drawRect(skia.Rect(-W, -H, 2 * W, 2 * H), fp((0, 0, 0)))
    words = S["arg"].split()
    key = S["keys"][0] if S["keys"] else None
    t0 = CUE[key] if key else S["s0"] + .2
    d = (LINES[key]["dur"] - .15) if key else 1.2
    tot = sum(len(w) + 1 for w in words); acc = 0; k = 0
    for w in words:
        if gt >= t0 + d * acc / tot - .04: k += 1
        acc += len(w) + 1
    size = 130 if len(S["arg"]) < 40 else 104
    f = skia.Font(FONT_HAND, size); full = f.measureText(S["arg"])
    if k: c.drawString(" ".join(words[:k]), W / 2 - full / 2, H / 2 + 44, f, fp('#FFFFFF'))


# ---------------------------------------------------------------- 00 email
def sh_email(c, gt, S):
    room_bg(c, gt, gt)
    # laptop on desk
    rect(c, 1330, 560, 1760, 770, '#2B2D3C', LW, r=10)
    rect(c, 1360, 590, 1730, 740, '#BFE3F0', LW * .6)
    label(c, "INBOX (1)", 1550, 640, 34, '#1B2A6A', align='center', skew=0)
    rect(c, 1380, 660, 1710, 700, '#F4EFE2', LW * .5)
    label(c, "1.200 kerabat baru", 1400, 690, 26, '#C8242C', skew=0)
    c.drawOval(skia.Rect(900, 1000, 1110, 1044), fp((0, 0, 0), 110, blur=8))
    laughing = CUE['n3'] <= gt < CUE['n4']
    shocked = gt >= CUE['n4']
    eyes = 'closed' if (laughing or blink(gt, 2.3, .2)) else ('wide' if shocked else 'dot')
    mouth = 'open' if laughing else ('o' if shocked else 'smirk')
    sq = 0.05 * math.sin(K(gt, S["s0"], .3) * math.pi)
    draw_char3(c, 1005, 1024, 1.08, DIMAS, face=-0.6, eyes=eyes, mouth=mouth, brow=.9 if shocked else .3,
               arms=(('down', 'gesture', K(gt, CUE['n2'], .3)), 'pocket'), tilt=-2 + 1.5 * math.sin(gt * 2.2),
               bob=3 + 3 * math.sin(gt * 3.1), squash=sq, light=1, rim='#FFE6B0')
    room_night(c)
    # email pop-up card at n2
    if gt > CUE['n2'] - .1:
        pu = pop(K(gt, CUE['n2'] - .1, .3))
        c.save(); c.translate(480, 330); c.rotate(-4); c.scale(pu, pu)
        rect(c, -330, -150, 330, 150, '#FBFAF2', LW, r=12)
        label(c, "SUBJEK:", -300, -96, 40, INK, skew=-0.1)
        label(c, "Kamu punya", -300, -20, 64, INK, skew=-0.1)
        label(c, "1.200 kerabat baru!", -300, 58, 64, RED, skew=-0.1)
        c.restore()
    if gt > CUE['n3']:
        poplabel(c, "PASTI SPAM", 1450, 330, gt - CUE['n3'], 110, LIME, -5)
    if gt > CUE['n4']:
        poplabel(c, "EMAIL ITU NYATA", 1450, 480, gt - CUE['n4'], 96, CREAM, 5)
    tag(c, "JAM 02:00  ·  RUMAH DIMAS", (gt - S["s0"] - .2) / 1.0)


# ---------------------------------------------------------------- 01 swab
def sh_swab(c, gt, S):
    table_base(c)
    # DNA kit box slides in
    k = back(K(gt, S["s0"] + .05, .5), 1.3)
    px = lerp(-560, 760, k)
    c.save(); c.translate(px, 520); c.rotate(-4)
    c.drawRect(skia.Rect(-282, -188, 292, 212), fp((60, 40, 10), 70, blur=12))
    rect(c, -290, -200, 290, 200, '#FBFAF2', LW, r=10)
    label(c, "TES DNA", 0, -110, 84, '#2A44A8', font=MARKER, align='center', skew=0)
    label(c, "usap · kirim · tunggu", 0, -30, 44, INK, align='center', skew=-0.1)
    # cotton bud drawing
    line(c, -180, 60, 180, 60, 14, INK); line(c, -180, 60, 180, 60, 8, '#F4EFE2')
    circ(c, -196, 60, 26, '#F4EFE2', LW * .8); circ(c, 196, 60, 26, '#F4EFE2', LW * .8)
    label(c, "1 USAPAN KECIL", 0, 150, 52, '#2A44A8', align='center', skew=-0.1)
    c.restore()
    sleeve(c, px - 900, 700, px - 360, 640, 170, '#2E6B6B', skin='#E8C39A')
    # envelope at n6
    if gt > CUE['n6'] - .1:
        kb = back(K(gt, CUE['n6'] - .1, .45), 1.4)
        ex = lerp(2400, 1420, kb)
        c.save(); c.translate(ex, 760); c.rotate(6)
        rect(c, -260, -110, 260, 110, '#F7F3E8', LW, r=8)
        poly(c, [(-260, -110), (0, 30), (260, -110)], '#EFE6CE', LW * .7)
        stamp(c, "POS", 0, 10, 1.0, rot=-8, size=64, v='#2F8A4E')
        c.restore()
        sleeve(c, ex + 560, 820, ex + 60, 800, 170, '#2E6B6B', skin='#E8C39A')
    if gt > CUE['n7']:
        poplabel(c, "PINTU KE MASA LALU", 960, 260, gt - CUE['n7'], 104, LIME, -4)


# ---------------------------------------------------------------- 04 gilad
def sh_gilad(c, gt, S):
    room_bg(c, gt, gt)
    # computer on desk with family tree on screen
    rect(c, 1330, 520, 1760, 770, '#2B2D3C', LW, r=10)
    rect(c, 1360, 550, 1730, 740, '#BFE3F0', LW * .6)
    c.save(); c.clipRect(skia.Rect(1360, 550, 1730, 740))
    for (tx, ty) in ((1450, 700), (1545, 620), (1640, 700), (1495, 640), (1595, 640)):
        circ(c, tx, ty, 16, '#E6BE8E', LW * .5)
    line(c, 1450, 700, 1545, 620, 4, INK); line(c, 1640, 700, 1545, 620, 4, INK)
    line(c, 1495, 640, 1545, 620, 4, INK); line(c, 1595, 640, 1545, 620, 4, INK)
    c.restore()
    c.drawOval(skia.Rect(900, 1000, 1110, 1044), fp((0, 0, 0), 110, blur=8))
    sq = 0.05 * math.sin(K(gt, S["s0"], .3) * math.pi)
    draw_char3(c, 1005, 1024, 1.0, GILAD, face=-0.7, eyes='closed' if blink(gt, 2.3, .2) else 'dot',
               mouth='smile', brow=.2, arms=(('down', 'present', K(gt, CUE['n10'], .3)), 'pocket'),
               tilt=-2 + 1.5 * math.sin(gt * 2.2), bob=3 + 3 * math.sin(gt * 3.1), squash=sq, light=1, rim='#FFE6B0')
    room_night(c)
    if gt > CUE['n10']:
        lower_third(c, "GILAD JAPHET", "13 TAHUN · TUGAS SEKOLAH", gt - CUE['n10'], 90, 930)
    if gt > CUE['n11']:
        poplabel(c, "TEMAN MAIN BOLA", 480, 300, gt - CUE['n11'], 84, CREAM, -5)
        poplabel(c, "GILAD BEGADANG", 480, 430, gt - CUE['n11'] - .6, 84, LIME, 4)
    if gt > CUE['n12']:
        stamp(c, "PERUSAHAAN BESAR", 1450, 330, (gt - CUE['n12']) / .9, rot=-8, size=96)


# ---------------------------------------------------------------- 05 skit1
def sh_skit1(c, gt, S):
    room_bg(c, gt, gt)
    # sofa back (characters sit behind the front panel, drawn later)
    rect(c, 240, 780, 1680, 1020, '#7A2228', LW, r=26)
    rect(c, 240, 700, 1680, 820, '#93222B', LW, r=26)
    for (bx, by) in ((420, 740), (1500, 740)): c.drawCircle(bx, by, 8, fp('#4E1218'))
    c.drawOval(skia.Rect(560, 1000, 1560, 1044), fp((0, 0, 0), 90, blur=8))
    # Dimas (left) speaks d1, d2 ; Ibu (right) speaks i1, i2
    d_spk = CUE['d1'] <= gt < CUE['d1'] + LINES['d1']['dur'] or CUE['d2'] <= gt < CUE['d2'] + LINES['d2']['dur']
    i_spk = CUE['i1'] <= gt < CUE['i1'] + LINES['i1']['dur'] or CUE['i2'] <= gt < CUE['i2'] + LINES['i2']['dur']
    d_key = 'd1' if gt < CUE['i1'] else 'd2'
    i_key = 'i1' if gt < CUE['d2'] else 'i2'
    dm, db = talk(d_key, gt, 'smile') if d_spk else ('smile', 0)
    im, ib = talk(i_key, gt, 'smile') if i_spk else ('smile', 0)
    draw_char3(c, 640, 1010, 0.95, DIMAS, face=0.6, eyes='closed' if blink(gt, 2.3, .2) else ('half' if d_spk else 'dot'),
               mouth=dm, brow=.5 if d_spk else 0, arms=(('down', 'gesture', K(gt, CUE[d_key], .3)) if d_spk else 'down', 'pocket'),
               bob=db * .6 + 2 * math.sin(gt * 2.4), light=1, rim='#FFE6B0')
    draw_char3(c, 1330, 1010, 0.95, IBU, face=-0.6, eyes='wide' if (i_spk and i_key == 'i2') else ('closed' if blink(gt, 2.6, 1.0) else 'dot'),
               mouth=im, brow=.8 if i_spk else 0, brow_tilt=-.6 if i_key == 'i2' else 0,
               arms=('down', ('down', 'chin', K(gt, CUE[i_key], .3)) if i_spk else 'down'),
               bob=ib * .6 + 2 * math.sin(gt * 2.4 + 1), light=-1, rim='#FFE6B0')
    # sofa front panel over the characters' legs (they sit behind it)
    rect(c, 240, 800, 1680, 1020, '#7A2228', LW, r=26)
    for (bx, by) in ((420, 850), (1500, 850)): c.drawCircle(bx, by, 8, fp('#4E1218'))
    room_night(c)
    if gt > CUE['d1']:
        lower_third(c, "DIMAS", "BARU TES DNA", gt - CUE['d1'], 90, 930)
    if gt > CUE['i1']:
        lower_third(c, "IBU", "KELUARGA SUDAH JELAS", gt - CUE['i1'], 1150, 930)
    if gt > CUE['d2']:
        poplabel(c, "SEPUPU DI BELANDA?", 620, 260, gt - CUE['d2'], 72, LIME, -4)
    if gt > CUE['i2']:
        poplabel(c, "KAKEK TAK PERNAH NAIK PESAWAT", 960, 430, gt - CUE['i2'], 72, CREAM, 4)


# ---------------------------------------------------------------- 07 dna
def sh_dna(c, gt, S):
    table_base(c)
    # lab tray: tubes + swab + envelope
    k = back(K(gt, S["s0"] + .05, .5), 1.3)
    px = lerp(-560, 760, k)
    c.save(); c.translate(px, 520); c.rotate(-3)
    c.drawRect(skia.Rect(-312, -218, 322, 232), fp((60, 40, 10), 70, blur=12))
    rect(c, -320, -230, 320, 230, '#FBFAF2', LW, r=10)
    for i, tx in enumerate((-180, -60, 60, 180)):
        rect(c, tx - 34, -160, tx + 34, 60, '#BFE3F0', LW * .7, r=12)
        rect(c, tx - 34, -160, tx + 34, -110, '#7FB069', LW * .7, r=12)
        label(c, "DNA", tx, 20, 36, '#2A44A8', align='center', skew=0)
    line(c, -260, 140, 260, 140, 14, INK); line(c, -260, 140, 260, 140, 8, '#F4EFE2')
    circ(c, -276, 140, 24, '#F4EFE2', LW * .8); circ(c, 276, 140, 24, '#F4EFE2', LW * .8)
    c.restore()
    sleeve(c, px - 900, 700, px - 380, 640, 170, '#F4EFE2', skin='#EBC79C', cuff='#2A44A8')
    # counter: 2.114 wilayah during n14
    if gt > CUE['n14'] + .15:
        pu = pop(K(gt, CUE['n14'] + .15, .3))
        v = int(round(2114 * ease_out(K(gt, CUE['n14'] + .25, 1.6))))
        c.save(); c.translate(1440, 290); c.rotate(-4); c.scale(pu, pu)
        label(c, f"{v:,}".replace(",", "."), 0, 0, 150, LIME, align='center', stroke=16, skew=-0.14)
        label(c, "WILAYAH DI DUNIA", 0, 96, 62, CREAM, align='center', stroke=13, skew=-0.14)
        c.restore()
    if gt > CUE['n15']:
        poplabel(c, "4× KABUPATEN", 960, 900, gt - CUE['n15'], 110, CREAM, -5)
    if gt > CUE['n13']:
        poplabel(c, "USAP · KIRIM · TUNGGU", 620, 250, gt - CUE['n13'], 76, LIME, -4)


# ---------------------------------------------------------------- 08 map
def sh_map(c, gt, S):
    c.drawRect(skia.Rect(-900, -700, W + 900, H + 700), fp('#0E1840'))
    for i in range(-8, 30): c.drawLine(i * 120, -700, i * 120, H + 700, ink(2, '#1A2658')); c.drawLine(-900, i * 120, W + 900, i * 120, ink(2, '#1A2658'))
    land = skia.Path(); land.moveTo(-200, 300); land.cubicTo(200, 120, 500, 260, 760, 180); land.cubicTo(1100, 80, 1500, 200, 2200, 120)
    land.lineTo(2200, 1300); land.lineTo(-200, 1300); land.cubicTo(60, 900, -120, 600, -200, 300); land.close(); shape(c, land, '#22306E', LW)
    isl = skia.Path(); isl.addOval(skia.Rect(260, -40, 620, 130)); shape(c, isl, '#22306E', LW)
    P0, P1 = (520, 640), (1440, 560)
    u = ease(K(gt, CUE['n16'] + .5, 2.2))
    for (px, py), nm in ((P0, "INDONESIA"), (P1, "BELANDA")):
        for k_, a_ in ((46, 30), (28, 60)): c.drawCircle(px, py, k_, fp('#FFD98A', a_))
        circ(c, px, py, 13, '#FFE9A0', LW * .7); label(c, nm, px, py + 90, 62, CREAM, align='center', stroke=10)
    for i in range(41):
        f = i / 40; x = lerp(P0[0], P1[0], f); y = lerp(P0[1], P1[1], f) - 190 * math.sin(math.pi * f)
        if f <= u and i % 2 == 0: c.drawCircle(x, y, 7, fp(RED))
    if gt > CUE['n16']:
        poplabel(c, "PETA LELUHURMU", 960, 240, gt - CUE['n16'], 110, LIME, -4)
    if gt > CUE['n17'] + .15:
        pu = pop(K(gt, CUE['n17'] + .15, .3))
        v = round(6.5 * ease_out(K(gt, CUE['n17'] + .25, 1.8)), 1)
        c.save(); c.translate(960, 900); c.rotate(-3); c.scale(pu, pu)
        label(c, f"{str(v).replace('.', ',')} JUTA KIT", 0, 0, 120, CREAM, align='center', stroke=14, skew=-0.14)
        c.restore()
    if gt > CUE['n18']:
        poplabel(c, "LEBIH DARI SINGAPURA", 960, 420, gt - CUE['n18'], 84, GOLD, 5)


# ---------------------------------------------------------------- 10 archive
def sh_archive(c, gt, S):
    # wall of archive drawers + documents
    c.drawRect(skia.Rect(-900, -700, W + 900, H + 700), fp('#3A2E22'))
    for row in range(5):
        for col in range(8):
            x0 = 60 + col * 230; y0 = 60 + row * 190
            rect(c, x0, y0, x0 + 200, y0 + 160, '#6E4426' if (row + col) % 2 else '#7C4E2C', LW * .6, r=6)
            circ(c, x0 + 100, y0 + 80, 10, '#D0A548', LW * .5)
    # big document in front
    k = back(K(gt, S["s0"] + .05, .5), 1.3)
    px = lerp(-700, 700, k)
    c.save(); c.translate(px, 540); c.rotate(-4)
    c.drawRect(skia.Rect(-292, -328, 312, 352), fp((60, 40, 10), 70, blur=12)); rect(c, -300, -340, 300, 340, '#FBFAF2', LW)
    label(c, "AKTE LAHIR", 0, -250, 56, INK, align='center', skew=-0.1)
    for i in range(8): c.drawLine(-240, -180 + i * 52, 240 - (i % 3) * 60, -180 + i * 52, ink(5, '#8E8878'))
    circ(c, 180, 260, 44, '#C8242C', LW * .7); c.drawCircle(180, 260, 24, fp('#FBFAF2'))
    c.restore()
    sleeve(c, px - 940, 720, px - 380, 660, 170, '#2E3A5C', skin='#EBC79C')
    if gt > CUE['n20'] + .15:
        pu = pop(K(gt, CUE['n20'] + .15, .3))
        v = round(19.9 * ease_out(K(gt, CUE['n20'] + .25, 2.0)), 1)
        c.save(); c.translate(1440, 300); c.rotate(-4); c.scale(pu, pu)
        label(c, f"{str(v).replace('.', ',')} MILIAR", 0, 0, 130, LIME, align='center', stroke=15, skew=-0.14)
        label(c, "CATATAN SEJARAH", 0, 92, 58, CREAM, align='center', stroke=12, skew=-0.14)
        c.restore()
    if gt > CUE['n21']:
        poplabel(c, "200× GUNUNG EVEREST", 560, 960, gt - CUE['n21'], 72, GOLD, -4)
    if gt > CUE['n22']:
        poplabel(c, "AKTE · NIKAH · FOTO LAMA", 960, 180, gt - CUE['n22'], 72, CREAM, 4)


# ---------------------------------------------------------------- 11 tree
def sh_tree(c, gt, S):
    c.drawRect(skia.Rect(-900, -700, W + 900, H + 700), fp('#E9DFBF'))
    c.drawRect(skia.Rect(-900, -700, W + 900, H + 700), sp(radial(960, 520, 1300, [hx('#F6EED4'), hx('#E6DBB8'), hx('#CDBF98')], [0, .6, 1])))
    # two family trees
    def tree(cx, cy, nodes, col):
        for (dx, dy, nm) in nodes:
            x, y = cx + dx, cy + dy
            circ(c, x, y, 46, col, LW * .8)
            label(c, nm, x, y + 88, 40, INK, align='center', skew=-0.1)
        for (a, b) in [((nodes[0][0], nodes[0][1]), (nodes[2][0], nodes[2][1])),
                       ((nodes[1][0], nodes[1][1]), (nodes[2][0], nodes[2][1])),
                       ((nodes[2][0], nodes[2][1]), (nodes[3][0], nodes[3][1]))]:
            line(c, cx + a[0], cy + a[1] + 46, cx + b[0], cy + b[1] - 46, LW * .7)
    tree(480, 420, [(-140, -140, "Kakek"), (140, -140, "Nenek"), (0, 0, "Ibu"), (0, 160, "Dimas")], '#F4EFE2')
    tree(1440, 420, [(-140, -140, "Kakek"), (140, -140, "Nenek"), (0, 0, "Ibu"), (0, 160, "Rani")], '#F4EFE2')
    # Smart Matches link lights up during n23
    u = ease(K(gt, CUE['n23'] + .4, 1.6))
    if u > 0:
        x0, y0, x1, y1 = 480 + 140, 420 - 140, 1440 - 140, 420 - 140
        mx, my = lerp(x0, x1, u), lerp(y0, y1, u) - 120 * math.sin(math.pi * u)
        c.drawLine(x0, y0, mx, my, ink(10, RED))
        for k_, a_ in ((40, 40), (26, 70)): c.drawCircle(mx, my, k_, fp('#FFD98A', a_))
        circ(c, mx, my, 14, '#FFE9A0', LW * .7)
        if u >= 1:
            c.drawLine(x0, y0, x1, y1, ink(10, RED))
            stamp(c, "SMART MATCHES", 960, 160, (gt - (CUE['n23'] + 2.0)) / .9, rot=-6, size=96)
    if gt > CUE['n24']:
        poplabel(c, "DIMAS MENEMUKAN RANI", 960, 900, gt - CUE['n24'], 96, LIME, -4)


# ---------------------------------------------------------------- 12 skit2 (video call)
def sh_skit2(c, gt, S):
    c.drawRect(skia.Rect(-900, -700, W + 900, H + 700), fp('#141A30'))
    d_spk = CUE['d3'] <= gt < CUE['d3'] + LINES['d3']['dur'] or CUE['d4'] <= gt < CUE['d4'] + LINES['d4']['dur']
    r_spk = CUE['r1'] <= gt < CUE['r1'] + LINES['r1']['dur'] or CUE['r2'] <= gt < CUE['r2'] + LINES['r2']['dur']
    d_key = 'd3' if gt < CUE['r1'] else 'd4'
    r_key = 'r1' if gt < CUE['d4'] else 'r2'
    dm, db = talk(d_key, gt, 'smile') if d_spk else ('smile', 0)
    rm, rb = talk(r_key, gt, 'smile') if r_spk else ('smile', 0)
    for (cx, spec, face, mouth, bob, spk, nm, sub) in (
            (480, DIMAS, 0.3, dm, db, d_spk, "DIMAS", "JAKARTA"),
            (1440, RANI, -0.3, rm, rb, r_spk, "RANI", "BELANDA")):
        c.save(); c.translate(cx, 540)
        rect(c, -380, -400, 380, 400, '#2E3A5C' if spk else '#232B45', LW, r=24)
        c.restore()
        # puppet bust inside the frame
        c.save(); c.translate(cx, 540); c.clipRect(skia.Rect(-380, -400, 380, 400))
        draw_char3(c, 0, 330, 1.05, spec, face=face, eyes='closed' if blink(gt, 2.4, cx) else ('half' if spk else 'dot'),
                   mouth=mouth, brow=.5 if spk else 0, arms=('down', 'down'), bob=bob * .6 + 2 * math.sin(gt * 2.4),
                   light=1 if cx < 960 else -1, rim='#FFE6B0')
        c.restore()
        c.drawRRect(skia.RRect.MakeRectXY(skia.Rect(cx - 380, 140, cx + 380, 940), 24, 24), ink(LW))
        label(c, nm, cx - 340, 900, 56, CREAM, skew=-0.1)
        label(c, sub, cx + 340, 900, 40, GOLD, align='right', skew=-0.1)
        if spk:
            c.drawRect(skia.Rect(cx - 380, 140, cx + 380, 156), fp(LIME))
    if gt > CUE['d3']:
        poplabel(c, "JADI KITA SEPUPU?", 960, 180, gt - CUE['d3'], 88, LIME, -4)
    if gt > CUE['r2']:
        poplabel(c, "ADA FOTO BELIAU DI ARSIPKU", 960, 1020, gt - CUE['r2'], 64, CREAM, 4)


# ---------------------------------------------------------------- 14 world
def sh_world(c, gt, S):
    room_bg(c, gt, gt)
    # globe on desk
    circ(c, 1560, 660, 90, '#7FB069', LW)
    c.drawOval(skia.Rect(1480, 600, 1640, 720), fp('#BFE3F0'))
    for (gx, gy) in ((1520, 640), (1600, 690), (1560, 700)): c.drawCircle(gx, gy, 18, fp('#7FB069'))
    rect(c, 1520, 750, 1600, 790, '#6E4426', LW)
    c.drawOval(skia.Rect(900, 1000, 1110, 1044), fp((0, 0, 0), 110, blur=8))
    sq = 0.05 * math.sin(K(gt, S["s0"], .3) * math.pi)
    draw_char3(c, 1005, 1024, 1.08, GILAD_ADULT, face=-0.6, eyes='closed' if blink(gt, 2.3, .2) else 'half',
               mouth='smile', brow=.3, arms=(('down', 'present', K(gt, CUE['n26'], .3)), 'pocket'),
               tilt=-2 + 1.5 * math.sin(gt * 2.2), bob=3 + 3 * math.sin(gt * 3.1), squash=sq, light=1, rim='#FFE6B0',
               sparkle=(gt - (CUE['n29'] + .5)) / .3 if gt > CUE['n29'] + .5 else 0)
    room_night(c)
    if gt > CUE['n25']:
        lower_third(c, "GILAD JAPHET", "RUANG TAMU · ISRAEL", gt - CUE['n25'], 90, 930)
    if gt > CUE['n26']:
        poplabel(c, "42 BAHASA", 1450, 330, gt - CUE['n26'], 110, LIME, -5)
    if gt > CUE['n27']:
        stamp(c, "$600 JUTA", 1450, 480, (gt - CUE['n27']) / .9, rot=-8, size=120)
    if gt > CUE['n28']:
        poplabel(c, "SETENGAH JUTA MOTOR", 480, 300, gt - CUE['n28'], 84, GOLD, -4)


# ---------------------------------------------------------------- 15 phone
def sh_phone(c, gt, S):
    # split-screen phone call: Dimas left, Ibu right, blurred room behind
    blur_begin(c, 13)
    c.save(); c.translate(-900, -200); c.scale(1.5, 1.5); room_bg(c, gt, gt); c.restore()
    c.restore()
    night(c, [('pool', 480, 520, 700, .5), ('pool', 1440, 520, 700, .5)], '#4C5CA0')
    d_spk = CUE['d5'] <= gt < CUE['d5'] + LINES['d5']['dur']
    i_spk = CUE['i3'] <= gt < CUE['i3'] + LINES['i3']['dur']
    dm, db = talk('d5', gt, 'smile') if d_spk else ('smile', 0)
    im, ib = talk('i3', gt, 'smile') if i_spk else ('smile', 0)
    draw_char3(c, 480, 1390, 1.9, DIMAS, face=0.5, eyes='closed' if blink(gt, 2.3, .2) else ('half' if d_spk else 'dot'),
               mouth=dm, brow=.5 if d_spk else 0, arms=(('phone', 'down', 0), 'down'),
               bob=db * .6, light=1, rim='#FFE6B0')
    # phone in Dimas' hand
    rect(c, 480 + 90, 1390 - 560, 480 + 150, 1390 - 380, '#2B2D3C', LW * .7, r=10)
    draw_char3(c, 1440, 1390, 1.9, IBU, face=-0.5, eyes='closed' if blink(gt, 2.6, 1.0) else ('half' if i_spk else 'dot'),
               mouth=im, brow=.5 if i_spk else 0, arms=('down', ('down', 'chin', K(gt, CUE['i3'], .3)) if i_spk else 'down'),
               bob=ib * .6, light=-1, rim='#FFE6B0')
    add_light(c, 480, 380, 600, '#FFD98A', 30); add_light(c, 1440, 380, 600, '#FFD98A', 30)
    if gt > CUE['n30']:
        tag(c, "MALAM INI  ·  DIMAS MENELEPON IBU", (gt - CUE['n30']) / 1.0, x=70, y=H - 86)
    if gt > CUE['i3']:
        poplabel(c, "KELUARGA TIDAK MENUNGGU", 960, 300, gt - CUE['i3'], 88, LIME, -4)


# ---------------------------------------------------------------- 16 polaroid
HERO_POS = [960, 620]


def sh_polaroid(c, gt, S):
    # family tree wide shot (background for the freeze)
    c.drawRect(skia.Rect(-900, -700, W + 900, H + 700), fp('#E9DFBF'))
    c.drawRect(skia.Rect(-900, -700, W + 900, H + 700), sp(radial(960, 520, 1300, [hx('#F6EED4'), hx('#E6DBB8'), hx('#CDBF98')], [0, .6, 1])))
    # tree trunk + branches
    line(c, 960, 1000, 960, 500, 26, INK)
    for (a, b) in (((960, 700), (620, 480)), ((960, 700), (1300, 480)), ((960, 560), (760, 340)), ((960, 560), (1160, 340))):
        line(c, *a, *b, 16, INK)
    nodes = [(620, 440, DIMAS, "Dimas"), (1300, 440, RANI, "Rani"), (760, 300, IBU, "Ibu"),
             (1160, 300, GILAD_ADULT, "Gilad"), (960, 420, DIMAS, "Kamu")]
    for (nx, ny, spec, nm) in nodes:
        rect(c, nx - 110, ny - 110, nx + 110, ny + 110, '#FBFAF2', LW, r=8)
        circ(c, nx, ny, 62, spec['skin'], LW * .8)
        label(c, nm, nx, ny + 150, 44, INK, align='center', skew=-0.1)
    if gt > CUE['n31']:
        poplabel(c, "1.200 KERABAT BARU", 960, 180, gt - CUE['n31'], 100, LIME, -4)
    # n32 payoff line is drawn by render.py in red marker under the polaroid —
    # do NOT also draw it inside the frozen photo (would duplicate).


FN = dict(email=sh_email, swab=sh_swab, card=sh_card, gilad=sh_gilad, skit1=sh_skit1,
          dna=sh_dna, map=sh_map, archive=sh_archive, tree=sh_tree, skit2=sh_skit2,
          world=sh_world, phone=sh_phone, polaroid=sh_polaroid)
VIG = dict(card=0, swab=.46, dna=.46, archive=.46, tree=.46, map=.55)
