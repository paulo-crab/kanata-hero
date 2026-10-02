"""Noor portrait, chibi direction C. Spec: PORTRAITS_SPEC.md, persona: PORTRAIT_PERSONAS.md.

Status: Approved by the player 2026-10-02. A longer, narrower head (chin on row 38) and the narrowest
shoulders in the cast; blue-black crop with two crown tufts of different size and a notch between
them; the coral folder held against the left (screen-left) shoulder. Persona: precise, dry, quietly
defiant. Half-lidded eyes with a flat upper lid, brows that never match, a flat mouth with one corner.
Signature: noor_unimpressed (flat lids, a sidelong glance, a dead-flat mouth).
Every key is a key of noor_sprites.PAL (hair ABCD, skin klmn, shirt pqrs, folder cdef and jlJ).
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import chibi  # noqa: E402
import noor_sprites as spr  # noqa: E402
from chibi import head_spans, rle_hair  # noqa: E402

SPRITE = spr
PAL = dict(spr.PAL)
SLOTS = spr.SLOTS
EXTRA = {"s": {"hex": spr.PAL["s"], "use": "eye glint (the shirt's lightest step)"}}
SKIN = {"1": "n", "2": "m", "4": "f", "5": "s", "6": "S"}   # fill, shade, blush, glint, mouth inside
BROW = "A"
SIGNATURES = ("noor_unimpressed",)
PROP_KEYS = "dej"                                  # keys that identify the costume and prop at a glance
TAGLINE = "Tall and narrow: half-lidded eyes, brows that never match, a flat mouth with one corner. Deadpan."

HEAD = head_spans(3, [8, 12, 14, 15] + [16] * 23 + [16, 15, 14, 13, 11, 9, 7, 5, 3])    # tall and narrow: rows 3-38
BODY = {40: (19, 28), 41: (15, 32), 42: (12, 35)}
BODY.update({r: (10, 37) for r in range(43, 48)})


def cloth(r, c, a, b, spans):
    d = abs(c - 23.5)
    v = 3.5 - (r - 40)
    if r <= 42 and d <= v - 1:                      # the V neck: skin, with a dark neck line along its edge
        return "m"
    if r <= 42 and d <= v:
        return "p"
    k = "r"
    if c <= a + 2:
        k = "s"
    elif c >= b - 3:
        k = "q"
    if r >= 43 and c in (23, 24):                   # placket
        k = "q"
    if r >= 43 and c in (a + 5, b - 5):             # sleeve seams
        k = "q"
    return k


# The coral folder is held against her left (screen-left) shoulder, overlapping the shirt edge: two sea-blue
# tabs, a coral face, a pale label.
PROPS = [
    (41, 5, [".oooo.oooo..", "ojJjoojJjo..", "oooooooooooo", "odeeeeeeeeeo", "odeeffffeeeo",
             "odeeejjjeeeo", "odeeeeeeeeeo", "oddddddddddo"]),
]

HAIR = rle_hair(6, 36, 2, [
    ".9 D2 C2 B1 .6 D1 C1 B1 .13",                 # r2   two crown tufts, the left one larger
    ".8 D4 C4 B1 o1 D2 C5 B3 .8",                  # r3   a notch between them
    ".6 D6 C8 D3 C4 B3 .6",                        # r4
    ".4 D5 C8 D5 C7 B3 .4",                        # r5
    ".3 D4 C10 D5 C8 B3 .3",                       # r6
    ".2 C4 D5 C10 D3 C8 B2 .2",                    # r7
    ".2 C14 D4 C12 B2 .2",                         # r8
    ".2 C30 B2 .2",                                # r9
    ".2 C30 B2 .2",                                # r10
    ".2 C30 B2 .2",                                # r11
    ".2 C30 B2 .2",                                # r12
    ".2 C30 B2 .2",                                # r13
    ".2 C12 .8 C10 B2 .2",                         # r14  a heavy left lock, the right hairline stepped
    ".2 C11 .9 C9 B3 .2",                          # r15
    ".2 C10 .12 C3 .3 C2 B2 .2",                   # r16  uneven tips
    ".2 C8 .22 B2 .2",                             # r17
    ".2 C4 .26 B2 .2",                             # r18
    ".2 B3 .31",                                   # r19
])

_EYE = ["oooo", "o5oo", ".oo."]                    # half-lidded: a flat upper lid
_BLUSH = [(29, 10, ["44", "44"]), (29, 36, ["44", "44"])]      # small: dry

FACE = {
    "neutral": _BLUSH + [
        (24, 14, _EYE), (24, 30, _EYE),
        (21, 14, ["===="]), (20, 30, ["===="]),                  # brows that never quite match
        (31, 21, ["ooooo"]), (30, 26, ["o"]),                     # a flat dry mouth, one corner up
    ],
    "concerned": _BLUSH + [
        (24, 14, _EYE), (24, 30, _EYE),
        (20, 14, ["="]), (21, 15, ["=="]), (22, 17, ["="]),         # the left brow drops toward the nose
        (18, 30, [".=="]), (19, 30, ["=..="]),                    # the right brow lifts: skeptical
        (31, 20, ["oooooo"]), (32, 26, ["o"]),                    # a flat mouth, one corner pulled down
    ],
    "pleased": _BLUSH + [
        (25, 14, ["oooo", ".oo."]), (25, 30, ["oooo", ".oo."]),   # a squint-smile: the lids rise to meet
        (20, 14, ["===="]), (19, 30, ["===="]),
        (31, 20, ["ooooo"]), (30, 25, ["o"]), (29, 26, ["o"]),    # a quiet one-sided smile, lips closed
    ],
    "noor_unimpressed": [
        (24, 15, ["oooo", "o5oo"]), (24, 31, ["oooo", "o5oo"]),    # lids flat, the glance slides right
        (21, 14, ["===="]), (21, 30, ["===="]),                  # both brows flat and low
        (31, 21, ["oooooo"]),                                     # a dead-flat mouth
    ],
}

EXPRESSIONS = chibi.build(sys.modules[__name__])
