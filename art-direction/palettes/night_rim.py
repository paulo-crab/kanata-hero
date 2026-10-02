"""The Night Shift people rim: one reference implementation (player decisions 2026-10-02, PALETTES_SPEC rule 1).

People in Night Shift get light on their lit (upper-left) silhouette by a per-pixel rule that looks at what is
actually behind the sprite. Cool moonlight on the open floor; where a warm source lights someone, the warm edge
is limited to the head and shoulders (sprite rows 0 to WARM_RIM_ROWS - 1).

  For each upper-left silhouette pixel (an opaque pixel with a transparent pixel above or to its left), the
  background behind it is the scene pixel at that transparent neighbour (above, else left; a neighbour outside
  the frame counts as the scene pixel under the pixel itself).

  1. Moonlight (the open floor, and the body rows everywhere). Recolour the pixel to the cool rim
     `dp.NIGHT_RIM` (#8E96B8, glass step 2) only if
       (a) it is #202337, or its own contrast against that background is below 3:1, AND
       (b) the rim contrasts with that background MORE than the pixel's current colour does.
     On the slate floor (#4C5865: rim 2.49:1 vs ink 2.13:1) the cool rim appears; on a warm lamp pool the
     moonlight loses to the ink outline (rim 1.27:1 vs ink 4.19:1) so the ink stays.
  2. Warm light (a lamp pool, WARM_RIM_ROWS). Where the background is a warm lamp-pool colour (Night Shift
     accent steps 0 and 1, `POOL_COLOURS`) and the pixel is on sprite rows 0..WARM_RIM_ROWS-1 (head and
     shoulders), an ink pixel (or a pixel below 3:1 that the warm rim improves) becomes the warm rim
     `WARM_RIM` (#F9D79A, accent step 3) when that reaches at least WARM_MIN:1 against the pool (2.68:1 on
     #B8745A). Rows WARM_RIM_ROWS..23 fall through to rule 1 and keep the ink outline.

Pixels that are already the rim colours, and Ada's baked lantern rim (key R, #F9D79A, now baked on her head and
shoulders only), are never touched. The landmark's coworker silhouettes behind the lit break-room window keep
a warm rim of their own (nightshift_kit.draw_figs): they are backlit by the lit room.

No side effects and numpy only, so the palette builds, the Ada room and the kit can all import it.
`nightshift_kit.night_rim` is this function.
"""
import numpy as np

import district_palettes as dp  # noqa: E402  (pure data)

INK = (0x20, 0x23, 0x37)
_ACC = dp.DISTRICTS["nightshift"]["accent"]
WARM_RIM = _ACC[3]                          # #F9D79A, accent step 3: the warm edge of a lamp pool or a lantern
POOL_COLOURS = {tuple(int(h[i:i + 2], 16) for i in (1, 3, 5)) for h in _ACC[:2]}   # pool fill (step 1) and joints (step 0)
BAKED_LANTERN_RIM = tuple(int(WARM_RIM[i:i + 2], 16) for i in (1, 3, 5))            # Ada's key R: never recoloured
MIN_CONTRAST = 3.0
WARM_RIM_ROWS = 13     # sprite rows 0-12 are the head and shoulders; the warm edge is limited to them
WARM_MIN = 2.5         # the warm rim must reach this against the pool to be used


def hex2rgb(h):
    """'#RRGGBB' (or an RGB triple, returned as ints) to an (r, g, b) tuple."""
    if isinstance(h, str):
        return tuple(int(h[i:i + 2], 16) for i in (1, 3, 5))
    return tuple(int(v) for v in h)


def _lin(c):
    c = np.asarray(c, float) / 255.0
    return np.where(c <= 0.03928, c / 12.92, ((c + 0.055) / 1.055) ** 2.4)


def luminance(rgb):
    r, g, b = _lin(rgb)
    return float(0.2126 * r + 0.7152 * g + 0.0722 * b)


def contrast(a, b):
    """WCAG contrast ratio of two colours (hex strings, RGB triples or arrays)."""
    a, b = hex2rgb(a), hex2rgb(b)
    la, lb = luminance(a), luminance(b)
    return (max(la, lb) + 0.05) / (min(la, lb) + 0.05)


def flat(rim_like_shape, bg_hex):
    """A flat background patch the size of a sprite frame, for a flat floor or pool colour."""
    h, w = rim_like_shape[:2]
    patch = np.empty((h, w, 3), np.uint8)
    patch[:] = hex2rgb(bg_hex)
    return patch


def upper_left_background(sprite, background):
    """Yield (y, x, bg_rgb) for every upper-left silhouette pixel of the sprite."""
    a = sprite[:, :, 3] > 0
    h, w = a.shape
    for y, x in zip(*np.nonzero(a)):
        if y == 0 or not a[y - 1, x]:
            yield y, x, background[y - 1, x] if y > 0 else background[y, x]
        elif x == 0 or not a[y, x - 1]:
            yield y, x, background[y, x - 1] if x > 0 else background[y, x]


def night_rim(sprite_rgba, background_rgb_patch, rim_hex):
    """Return a copy of the sprite with the Night Shift rim applied by the per-pixel rules above
    (moonlight `rim_hex`; warm head-and-shoulders rim over lamp pools).

    sprite_rgba: HxWx4 uint8. background_rgb_patch: HxWx3 uint8, the scene region under the sprite frame."""
    out = sprite_rgba.copy()
    rim = np.array(hex2rgb(rim_hex), np.uint8)
    for y, x, bg in upper_left_background(sprite_rgba, background_rgb_patch):
        c = tuple(int(v) for v in sprite_rgba[y, x, :3])
        if c == BAKED_LANTERN_RIM or c == tuple(int(v) for v in rim):
            continue
        cur = contrast(c, bg)
        if not (c == INK or cur < MIN_CONTRAST):
            continue
        if y < WARM_RIM_ROWS and tuple(int(v) for v in bg) in POOL_COLOURS:
            warm = contrast(BAKED_LANTERN_RIM, bg)
            if warm >= WARM_MIN and (c == INK or warm > cur):
                out[y, x, :3] = BAKED_LANTERN_RIM
                continue
        if contrast(rim, bg) > cur:
            out[y, x, :3] = rim
    return out


def night_rim_on_scene(scene, sprite_rgba, ax, ay, rim_hex):
    """night_rim for a 16x24 person placed with its anchor at (ax, ay) (the place_px convention): the background
    patch is the scene region under the frame, read before the sprite is pasted."""
    h, w = sprite_rgba.shape[:2]
    x0, y0 = ax - w // 2, ay - h
    return night_rim(sprite_rgba, scene[y0:y0 + h, x0:x0 + w, :3], rim_hex)
