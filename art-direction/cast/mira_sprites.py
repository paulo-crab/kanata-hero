"""Mira (courier) frames, hand-placed at 16x24 logical px.

Status: APPROVED 2026-10-02. Built on the approved person rules (Gate 1 spec)
and the cast frame rule (IVO_SPEC.md). Spec: MIRA_SPEC.md.
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "gate1"))
import engineer_sprites as eng  # noqa: E402  (shared walk legs)

PAL = {
    ".": None,
    "o": "#202337",
    # hair: fill D C B, A only on contour
    "A": "#1E1A26", "B": "#332833", "C": "#4D3A44", "D": "#6B5058",
    # skin: fill n m l, k only on contour / forehead shadow
    "k": "#3E2630", "l": "#5E3A36", "m": "#85563F", "n": "#A9744F",
    # jacket main panel (ochre): fill y x, z on 1 px only, w on contour
    "w": "#5C4038", "x": "#9A6A3E", "y": "#C99A4E", "z": "#EDCB7A",
    # jacket second panel (garden green), her right side and sleeve
    "E": "#21484A", "F": "#326D60", "G": "#5FA06D", "H": "#B2CE78",
    # strap and bag (coral): her identity colour, used nowhere else on her
    "c": "#71394F", "d": "#B65761", "e": "#E67A70", "f": "#F6B18E",
    # trousers (navy)
    "O": "#2C3352", "P": "#3E4870",
    # shoes (ink ramp)
    "S": "#343650", "T": "#535971", "U": "#777A8C",
}

SLOTS = {"hair": "ABCD", "skin": "klmn", "jacket": "wxyzEFGH", "trousers": "OP"}

# S: puff on her left (screen-right); green panel on her right (screen-left);
# strap from her right shoulder down to the bag at her left hip (screen-right).
S = [
    "..........oooo..",
    "......ooooDDCDo.",
    "....ooCCDDoCDCo.",
    "...oCCDCCCBCBo..",
    "...oCCCCCBBBBo..",
    "...oCBAAABCBo...",
    "...oBnnnnmnBo...",
    "...omnonnonmo...",
    "...omnnnnnnmo...",
    "....ommmmmmo....",
    "...oHeGFyyyxo...",
    "..oGGdeFyyyxxo..",
    "..oGGFdeyyxyxo..",
    "..oGFFFdeyxyxo..",
    "..oFEFFFdexxxo..",
    "..omFFFFxxoeffo.",
    "..olFFFFxxodeeo.",
    "....oOPPOPocddo.",
    "....oOPPoPPoooo.",
    "....oOPPoPPo....",
    "....oOPPoTUTo...",
    "...oTUUToSTSo...",
    "...oSTTSoooo....",
    "....oooo........",
]

# N: puff at screen-left; green panel at screen-right; strap's back runs from
# screen-right shoulder to the bag at screen-left hip.
N = [
    "..ooo...........",
    ".oDDCooooo......",
    ".oCDCoDDCCCBo...",
    "..oBCCDDCCCBo...",
    "...oCDDCCCBBo...",
    "...oCCCBBCBBo...",
    "...oBCCBBBBBo...",
    "...omBBBBBBmo...",
    "...ommBAABmmo...",
    "....ommmmmmo....",
    "...oyyyxGGeFo...",
    "..oyyyxxGedFFo..",
    "..oyyxxxedGFEo..",
    "..oyxxxedFFFEo..",
    "..oxxxedFFFFFo..",
    ".oeffoxxFFFFmo..",
    ".oeedoxxFFFFlo..",
    ".oddcoPPOPPo....",
    "..oooOPPoPPo....",
    "....oOPPoPPo....",
    "...oSTTSoPPo....",
    "...oSSSSoSTSo...",
    "....oooooSSSo...",
    ".........ooo....",
]

# E: head 1 px ahead of the body (the lean); green near flank and sleeve;
# strap from the near shoulder back to the bag on the far hip, showing behind.
E = [
    "..ooo...........",
    ".oDDCoooooo.....",
    ".oCDCoCDDCCo....",
    "..oBCCCDCCCCo...",
    "...oCCCCCBBCo...",
    "...oBCCCBBAAo...",
    "...oBBCBmnnno...",
    "...oBBBmnnono...",
    "...oBBmnnnnmo...",
    "....oAmmmmmo....",
    "...oHGGGeyyo....",
    "..oGGGGedyyxo...",
    "..oGGGedFFyxo...",
    "..oGGedGFFyxo...",
    ".oceedGGFFxwo...",
    ".oddoFFFmmFxo...",
    ".occoFFFlmFwo...",
    "..ooooOPPPPo....",
    "....oOPPoPPo....",
    "....oOPPoPPo....",
    "...oTUToOPPo....",
    "...oSTSooTUUTo..",
    "....ooo.oSTTTSo.",
    ".........oooooo.",
]

# W: head 1 px ahead (left); ochre near flank; bag on the near hip, forward of
# the body edge; strap from the far shoulder down across the chest to the bag.
W = [
    ".........oooo...",
    "......ooooDDCo..",
    "....ooDDCCoDCo..",
    "...oDDCCCCCCBo..",
    "..oDCCCCCBBBo...",
    "..oAACCCBBBBo...",
    "..onnnmBCBBBo...",
    "..ononmBBBBBo...",
    "..onnnnnmBAo....",
    "...omnnmmAo.....",
    "....ozyyyeFGo...",
    "...oyyyyedxFEo..",
    "...oyyyedxxxwo..",
    "...oyyedxxxxwo..",
    "..oeeffoxxxwo...",
    "..odeeeomxxwo...",
    "..ocdddolxxwo...",
    "...ooooPPPPOo...",
    "....oOPPPPOo....",
    "....oPPoPPOo....",
    "....oPPoTUTo....",
    "..oTUUToSTSo....",
    ".oSTTTSoooo.....",
    ".oooooo.........",
]

# The bag is drawn once per facing and painted onto every frame: a dark flap
# line, a buckle, a #B65761 body (never the marker coral), a lit lip.
BAG_FRONT = ["ofeeeo", "occcco", "oddUdo", "odddco", ".oooo."]
BAG_BACK = ["oeeedo", "oddddo", "oddddo", "occcco", ".oooo."]
BAG_SIDE = ["ofeeo", "occco", "odUdo", "oddco", ".ooo."]   # far hip, behind the body
# facing: (top row, rest column, swing dx on passing frames, art)
BAGS = {
    "s": (15, 9, -1, BAG_FRONT),   # her left hip, screen-right; swings in toward her
    "n": (15, 1, 1, BAG_BACK),     # her left hip from behind, screen-left
    "e": (14, 1, -1, BAG_SIDE),    # far hip, trailing behind her back
    "w": (14, 2, -1, BAG_FRONT),   # near hip, forward of the body edge
}
GLINT_LIMITS = {"z": 1, "H": 1, "f": 1}  # enforced by check_gate1.py


def lower(frame):
    """1 px settle: head and torso down, dropping the top leg row. The bag is
    painted afterwards at the same 1 px offset, so it never changes shape."""
    return ["." * 16] + frame[0:18] + frame[19:24]


def finish(frame, facing, dy=0, swing=False):
    """Panel fills step down away from the lit shoulder, the strap shadow is the
    coral contour step, and the bag is painted on top (offset by dy, swung by 1 px)."""
    out = []
    for y, row in enumerate(frame):
        if 12 + dy <= y <= 17 + dy:
            row = row.replace("y", "x").replace("G", "F")
        if 10 + dy <= y <= 17 + dy:
            row = row.replace("d", "c")
        out.append(row)
    r0, c0, dx, bag = BAGS[facing]
    c0 += dx if swing else 0
    for i, line in enumerate(bag):
        row = list(out[r0 + dy + i])
        for j, ch in enumerate(line):
            if ch != ".":
                row[c0 + j] = ch
        out[r0 + dy + i] = "".join(row)
    return out


# Mira's energy in the side walk comes from the trailing heel lifting off; the
# stride stays inside the approved Gate 1 overhead limit (columns 2-14).
STRIDE_C0 = [
    "....oOPPoPPPo...",
    "...oOPPo.oPPo...",
    "..oSTTo..oPPPo..",
    "..oSSo...oTUUTo.",
    "..oo.....oSTTTo.",
    ".........oooooo.",
]
STRIDE_C2 = [
    "....oPPPoOOOo...",
    "...oPPPo.oOOo...",
    "..oTUUo..oOOOo..",
    "..oTTo...oSTTSo.",
    "..oo.....oSSSTo.",
    ".........oooooo.",
]
SIDE = (STRIDE_C0, eng.LEG_P1, STRIDE_C2, eng.LEG_P3)


def walk(base, legs, facing):
    out = []
    for i, lg in enumerate(legs):
        raw = base[0:18] + lg
        if i % 2 == 0:   # contact: 1 px lower
            out.append(finish(lower(raw), facing, dy=1))
        else:            # passing: the bag swings 1 px
            out.append(finish(raw, facing, swing=True))
    return out


IDLE = {f: [finish(g, f), finish(lower(g), f, dy=1)] for f, g in (("s", S), ("n", N), ("e", E), ("w", W))}
WALK = {
    "s": walk(S, eng.LEGS_S, "s"),
    "n": walk(N, eng.LEGS_N, "n"),
    "e": walk(E, SIDE, "e"),
    "w": walk(W, [[r[::-1] for r in lg] for lg in SIDE], "w"),
}
