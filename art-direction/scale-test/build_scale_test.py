"""Scale test: one Orientation crop drawn natively at 16 px and 32 px tiles.

Both versions share one layout in cell units and the same on-screen size at
1366x768 (16 px x4, 32 px x2), so the only variable is pixel density.
People are 1 x 1.5 cells (16x24 or 32x48 logical pixels).

Run: python3 build_scale_test.py   (needs Pillow + numpy)
"""
import math
import os
import random

import numpy as np
from PIL import Image, ImageDraw, ImageFont

OUT = os.path.dirname(os.path.abspath(__file__))


def hx(s):
    s = s.lstrip("#")
    return np.array([int(s[i:i + 2], 16) for i in (0, 2, 4)], dtype=np.uint8)


def ramp(*cs):
    return [hx(c) for c in cs]


# Orientation palette from STYLE_BIBLE.md, plus character skin/hair ramps.
INK = ramp("#202337", "#343650", "#535971", "#777A8C")
STONE = ramp("#665D65", "#968A85", "#C7B7A0", "#F0DEC0")
GLASS = ramp("#203A50", "#366479", "#5AA3AE", "#A0DDD4")
WOOD = ramp("#523D4C", "#85565A", "#BA785F", "#E4AA73")
GREEN = ramp("#21484A", "#326D60", "#5FA06D", "#B2CE78")
BRASS = ramp("#705056", "#AC7655", "#E1AC62", "#F5D580")
CORAL = ramp("#71394F", "#B65761", "#E67A70", "#F6B18E")
VIOLET = ramp("#413755", "#67547C", "#9477AF", "#C3A6D6")
NAVY = ramp("#202337", "#2C3352", "#3E4870", "#59658F")
TEALJ = ramp("#1B4450", "#25707A", "#3A9C9C", "#7CCFC2")
OCHRE = ramp("#5C4038", "#9A6A3E", "#C99A4E", "#EDCB7A")
SKIN_ENG = ramp("#6E4433", "#9C6448", "#C98B62", "#E8B184")
SKIN_IVO = ramp("#8A5A4A", "#C08870", "#E3B094", "#F6D2B8")
SKIN_MIRA = ramp("#3E2630", "#5E3A36", "#85563F", "#A9744F")
HAIR_ENG = ramp("#2B1E26", "#4A2E2E", "#6E4434", "#93603F")
HAIR_IVO = ramp("#535971", "#8C8F9C", "#BFC0C6", "#E6E4E0")
HAIR_MIRA = ramp("#1E1A26", "#332833", "#4D3A44", "#6B5058")
PAPER = ramp("#C7B7A0", "#E2D6C2", "#F4F2EC", "#FFFFFF")

FLOOR = hx("#E6D3B3")
FLOOR_LIT = hx("#F0DEC0")
FLOOR_INLAY = hx("#D6C1A0")
JOINT = hx("#C7B7A0")


def mix(a, b, t):
    return (a.astype(float) * (1 - t) + b.astype(float) * t).astype(np.uint8)


def shifted(m, dx, dy):
    """out[y, x] = m[y + dy, x + dx], False outside."""
    h, w = m.shape
    out = np.zeros_like(m)
    ys0, ys1 = max(0, -dy), min(h, h - dy)
    xs0, xs1 = max(0, -dx), min(w, w - dx)
    out[ys0:ys1, xs0:xs1] = m[ys0 + dy:ys1 + dy, xs0 + dx:xs1 + dx]
    return out


def shade_mask(img, m, r, k_shadow=1, k_light=1, outline=None, light_top_only=False):
    """Fill a mask with stepped upper-left lighting and an optional edge tone."""
    img[m] = r[2]
    sh = m.copy()
    for k in range(1, k_shadow + 1):
        sh &= shifted(m, k, k)
    img[m & ~sh] = r[1]
    lit = m.copy()
    for k in range(1, k_light + 1):
        lit &= shifted(m, 0, -k) if light_top_only else shifted(m, -k, -k)
    img[m & ~lit & sh] = r[3]
    if outline is not None:
        edge = m & ~(shifted(m, 1, 0) & shifted(m, 0, 1) & shifted(m, -1, 0) & shifted(m, 0, -1))
        img[edge & ~lit] = r[3] if outline == "lit" else img[edge & ~lit]
        img[edge & lit] = outline


class Canvas:
    def __init__(self, cells_w, cells_h, t):
        self.t = t
        self.w, self.h = int(cells_w * t), int(cells_h * t)
        self.img = np.zeros((self.h, self.w, 3), np.uint8)
        yy, xx = np.mgrid[0:self.h, 0:self.w]
        self.cx = (xx + 0.5) / t
        self.cy = (yy + 0.5) / t

    def px(self, v):
        return int(round(v * self.t))

    def rect(self, x0, y0, x1, y1, c):
        self.img[self.px(y0):self.px(y1), self.px(x0):self.px(x1)] = c

    def rmask(self, x0, y0, x1, y1):
        m = np.zeros((self.h, self.w), bool)
        m[self.px(y0):self.px(y1), self.px(x0):self.px(x1)] = True
        return m

    def ellipse(self, cx, cy, rx, ry):
        return ((self.cx - cx) / rx) ** 2 + ((self.cy - cy) / ry) ** 2 <= 1.0

    def blob(self, cx, cy, r, phase, lobes=5, amp=0.14):
        dx, dy = self.cx - cx, self.cy - cy
        ang = np.arctan2(dy, dx)
        rr = r * (1 + amp * np.sin(lobes * ang + phase))
        return dx * dx + dy * dy <= rr * rr

    def shadow(self, m, strength=0.42):
        self.img[m] = mix(self.img[m], INK[2], strength)


