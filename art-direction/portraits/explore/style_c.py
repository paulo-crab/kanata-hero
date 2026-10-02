"""Direction C, "Chibi icon": an oversized head fills most of the 48x48 and the shoulders are tiny.

A round, wide head (rows 3-37), shoulders only in the bottom ten rows, very flat shading (fill and
one crescent of shadow), round dot eyes with highlights, big readable mouths and round cheeks.
Ruler (cols):  0123456789012345 0123456789012345 0123456789012345   axis between 23|24
"""
NAME = "C  Chibi icon"

HEAD = {3: (15, 32), 4: (11, 36), 5: (9, 38), 6: (8, 39)}
HEAD.update({r: (6, 41) for r in range(7, 29)})
HEAD.update({29: (7, 40), 30: (7, 40), 31: (8, 39), 32: (9, 38), 33: (11, 36), 34: (13, 34), 35: (16, 31), 36: (18, 29)})
NECK = None
BODY = {38: (17, 30), 39: (13, 34), 40: (10, 37)}
BODY.update({r: (8, 39) for r in range(41, 48)})
UNDER_FRINGE = True


def skin_token(r, c, a, b):
    """Very flat: fill, and one crescent of shadow on the lower right."""
    return "2" if c + max(0, r - 28) >= 39 else "1"


PROPS = {
    "engineer": [(43, 29, ["bbb", "bdb", "bcb"])],
    "ivo": [(43, 26, ["gggggggggggg", "gJjjjjjjjjhg", "gjjjjjjjjhhg", "gjjjjjjjhhhg", "gggggggggggg"])],
}

# window: columns 4..43 (40 keys); head columns 6..41 are index 2..37
HAIR = {
    "engineer": (4, 40, 2, [
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
        ".2 C5 .13 C13 B4 .3",              # r15
        ".2 C4 .14 C5 .3 C6 B4 .2",         # r16
        ".2 C4 .16 C3 .4 C5 B4 .2",         # r17
        ".2 C3 .24 C4 B3 .4",               # r18
        ".2 B2 .27 C3 B2 .4",               # r19
        ".36 B2 .2",                        # r20
    ]),
    "ivo": (4, 40, 2, [
        ".7 D3 C2 .3 D4 C2 .3 C3 B1 .12",   # r2
        ".5 D6 C21 B3 .5",                  # r3
        ".4 D7 C22 B4 .3",                  # r4
        ".3 C2 D7 C22 B4 .2",               # r5
        ".2 C5 D7 C20 B4 .2",               # r6
        ".2 C9 D6 C17 B4 .2",               # r7
        ".2 C13 D5 C14 B4 .2",              # r8
        ".1 C34 B4 .1",                     # r9   the side tufts bulge past the head
        ".1 C34 B4 .1",                     # r10
        ".1 C34 B4 .1",                     # r11
        ".1 C34 B4 .1",                     # r12
        ".1 C34 B4 .1",                     # r13
        ".2 C7 C5 .1 C6 .1 C5 .1 C6 B4 .2",     # r14  toothed fringe
        ".2 C6 .5 C4 .3 C6 .3 C5 B4 .2",        # r15
        ".2 C5 .8 C4 .1 C7 .5 C3 B3 .2",        # r16
        ".2 C4 .15 C6 .6 C2 B3 .2",             # r17  centre forelock
        ".2 C3 .17 C4 .14",                     # r18
        ".2 B2 .19 C2 .15",                     # r19
    ]),
    "mira": (4, 40, 2, [
        ".26 D4 C6 B2 .2",                  # r2   the puff, her left (screen right)
        ".8 D6 C22 B3 .1",                  # r3
        ".5 D7 C24 B4",                     # r4
        ".3 C3 D7 C23 B4",                  # r5
        ".2 C5 D7 C22 B4",                  # r6
        ".2 C9 D6 C19 B4",                  # r7
        ".2 C14 D5 C15 B4",                 # r8
        ".2 C32 B4 .2",                     # r9
        ".2 C32 B4 .2",                     # r10
        ".2 C32 B4 .2",                     # r11
        ".2 C32 B4 .2",                     # r12
        ".2 C32 B4 .2",                     # r13
        ".2 C15 .1 C15 B4 .3",              # r14  the parting
        ".2 C14 .3 C13 B4 .4",              # r15
        ".2 C4 .6 C5 .1 C6 .6 C3 B3 .4",    # r16
        ".2 C3 .26 C2 B3 .4",               # r17
        ".2 B2 .27 B3 .6",                  # r18
    ]),
}

_EYE = [".oo.", "o5oo", "oooo", ".oo."]            # round dot with a glint
_EYES = [(22, 14, _EYE), (22, 30, _EYE)]
_BLUSH = [(27, 9, ["4444", "4444"]), (27, 35, ["4444", "4444"])]

FACE = {
    "neutral": _EYES + _BLUSH + [
        (19, 14, ["BBBB"]), (19, 30, ["BBBB"]),
        (28, 20, ["o"]), (28, 27, ["o"]), (29, 21, ["oooooo"]),        # a wide, gentle smile
    ],
    "concerned": _EYES + _BLUSH + [
        (20, 14, ["B"]), (19, 15, ["BB"]), (18, 17, ["B"]),            # brows tilted up in the middle
        (18, 30, ["B"]), (19, 31, ["BB"]), (20, 33, ["B"]),
        (29, 22, [".oo.", "o66o", ".oo."]),                            # a small worried "o"
    ],
    "pleased": [
        (23, 14, [".oo.", "o..o"]), (23, 30, [".oo.", "o..o"]),                 # closed, smiling eyes (thick arcs)
        (19, 14, ["B"]), (18, 15, ["BB"]), (19, 17, ["B"]),
        (19, 30, ["B"]), (18, 31, ["BB"]), (19, 33, ["B"]),
        (28, 20, ["oooooooo", "o666666o", ".oooooo."]),                # big open smile
    ] + _BLUSH,
}
