"""Shared geometry, expression kit and helpers for 48x48 head-and-shoulders portraits.

Status: Approved by the director 2026-10-02. Rules: PORTRAIT_RULES.md.

A portrait grid is 48 rows of 48 keys. Source files write each row as three 16-key
blocks separated by spaces (one block is one world tile; the face axis falls between
columns 23 and 24, inside the second block); `parse` strips the spaces. Keys are the
character's own world-sprite PAL keys. A portrait is a hand-placed BASE (hair, skin
shading, ears, neck, clothing) plus an expression kit of small stamps (brows, eyes,
nose, mouth) and a head tilt, so the three expressions always share one skull.
"""

W = H = 48

# ---- construction guides (all row/column numbers are portrait pixels, 0-indexed) ----
GUIDE = {
    "hair_top_row": 1,       # topmost outline row of hair, tuft or puff: row 0 stays clear
    "hairline_row": 12,      # forehead skin starts here at the lowest point of the fringe
    "brow_row": 17,
    "eye_rows": (19, 20),    # eye line: the lid is on row 19, the iris on row 20
    "nose_row": 23,
    "mouth_row": 27,
    "chin_row": 32,          # first outline row below the chin
    "neck_rows": (32, 35),
    "shoulder_row": 35,      # first jacket row at the neck; the slope reaches full width by row 40
    "crop_row": 47,          # last row: no outline below it, the body runs on out of frame
    "face_cols": (14, 33),   # face fill, 20 px; the outline sits on columns 13 and 34
    "ear_cols": ((11, 12), (35, 36)),
    "eye_cols": ((17, 20), (27, 30)),
    "centre": (23, 24),      # the axis is the edge between these two columns
    "shoulder_cols": (2, 45),
}

# Face fill per row (inclusive columns). Outlines are the pixels beside these spans.
FACE = {r: (14, 33) for r in range(12, 25)}
FACE.update({25: (15, 32), 26: (15, 32), 27: (16, 31), 28: (16, 31), 29: (17, 30), 30: (18, 29), 31: (19, 28)})
NECK = {r: (20, 27) for r in range(32, 36)}
TORSO = {35: (16, 31), 36: (12, 35), 37: (9, 38), 38: (6, 41), 39: (4, 43), 40: (3, 44)}
TORSO.update({r: (2, 45) for r in range(41, 48)})

# ---- expression kit -------------------------------------------------------------
# Abstract keys in a stamp: B brow (hair key of the character), o outline ink,
# s lightest skin step, t mid, u shadow, v darkest skin step (contours only).
# "." leaves the base untouched. Rows are listed top to bottom; (row, col) is the
# top-left corner of the stamp.
KIT = {
    "neutral": [
        (17, 16, ["BBBBB"]), (17, 27, ["BBBBB"]),              # level brows
        (19, 17, [".oo.", "soos"]), (19, 27, [".oo.", "soos"]),  # open eyes
        (22, 23, ["s"]), (23, 24, ["u"]), (24, 23, ["uu"]),     # nose
        (27, 21, ["uuuuuu"]), (28, 23, ["ss"]),                 # level mouth, lit lower lip
    ],
    "concerned": [
        (18, 16, ["BB"]), (17, 18, ["BB"]), (16, 20, ["B"]),     # inner ends raised
        (16, 27, ["B"]), (17, 28, ["BB"]), (18, 30, ["BB"]),
        (19, 17, ["oooo", "soos", ".uu."]), (19, 27, ["oooo", "soos", ".uu."]),
        (22, 23, ["s"]), (23, 24, ["u"]), (24, 23, ["uu"]),
        (27, 22, ["uuuu"]), (28, 21, ["u"]), (28, 26, ["u"]),   # corners drop
    ],
    "pleased": [
        (17, 17, ["BBB"]), (18, 16, ["B"]), (18, 20, ["B"]),     # soft arched brows
        (17, 28, ["BBB"]), (18, 27, ["B"]), (18, 31, ["B"]),
        (19, 17, [".oo.", "o..o"]), (19, 27, [".oo.", "o..o"]),  # closed, smiling eyes
        (22, 23, ["s"]), (23, 24, ["u"]), (24, 23, ["uu"]),
        (26, 20, ["u"]), (26, 27, ["u"]), (27, 21, ["u"]), (27, 26, ["u"]), (28, 22, ["uuuu"]),
    ],
}

# Head tilt: whole-row shifts applied after stamping, rows (first, last, dx). Row 0 is
# included so the top outline moves with the hair.
# Rows that carry the shoulders are never shifted.
TILT = {
    "neutral": [],
    "concerned": [(0, 14, -1)],
    "pleased": [(0, 14, 1)],
}


def parse(rows):
    """Strip the 16-key block spaces and validate 48x48."""
    grid = ["".join(r.split()) for r in rows]
    assert len(grid) == H, f"{len(grid)} rows"
    for y, r in enumerate(grid):
        assert len(r) == W, f"row {y} has {len(r)} keys"
    return grid


def blocks(grid):
    """Inverse of parse: rows as three 16-key blocks, for writing source files."""
    return [" ".join(r[i:i + 16] for i in (0, 16, 32)) for r in grid]


def stamp(grid, row, col, rows, keymap):
    g = [list(r) for r in grid]
    for dy, line in enumerate(rows):
        for dx, ch in enumerate(line):
            if ch == ".":
                continue
            g[row + dy][col + dx] = keymap.get(ch, ch)
    return ["".join(r) for r in g]


def shift_rows(grid, first, last, dx):
    g = list(grid)
    for y in range(first, last + 1):
        r = g[y]
        g[y] = ("." * dx + r[:W - dx]) if dx > 0 else (r[-dx:] + "." * -dx)
    return g


def skin_map(skin, brow):
    """skin is the SLOTS['skin'] string 'klmn' (darkest to lightest)."""
    return {"B": brow, "s": skin[3], "t": skin[2], "u": skin[1], "v": skin[0]}


def separate_hair_skin(grid, hair, skin):
    """Light hair (hair[1:]) must not touch lit skin (skin[1:]): such skin pixels take the darkest
    skin step, a forehead and temple shadow. Used for pale hair against pale skin (Ivo)."""
    g = [list(r) for r in grid]
    for y in range(1, H - 1):
        for x in range(1, W - 1):
            if grid[y][x] in skin[1:] and any(grid[y + dy][x + dx] in hair[1:] for dy, dx in ((1, 0), (-1, 0), (0, 1), (0, -1))):
                g[y][x] = skin[0]
    return ["".join(r) for r in g]


def compose(base, expr, skin, brow, extra=(), tilt=None, hair=None):
    """Base + kit stamps + optional character stamps (row, col, rows) + head tilt.

    `tilt` overrides TILT[expr] for a character (a list of (first_row, last_row, dx)). Pass `hair`
    (the hair ramp) to re-apply the hair/skin separation after tilting."""
    km = skin_map(skin, brow)
    g = list(base)
    for row, col, rows in KIT[expr]:
        g = stamp(g, row, col, rows, km)
    for row, col, rows in extra:
        g = stamp(g, row, col, rows, km)
    for first, last, dx in (TILT[expr] if tilt is None else tilt):
        g = shift_rows(g, first, last, dx)
    if hair:
        g = separate_hair_skin(g, hair, skin)
    return g
