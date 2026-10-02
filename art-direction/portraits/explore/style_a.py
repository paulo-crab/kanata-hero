"""Direction A, "Sprite-true": the sprite's face language scaled up.

A boxy head (flat crown, square jaw with small corner bevels) that fills rows 2-37, short
shoulders, eyes as 2x3 ink blocks with a 1 px glint and no sclera, a one-pixel nose, a short
line for a mouth, two skin tones (fill and one shadow side) and a small blush cluster on each
cheek. Hair is a few big clumps with one highlight band and no strand lines.
Ruler (cols):  0123456789012345 0123456789012345 0123456789012345   axis between 23|24
"""
from explore_common import R

NAME = "A  Sprite-true"

# head fill per row, inclusive columns: a 28 px wide box, bevelled at the jaw
HEAD = {r: (10, 37) for r in range(6, 35)}
HEAD.update({35: (11, 36), 36: (12, 35)})
# short shoulders, no neck: the chin line sits on the cardigan
BODY = {38: (14, 33), 39: (9, 38), 40: (6, 41), 41: (4, 43)}
BODY.update({r: (3, 44) for r in range(42, 48)})
NECK = None
UNDER_FRINGE = True


def skin_token(r, c, a, b):
    """Two tones: fill, and the shadow on the three right-hand columns and under the jaw."""
    return "2" if (c >= 35 or r == 36) else "1"


PROPS = {
    "engineer": [(42, 31, ["bbb", "bdb", "bcb"])],
    "ivo": [(42, 29, ["gggggggggggg", "gJjjjjjjjjhg", "gjjjjjjjjhhg", "gjjjjjjjhhhg", "gggggggggggg", "gggggggggggg"])],
}

# window: columns 8..39 (32 keys); head columns 10..37 are index 2..29
HAIR = {
    "engineer": (8, 32, 2, [
        ".7 D2 C2 .7 C2 B1 .11",            # r2   two tufts above the flat crown
        ".3 D6 C17 B3 .3",                  # r3   flat crown
        ".2 D7 C18 B3 .2",                  # r4
        ".2 C3 D6 C15 B4 .2",              # r5   one highlight band running down to the right
        ".2 C5 D6 C13 B4 .2",               # r6
        ".2 C8 D5 C11 B4 .2",               # r7
        ".2 C12 D4 C8 B4 .2",               # r8
        ".2 C24 B4 .2",                     # r9
        ".2 C24 B4 .2",                     # r10
        ".2 C24 B4 .2",                     # r11
        ".2 C4 .10 C10 B4 .2",              # r12  short left temple, forehead opens, long swept fringe at right
        ".2 C4 .9 C11 B4 .2",               # r13
        ".2 C3 .10 C4 .3 C6 B2 .2",         # r14
        ".2 C3 .11 C2 .4 C5 B3 .2",         # r15
        ".25 C3 B2 .2",                     # r16  the fringe's point
        ".28 B2 .2",                        # r17
    ]),
    "ivo": (8, 32, 2, [
        ".5 D3 C2 .2 D3 C2 .2 C3 B1 .9",    # r2   three silver tufts
        ".3 D6 C17 B3 .3",                  # r3
        ".2 D7 C18 B3 .2",                  # r4
        ".2 C2 D7 C16 B3 .2",               # r5
        ".2 C5 D6 C14 B3 .2",               # r6
        ".2 C9 D5 C11 B3 .2",               # r7
        ".2 C13 D4 C8 B3 .2",               # r8
        ".1 C26 B4 .1",                     # r9   the side tufts bulge past the head box
        ".1 C26 B4 .1",                     # r10
        ".1 C27 B3 .1",                     # r11
        ".1 C26 B4 .1",                     # r12
        ".1 C5 C4 .1 C5 .1 C4 .1 C5 B3 .2",     # r13  toothed fringe
        ".1 C4 .4 C3 .3 C5 .3 C4 B3 .2",        # r14
        ".1 C3 .12 C4 .5 C3 B2 .2",             # r15  centre forelock
        ".1 B2 .14 C2 .13",                     # r16
    ]),
    "mira": (8, 32, 2, [
        ".22 D3 C4 B1 .2",                  # r2   the puff, her left (screen right)
        ".3 D7 C13 D2 C4 B3",               # r3
        ".2 D8 C18 B4",                     # r4
        ".2 C2 D7 C16 B5",                  # r5
        ".2 C5 D6 C14 B5",                  # r6
        ".2 C9 D5 C11 B5",                  # r7
        ".2 C13 D4 C8 B5",                  # r8
        ".2 C24 B6",                        # r9
        ".2 C24 B4 .2",                     # r10
        ".2 C24 B4 .2",                     # r11
        ".2 C12 .1 C12 B3 .2",              # r12  the parting
        ".2 C11 .3 C11 B3 .2",              # r13
        ".2 C4 .5 C4 .1 C5 .5 C2 B2 .2",    # r14
        ".2 C3 .21 B3 .3",                  # r15
    ]),
}

# face stamps (row, col, rows). Tokens: o ink, 5 glint, 6 mouth interior, 4 blush, 2 skin shade, B brow.
# Eyes are 2x3 ink blocks at columns 16-17 and 30-31 (mirror images about the 23|24 axis).
_EYES = [(22, 16, ["5o", "oo", "oo"]), (22, 30, ["5o", "oo", "oo"])]
_BLUSH = [(26, 12, ["444", "444"]), (26, 33, ["444", "444"])]
_NOSE = [(27, 24, ["2"])]

FACE = {
    "neutral": _EYES + _BLUSH + _NOSE + [
        (19, 15, ["BBB"]), (19, 30, ["BBB"]),                              # level brows
        (29, 20, ["o"]), (29, 27, ["o"]), (30, 21, ["oooooo"]),            # a short line with its ends lifted
    ],
    "concerned": _NOSE + [
        (22, 16, ["5o", "oo", "o5"]), (22, 30, ["5o", "oo", "o5"]),        # watery eyes: a second glint
        (20, 15, ["B"]), (19, 16, ["B"]), (18, 17, ["B"]),                 # brows tilted up in the middle
        (18, 30, ["B"]), (19, 31, ["B"]), (20, 32, ["B"]),
        (30, 22, ["oooo"]), (31, 21, ["o"]), (31, 26, ["o"]),              # small mouth, corners down
    ] + _BLUSH,
    "pleased": [
        (23, 15, ["o"]), (22, 16, ["oo"]), (23, 18, ["o"]),                # closed, smiling eyes
        (23, 29, ["o"]), (22, 30, ["oo"]), (23, 32, ["o"]),
        (19, 15, ["B"]), (18, 16, ["BB"]), (18, 30, ["BB"]), (19, 32, ["B"]),
        (29, 20, ["oooooooo", ".o6666o.", "..oooo.."]),                    # open smile
    ] + _BLUSH + _NOSE,
}
