"""Hal (systems technician) frames, hand-placed at 16x24 logical px.

Status: Candidate, pending director review. Built on the person rules approved at Gate 1
(gate1/GATE1_ENGINEER_SPEC.md) and the cast frame rule (IVO_SPEC.md). Spec: HAL_SPEC.md.
Skin and hair come from CAST_RAMPS in palettes/district_palettes.py (never retyped here).
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "gate1"))
sys.path.insert(0, os.path.join(HERE, "..", "palettes"))
import district_palettes as dp  # noqa: E402
import engineer_sprites as eng  # noqa: E402  (shared walk legs and lower())

_RAMP = dp.CAST_RAMPS["hal"]

PAL = {
    ".": None,
    "o": "#202337",
    # hair, sandy blond (CAST_RAMPS): fill D C B, A only on contour / fringe tips
    **dict(zip("ABCD", _RAMP["hair"])),
    # skin, golden brown (CAST_RAMPS): fill n m l, k only on contour / forehead shadow
    **dict(zip("klmn", _RAMP["skin"])),
    # utility vest, steel cobalt (hue 219-225, outside the teal band; at most 53% saturation): fill s r q, p on contour and seams
    "p": "#1B2A58", "q": "#2D4585", "r": "#4767AD", "s": "#86A4DA",
    # long-sleeve undershirt, warm stone: lit y, fill x, shade w
    "w": "#8F8372", "x": "#C7B7A0", "y": "#E6DBC8",
    # work trousers, neutral charcoal
    "O": "#353539", "P": "#4F4F55",
    # boots, heavy brown leather
    "S": "#3A2A28", "T": "#664636", "U": "#8E6244",
    # thick gloves, the ink ramp: shade g, fill h, lit j
    "g": "#343650", "h": "#535971", "j": "#777A8C",
    # tool roll, Systems safety orange (accent ramp): shade E, fill F, lit G, glint H
    "E": "#7A2F1B", "F": "#C2521A", "G": "#F2842B", "H": "#FFB36B",
}

SLOTS = {"hair": "ABCD", "skin": "klmn", "jacket": "pqrs", "trousers": "OP",
         "sleeves": "wxy", "gloves": "gjh", "roll": "EFGH"}
HAIR_SKIN_SEPARATED = True   # blond hair and golden skin are close in value: a k pixel always sits between
GLINT_LIMITS = {"H": 1}

# Torso rows 10-16 (vest 7 rows), trousers from row 17, shared legs below. The head is rows 1-9 (8 rows of
# head and a tuft row), so Hal is 2 px shorter than the Engineer: the compact silhouette of hal.md.
# The tool roll is tucked under his left arm, pointing forward, and is painted by finish() afterwards.
S = [
"................",
"......o..o......",
".....oDooCo.....",
"....oDDCDCBo....",
"...oDCDBCCBBo...",
"...okABkkBkko...",
"...oknknmknko...",
"...oknonnonko...",
"...oknnmmnlko...",
"....oklmmlko....",
"...osrxyyxrqo...",
"..ossrpxxprqqo..",
"..oyxsrpqqqxwo..",
"..oyxqqpqqqxwo..",
".ojjhrrpqqqjhho.",
".ohhgqqpqqqhggo.",
".oooopqqqqpoooo.",
] + eng.S[17:]

N = [
"................",
"......o..o......",
".....oDooCo.....",
"....oDDCDCBo....",
"...oDCDBCCBBo...",
"...oCDBBCBBo....",
"....oCBCCBBBo...",
"...okBBCBBBko...",
"...okkAAAAkko...",
"....okllllko....",
"...osrrrrrrqo...",
"..ossrrrrrrqqo..",
"..oyxsrrpqqxwo..",
"..oyxsrrpqqxwo..",
".ojjhrrrpqqjhho.",
".ohhgqqqpqqhggo.",
".oooopqqpqqpooo.",
] + eng.N[17:]

E = [
"................",
"......o..o......",
".....oDooCo.....",
"....oDDCDCBo....",
"...oDCDCCBBBo...",
"...oCDCBkAkko...",
"...oBBCBkmnno...",
"...oBBAkmnono...",
"...okkknmmnlo...",
"....okklmmko....",
"...ossrrrxyqo...",
"...ossrrrrrqo...",
"...osryxrrqqo...",
"...osogggrqqo...",
"...osojjhjoqo...",
"...osohhgooqo...",
"...opoooopppo...",
] + eng.E[17:]

W = [
"................",
"......o..o......",
".....oDooBo.....",
"....oDDCCBBo....",
"...oDCCDCBBBo...",
"...okkAkBCBBo...",
"...onnnkBCBBo...",
"...ononnkABBo...",
"...olnmmnkkko...",
"....okmmlkko....",
"...osxyrrrrqo...",
"...ossrrrrrqo...",
"...osrryxrqqo...",
"...osrrgggoqo...",
"...osojjjhoqo...",
"...osoohhgoqo...",
"...opppoooopo...",
] + eng.W[17:]

# --- the tool roll (painted by finish(), after the body, so it never changes shape) ------------------------
# Tucked under his left arm and pointing forward. S and N see it lying along his side (cord bands, the
# end disc at the bottom in S); E and W see its length protruding past the belt, tool tips at the front.
# Safety orange: lit G, fill F, shade E, one H glint, a cream cord y.
ROLL_S = [".ooo.", "oHGFo", "oyyyo", "oGFEo", "oFEEo", ".ooo."]
ROLL_N = [".ooo.", "oGGFo", "oyyyo", "oGFEo", "oFFEo", ".ooo."]
ROLL_E = [".oooooo.", "oHGyFEh.", "oFFyEEh.", ".oooooo."]
ROLL_W = [".oooooo.", ".hEFyGHo", ".hEEyFFo", ".oooooo."]
# facing: (top row, left col, art)
ROLLS = {"s": (12, 10, ROLL_S), "n": (12, 1, ROLL_N), "e": (15, 8, ROLL_E), "w": (15, 0, ROLL_W)}


def finish(frame, facing, dy=0):
    """Paint the roll onto a frame; dy is the 1 px settle the body took (the roll moves with it)."""
    out = [list(r) for r in frame]
    r0, c0, art = ROLLS[facing]
    for j, line in enumerate(art):
        for i, ch in enumerate(line):
            if ch != ".":
                out[r0 + dy + j][c0 + i] = ch
    return ["".join(r) for r in out]


lower = eng.lower
BASE = {"s": S, "n": N, "e": E, "w": W}
IDLE = {f: [finish(g, f), finish(lower(g), f, 1)] for f, g in BASE.items()}


def walk(base, legs, facing):
    out = []
    for i, lg in enumerate(legs):
        raw = base[0:18] + lg
        out.append(finish(lower(raw), facing, 1) if i % 2 == 0 else finish(raw, facing))
    return out


SIDE_LEGS = (eng.LEG_C0, eng.LEG_P1, eng.LEG_C2, eng.LEG_P3)
WALK = {
    "s": walk(S, eng.LEGS_S, "s"),
    "n": walk(N, eng.LEGS_N, "n"),
    "e": walk(E, SIDE_LEGS, "e"),
    "w": walk(W, [[r[::-1] for r in lg] for lg in SIDE_LEGS], "w"),
}
