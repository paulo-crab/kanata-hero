"""Drawing helpers shared by the four district quest-prop sets (Records, Systems, Night Shift, Executive).

Each function paints palette constants only onto an `env.Room` (hard pixels, light from the upper left) and takes
a `shared_pieces.Pal`, so every district recolours the same drawing with its own ramps. Nothing here names a
district. The district modules (`records_kit.py`, `systems_kit.py`, `nightshift_kit.py`, `executive_kit.py`) capture
these drawings into atlas entries with `orientation_kit.make`, give them footprint, collision and state sets, and
(Night Shift only) run their lit-edge pass afterwards.

Contents:
  FONT, text()          a 3x5 pixel font for the digits and the symbols the quests print (+ - & * ( ) _ and 0-9)
  courier_chute()       Mira's pneumatic courier chute, idle or ready (a letter in the slot, a lit indicator)
  mira_decor()          the five Mira reward desk decorations
  folding_stool()       Hal's folding stool with his tool roll (Systems quest prop, Executive place)
A Pal may carry a `paper` ramp (light) for paper, slips and label plates; without one the wall ramp is used (linen in Records).
"""
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
for sub in ("gate1", "scale-test", "palettes"):
    sys.path.insert(0, os.path.join(HERE, "..", sub))
import build_scale_test as bst  # noqa: E402
import environment as env  # noqa: E402

INK, shifted = bst.INK, bst.shifted

FONT = {
    "0": ("XXX", "X.X", "X.X", "X.X", "XXX"), "1": (".X.", "XX.", ".X.", ".X.", "XXX"),
    "2": ("XXX", "..X", "XXX", "X..", "XXX"), "3": ("XXX", "..X", "XXX", "..X", "XXX"),
    "4": ("X.X", "X.X", "XXX", "..X", "..X"), "5": ("XXX", "X..", "XXX", "..X", "XXX"),
    "6": ("XXX", "X..", "XXX", "X.X", "XXX"), "7": ("XXX", "..X", "..X", ".X.", ".X."),
    "8": ("XXX", "X.X", "XXX", "X.X", "XXX"), "9": ("XXX", "X.X", "XXX", "..X", "XXX"),
    "+": ("...", ".X.", "XXX", ".X.", "..."), "-": ("...", "...", "XXX", "...", "..."),
    "&": (".X.", "X.X", ".XX", "X.X", ".XX"), "*": ("X.X", ".X.", "XXX", ".X.", "X.X"),
    "(": (".X.", "X..", "X..", "X..", ".X."), ")": (".X.", "..X", "..X", "..X", ".X."),
    "_": ("...", "...", "...", "...", "XXX"), "$": (".XX", "XX.", ".X.", ".XX", "XX."),
}


def text(r, x, y, s, c, scale=1, gap=1):
    """Draw `s` in the 3x5 font with its top-left at (x, y). Returns the x after the last glyph."""
    for ch in s:
        for yy, row in enumerate(FONT[ch]):
            for xx, v in enumerate(row):
                if v == "X":
                    r.rect(x + xx * scale, y + yy * scale, x + (xx + 1) * scale, y + (yy + 1) * scale, c)
        x += 3 * scale + gap
    return x - gap


def text_w(s, scale=1, gap=1):
    return len(s) * (3 * scale + gap) - gap


def _paper(pal):
    """The ramp used for paper, slips and label plates: the district's `paper` ramp if its Pal has one, else its wall ramp
    (linen in Records; the other districts' wall ramps are dark, so their kits set `PAL.paper` to a light ramp)."""
    return getattr(pal, "paper", pal.wall)


def dot(r, x, y, c):
    r.img[y, x] = c


# ------------------------------------------------------------------ Mira's courier chute

CHUTE_W, CHUTE_H = 32, 28   # body; the sprite also carries the tube above and the contact shadow below


