"""Glitch sprites (misregistered office objects), hand-placed on the 16 px grid.

Status: Approved by the director 2026-10-02. Spec: GLITCHES_SPEC.md.

Three archetypes, each with a roam set, a misregister set, one repaired (snap) frame and
the ordinary prop it becomes:
  stapler  32x16 (2x1 cells) a grey desk stapler that hops, with a violet outline ghost
  chair    32x16 (2x1 cells) a coral office chair (the room's own chair kit) and its violet, displaced duplicate shadow
  form     16x16 (1x1 cell)  a sheet of paper with a wrong violet-backed fold and drifting print

Pixels are key grids (one character per pixel, "." transparent). The housing
layers are hand-placed grids. A frame is those layers stacked with whole-pixel
offsets (the hop height, the part that slips out of register), plus a violet
ghost: the 1 px outline of a layer's silhouette shifted by a few pixels. No
blending, no gradients. Light comes from the upper left.

Colour rules (STYLE_BIBLE section 3 and 7):
  - violet is for the anomaly only: contour "a" #413755, fill "b" #67547C and
    the emissive steps "c" #9477AF and "d" #C3A6D6 (at most two glow steps);
  - the housing and the 1 px contour come first, so glow pixels never touch
    transparency: the glow can't erase the silhouette;
  - the UI marker hex #9876D5 is never used.
"""

PAL = {
    ".": None,
    # ink outline ramp: "o" is the default outline, "i" and "j" fill, "k" metal highlight
    "o": "#0E1020", "i": "#1C2038", "j": "#3A4160", "k": "#6A7392",
    # violet anomaly ramp: "a" contour only, "b" fill, "c" glow, "d" hot core
    "a": "#413755", "b": "#67547C", "c": "#9477AF", "d": "#C3A6D6",
    # chair, the coral upholstery ramp the room's task chairs use
    "D": "#C8485A", "E": "#F26A5A", "F": "#FFB38A",
    # paper, from the stone and paper ramps
    "p": "#C7B7A0", "q": "#E2D6C2", "r": "#F4F2EC",
}

VIOLET_KEYS = "abcd"
GLOW_KEYS = "cd"          # the emissive steps: at most two, hard-edged
CONTOUR_KEYS = "oia"     # outline or dark steps allowed on the silhouette
UI_MARKERS = {"#19AFA2", "#EC776D", "#9876D5", "#E6B750"}

W16 = 16


# ------------------------------------------------------------------ helpers

def rows16(*rows, top=0, w=16, h=16):
    """Pad hand-placed rows to a w x h grid, the first row landing on grid row `top`."""
    out = ["." * w for _ in range(h)]
    for i, r in enumerate(rows):
        assert len(r) <= w, (len(r), r)
        out[top + i] = r + "." * (w - len(r))
    return out


def blank(w, h):
    return [["."] * w for _ in range(h)]


def paste(dst, src, ox=0, oy=0, only=None):
    """Stack `src` onto `dst` (lists of lists) at an integer offset; "." is transparent."""
    h, w = len(dst), len(dst[0])
    for y, row in enumerate(src):
        for x, ch in enumerate(row):
            if ch == "." or (only and ch not in only):
                continue
            tx, ty = x + ox, y + oy
            if 0 <= tx < w and 0 <= ty < h:
                dst[ty][tx] = ch
    return dst


def silhouette(grid):
    return {(x, y) for y, r in enumerate(grid) for x, ch in enumerate(r) if ch != "."}


def ghost(mask, dx, dy, w, h, key="b"):
    """1 px outline of `mask` shifted by (dx, dy): the displaced violet duplicate."""
    moved = {(x + dx, y + dy) for x, y in mask}
    edge = {(x, y) for x, y in moved
            if any((x + ax, y + ay) not in moved for ax, ay in ((1, 0), (-1, 0), (0, 1), (0, -1)))}
    return {p: key for p in edge if 0 <= p[0] < w and 0 <= p[1] < h}


def finish(layers, w, h, ghosts=()):
    """Compose [(grid, ox, oy), ...] bottom to top over any ghost outlines."""
    g = blank(w, h)
    for gh in ghosts:
        for (x, y), ch in gh.items():
            g[y][x] = ch
    for grid, ox, oy in layers:
        paste(g, grid, ox, oy)
    return ["".join(r) for r in g]


# ------------------------------------------------------------------ helpers (wide frames)

def seg(*parts, w=32):
    """One 32-wide row from (x, "keys") segments; "." elsewhere."""
    row = ["."] * w
    for x, keys in parts:
        for i, ch in enumerate(keys):
            row[x + i] = ch
    return "".join(row)


