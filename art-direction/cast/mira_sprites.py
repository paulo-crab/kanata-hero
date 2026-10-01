"""Mira (courier) frames, hand-placed at 16x24 logical px.

Status: REVIEW_REQUIRED. Built on the approved person rules (Gate 1 spec)
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
    "..........ooo...",
    "......oooooDDo..",
    "....ooCCDDoCDo..",
    "...oCCDCCCBCBo..",
    "...oCCCCCBBBBo..",
    "...oCBAAAAABo...",
    "...oBnnnnmnBo...",
    "...omnonnonmo...",
    "...omnnnnnnmo...",
    "....ommmmmmo....",
    "...oHeGFyyyxo...",
    "..oHGdeFyyxyxo..",
    "..oGGFdeyyxyxo..",
    "..oGFFFdeyxyxo..",
    "..oFEFFFdexwxo..",
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
    "...ooo..........",
    "..oDDooooo......",
    "..oDCoDDCCCBo...",
    "..oBCCCCCCCBo...",
    "...oCCCCCCBBo...",
    "...oCCCCBBBBo...",
    "...oBCCBBBBBo...",
    "...omBBBBBBmo...",
    "...omBAAAABmo...",
    "....ommmmmmo....",
    "...oyyyxGGeFo...",
    "..oyyyxxGedFFo..",
    "..oyyxxxedGFEo..",
    "..oyxxxedFFFEo..",
    "..oxwxedFFFFFo..",
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
    "...ooo..........",
    "..oDDoooooo.....",
    "..oCDoCDDCCo....",
    "..oBCCCDCCCCo...",
    "...oCCCCCBBCo...",
    "...oBCCCBBAAo...",
    "...oBBCBmnnno...",
    "...oBBBmnnono...",
    "...oBBmnnnnmo...",
    "....oAmmmmmo....",
    "...oHGGGeyyo....",
    "..oHGGGedyyxo...",
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
    "..........ooo...",
    "......ooooooDo..",
    "....ooDDCCCoDo..",
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
BAGS = {
    "s": (15, 10, BAG_FRONT),   # her left hip, screen-right
    "n": (15, 0, BAG_BACK),     # her left hip seen from behind, screen-left
    "w": (14, 2, BAG_FRONT),    # near hip, forward of the body edge
}  # "e": the bag is on the far hip, drawn behind the body in the grid


def finish(frame, facing):
    """Panel fills step down away from the lit shoulder, the strap shadow is the
    coral contour step, and the bag is painted on top."""
    out = []
    for y, row in enumerate(frame):
        if 12 <= y <= 17:
            row = row.replace("y", "x").replace("G", "F")
        if 10 <= y <= 17:
            row = row.replace("d", "c")
        out.append(row)
    if facing in BAGS:
        r0, c0, bag = BAGS[facing]
        for i, line in enumerate(bag):
            row = list(out[r0 + i])
            for j, ch in enumerate(line):
                if ch != ".":
                    row[c0 + j] = ch
            out[r0 + i] = "".join(row)
    return out


# Longer side-view stride than the shared poses (feet one column further apart).
STRIDE_C0 = [
    "....oOPPoPPPo...",
    "..oOPPo..oPPPo..",
    "..oOPo....oPPPo.",
    ".oSTTo....oTUUTo",
    ".oSSo.....oSTTTo",
    ".oo.......oooooo",
]
STRIDE_C2 = [
    "....oPPPoOOOo...",
    "..oPPPo..oOOOo..",
    "..oPPo....oOOOo.",
    ".oTUUo....oSTTSo",
    ".oTTo.....oSSSTo",
    ".oo.......oooooo",
]
SIDE = (STRIDE_C0, eng.LEG_P1, STRIDE_C2, eng.LEG_P3)


def lower_front(frame):
    """S/N settle: head and torso down 1 px, dropping row 17 (legs keep the bag's base row)."""
    return ["." * 16] + frame[0:17] + frame[18:24]


def lower_side(frame):
    """E/W settle: keep row 17 (the bag's base), drop the top leg row instead."""
    return ["." * 16] + frame[0:18] + frame[19:24]


def walk(base, legs, lower, facing):
    out = []
    for i, lg in enumerate(legs):
        fr = finish(base[0:18] + lg, facing)
        out.append(lower(fr) if i % 2 == 0 else fr)
    return out


IDLE = {
    "s": [finish(S, "s"), lower_front(finish(S, "s"))],
    "n": [finish(N, "n"), lower_front(finish(N, "n"))],
    "e": [finish(E, "e"), lower_side(finish(E, "e"))],
    "w": [finish(W, "w"), lower_side(finish(W, "w"))],
}
WALK = {
    "s": walk(S, eng.LEGS_S, lower_front, "s"),
    "n": walk(N, eng.LEGS_N, lower_front, "n"),
    "e": walk(E, SIDE, lower_side, "e"),
    "w": walk(W, [[r[::-1] for r in lg] for lg in SIDE], lower_side, "w"),
}