# ---------------------------------------------------------------- environment

def floor(c):
    t = c.t
    c.img[:] = FLOOR
    # Skylight pool: lighter slabs in a stepped band across the ring.
    pool = np.zeros((c.h, c.w), bool)
    for i in range(6):
        pool |= c.rmask(4 + i * 0.5, 3.0 + i * 1.0, 11.5 + i * 0.5, 4.0 + i * 1.0)
    pool &= c.rmask(3.5, 3.0, 13.5, 10.6)
    c.img[pool] = FLOOR_LIT
    for gx in range(21):
        for gy in range(13):
            if (gx % 4 == 1 and gy % 4 == 1) or (gx % 4 == 3 and gy % 4 == 3):
                inset = 0.18
                c.rect(gx + inset, gy + inset, gx + 1 - inset, gy + 1 - inset, FLOOR_INLAY)
    # Slab joints on every cell edge.
    for gx in range(21):
        c.img[:, min(c.w - 1, gx * t)] = JOINT
    for gy in range(13):
        c.img[min(c.h - 1, gy * t), :] = JOINT
    if t >= 32:
        # Bevel highlight and sparse wear clusters.
        for gx in range(21):
            if gx * t + 1 < c.w:
                c.img[:, gx * t + 1] = mix(c.img[:, gx * t + 1], FLOOR_LIT, 0.6)
        rnd = random.Random(4)
        for _ in range(26):
            x, y = rnd.randrange(c.w - 4), rnd.randrange(c.h - 4)
            c.img[y:y + 1, x:x + 3] = mix(c.img[y, x], JOINT, 0.7)
            c.img[y + 1, x + 1] = mix(c.img[y + 1, x + 1], JOINT, 0.7)


def box(c, x0, y0, x1, y1, face, top, face_r, cast=True, k=None):
    """Furniture block: lit top plane, darker front face, outline, contact shadow."""
    t = c.t
    k = k or (2 if t >= 32 else 1)
    if cast:
        sm = c.rmask(x0 + 0.08, y1, x1 + 0.12, y1 + (0.16 if t >= 32 else 0.19))
        c.shadow(sm)
    mt = c.rmask(x0, y0, x1, y1 - face)
    shade_mask(c.img, mt, top, k_shadow=0, k_light=k, light_top_only=True)
    mf = c.rmask(x0, y1 - face, x1, y1)
    c.img[mf] = face_r[1]
    c.img[c.px(y1) - k:c.px(y1), c.px(x0):c.px(x1)] = face_r[0]
    c.img[c.px(y1 - face):c.px(y1 - face) + 1, c.px(x0):c.px(x1)] = face_r[3] if t >= 32 else face_r[2]
    outline(c, c.rmask(x0, y0, x1, y1))


def outline(c, m, color=None):
    ring = (shifted(m, 1, 0) | shifted(m, -1, 0) | shifted(m, 0, 1) | shifted(m, 0, -1)) & ~m
    inner = m & ~(shifted(m, 1, 0) & shifted(m, -1, 0) & shifted(m, 0, 1) & shifted(m, 0, -1))
    c.img[inner] = INK[0] if color is None else color


def north_wall(c):
    t = c.t
    k = 2 if t >= 32 else 1
    c.rect(0, 0, 20, 0.38, INK[1])
    c.img[0:k, :] = INK[2]
    c.img[c.px(0.38) - k:c.px(0.38), :] = INK[0]
    # Face: glass panels with stone piers.
    c.rect(0, 0.38, 20, 2.0, STONE[1])
    for i, x in enumerate([0.3, 2.4, 5.2, 13.1, 15.2]):
        w = 1.8
        m = c.rmask(x, 0.55, x + w, 1.78)
        c.img[m] = GLASS[1]
        c.img[m & (c.cy > 1.25)] = GLASS[2]
        band = m & (np.abs((c.cx - x) - (c.cy - 0.55) * 0.7 - (0.45 + 0.3 * (i % 2))) < (0.11 if t >= 32 else 0.13))
        c.img[band] = GLASS[3]
        mid = c.rmask(x + w / 2 - 0.03, 0.55, x + w / 2 + 0.03, 1.78)
        c.img[mid] = INK[1]
        outline(c, m, INK[1])
    # Printer alcove back wall: brighter stone with a brass wayfinding plaque.
    c.rect(8.4, 0.38, 12.6, 2.0, STONE[2])
    c.rect(9.6, 0.7, 11.4, 1.15, BRASS[2])
    c.img[c.px(0.7):c.px(0.7) + 1, c.px(9.6):c.px(11.4)] = BRASS[3]
    c.img[c.px(1.15) - k:c.px(1.15), c.px(9.6):c.px(11.4)] = BRASS[0]
    for xx in (10.0, 10.5, 11.0):
        c.rect(xx - 0.12, 0.84, xx + 0.12, 1.0, INK[1])
    # Baseboard + contact shadow on the floor.
    c.rect(0, 1.9, 20, 2.0, INK[0])
    c.shadow(c.rmask(0, 2.0, 20, 2.0 + (0.16 if t >= 32 else 0.19)), 0.35)


