"""Ivo (Orientation reception lead) frames, hand-placed at 16x24 logical px.

Status: APPROVED by the player 2026-10-02. Built on the person rules approved at Gate 1
(art-direction/gate1/GATE1_ENGINEER_SPEC.md): same frame, anchor, timing,
contour-only darkest step, and renderer-drawn shadow. Spec: IVO_SPEC.md.
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "gate1"))
import engineer_sprites as eng  # noqa: E402  (shared walk legs and lower())

PAL = {
    ".": None,
    "o": "#202337",
    # hair, silver: fill D C B, A only on contour
    "A": "#535971", "B": "#8C8F9C", "C": "#BFC0C6", "D": "#E6E4E0",
    # skin: fill n m l, k only on contour
    "k": "#8A5A4A", "l": "#C08870", "m": "#E3B094", "n": "#F6D2B8",
    # cardigan (wood/terracotta): fill s r q, p on contour
    "p": "#523D4C", "q": "#85565A", "r": "#BA785F", "s": "#E4AA73",
    # shirt strip (ochre)
    "x": "#9A6A3E", "y": "#C99A4E", "z": "#EDCB7A",
    # trousers (navy)
    "O": "#2C3352", "P": "#3E4870",
    # shoes (ink ramp)
    "S": "#343650", "T": "#535971", "U": "#777A8C",
    # tablet face: blue glass, never #19AFA2, lightest step on 1 px only; back is ink (S T)
    "g": "#203A50", "h": "#366479", "j": "#5AA3AE", "J": "#A0DDD4",
}

SLOTS = {"hair": "ABCD", "skin": "klmn", "jacket": "pqrs", "trousers": "OP"}

S = [
    "................",
    "......ooooo.....",
    "....ooCDDCCo....",
    "...oCDDCCBCBo...",
    "...oCCBCCBCBo...",
    "...oBCCBBCBBo...",
    "...oBkkkAkkBo...",
    "...oknommomko...",
    "...oknmmmmmko...",
    "....okllllko....",
    "..osssryzrrqqo..",
    ".osrrrryyrrrqqo.",
    ".psrrrpxygggggo.",
    ".psrrrpxygJjjgo.",
    ".psqrrpxygjhjgo.",
    ".opqqrqqqmggggo.",
    ".omqqqqqqqqqmmo.",
    "..opqqqqqqqqpo..",
    "....oOPPoPPOo...",
    "....oOPPoPPOo...",
    "....oOPPoPPOo...",
    "...oTUUToTUUTo..",
    "...oSTTSoSTTSo..",
    "....oooo.oooo...",
]

N = [
    "................",
    "......ooooo.....",
    "....ooCDDCCo....",
    "...oCDDCCBCBo...",
    "...oCCBCCBCBo...",
    "...oBCCBCBBBo...",
    "...oBBCBBBBBo...",
    "...okBBBBBBko...",
    "...okkAAAAkko...",
    "....okllllko....",
    "..osssrrrrrqqo..",
    ".osrrrrrrrrrqqo.",
    ".psrrrrqrrrqqqo.",
    ".oSSSrrqrrrqqqo.",
    ".oSTSrrqrrqqqqo.",
    ".oSSSqqqqqqqqpo.",
    ".ommqqqqqqqqqmo.",
    "..opqqqqqqqqpo..",
    "....oOPPoPPOo...",
    "....oOPPoPPOo...",
    "....oOPPoPPOo...",
    "...oSTTSoSTTSo..",
    "...oSSSSoSSSSo..",
    "....oooo.oooo...",
]

E = [
    "................",
    ".....ooooo......",
    "....ooCDDCo.....",
    "...oCDDCCBCo....",
    "...oCCBCCBCBo...",
    "...oBCCBBCBAo...",
    "...oBBCBkkkko...",
    "...oBBAkmnomo...",
    "...oBAkmmmmmo...",
    "....oAklmmko....",
    "...ossrrryzqo...",
    "..osrrrrrxyqqo..",
    "..psrrrrrxggggg.",
    "..psrqrrrxgJjjg.",
    "..osqqrrrqgjhjg.",
    "..opqqmmqqmgggg.",
    "...opqlmqqqpo...",
    "...opqqqqqqpo...",
    "....oOPPPPOo....",
    "....oOPPoPPo....",
    "....oOPPoPPo....",
    "...oTUToTUUTo...",
    "...oSTSoSTTTSo..",
    "....ooo.ooooo...",
]

W = [
    "................",
    "......ooooo.....",
    ".....oCDDCoo....",
    "....oCDDCCBCo...",
    "...oCDCCBCCBo...",
    "...oACBCCBBBo...",
    "...okkkkBCBBo...",
    "...omonkABBBo...",
    "...ommmmkABBo...",
    "....okmmlkAo....",
    "...oyzsrrrrqo...",
    "..oxysrrrrrqqo..",
    ".gggggrrrrrqqo..",
    ".gJjjgrrqrrqqo..",
    ".gjhjgrrqrqqpo..",
    ".ggggmqqqqqqpo..",
    "...oqqqqqqqpo...",
    "...opqqqqqqpo...",
    "....oOPPPPOo....",
    "....oPPoPPOo....",
    "....oPPoPPOo....",
    "...oTUUToTUTo...",
    "..oSTTTSoSTSo...",
    "...ooooo.ooo....",
]


def lower(frame):
    """1 px settle that keeps Ivo's hem row (17): the top leg row is dropped instead."""
    return ["." * 16] + frame[0:18] + frame[19:24]


HAIR_SKIN_SEPARATED = True  # silver hair matches skin luminance: never let them touch


def walk(base, legs):
    """Ivo keeps the tablet still, so motion is legs plus the shared 1 px contact bob."""
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
