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


# --- Extra animation sets (tasks 8.1-8.4, candidate) -----------------------------------------
# EXTRA frames are the approved idle frames with hand-placed stamps: each stamp is a small key
# grid pasted at (x, y). A space keeps the pixel underneath, "." clears it. The approved IDLE and
# WALK frames above are never edited. Format: EXTRA[set][key] = [frames]; EXTRA_MS[set] = ms.
def stamp(frame, x, y, art):
    """Paste a key grid onto a frame at column x, row y and return the new frame."""
    out = [list(r) for r in frame]
    for j, line in enumerate(art):
        for i, ch in enumerate(line):
            if ch != " ":
                out[y + j][x + i] = ch
    return ["".join(r) for r in out]


def stamps(frame, *parts):
    """Apply several (x, y, art) stamps in order."""
    for x, y, art in parts:
        frame = stamp(frame, x, y, art)
    return frame


def dip(frame, n=1):
    """Head only (rows 0-9) drops n px onto the shoulders: a nod or a bowed head. Torso and legs stay."""
    out = [list(r) for r in frame]
    for y in range(10):
        out[y] = ["."] * 16
    for y in range(10):
        for x, ch in enumerate(frame[y]):
            if ch != ".":
                out[y + n][x] = ch
    return ["".join(r) for r in out]


def tilt(frame, dx):
    """Head only (rows 0-9) slides dx px sideways over the shoulders: a head tilt. Torso and legs stay."""
    out = [list(r) for r in frame]
    for y in range(10):
        out[y] = ["."] * 16
    for y in range(10):
        for x, ch in enumerate(frame[y]):
            if ch != "." and 0 <= x + dx < 16:
                out[y][x + dx] = ch
    return ["".join(r) for r in out]


# Shared arm stamps for S and N (torso columns are identical there): the near arms flare 1 px out.
FLARE_L = [(1, 12, ["pspr"]), (1, 13, ["pspr"]), (1, 14, ["ospr"])]   # screen-left elbow out
FLARE_R_S = [(13, 12, ["qo"]), (13, 13, ["qo"]), (13, 14, ["qo"])]    # screen-right elbow out (S)
FLARE_R_N = [(11, 12, ["rpqo"]), (11, 13, ["rpqo"]), (11, 14, ["rpqo"])]