def east_wall(c):
    t = c.t
    k = 2 if t >= 32 else 1
    wall = c.rmask(19.45, 2.0, 20, 12) & ~c.rmask(19.45, 4.0, 20, 6.0)
    c.img[wall] = INK[1]
    c.img[wall & (c.cx < 19.45 + k / t)] = INK[2]
    # Records passage: cool sea-blue floor and a gold threshold.
    c.rect(19.45, 4.0, 20, 6.0, GLASS[1])
    c.rect(19.6, 4.0, 20, 6.0, GLASS[0])
    c.rect(19.3, 4.05, 19.45, 5.95, BRASS[2])
    for y in (3.85, 6.0):
        c.rect(19.3, y, 19.75, y + 0.15, INK[0])


def planter(c):
    t = c.t
    k = 2 if t >= 32 else 1
    x0, y0, x1, y1, face = 6.0, 4.9, 11.0, 8.4, 0.5
    c.shadow(c.rmask(x0 + 0.1, y1, x1 + 0.15, y1 + (0.16 if t >= 32 else 0.19)))
    # Front face with stone joints.
    mf = c.rmask(x0, y1 - face, x1, y1)
    c.img[mf] = STONE[1]
    c.img[c.px(y1 - face):c.px(y1 - face) + k, c.px(x0):c.px(x1)] = STONE[3]
    c.img[c.px(y1) - k:c.px(y1), c.px(x0):c.px(x1)] = STONE[0]
    for xx in np.arange(x0 + 1, x1, 1.0):
        c.rect(xx - 0.5 / t, y1 - face + k / t, xx + 0.5 / t, y1 - k / t, STONE[0])
    # Top: dark soil with a stone lip.
    c.rect(x0, y0, x1, y1 - face, WOOD[0])
    lip = c.rmask(x0, y0, x1, y1 - face) & ~c.rmask(x0 + 0.18, y0 + 0.18, x1 - 0.18, y1 - face - 0.12)
    c.img[lip] = STONE[2]
    c.img[lip & (c.cy < y0 + 0.09)] = STONE[3]
    # Pond.
    pond = c.ellipse(9.75, 7.15, 0.95, 0.5)
    c.img[pond] = GLASS[1]
    c.img[pond & (c.cy < 7.0)] = GLASS[2]
    c.img[pond & ~shifted(pond, 0, 1)] = GLASS[0]
    c.img[pond & (np.abs(c.cy - 6.95) < 0.5 / t * k) & (np.abs(c.cx - 9.5) < 0.35)] = GLASS[3]
    outline(c, pond, GLASS[0])
    # Foliage clusters, back to front.
    rnd = random.Random(7 if t < 32 else 8)
    clusters = []
    for gx in np.arange(6.45, 10.8, 0.62 if t < 32 else 0.48):
        for gy in (5.35, 5.9, 6.5, 7.15, 7.6):
            if ((gx - 8.4) / 2.0) ** 2 + ((gy - 6.2) / 1.25) ** 2 < 0.55:
                continue  # leave room for the tree
            if ((gx - 9.75) / 1.05) ** 2 + ((gy - 7.15) / 0.55) ** 2 < 1:
                continue  # keep the pond open
            r = (0.42 if t < 32 else 0.36) * rnd.uniform(0.8, 1.15)
            clusters.append((gx + rnd.uniform(-0.1, 0.1), gy + rnd.uniform(-0.08, 0.08), r))
    # Tree canopy: larger clusters ringed around the trunk.
    tree = []
    for ang in np.linspace(0, 2 * math.pi, 8 if t < 32 else 12, endpoint=False):
        tree.append((8.3 + math.cos(ang) * 1.15, 5.3 + math.sin(ang) * 0.75, 0.66 if t < 32 else 0.55))
    for ang in np.linspace(0.4, 2 * math.pi + 0.4, 5 if t < 32 else 7, endpoint=False):
        tree.append((8.15 + math.cos(ang) * 0.5, 4.95 + math.sin(ang) * 0.35, 0.6 if t < 32 else 0.5))
    tree.append((7.95, 4.75, 0.55 if t < 32 else 0.45))
    for cl in sorted(clusters, key=lambda q: q[1]):
        leaf(c, *cl, rnd, rmp=BED)
    # Canopy shadow falls down-right across the bed planting.
    cshadow = c.ellipse(8.55, 5.95, 1.55, 0.85) & c.rmask(6.12, 4.6, 10.88, 7.9) & ~c.ellipse(9.75, 7.15, 1.05, 0.6)
    c.shadow(cshadow, 0.38)
    # Trunk base visible below canopy.
    trunk = c.rmask(8.0, 6.3, 8.45, 6.95)
    shade_mask(c.img, trunk, WOOD, k_shadow=k, k_light=1)
    outline(c, trunk, WOOD[0])
    canopy = np.zeros((c.h, c.w), bool)
    for cl in sorted(tree, key=lambda q: q[1]):
        before = c.img.copy()
        leaf(c, *cl, rnd, big=True, clip=(5.6, 3.3, 11.2, 8.0))
        canopy |= np.any(c.img != before, axis=2)
    # Dark contour around the whole canopy so it lifts off the bed.
    ring = (shifted(canopy, 1, 0) | shifted(canopy, 0, 1) | shifted(canopy, -1, 0) | shifted(canopy, 0, -1)) & ~canopy
    c.img[ring & ~(shifted(canopy, 0, 1) & ~shifted(canopy, 0, -1))] = INK[0]
    # Flowers: coral and brass clusters.
    for fx, fy in [(6.6, 7.6), (7.3, 5.25), (10.6, 5.5), (6.9, 6.3), (10.5, 7.75)]:
        r0 = 0.09 if t >= 32 else 0.07
        m = c.ellipse(fx, fy, r0 * 1.6, r0 * 1.3)
        c.img[m] = CORAL[3]
        c.img[m & ~shifted(m, 1, 1)] = CORAL[1]
        c.img[c.ellipse(fx, fy, r0 * 0.6, r0 * 0.6)] = BRASS[3]


