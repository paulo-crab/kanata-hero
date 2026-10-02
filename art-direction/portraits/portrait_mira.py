"""Mira portrait, chibi direction C, plus the six patch states. Spec: PORTRAITS_SPEC.md, persona: PORTRAIT_PERSONAS.md.

Status: Candidate, pending director review. A round head with a slightly pointed chin, big bright
oval eyes with a second sparkle, a bun on her left (screen right) that is separated from the dome by an
ink notch, a cocked right brow and a lopsided smirk. Signature: mira_grin (wink and a tongue-out grin).
Every key is a key of mira_sprites.PAL (hair ABCD, skin klmn, ochre panel wxyz, green panel EFGH,
coral strap cdef). The blush uses the skin ramp, not the strap coral (decision in PORTRAITS_SPEC).
Patch icons come from ../cast/mira_patches.py (PORTRAIT_PATCHES) and are applied by `with_patches`.
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import chibi  # noqa: E402
import mira_sprites as spr  # noqa: E402
from chibi import head_spans, rle_hair  # noqa: E402

SPRITE = spr
PAL = dict(spr.PAL)
SLOTS = spr.SLOTS
EXTRA = {"r": {"hex": spr.PAL["r"], "use": "eye glints and teeth (the paper's lightest step)"}}
SKIN = {"1": "n", "2": "m", "4": "D", "5": "r", "6": "w"}   # fill, shade, blush (the plum hair step, not the coral), glint, mouth inside
BROW = "B"
SIGNATURES = ("mira_grin",)
PROP_KEYS = "de"                                  # keys that identify the costume and prop at a glance
TAGLINE = "Big sparkly eyes, a cocked right brow, a lopsided smirk; the bun sits apart from the dome. Winks."

HEAD = head_spans(3, [9, 13, 15, 16] + [18] * 21 + [18, 17, 16, 14, 12, 10, 8, 6, 5])    # a slightly pointed chin
BODY = {38: (17, 30), 39: (13, 34), 40: (10, 37)}
BODY.update({r: (8, 39) for r in range(41, 48)})


def cloth(r, c, a, b, spans):
    t = min(spans)
    if c <= 23:                                     # her right: garden green
        k = "F"
        if c <= a + 2:
            k = "G"
        if c == 23:
            k = "E"
    else:                                           # her left: ochre
        k = "x"
        if c == b:                                  # the dark step only on the contour
            k = "w"
        if c == 24:
            k = "y"
    s = c - 11 - (r - t)                            # coral strap, from her right shoulder across the chest
    if r > t and s in (0, 1):
        k = "e" if s == 0 else "d"
    return k


PROPS = []

# The dome and fringe, with the bun on her left (screen right). The bun is a ball with its own ink
# arc (the notch) where it overlaps the dome. Window columns 4..43.
HAIR = rle_hair(4, 40, 2, [
    ".30 D1 C2 B1 .6",                          # r2   top of the bun
    ".11 D3 C12 o3 D2 C3 B1 .5",                # r3   dome, then the V notch, then the bun
    ".7 D5 C14 o2 D2 C4 B2 .4",                 # r4
    ".5 D6 C15 o1 D2 C6 B2 .3",                 # r5
    ".4 D7 C15 o1 D2 C6 B2 .3",                 # r6
    ".2 D8 C16 o1 D2 C6 B3 .2",                 # r7
    ".2 D8 C17 o1 D1 C5 B4 .2",                 # r8
    ".2 D6 C20 o1 D1 C4 B1 o1 B2 .2",           # r9   the bun's lower arc
    ".2 C25 B2 o6 B3 .2",                       # r10
    ".2 C32 B4 .2",                             # r11
    ".2 C32 B4 .2",                             # r12
    ".2 C32 B4 .2",                             # r13
    ".2 C14 .1 C17 B4 .2",                      # r14  the parting
    ".2 C13 .3 C6 .4 C6 B4 .2",                 # r15
    ".2 C4 .6 C5 .1 C6 .6 C5 B3 .2",            # r16
    ".2 C3 .29 C2 B2 .2",                       # r17
    ".2 B2 .32 B2 .2",                          # r18
])

_EYE = [".oo.", "o5oo", "oooo", "oo5o", ".oo."]    # a tall oval with a second sparkle
_BLUSH = [(27, 9, ["4444", "4444"]), (27, 35, ["4444", "4444"])]

FACE = {
    "neutral": _BLUSH + [
        (22, 14, _EYE), (22, 30, _EYE),
        (19, 14, ["===="]), (17, 30, [".==."]), (18, 30, ["=..="]),      # the right brow cocked: ready to go
        (30, 20, ["ooo"]), (29, 23, ["ooo"]), (28, 26, ["oo"]),           # a lopsided smirk, rising to her left
    ],
    "concerned": _BLUSH + [
        (23, 13, [".oo.", "o5oo", "oooo", ".oo."]), (23, 29, [".oo.", "o5oo", "oooo", ".oo."]),   # eyes down and aside
        (21, 14, ["="]), (20, 15, ["="]), (19, 16, ["=="]), (18, 18, ["="]),      # brows steeply up: earnest
        (18, 30, ["="]), (19, 31, ["="]), (20, 32, ["=="]), (22, 34, ["="]),
        (29, 19, ["oooo"]), (30, 18, ["o"]),                              # a small pressed mouth, off centre
    ],
    "pleased": _BLUSH + [
        (23, 14, [".oo.", "o..o"]), (23, 30, [".oo.", "o..o"]),             # closed eyes: proud
        (17, 14, ["===="]), (17, 30, ["===="]),                           # both brows lifted
        (28, 19, ["oooooooooo"]), (29, 19, ["o55555555o"]), (30, 20, [".oooooooo."]),   # a toothy smile
    ],
    "mira_grin": _BLUSH + [
        (22, 14, _EYE),                                                    # a wink: the left eye stays open,
        (24, 30, [".oo.", "o..o"]),                                       # the right eye is a closed arc
        (19, 14, ["===="]), (16, 30, [".==."]), (17, 30, ["=..="]),       # cocked brow, higher still
        (28, 18, ["oooooooooo"]), (29, 18, ["o66666666o"]), (30, 19, ["o66dddd6o"]), (31, 20, [".oooooo."]),   # grin, tongue out
    ],
}

EXPRESSIONS = chibi.build(sys.modules[__name__])

import mira_patches as patches  # noqa: E402  (../cast, already on sys.path)

# Patch icons use mira_patches.PATCH_PAL keys (hexes already in her palette or the brass ramp).
PATCH_PAL = dict(PAL)
PATCH_PAL.update(patches.PATCH_PAL)


def with_patches(grid, k):
    """The portrait wearing patches 1..k (0 returns the grid unchanged)."""
    return patches.portrait_patches(grid, k)
