"""Rich finish: the shared drawing code (RICH_FINISH_SPEC.md sections 1 to 3).

Promoted from the reference implementation in ../rich-finish/ (art_v2.py, art_v4.py). Kits and
gate1/environment.py call it; nothing copies the mock scripts. Everything here draws onto an
env.Room (needs r.img, r.x, r.y, r.rect, r.mask, r.outline, r.cast, r.edge) with hard pixels and
flat steps, light from the upper left.

Leaf fans take a district foliage ramp (4 steps, shadow -> light) and add the district's edge
and tip tones (palettes/district_palettes.py FOLIAGE_EXTRA), so every district keeps its own
greens and gains the five-tone fan.
"""
import math
import os
import random
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "palettes"))
import district_palettes as dp  # noqa: E402


def hx(s):
    s = s.lstrip("#")
    return np.array([int(s[i:i + 2], 16) for i in (0, 2, 4)], dtype=np.uint8)


# Blue planters, mulch and accents (RICH_EXTRAS in district_palettes.py)
POT = [hx(h) for h in dp.RICH_EXTRAS["planter"]]
POT_LIP = hx(dp.RICH_EXTRAS["planter_lip"][0])
POT_BOLT = hx(dp.RICH_EXTRAS["planter_bolt"][0])
MULCH = [hx(h) for h in dp.RICH_EXTRAS["mulch"]]  # soil, mulch, orange fleck


def fan_palette(ramp):
    """[edge, t1, t2, t3, t4, tip] for a 4-step foliage ramp of RGB triples."""
    key = tuple(int(v) for v in ramp[0])
    for d, pal in dp.DISTRICTS.items():
        if tuple(int(v) for v in hx(pal["foliage"][0])) == key:
            ex = dp.FOLIAGE_EXTRA[d]
            return [hx(ex["edge"])] + [hx(h) for h in pal["foliage"]] + [hx(ex["tip"])]
    # an unknown ramp (a clipped or tinted variant): derive a tip and an edge
    lift = lambda c, k: np.clip(c.astype(int) + k, 0, 255).astype(np.uint8)  # noqa: E731
    return [lift(ramp[0], -22)] + [np.asarray(c, np.uint8) for c in ramp] + [lift(ramp[3], 40)]


def _shift4(m):
    out = np.zeros_like(m)
    out[:, 1:] |= m[:, :-1]
    out[:, :-1] |= m[:, 1:]
    out[1:, :] |= m[:-1, :]
    out[:-1, :] |= m[1:, :]
    return out


def fan(r, cx, cy, rad, seed, P, count=5, spread=None, clip=None, tone_shift=0):
    """A fan of count + 2 pointed leaves: dark edge, five tones lit from the upper left, a vein, painter's order."""
    if rad > 7:  # large canopies are several smaller fans
        rnd0 = random.Random(seed * 7 + 1)
        whole = np.zeros(r.img.shape[:2], bool)
        for k in range(5):
            a0 = 2 * math.pi * k / 5 + rnd0.uniform(-0.4, 0.4)
            dist = rad * (0.0 if k == 0 else 0.62)
            whole |= fan(r, cx + math.cos(a0) * dist, cy + math.sin(a0) * dist * 0.8, rad * 0.58,
                         seed * 11 + k, P, count=5, clip=clip)
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
            r.img[m & (tone == k)] = P[k]
        r.img[vein] = P[2]
        outside = _shift4(m) & ~m
        if clip is not None:
            outside &= clip
        r.img[outside & ~whole] = P[0]       # dark edge against what lies behind
        r.img[ring & (lit < 0.3)] = P[1]     # shaded edge, no hard ring on the lit side
        whole |= m
    return whole


def sparkles(r, mask, seed, P):
    """Sun catching leaf tips: a third of the upper-left edge pixels (x + y divisible by 3, so the pattern moves
    with the plant by whole 3 px steps, as the desk-front occluders require) become the tip tone."""
    edge = mask & ~np.roll(np.roll(mask, 1, 0), 1, 1)
    r.img[edge & ((r.x.astype(int) + r.y.astype(int)) % 3 == 0)] = P[5]


def leaves(r, cx, cy, rad, seed, ramp, count=5, spread=None, clip=None):
    """Two layers (a shaded back layer, then the lit front layer) with sparkle tips. Returns the leaf mask."""
    P = fan_palette(ramp)
    if rad > 7:  # large canopy: seven smaller fans, each with a back and a front layer
        rnd = random.Random(seed * 13 + 5)
        whole = np.zeros(r.img.shape[:2], bool)
        for k in range(7):
            a0 = 2 * math.pi * k / 7 + rnd.uniform(-0.4, 0.4)
            dist = rad * (0.0 if k == 0 else 0.68)
            fx, fy = cx + math.cos(a0) * dist, cy + math.sin(a0) * dist * 0.8
            whole |= fan(r, fx, fy, rad * 0.5, seed * 11 + k, P, count=5, clip=clip, tone_shift=1)
            whole |= fan(r, fx - 0.8, fy - 0.8, rad * 0.46, seed * 17 + k, P, count=5, clip=clip)
        sparkles(r, whole, seed, P)
        return whole
    back = fan(r, cx + 0.6, cy + 0.6, rad * 0.9, seed + 91, P, count=count, spread=spread, clip=clip, tone_shift=1)
    front = fan(r, cx, cy, rad, seed, P, count=count + 1, spread=spread, clip=clip)
    sparkles(r, front, seed, P)
    return back | front


def planter(r, x, y, seed, ramp):
    """Blue planter: lit lip, shaded right side and base, a metal band with two bolts, orange mulch, a leaf fan."""
    r.cast(x, x + 12, y + 12)
    pot = r.mask(x, y + 4, x + 12, y + 12)
    r.img[pot] = POT[1]
    r.rect(x, y + 4, x + 12, y + 6, POT[2])
    r.rect(x + 1, y + 4, x + 11, y + 5, POT_LIP)
    r.rect(x, y + 4, x + 1, y + 12, POT[2])
    r.rect(x + 11, y + 6, x + 12, y + 12, POT[0])
    r.rect(x, y + 11, x + 12, y + 12, POT[0])
    r.rect(x + 1, y + 8, x + 11, y + 9, POT[0])
    for bx in (x + 2, x + 9):
        r.img[y + 7, bx] = POT_BOLT
    r.outline(pot)
    r.rect(x + 2, y + 5, x + 10, y + 6, MULCH[1])
    r.img[y + 5, x + 4] = MULCH[2]
    r.img[y + 5, x + 7] = MULCH[2]
    leaves(r, x + 6, y + 1, 6.5, seed, ramp, count=6, spread=6)


def extend(m):
    """Complete an exact-hex recolour map (UPPER hex -> UPPER hex) for the rich-finish sprites: the Orientation
    leaf-fan edge and tip tones follow the destination foliage ramp, and the planter, mulch, rock, moss and flower
    colours pass through unchanged. Returns a new dict; existing entries win."""
    out = dict(m)
    O = dp.DISTRICTS["orientation"]["foliage"]
    if all(h.upper() in m for h in O):
        P = fan_palette([hx(m[h.upper()]) for h in O])
        ex = dp.FOLIAGE_EXTRA["orientation"]
        out.setdefault(ex["edge"].upper(), "#%02X%02X%02X" % tuple(P[0]))
        out.setdefault(ex["tip"].upper(), "#%02X%02X%02X" % tuple(P[5]))
    for steps in dp.RICH_EXTRAS.values():
        for h in steps:
            out.setdefault(h.upper(), h.upper())
    return out