BED = ramp("#1B3B3E", "#2A5A50", "#3F7F5E", "#5FA06D")


def leaf(c, cx, cy, r, rnd, big=False, rmp=None, clip=(6.12, 4.6, 10.88, 8.0)):
    t = c.t
    k = 2 if t >= 32 else 1
    rmp = rmp or GREEN
    m = c.blob(cx, cy, r, rnd.uniform(0, 6.28), lobes=6 if big else 5)
    m &= c.rmask(*clip)
    shade_mask(c.img, m, rmp, k_shadow=k, k_light=k)
    edge = m & ~(shifted(m, 1, 0) & shifted(m, 0, 1))
    c.img[edge] = rmp[0]
    if t >= 32:
        # Warm leaf tips: small clusters along the lit edge.
        tips = m & ~shifted(m, -2, -2) & shifted(m, 1, 1)
        c.img[tips & ((np.floor(c.cx * t) + np.floor(c.cy * t)) % 3 == 0)] = hx("#D4E39A")


def desk(c, x0, y0, monitor=True):
    t = c.t
    box(c, x0, y0, x0 + 2.0, y0 + 0.95, 0.3, WOOD, WOOD)
    if monitor:
        mon = c.rmask(x0 + 0.55, y0 - 0.25, x0 + 1.45, y0 + 0.35)
        c.img[mon] = INK[1]
        scr = c.rmask(x0 + 0.62, y0 - 0.18, x0 + 1.38, y0 + 0.26)
        c.img[scr] = GLASS[2]
        c.img[scr & (c.cy < y0 - 0.02)] = GLASS[3]
        outline(c, mon)
        c.rect(x0 + 0.9, y0 + 0.35, x0 + 1.1, y0 + 0.5, INK[1])
    # Chair in front.
    ch = c.ellipse(x0 + 1.0, y0 + 1.35, 0.36, 0.28)
    shade_mask(c.img, ch, CORAL, k_shadow=2 if t >= 32 else 1)
    outline(c, ch)


def printer(c):
    t = c.t
    box(c, 8.6, 2.0, 12.4, 3.05, 0.35, PAPER, STONE)
    body = c.rmask(9.5, 1.75, 11.5, 2.55)
    shade_mask(c.img, body, ramp("#535971", "#8C93A6", "#C9CEDA", "#EEF1F6"), k_shadow=2 if t >= 32 else 1)
    outline(c, body)
    scr = c.rmask(9.75, 1.9, 10.6, 2.25)
    c.img[scr] = hx("#19AFA2")
    c.img[scr & (c.cy < 2.02)] = GLASS[3]
    # Badge cards on the counter.
    for i, col in enumerate([CORAL[2], GLASS[2], BRASS[2]]):
        cm = c.rmask(8.85 + i * 0.22, 2.25 + i * 0.05, 9.25 + i * 0.22, 2.55 + i * 0.05)
        c.img[cm] = col
        outline(c, cm, INK[1])
    slot = c.rmask(10.85, 2.05, 11.3, 2.15)
    c.img[slot] = INK[0]


def pot_plant(c, x, y):
    t = c.t
    k = 2 if t >= 32 else 1
    pot = c.rmask(x + 0.2, y + 0.45, x + 0.8, y + 0.95)
    c.shadow(c.rmask(x + 0.25, y + 0.95, x + 0.9, y + 1.08))
    shade_mask(c.img, pot, WOOD, k_shadow=k, light_top_only=True)
    outline(c, pot)
    rnd = random.Random(int(x * 10 + y))
    for (dx, dy, r) in [(0.3, 0.3, 0.26), (0.7, 0.3, 0.26), (0.5, 0.12, 0.3), (0.5, 0.42, 0.24)]:
        m = c.blob(x + dx, y + dy, r, rnd.uniform(0, 6), lobes=5, amp=0.18)
        shade_mask(c.img, m, GREEN, k_shadow=k, k_light=k)
        c.img[m & ~(shifted(m, 1, 0) & shifted(m, 0, 1))] = GREEN[0]


def bench(c, x0, y0):
    box(c, x0, y0, x0 + 2.0, y0 + 0.55, 0.22, WOOD, WOOD)
    for i in range(1, 4):
        c.rect(x0 + i * 0.5 - 0.5 / c.t, y0 + 0.04, x0 + i * 0.5 + 0.5 / c.t, y0 + 0.31, WOOD[1])