def courier_chute(r, x0, y0, pal, ready):
    """A pneumatic courier chute seen from the high overhead camera, 2x1 cells: a metal cabinet (lit top plane,
    darker front face) with a slot in the top, a tube that rises into the ceiling at the right, a catch tray on the
    face with a stack of slips, and an indicator lamp. `ready` (Mira has a route to offer): a slip stands in the slot
    and the lamp is lit in the district accent. Body x0..x0+31, y0+8..y0+27; the tube reaches y0. Contact shadow below."""
    G, W, A = pal.glass, _paper(pal), pal.accent
    r.cast(x0, x0 + CHUTE_W, y0 + 28)
    body = r.mask(x0, y0 + 8, x0 + CHUTE_W, y0 + 28)
    r.img[body] = G[1]
    r.rect(x0, y0 + 8, x0 + CHUTE_W, y0 + 15, G[2])          # top plane
    r.rect(x0, y0 + 8, x0 + CHUTE_W, y0 + 9, G[3])
    r.rect(x0, y0 + 8, x0 + 1, y0 + 15, G[3])
    r.rect(x0, y0 + 15, x0 + CHUTE_W, y0 + 16, G[3])         # lit edge between the planes
    r.rect(x0, y0 + 27, x0 + CHUTE_W, y0 + 28, G[0])
    # the slot: an ink well with a lit lip in the accent
    r.rect(x0 + 5, y0 + 10, x0 + 19, y0 + 14, INK[0])
    r.rect(x0 + 6, y0 + 11, x0 + 18, y0 + 13, INK[1])
    r.rect(x0 + 5, y0 + 10, x0 + 19, y0 + 11, A[2])
    r.img[y0 + 10, x0 + 6] = A[3]
    if ready:
        sl = r.mask(x0 + 8, y0 + 6, x0 + 16, y0 + 12)         # a slip standing in the slot
        r.img[sl] = W[3]
        r.rect(x0 + 9, y0 + 8, x0 + 14, y0 + 9, W[1])
        r.rect(x0 + 9, y0 + 10, x0 + 12, y0 + 11, W[1])
        r.outline(sl)
        r.rect(x0 + 5, y0 + 10, x0 + 19, y0 + 11, A[2])
    # the tube rising into the ceiling, right side
    tube = r.mask(x0 + 23, y0, x0 + 28, y0 + 15)
    r.img[tube] = G[2]
    r.rect(x0 + 23, y0, x0 + 25, y0 + 15, G[3])
    r.rect(x0 + 27, y0, x0 + 28, y0 + 15, G[1])
    r.rect(x0 + 22, y0 + 12, x0 + 29, y0 + 14, G[1])         # collar
    r.rect(x0 + 22, y0 + 12, x0 + 29, y0 + 13, G[3])
    r.outline(tube)
    # catch tray on the face: recess, a stack of slips, a lit lip
    r.rect(x0 + 4, y0 + 18, x0 + 21, y0 + 26, INK[0])
    r.rect(x0 + 5, y0 + 19, x0 + 20, y0 + 25, INK[1])
    r.rect(x0 + 6, y0 + 21, x0 + 16, y0 + 25, W[2])
    r.rect(x0 + 6, y0 + 21, x0 + 16, y0 + 22, W[3])
    r.rect(x0 + 8, y0 + 23, x0 + 14, y0 + 24, A[2])
    r.rect(x0 + 5, y0 + 25, x0 + 20, y0 + 26, G[3])
    # indicator lamp
    r.rect(x0 + 24, y0 + 18, x0 + 30, y0 + 24, INK[0])
    if ready:
        r.rect(x0 + 25, y0 + 19, x0 + 29, y0 + 23, A[2])
        r.rect(x0 + 26, y0 + 20, x0 + 28, y0 + 22, A[3])
        r.img[y0 + 19, x0 + 25] = A[3]
    else:
        r.rect(x0 + 25, y0 + 19, x0 + 29, y0 + 23, G[1])
        r.rect(x0 + 25, y0 + 19, x0 + 29, y0 + 20, G[2])
    r.rect(x0 + 23, y0 + 25, x0 + 29, y0 + 26, W[3])        # label plate under the lamp
    r.rect(x0 + 24, y0 + 25, x0 + 28, y0 + 26, W[2])
    r.outline(body)
    return body


