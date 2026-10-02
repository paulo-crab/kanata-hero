"""Ada portrait, chibi direction C. Spec: PORTRAITS_SPEC.md, persona: PORTRAIT_PERSONAS.md.

Status: Candidate, pending director review. A soft round head under a warm-white cloud of hair (three
scalloped crown bumps with ink notches), the moss coat with a skin V neck, and the lantern at the
lower right. Persona: direct, kind, calm. Heavy shaded upper lids over a steady gaze, low even brows,
a straight serene mouth that only smiles when she is pleased. No signature expression beyond the three
standard ones (the docs name none).
Every key is a key of ada_sprites.PAL (hair ABCD, skin klmn, coat pqrs, lantern fguvw).
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import chibi  # noqa: E402
import ada_sprites as spr  # noqa: E402
from chibi import head_spans, rle_hair  # noqa: E402

SPRITE = spr
PAL = dict(spr.PAL)
SLOTS = spr.SLOTS
EXTRA = {"D": {"hex": spr.PAL["D"], "use": "eye glint (the hair's lightest step)"}}
SKIN = {"1": "n", "2": "m", "4": "T", "5": "D", "6": "S"}   # fill, shade, blush (the warm shoe step), glint, mouth inside
BROW = "B"
SIGNATURES = ()
PROP_KEYS = "fgu"                                  # keys that identify the costume and prop at a glance
TAGLINE = "Calm: heavy shaded lids, low even brows, a straight serene mouth; only smiles when pleased."

HEAD = head_spans(3, [9, 13, 15, 16] + [17] * 22 + [17, 16, 15, 14, 12, 10, 8, 6])
BODY = {38: (17, 30), 39: (13, 34), 40: (10, 37)}
BODY.update({r: (8, 39) for r in range(41, 48)})


def cloth(r, c, a, b, spans):
    d = abs(c - 23.5)
    v = 3.5 - (r - 38)
    if r <= 41 and d <= v - 1:                      # a V neck of skin, edged with the coat's dark step
        return "m"
    if r <= 41 and d <= v:
        return "p"
    k = "r"
    if c <= a + 3:
        k = "s"
    elif c >= b - 3:
        k = "q"
    if r >= 42 and c in (23, 24):                   # placket
        k = "q"
    if r >= 42 and c in (23 - (r - 41), 24 + (r - 41)):    # two lapel creases
        k = "q"
    if r in (44, 46) and c == 23:                   # buttons
        k = "w"
    return k


# The lantern's top at the lower right: a lit cap, a glass of glow and core, an ink frame.
PROPS = [
    (41, 31, ["..uuuu..", ".uwwwwu.", ".uffffu.", ".ufgggu.", ".uffgfu.", ".uffffu.", "..uvvu.."]),
]

HAIR = rle_hair(4, 40, 2, [
    ".8 D1 C1 B1 .6 D2 C3 B1 .4 D1 C1 B1 .10",             # r2   three scalloped crown bumps
    ".5 D3 C4 B2 o2 D2 C4 B2 o2 D2 C3 B1 .8",              # r3   ink notches between them
    ".5 D4 C5 B2 o1 D3 C4 B2 o1 D3 C4 B1 .5",              # r4
    ".3 D5 C7 B2 D4 C7 B2 C4 B3 .3",                       # r5
    ".2 D5 C8 B2 D5 C8 B2 C3 B3 .2",                       # r6
    ".2 C14 B1 C10 B1 C8 B2 .2",                           # r7   strand lines where the clusters meet
    ".2 C13 B1 C10 B1 C9 B2 .2",                           # r8
    ".2 C12 B2 C10 B2 C8 B2 .2",                           # r9
    ".2 C12 B1 C11 B1 C9 B2 .2",                           # r10
    ".2 C34 B2 .2",                                        # r11
    ".2 C34 B2 .2",                                        # r12
    ".2 C34 B2 .2",                                        # r13
    ".2 C8 .1 C8 .2 C9 .1 C5 B2 .2",                       # r14  an uneven fringe
    ".2 C7 .3 C6 .3 C6 .4 C4 B3 .2",                       # r15
    ".2 C5 .6 C5 .3 C3 .8 C3 B2 .3",                       # r16
    ".2 B3 .16 B2 .17",                                    # r17
])

_EYE = ["2222", "o5oo", "oooo", ".oo."]                    # a heavy shaded upper lid over a steady gaze
_BLUSH = [(27, 9, ["444", "444"]), (27, 36, ["444", "444"])]

FACE = {
    "neutral": _BLUSH + [
        (23, 14, _EYE), (23, 30, _EYE),
        (20, 13, ["====="]), (20, 30, ["====="]),                # low, even, steady brows
        (29, 21, ["oooooo"]), (30, 23, ["oo"]),                  # a straight, serene mouth with a small lower lip
    ],
    "concerned": _BLUSH + [
        (22, 14, [".oo.", "o5oo", "oooo", ".oo."]), (22, 30, [".oo.", "o5oo", "oooo", ".oo."]),   # the lids lift: she means it
        (19, 13, ["====="]), (20, 13, ["....."]), (19, 30, ["====="]),
        (30, 20, ["oooooooo"]),                                  # a firm level line
    ],
    "pleased": [
        (23, 14, ["o..o", ".oo."]), (23, 30, ["o..o", ".oo."]),  # serene closed eyes (lids resting)
        (20, 13, ["====="]), (20, 30, ["====="]),
        (28, 19, ["o"]), (28, 28, ["o"]), (29, 20, ["oooooooo"]),                # a wide, gentle smile
        (27, 8, ["44444", "44444"]), (27, 35, ["44444", "44444"]),                # warmer cheeks
    ],
}

EXPRESSIONS = chibi.build(sys.modules[__name__])