def rows_at(top, rows, w=32, h=16):
    """Hand-placed rows (each a seg() string) starting at frame row `top`, padded to w x h."""
    return rows16(*rows, top=top, w=w, h=h)


def shift_grid(grid, dx, dy):
    out = blank(len(grid[0]), len(grid))
    paste(out, grid, dx, dy)
    return ["".join(r) for r in out]


# ------------------------------------------------------------------ stapler
# A classic desk stapler in 3/4 overhead, 32x16 (2x1 cells), hinge to the west,
# rounded nose to the east, light from the upper left: a raised hinge block, a
# metal/ink-grey top arm with a lit top plane and a darker front face, and a dark
# base plate. The staple slot at the nose is the emissive core (3 px: c d c) inside
# the arm. The violet cue is a 1 px outline ghost of the whole body, offset (3, 1).

STAPLER_BASE = rows_at(6, [   # hinge block (frame rows 6..12) and the base plate (rows 13..14)
    seg((4, "ooooo")),
    seg((3, "okkkkjo")),
    seg((3, "okkjjjo")),
    seg((3, "ojjjjjo")),
    seg((3, "ojjjjjo")),
    seg((3, "oiiiiio")),
    seg((3, "ooooooo")),
    seg((3, "ojjj" + "i" * 19 + "o")),
    seg((4, "o" * 22)),
])
STAPLER_ARM = rows_at(8, [    # the top arm, frame rows 8..12, columns 9..25; its nose is rounded
    seg((9, "o" * 15)),
    seg((9, "o" + "k" * 14 + "o")),
    seg((9, "o" + "j" * 11 + "cdc" + "j" + "o")),
    seg((9, "o" + "i" * 15 + "o")),
    seg((9, "o" * 17)),
])


def stapler_frame(lift=0, arm=(0, 0), ghost_off=(3, 1), slip_ghost=False, body_ghost=True):
    """lift: pixels the body is raised (hop). arm: (dx, dy) the arm slips from its base.

    The violet ghost is the 1 px outline of the resting silhouette shifted by
    ghost_off, so during a hop it stays on the floor while the body rises.
    """
    w, h = 32, 16
    home = blank(w, h)
    paste(home, STAPLER_ARM)
    paste(home, STAPLER_BASE)
    ghosts = [ghost(silhouette(home), ghost_off[0], ghost_off[1], w, h)] if body_ghost else []
    if slip_ghost:  # the arm's home outline stays behind where the arm has slipped
        arm_home = blank(w, h)
        paste(arm_home, STAPLER_ARM)
        ghosts.append(ghost(silhouette(arm_home), 0, 0, w, h, key="b"))
    layers = [(STAPLER_BASE, 0, -lift), (STAPLER_ARM, arm[0], arm[1] - lift)]
    return finish(layers, w, h, ghosts)


STAPLER_ARM_PLAIN = [r.replace("cdc", "iii") for r in STAPLER_ARM]   # the staple slot, no glow
STAPLER_ARM_SNAP = [r.replace("cdc", "bbb") for r in STAPLER_ARM]    # glow out, a dim violet afterglow in the slot


def halo(mask, w, h, key="b"):
    """1 px ring just outside `mask` (4-neighbour dilation): the violet 'register ring'."""
    ring = {(x + ax, y + ay) for x, y in mask for ax, ay in ((1, 0), (-1, 0), (0, 1), (0, -1))} - mask
    return {p: key for p in ring if 0 <= p[0] < w and 0 <= p[1] < h}


def stapler_plain(snap=False):
    """The ordinary stapler (snap=False) or the one-frame snap into register (snap=True).

    Snap: the arm is back on its base and the glow is out; the violet ghost has collapsed onto
    the body, leaving a 1 px register ring hugging the silhouette and a dim slot.
    """
    w, h = 32, 16
    arm = STAPLER_ARM_SNAP if snap else STAPLER_ARM_PLAIN
    body = blank(w, h)
    paste(body, arm)
    paste(body, STAPLER_BASE)
    ghosts = [halo(silhouette(body), w, h)] if snap else []
    return finish([(STAPLER_BASE, 0, 0), (arm, 0, 0)], w, h, ghosts)


STAPLER = {
    "size": (32, 16), "footprint": (2, 1),
    "roam": [  # hop: rest, rise, apex, land. The ghost stays on the floor.
        stapler_frame(0), stapler_frame(2), stapler_frame(3), stapler_frame(1),
    ],
    "misregister": [  # the arm slips off its base by 1-2 px
        stapler_frame(0, arm=(2, -1), slip_ghost=True, body_ghost=False),
        stapler_frame(0, arm=(-1, -2), slip_ghost=True, body_ghost=False),
    ],
    "repaired": [stapler_plain(snap=True)],
    "ordinary": [stapler_plain()],
}


