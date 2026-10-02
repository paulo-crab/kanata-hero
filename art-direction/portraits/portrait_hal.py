"""Hal portrait, chibi direction C. Spec: PORTRAITS_SPEC.md, persona: PORTRAIT_PERSONAS.md.

Status: Candidate, pending director review. A compact, rounder, broader head (shorter, wider than the
standard), a sandy mop with three outline-capped crown spikes, a stone-sleeved cobalt vest and the
orange tool roll at the lower right. Persona: practical, anxious when the system misbehaves, focused
once a fix is in sight. Brows that slant in (focus), big wide eyes when anxious, a sweat bead,
and a pleased that keeps its eyes open. Signature: hal_puzzled.
Every key is a key of hal_sprites.PAL (hair ABCD, skin klmn, vest pqrs, sleeves wxy, tool roll EFGH).
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import chibi  # noqa: E402
import hal_sprites as spr  # noqa: E402
from chibi import head_spans, rle_hair  # noqa: E402

SPRITE = spr
PAL = dict(spr.PAL)
SLOTS = spr.SLOTS
EXTRA = {"y": {"hex": spr.PAL["y"], "use": "eye glint (the shirt's lightest step)"}}
SKIN = {"1": "n", "2": "m", "4": "U", "5": "y", "6": "S"}   # fill, shade, blush, glint, mouth inside
BROW = "o"
SIGNATURES = ("hal_puzzled",)
PROP_KEYS = "EFG"                                  # keys that identify the costume and prop at a glance
TAGLINE = "Compact and broad: slanted focus brows, wide anxious eyes with a sweat bead, a pleased with open eyes."

HEAD = head_spans(5, [10, 14, 17, 19] + [20] * 19 + [20, 19, 18, 17, 15, 13, 11, 9, 6])    # compact: rows 5-36, up to 40 wide
BODY = {38: (14, 33), 39: (9, 38), 40: (6, 41)}
BODY.update({r: (5, 42) for r in range(41, 48)})


def cloth(r, c, a, b, spans):
    d = abs(c - 23.5)
    v = 4.5 - (r - 38)
    if r <= 41 and d <= v - 1:                      # the stone shirt V at the neck
        return "x" if c < 24 else "y"
    if r <= 41 and d <= v:
        return "w"
    if c <= a + 1 or c >= b - 1:                    # stone sleeves at both edges
        return "x" if r < 44 else "w"
    if c == a + 2 or c == b - 2:
        return "p"
    k = "r"
    if c <= a + 5:
        k = "s"
    elif c >= b - 5:
        k = "q"
    if r >= 42 and c in (23, 24):                   # the zip
        k = "q"
    if 44 <= r <= 46 and 11 <= c <= 17:             # chest pocket on the left
        k = "q"                                     # a darker pocket
        if r == 44:
            k = "s"                                 # with a lit lip
    return k


# The orange tool roll under his left arm: two steel tool tips, a cord band, one glint.
PROPS = [
    (40, 31, ["..j..h..", ".jj..hh."]),
    (42, 31, ["oEEEEEEo", "EFFFFFFE", "EGyyyGGE", "EGGGGGHE", "EFFFFFFE", "EEEEEEEE"]),
]

HAIR = rle_hair(2, 44, 2, [
    ".13 D1 C1 .6 D1 C1 .6 C1 B1 .13",                    # r2   three crown spikes: tips
    ".12 D2 C1 B1 .4 D2 C1 B1 .4 D1 C2 B1 .12",           # r3
    ".11 D3 C2 B1 .2 D3 C2 B1 .2 D2 C3 B1 .11",           # r4
    ".10 D3 C3 B1 o2 D2 C3 B1 o2 D2 C3 B1 C1 .10",        # r5   the notches run down between them
    ".6 D5 C9 D4 C9 B5 .6",                               # r6   the spikes merge into the mop
    ".4 D6 C10 D5 C10 B5 .4",                             # r7
    ".3 D6 C12 D5 C10 B5 .3",                             # r8
    ".2 C8 D6 C12 D4 C6 B4 .2",                           # r9
    ".2 C34 B6 .2",                                       # r10
    ".2 C34 B6 .2",                                       # r11
    ".2 C34 B6 .2",                                       # r12
    ".2 C34 B6 .2",                                       # r13
    ".2 C34 B6 .2",                                       # r14
    ".2 C7 .1 C9 .2 C9 .1 C7 B4 .2",                      # r15  an uneven fringe
    ".2 C6 .3 C7 .5 C7 .3 C5 B4 .2",                      # r16
    ".2 C5 .14 C4 .11 C4 B2 .2",                          # r17  side locks stop above the ears
    ".2 C3 .31 C2 B4 .2",                                 # r18
    ".2 B2 .40",                                          # r19
])

_EYE = [".oo.", "o5oo", "oooo", ".oo."]                    # the standard dot
_BIG = [".ooo.", "o5ooo", "ooooo", "oo5oo", ".ooo."]       # wide-open: anxious or puzzled
_BLUSH = [(27, 8, ["4444", "4444"]), (27, 36, ["4444", "4444"])]

FACE = {
    "neutral": _BLUSH + [
        (22, 13, _EYE), (22, 31, _EYE),
        (19, 13, ["=="]), (20, 15, ["=="]), (20, 31, ["=="]), (19, 33, ["=="]),   # brows slant in: focused
        (29, 21, ["oooooo"]),                                                      # a short, pursed line
    ],
    "concerned": _BLUSH + [
        (21, 12, _BIG), (21, 31, _BIG),
        (20, 12, ["="]), (19, 13, ["="]), (18, 14, ["=="]), (17, 16, ["=="]),       # brows steeply up: anxious
        (17, 30, ["=="]), (18, 32, ["=="]), (19, 34, ["="]), (20, 35, ["="]),
        (30, 20, ["oo"]), (29, 22, ["oo"]), (30, 24, ["oo"]), (29, 26, ["oo"]),    # a wobbling mouth
        (19, 38, [".s", "ss", "sr"]),                                              # a bead of sweat
    ],
    "pleased": _BLUSH + [
        (23, 13, [".oo.", "o5oo", "oooo"]), (23, 31, [".oo.", "o5oo", "oooo"]),    # open, settled eyes, lower lids up
        (19, 13, ["===="]), (19, 31, ["===="]),                                    # brows level and low
        (29, 20, ["oooooo"]), (28, 26, ["o"]), (27, 27, ["o"]),                    # a lopsided, confident smile
    ],
    "hal_puzzled": _BLUSH + [
        (21, 12, _BIG), (23, 31, [".oo.", "o5oo", "oo.."]),                         # one big eye, one small
        (16, 12, ["==="]), (17, 14, ["=="]),                                       # one brow high
        (21, 31, ["===="]),                                                        # the other low
        (30, 19, ["oo"]), (29, 21, ["oo"]), (30, 23, ["oo"]), (29, 25, ["o"]),      # a squiggle, off centre
    ],
}

EXPRESSIONS = chibi.build(sys.modules[__name__])