def mail_counter(c, x0, y0):
    t = c.t
    box(c, x0, y0, x0 + 3.2, y0 + 0.95, 0.38, WOOD, WOOD)
    rnd = random.Random(3)
    for i in range(5):
        ex = x0 + 0.25 + i * 0.55
        em = c.rmask(ex, y0 + 0.08 + (i % 2) * 0.06, ex + 0.42, y0 + 0.4 + (i % 2) * 0.06)
        c.img[em] = PAPER[2] if i % 3 else CORAL[3]
        c.img[em & ~shifted(em, 0, 1)] = PAPER[0]
        outline(c, em, INK[1])
    # Coral courier strap on the counter edge.
    c.rect(x0 + 2.6, y0 + 0.45, x0 + 3.0, y0 + 0.6, CORAL[2])


# ---------------------------------------------------------------- markers

def marker(c, kind, x, y):
    """World interaction markers: distinct silhouette per meaning."""
    t = c.t
    s = 0.42
    if kind == "talk":  # coral speech bubble
        m = c.rmask(x - s, y - s * 0.7, x + s, y + s * 0.45)
        corner = (c.cx < x - s + 0.08) | (c.cx > x + s - 0.08)
        corner &= (c.cy < y - s * 0.7 + 0.08) | (c.cy > y + s * 0.45 - 0.08)
        m &= ~corner
        tail = (c.cy >= y + s * 0.45) & (c.cy < y + s * 0.8) & (c.cx > x - 0.12) & (c.cx < x + 0.12 - (c.cy - y - s * 0.45))
        m |= tail
        c.img[m] = CORAL[2]
        c.img[m & ~shifted(m, 0, -1)] = CORAL[3]
        for dx in (-0.2, 0, 0.2):
            c.img[c.ellipse(x + dx, y - 0.12, 0.065, 0.065) | c.rmask(x + dx - 0.5 / t, y - 0.12 - 0.5 / t, x + dx + 0.5 / t, y - 0.12 + 0.5 / t)] = PAPER[3]
        outline(c, m, CORAL[0])
    elif kind == "terminal":  # teal monitor
        m = c.rmask(x - s, y - s * 0.7, x + s, y + s * 0.4)
        m |= c.rmask(x - 0.12, y + s * 0.4, x + 0.12, y + s * 0.7)
        m |= c.rmask(x - 0.25, y + s * 0.7, x + 0.25, y + s * 0.85)
        c.img[m] = hx("#19AFA2")
        c.img[c.rmask(x - s + 0.1, y - s * 0.7 + 0.1, x + s - 0.1, y + s * 0.4 - 0.1)] = GLASS[3]
        outline(c, m, GLASS[0])
    elif kind == "route":  # gold diamond with doorway cutout
        m = (np.abs(c.cx - x) + np.abs(c.cy - y)) <= s
        door = c.rmask(x - 0.1, y - 0.12, x + 0.1, y + 0.2)
        c.img[m] = BRASS[2]
        c.img[m & ~shifted(m, 0, -1)] = BRASS[3]
        c.img[door] = BRASS[0]
        outline(c, m, BRASS[0])
    elif kind == "glitch":  # violet folded page
        m = c.rmask(x - 0.3, y - 0.38, x + 0.3, y + 0.38)
        fold = (c.cx - (x + 0.3)) + (y - 0.38 - c.cy) > -0.22
        m &= ~fold
        c.img[m] = VIOLET[2]
        tri = c.rmask(x + 0.08, y - 0.38, x + 0.3, y - 0.16) & ((c.cx - (x + 0.08)) < (c.cy - (y - 0.38)))
        c.img[tri] = VIOLET[3]
        for yy in (y - 0.05, y + 0.12):
            c.rect(x - 0.18, yy, x + 0.15, yy + 1.0 / t, VIOLET[0])
        outline(c, m | tri, VIOLET[0])


# ---------------------------------------------------------------- characters
# Shapes are authored in the 16x24 design space and rasterized natively at
# 1 or 2 logical pixels per unit, so the 32x48 sprite gets real extra detail.