# ------------------------------------------------------------------ chair + wrong shadow
# The room's own coral task chair (backrest, lit seat edge, darker front face) stands
# at the right of a 32x16 frame (2x1 cells). Its normal ink contact shadow is drawn
# by the renderer. Cast toward the UPPER LEFT, the direction of the light, lies a
# second, wrong shadow: flat and low, with no top plane. It is a skewed seat
# parallelogram 5 px tall, a backrest strip and short leg strokes, in the dark
# violet steps (contour a, fill b) with a one-step #9477AF core glow on the seat.

CHAIR_BACK = [  # frame rows 4..6, chair-local columns 0..11 (placed at x = CH_X)
    ".oooooooooo.",
    ".oEEEEEEEEo.",
    ".oDDDDDDDDo.",
]
CHAIR_SEAT = [  # rows 7..14; the contour on row 7 is shared with the backrest's underside
    "oooooooooooo",
    "oFFFFFFFFFFo",
    "oEEEEEEEEEEo",
    "oEEEEEEEEEEo",
    "oEEEEEEEEEEo",
    "oDDDDDDDDDDo",
    "oDDDDDDDDDDo",
    ".oooooooooo.",
]
CH_X, CH_BACK_TOP, CH_SEAT_TOP = 19, 4, 7

SHADOW_A = rows_at(5, [       # rest: frame rows 5..14, leaning 1 px per row toward the upper left
    seg((3, "a" * 8)),                      # 5  backrest strip, farthest along the cast
    seg((4, "a" + "b" * 6 + "a")),          # 6
    seg((5, "a" * 8)),                      # 7
    seg((8, "aa")),                         # 8  post stroke
    seg((5, "a" * 10)),                     # 9  seat parallelogram, 5 rows, no top plane
    seg((6, "a" + "b" * 8 + "a")),          # 10
    seg((7, "a" + "bcccccbb" + "a")),       # 11 one-step glow core
    seg((8, "a" + "b" * 8 + "a")),          # 12
    seg((9, "a" * 10)),                     # 13
    seg((12, "aa"), (15, "aa"), (18, "a")), # 14 leg strokes
])
SHADOW_B = rows_at(5, [       # stretched: the seat shadow is one row taller and the legs vanish
    seg((3, "a" * 8)),
    seg((4, "a" + "b" * 6 + "a")),
    seg((5, "a" * 8)),
    seg((8, "aa")),
    seg((5, "a" * 10)),
    seg((6, "a" + "b" * 8 + "a")),
    seg((7, "a" + "bcccccbb" + "a")),
    seg((8, "a" + "b" * 8 + "a")),
    seg((9, "a" + "b" * 8 + "a")),
    seg((10, "a" * 10)),
])


def chair_frame(shadow, dx=0, dy=0):
    g = blank(32, 16)
    if shadow is not None:
        paste(g, shift_grid(shadow, dx, dy))
    paste(g, CHAIR_SEAT, CH_X, CH_SEAT_TOP)
    paste(g, CHAIR_BACK, CH_X, CH_BACK_TOP)
    return ["".join(r) for r in g]


# Snap: the wrong shadow has slid down to the chair's own foot and lies flat in register there: a
# low three-row slab at the chair's left foot, joined by a 1 px line along the floor under the seat
# (the renderer's normal contact shadow sits on that row, so the line replaces it for this one
# frame). Contour "a" only touches transparency, the fill "b" sits inside; the glow is out and nothing
# violet is left up and to the left.
SNAP_SHADOW = rows_at(13, [
    seg((13, "a" * 6)),
    seg((12, "a" + "b" * 5 + "a")),
    seg((12, "a" * 19)),
])

CHAIR = {
    "size": (32, 16), "footprint": (2, 1),
    "roam": [  # the wrong shadow drifts away from the chair and stretches, then settles
        chair_frame(SHADOW_A), chair_frame(SHADOW_B, -1, 0),
        chair_frame(SHADOW_B, -1, -1), chair_frame(SHADOW_A, 0, -1),
    ],
    "misregister": [  # the shadow jumps 1-2 px away from the chair base
        chair_frame(SHADOW_A, -2, 0), chair_frame(SHADOW_B, -1, -2),
    ],
    "repaired": [chair_frame(SNAP_SHADOW)],
    "ordinary": [chair_frame(None)],
}


