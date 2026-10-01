"""Engineer (player avatar) Gate 1 frames, hand-placed at 16x24 logical px.

Status: Gate 1 approved by the player 2026-10-02. Walks S, N, W added after the gate.
Spec: GATE1_ENGINEER_SPEC.md. Every pixel is a key into PAL; "." is
transparent. Anchor is the pixel edge between columns 7 and 8 under row 23.
Customization swaps ramps in PAL only; the key layout never changes.
"""

PAL = {
    ".": None,
    "o": "#202337",  # outline ink (STYLE_BIBLE section 3)
    # hair: fill C B D, A only on contour swaps
    "A": "#2B1E26", "B": "#4A2E2E", "C": "#6E4434", "D": "#93603F",
    # skin: fill n m l, k only on contour / occlusion
    "k": "#6E4433", "l": "#9C6448", "m": "#C98B62", "n": "#E8B184",
    # jacket (muted teal, all steps <= 60% HSL saturation): fill s r q, p on contour
    "p": "#1B4450", "q": "#25707A", "r": "#3A9C9C", "s": "#7CCFC2",
    # collar
    "w": "#C7B7A0", "x": "#E2D6C2", "y": "#F4F2EC",
    # trousers: fill P O (#202337 shared with outline)
    "O": "#2C3352", "P": "#3E4870", "Q": "#59658F",
    # shoes
    "S": "#523D4C", "T": "#85565A", "U": "#BA785F",
    # badge (brass)
    "b": "#705056", "c": "#AC7655", "d": "#E1AC62",
}

# Ramp groups that a customization option may replace, key-for-key.
SLOTS = {
    "hair": "ABCD",
    "skin": "klmn",
    "jacket": "pqrs",
    "trousers": "OPQ",
}

S = [
"......oooo......",
"....AADDCCoo....",
"...ADDDCCCCBo...",
"...ADCCCCCBBo...",
"...oCCCCBBBBo...",
"...oCCBCBBBBo...",
"...oBllllmBBo...",
"...oBnommomBo...",
"...oknmmmmlko...",
"....oklmmlko....",
"...ossxyyxqqo...",
"..psprryyrbqqo..",
"..psprrqyqrdqo..",
"..psprrrqqqcqo..",
"..osprrrqqqpqo..",
"..ompqqqqqqpmo..",
"..oloOPPPPOolo..",
"....oOPPOPPPo...",
"....oOPPoOPPo...",
"....oOPPoOPPo...",
"....oOPPoTUUTo..",
"...oTUUToSTTSo..",
"...oSTTSooooo...",
"....oooo........",
]
N = [
"....oooooo......",
"...ADDDCCCoo....",
"...ADDDDCCCBo...",
"...ADDCCDCBBo...",
"...oCDCCCBCBo...",
"...oCCCBCCBBo...",
"...oCBCCBBBBo...",
"...oBCBBBCBBo...",
"...oBBCBBBBBo...",
"....oBlmmlAo....",
"...osssxxsqqo...",
"..psprrqrrrpqo..",
"..psprrqrrrpqo..",
"..psprrqqqqpqo..",
"..osprrqqqqpqo..",
"..ompqqpqqqpmo..",
"..oloOPPPPOolo..",
"....oOPPOPPPo...",
"....oOPPoOPPo...",
"....oOPPoOPPo...",
"...oSTTSoOPPo...",
"...oSSSSoSTTSo..",
"....oooooSSSSo..",
".........oooo...",
]
E_HEAD = [
".....ooooo......",
"....ADDDCCoo....",
"...ADDCCCCCCo...",
"...ADCCCCCCBBo..",
"...oCCCCCBBBo...",
"...oCCCCCBBBo...",
"...oBCCBlllmo...",
"...oBBBknomno...",
"...oABBkmmmmo...",
"....oABlmmlo....",
"....osssxyqo....",
"...psrrrrxqqo...",
]
ARM_N = [
"...psrrqqrrqo...",
"...psrrqpqqqo...",
"...osrrqpqqpo...",
"...opqqmmqqpo...",
"....oOPlmPOo....",
]
ARM_B = [
"...psrqqrrrqo...",
"...psqprqqqqo...",
"...oqprrqqqpo...",
"...ommqqqqqpo...",
"...olmPPPPOo....",
]
ARM_F = [
"...psrrrqqrqo...",
"...psrrrqqpqo...",
"...osrrrqqpqo...",
"...opqqqqqmmo...",
"....oOPPPPlmo...",
]
E_LEGS = [
"....oOPPPPOo....",
"....oOPPoPPo....",
"....oOPPoPPo....",
"...oTUToOPPo....",
"...oSTSooTUUTo..",
"....ooo.oSTTTSo.",
".........oooooo.",
]
W = [
"......ooooo.....",
"....AADDDCCo....",
"...ADDDCCCCBo...",
"..ADDCCCCCCBo...",
"...oDCCCCBBBo...",
"...oCCCCCBBBo...",
"...ollmBBBBBo...",
"...onmonkBBAo...",
"...ommmmkBBAo...",
"....olmmlBAo....",
"....oyxsssqo....",
"...psybrrrqqo...",
"...psdrqqrrqo...",
"...pscrqpqqqo...",
"...osrrqpqqpo...",
"...opqqmmqqpo...",
"....oOPlmPOo....",
"....oOPPPPOo....",
"....oOPPPPOo....",
"....oPPoPPOo....",
"....oPPoTUTo....",
"..oTUUToSTSo....",
".oSTTTSoooo.....",
".oooooo.........",
]
LEG_C0 = [
"....oOPPoPPPo...",
"...oOPPo.oPPo...",
"...oOPo..oPPPo..",
"..oSTTo..oTUUTo.",
"..oSSo...oSTTTo.",
"..oo.....oooooo.",
]
LEG_P1 = [
"....oOPPPPOo....",
"....oOPoPPPo....",
"...oTUToPPPo....",
"...oSTSoTUUTo...",
"....ooooSTTTUo..",
"........oooooo..",
]
LEG_C2 = [
"....oPPPoOOOo...",
"...oPPPo.oOOo...",
"...oPPo..oOOOo..",
"..oTUUo..oSTTSo.",
"..oTTo...oSSSTo.",
"..oo.....oooooo.",
]
LEG_P3 = [
"....oOPPPPOo....",
"....oPPoOOOo....",
"...oTUToOOOo....",
"...oTTToSTTSo...",
"....ooooSSTTSo..",
"........oooooo..",
]
E = E_HEAD + ARM_N + E_LEGS

