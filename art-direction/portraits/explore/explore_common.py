"""Shared helper for the portrait style exploration (48x48, three directions).

Status: exploration, not a rollout. The current portraits (../portrait_*.py) are untouched.

Every portrait is composed from layers, back to front: body (+ neck), head, hair, face stamps.
Body and head are written as per-row span tables (hand-placed numbers), hair as run-length rows
(`R`), face features as small character stamps. Outlines (#202337, key `o`) are added around each
layer as it is painted, so the silhouette is closed by construction: the body and hair take an
outline only toward transparency, the head also takes one over the body (the chin line).

Tokens used while composing (mapped to real sprite keys by `finish`):
  1 skin fill   2 skin shade   3 skin light   7 deep shade   4 blush   5 eye highlight   6 mouth interior
  B brow key    o outline ink
Hair and clothing are written with the sprite's own keys.
"""
import os
import sys

import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
for sub in ("gate1", "cast", "scale-test", "portraits"):
    sys.path.insert(0, os.path.join(HERE, "..", "..", sub))
import build_scale_test as bst  # noqa: E402
import build_gate1 as g1  # noqa: E402
import engineer_sprites as eng  # noqa: E402
import ivo_sprites as ivo  # noqa: E402
import mira_sprites as mira  # noqa: E402

W = H = 48
OUTLINE = "#202337"
MARKERS = {"#19AFA2", "#EC776D", "#9876D5", "#E6B750"}
VIOLET = {"#413755", "#67547C", "#9477AF", "#C3A6D6"}
EXPRESSIONS = ("neutral", "concerned", "pleased")

# Per character: the sprite module, the skin tokens, the brow key and the recorded extra.
# EXTRA records the one pale highlight key per character: it is already a pale step of that
# sprite's PAL (same hex), reused as the eye glint, so no hex is added to the palette.
CHARS = {
    "engineer": dict(
        spr=eng, skin={"1": "n", "2": "m", "3": "n", "4": "U", "5": "y", "6": "T", "7": "l"}, brow="B",
        extra={"y": {"hex": eng.PAL["y"], "use": "eye glint (the collar's lightest step)"}},
        label="Engineer"),
    "ivo": dict(
        spr=ivo, skin={"1": "n", "2": "m", "3": "n", "4": "l", "5": "D", "6": "q", "7": "l"}, brow="A",
        extra={"D": {"hex": ivo.PAL["D"], "use": "eye glint (the hair's lightest step)"}},
        label="Ivo"),
    "mira": dict(
        spr=mira, skin={"1": "n", "2": "m", "3": "n", "4": "d", "5": "r", "6": "w", "7": "l"}, brow="B",
        extra={"r": {"hex": mira.PAL["r"], "use": "eye glint (the paper's lightest step)"}},
        label="Mira"),
}


def R(spec, width):
    """Run-length row: 'D3 C18 .2' is three D, eighteen C, two transparent. Width is asserted."""
    out = ""
    for tok in spec.split():
        out += tok[0] * int(tok[1:])
    assert len(out) == width, f"run-length row has {len(out)} keys, want {width}: {spec}"
    return out


def blank():
    return [["."] * W for _ in range(H)]


def paint_spans(g, spans, keyfn):
    mask = set()
    for r, (a, b) in spans.items():
        for c in range(a, b + 1):
            g[r][c] = keyfn(r, c, a, b)
            mask.add((r, c))
    return mask


def ring(g, mask, over_all):
    """Outline ink around a layer's mask. over_all: also over other layers; else only on transparency."""
    for (r, c) in list(mask):
        for dr, dc in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            rr, cc = r + dr, c + dc
            if 0 <= rr < H and 0 <= cc < W and (rr, cc) not in mask:
                if over_all or g[rr][cc] == ".":
                    g[rr][cc] = "o"


def paint_hair(g, c0, width, r0, rows):
    mask = set()
    for i, spec in enumerate(rows):
        row = R(spec, width)
        for j, ch in enumerate(row):
            if ch != ".":
                g[r0 + i][c0 + j] = ch
                mask.add((r0 + i, c0 + j))
    return mask


def stamp(g, r, c, rows):
    for dy, line in enumerate(rows):
        for dx, ch in enumerate(line):
            if ch != ".":
                g[r + dy][c + dx] = ch


