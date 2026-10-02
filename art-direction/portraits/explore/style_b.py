"""Direction B, "Warm RPG bust": a rounded-square head in the classic 16-bit dialogue-portrait style.

Rounded corners and a soft jaw, small ears, a short neck and medium shoulders. Eyes are 3x3 ink
blocks with a glint and a soft lid line (one skin-shade row above), a tiny nose hint, friendly
mouths. Three skin tones (fill, shade, deep shade under the chin) plus a soft blush; simplified hair clumps with one
highlight band.
Ruler (cols):  0123456789012345 0123456789012345 0123456789012345   axis between 23|24
"""
NAME = "B  Warm RPG bust"

HEAD = {4: (14, 33), 5: (12, 35), 6: (11, 36)}
HEAD.update({r: (11, 36) for r in range(7, 30)})
HEAD.update({r: (9, 38) for r in range(21, 26)})       # small ears at the sides
HEAD.update({30: (12, 35), 31: (13, 34), 32: (15, 32), 33: (17, 30)})
NECK = {r: (20, 27) for r in range(34, 37)}
BODY = {37: (15, 32), 38: (10, 37), 39: (7, 40), 40: (5, 42), 41: (3, 44)}
BODY.update({r: (2, 45) for r in range(42, 48)})
UNDER_FRINGE = True
NECK_TOKEN = "7"        # the neck is in the deep shade under the chin


def skin_token(r, c, a, b):
    """Three tones: fill, a shade on the right cheek and ear, and a deep shade under the chin."""
    if r == 33 or (r == 32 and c >= 24):
        return "7"
    if c >= 35 or (r in range(21, 26) and c >= 37):
        return "2"
    return "1"


PROPS = {
    "engineer": [(43, 31, ["bbb", "bdb", "bcb"])],
    "ivo": [(43, 28, ["gggggggggggg", "gJjjjjjjjjhg", "gjjjjjjjjhhg", "gjjjjjjjhhhg", "gggggggggggg"])],
}

# window: columns 6..41 (36 keys); head columns 11..36 are index 5..30, ears index 3-4 and 31-32
HAIR = {
    "engineer": (6, 36, 2, [
        ".11 D3 C5 B1 .16",                 # r2
        ".8 D5 C13 B3 .7",                  # r3  rounded dome
        ".6 D6 C16 B4 .4",                  # r4
        ".4 C3 D6 C15 B4 .4",               # r5  one highlight band
        ".3 C5 D6 C13 B5 .4",               # r6
        ".3 C9 D5 C10 B5 .4",               # r7
        ".3 C13 D4 C7 B5 .4",               # r8
        ".3 C24 B5 .4",                     # r9
        ".3 C24 B5 .4",                     # r10
        ".3 C24 B5 .4",                     # r11
        ".3 C5 .8 C11 B5 .4",               # r12  short left temple, long swept fringe at right
        ".3 C4 .8 C12 B5 .4",               # r13
        ".3 C4 .9 C5 .3 C4 B4 .4",          # r14
        ".3 C3 .13 C3 .4 C4 B2 .4",         # r15
        ".27 C3 B2 .4",                     # r16
        ".30 B2 .4",                        # r17
    ]),
    "ivo": (6, 36, 2, [
        ".7 D3 C2 .3 D3 C2 .3 C3 B1 .9",    # r2
        ".5 D6 C15 B3 .7",                  # r3
        ".4 D7 C16 B4 .5",                  # r4
        ".4 C2 D7 C15 B4 .4",               # r5
        ".3 C5 D6 C13 B5 .4",               # r6
        ".3 C9 D5 C10 B5 .4",               # r7
        ".3 C13 D4 C7 B5 .4",               # r8
        ".3 C24 B5 .4",                     # r9
        ".3 C24 B5 .4",                     # r10
        ".3 C24 B5 .4",                     # r11
        ".3 C24 B5 .4",                     # r12
        ".3 C5 C4 .1 C4 .1 C4 .1 C4 B4 .5",     # r13  toothed fringe
        ".3 C4 .4 C3 .3 C5 .3 C4 B2 .5",        # r14
        ".3 C3 .13 C4 .4 C3 B2 .4",             # r15  centre forelock
        ".3 B2 .15 C2 .14",                     # r16
    ]),
    "mira": (6, 36, 2, [
        ".25 D3 C5 B1 .2",                  # r2   the puff, her left (screen right)
        ".6 D8 C17 B3 .2",                  # r3
        ".5 D8 C19 B3 .1",                  # r4
        ".4 C3 D6 C17 B4 .2",               # r5
        ".4 C5 D6 C15 B4 .2",               # r6
        ".4 C9 D5 C11 B5 .2",               # r7
        ".4 C13 D4 C9 B4 .2",               # r8
        ".4 C24 B4 .4",                     # r9
        ".4 C24 B4 .4",                     # r10
        ".4 C24 B4 .4",                     # r11
        ".4 C12 .1 C11 B4 .4",              # r12  the parting
        ".4 C11 .3 C10 B4 .4",              # r13
        ".4 C4 .5 C4 .1 C5 .5 C2 B2 .4",    # r14
        ".4 C3 .21 B3 .5",                  # r15
    ]),
}

_EYES = [(21, 16, ["5oo", "ooo", "ooo"]), (21, 29, ["5oo", "ooo", "ooo"]),
         (20, 15, ["2222"]), (20, 29, ["2222"])]            # eyes and a soft lid line
_NOSE = [(25, 23, ["22"])]
_BLUSH = [(26, 13, ["44"]), (27, 12, ["444"]), (26, 33, ["44"]), (27, 33, ["444"])]

FACE = {
    "neutral": _EYES + _NOSE + _BLUSH + [
        (18, 15, ["BBBB"]), (18, 29, ["BBBB"]),
        (28, 21, ["o"]), (28, 26, ["o"]), (29, 22, ["oooo"]),          # a tiny smile
    ],
    "concerned": _EYES + _NOSE + _BLUSH + [
        (23, 18, ["5"]), (23, 31, ["5"]),                              # watery eyes: a second glint
        (19, 15, ["B"]), (18, 16, ["BB"]), (17, 18, ["B"]),            # brows tilted up in the middle
        (17, 29, ["B"]), (18, 30, ["BB"]), (19, 32, ["B"]),
        (29, 22, ["oooo"]), (30, 21, ["o"]), (30, 26, ["o"]),
    ],
    "pleased": [
        (20, 15, ["2222"]), (20, 29, ["2222"]),
        (23, 15, ["o"]), (22, 16, ["oo"]), (23, 18, ["o"]),            # closed eyes, smiling arcs
        (23, 29, ["o"]), (22, 30, ["oo"]), (23, 32, ["o"]),
        (18, 15, ["B"]), (17, 16, ["BB"]), (17, 30, ["BB"]), (18, 32, ["B"]),
        (28, 20, ["oooooooo"]), (29, 21, ["o6666o"]), (30, 22, ["oooo"]),   # open smile
    ] + _NOSE + _BLUSH,
}