# ------------------------------------------------------------------ Mira reward decorations

def decor_courier_loop(r, x0, y0, pal):
    """Courier Loop: a loop-arrow medal on a small stand (the route plaque). 12 x 12."""
    A, W, WD = pal.accent, _paper(pal), pal.wood
    base = r.mask(x0 + 2, y0 + 10, x0 + 10, y0 + 12)
    r.img[base] = WD[1]
    r.rect(x0 + 2, y0 + 10, x0 + 10, y0 + 11, WD[2])
    r.outline(base)
    r.rect(x0 + 5, y0 + 9, x0 + 7, y0 + 10, WD[0])
    medal = r.disc(x0 + 6, y0 + 4.5, 6, 4.8)                       # a linen medal with a loop arrow on it
    r.img[medal] = W[3]
    r.img[medal & ~shifted(medal, 1, 1)] = W[2]
    ring = r.disc(x0 + 6, y0 + 4.5, 3.9, 2.9) & ~r.disc(x0 + 6, y0 + 4.5, 2.2, 1.4)
    ring &= ~((r.x > x0 + 7) & (r.y < y0 + 4))                      # the gap the arrowhead closes
    r.img[ring] = A[2]
    r.img[ring & ~shifted(ring, -1, -1)] = A[3]
    r.img[ring & ~shifted(ring, 1, 1)] = A[1]
    for (dx, dy) in ((7, 2), (8, 2), (9, 2), (8, 3), (9, 3), (9, 4)):   # the arrowhead, pointing down on the right of the ring
        r.img[y0 + dy, x0 + dx] = A[2]
    r.img[y0 + 2, x0 + 7] = A[3]
    r.outline(medal)


def decor_archive_folder(r, x0, y0, pal):
    """Archive Loop: a desk folder, the accent-colour cover with a lit tab and a sheet showing. 12 x 10."""
    A, W = pal.accent, _paper(pal)
    r.rect(x0 + 1, y0 + 1, x0 + 10, y0 + 3, W[3])          # sheet
    r.rect(x0 + 2, y0 + 2, x0 + 7, y0 + 3, W[1])
    cov = r.mask(x0, y0 + 3, x0 + 12, y0 + 10)
    r.img[cov] = A[2]
    r.rect(x0, y0 + 3, x0 + 12, y0 + 4, A[3])
    r.rect(x0, y0 + 9, x0 + 12, y0 + 10, A[1])
    r.rect(x0 + 11, y0 + 4, x0 + 12, y0 + 9, A[1])
    tab = r.mask(x0 + 1, y0 + 1, x0 + 6, y0 + 4)
    r.img[tab] = A[3]
    r.rect(x0 + 2, y0 + 2, x0 + 5, y0 + 3, A[1])
    r.rect(x0 + 3, y0 + 6, x0 + 9, y0 + 7, W[3])           # label strip
    r.rect(x0 + 4, y0 + 7, x0 + 7, y0 + 8, INK[1])
    r.outline(cov | tab | r.mask(x0 + 1, y0 + 1, x0 + 10, y0 + 3))


