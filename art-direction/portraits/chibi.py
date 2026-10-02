"""Shared style module for the "Chibi icon" portraits (48x48, one module per character on top).

Status: Candidate, pending director review. Rules: PORTRAIT_RULES.md. Personas: PORTRAIT_PERSONAS.md.
Replaces portrait_template.py. Generalises explore/explore_common.py and explore/style_c.py.

Direction C (player choice 2026-10-02): an oversized round head fills most of the 48x48, the shoulders
are tiny and sit in the bottom ten rows, shading is flat (one fill and one crescent of shade), eyes are
dots with a glint, mouths are big and readable, cheeks are round with blush. Per character the
modules vary the head shape, the hair, the costume and their own expression stamps.

A portrait is composed from layers, back to front: body, head, hair, face stamps. Body and head are
per-row span tables, hair is a hand-placed key grid, face features are small stamps. The outline
(`#202337`, key `o`) is added around each layer as it is painted, so the silhouette is closed by
construction: the body and the hair take an outline only toward transparency, the head also takes one
over the body (the chin line).

Tokens used while composing (mapped to the character's real sprite keys by `finish`):
  1 skin fill   2 skin shade   4 blush   5 eye glint   6 mouth interior   = brow key   o outline ink
Hair, clothing and any other feature are written with the character's own sprite keys.

Module contract (what a portrait_<name>.py defines):
  SPRITE, PAL, SLOTS, EXTRA, SKIN (token -> key), BROW (key), HEAD, BODY, HAIR, cloth(), PROPS,
  FACE[expr] (stamps), SIGNATURES (names of extra expressions), EXPRESSIONS (built by `build`).
Ruler for hair rows:  0123456789012345 0123456789012345 0123456789012345  (axis between 23|24)
"""
import os
import sys

import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
for _sub in ("gate1", "cast", "scale-test"):
    sys.path.insert(0, os.path.join(HERE, "..", _sub))
import build_gate1 as g1  # noqa: E402
import build_scale_test as bst  # noqa: E402

W = H = 48
OUTLINE = "#202337"
MARKERS = {"#19AFA2", "#EC776D", "#9876D5", "#E6B750"}
VIOLET = {"#413755", "#67547C", "#9477AF", "#C3A6D6"}
STANDARD = ("neutral", "concerned", "pleased")

# Shared framing (portrait pixels, 0-indexed): see PORTRAIT_RULES.md
FRAME = {
    "hair_top_outline_row": 1,    # the topmost outline row (row 0 stays clear)
    "head_rows": (3, 36),         # the standard head; a character may shift it by a row or two
    "eye_rows": (22, 25),         # the standard eye block (4 px tall)
    "brow_row": 19,
    "mouth_rows": (28, 30),
    "blush_rows": (27, 28),
    "shoulders_from_row": 38,
    "crop_row": 47,
    "axis": (23, 24),
}


# ---- grid helpers ----------------------------------------------------------------------------
def R(spec, width):
    """Run-length row: 'D3 C18 .2' is three D, eighteen C, two transparent. Width is asserted."""
    out = ""
    for tok in spec.split():
        out += tok[0] * int(tok[1:])
    assert len(out) == width, f"run-length row has {len(out)} keys, want {width}: {spec}"
    return out


def rle_hair(c0, width, r0, rows):
    """Hair written as run-length rows inside a window starting at column c0 -> (r0, 48-wide rows)."""
    return r0, [("." * c0 + R(s, width)).ljust(W, ".") for s in rows]


def block_hair(r0, rows):
    """Hair written as 48-key rows in three 16-key blocks separated by spaces -> (r0, 48-wide rows)."""
    out = []
    for s in rows:
        row = s.replace(" ", "")
        assert len(row) == W, f"hair row has {len(row)} keys, want 48: {s}"
        out.append(row)
    return r0, out


def blank():
    return [["."] * W for _ in range(H)]


def head_spans(top, half_widths):
    """Head spans from half-widths (px each side of the axis), one per row from `top`."""
    return {top + i: (24 - h, 23 + h) for i, h in enumerate(half_widths)}


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


def paint_hair(g, hair):
    r0, rows = hair
    mask = set()
    for i, row in enumerate(rows):
        for j, ch in enumerate(row):
            if ch != ".":
                g[r0 + i][j] = ch
                mask.add((r0 + i, j))
    return mask


def stamp(g, r, c, rows):
    for dy, line in enumerate(rows):
        for dx, ch in enumerate(line):
            if ch != "." and 0 <= r + dy < H and 0 <= c + dx < W:
                g[r + dy][c + dx] = ch


def mirror(rows):
    return [row[::-1] for row in rows]


def pair(r, c, rows):
    """A symmetric feature: the stamp at column c and its mirror image across the axis."""
    w = max(len(x) for x in rows)
    return [(r, c, rows), (r, W - c - w, mirror(rows))]


def shift(stamps, dr=0, dc=0):
    return [(r + dr, c + dc, rows) for r, c, rows in stamps]


def skin_token(r, c, a, b):
    """Flat: the fill, and one crescent of shade down the lower right."""
    return "2" if c + max(0, r - 28) >= b - 2 else "1"


# ---- composition -----------------------------------------------------------------------------
def compose(m, expr, face=None):
    """One portrait grid (48 strings of sprite keys) for character module `m` and an expression name."""
    g = blank()
    body = paint_spans(g, m.BODY, lambda r, c, a, b: m.cloth(r, c, a, b, m.BODY))
    for r, c, rows in getattr(m, "PROPS", ()):
        stamp(g, r, c, rows)
    ring(g, body, over_all=False)
    head = paint_spans(g, m.HEAD, getattr(m, "skin_token", skin_token))
    ring(g, head, over_all=True)
    hair = paint_hair(g, m.HAIR)
    if getattr(m, "UNDER_FRINGE", True):     # a one-pixel cast shadow under the fringe
        for (r, c) in hair:
            if r + 1 < H and g[r + 1][c] == "1" and (r + 1, c) not in hair:
                g[r + 1][c] = "2"
    ring(g, hair, over_all=False)
    for r, c, rows in (face if face is not None else m.FACE[expr]):
        stamp(g, r, c, rows)
    return finish(g, m)


def finish(g, m):
    tok = dict(m.SKIN)
    tok["="] = m.BROW
    return ["".join(tok.get(ch, ch) for ch in row) for row in g]


def build(m):
    """All expressions of a module: the three standard ones and its signature expressions."""
    out = {e: compose(m, e) for e in STANDARD}
    for name in getattr(m, "SIGNATURES", ()):
        out[name] = compose(m, name)
    return out


# ---- rendering -------------------------------------------------------------------------------
def grid_img(grid, pal):
    """A 48x48 key grid as an RGBA image (the sibling of build_gate1.frame_rgba, which is 16x24)."""
    arr = np.zeros((len(grid), len(grid[0]), 4), np.uint8)
    for y, row in enumerate(grid):
        for x, ch in enumerate(row):
            c = pal[ch]
            if c:
                arr[y, x, :3] = bst.hx(c)
                arr[y, x, 3] = 255
    return Image.fromarray(arr, "RGBA")


def sprite_img(spr, pal=None):
    return Image.fromarray(g1.frame_rgba(spr.IDLE["s"][0], pal or spr.PAL), "RGBA")


def up(im, z):
    return im.resize((im.width * z, im.height * z), Image.NEAREST)


def on(im, color, z):
    bg = Image.new("RGBA", im.size, color)
    bg.alpha_composite(im)
    return up(bg, z)