def character(kind, s):
    w, h = 16 * s, 24 * s
    yy, xx = np.mgrid[0:h, 0:w]
    X = (xx + 0.5) / s
    Y = (yy + 0.5) / s
    img = np.zeros((h, w, 3), np.uint8)
    pid = -np.ones((h, w), int)
    parts = []

    def ell(cx, cy, rx, ry):
        return ((X - cx) / rx) ** 2 + ((Y - cy) / ry) ** 2 <= 1

    def rr(x0, y0, x1, y1, rad=0.0):
        m = (X >= x0) & (X < x1) & (Y >= y0) & (Y < y1)
        if rad:
            for cx_, cy_ in [(x0 + rad, y0 + rad), (x1 - rad, y0 + rad), (x0 + rad, y1 - rad), (x1 - rad, y1 - rad)]:
                corner = (np.abs(X - cx_) > 0) & (((X < x0 + rad) & (cx_ < (x0 + x1) / 2)) | ((X > x1 - rad) & (cx_ > (x0 + x1) / 2)))
                corner &= ((Y < y0 + rad) & (cy_ < (y0 + y1) / 2)) | ((Y > y1 - rad) & (cy_ > (y0 + y1) / 2))
                m &= ~(corner & (((X - cx_) ** 2 + (Y - cy_) ** 2) > rad * rad))
        return m

    def add(m, r, edge=0, k_shadow=None):
        parts.append((m, r, edge, k_shadow))

    if kind == "engineer":
        skin, hair, top, legs = SKIN_ENG, HAIR_ENG, TEALJ, NAVY
        add(rr(5.0, 16.5, 7.7, 22.4), legs)
        add(rr(8.3, 16.5, 11.0, 21.8), legs)
        add(rr(4.6, 21.4, 7.9, 23.2, 0.7), WOOD)
        add(rr(8.1, 20.8, 11.4, 22.6, 0.7), WOOD)
        add(rr(3.7, 10.4, 12.3, 17.6, 1.4), top)
        add(rr(6.9, 10.4, 9.1, 13.4) & (np.abs(X - 8) < 1.25 - (Y - 10.4) * 0.38), PAPER)
        add(rr(2.6, 11.0, 4.6, 16.4, 0.9), top)
        add(rr(11.4, 11.0, 13.4, 16.0, 0.9), top)
        add(ell(3.6, 16.8, 1.0, 0.9), skin)
        add(ell(12.4, 16.4, 1.0, 0.9), skin)
        add(ell(8.0, 6.3, 4.4, 4.5), skin)
        hm = ell(8.0, 5.0, 4.9, 4.3) & (Y < 6.0 + 0.9 * np.cos((X - 8) * 0.9)) | (ell(8.0, 5.5, 4.9, 4.4) & ((X < 4.4) | (X > 11.7)) & (Y < 8.2))
        hm |= ell(10.2, 3.0, 2.6, 1.6)  # swept top
        add(hm, hair, edge=1)
        badge = rr(9.5, 12.8, 10.7, 14.3)
        add(badge, BRASS)
    elif kind == "ivo":
        skin, hair, top, legs = SKIN_IVO, HAIR_IVO, WOOD, NAVY
        add(rr(5.2, 17.2, 7.8, 22.4), legs)
        add(rr(8.2, 17.2, 10.8, 22.4), legs)
        add(rr(4.8, 21.4, 8.0, 23.2, 0.7), INK)
        add(rr(8.0, 21.4, 11.2, 23.2, 0.7), INK)
        add(rr(2.6, 10.2, 13.4, 18.4, 1.8), top)  # broad cardigan
        add(rr(6.6, 10.2, 9.4, 18.0) & (np.abs(X - 8) < 0.8 + (Y - 10.2) * 0.12), OCHRE)
        add(rr(1.8, 11.0, 4.0, 17.4, 1.0), top)
        add(rr(12.0, 11.0, 14.2, 14.6, 1.0), top)
        add(ell(2.9, 17.6, 1.0, 0.9), skin)
        add(rr(11.2, 12.0, 15.2, 15.6, 0.4), GLASS)  # tablet held out
        add(ell(13.0, 15.0, 1.0, 0.8), skin)
        add(ell(8.0, 6.3, 4.3, 4.4), skin)
        hm = ell(8.0, 4.6, 4.8, 3.6) & (Y < 5.6 + 0.6 * np.cos((X - 8) * 0.8))
        hm |= ell(8.0, 5.8, 4.8, 3.9) & ((X < 4.3) | (X > 11.7)) & (Y < 7.6)
        add(hm, hair, edge=1)
    else:  # mira
        skin, hair, top, legs = SKIN_MIRA, HAIR_MIRA, OCHRE, NAVY
        add(rr(4.6, 16.4, 7.2, 21.6), legs)
        add(rr(8.6, 16.8, 11.2, 22.4), legs)
        add(rr(4.0, 20.6, 7.3, 22.4, 0.7), CORAL)
        add(rr(8.4, 21.4, 11.7, 23.2, 0.7), CORAL)
        add(rr(3.8, 10.4, 12.2, 17.2, 1.3), top)
        add(rr(8.0, 10.4, 12.2, 17.2, 1.3), GREEN)  # asymmetric jacket panel
        add(rr(2.7, 10.8, 4.6, 15.8, 0.9), top)
        add(rr(11.4, 10.8, 13.3, 16.2, 0.9), GREEN)
        strap = (np.abs((X - 4.5) - (Y - 10.6) * 1.05) < 0.75) & (Y > 10.4) & (Y < 16.4)
        add(strap, CORAL, k_shadow=1)
        add(rr(10.6, 14.6, 14.6, 18.4, 0.8), CORAL)  # messenger bag
        add(ell(3.6, 16.2, 1.0, 0.9), skin)
        add(ell(8.0, 6.4, 4.3, 4.4), skin)
        hm = ell(8.0, 4.9, 5.1, 4.1) & (Y < 5.8 + 0.7 * np.cos((X - 7) * 0.9))
        hm |= ell(11.3, 2.6, 2.4, 2.2)  # high puff
        hm |= ell(8.0, 6.0, 5.1, 4.2) & ((X < 4.2) | (X > 11.8)) & (Y < 8.8)
        add(hm, hair, edge=1)

    k = 2 if s >= 2 else 1
    for i, (m, r, edge, ks) in enumerate(parts):
        m = m & (pid >= -1)
        shade_mask(img, m, r, k_shadow=ks or k, k_light=1)
        pid[m] = i
    # Occlusion edges: a part darkens where a later (front) part overlaps it.
    for i, (m, r, edge, ks) in enumerate(parts):
        own = pid == i
        front = pid > i
        touch = own & (shifted(front, 1, 0) | shifted(front, -1, 0) | shifted(front, 0, 1) | shifted(front, 0, -1))
        img[touch] = r[0] if edge == 0 else r[1]
    # Hair casts a short shadow on the forehead.
    face_i = [i for i, p in enumerate(parts) if p[1] is skin][-1]
    face = pid == face_i
    hair_m = pid == len(parts) - 1 - (1 if kind == "engineer" else 0)
    img[face & shifted(hair_m, 0, -1)] = skin[1]
    if s >= 2:
        img[face & shifted(hair_m, 0, -2) & ~shifted(hair_m, 0, -1)] = mix(skin[1], skin[2], 0.5)

    # Face details, placed per resolution.
    eye_y = 7.4 if kind != "ivo" else 7.6
    ex = (6.1, 9.9) if kind != "mira" else (6.0, 9.8)
    for x in ex:
        if s == 1:
            img[int(eye_y), int(x)] = INK[0]
        else:
            px, py = int(x * 2), int(eye_y * 2)
            img[py:py + 2, px:px + 2] = INK[0]
            img[py, px + 1] = INK[2]
            img[py - 2, px - 1:px + 2] = (hair[0] if kind != "ivo" else hair[0])  # brows
    if s >= 2:
        mx, my = 16, int(9.3 * 2)
        img[my, mx - 1:mx + 2] = skin[0]
        img[my - 3, 15:17] = skin[1]  # nose shadow
        img[int(8.6 * 2), 10:12] = mix(skin[2], CORAL[2], 0.45)  # cheeks
        img[int(8.6 * 2), 20:22] = mix(skin[2], CORAL[2], 0.45)
        if kind == "ivo":
            img[int(14.2 * 2):int(14.2 * 2) + 1, 24:29] = GLASS[3]
            img[int(13.2 * 2), 24:30] = hx("#19AFA2")
        if kind == "engineer":
            img[int(10.6 * 2):int(12.8 * 2), 20] = BRASS[1]  # lanyard
    opaque = pid >= 0
    # Selective outline: lit top-left edges use the part's dark tone.
    ring = (shifted(opaque, 1, 0) | shifted(opaque, -1, 0) | shifted(opaque, 0, 1) | shifted(opaque, 0, -1)) & ~opaque
    out = img.copy()
    alpha = opaque.copy()
    for (dx, dy) in [(1, 0), (0, 1), (-1, 0), (0, -1)]:
        nb = ring & shifted(opaque, dx, dy)
        src_id = shifted_ids(pid, dx, dy)
        for y, x in zip(*np.nonzero(nb & ~alpha)):
            r = parts[src_id[y, x]][1]
            lit_side = dx > 0 or dy > 0  # outline pixel sits above/left of the form
            out[y, x] = r[0] if lit_side else INK[0]
            alpha[y, x] = True
    rgba = np.dstack([out, alpha.astype(np.uint8) * 255])
    return rgba