def _extra():
    # ---- interact: reach, then hold ------------------------------------------------------------
    # S: the forearms come forward and the hands meet at the belt (terminal, handover).
    s_i0 = stamps(S, (2, 14, ["osprqnmqqpqo"]), (2, 15, ["oqppplmqqpmo"]), (2, 16, [".."]))
    s_i1 = stamps(S, (2, 14, ["osprqnmmqpqo"]), (2, 15, ["oqppplmlqpqo"]), (2, 16, [".."]), (12, 16, [".."]))
    # N: the left arm reaches up past the shoulder (half, then hand beside the head); hand rows <10 are skin.
    n_hand = [(1, 7, ["oo"]), (0, 8, ["onm"]), (0, 9, ["olm"]), (1, 10, ["oss"])]
    n_i0 = stamps(N, *FLARE_L, (3, 15, ["q"]), (2, 16, [".."]), (0, 12, ["onm"]), (0, 13, ["olm"]))
    n_i1 = stamps(N, *n_hand, (3, 15, ["q"]), (2, 16, [".."]))
    # E: the near forearm extends toward the facing, hand half out, then fully out.
    e_i0 = stamps(E, (8, 13, ["rrr"]), (8, 14, ["pppnm"]), (11, 15, ["oo"]), (7, 15, ["qq"]), (7, 16, ["PP"]))
    e_i1 = stamps(E, (12, 12, ["oo "]), (8, 13, ["rrrrnmo"]), (8, 14, ["pppplmo"]), (12, 15, ["ooo"]),
                  (7, 15, ["qq"]), (7, 16, ["PP"]))
    # W: the same toward the left.
    w_i0 = stamps(W, (6, 14, ["mn"]), (3, 14, ["opp"]), (7, 15, ["qq"]), (7, 16, ["PP"]))
    w_i1 = stamps(W, (1, 12, ["oo "]), (0, 13, ["onmsrrr"]), (0, 14, ["olmpppp"]), (0, 15, ["ooo"]),
                  (7, 15, ["qq"]), (7, 16, ["PP"]))
    interact = {"s": [s_i0, s_i1], "n": [n_i0, n_i1], "e": [e_i0, e_i1], "w": [w_i0, w_i1]}

    # ---- reaction: concerned (head bows, hand to the chin; N only bows) ---------------------------
    no_hand_r = [(12, 15, ["q"]), (12, 16, [".."])]
    def fist(x, d):
        """Outlined fist at the chin for a head dipped by d px: 4x3 with a dark rim."""
        y = 9 + d
        return [(x, y, ["onmo"]), (x, y + 1, ["olmo"]), (x + 1, y + 2, ["oo"])]
    s_c0 = stamps(dip(S), *FLARE_R_S, *no_hand_r)
    s_c1 = stamps(dip(S), *FLARE_R_S, *no_hand_r, *fist(9, 1))
    s_c2 = lower(stamps(dip(S), *FLARE_R_S, *no_hand_r, *fist(9, 1)))
    gone = [(7, 15, ["qq"]), (7, 16, ["PP"])]
    e_c0 = stamps(dip(E), *gone)
    e_c1 = stamps(dip(E), *gone, *fist(10, 1))
    e_c2 = lower(stamps(dip(E), *gone, *fist(10, 1)))
    w_c0 = stamps(dip(W), *gone)
    w_c1 = stamps(dip(W), *gone, *fist(3, 1))
    w_c2 = lower(stamps(dip(W), *gone, *fist(3, 1)))
    concerned = {"s": [s_c0, s_c1, s_c2], "n": [dip(N), lower(dip(N))],
                 "e": [e_c0, e_c1, e_c2], "w": [w_c0, w_c1, w_c2]}

    # ---- reaction: satisfied (hands on hips, then a fist pump; the pump settles with a breath) ------
    s_ak = stamps(S, *FLARE_L, *FLARE_R_S)
    s_fist = stamps(S, (13, 7, ["oo"]), (13, 8, ["nmo"]), (12, 9, [".lmo"]), (12, 10, ["qqpo"]),
                    (13, 11, ["qpo"]), (13, 12, ["po"]), (12, 15, ["q"]), (12, 16, [".."]))
    n_ak = stamps(N, *FLARE_L, *FLARE_R_N)
    e_fist = stamps(E, (13, 9, ["o"]), (12, 10, ["nmo"]), (12, 11, ["lmo"]), (9, 12, ["pppoo"]),
                    *gone)
    w_fist = stamps(W, (2, 9, ["o"]), (1, 10, ["onm"]), (1, 11, ["olm"]), (1, 12, ["oopp"]),
                    *gone)
    satisfied = {"s": [s_ak, s_fist, lower(s_fist)], "n": [n_ak, lower(n_ak), n_ak],
                 "e": [E, e_fist, lower(e_fist)], "w": [W, w_fist, lower(w_fist)]}

    # ---- quick turn: one in-between frame per adjacent pair, the head leads -------------------------
    turn = {"se": [E[:10] + S[10:]], "en": [N[:10] + E[10:]], "nw": [W[:10] + N[10:]], "ws": [S[:10] + W[10:]]}
    return {"interact": interact, "react_concerned": concerned, "react_satisfied": satisfied, "turn": turn}


EXTRA = _extra()
EXTRA_MS = {"interact": 250, "react_concerned": 300, "react_satisfied": 300, "turn": 60}
EXTRA_ASYMMETRIC = {"interact", "react_satisfied"}