def compose(style, who, expr):
    """Build one portrait grid (48 strings of sprite keys) for a style module, character and expression."""
    cfg = CHARS[who]
    g = blank()
    # neck first, then the body over it
    body = set()
    if getattr(style, "NECK", None):
        body |= paint_spans(g, style.NECK, lambda r, c, a, b: getattr(style, "NECK_TOKEN", "2"))
    body |= paint_spans(g, style.BODY, lambda r, c, a, b: CLOTH[who](r, c, a, b, style.BODY))
    extra_props(g, who, style)
    ring(g, body, over_all=False)
    # head
    head = paint_spans(g, style.HEAD, lambda r, c, a, b: style.skin_token(r, c, a, b))
    ring(g, head, over_all=True)
    # hair
    c0, width, r0, rows = style.HAIR[who]
    hair = paint_hair(g, c0, width, r0, rows)
    if getattr(style, "UNDER_FRINGE", False):     # a one-pixel cast shadow under the fringe
        for (r, c) in hair:
            if r + 1 < H and g[r + 1][c] == "1" and (r + 1, c) not in hair:
                g[r + 1][c] = "2"
    ring(g, hair, over_all=False)
    # face
    for r, c, rows in style.FACE[expr]:
        stamp(g, r, c, rows)
    for r, c, rows in getattr(style, "CHAR_FACE", {}).get((who, expr), ()):
        stamp(g, r, c, rows)
    return finish(g, cfg, getattr(style, "SKIN", {}).get(who, {}))


def finish(g, cfg, override=None):
    m = dict(cfg["skin"])
    m.update(override or {})
    m["B"] = cfg["brow"]
    out = []
    for row in g:
        out.append("".join(m.get(ch, ch) for ch in row))
    return out


# ---- clothing, one function per character: (row, col, span_a, span_b, body_spans) -> key -------
def top_row(spans):
    return min(spans)


def cloth_engineer(r, c, a, b, spans):
    t = top_row(spans)
    k = "r"
    if c <= a + 3:
        k = "s"
    elif c >= b - 3:
        k = "q"
    d = abs(c - 23.5)
    if r - t <= 3 and d <= 5 - (r - t):          # cream collar V
        k = "y" if c < 24 else "x"
        if d > 4 - (r - t):
            k = "w"
    return k


def cloth_ivo(r, c, a, b, spans):
    k = "r"
    if c <= a + 3:
        k = "s"
    elif c >= b - 3:
        k = "q"
    if 21 <= c <= 26:                               # ochre shirt strip
        k = "x" if c in (21, 26) else "y"
        if c == 22 and r == top_row(spans) + 2:
            k = "z"
    return k


def cloth_mira(r, c, a, b, spans):
    t = top_row(spans)
    if c <= 23:                                     # her right: garden green
        k = "F"
        if c <= a + 2:
            k = "G"
        if c == 23:
            k = "E"
    else:                                           # her left: ochre
        k = "x"
        if c >= b - 2:
            k = "w"
        if c in (24, 25):
            k = "y"
    s = c - 11 - (r - t)                            # coral strap, from her right shoulder across the chest
    if r > t and s in (0, 1):
        k = "e" if s == 0 else "d"
    return k


CLOTH = {"engineer": cloth_engineer, "ivo": cloth_ivo, "mira": cloth_mira}


def extra_props(g, who, style):
    """Signature props that sit on the body: the Engineer's badge, Ivo's tablet corner."""
    p = getattr(style, "PROPS", {}).get(who)
    if p:
        for r, c, rows in p:
            stamp(g, r, c, rows)


# ---- rendering ------------------------------------------------------------------------------
def pal_of(who):
    return CHARS[who]["spr"].PAL


def grid_img(grid, pal):
    arr = np.zeros((len(grid), len(grid[0]), 4), np.uint8)
    for y, row in enumerate(grid):
        for x, ch in enumerate(row):
            c = pal[ch]
            if c:
                arr[y, x, :3] = bst.hx(c)
                arr[y, x, 3] = 255
    return Image.fromarray(arr, "RGBA")


def sprite_img(who):
    spr = CHARS[who]["spr"]
    return Image.fromarray(g1.frame_rgba(spr.IDLE["s"][0], spr.PAL), "RGBA")


def up(im, z):
    return im.resize((im.width * z, im.height * z), Image.NEAREST)


def on(im, color, z):
    bg = Image.new("RGBA", im.size, color)
    bg.alpha_composite(im)
    return up(bg, z)
