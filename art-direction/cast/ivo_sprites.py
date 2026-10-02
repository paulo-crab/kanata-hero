"""Ivo (Orientation reception lead) frames, hand-placed at 16x24 logical px.

Status: APPROVED by the player 2026-10-02. Built on the person rules approved at Gate 1
(art-direction/gate1/GATE1_ENGINEER_SPEC.md): same frame, anchor, timing,
contour-only darkest step, and renderer-drawn shadow. Spec: IVO_SPEC.md.
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "gate1"))
import engineer_sprites as eng  # noqa: E402  (shared walk legs and lower())

PAL = {
    ".": None,
    "o": "#0E1020",
    # hair, silver: fill D C B, A only on contour
    "A": "#535971", "B": "#8C8F9C", "C": "#BFC0C6", "D": "#E6E4E0",
    # skin: fill n m l, k only on contour
    "k": "#8A5A4A", "l": "#C08870", "m": "#E3B094", "n": "#F6D2B8",
    # cardigan (wood/terracotta): fill s r q, p on contour
    "p": "#523D4C", "q": "#85565A", "r": "#BA785F", "s": "#E4AA73",
    # shirt strip (ochre)
    "x": "#9A6A3E", "y": "#C99A4E", "z": "#EDCB7A",
    # trousers (navy)
    "O": "#2C3352", "P": "#3E4870",
    # shoes (ink ramp)
    "S": "#1C2038", "T": "#3A4160", "U": "#6A7392",
    # tablet face: blue glass, never #19AFA2, lightest step on 1 px only; back is ink (S T)
    "g": "#203A50", "h": "#366479", "j": "#5AA3AE", "J": "#A0DDD4",
}

SLOTS = {"hair": "ABCD", "skin": "klmn", "jacket": "pqrs", "trousers": "OP"}

S = [
    "................",
    "......ooooo.....",
    "....ooCDDCCo....",
    "...oCDDCCBCBo...",
    "...oCCBCCBCBo...",
    "...oBCCBBCBBo...",
    "...oBkkkAkkBo...",
    "...oknommomko...",
    "...oknmmmmmko...",
    "....okllllko....",
    "..osssryzrrqqo..",
    ".osrrrryyrrrqqo.",
    ".psrrrpxygggggo.",
    ".psrrrpxygJjjgo.",
    ".psqrrpxygjhjgo.",
    ".opqqrqqqmggggo.",
    ".omqqqqqqqqqmmo.",
    "..opqqqqqqqqpo..",
    "....oOPPoPPOo...",
    "....oOPPoPPOo...",
    "....oOPPoPPOo...",
    "...oTUUToTUUTo..",
    "...oSTTSoSTTSo..",
    "....oooo.oooo...",
]

N = [
    "................",
    "......ooooo.....",
    "....ooCDDCCo....",
    "...oCDDCCBCBo...",
    "...oCCBCCBCBo...",
    "...oBCCBCBBBo...",
    "...oBBCBBBBBo...",
    "...okBBBBBBko...",
    "...okkAAAAkko...",
    "....okllllko....",
    "..osssrrrrrqqo..",
    ".osrrrrrrrrrqqo.",
    ".psrrrrqrrrqqqo.",
    ".oSSSrrqrrrqqqo.",
    ".oSTSrrqrrqqqqo.",
    ".oSSSqqqqqqqqpo.",
    ".ommqqqqqqqqqmo.",
    "..opqqqqqqqqpo..",
    "....oOPPoPPOo...",
    "....oOPPoPPOo...",
    "....oOPPoPPOo...",
    "...oSTTSoSTTSo..",
    "...oSSSSoSSSSo..",
    "....oooo.oooo...",
]

E = [
    "................",
    ".....ooooo......",
    "....ooCDDCo.....",
    "...oCDDCCBCo....",
    "...oCCBCCBCBo...",
    "...oBCCBBCBAo...",
    "...oBBCBkkkko...",
    "...oBBAkmnomo...",
    "...oBAkmmmmmo...",
    "....oAklmmko....",
    "...ossrrryzqo...",
    "..osrrrrrxyqqo..",
    "..psrrrrrxggggg.",
    "..psrqrrrxgJjjg.",
    "..osqqrrrqgjhjg.",
    "..opqqmmqqmgggg.",
    "...opqlmqqqpo...",
    "...opqqqqqqpo...",
    "....oOPPPPOo....",
    "....oOPPoPPo....",
    "....oOPPoPPo....",
    "...oTUToTUUTo...",
    "...oSTSoSTTTSo..",
    "....ooo.ooooo...",
]

W = [
    "................",
    "......ooooo.....",
    ".....oCDDCoo....",
    "....oCDDCCBCo...",
    "...oCDCCBCCBo...",
    "...oACBCCBBBo...",
    "...okkkkBCBBo...",
    "...omonkABBBo...",
    "...ommmmkABBo...",
    "....okmmlkAo....",
    "...oyzsrrrrqo...",
    "..oxysrrrrrqqo..",
    ".gggggrrrrrqqo..",
    ".gJjjgrrqrrqqo..",
    ".gjhjgrrqrqqpo..",
    ".ggggmqqqqqqpo..",
    "...oqqqqqqqpo...",
    "...opqqqqqqpo...",
    "....oOPPPPOo....",
    "....oPPoPPOo....",
    "....oPPoPPOo....",
    "...oTUUToTUTo...",
    "..oSTTTSoSTSo...",
    "...ooooo.ooo....",
]


def lower(frame):
    """1 px settle that keeps Ivo's hem row (17): the top leg row is dropped instead."""
    return ["." * 16] + frame[0:18] + frame[19:24]


