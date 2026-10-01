"""Noor (Records archive clerk) frames, hand-placed at 16x24 logical px.

Status: Candidate, pending director review. Built on the person rules approved at Gate 1
(gate1/GATE1_ENGINEER_SPEC.md) and the cast frame rule (IVO_SPEC.md): 16x24, anchor between
columns 7|8, feet on row 23, darkest step on contours only, renderer-drawn shadow.
Spec: NOOR_SPEC.md. Skin and hair come from CAST_RAMPS (palettes/district_palettes.py).
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "gate1"))
sys.path.insert(0, os.path.join(HERE, "..", "palettes"))
import engineer_sprites as eng  # noqa: E402  (shared walk legs and lower())
from district_palettes import CAST_RAMPS, DISTRICTS  # noqa: E402

_HAIR, _SKIN = CAST_RAMPS["noor"]["hair"], CAST_RAMPS["noor"]["skin"]
_REC = DISTRICTS["records"]

PAL = {
    ".": None,
    "o": "#202337",
    # hair (blue-black, from CAST_RAMPS): fill B C D, A only on contour and the fringe underside
    **dict(zip("ABCD", _HAIR)),
    # skin (light olive, from CAST_RAMPS): fill n m l, k only on contour / occlusion
    **dict(zip("klmn", _SKIN)),
    # shirt, linen: fill r q, s on the lit edge, p on contour and seams
    "p": "#8A8985", "q": "#C9C7BF", "r": "#DAD8D0", "s": "#EFEFEC",
    # trousers, sea blue (hue 195, saturation <= 40%)
    "O": "#2A4A60", "P": "#3F7388",
    # shoes, dark cherry (Records wood ramp)
    "S": _REC["wood"][0], "T": _REC["wood"][1], "U": _REC["wood"][2],
    # cherry-wood stamp (Records wood ramp): w base shadow, x shaded face, y face, z glint
    "w": _REC["wood"][0], "x": _REC["wood"][1], "y": _REC["wood"][2], "z": _REC["wood"][3],
    # coral file folder (Records accent ramp)
    "c": _REC["accent"][0], "d": _REC["accent"][1], "e": _REC["accent"][2], "f": _REC["accent"][3],
    # sea-blue file tabs (Records glass ramp)
    "g": _REC["glass"][0], "h": _REC["glass"][1], "j": _REC["glass"][2], "J": _REC["glass"][3],
}

SLOTS = {"hair": "ABCD", "skin": "klmn", "jacket": "pqrs", "trousers": "OP"}
HAIR_SKIN_SEPARATED = True   # the hair/skin lightness gap is narrow: a skin `k` or ink pixel always sits between
GLINT_LIMITS = {"z": 1, "J": 3, "f": 8}


# Rows 0-16 of each facing (head, shirt with rolled sleeves, hips); row 17 and the legs come from the
# shared poses. The shirt ends at row 15, so the trousers run 8 rows (16-23): the long legs of a tall figure.
S_TOP = [
    "......o..oo.....",
    ".....oDooDCo....",
    "....oDDDCCDBo...",
    "...oDDCCDDCBo...",
    "...oCDDCCCCBo...",
    "...oCCCCAAAAo...",
    "...oAAkkmmmlo...",
    "...olnommomlo...",
    "...olnmmmmmlo...",
    ".....okllko.....",
    "....ospkkpqo....",
    "...ossrrrrqqo...",
    "...orrrrqrqqo...",
    "...osrrrqrrro...",
    "...omqrrqrqlo...",
    "...omqqqqqqlo...",
    "....oOPPPPPPo...",
]
N_TOP = [
    ".....oo..o......",
    "....oCDooDo.....",
    "....oDDDCCDBo...",
    "...oDDCCDDCBo...",
    "...oCDDCCCCBo...",
    "...oCCCCCBBBo...",
    "...okBCCCBCko...",
    "...olkBCCkklo...",
    "...olkkkkkklo...",
    ".....okllko.....",
    "....osrrrrqo....",
    "...ossrrrrqqo...",
    "...orrrrrrqqo...",
    "...osrrrqrrro...",
    "...omqrrqrqlo...",
    "...omqqqqqqlo...",
    "....oOPPPPPPo...",
]
E_TOP = [
    ".......o.oo.....",
    "....oooDoDCo....",
    "....oDDDCCDBo...",
    "...oDDCCDDCBo...",
    "...oCDDCCCBBo...",
    "...oCCBCCAAAo...",
    "...oBCCAAmmmo...",
    "...oBBAlmnomo...",
    "...oBAklmmmmo...",
    "....oklmmlko....",
    "....osqkpqqo....",
    "....ossrrrqo....",
    "....osrrqrqo....",
    "....orssqrqo....",
    "....ormmqrqo....",
    "....oqmlqqpo....",
    "....oOPPPPOo....",
]
W_TOP = [
    "......o.oo......",
    "....ooDoDCoo....",
    "...oDDDCCCBo....",
    "...oDDCCDCBBo...",
    "...oDDCCCDBBo...",
    "...oAAACCCBBo...",
    "...ommmAACCBo...",
    "...omonmlABBo...",
    "...ommmmlkABo...",
    "....oklmmlko....",
    "....osrpkqqo....",
    "....osrrrqqo....",
    "....osrqrrqo....",
    "....osrqssqo....",
    "....osrqmmqo....",
    "....osqqlmpo....",
    "....oOPPPPOo....",
]

E_LEGS = eng.E_LEGS                                   # rows 17-23 of the idle side view
W_LEGS = [r[::-1] for r in eng.E_LEGS]


def lower(frame):
    """1 px settle (shared): head and torso down, dropping row 17. Props are painted afterwards."""
    return eng.lower(frame)


# --- props, painted onto finished frames --------------------------------------------------------
def paint(frame, x, y, art, under=False):
    """Paste a key grid at column x, row y. A space keeps the pixel underneath; with under=True
    only transparent pixels are filled, so the art sits behind the body."""
    out = [list(r) for r in frame]
    for j, line in enumerate(art):
        for i, ch in enumerate(line):
            if ch != " " and 0 <= y + j < 24 and 0 <= x + i < 16 and (not under or out[y + j][x + i] == "."):
                out[y + j][x + i] = ch
    return ["".join(r) for r in out]


# Cherry-wood stamp, 5x6, a T/mushroom: a lit knob (z glint, y face, x shade) on a narrow neck gripped by a fist,
# above a flat dark ink plate. It is the darkest prop. STAMP_A is gripped from the right (S, E), STAMP_B from the left.
STAMP_A = ["..oo.", ".ozyo", ".oyxo", ".mxl.", "oxxxo", "owwwo"]
STAMP_B = [".oo..", "ozyo.", "oyxo.", ".mxl.", "oxxxo", "owwwo"]
# Pale coral file folder, a flat 4x7 rectangle: two sea-blue tabs on the top edge, a pale face (f) with a coral
# edge (e) and a sea-blue label. It is the lightest prop. FOLDER_A hangs to the left of the body, FOLDER_B to the right.
FOLDER_A = ["jJ..", "oooo", "ofee", "oJfe", "ofee", "ofee", "oooo"]
FOLDER_B = ["..Jj", "oooo", "eefo", "efJo", "eefo", "eefo", "oooo"]

# (x, y, art, under) per facing at the unlowered position. under=True paints only transparent pixels, so that
# prop sits partly behind the body. Exactly one prop per facing is partly hidden, so they never read as a pair.
PROPS = {
    "s": [(0, 10, FOLDER_A, True), (9, 11, STAMP_A, False)],
    "n": [(12, 10, FOLDER_B, False), (1, 11, STAMP_B, True)],
    "e": [(2, 10, FOLDER_A, True), (10, 11, STAMP_A, False)],
    "w": [(10, 10, FOLDER_B, True), (1, 11, STAMP_B, False)],
}


def finish(frame, facing, dy=0):
    for x, y, art, under in PROPS[facing]:
        frame = paint(frame, x, y + dy, art, under)
    return frame


def walk(top, legs, facing):
    out = []
    for i, lg in enumerate(legs):
        raw = top[0:18] + lg
        out.append(finish(lower(raw), facing, 1) if i % 2 == 0 else finish(raw, facing))
    return out


S = S_TOP + eng.S[17:]
N = N_TOP + eng.N[17:]
E = E_TOP + E_LEGS
W = W_TOP + W_LEGS
SIDE_LEGS = (eng.LEG_C0, eng.LEG_P1, eng.LEG_C2, eng.LEG_P3)
IDLE = {f: [finish(fr, f), finish(lower(fr), f, 1)] for f, fr in (("s", S), ("n", N), ("e", E), ("w", W))}
WALK = {
    "s": walk(S, eng.LEGS_S, "s"),
    "n": walk(N, eng.LEGS_N, "n"),
    "e": walk(E, SIDE_LEGS, "e"),
    "w": walk(W, [[r[::-1] for r in lg] for lg in SIDE_LEGS], "w"),
}
