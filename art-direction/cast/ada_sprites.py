"""Ada (night caretaker) frames, hand-placed at 16x24 logical px.

Status: Candidate, pending director review. Built on the approved person rules (Gate 1 spec) and the
cast frame rule (IVO_SPEC.md). Spec and the lantern rim-light ruling: ADA_SPEC.md.

Frames are written as raw grids (coat, head, boots) plus one small overlay per facing for the hand and
lantern. finish() paints the overlay after any 1 px settle, so the lantern never changes shape.
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "gate1"))
sys.path.insert(0, os.path.join(HERE, "..", "palettes"))
import engineer_sprites as eng  # noqa: E402  (shared leg poses and lower())
from district_palettes import CAST_RAMPS, DISTRICTS  # noqa: E402

_HAIR, _SKIN = CAST_RAMPS["ada"]["hair"], CAST_RAMPS["ada"]["skin"]
_LAMP = DISTRICTS["nightshift"]["accent"]      # warm pools of light: #7A4A4A #B8745A #E8A55F #F9D79A
_WOOD = DISTRICTS["nightshift"]["wood"]        # dim desk wood: used for Ada's boots

PAL = {
    ".": None,
    "o": "#202337",
    # hair, warm white (CAST_RAMPS): fill D C B, A only on contour
    "A": _HAIR[0], "B": _HAIR[1], "C": _HAIR[2], "D": _HAIR[3],
    # skin, deep warm brown (CAST_RAMPS): fill n m l, k only on contour / forehead shadow
    "k": _SKIN[0], "l": _SKIN[1], "m": _SKIN[2], "n": _SKIN[3],
    # long coat (moss olive, hue 80-90, never teal): fill s r q, p on inner shadow lines and the hem band
    "p": "#3C482B", "q": "#87A05E", "r": "#A7BC7B", "s": "#C9D69F",
    # trousers (warm charcoal)
    "O": "#3A3636", "P": "#5C5654",
    # boots (Night Shift wood ramp)
    "S": _WOOD[1], "T": _WOOD[2], "U": _WOOD[3],
    # lantern housing (ink ramp): dark frame, mid frame, lit lip
    "u": "#343650", "v": "#535971", "w": "#777A8C",
    # lantern light (Night Shift lamp ramp, steps 2 and 3): glow, core. Never the gold marker, never violet.
    "f": _LAMP[2], "g": _LAMP[3],
    # baked rim light on the contour beside the lantern (same hex as the renderer rim, step 3)
    "R": _LAMP[3],
}

SLOTS = {"hair": "ABCD", "skin": "klmn", "jacket": "pqrs", "trousers": "OP"}

HAIR_SKIN_SEPARATED = True   # warm-white hair against deep skin: a k, A or o pixel always sits between them
GLINT_LIMITS = {"g": 2, "R": 6}   # lantern core: 2 px at most; baked rim: 6 px at most

BAKED_RIM = True   # the ruling, ADA_SPEC.md decision 1: lantern-side contour pixels are baked as R

# Raw grids: head, long coat and boots at rest, without the hand and lantern (finish() paints them).
# Coat: 12 px shoulders, a belt on row 13, a straight fall to row 17, a flared hem on rows 18-19.
S = [
    "................",
    "....oo..oo..o...",
    "...oDDooDCooCo..",
    "..oDDCBBCDCCBo..",
    "..oCDCCBBCBBBo..",
    "...oBBAABABAo...",
    "...okknnknknno..",
    "...oknonnonnko..",
    "...oknnmmnnnko..",
    "....okmmmmko....",
    "..osssqllqrqqo..",
    "..osrprpqrprqo..",
    "..osrprpqrpqqo..",
    "..osrppwpppqqo..",
    "..onmqpqrqqqqo..",
    "..omlqpqrqqqqo..",
    "..oqrqqpqqqqqo..",
    "..oqqqqpqqqqqo..",
    ".oqrrqqpqqqqqpo.",
    ".oppppppppppppo.",
    "....oOPPoPPOo...",
    "...oTUUToTUUTo..",
    "...oSTTSoSTTSo..",
    "....oooo.oooo...",
]

N = [
    "................",
    "....oo..oo..o...",
    "...oDDooDCooCo..",
    "..oDDCBBCDCCBo..",
    "..oCDCCBBCBBBo..",
    "...oBCCBBCBBBo..",
    "...oBBCBBBBBBo..",
    "...okBBBBBBko...",
    "...okkAAAAkko...",
    "....okllllko....",
    "..osssqqqqrqqo..",
    "..osrprpqrprqo..",
    "..osrprpqrpqqo..",
    "..osrpppppppqo..",
    "..oqrqpqrqqnmo..",
    "..oqqqpqrqqmlo..",
    "..oqrqqpqqqqqo..",
    "..oqqqqpqqqqqo..",
    ".oqrrqqppqqqqpo.",
    ".opppppoopppppo.",
    "....oOPPoPPOo...",
    "...oSTTSoSTTSo..",
    "...oSSSSoSSSSo..",
    "....oooo.oooo...",
]

E = [
    "................",
    "....oo..oo......",
    "...oDDooDCoo....",
    "..oDDCBBCCCBo...",
    "..oCDCCBBCBBBo..",
    "...oBBBBAAABo...",
    "...oBBAknnnko...",
    "...oBBAknnono...",
    "...oBBAkmmnno...",
    "....oAklmmko....",
    "...ossrrqqrqo...",
    "..ossrrrrqpqqo..",
    "..osrrrrqqpqqo..",
    "..opppppppppqo..",
    "..orrrqqqqpqqo..",
    "..orrqqqqqpqqo..",
    "..oqrqqqqqpqqo..",
    "..oqqqqqqqpqqo..",
    ".oqrrqqqqqqqqpo.",
    ".oppppppppppppo.",
    "....oOPPoPPo....",
    "...oTUToTUUTo...",
    "...oSTSoSTTTSo..",
    "....ooo.ooooo...",
]

W = [
    "................",
    "....oo..oo......",
    "...oDDooDCoo....",
    "..oDDCBBCCCBo...",
    "..oCDCCBBCBBBo..",
    "...oBAAABBBBo...",
    "...oknnnkABBo...",
    "...ononnkABBo...",
    "...onnmmkABBo...",
    "....okmmlkAo....",
    "...ossrrqqrqo...",
    "..osspqrrrrqqo..",
    "..osrpqrrrrqqo..",
    "..oppppppppqqo..",
    "..orrpqrrqqqqo..",
    "..orrpqrqqqqqo..",
    "..oqrpqqqqqqqo..",
    "..oqqpqqqqqqqo..",
    ".oqrrqqqqqqqqpo.",
    ".oppppppppppppo.",
    "....oPPoPPOo....",
    "...oTUUToTUTo...",
    "..oSTTTSoSTSo...",
    "...ooooo.ooo....",
]

# Hem rows 18-19 (the coat's lower edge) by facing; walks repaint them over the shared leg poses.
HEM = {"s": (S[18], S[19]), "n": (N[18], N[19]), "e": (E[18], E[19]), "w": (W[18], W[19])}

# --- The lantern (Ada's left hand): housing first, then a 2-step hard glow ---------------------------
# Front view (S, E, W): a ring the hand grips, a lit cap, glass (core g, glow f) inside a dark frame, a base.
LANT_FRONT = [
    ".uuu.",
    "uwwvu",
    "uggfu",
    "ufffu",
    "ufffu",
    "uvvvu",
]
# Seen from behind (N): the same housing, its glass facing away; only a 1 px edge of glow leaks past the frame.
LANT_BACK = [
    ".uuu.",
    "uwwvu",
    "ugfvu",
    "uffvu",
    "uffvu",
    "uvvvu",
]
# facing: (hand column, lantern column, art). S and E carry the lantern at screen-right, N and W at screen-left.
LANTERN = {
    "s": (9, 8, LANT_FRONT),
    "n": (4, 3, LANT_BACK),
    "e": (9, 8, LANT_FRONT),
    "w": (4, 3, LANT_FRONT),
}
HAND_ROW, LANT_ROW = 12, 13


def finish(frame, facing, dy=0, baked=None):
    """Paint the hand and lantern over a frame, dy rows lower (the settle). When baked, the contour
    pixels beside the lantern turn into the rim colour (R); see ADA_SPEC.md decision 1."""
    baked = BAKED_RIM if baked is None else baked
    hx, lx, art = LANTERN[facing]
    out = [list(r) for r in frame]
    for y, ch_row in ((HAND_ROW + dy, "nm"), ):
        for i, ch in enumerate(ch_row):
            out[y][hx + i] = ch
    for j, line in enumerate(art):
        for i, ch in enumerate(line):
            if ch != ".":
                out[LANT_ROW + dy + j][lx + i] = ch
    if baked:   # the outermost contour pixel of each row beside the lantern, on the lantern's side
        for y in range(LANT_ROW + dy, LANT_ROW + dy + len(art)):
            cols = [x for x, ch in enumerate(out[y]) if ch == "o"]
            if cols:
                out[y][max(cols) if facing in "se" else min(cols)] = "R"
    return ["".join(r) for r in out]


def sway(facing, k):
    """Hem rows 18-19 for walk frame k: passing frames tuck the hem in 1 px on one side (the coat sways)."""
    r18, r19 = HEM[facing]
    if k % 2 == 0:
        return r18, r19
    mid = r19[3:14]
    # tuck one side of the hem band in by 1 px, keeping it inside columns 1-14
    return r18, (".." + "o" + mid + "o" + ".") if k == 1 else ("." + "o" + mid + "o" + "..")


def walk(base, legs, facing):
    out = []
    for k, lg in enumerate(legs):
        raw = base[0:18] + lg
        raw[18], raw[19] = sway(facing, k)
        if k % 2 == 0:   # contact: the body and the lantern settle 1 px, the hem and boots stay
            out.append(finish(eng.lower(raw), facing, dy=1))
        else:
            out.append(finish(raw, facing))
    return out


SIDE_LEGS = (eng.LEG_C0, eng.LEG_P1, eng.LEG_C2, eng.LEG_P3)
# Idle frame 1 lowers the head and torso by 1 px and keeps the lantern still (ada.md: "lantern still").
IDLE = {f: [finish(fr, f), finish(eng.lower(fr), f)] for f, fr in (("s", S), ("n", N), ("e", E), ("w", W))}
WALK = {
    "s": walk(S, eng.LEGS_S, "s"),
    "n": walk(N, eng.LEGS_N, "n"),
    "e": walk(E, SIDE_LEGS, "e"),
    "w": walk(W, [[r[::-1] for r in lg] for lg in SIDE_LEGS], "w"),
}