# ------------------------------------------------------------------ folded form
# A sheet of printed paper lying on the floor. Its top-right corner is folded
# the wrong way: the flap shows a violet back, with the emissive core inside it.
# The page, its ink lines and the flap are separate hand-placed layers.

# Page outline, page-local rows 0..12 (frame rows 3..15 at rest). The diagonal fold
# runs (6,0) -> (12,6); the cut corner above it is empty.
FORM_PAGE = [
    "...oooo.........",   # 0
    "...orrro........",   # 1
    "...orrrro.......",   # 2
    "...orrrrro......",   # 3
    "...orrrrrro.....",   # 4
    "...orrrrrrro....",   # 5
    "...orrrrrrrro...",   # 6
    "...orrrrrrrrqo..",   # 7
    "...orrrrrrrrqo..",   # 8
    "...orrrrrrrrqo..",   # 9
    "...orrrrrrrqqo..",   # 10
    "...oqqqqqqqqpo..",   # 11
    "...oooooooooo...",   # 12
]
FORM_TOP = 3
# The 'wrong' fold: the flap lies over the page below the diagonal, violet side up.
FLAP_CLOSED = [  # page-local rows 0..6
    "......o.........",   # 0  fold start
    "......ao........",   # 1
    "......abo.......",   # 2
    "......abbo......",   # 3
    "......acbbo.....",   # 4
    "......adcbbo....",   # 5
    "......aaaaaao...",   # 6
]
FLAP_HALF = [  # the flap lifting: foreshortened to a 2 px band along the fold
    "......o.........",
    "......bo........",
    ".......bo.......",
    "......abbo......",
    ".......cbbo.....",
    ".......bcbbo....",
    "........aaaao...",
]
FLAP_EDGE = [  # edge-on: a thin lit band just inside the fold, the page showing beneath
    "......o.........",
    ".....bco........",
    "......bco.......",
    ".......bco......",
    "........bdo.....",
    ".........bco....",
    "..........bco...",
]
# Printed lines on the page: two short lines of text in ink metal.
FORM_PRINT = [  # page-local rows 0..12, same frame as FORM_PAGE (only the 'k' pixels)
    "................",
    "................",
    "................",
    "................",
    "................",
    "................",
    "................",
    "................",
    "................",
    "....kkkkkkk.....",   # 10
    "................",
    "....kkkkk.......",   # 12
    "................",
]


def form_frame(flap, lift=0, print_off=(0, 0), flap_off=(0, 0), print_ghost=None):
    w = h = 16
    layers = [(FORM_PAGE, 0, FORM_TOP - lift)]
    # printed lines, clipped to the page interior (x4..11) so they never leave the paper
    pr = blank(w, h)
    for y, row in enumerate(FORM_PRINT):
        for x, ch in enumerate(row):
            if ch != ".":
                tx, ty = x + print_off[0], y + print_off[1]
                if 4 <= tx <= 11:
                    pr[ty][tx] = ch
    layers_extra = []
    if print_ghost:
        gd = blank(w, h)
        for y, row in enumerate(FORM_PRINT):
            for x, ch in enumerate(row):
                if ch != ".":
                    tx, ty = x + print_ghost[0], y + print_ghost[1]
                    if 4 <= tx <= 11 and FORM_PAGE[ty][tx] in "rq":
                        gd[ty][tx] = "b"
        layers_extra.append((gd, 0, FORM_TOP - lift))
    layers += layers_extra
    layers.append((pr, 0, FORM_TOP - lift))
    layers.append((flap, flap_off[0], FORM_TOP - lift + flap_off[1]))
    return finish(layers, w, h)


# The ordinary sheet the form becomes: flat, the cut corner restored, a block of five printed lines
# (the folded form's two lines stay where they were; three more fill the part the flap hid).
FORM_FLAT = [  # page-local rows 0..12, columns 3..13
    "...ooooooooooo..",   # 0
    "...orrrrrrrrro..",   # 1  (columns 4..12 are paper)
    "...orrrrrrrrro..",
    "...orrrrrrrrro..",
    "...orrrrrrrrro..",
    "...orrrrrrrrro..",
    "...orrrrrrrrqo..",
    "...orrrrrrrrqo..",
    "...orrrrrrrrqo..",
    "...orrrrrrrrqo..",
    "...orrrrrrrqqo..",
    "...oqqqqqqqqpo..",
    "...ooooooooooo..",   # 12
]
FORM_FLAT_PRINT = {3: 7, 5: 6, 7: 7, 9: 7, 11: 5}   # page row -> number of ink pixels, from column 4
# The crease the fold left behind, page-local (x, y), snapped one frame: the glow marks its middle.
FORM_CREASE = [(6, 1, "b"), (7, 2, "b"), (8, 3, "c"), (9, 4, "c"), (10, 5, "b"), (11, 6, "b")]


