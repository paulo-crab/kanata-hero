"""Mock 2 art: the '08 finish' draft. A vivid extended palette plus leaf-fan foliage, blue planters,
garden benches and white flowers. Drop-in replacements for functions in gate1/environment.py.
DRAFT for board validation; it is not approved and breaks two current style-bible rules (see the note).
"""
import math
import random

import numpy as np

import build_scale_test as bst

H = bst.hx

# Foliage: outline, then five tones (08's leaves run from deep green to a yellow-green highlight).
FOL = [H(x) for x in ("#0B2B17", "#134A22", "#1F7A2B", "#3FA832", "#7BD23C", "#C4F061")]
POT = [H(x) for x in ("#16223C", "#26395E", "#3D5C8E")]
ORANGE = H("#E8892B")
PETAL, PETAL_SHADE, SOIL = H("#FFF6EA"), H("#E9D2C0"), H("#5A3418")

# Base-ramp -> vivid-ramp remap, applied to the finished frame (exact colour matches only).
REMAP = {
    "INK": ("#202337 #343650 #535971 #777A8C", "#0E1020 #1C2038 #3A4160 #6A7392"),
    "WOOD": ("#523D4C #85565A #BA785F #E4AA73", "#3A2216 #7C4220 #B8671F #E69A3A"),
    "GLASS": ("#203A50 #366479 #5AA3AE #A0DDD4", "#0F3550 #1D7396 #3CBAD6 #A8F0EE"),
    "GREEN": ("#21484A #326D60 #5FA06D #B2CE78", "#134A22 #1F7A2B #3FA832 #7BD23C"),
    "BRASS": ("#705056 #AC7655 #E1AC62 #F5D580", "#7A4A2A #C98A3A #FFC83D #FFF0A0"),
    "CORAL": ("#71394F #B65761 #E67A70 #F6B18E", "#7A2E40 #C8485A #F26A5A #FFB38A"),
}


def remap(a):
    out = a.copy()
    for old, new in REMAP.values():
        for o, n in zip(old.split(), new.split()):
            out[np.all(a == H(o), axis=2)] = H(n)
    return out


def leaves_v2(r, cx, cy, rad, seed, ramp=None, count=5, spread=None, clip=None, tone_shift=0):
    """A fan of pointed leaves: dark outline, five tones lit from the upper left, a vein, painter's order."""
    if rad > 7:
        rnd0 = random.Random(seed * 7 + 1)
        whole = np.zeros(r.img.shape[:2], bool)
        for k in range(5):
            a0 = 2 * math.pi * k / 5 + rnd0.uniform(-0.4, 0.4)
            dist = rad * (0.0 if k == 0 else 0.62)
            whole |= leaves_v2(r, cx + math.cos(a0) * dist, cy + math.sin(a0) * dist * 0.8, rad * 0.58,
                               seed * 11 + k, count=5, clip=clip)
        return whole
    rnd = random.Random(seed)
    spread = spread or rad * 0.9
    n = count + 2
    leaves = []
    for i in range(n):
        ang = 2 * math.pi * i / n + rnd.uniform(-0.18, 0.18)
        d = spread * rnd.uniform(0.0, 0.28)
        leaves.append((cy + math.sin(ang) * d * 0.8, cx + math.cos(ang) * d, ang, rad * rnd.uniform(0.95, 1.25)))
    leaves.sort()
    X, Y = r.x, r.y
    whole = np.zeros(r.img.shape[:2], bool)
    for py, px, ang, L in leaves:
        ca, sa = math.cos(ang), math.sin(ang)
        u = (X - px) * ca + (Y - py) * sa
        v = -(X - px) * sa + (Y - py) * ca
        t = np.clip(u / L, 0, 1)
        W = L * 0.36
        m = (u >= 0) & (u <= L) & (np.abs(v) <= W * np.sin(np.pi * t) ** 0.75 + 0.35)
        if clip is not None:
            m &= clip
        if not m.any():
            continue
        lit = ((X - px) * -0.7 + (Y - py) * -0.7) / max(L, 1)
        ring = r.edge(m)
        tone = np.full(m.shape, 3)
        tone[lit > 0.05] = 4
        tone[(lit > 0.45) | (t > 0.82)] = 5
        tone[lit < -0.25] = 2
        tone[lit < -0.6] = 1
        vein = m & (np.abs(v) < 0.5) & (t > 0.18) & (t < 0.72)
        tone = np.maximum(1, tone - tone_shift)
        for k in range(1, 6):
            r.img[m & (tone == k)] = FOL[k]
        r.img[vein] = FOL[max(1, 2)]
        outside = (shift4(m) & ~m)
        if clip is not None:
            outside &= clip
        r.img[outside & ~whole] = FOL[0]       # dark edge against what lies behind
        r.img[ring & (lit < 0.3)] = FOL[1]     # shaded edge, no hard ring on the lit side
        whole |= m
    return whole