def shifted_ids(a, dx, dy):
    h, w = a.shape
    out = -np.ones_like(a)
    ys0, ys1 = max(0, -dy), min(h, h - dy)
    xs0, xs1 = max(0, -dx), min(w, w - dx)
    out[ys0:ys1, xs0:xs1] = a[ys0 + dy:ys1 + dy, xs0 + dx:xs1 + dx]
    return out


def place(c, sprite, foot_x, foot_y):
    """Paste a sprite with its feet (bottom-centre) at a cell coordinate."""
    t = c.t
    h, w = sprite.shape[:2]
    # Contact shadow first.
    sh = c.ellipse(foot_x, foot_y - 0.06, 0.42, 0.13)
    c.shadow(sh, 0.5)
    x0 = c.px(foot_x) - w // 2
    y0 = c.px(foot_y) - h
    a = sprite[:, :, 3] > 0
    region = c.img[y0:y0 + h, x0:x0 + w]
    region[a] = sprite[:, :, :3][a]


# ---------------------------------------------------------------- scene

def scene(t):
    c = Canvas(20, 11.25, t)
    s = t // 16
    floor(c)
    north_wall(c)
    east_wall(c)
    pot_plant(c, 0.15, 1.75)
    pot_plant(c, 12.85, 1.75)
    pot_plant(c, 17.9, 1.75)
    printer(c)
    desk(c, 1.0, 4.9)
    desk(c, 15.4, 3.0, monitor=True)
    bench(c, 14.2, 6.6)
    planter(c)
    place(c, character("ivo", s), 8.0, 3.95)
    place(c, character("engineer", s), 13.4, 9.1)
    place(c, character("mira", s), 17.1, 9.55)
    mail_counter(c, 15.4, 9.35)
    marker(c, "talk", 8.0, 1.95)
    marker(c, "terminal", 10.15, 1.15)
    marker(c, "route", 18.9, 4.95)
    marker(c, "glitch", 3.6, 3.4)
    return c


def font(size, mono=False, bold=False):
    if mono:
        return ImageFont.truetype("/System/Library/Fonts/SFNSMono.ttf", size)
    path = "/System/Library/Fonts/HelveticaNeue.ttc"
    return ImageFont.truetype(path, size, index=1 if bold else 0)


def keycap(d, x, y, w, label, held=False, size=26):
    h = 52
    d.rounded_rectangle([x, y + 4, x + w, y + h + 4], 9, fill="#0F1522")
    d.rounded_rectangle([x, y, x + w, y + h], 9, fill="#F4F2EC" if not held else "#19AFA2",
                        outline="#19AFA2" if held else "#C7CBD1", width=2)
    f = font(size, bold=True)
    tw = d.textlength(label, font=f)
    d.text((x + (w - tw) / 2, y + (h - size) / 2 - 2), label, font=f, fill="#182B38")