def form_flat(snap=False):
    w = h = 16
    g = blank(w, h)
    paste(g, FORM_FLAT, 0, FORM_TOP)
    for row, n in FORM_FLAT_PRINT.items():
        for x in range(4, 4 + n):
            g[FORM_TOP + row][x] = "k"
    if snap:
        for x, y, ch in FORM_CREASE:   # a 2 px band: the crease and the pixel below it
            g[FORM_TOP + y][x] = ch
            if g[FORM_TOP + y + 1][x] in "rqp":
                g[FORM_TOP + y + 1][x] = "b"
    return ["".join(r) for r in g]


FORM = {
    "size": (16, 16), "footprint": (1, 1),
    "roam": [  # the flap flutters: closed, half, edge-on, half; the page lifts 1-2 px
        form_frame(FLAP_CLOSED, 0),
        form_frame(FLAP_HALF, 1),
        form_frame(FLAP_EDGE, 2),
        form_frame(FLAP_HALF, 0),
    ],
    "misregister": [  # the print slips 2 px with a violet duplicate line; the flap slips 1 px
        form_frame(FLAP_CLOSED, 0, print_off=(2, 0), print_ghost=(0, 1)),
        form_frame(FLAP_CLOSED, 0, print_off=(-1, 0), print_ghost=(2, 1), flap_off=(1, -1)),
    ],
    "repaired": [form_flat(snap=True)],
    "ordinary": [form_flat()],
}

# ------------------------------------------------------------------ metadata

ARCHETYPES = {
    "stapler": {
        "grid": STAPLER, "anchor": (16, 16),
        "shadow": {"x0": 4, "x1": 26, "row": 14},   # renderer contact shadow under the base
        "roam": {"ms": 120, "move_px_per_frame": [0, 2, 2, 0], "lift_px": [0, 2, 3, 1],
                 "note": "hop: rise, apex, land; travels 4 px per 480 ms cycle"},
        "misregister": {"ms": 80, "play": "flicker"},
        "repaired": {"ms": 160, "play": "once", "cue": "a 1 px violet register ring hugs the body, the slot is a dim violet afterglow"},
        "ordinary": {"collision": ["00"], "note": "a plain stapler lying on the floor; walkable (decor)"},
    },
    "chair": {
        "grid": CHAIR, "anchor": (16, 16),
        "shadow": {"x0": 20, "x1": 30, "row": 14},
        "roam": {"ms": 200, "move_px_per_frame": [1, 1, 1, 1], "lift_px": [0, 0, 0, 0],
                 "note": "the chair drifts 4 px per 800 ms cycle; its wrong shadow drifts away up-left and stretches"},
        "misregister": {"ms": 80, "play": "flicker"},
        "repaired": {"ms": 160, "play": "once", "cue": "the wrong shadow lies flat as a 1 px violet line at the chair's foot"},
        "ordinary": {"collision": ["01"], "note": "the task chair with only its single correct (renderer) shadow; blocks its own cell"},
    },
    "form": {
        "grid": FORM, "anchor": (8, 16),
        "shadow": {"x0": 4, "x1": 12, "row": 15},
        "roam": {"ms": 120, "move_px_per_frame": [0, 2, 2, 0], "lift_px": [0, 1, 2, 0],
                 "note": "flutter: the flap opens edge-on as the page lifts; travels 4 px per 480 ms cycle"},
        "misregister": {"ms": 80, "play": "flicker"},
        "repaired": {"ms": 160, "play": "once", "cue": "the fold has gone flat; its crease shows as a violet diagonal with a glow centre"},
        "ordinary": {"collision": ["0"], "note": "a flat sheet of printed paper lying on the floor; walkable (decor)"},
    },
}

KINDS = ("roam", "misregister", "repaired", "ordinary")
REPAIRED_MS = 160          # the snap frame: four 40 ms GIF ticks, long enough to read, short enough to be a snap

# Animation names in atlas order.
ANIMATIONS = [(a, k) for a in ARCHETYPES for k in KINDS]


def frames(arch, anim):
    return ARCHETYPES[arch]["grid"][anim]


# Import-time sanity: every grid is rectangular and the declared size.
for _a, _d in ARCHETYPES.items():
    _w, _h = _d["grid"]["size"]
    for _k in KINDS:
        for _fr in _d["grid"][_k]:
            assert len(_fr) == _h and all(len(r) == _w for r in _fr), (_a, _k)
