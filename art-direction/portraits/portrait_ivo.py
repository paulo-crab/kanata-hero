"""Ivo portrait, chibi direction C. Spec: PORTRAITS_SPEC.md, persona: PORTRAIT_PERSONAS.md.

Status: Approved by the player 2026-10-02. Softer, older head (a wide, rounded jaw), silver hair in
clusters with side tufts, the broadest shoulders in the cast, the tablet corner at the lower right.
Persona: precise and polite, scripted, then questioning. Small oval eyes, perfectly level fine brows,
a narrow tidy smile with a laugh line either side. Signature: ivo_laugh (the unscripted laugh).
Every key is a key of ivo_sprites.PAL (hair ABCD, skin klmn, cardigan pqrs, shirt xyz, tablet ghjJ).
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import chibi  # noqa: E402
import ivo_sprites as spr  # noqa: E402
from chibi import head_spans, rle_hair  # noqa: E402

SPRITE = spr
PAL = dict(spr.PAL)
SLOTS = spr.SLOTS
EXTRA = {"D": {"hex": spr.PAL["D"], "use": "eye glint and laugh teeth (the hair's lightest step)"}}
SKIN = {"1": "n", "2": "m", "4": "l", "5": "D", "6": "q"}
BROW = "A"
SIGNATURES = ("ivo_laugh",)
PROP_KEYS = "gj"                                  # keys that identify the costume and prop at a glance
TAGLINE = "Softer, older: small oval eyes, level brows, a narrow tidy smile with laugh lines. Laughs when unscripted."

HEAD = head_spans(3, [9, 13, 15, 16] + [18] * 23 + [18, 18, 17, 16, 14, 11, 8])      # a softer, wider jaw
BODY = {38: (15, 32), 39: (10, 37), 40: (6, 41)}
BODY.update({r: (5, 42) for r in range(41, 48)})


def cloth(r, c, a, b, spans):
    k = "r"
    if c <= a + 3:
        k = "s"
    elif c >= b - 3:
        k = "q"
    if 21 <= c <= 26:                               # ochre shirt strip down the centre
        k = "x" if c in (21, 26) else "y"
        if c == 22 and r == min(spans) + 2:
            k = "z"
    return k


PROPS = [(43, 28, ["gggggggggggg", "gJjjjjjjjjhg", "gjjjjjjjjhhg", "gjjjjjjjhhhg", "gggggggggggg"])]

HAIR = rle_hair(4, 40, 2, [
    ".8 D2 C2 B1 .4 D2 C3 B1 .3 D2 C2 B1 .9",       # r2   three cluster tops
    ".6 D3 C4 B1 o2 D2 C5 B1 o2 D3 C4 B1 .6",       # r3   ink notches between the clusters
    ".4 D3 C5 B2 o1 D3 C5 B2 o1 D3 C5 B2 .4",       # r4
    ".3 D4 C6 B2 D4 C7 B2 D3 C4 B2 .3",             # r5
    ".2 C5 D6 C9 B2 D4 C6 B4 .2",                   # r6
    ".2 C10 D5 C9 B2 C8 B2 .2",                     # r7
    ".1 C12 D3 C10 B2 C8 B3 .1",                    # r8   the side tufts bulge past the head
    ".1 C34 B4 .1",                                 # r9
    ".1 C34 B4 .1",                                 # r10
    ".2 C32 B4 .2",                                 # r11  and step back in
    ".2 C32 B4 .2",                                 # r12
    ".2 C32 B4 .2",                                 # r13
    ".2 C12 .1 C6 .1 C5 .1 C6 B4 .2",               # r14  toothed fringe
    ".2 C6 .5 C4 .3 C6 .3 C5 B4 .2",                # r15
    ".2 C5 .8 C4 .1 C7 .5 C3 B3 .2",                # r16
    ".2 C4 .15 C6 .6 C2 B3 .2",                     # r17  centre forelock
    ".2 C3 .17 C4 .14",                             # r18
    ".2 B2 .19 C2 .15",                             # r19
])

_EYE = [".oo.", "o5oo", ".oo."]                    # a small oval, three rows tall
_EYES = [(23, 14, _EYE), (23, 30, _EYE)]
_BLUSH = [(27, 10, ["444", "444"]), (27, 35, ["444", "444"])]
_LINES = [(29, 19, ["2"]), (29, 28, ["2"])]        # a laugh line either side of the mouth

FACE = {
    "neutral": _EYES + _BLUSH + _LINES + [
        (20, 14, ["===="]), (20, 30, ["===="]),                      # fine brows, level and exactly mirrored
        (29, 21, ["o....o"]), (30, 22, ["oooo"]),                     # a narrow, tidy, scripted smile
    ],
    "concerned": [
        (22, 14, [".oo.", "o5oo", "oooo", ".oo."]), (22, 30, [".oo.", "o5oo", "oooo", ".oo."]),   # the eyes open wide
        (19, 14, ["===="]),                                           # one brow stays level
        (17, 31, ["=="]), (18, 30, ["="]), (18, 33, ["="]),           # the other arches high: "is that so?"
        (29, 22, ["oooo"]), (28, 26, ["o"]),                          # a flat doubtful mouth, one end lifted
    ] + _BLUSH,
    "pleased": _BLUSH + _LINES + [
        (23, 14, [".oo.", "o..o"]), (23, 30, [".oo.", "o..o"]),     # soft closed eyes
        (19, 15, ["=="]), (20, 14, ["="]), (20, 17, ["="]),         # brows relax into small arches
        (19, 31, ["=="]), (20, 33, ["="]), (20, 30, ["="]),
        (28, 19, ["o"]), (28, 28, ["o"]), (29, 20, ["o"]), (29, 27, ["o"]), (30, 21, ["oooooo"]),   # a deep closed smile
    ],
    "ivo_laugh": _BLUSH + [
        (22, 14, [".oo.", "o..o"]), (22, 30, [".oo.", "o..o"]),     # eyes squeezed shut
        (18, 14, ["===="]), (18, 30, ["===="]),                      # brows up
        (27, 19, ["oooooooooo"]),                                     # the whole mouth opens: teeth, then the dark inside
        (28, 19, ["o55555555o"]), (29, 19, ["o66666666o"]),
        (30, 20, ["o666666o"]), (31, 21, [".oooooo."]),
    ],
}

EXPRESSIONS = chibi.build(sys.modules[__name__])