HAIR_SKIN_SEPARATED = True  # silver hair matches skin luminance: never let them touch


def walk(base, legs):
    """Ivo keeps the tablet still, so motion is legs plus the shared 1 px contact bob."""
    out = []
    for i, lg in enumerate(legs):
        fr = base[0:18] + lg
        out.append(lower(fr) if i % 2 == 0 else fr)
    return out


SIDE_LEGS = (eng.LEG_C0, eng.LEG_P1, eng.LEG_C2, eng.LEG_P3)
IDLE = {f: [fr, lower(fr)] for f, fr in (("s", S), ("n", N), ("e", E), ("w", W))}
WALK = {
    "s": walk(S, eng.LEGS_S),
    "n": walk(N, eng.LEGS_N),
    "e": walk(E, SIDE_LEGS),
    "w": walk(W, [[r[::-1] for r in lg] for lg in SIDE_LEGS]),
}


# --- Extra animation sets (tasks 8.1-8.3, approved 2026-10-02) ----------------------------------------------
# Same format as the Engineer's (engineer_sprites.EXTRA): the approved idle frames plus hand-placed
# stamps. IDLE and WALK above are never edited.
stamp, stamps, dip, tilt = eng.stamp, eng.stamps, eng.dip, eng.tilt

TAB5 = ["ggggg", "gJjjg", "gjhjg", "ggggg"]                                   # the approved 5x4 tablet
TAB6 = ["gggggg", "gJjjjg", "gjhhjg", "gjjjjg", "gggggg"]                      # nearer to the player: 6x5
BACK5 = ["SSSSS", "STTTS", "STTTS", "SSSSS"]                                   # N: the back, enlarged
FLASH_BRIGHT = str.maketrans({"j": "J", "h": "j"})   # screen up 1-2 steps, content mark stays darker
FLASH_DIM = str.maketrans({"J": "h", "j": "h", "h": "g"})


def lift(frame):
    """Head tipped back: it rises 1 px on a stretched neck (the chin row repeats). Torso and legs stay."""
    return frame[1:10] + [frame[9]] + frame[10:]


def flash(frame, table):
    """Recolour only the tablet glass (keys g h j J are used nowhere else on Ivo)."""
    return [row.translate(table) for row in frame]


