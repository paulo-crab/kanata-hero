"""Vale (executive liaison) frames, hand-placed at 16x24 logical px.

Status: candidate, pending director review. Built on the person rules approved at Gate 1
(art-direction/gate1/GATE1_ENGINEER_SPEC.md) and the cast frame rule (cast/IVO_SPEC.md).
Spec: VALE_SPEC.md. This is softening state 0 (0 repairs): rigid, square shoulders, arms tight,
feet together. Later states (shoulders drop, arms relax, asymmetric stance) are EXTRA sets.
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "gate1"))
sys.path.insert(0, os.path.join(HERE, "..", "palettes"))
import engineer_sprites as eng  # noqa: E402  (shared walk legs)
import district_palettes as dp  # noqa: E402  (CAST_RAMPS, DISTRICTS)

_R = dp.CAST_RAMPS["vale"]
_X = dp.DISTRICTS["executive"]

PAL = {
    ".": None,
    "o": "#202337",
    # hair, dark graphite (CAST_RAMPS): fill D C B, A only on contour
    **dict(zip("ABCD", _R["hair"])),
    # skin, pale ivory (CAST_RAMPS): fill n m l, k only on contour / forehead shadow
    **dict(zip("klmn", _R["skin"])),
    # suit, desaturated ink navy (22-29 % saturation, against the Executive wall's 38-47 %):
    # fill r q, s only as a 1-px lit edge on the upper-left, p on contour and seams
    "p": "#262B46", "q": "#3C4465", "r": "#566089", "s": "#9AA6C8",
    # shirt (cool white, apart from the warm ivory skin): fill x w, y lit collar tip
    "w": "#A9B0C6", "x": "#DDE2EC", "y": "#F4F2EC",
    # tie (living green, Executive foliage ramp): t shade, u fill, v lit knot on 1 px
    "t": _X["foliage"][0], "u": _X["foliage"][1], "v": _X["foliage"][2],
    # copper badge (Executive accent ramp): b frame, c face, d lit face, e glint on 1 px
    "b": _X["accent"][0], "c": _X["accent"][1], "d": _X["accent"][2], "e": _X["accent"][3],
    # trousers (suit navy, a step darker than the jacket)
    "O": "#2A2F4C", "P": "#3A4162",
    # shoes (walnut, Executive wood ramp)
    "S": _X["wood"][0], "T": _X["wood"][1], "U": _X["wood"][2],
}

SLOTS = {"hair": "ABCD", "skin": "klmn", "jacket": "pqrs", "trousers": "OP"}
GLINT_LIMITS = {"e": 1, "v": 1, "y": 3}  # enforced by check_gate1.py
HAIR_SKIN_SEPARATED = False  # graphite hair is 29 L* darker than the skin: no equal-luminance contact

S = [
    "........oo......",
    ".....oooDDoo....",
    "....oDDDDCCCoo..",
    "...oDDDkCCDCBo..",
    "...oDDkCCBCBBo..",
    "...oCCBBCBBBo...",
    "...okkBAkkkBo...",
    "...oknommomko...",
    "...oknmllmmko...",
    "....oklmmlko....",
    ".osssswxxwrrrro.",
    ".osrprwxywqpqqo.",
    ".osrprxvuwqpqqo.",
    ".orrprputedpqqo.",
    ".orrpqputdcpqqo.",
    ".oxwpqqutbbpwwo.",
    ".onmpqqrpqqpmlo.",
    "..oprqqqpqqqpo..",
    "....oOPPoPPOo...",
    "....oOPPoPPOo...",
    "....oOPPoPPOo...",
    "...oTUUToTUUTo..",
    "...oSTTSoSTTSo..",
    "....oooo.oooo...",
]

N = [
    "......oo........",
    "....ooDDooo.....",
    "..ooDDDDCCCo....",
    "..oDDDBCCDCBo...",
    "..oDDBCCBCBBo...",
    "...oCCBBCBBBo...",
    "...oCBBBBBBBo...",
    "...olBBBBBBlo...",
    "....olBAABlo....",
    "....oklmmlko....",
    ".osssswxxwrrrro.",
    ".osrprqqqqqpqqo.",
    ".osrprqpqqqpqqo.",
    ".osrprqpqqqpqqo.",
    ".osrprqpqqqpqqo.",
    ".oxwprqqqqqpwwo.",
    ".onmprqqqqqpmlo.",
    "..oprrqpqqqqpo..",
    "....oOPPoPPOo...",
    "....oOPPoPPOo...",
    "....oOPPoPPOo...",
    "...oSTTSoSTTSo..",
    "...oSSSSoSSSSo..",
    "....oooo.oooo...",
]

E = [
    "........oo......",
    ".....oooDDoo....",
    "....oDDDDCCCo...",
    "...oDDDCCCCCCo..",
    "...oDCCBCCCBBo..",
    "...oCCBBCBBBBo..",
    "...oBCBBkkkko...",
    "...oBBAkmnomo...",
    "...oBAkmmmllo...",
    "....oAklmmko....",
    "...ossswxxrro...",
    "...osrqqqpyxo...",
    "...osrqqqpvuo...",
    "...orrqqqpudo...",
    "...orqqqqptbo...",
    "...oqxwwwpqqo...",
    "...oqqnmrpqqo...",
    "...opqqqqqqpo...",
    "....oOPPPPOo....",
    "....oOPPoPPo....",
    "....oOPPoPPo....",
    "...oTUToTUUTo...",
    "...oSTSoSTTTSo..",
    "....ooo.ooooo...",
]

W = [
    "......oo........",
    "....ooDDooo.....",
    "...oDDDDCCCo....",
    "..oDDDCCCCCCo...",
    "..oDCCBCCCBBo...",
    "..oCCBBCBBBBo...",
    "...okkkkBCBBo...",
    "...omonmkBBAo...",
    "...ollmmmkBAo...",
    "....okmmlkAo....",
    "...ossxxwrrro...",
    "...oyxprqqqqo...",
    "...ovuprqqqqo...",
    "...oedprqqqqo...",
    "...odcprqqqqo...",
    "...obbpwwwxqo...",
    "...oqqprnmrqo...",
    "...opqqqqqqpo...",
    "....oOPPPPOo....",
    "....oPPoPPOo....",
    "....oPPoPPOo....",
    "...oTUUToTUTo...",
    "..oSTTTSoSTSo...",
    "...ooooo.ooo....",
]


def lower(frame):
    """1 px settle that keeps the jacket hem (row 17): the top leg row is dropped instead
    (eng.lower would drop the hem and bring the hands onto the trousers)."""
    return ["." * 16] + frame[0:18] + frame[19:24]


def walk(base, legs):
    """Rigid walk: neither arm swings. Motion is the legs plus the shared 1 px contact bob."""
    out = []
    for i, lg in enumerate(legs):
        fr = base[0:18] + lg
        out.append(lower(fr) if i % 2 == 0 else fr)
    return out


SIDE_LEGS = (eng.LEG_C0, eng.LEG_P1, eng.LEG_C2, eng.LEG_P3)
IDLE = {f: [fr, lower(fr)] for f, fr in (("s", S), ("n", N), ("e", E), ("w", W))}
WALK = {
    "s": walk(S, eng.LEGS_S),
    "n": walk(N, eng.LEGS_N),
    "e": walk(E, SIDE_LEGS),
    "w": walk(W, [[r[::-1] for r in lg] for lg in SIDE_LEGS]),
}