def shift4(m):
    out = np.zeros_like(m)
    out[:, 1:] |= m[:, :-1]
    out[:, :-1] |= m[:, 1:]
    out[1:, :] |= m[:-1, :]
    out[:-1, :] |= m[1:, :]
    return out


def pot_v2(r, x, y, seed):
    """Blue planter with a leaf fan and an orange accent, like the planters in 08."""
    r.cast(x, x + 12, y + 12)
    pot = r.mask(x, y + 4, x + 12, y + 12)
    r.img[pot] = POT[1]
    r.rect(x, y + 4, x + 12, y + 6, POT[2])
    r.rect(x, y + 4, x + 1, y + 12, POT[2])
    r.rect(x, y + 11, x + 12, y + 12, POT[0])
    r.outline(pot)
    r.rect(x + 2, y + 4, x + 10, y + 5, SOIL)
    leaves_v2(r, x + 6, y + 1, 6.5, seed, count=6, spread=6)
    r.img[y + 3, x + 4] = ORANGE
    r.img[y + 3, x + 8] = ORANGE


def bench_v(r, x0, y0, w, h):
    """Vertical-plank park bench for the garden sides (08 has one each side)."""
    r.cast(x0, x0 + w, y0 + h)
    body = r.mask(x0, y0, x0 + w, y0 + h)
    r.img[body] = H("#B8671F")
    for px in range(x0 + 2, x0 + w - 1, 3):
        r.rect(px, y0 + 1, px + 1, y0 + h - 1, H("#7C4220"))
    r.rect(x0 + 1, y0, x0 + 2, y0 + h, H("#E69A3A"))
    r.outline(body)


def flower(r, x, y):
    r.img[y - 1, x] = PETAL
    r.img[y + 1, x] = PETAL_SHADE
    r.img[y, x - 1] = PETAL
    r.img[y, x + 1] = PETAL_SHADE
    r.img[y, x] = ORANGE


ROCK = [H(x) for x in ("#2B2F3A", "#565B66", "#8A8F99", "#B8BDC6")]
BARK = [H(x) for x in ("#3A2216", "#7C4220", "#B8671F", "#E69A3A")]


def rock(room, cx, cy, rr, bed):
    m = room.blob(cx, cy, rr, 1.0, lobes=4, amp=0.12) & bed
    bst.shade_mask(room.img, m, ROCK, k_shadow=1, k_light=1)
    room.img[m & ~bst.shifted(m, -1, -1)] = ROCK[3]
    room.outline(m, ROCK[0])


def trunk(room):
    """Root flare and two limbs, lit from the upper left (08's tree has visible roots)."""
    cx = 133
    rows = {96: 4, 98: 4, 100: 5, 102: 5, 104: 6, 106: 6, 108: 7, 110: 8, 112: 10, 114: 12}
    m = np.zeros(room.img.shape[:2], bool)
    for y, w in rows.items():
        m[y:y + 2, cx - w // 2: cx + (w + 1) // 2] = True
    for dx in (-1, 1):                                    # roots creeping out along the bed
        for t in range(5):
            m[113 + t // 2, cx + dx * (6 + t)] = True
            m[114 + t // 2, cx + dx * (6 + t)] = True
    bst.shade_mask(room.img, m, BARK, k_shadow=2, k_light=1)
    room.outline(m, BARK[0])


def finish_art(c, room):
    """Garden dressing drawn over the finished room: trunk, rocks, benches, white flowers."""
    a = room.img
    bed = np.zeros(a.shape[:2], bool)
    bed[82:128, 100:172] = True
    old_shadow = np.all(a == bst.INK[1], axis=2) & bed     # canopy shadow on the bed: dark green, not navy
    a[old_shadow] = FOL[0]
    for col in bst.INK:                                    # the flat navy rocks give way to grey ones
        a[np.all(a == col, axis=2) & bed] = FOL[1]
    trunk(room)
    rock(room, 111, 113, 5, bed)
    rock(room, 161, 108, 4, bed)
    bench_v(room, 84, 94, 10, 28)
    bench_v(room, 178, 94, 10, 28)
    for fx, fy in [(104, 112), (106, 120), (168, 110), (124, 121), (162, 121), (146, 90)]:
        flower(room, fx, fy)
