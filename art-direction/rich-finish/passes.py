"""Richness passes for the director's mock-ups. DRAFTS to validate with the board, not approved art.

Every pass works on the native 320x192 array and keeps hard pixels: no blur, no gradients, only
flat colour steps. Floor-only passes read the pixel colour, so they never touch props or actors.
"""
import numpy as np

import build_scale_test as bst

FLOOR = [tuple(bst.STONE[i]) for i in (3, 2, 1)]  # plain floor, joints, inlay band
WALL_Y = 34  # first floor row below the north wall


def floor_mask(a, extra=()):
    m = np.zeros(a.shape[:2], bool)
    for c in list(FLOOR) + list(extra):
        m |= np.all(a == np.array(c, np.uint8), axis=2)
    m[:WALL_Y] = False
    return m


def shift(m, dx, dy):
    out = np.zeros_like(m)
    h, w = m.shape
    ys, xs = slice(max(0, dy), min(h, h + dy)), slice(max(0, dx), min(w, w + dx))
    yo, xo = slice(max(0, -dy), min(h, h - dy)), slice(max(0, -dx), min(w, w - dx))
    out[ys, xs] = m[yo, xo]
    return out


def tint(a, mask, mul=(1, 1, 1), add=(0, 0, 0)):
    f = a[mask].astype(np.float32) * np.array(mul, np.float32) + np.array(add, np.float32)
    a[mask] = np.clip(f, 0, 255).astype(np.uint8)


def slab_variation(a, seed=3, grain=True):
    """Per-slab tone drift on the 32 px running-bond slabs, plus sparse grain (08's floor is never uniform)."""
    rnd = np.random.RandomState(seed)
    base = np.array(FLOOR[0], np.uint8)
    f = np.all(a == base, axis=2)
    f[:WALL_Y] = False
    for row in range(0, 192, 32):
        off = 16 if (row // 32) % 2 else 0
        for col in range(off - 32, 320, 32):
            m = np.zeros_like(f)
            m[max(0, row + 1):row + 32, max(0, col + 1):col + 32] = True
            m &= f
            roll = rnd.rand()
            if roll < 0.28:
                tint(a, m, add=(-7, -9, -12))
            elif roll < 0.5:
                tint(a, m, add=(5, 5, 4))
    if grain:
        g = floor_mask(a)
        tint(a, g & (rnd.rand(*g.shape) < 0.018), add=(-14, -16, -20))
    return a


def cast_shadows(a, mask_objects, dx=4, dy=3, mul=(0.80, 0.78, 0.86)):
    """Flat shadow patches on the floor, offset away from the upper-left light."""
    floor = floor_mask(a)
    obj = mask_objects & ~floor
    obj[:WALL_Y] = False
    sh = shift(obj, dx, dy) & shift(obj, dx // 2, dy // 2) & floor
    tint(a, sh, mul=mul)
    return a


def lamp_glow(a, lamps, r_out=26, r_in=12, add_out=(9, 6, -3), add_in=(16, 11, -6)):
    """Two hard-edged warm steps around each lamp, on floor pixels only (STYLE_BIBLE §7: one or two steps)."""
    floor = floor_mask(a) | np.all(a == np.array(bst.BRASS[3], np.uint8), axis=2)
    yy, xx = np.mgrid[0:a.shape[0], 0:a.shape[1]]
    for cx, cy in lamps:
        d = np.hypot(xx - cx, (yy - cy) * 1.25)
        tint(a, floor & (d < r_out) & (d >= r_in), add=add_out)
        tint(a, floor & (d < r_in), add=add_in)
    return a


def light_shafts(a, windows, slope=0.5, y_end=150, add=(11, 9, 2), add_core=(9, 7, 1)):
    """Sun through the north windows: diagonal bands on the floor, two flat steps."""
    floor = floor_mask(a)
    yy, xx = np.mgrid[0:a.shape[0], 0:a.shape[1]]
    for x0, w in windows:
        shift_x = (yy - WALL_Y) * slope
        band = (xx >= x0 + shift_x) & (xx < x0 + w + shift_x) & (yy < y_end)
        core = (xx >= x0 + shift_x + w * 0.25) & (xx < x0 + w * 0.75 + shift_x) & (yy < y_end)
        tint(a, floor & band, add=add)
        tint(a, floor & core, add=add_core)
    return a


def vignette_steps(a, strength=(0.93,), margin=(9,)):
    """Stepped edge darkening for depth (hard bands, never a gradient)."""
    h, w = a.shape[:2]
    yy, xx = np.mgrid[0:h, 0:w]
    edge = np.minimum.reduce([xx, w - 1 - xx, yy - 0, (180 - 1 - yy)])
    for m, s in zip(margin[::-1], strength[::-1]):
        tint(a, (edge < m) & (yy < 180), mul=(s, s, s * 1.02))
    return a