def _extra():
    s0, n0, e0, w0 = S, N, E, W
    # ---- 8.1 interact: the tablet is raised, then held out toward the player (it grows: it is nearer) ----
    s_i0 = stamps(s0, (9, 15, ["qqqqq"]), (9, 11, TAB5), (9, 14, ["m"]))
    s_i1 = stamps(s0, (9, 11, TAB6), (15, 11, ["o", "o", "o", "o", "o"]), (8, 15, ["m"]))
    e_i0 = stamps(e0, (10, 15, ["qqo.."]), (10, 11, TAB5), (10, 14, ["m"]))
    e_i1 = stamps(e0, (10, 11, TAB6), (9, 15, ["m"]))
    w_i0 = stamps(w0, (1, 15, ["..oqq"]), (1, 11, TAB5), (5, 14, ["m"]))
    w_i1 = stamps(w0, (0, 11, TAB6), (6, 15, ["m"]))
    n_i0 = stamps(n0, (2, 15, ["qqq"]), (2, 12, ["SSS", "STS", "SSS"]), (1, 12, ["o"]))
    n_i1 = stamps(n0, (2, 15, ["qqq"]), (1, 11, BACK5), (0, 11, ["o", "o", "o", "o"]))
    interact = {"s": [s_i0, s_i1], "n": [n_i0, n_i1], "e": [e_i0, e_i1], "w": [w_i0, w_i1]}

    # ---- 8.3 scripted wave (free hand beside the head; hand rows <10 are skin only) ----------------------
    raise_arm = [(0, 10, ["oqs"]), (2, 16, ["q"])]
    wave0 = stamps(s0, *raise_arm, (0, 10, ["oqs"]), (1, 9, ["lm"]))
    wave_a = stamps(s0, *raise_arm, (1, 6, ["oo"]), (0, 7, ["onm"]), (0, 8, ["olm"]), (0, 9, ["olm"]))
    wave_b = stamps(s0, *raise_arm, (0, 5, ["oo"]), (0, 6, ["onm"]), (0, 7, ["olm"]), (1, 8, ["lm"]), (1, 9, ["lm"]))
    wave = {"s": [wave0, wave_a, wave_b]}

    # ---- 8.3 nod: the head bows onto the shoulders and returns ---------------------------------------------
    nod = {f: [dip(g), dip(g, 2), dip(g)] for f, g in (("s", s0), ("n", n0), ("e", e0), ("w", w0))}

    # ---- 8.3 unscripted laugh: shoulders heave (head thrown back, then bent forward) -----------------------
    belly = [(4, 15, ["nm"]), (4, 16, ["lm"])]
    # Closed eyes: a 2 px wide horizontal ink line per eye (S) or per profile eye (E, W). The skin and
    # hair-shadow steps (k, A) were tried and vanish at 1x, so ink is used; the lines are 2 px wide, so
    # they read as a squint, not as the open 1 px dot eyes.
    sq = {"s": [(5, 7, ["oo"]), (9, 7, ["oo"])], "e": [(9, 7, ["oo"])], "w": [(5, 7, ["oo"])], "n": []}
    base = {"s": stamps(s0, *sq["s"], *belly), "n": n0, "e": stamps(e0, *sq["e"]), "w": stamps(w0, *sq["w"])}

    def laugh_set(g):
        # 4 phases against fixed feet: head tipped back / torso up, level / down, back / down, level / up.
        return [lift(g), lower(g), g[:10] + [g[9]] + lower(g)[11:], g]
    laugh = {f: laugh_set(g) for f, g in base.items()}

    # ---- 8.3 Level 03 tablet flash: glass steps only, a hard 1-2 step glow, no halo, no marker hex ---------
    tab_flash = {f: [flash(g, FLASH_BRIGHT), flash(g, FLASH_DIM)] for f, g in (("s", s0), ("e", e0), ("w", w0))}

    # ---- 8.2 reactions ---------------------------------------------------------------------------------------
    def fist(x, d):
        y = 9 + d
        return [(x, y, ["onmo"]), (x, y + 1, ["olmo"]), (x + 1, y + 2, ["oo"])]
    gone = [(2, 15, ["q"]), (2, 16, ["q"])]
    quest = {
        "s": [dip(s0), stamps(dip(s0), *gone, *fist(4, 1)), lower(stamps(dip(s0), *gone, *fist(4, 1)))],
        "n": [dip(n0), lower(dip(n0))],
        "e": [dip(e0), stamps(dip(e0), *fist(8, 1)), lower(stamps(dip(e0), *fist(8, 1)))],
        "w": [dip(w0), stamps(dip(w0), *fist(3, 1)), lower(stamps(dip(w0), *fist(3, 1)))],
    }
    relieved = {f: [lower(g), lower(dip(g)), lower(g)] for f, g in (("s", s0), ("n", n0), ("e", e0), ("w", w0))}
    return {"interact": interact, "wave": wave, "nod": nod, "laugh": laugh, "tablet_flash": tab_flash,
            "react_questioning": quest, "react_relieved": relieved}


EXTRA = _extra()
EXTRA_MS = {"interact": 250, "wave": 250, "nod": 140, "laugh": 160, "tablet_flash": 350,
            "react_questioning": 300, "react_relieved": 300}
EXTRA_MODE = {"wave": "loop", "laugh": "loop", "tablet_flash": "loop"}
EXTRA_ASYMMETRIC = {"interact", "wave", "react_questioning"}
