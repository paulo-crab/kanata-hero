"""Engineer portrait, chibi direction C. Spec: PORTRAITS_SPEC.md, persona: PORTRAIT_PERSONAS.md.

Status: Candidate, pending director review. The Engineer is the baseline of the cast: the standard
round head, the standard round dot eyes and the standard mouths. Every other character deviates from
this set. Personal tic: the left brow rides one pixel higher than the right (observant).
Every key is a key of engineer_sprites.PAL (hair ABCD, skin klmn, jacket pqrs, collar wxy, badge bcd).
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import chibi  # noqa: E402
import engineer_sprites as spr  # noqa: E402
from chibi import R, head_spans, rle_hair  # noqa: E402

SPRITE = spr
PAL = dict(spr.PAL)
SLOTS = spr.SLOTS
EXTRA = {"y": {"hex": spr.PAL["y"], "use": "eye glint (the collar's lightest step)"}}
SKIN = {"1": "n", "2": "m", "4": "U", "5": "y", "6": "T"}   # fill, shade, blush (terracotta), glint, mouth inside
BROW = "B"
SIGNATURES = ()
PROP_KEYS = "bcd"                                  # keys that identify the costume and prop at a glance
TAGLINE = "The baseline: standard round head, standard dot eyes. Left brow rides a pixel high (observant)."

HEAD = head_spans(3, [9, 13, 15, 16] + [18] * 22 + [17, 17, 16, 15, 13, 11, 8, 6])
BODY = {38: (17, 30), 39: (13, 34), 40: (10, 37)}
BODY.update({r: (8, 39) for r in range(41, 48)})


def cloth(r, c, a, b, spans):
    t = min(spans)
    k = "r"
    if c <= a + 3:
        k = "s"
    elif c >= b - 3:
        k = "q"
    d = abs(c - 23.5)
    if r - t <= 3 and d <= 5 - (r - t):          # cream collar V
        k = "y" if c < 24 else "x"
        if d > 4 - (r - t):
            k = "w"
    return k


PROPS = [(43, 29, ["bbb", "bdb", "bcb"])]           # the brass badge on its lanyard

HAIR = rle_hair(4, 40, 2, [
    ".12 D3 C5 B1 .19",                 # r2
    ".8 D5 C16 B3 .8",                  # r3
    ".5 D6 C21 B4 .4",                  # r4
    ".3 C3 D7 C20 B5 .2",               # r5   one highlight band
    ".2 C4 D8 C20 B4 .2",               # r6
    ".2 C9 D7 C17 B3 .2",               # r7
    ".2 C14 D6 C13 B3 .2",              # r8
    ".2 C32 B4 .2",                     # r9
    ".2 C32 B4 .2",                     # r10
    ".2 C32 B4 .2",                     # r11
    ".2 C32 B4 .2",                     # r12
    ".2 C32 B4 .2",                     # r13
    ".2 C6 .12 C14 B4 .2",              # r14  short left temple, long swept fringe at right
    ".2 C5 .13 C13 B5 .2",              # r15
    ".2 C4 .14 C5 .3 C6 B4 .2",         # r16
    ".2 C4 .16 C3 .4 C5 B4 .2",         # r17
    ".2 C3 .24 C4 B3 .4",               # r18
    ".2 B2 .27 C3 B2 .4",               # r19
    ".36 B2 .2",                        # r20
])

_EYE = [".oo.", "o5oo", "oooo", ".oo."]            # the standard round dot with a glint
_EYES = [(22, 14, _EYE), (22, 30, _EYE)]
_BLUSH = [(27, 9, ["4444", "4444"]), (27, 35, ["4444", "4444"])]

FACE = {
    "neutral": _EYES + _BLUSH + [
        (18, 14, ["===="]), (19, 30, ["===="]),                       # level brows, the left one a pixel high
        (28, 20, ["o"]), (28, 27, ["o"]), (29, 21, ["oooooo"]),        # a wide, gentle smile
    ],
    "concerned": _EYES + _BLUSH + [
        (20, 14, ["="]), (19, 15, ["=="]), (18, 17, ["="]),            # brows tilted up in the middle
        (18, 30, ["="]), (19, 31, ["=="]), (20, 33, ["="]),
        (29, 22, [".oo.", "o66o", ".oo."]),                            # a small worried "o"
    ],
    "pleased": _BLUSH + [
        (23, 14, [".oo.", "o..o"]), (23, 30, [".oo.", "o..o"]),                 # closed, smiling eyes (thick arcs)
        (19, 14, ["="]), (18, 15, ["=="]), (19, 17, ["="]),
        (19, 30, ["="]), (18, 31, ["=="]), (19, 33, ["="]),
        (28, 20, ["oooooooo", "o666666o", ".oooooo."]),                # big open smile
    ],
}

EXPRESSIONS = chibi.build(sys.modules[__name__])