def decor_signed_sent(r, x0, y0, pal):
    """Signed and Sent: an envelope with a stamped seal and a signature line. 13 x 9."""
    A, W = pal.accent, _paper(pal)
    env_m = r.mask(x0, y0, x0 + 13, y0 + 9)
    r.img[env_m] = W[3]
    r.rect(x0, y0 + 7, x0 + 13, y0 + 9, W[2])
    for i in range(6):                                      # the flap's V
        r.img[y0 + 1 + i // 2, x0 + 1 + i] = W[1]
        r.img[y0 + 1 + i // 2, x0 + 11 - i] = W[1]
    r.rect(x0 + 2, y0 + 6, x0 + 7, y0 + 7, INK[2])           # signature line
    r.img[y0 + 5, x0 + 3] = INK[2]
    r.img[y0 + 5, x0 + 5] = INK[2]
    seal = r.disc(x0 + 10, y0 + 5.5, 2.4, 2.4)
    r.img[seal] = A[2]
    r.img[y0 + 5, x0 + 9] = A[3]
    r.img[y0 + 6, x0 + 11] = A[1]
    r.outline(env_m)


def decor_relay(r, x0, y0, pal):
    """Signal Keeper: a miniature relay, a device block with a wound coil, two terminals and a lit LED. 12 x 11."""
    G, A, F, W = pal.glass, pal.accent, pal.foliage, _paper(pal)
    plate = r.mask(x0, y0 + 9, x0 + 12, y0 + 11)
    r.img[plate] = W[1]
    r.rect(x0, y0 + 9, x0 + 12, y0 + 10, W[2])
    r.outline(plate)
    blk = r.mask(x0 + 1, y0 + 1, x0 + 11, y0 + 9)
    r.img[blk] = G[2]
    r.rect(x0 + 1, y0 + 1, x0 + 11, y0 + 2, G[3])
    r.rect(x0 + 1, y0 + 1, x0 + 2, y0 + 9, G[3])
    r.rect(x0 + 10, y0 + 2, x0 + 11, y0 + 9, G[1])
    r.rect(x0 + 1, y0 + 8, x0 + 11, y0 + 9, G[1])
    for k in range(3):                                      # wound coil
        r.rect(x0 + 3, y0 + 3 + 2 * k, x0 + 8, y0 + 4 + 2 * k, A[2])
        if k < 2:
            r.rect(x0 + 3, y0 + 4 + 2 * k, x0 + 8, y0 + 5 + 2 * k, A[1])
    r.rect(x0 + 3, y0 + 3, x0 + 8, y0 + 4, A[3])
    r.img[y0 + 3, x0 + 9] = F[3]                           # LED
    r.img[y0 + 4, x0 + 9] = F[2]
    r.outline(blk)
    for px_ in (x0 + 3, x0 + 8):                            # terminals
        r.rect(px_, y0 + 9, px_ + 1, y0 + 11, INK[1])


def decor_night_courier(r, x0, y0, pal):
    """Night Courier: a small satchel with a coral-family strap and a crescent charm on the flap. 12 x 10."""
    WD, A, G = pal.wood, pal.accent, pal.glass
    bag = r.mask(x0, y0 + 2, x0 + 12, y0 + 10)
    r.img[bag] = WD[2]
    r.rect(x0, y0 + 2, x0 + 12, y0 + 3, WD[3])
    r.rect(x0, y0 + 9, x0 + 12, y0 + 10, WD[0])
    r.rect(x0 + 11, y0 + 3, x0 + 12, y0 + 9, WD[1])
    flap = r.mask(x0 + 1, y0 + 3, x0 + 11, y0 + 7)
    r.img[flap] = WD[1]
    r.rect(x0 + 1, y0 + 3, x0 + 11, y0 + 4, WD[2])
    r.rect(x0 + 1, y0 + 6, x0 + 11, y0 + 7, WD[0])
    r.outline(bag)
    strap = r.mask(x0 + 3, y0, x0 + 5, y0 + 3)              # strap rising to the shoulder loop
    r.img[strap] = A[2]
    r.rect(x0 + 3, y0, x0 + 4, y0 + 3, A[3])
    r.rect(x0 + 5, y0 + 1, x0 + 9, y0 + 2, A[2])
    r.rect(x0 + 8, y0 + 1, x0 + 9, y0 + 3, A[1])
    for (dx, dy) in ((7, 4), (8, 4), (6, 5), (6, 6), (7, 7)):   # crescent charm
        r.img[y0 + dy, x0 + dx] = G[3]
    r.img[y0 + 5, x0 + 9] = A[3]



def folding_stool(r, x0, y0, pal):
    """Hal's folding stool, 1 cell: a canvas seat (wood ramp) on crossed legs (wall ramp), his tool roll (accent ramp) leaning on the right."""
    W, WD, A = pal.wall, pal.wood, pal.accent
    r.cast(x0 + 2, x0 + 12, y0 + 15, rows=1)
    for k in range(7):                                                   # crossed legs
        r.img[y0 + 8 + k, x0 + 3 + k] = W[1]
        r.img[y0 + 8 + k, x0 + 10 - k] = INK[1]
    r.rect(x0 + 2, y0 + 14, x0 + 5, y0 + 15, INK[1])
    r.rect(x0 + 9, y0 + 14, x0 + 12, y0 + 15, INK[1])
    seat = r.disc(x0 + 7, y0 + 5.5, 6, 3.6)
    r.img[seat] = WD[2]
    r.img[seat & ~shifted(seat, -1, -1)] = WD[3]
    r.img[seat & ~shifted(seat, 1, 1)] = WD[1]
    r.rect(x0 + 5, y0 + 5, x0 + 10, y0 + 6, WD[1])                      # a canvas seam
    r.outline(seat)
    roll = r.mask(x0 + 11, y0 + 4, x0 + 15, y0 + 13)                      # orange tool roll
    r.img[roll] = A[2]
    r.rect(x0 + 11, y0 + 4, x0 + 12, y0 + 13, A[3])
    r.rect(x0 + 14, y0 + 4, x0 + 15, y0 + 13, A[1])
    r.rect(x0 + 11, y0 + 7, x0 + 15, y0 + 8, INK[1])                      # straps
    r.rect(x0 + 11, y0 + 10, x0 + 15, y0 + 11, INK[1])
    r.outline(roll)


DECOR = {"courier_loop": decor_courier_loop, "archive_folder": decor_archive_folder, "signed_sent": decor_signed_sent,
         "relay": decor_relay, "night_courier": decor_night_courier}


def mira_decor(r, kind, x0, y0, pal):
    DECOR[kind](r, x0, y0, pal)


# ------------------------------------------------------------------ wave 2: reward desk decorations (Night Shift, Executive)

def decor_dawn_lamp(r, x0, y0, pal):
    """Desk for Dawn: a small desk lamp, a wood foot and stem under a warm shade with one lit step. 10 x 13."""
    WD, A, G = pal.wood, pal.accent, pal.glass
    foot = r.mask(x0 + 1, y0 + 11, x0 + 9, y0 + 13)
    r.img[foot] = WD[1]
    r.rect(x0 + 1, y0 + 11, x0 + 9, y0 + 12, WD[2])
    r.outline(foot)
    r.rect(x0 + 4, y0 + 5, x0 + 6, y0 + 11, WD[1])              # the stem
    r.rect(x0 + 4, y0 + 5, x0 + 5, y0 + 11, WD[2])
    shade = r.mask(x0, y0, x0 + 10, y0 + 6)
    r.img[shade] = A[2]
    r.rect(x0, y0, x0 + 10, y0 + 1, A[3])
    r.rect(x0, y0, x0 + 2, y0 + 6, A[3])
    r.rect(x0 + 8, y0 + 1, x0 + 10, y0 + 6, A[1])
    r.rect(x0 + 1, y0 + 5, x0 + 9, y0 + 6, A[1])
    r.outline(shade)
    r.img[y0 + 2, x0 + 4] = G[3]                                 # a pale glint on the shade: the first light of dawn
    r.img[y0 + 2, x0 + 5] = G[3]


def decor_name_plaque(r, x0, y0, pal):
    """Names on the Wall: a small desk plaque, an accent plate with three inked name lines on a wood base. 14 x 9."""
    WD, A, W = pal.wood, pal.accent, _paper(pal)
    base = r.mask(x0, y0 + 6, x0 + 14, y0 + 9)
    r.img[base] = WD[1]
    r.rect(x0, y0 + 6, x0 + 14, y0 + 7, WD[2])
    r.rect(x0, y0 + 8, x0 + 14, y0 + 9, WD[0])
    r.outline(base)
    plate = r.mask(x0 + 1, y0, x0 + 13, y0 + 6)
    r.img[plate] = A[2]
    r.rect(x0 + 1, y0, x0 + 13, y0 + 1, A[3])
    r.rect(x0 + 1, y0, x0 + 2, y0 + 6, A[3])
    r.rect(x0 + 12, y0 + 1, x0 + 13, y0 + 6, A[1])
    for i, w in enumerate((8, 6, 7)):                            # three names, each its own length
        r.rect(x0 + 3, y0 + 1 + i * 2, x0 + 3 + w, y0 + 2 + i * 2, W[3] if i != 1 else INK[1])
    r.outline(plate)


REWARD_DECOR = {"dawn_lamp": decor_dawn_lamp, "name_plaque": decor_name_plaque}


def reward_decor(r, kind, x0, y0, pal):
    REWARD_DECOR[kind](r, x0, y0, pal)


# ------------------------------------------------------------------ wave 2: the shared integration set
# The elevator door set, call panel, desk-front occluders and the optional-artifact props, drawn by the Orientation
# team's builders in shared_pieces.py (read-only here) with a district Pal. The geometry is copied from Orientation's
# own entries (orientation_quest.py) and check_elevator_geometry asserts it against orientation-atlas.json.

import shared_pieces as shp  # noqa: E402

IX0, IY0 = 64, 64   # capture origin for every integration piece (the Orientation scratch origin)

ARTIFACT_SLUGS = {
    "carbon_copy_a": "carbon_copy_a", "margin_stamp": "margin_stamp", "uncut_index": "uncut_index",
    "noor_annotation": "noors_annotation",          # the data and levels.md slug is noor_annotation, the drawing kind noors_annotation
    "id_envelope": "id_envelope", "alarm_strip": "alarm_strip", "scoring_proof": "scoring_proof",
    "original_routing_diagram": "original_routing_diagram", "ada_shift_book": "adas_shift_book",
    "public_audit_copy": "public_audit_copy",
}
ARTIFACT_NOTES = {
    "carbon_copy_a": "Carbon copy A (Records level 08): a sheet with a coral header over its carbon copy",
    "margin_stamp": "Margin stamp (Records level 09): a ruled sheet with a round coral stamp in the margin",
    "uncut_index": "Uncut index (Records level 10): an index sheet with four tabs along its long edge",
    "noor_annotation": "Noor's annotation (Records level 11): a page with a dry coral underline and a margin note over a second sheet",
    "id_envelope": "ID envelope (Systems level 12): an envelope with an address block and a stamp for a vanished department",
    "alarm_strip": "Alarm strip (Systems level 14): a paper strip of six alert pictograms with one extra department mark",
    "scoring_proof": "Scoring proof (Systems level 15): a proof sheet with three rising bars (a longer route scores higher)",
    "original_routing_diagram": "Original routing diagram (Systems level 16): a diagram of nodes and traces with three signatures",
    "ada_shift_book": "Ada's shift book (Night Shift level 19): a small closed book with a name label and a ribbon marker",
    "public_audit_copy": "Public audit copy (Executive level 20): a bound audit copy with a seal over a second sheet",
}
ARTIFACT_LEVELS = {"records": ("carbon_copy_a", "margin_stamp", "uncut_index", "noor_annotation"),
                   "systems": ("id_envelope", "alarm_strip", "scoring_proof", "original_routing_diagram"),
                   "nightshift": ("ada_shift_book",), "executive": ("public_audit_copy",)}


def call_panel_stop_lit(r, x0, y0, pal):
    """The call panel with the Executive stop lit (Night Shift, revealed by level 19): the base panel, its display's
    second bar and the up button turned to the accent's lit step."""
    shp.elevator_call_panel(r, x0, y0, pal)
    A = pal.accent
    r.rect(x0 + 6, y0 + 4, x0 + 9, y0 + 5, A[3])
    btn = r.disc(x0 + 6, y0 + 8 + 2.5, 3.2)
    r.img[btn] = A[3]
    r.img[r.edge(btn)] = INK[0]
    r.rect(x0 + 6, y0 + 9, x0 + 7, y0 + 10, INK[0])
    r.rect(x0 + 5, y0 + 10, x0 + 8, y0 + 11, INK[0])


def fit_front(front, desk):
    """Pixel check: the desk-front occluder `front` (a Piece) equals the desk sprite `desk` (a Piece) wherever it is opaque.
    Returns (differing pixels, opaque pixels)."""
    fx, fy = front.fp_room[0] - front.tl[0], front.fp_room[1] - front.tl[1]
    dx, dy = desk.fp_room[0] - desk.tl[0], desk.fp_room[1] - desk.tl[1]
    h, w = front.sprite.shape[:2]
    bad = 0
    n = 0
    for j in range(h):
        for i in range(w):
            if front.sprite[j, i, 3] == 0:
                continue
            n += 1
            ri, rj = i - fx + dx, j - fy + dy
            if not (0 <= rj < desk.sprite.shape[0] and 0 <= ri < desk.sprite.shape[1]) or not np.array_equal(front.sprite[j, i], desk.sprite[rj, ri]):
                bad += 1
    return bad, n


def artifact_pal(pal):
    """artifact_prop paints paper with the wall ramp; a district whose wall ramp is dark (steel, indigo, navy) carries a light
    `paper` ramp on its Pal (set by its kit module), so the artifacts get a Pal clone whose wall ramp is that paper."""
    import copy
    p = copy.copy(pal)
    if hasattr(pal, "paper"):
        p.wall = pal.paper
    return p


def integration_pieces(mk, pal, kit, desks=None, desk_pal=None):
    """The wave-2 shared set for one district. `mk(name, draw, box, fp, cells, collision, layer, kind, shadow=True,
    shadow_rect=None, y_sort=False, note='', tags=[])` captures a piece (a Night Shift mk also runs its edge passes).
    `desks` maps 'desk_a' / 'desk_b' to the district's own desk Pieces (they get an occluder; a kit without them passes None); `desk_pal` is the
    Pal the district's desk was recoloured with when it differs from `pal` (Systems and Executive map the desk's paper to their floor ramp).
    Returns (pieces, state sets)."""
    x0, y0 = IX0, IY0
    out = []
    box = (x0, y0, x0 + 48, y0 + 48)
    for nm, t, coll, note in (
            ("elevator_closed", 0.0, ["111", "111", "000"], "doors shut: two steel leaves meet at a centre seam, a casing with two lamps, a lit floor indicator, a lit LIFT mat in front"),
            ("elevator_half", 0.5, ["111", "111", "000"], "leaves slid 6 px into the jamb pockets: the warm cab shows between them"),
            ("elevator_open", 1.0, ["111", "101", "000"], "leaves fully in the pockets (11 px, a 1 px lip stays): the cab is open and the centre cell walks in")):
        out.append(mk(nm, lambda r, t=t: shp.elevator_doors(r, x0, y0, pal, t), box, (x0, y0), (3, 3), coll, "rear_wall", "door", shadow=False, shadow_rect=(0, 32, 48, 2),
                      y_sort=False, note=f"elevator, {note}. Orientation's module in the {kit} ramps (shared_pieces.elevator_doors): 3 x 3 cells, rows 0-1 are the north wall, "
                                         "row 2 the lit mat. Replaces three wall_n_plain columns", tags=["elevator", "door", "sliding", nm.split("_")[1], "wave 2"]))
    out.append(mk("elevator_call_panel", lambda r: shp.elevator_call_panel(r, x0, y0, pal), (x0, y0, x0 + 12, y0 + 22), (x0, y0), (1, 2), ["0", "0"], "rear_wall", "wall",
                  shadow=False, y_sort=False, note=f"wall call panel for the elevator, {kit} ramps (shared_pieces.elevator_call_panel): steel plate, small lit display, up and down buttons. "
                  "Overlay on wall_n_plain (no collision of its own); place it on the wall face 9 px below the wall top, one cell beside the elevator", tags=["elevator", "panel", "interact", "wave 2"]))
    if kit == "nightshift":
        out.append(mk("elevator_call_panel_executive_lit", lambda r: call_panel_stop_lit(r, x0, y0, pal), (x0, y0, x0 + 12, y0 + 22), (x0, y0), (1, 2), ["0", "0"], "rear_wall", "wall",
                      shadow=False, y_sort=False, note="the call panel with the Executive stop lit: the display's second bar and the up button in the lit warm step (revealed by level 19). "
                      "Same geometry as elevator_call_panel", tags=["elevator", "panel", "interact", "executive", "wave 2"]))
    anims = {"elevator": {"kind": "state_set", "default": "closed",
                          "states": {"closed": {"entries": ["elevator_closed"], "blocked": True}, "half": {"entries": ["elevator_half"], "blocked": True},
                                     "open": {"entries": ["elevator_open"], "blocked": False}},
                          "play": ["closed", "half", "open"], "ms_per_frame": 120,
                          "note": "play forward on approach or arrival, backward on leave; only open lets the centre cell through (the same set as Orientation's, in the district ramps)"}}
    if kit == "nightshift":
        anims["elevator_panel"] = {"kind": "state_set", "default": "base",
                                   "states": {"base": {"entries": ["elevator_call_panel"]}, "executive_lit": {"entries": ["elevator_call_panel_executive_lit"]}},
                                   "note": "level 19: the Executive stop lights on the call panel"}
    if desks:
        fx, fy = x0, y0 + 2
        assert (fx + fy) % 3 == (16 + 78) % 3 == (246 + 46) % 3   # the plant's lit tips depend on (x + y) % 3, as in Orientation
        for nm, seed in (("desk_a_front", 7), ("desk_b_front", 8)):
            p = mk(nm, lambda r, seed=seed: shp.desk_front(r, fx, fy, desk_pal or pal, seed), (fx, fy + shp.FRONT_TOP, fx + 35, fy + shp.FRONT_BOT), (fx, fy), (2, 1), ["00"], "front_prop", "prop",
                   shadow=False, y_sort=True, note=f"occluder for {nm[:6]}: the desk's monitor and first 8 px of top plane redrawn on front_prop so a seated worker's lower body is hidden; "
                   "seamless over the desk (same pixels). Place at the desk origin after the actors; seat convention in ORIENTATION_KIT_SPEC", tags=["desk", "front", "occluder", "wave 2"])
            bad, n = fit_front(p, desks[nm[:6]])
            assert bad == 0, f"{kit} {nm}: {bad} of {n} opaque pixels differ from the district desk"
            out.append(p)
    apal = artifact_pal(pal)
    for slug in ARTIFACT_LEVELS[kit]:
        k = ARTIFACT_SLUGS[slug]
        out.append(mk(f"artifact_{slug}", lambda r, k=k: shp.artifact_prop(r, x0, y0, apal, k), (x0, y0, x0 + 16, y0 + 16), (x0, y0), (1, 1), ["0"], "front_prop", "prop",
                      shadow=True, y_sort=False, note=ARTIFACT_NOTES[slug] + ". 16 x 16 px with a baked contact shadow and a small pale glass-step glint at the upper left as the inspectable cue "
                      "(never a UI marker colour). No collision: lay it on a desk, a table or a blocked cell", tags=["artifact", "inspectable", slug, "wave 2"]))
    return out, anims


def check_elevator_geometry(entries, orient_atlas_json):
    """Assert the district's elevator, panel and occluder entries have Orientation's geometry (everything but pixels, rect, note).
    `entries` maps name -> atlas entry dict of the district."""
    keys = ("kind", "size_px", "footprint", "collision", "layer", "y_sort", "anchor", "composite")
    oe = {e["name"]: e for e in orient_atlas_json["entries"]}
    for nm in ("elevator_closed", "elevator_half", "elevator_open", "elevator_call_panel", "desk_a_front", "desk_b_front"):
        if nm not in entries:
            continue
        for k in keys:
            assert entries[nm][k] == oe[nm][k], f"{nm}.{k}: {entries[nm][k]} != Orientation {oe[nm][k]}"
        assert entries[nm].get("contact_shadow") == oe[nm].get("contact_shadow"), f"{nm}.contact_shadow"
    for nm, e in entries.items():
        if nm.startswith("artifact_") and nm[9:] in ARTIFACT_SLUGS:
            o = oe["artifact_unissued_badge"]
            for k in keys:
                assert e[k] == o[k], f"{nm}.{k}: {e[k]} != Orientation artifact {o[k]}"
