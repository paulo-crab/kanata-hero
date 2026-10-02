"""Vale portrait, chibi direction C. Spec: PORTRAITS_SPEC.md, persona: PORTRAIT_PERSONAS.md.

Status: Candidate, pending director review. A squarer, stiffer head (flat top, flat chin), the only
flat, square shoulders in the cast, graphite hair with a cowlick and a skin-coloured side part, the
green tie and the copper badge. Persona: rigid, wants a defensible audit once shown the evidence, and
softens. Small squared eyes, straight brows, a dead-straight mouth and no blush at rest; pleased is
restrained (corners up by one pixel, a faint blush); the signature vale_softened is the first real
softening.
Every key is a key of vale_sprites.PAL (hair ABCD, skin klmn, suit pqrs, shirt wxy, tie tuv, badge bcde).
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import chibi  # noqa: E402
import vale_sprites as spr  # noqa: E402
from chibi import head_spans, rle_hair  # noqa: E402

SPRITE = spr
PAL = dict(spr.PAL)
SLOTS = spr.SLOTS
EXTRA = {"y": {"hex": spr.PAL["y"], "use": "eye glint (the shirt's lightest step)"}}
SKIN = {"1": "n", "2": "m", "4": "l", "5": "y", "6": "S"}   # fill, shade, blush, glint, mouth inside
BROW = "B"
SIGNATURES = ("vale_softened",)
PROP_KEYS = "bcu"                                  # keys that identify the costume and prop at a glance
TAGLINE = "Squarer and stiffer: small squared eyes, straight brows, a dead-level mouth, no blush at rest. Softens."

HEAD = head_spans(3, [11, 14, 16, 17] + [18] * 24 + [18, 17, 16, 15, 14, 12])      # flat top, flat chin
BODY = {38: (8, 39)}
BODY.update({r: (6, 41) for r in range(39, 48)})             # square shoulders from the first row


def cloth(r, c, a, b, spans):
    d = abs(c - 23.5)
    v = 4.5 - (r - 38)
    if r <= 42 and d <= v - 1:                      # the pale shirt V
        return "x" if c < 24 else "y"
    if r <= 42 and d <= v:
        return "w"
    k = "r"
    if c <= a + 2 or r == 38:                       # the lit left sleeve edge and the top of the shoulders
        k = "s"
    elif c >= b - 4:
        k = "q"
    if r >= 39 and c in (a + 6, b - 6):             # seams between the sleeves and the torso
        k = "o"
    if abs(c - 23.5) <= 1 and r >= 41:              # the green tie
        k = "u"
        if c == 24:
            k = "t"
        if r == 41:
            k = "v" if c == 23 else "u"
    return k


PROPS = [(43, 29, ["bbbb", "bcdb", "bccb", "bcdb", "bbbb"])]       # the copper badge, a lit corner

# Graphite hair: a cowlick, a side part (skin '2'), strands sweeping right, and an uneven fringe.
_h = rle_hair(4, 40, 2, [
    ".15 D1 C3 B1 .20",                             # r2   the cowlick
    ".8 D5 C14 B5 .8",                              # r3
    ".6 D6 C16 B6 .6",                              # r4
    ".4 D7 C18 B7 .4",                              # r5
    ".3 D8 C19 B7 .3",                              # r6
    ".2 C4 D6 C20 B6 .2",                           # r7
    ".2 C10 D4 C16 B6 .2",                          # r8
    ".2 C12 B1 C17 B6 .2",                          # r9
    ".2 C16 B1 C13 B6 .2",                          # r10
    ".2 C20 B1 C9 B6 .2",                           # r11
    ".2 C24 B1 C5 B6 .2",                           # r12
    ".2 C28 B1 C1 B6 .2",                           # r13
    ".2 C10 .1 C14 .1 C4 B6 .2",                    # r14
    ".2 C8 .3 C10 .4 C6 B5 .2",                     # r15
    ".2 C5 .6 C6 .8 C4 B7 .2",                      # r16
    ".2 C3 .13 C3 .10 C2 B5 .2",                    # r17  the long centre lock
    ".2 B2 .14 B2 .13 B5 .2",                       # r18
])
_r0, _rows = _h
for _r, _c in ((5, 20), (6, 19), (7, 19), (8, 18)):  # the side part: a short skin line left of centre, leaning left
    _rows[_r - 2] = _rows[_r - 2][:_c] + "2" + _rows[_r - 2][_c + 1:]
HAIR = (_r0, _rows)

_EYE = ["oooo", "o5oo", "oooo"]                    # small and squared
_WIDE = [".oo.", "o5oo", "oooo", ".oo."]
_BLUSH = [(28, 9, ["444", "444"]), (28, 36, ["444", "444"])]

FACE = {
    "neutral": [
        (23, 14, _EYE), (23, 30, _EYE),
        (20, 13, ["====="]), (20, 30, ["====="]),                # straight, level brows
        (30, 20, ["oooooooo"]),                                  # a dead-straight, tight mouth, and no blush
    ],
    "concerned": _BLUSH[:0] + [
        (22, 14, _WIDE), (22, 30, _WIDE),                        # the eyes widen
        (21, 13, ["="]), (20, 14, ["="]), (19, 15, ["=="]), (18, 17, ["="]),     # brows pinch up
        (18, 30, ["="]), (19, 31, ["=="]), (20, 33, ["="]), (21, 34, ["="]),
        (31, 22, ["oooo"]), (32, 21, ["o"]), (32, 26, ["o"]),     # the line gives way: a small frown
    ],
    "pleased": [
        (23, 14, _EYE), (23, 30, _EYE),
        (19, 13, ["====="]), (19, 30, ["====="]),                # the brows lift a pixel
        (29, 20, ["o"]), (29, 27, ["o"]), (30, 21, ["oooooo"]),   # restrained: the corners rise by one pixel
        (28, 10, ["44"]), (28, 36, ["44"]),                       # a faint blush
    ],
    "vale_softened": _BLUSH + [
        (23, 14, ["oooo", "o5oo", ".oo."]), (23, 30, ["oooo", "o5oo", ".oo."]),    # the lids ease
        (19, 14, ["===="]), (20, 13, ["="]), (20, 18, ["="]),                     # brows relax into arches
        (19, 30, ["===="]), (20, 29, ["="]), (20, 34, ["="]),
        (28, 20, ["o"]), (28, 27, ["o"]), (29, 21, ["o"]), (29, 26, ["o"]), (30, 22, ["oooo"]),   # a real, closed-lip smile
    ],
}

EXPRESSIONS = chibi.build(sys.modules[__name__])
