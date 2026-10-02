"""Hal (systems technician) frames, hand-placed at 16x24 logical px.

Status: Approved by the director 2026-10-02. Built on the person rules approved at Gate 1
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


# --- Extra animation sets (tasks 8.1-8.2, approved 2026-10-02) ------------------------------------------------
# Same format as the Engineer's (engineer_sprites.EXTRA). Frames are built from the raw (rollless) grids
# above plus hand-placed stamps, then finish() paints the roll, so the roll never deforms. IDLE and WALK
# above are never edited. Stamp rule (eng.stamp): a space keeps the pixel beneath, "." clears it.
# Rows 0-9 of every frame hold head keys only, so no glove or tool goes above row 10.
stamp, stamps, dip, tilt = eng.stamp, eng.stamps, eng.dip, eng.tilt

# Free-hand glove raised toward the panel (S: his right hand, screen-left; N: his right hand, screen-right).
S_UP1 = [(0, 13, [".ojjh"]), (0, 14, [".ohhg"]), (0, 15, [".oooo"]), (0, 16, ["....o"])]
S_UP2 = [(0, 12, [".ojjh"]), (0, 13, [".ohhg"]), (0, 14, [".oooo"]), (0, 15, ["....o"]), (0, 16, ["....o"])]
N_UP1 = [(11, 13, ["jhho"]), (11, 14, ["hggo"]), (11, 15, ["oooo"])]
N_UP2 = [(11, 12, ["jhho"]), (11, 13, ["hggo"]), (11, 14, ["oooo"]), (11, 15, ["o..."]), (11, 16, ["po.."])]
# The tool: a steel shaft and tip (ink ramp) held in the raised glove, growing as the hand lifts.
S_TOOL1 = [(1, 10, ["j"]), (1, 11, ["h"]), (1, 12, ["h"]), (0, 10, ["o"]), (0, 11, ["o"]), (0, 12, ["o"])]
S_TOOL2 = [(1, 10, ["j"]), (1, 11, ["h"]), (0, 10, ["o"]), (0, 11, ["o"])]
N_TOOL1, N_TOOL2 = [(14, 11, ["j"]), (14, 12, ["h"])], [(14, 10, ["j"]), (14, 11, ["h"])]
# E and W: the forearm comes forward (stone sleeve), the glove passes the belt line, the tool points ahead.
E_REACH1 = [(5, 13, ["rxxxgjjho"]), (5, 14, ["rrrqqhhgo"]), (5, 15, ["rrqqqq"])]
E_REACH2 = [(5, 13, ["rxxxxgjjhhj"]), (5, 14, ["rrrqqqhhgo"]), (5, 15, ["rrqqqq"])]
W_REACH1 = [(2, 13, ["ojjhgxxxr"]), (2, 14, ["ohhgrrqqq"]), (5, 15, ["rrrqqq"])]
W_REACH2 = [(0, 13, ["jhjjhgxxxxr"]), (1, 14, ["ohhgrrqqqq"]), (5, 15, ["rrrqqq"])]
E_TOOL1, W_TOOL1 = [(14, 13, ["hj"])], [(0, 13, ["jh"])]


def fin(f, g, low=False):
    """Finish a raw grid: settle it 1 px when `low`, then paint the roll at the same offset."""
    return finish(lower(g), f, 1) if low else finish(g, f)


def _extra():
    s0, n0, e0, w0 = S, N, E, W
    # ---- interact: the free glove lifts a tool to the panel (S, N), or the arm reaches ahead (E, W) ------
    interact = {
        "s": [fin("s", stamps(s0, *S_UP1, *S_TOOL1)), fin("s", stamps(s0, *S_UP2, *S_TOOL2))],
        "n": [fin("n", stamps(n0, *N_UP1, *N_TOOL1)), fin("n", stamps(n0, *N_UP2, *N_TOOL2))],
        "e": [fin("e", stamps(e0, *E_REACH1, *E_TOOL1)), fin("e", stamps(e0, *E_REACH2))],
        "w": [fin("w", stamps(w0, *W_REACH1, *W_TOOL1)), fin("w", stamps(w0, *W_REACH2))],
    }
    # ---- puzzled (hal.md "head tilt / scratch"): the head tilts, then the free glove comes up open ---------
    sp, np_ = stamps(tilt(s0, -1), *S_UP2), stamps(tilt(n0, 1), *N_UP2)
    ep, wp = stamps(tilt(e0, -1), *E_REACH1), stamps(tilt(w0, 1), *W_REACH1)
    puzzled = {
        "s": [fin("s", tilt(s0, -1)), fin("s", sp), fin("s", sp, True)],
        "n": [fin("n", tilt(n0, 1)), fin("n", np_), fin("n", np_, True)],
        "e": [fin("e", tilt(e0, -1)), fin("e", ep), fin("e", ep, True)],
        "w": [fin("w", tilt(w0, 1)), fin("w", wp), fin("w", wp, True)],
    }
    # ---- anxious (hal.md portrait "Anxious"): the head sinks onto the shoulders and the shoulders drop ------
    anxious = {f: [fin(f, dip(g)), fin(f, dip(g), True), fin(f, dip(g, 2), True)]
               for f, g in (("s", s0), ("n", n0), ("e", e0), ("w", w0))}
    return {"interact": interact, "react_puzzled": puzzled, "react_anxious": anxious}


# --- Working poses: crouched repair, seated on the stool, pulling the false panel (and the stool prop) -------------
# Built from the approved raw grids: the head rows are the base head, moved down; the rest is hand-placed rows.
# The roll is painted by hand per pose (it lies on the near thigh when he is low, so finish() is not used there).
# Row rule: rows 0-9 hold head keys only (hair, skin, outline), so gloves never go above row 10.
BL = "." * 16


def _paint(fr, art, r0, c0):
    out = [list(r) for r in fr]
    for j, line in enumerate(art):
        for i, ch in enumerate(line):
            if ch != ".":
                out[r0 + j][c0 + i] = ch
    return ["".join(r) for r in out]


def _shift(fr, y0, y1, dx):
    """Slide rows y0..y1 dx px sideways (a head lean)."""
    out = list(fr)
    for y in range(y0, y1 + 1):
        n = ["."] * 16
        for x, ch in enumerate(fr[y]):
            if ch != "." and 0 <= x + dx < 16:
                n[x + dx] = ch
        out[y] = "".join(n)
    return out


def _mir(half):
    return half + half[::-1]


def _flip(rows):
    return [r[::-1] for r in rows]


# ---- crouch_repair: head at rows 8-16 (E/W: 7-15), 2-3 torso rows, the arm and tool to the panel, short legs ----
CROUCH_ROLL_E = [".oooooo.", "oHGyFEh.", ".oooooo."]          # 3-row roll lying across the near thigh
CROUCH_LEGS_E = [
    "...opPPPPPPPPo..",
    "...oPPPPPPPPPo..",
    "...oTUUToTUUUTo.",
    "...oSSSSoSSSSSo.",
]
CROUCH_LOW_N = [_mir(x) for x in (".oOPPxqq", "oOPPPoqq", "oSTTTSoo", "oSSSSSo.")]


def crouch_s(tool, hdx=0):
    low = [
        ".oOPPxhhhhxPPOo.",
        "oOPPPojjjjoPPPOo",
        "oTUUUTojhoTUUUTo" if tool else "oTUUUTooooTUUUTo",
        "oSSSSSooooSSSSSo" if tool else "oSSSSSo..oSSSSSo",
    ]
    fr = [BL] * 8 + S[1:10] + [S[10], S[11], S[12]] + low
    fr = _shift(fr, 8, 16, hdx) if hdx else fr
    return _paint(fr, ROLL_S, 17, 10)


def crouch_e(reach):
    st = stamps(E, *(E_REACH2 if reach else E_REACH1))
    fr = [BL] * 7 + E[1:10] + [st[10], st[12], st[13], st[14]] + CROUCH_LEGS_E
    return _paint(fr, CROUCH_ROLL_E, 19, 4)


def crouch_w(reach):
    st = stamps(W, *(W_REACH2 if reach else W_REACH1))
    fr = [BL] * 7 + W[1:10] + [st[10], st[12], st[13], st[14]] + _flip(CROUCH_LEGS_E)
    return _paint(fr, _flip(CROUCH_ROLL_E), 19, 4)


def crouch_n(up):
    fr = [BL] * 8 + N[1:10] + [N[10], N[11], N[12]] + CROUCH_LOW_N
    y = 17 if up else 18
    fr = _paint(fr, ["jjh", "hhg"], y, 1)
    fr = _paint(fr, ["jhh", "hgg"], y, 12)
    return _paint(fr, ROLL_N, 17, 1)


# ---- seated_stool: head rows 3-11, hips on row 17, thighs forward, boots on rows 21-23. The stool prop (below) is
# placed so its anchor (8, 16) lands on Hal's anchor (8, 24): its cell then starts at row 8 of this frame. ---------
SEATED_LOW_S = [_mir(x) for x in ("....opqq", "....oOPP", "..ojjOPP", ".oOPPPo.", "..oOPPo.", "..oTUUTo", "..oSTTSo")] \
    + [_mir("...oooo.")]
SEATED_LOW_E = [
    "...opPPPPPPPPo..",
    "...oOPPPPPPPPOo.",
    "........oOPPPo..",
    "........oOPPPo..",
    ".......oTUUUUTo.",
    ".......oSTTTTSo.",
    ".......oooooooo.",
]


def seated_s(glance=0):
    fr = [BL] * 3 + S[1:10] + [S[10], S[11], S[12], S[13]] + SEATED_LOW_S
    fr = _shift(fr, 3, 11, glance) if glance else fr
    return _paint(fr, ROLL_S, 14, 10)


def seated_e(glance=0):
    fr = [BL] * 3 + E[1:10] + [E[10], E[11], E[12], E[13], E[14]] + SEATED_LOW_E
    fr = _shift(fr, 3, 11, glance) if glance else fr
    return _paint(fr, CROUCH_ROLL_E, 16, 5)


def seated_w(glance=0):
    fr = [BL] * 3 + W[1:10] + [W[10], W[11], W[12], W[13], W[14]] + _flip(SEATED_LOW_E)
    fr = _shift(fr, 3, 11, glance) if glance else fr
    return _paint(fr, _flip(CROUCH_ROLL_E), 16, 4)


def breathe(fr):
    """The rest breath of a seated figure: head and shoulders (rows 3-13) settle 1 px; hips and legs stay."""
    out = list(fr)
    for y in range(13, 2, -1):
        out[y] = fr[y - 1]
    out[2] = BL
    return out


# ---- the stool: one cell (16x16 px, footprint 1x1, collision 1), steel frame and dark canvas from the ink ramp ----
# Rows 0-5 of the cell are empty; the seat top is rows 6-8, the front rail row 9, the legs rows 10-14, and the baked
# contact shadow is row 15 (rect [1, 15, 14, 1]). Keys come from PAL (g h j o), so it adds no hex.
STOOL = [BL] * 6 + [
    "ojjjjjjjjjjjjjjo",
    "ojhhhhhhhhhhhhjo",
    "ohhhhhhhhhhhhhho",
    "oggggggggggggggo",
    ".ojh........hjo.",
    ".ojh........hjo.",
    "ojjh........hjjo",
    "ojh..........hjo",
    "ojjh........hjjo",
    ".hggggggggggggh.",
]
STOOL_ENTRY = {
    # kit convention: content sits at the rect's top-left, so the 16x10 art (cell rows 6-15) starts at the rect's top
    # and the 1x1 footprint's top-left is 6 px above it (origin_px y = -6); the anchor is the footprint's bottom centre
    "name": "stool_folding", "kind": "prop", "size_px": [16, 10],
    "footprint": {"cells": [1, 1], "origin_px": [0, -6]}, "collision": ["1"],
    "layer": "rear_prop", "y_sort": True, "anchor": [8, 10], "composite": {"mode": "over"},
    "contact_shadow": [1, 9, 14, 1], "tags": ["seating", "hal"],
}
# Where the stool sits in a seated Hal frame: the stool cell's top-left, so anchors (8, 24) and (8, 16) coincide.
STOOL_CELL_IN_FRAME = [0, 8]


# ---- false_panel_pull (one-shot): reach, grip and pull the hatch down, then step back to rest ---------------------
GLOVE_L, GLOVE_R = ["jjh", "hhg"], ["jhh", "hgg"]


def _erase_belt_gloves_sn(fr):
    for y in (14, 15):
        r = list(fr[y])
        r[1:4], r[4] = ["."] * 3, "o"
        r[11], r[12:15] = "o", ["."] * 3
        fr = fr[:y] + ["".join(r)] + fr[y + 1:]
    return fr


def _arms_sn(base, level):
    """level 'up': gloves at shoulder height beside the head (rows 10-11); 'mid': rows 12-13; 'low': the base."""
    if level == "low":
        return base
    fr = _erase_belt_gloves_sn(base)
    y = 10 if level == "up" else 12
    fr = _paint(fr, GLOVE_L, y, 1)
    fr = _paint(fr, GLOVE_R, y, 12)
    if level == "up":
        fr = _paint(fr, ["ooo"], 9, 1)
        fr = _paint(fr, ["ooo"], 9, 12)
    return fr


BELT_E = {"e": ["...osrrrrrqqo...", "...osrrrrrqqo...", "...osrrqqqqqo..."],
          "w": ["...osrrrrrrqo...", "...osrrrrrrqo...", "...osrrrrrrqo..."]}


def _arm_ew(f, level):
    """E/W: the arm reaches forward at shoulder height ('up'), grips lower ('mid') or hangs at the belt ('low')."""
    base = BASE[f]
    if level == "low":
        return base
    fr = base[:13] + BELT_E[f] + base[16:]
    reach = {"e": (E_REACH2, E_REACH1), "w": (W_REACH2, W_REACH1)}[f][0 if level == "up" else 1]
    y_shift = -2 if level == "up" else -1       # the reach stamps sit on rows 13-15
    return stamps(fr, *[(x, y + y_shift, art) for x, y, art in reach])


def pull(f):
    g = {"s": lambda lv: _arms_sn(S, lv), "n": lambda lv: _arms_sn(N, lv),
         "e": lambda lv: _arm_ew("e", lv), "w": lambda lv: _arm_ew("w", lv)}[f]
    return [fin(f, g("up")), fin(f, g("mid"), True), fin(f, dip(g("low")), True), fin(f, BASE[f])]


def _extra_poses():
    crouch = {
        "s": [crouch_s(True), crouch_s(False), crouch_s(True, -1), crouch_s(False)],
        "e": [crouch_e(True), crouch_e(False), crouch_e(True), crouch_e(False)],
        "w": [crouch_w(True), crouch_w(False), crouch_w(True), crouch_w(False)],
        "n": [crouch_n(True), crouch_n(False), crouch_n(True), crouch_n(False)],
    }
    seated = {f: [fr, breathe(fr)] for f, fr in (("s", seated_s()), ("e", seated_e()), ("w", seated_w()))}
    return {"crouch_repair": crouch, "seated_stool": seated, "false_panel_pull": {f: pull(f) for f in "snew"}}


EXTRA = _extra()
EXTRA.update(_extra_poses())
EXTRA_MS = {"interact": 250, "react_puzzled": 300, "react_anxious": 300,
            "crouch_repair": 220, "seated_stool": 600, "false_panel_pull": 260}
EXTRA_MODE = {"crouch_repair": "loop", "seated_stool": "loop", "false_panel_pull": "once"}
EXTRA_ASYMMETRIC = {"interact", "react_puzzled"}
EXTRA_META = {
    "crouch_repair": {"note": "default working pose at machines; loop; the tool taps the panel in front of the facing"},
    "seated_stool": {
        "prop": "stool_folding", "prop_atlas": "hal-props-atlas.json",
        "stool_cell_in_frame_px": STOOL_CELL_IN_FRAME, "stool_sprite_in_frame_px": [0, 14],
        "note": "draw the stool (rear_prop) first, then this frame (actor) with the two anchors coinciding: the "
                "stool cell's top-left sits at (0, 8) inside the 16x24 frame, so its 16x10 sprite starts at (0, 14). "
                "Feet rest on row 23; the seat is under rows 14-17 (hips on row 17)",
    },
    "false_panel_pull": {"note": "one-shot, holds the last frame (standing rest); N is the facing for the machine's "
                                 "south-facing panel; swap the panel prop closed to open on frame 2"},
}
