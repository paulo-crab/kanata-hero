"""Shared kit for the background office workers (two bodies, three palettes).

Status: Approved by the director 2026-10-02. Spec: BACKGROUND_WORKERS_SPEC.md.
The key layout is shared by both bodies, so a palette is a ramp swap on the same
grids (STYLE_BIBLE section 3, GATE1 spec "Customization swaps ramps in PAL only").

Key groups
  hair   A B C D   A is the contour step only
  skin   k l m n   k is the contour step only
  top    p q r s   the shirt or sweater, p on contours and gap lines only
  under  w x y     a pale under-layer (collar, hem) so the top never has to be bright
  legs   O P       trousers
  shoes  S T U     the ink ramp, the same in every palette
  stuff  g h j     phone / screen glass for the individual idles (never #19AFA2)
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "gate1"))
import engineer_sprites as eng  # noqa: E402  (shared leg poses and lower())

lower = eng.lower

SLOTS = {"hair": "ABCD", "skin": "klmn", "jacket": "pqrs", "under": "wxy", "trousers": "OP"}

# Muted on purpose: every top and trouser step stays at or below 30% HSL saturation,
# and the fills sit in the mid values, so the extras recede behind the named cast.
# Names are plain colour words; none is a violet or a marker hue.
PALETTES = {
    "slate": {   # blue-grey top, charcoal trousers, dark brown hair, fair skin
        "hair": "#1F1B25 #352D34 #4C4041 #675856",
        "skin": "#8A5E4E #B38468 #D2A68A #EACBB2",
        "jacket": "#33405A #46556F #5C6C86 #7A8AA0",
        "under": "#8E8E98 #B4B3B8 #D2D0CF",
        "trousers": "#2B2F45 #3A3F58",
    },
    "olive": {   # sage top, brown-charcoal trousers, black hair, deep skin
        "hair": "#14111A #221D24 #332C33 #483E43",
        "skin": "#5A3A32 #744A38 #8C5C44 #A87852",
        "jacket": "#3B4130 #4F5A3F #65714F #848F68",
        "under": "#A89E8C #C9BFA9 #E0D8C6",
        "trousers": "#352F35 #463F46",
    },
    "ash": {     # warm grey top, navy trousers, grey hair, tan skin
        "hair": "#1E1E24 #55545C #6E6D75 #9D9AA3",
        "skin": "#4A3222 #A87850 #C79C72 #E0BC96",
        "jacket": "#4F4844 #665E58 #807770 #9C938A",
        "under": "#8A9098 #B0B5B8 #D0D3D2",
        "trousers": "#2F3550 #40486A",
    },
}

BASE = {
    ".": None,
    "o": "#202337",
    # shoes, ink ramp (same for every palette)
    "S": "#343650", "T": "#535971", "U": "#777A8C",
    # phone: dark bezel, glass face with one lit step (blue glass ramp, never the terminal teal)
    "g": "#203A50", "h": "#366479", "j": "#5AA3AE",
    # mug (individual idle): warm stone ramp
    "e": "#968A85", "f": "#C7B7A0", "i": "#F0DEC0",
}


def make_pal(name):
    """Full PAL for one palette name."""
    pal = dict(BASE)
    for slot, keys in SLOTS.items():
        for k, c in zip(keys, PALETTES[name][slot].split()):
            pal[k] = c
    return pal


PAL = make_pal("slate")

# Silhouette: one dark ink fill plus the outer contour. Used for distant and through-glass figures.
# The interior contour steps (eyes, hair edge, arm gaps) fill in, so only the outline and shape remain.
SILHOUETTE_FILL = "#343650"
SILHOUETTE_PAL = {k: (None if v is None else SILHOUETTE_FILL) for k, v in BASE.items()}
SILHOUETTE_PAL["o"] = "#202337"
for _slot in SLOTS.values():
    for _k in _slot:
        SILHOUETTE_PAL[_k] = SILHOUETTE_FILL
# Lit-edge version: the upper-left contour steps up one ink step where light allows.
SILHOUETTE_LIT_PAL = dict(SILHOUETTE_PAL, L="#535971")


def silhouette(frame):
    """Keep 'o' only where it touches open air (4-neighbour) or the frame edge; interior 'o' becomes fill."""
    out = []
    for y, row in enumerate(frame):
        r = list(row)
        for x, ch in enumerate(row):
            if ch != "o":
                continue
            nb = [frame[y - 1][x] if y else ".", frame[y + 1][x] if y < 23 else ".",
                  row[x - 1] if x else ".", row[x + 1] if x < 15 else "."]
            if "." not in nb:
                r[x] = "S"
        out.append("".join(r))
    return out


def silhouette_lit(frame):
    """Outer contour pixels with open air above or to the left become the lit step 'L'."""
    frame = silhouette(frame)
    out = []
    for y, row in enumerate(frame):
        r = list(row)
        for x, ch in enumerate(row):
            if ch != "o":
                continue
            up = frame[y - 1][x] if y else "."
            left = row[x - 1] if x else "."
            if up == "." or left == ".":
                r[x] = "L"
        out.append("".join(r))
    return out


def stamp(frame, art, row, col, shift=0):
    """Paint a small hand-placed prop or hand onto a copy of a frame ('.' is transparent)."""
    out = list(frame)
    for i, line in enumerate(art):
        r = list(out[row + shift + i])
        for j, ch in enumerate(line):
            if ch != ".":
                r[col + j] = ch
        out[row + shift + i] = "".join(r)
    return out


def check_frames(frames, name):
    for k, fr in frames.items():
        assert len(fr) == 24 and all(len(r) == 16 for r in fr), f"{name} {k}: not 16x24"


# Idle legs: level stance (extras are plainer than the named cast), shoes from the ink ramp.
LEGS_IDLE_S = [
    "....oOPPoPPOo...",
    "....oOPPoPPOo...",
    "....oOPPoPPOo...",
    "...oTUUToTUUTo..",
    "...oSTTSoSTTSo..",
    "....oooo.oooo...",
]
LEGS_IDLE_N = [row.translate(eng.HEEL) for row in LEGS_IDLE_S]
LEGS_S, LEGS_N = eng.LEGS_S, eng.LEGS_N


def walk_front_back(base, legs):
    """Same rule as the Engineer: contacts 1 px lower, passing frames not."""
    out = []
    for i, lg in enumerate(legs):
        fr = base[0:18] + lg
        out.append(lower(fr) if i % 2 == 0 else fr)
    return out


def walk_side(head, arms, hem, west=False):
    """E or W walk. head = rows 0-11, arms = (neutral, back, forward) 5-row blocks (rows 12-16)."""
    legs = [eng.LEG_C0, eng.LEG_P1, eng.LEG_C2, eng.LEG_P3]
    if west:
        legs = [[r[::-1] for r in lg] for lg in legs]
    _n, back, fwd = arms
    c0 = lower(head + back + [hem] + legs[0])
    p1 = head + arms[0] + [hem] + legs[1]
    c2 = lower(head + fwd + [hem] + legs[2])
    p3 = head + arms[0] + [hem] + legs[3]
    return [c0, p1, c2, p3]


def variant(base, rows, alt=None):
    """Individual idle: frame 0 replaces body rows from the dict {row: text}; frame 1 is the same
    pose settled 1 px (or, when alt is given, with those rows swapped first, e.g. a phone scroll)."""
    f0 = [rows.get(y, r) for y, r in enumerate(base)]
    f1 = f0 if alt is None else [{**rows, **alt}.get(y, r) for y, r in enumerate(base)]
    return [f0, lower(f1)]