def lower(frame):
    """Shift head+torso (rows 0-16) down 1 px; legs rows 18-23 unchanged."""
    blank = "." * 16
    return [blank] + frame[0:17] + frame[18:24]

def walk_e():
    up = lambda arm: E_HEAD + arm  # rows 0-16
    c0 = lower(up(ARM_B) + ["....oOPPPPOo...."] + LEG_C0)
    p1 = up(ARM_N) + ["....oOPPPPOo...."] + LEG_P1
    c2 = lower(up(ARM_F) + ["....oOPPPPOo...."] + LEG_C2)
    p3 = up(ARM_N) + ["....oOPPPPOo...."] + LEG_P3
    return [c0, p1, c2, p3]

# Front and back walks: legs alternate toward and away from the camera; the
# trailing foot lifts 2 px on contacts and 1 px on passing frames.
LEGS_S = [
    [  # contact: screen-left foot forward and planted, right foot back
        "....oOPPoOPPo...",
        "....oOPPoTUUTo..",
        "....oOPPoSTTSo..",
        "...oTUUTooooo...",
        "...oSTTSo.......",
        "....oooo........",
    ],
    [  # passing: right foot lifts past the planted left
        "....oOPPoOPPo...",
        "....oOPPoOPPo...",
        "....oOPPoTUTo...",
        "...oTUUToSTSo...",
        "...oSTTSoooo....",
        "....oooo........",
    ],
    [  # contact: screen-right foot forward and planted, left foot back
        "....oOPPoOPPo...",
        "...oTUUToOPPo...",
        "...oSTTSoOPPo...",
        "....oooooTUUTo..",
        "........oSTTSo..",
        ".........oooo...",
    ],
    [  # passing: left foot lifts past the planted right
        "....oOPPoOPPo...",
        "....oOPPoOPPo...",
        "....oTUToOPPo...",
        "....oSTSoTUUTo..",
        "....oooooSTTSo..",
        ".........oooo...",
    ],
]
HEEL = str.maketrans({"U": "T", "T": "S"})  # from behind the shoes show heels
LEGS_N = [[row.translate(HEEL) for row in legs] for legs in LEGS_S]


def walk_front_back(base, legs):
    out = []
    for i, lg in enumerate(legs):
        fr = base[0:18] + lg
        out.append(lower(fr) if i % 2 == 0 else fr)
    return out


def shift_arm(rows, dx):
    """Move the near arm (cols 7-8 of torso rows 12-16) by dx for a profile swing."""
    fill = ["r", "r", "r", "q", "P"]
    out = []
    for i, row in enumerate(rows):
        row = list(row)
        arm = row[7:9]
        row[7:9] = [fill[i], fill[i]]
        row[7 + dx:9 + dx] = arm
        out.append("".join(row))
    return out


def walk_w():
    """West walk: east's leg poses mirrored; west keeps its own head, light and badge."""
    head, arm = W[0:12], W[12:17]
    hem = "....oOPPPPOo...."
    legs = [[r[::-1] for r in lg] for lg in (LEG_C0, LEG_P1, LEG_C2, LEG_P3)]
    c0 = lower(head + shift_arm(arm, 2) + [hem] + legs[0])
    p1 = head + arm + [hem] + legs[1]
    c2 = lower(head + shift_arm(arm, -2) + [hem] + legs[2])
    p3 = head + arm + [hem] + legs[3]
    return [c0, p1, c2, p3]


IDLE = {f: [fr, lower(fr)] for f, fr in (("s", S), ("n", N), ("e", E), ("w", W))}
WALK = {"s": walk_front_back(S, LEGS_S), "n": walk_front_back(N, LEGS_N), "e": walk_e(), "w": walk_w()}
WALK_E = WALK["e"]