def ui_overlay(screen, vx, vy, vw, vh):
    d = ImageDraw.Draw(screen)
    # Objective HUD.
    d.rounded_rectangle([vx + 20, vy + 18, vx + 470, vy + 66], 10, fill=(24, 43, 56, 235))
    d.text((vx + 38, vy + 29), "Visit the four desks", font=font(21, bold=True), fill="#F4F2EC")
    d.text((vx + 285, vy + 31), "2 / 4   ·   Seals 0", font=font(18), fill="#A0DDD4")
    # Keyboard teaching inset: key position, hold order, output, effect.
    x0, y0, x1, y1 = vx + 20, vy + vh - 214, vx + 500, vy + vh - 20
    d.rounded_rectangle([x0, y0, x1, y1], 14, fill=(24, 43, 56, 242), outline="#19AFA2", width=2)
    d.text((x0 + 22, y0 + 16), "Move west", font=font(22, bold=True), fill="#F4F2EC")
    labels = [("KEY POSITION", x0 + 22), ("OUTPUT", x0 + 262), ("EFFECT", x0 + 362)]
    for lab, lx in labels:
        d.text((lx, y0 + 58), lab, font=font(13, bold=True), fill="#9FB3BD")
    keycap(d, x0 + 22, y0 + 84, 104, "Caps", held=True, size=22)
    d.text((x0 + 138, y0 + 98), "+", font=font(26, bold=True), fill="#F4F2EC")
    keycap(d, x0 + 166, y0 + 84, 60, "H")
    d.text((x0 + 262, y0 + 88), "←", font=font(34, mono=True), fill="#F4F2EC")
    d.text((x0 + 262, y0 + 130), "Left arrow", font=font(15), fill="#C5CED0")
    d.text((x0 + 362, y0 + 92), "Step west", font=font(19, bold=True), fill="#E6B750")
    d.text((x0 + 22, y0 + 156), "Hold Caps, then tap H. Release Caps to type.", font=font(16), fill="#C5CED0")
    # Contextual prompt next to Ivo.
    px_, py_ = vx + int(8.0 * 64) + 40, vy + int(2.6 * 64)
    d.rounded_rectangle([px_, py_, px_ + 132, py_ + 34], 8, fill=(24, 43, 56, 235))
    d.rounded_rectangle([px_ + 8, py_ + 6, px_ + 52, py_ + 28], 5, fill="#F4F2EC")
    d.text((px_ + 13, py_ + 8), "Caps", font=font(13, bold=True), fill="#182B38")
    d.text((px_ + 58, py_ + 7), "+N  Talk", font=font(16, bold=True), fill="#F4F2EC")


def build():
    results = {}
    for t, zoom in [(16, 4), (32, 2)]:
        c = scene(t)
        native = Image.fromarray(c.img[: int(180 * t / 16), : int(320 * t / 16)])
        native.save(os.path.join(OUT, f"orientation-{t}px-native.png"))
        vw, vh = 1280, 720
        scaled = native.resize((native.width * zoom, native.height * zoom), Image.NEAREST).crop((0, 0, vw, vh))
        screen = Image.new("RGBA", (1366, 768), "#151C2B")
        vx, vy = (1366 - vw) // 2, (768 - vh) // 2
        screen.paste(scaled, (vx, vy))
        overlay = Image.new("RGBA", screen.size, (0, 0, 0, 0))
        ui_overlay(overlay, vx, vy, vw, vh)
        screen = Image.alpha_composite(screen, overlay).convert("RGB")
        screen.save(os.path.join(OUT, f"orientation-{t}px-1366x768.png"))
        results[t] = (native, scaled)
    # Detail sheet: same screen region, both densities, plus sprites at 1x/8x.
    sheet = Image.new("RGB", (1366, 900), "#151C2B")
    d = ImageDraw.Draw(sheet)
    d.text((24, 18), "Same screen size, different pixel density (crop of the 1366x768 screen at 100%)", font=font(20, bold=True), fill="#F4F2EC")
    for i, t in enumerate((16, 32)):
        crop = results[t][1].crop((640, 300, 1280, 720))
        sheet.paste(crop, (24 + i * 671, 60))
        d.text((24 + i * 671, 488), f"{t} px tiles · {'16×24' if t == 16 else '32×48'} people · ×{4 if t == 16 else 2}", font=font(18, bold=True), fill="#E6B750")
    d.text((24, 530), "Native sprites (1×) and nearest-neighbour enlargements", font=font(20, bold=True), fill="#F4F2EC")
    x = 24
    for t, s in ((16, 1), (32, 2)):
        for kind in ("engineer", "ivo", "mira"):
            sp = Image.fromarray(character(kind, s), "RGBA")
            big = sp.resize((sp.width * (8 // s), sp.height * (8 // s)), Image.NEAREST)
            bg = Image.new("RGBA", (big.width + 16, big.height + 16), tuple(FLOOR) + (255,))
            bg.alpha_composite(big, (8, 8))
            sheet.paste(bg.convert("RGB"), (x, 580))
            nb = Image.new("RGBA", (sp.width + 8, sp.height + 8), tuple(FLOOR) + (255,))
            nb.alpha_composite(sp, (4, 4))
            sheet.paste(nb.convert("RGB"), (x, 580 + big.height + 24))
            x += big.width + 30
        x += 40
    sheet.save(os.path.join(OUT, "scale-comparison.png"))


if __name__ == "__main__":
    build()
