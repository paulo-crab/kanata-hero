"""Vale (executive liaison) frames, hand-placed at 16x24 logical px.

Status: Approved by the director 2026-10-02. Built on the person rules approved at Gate 1
(art-direction/gate1/GATE1_ENGINEER_SPEC.md) and the cast frame rule (cast/IVO_SPEC.md).
Spec: VALE_SPEC.md. This is softening state 0 (0 repairs): rigid, square shoulders, arms tight,
feet together. Later states (shoulders drop, arms relax, asymmetric stance) are EXTRA sets.
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "gate1"))
sys.path.insert(0, os.path.join(HERE, "..", "palettes"))
import engineer_sprites as eng  # noqa: E402  (shared walk legs)
import district_palettes as dp  # noqa: E402  (CAST_RAMPS, DISTRICTS)

_R = dp.CAST_RAMPS["vale"]
_X = dp.DISTRICTS["executive"]

PAL = {
    ".": None,
    "o": "#202337",
    # hair, dark graphite (CAST_RAMPS): fill D C B, A only on contour
    **dict(zip("ABCD", _R["hair"])),
    # skin, pale ivory (CAST_RAMPS): fill n m l, k only on contour / forehead shadow
    **dict(zip("klmn", _R["skin"])),
    # suit, desaturated ink navy (22-29 % saturation, against the Executive wall's 38-47 %):
    # fill r q, s only as a 1-px lit edge on the upper-left, p on contour and seams
    "p": "#262B46", "q": "#3C4465", "r": "#566089", "s": "#9AA6C8",
    # shirt (cool white, apart from the warm ivory skin): fill x w, y lit collar tip
    "w": "#A9B0C6", "x": "#DDE2EC", "y": "#F4F2EC",
    # tie (living green, Executive foliage ramp): t shade, u fill, v lit knot on 1 px
    "t": _X["foliage"][0], "u": _X["foliage"][1], "v": _X["foliage"][2],
    # copper badge (Executive accent ramp): b frame, c face, d lit face, e glint on 1 px
    "b": _X["accent"][0], "c": _X["accent"][1], "d": _X["accent"][2], "e": _X["accent"][3],
    # trousers (suit navy, a step darker than the jacket)
    "O": "#2A2F4C", "P": "#3A4162",
    # shoes (walnut, Executive wood ramp)
    "S": _X["wood"][0], "T": _X["wood"][1], "U": _X["wood"][2],
}

SLOTS = {"hair": "ABCD", "skin": "klmn", "jacket": "pqrs", "trousers": "OP"}
GLINT_LIMITS = {"e": 1, "v": 1, "y": 3}  # enforced by check_gate1.py
HAIR_SKIN_SEPARATED = False  # graphite hair is 29 L* darker than the skin: no equal-luminance contact

S = [
    "........oo......",
    ".....oooDDoo....",
    "....oDDDDCCCoo..",
    "...oDDDkCCDCBo..",
    "...oDDkCCBCBBo..",
    "...oCCBBCBBBo...",
    "...okkBAkkkBo...",
    "...oknommomko...",
    "...oknmllmmko...",
    "....oklmmlko....",
    ".osssswxxwrrrro.",
    ".osrprwxywqpqqo.",
    ".osrprxvuwqpqqo.",
    ".orrprputedpqqo.",
    ".orrpqputdcpqqo.",
    ".oxwpqqutbbpwwo.",
    ".onmpqqrpqqpmlo.",
    "..oprqqqpqqqpo..",
    "....oOPPoPPOo...",
    "....oOPPoPPOo...",
    "....oOPPoPPOo...",
    "...oTUUToTUUTo..",
    "...oSTTSoSTTSo..",
    "....oooo.oooo...",
]

N = [
    "......oo........",
    "....ooDDooo.....",
    "..ooDDDDCCCo....",
    "..oDDDBCCDCBo...",
    "..oDDBCCBCBBo...",
    "...oCCBBCBBBo...",
    "...oCBBBBBBBo...",
    "...olBBBBBBlo...",
    "....olBAABlo....",
    "....oklmmlko....",
    ".osssswxxwrrrro.",
    ".osrprqqqqqpqqo.",
    ".osrprqpqqqpqqo.",
    ".osrprqpqqqpqqo.",
    ".osrprqpqqqpqqo.",
    ".oxwprqqqqqpwwo.",
    ".onmprqqqqqpmlo.",
    "..oprrqpqqqqpo..",
    "....oOPPoPPOo...",
    "....oOPPoPPOo...",
    "....oOPPoPPOo...",
    "...oSTTSoSTTSo..",
    "...oSSSSoSSSSo..",
    "....oooo.oooo...",
]

E = [
    "........oo......",
    ".....oooDDoo....",
    "....oDDDDCCCo...",
    "...oDDDCCCCCCo..",
    "...oDCCBCCCBBo..",
    "...oCCBBCBBBBo..",
    "...oBCBBkkkko...",
    "...oBBAkmnomo...",
    "...oBAkmmmllo...",
    "....oAklmmko....",
    "...ossswxxrro...",
    "...osrqqqpyxo...",
    "...osrqqqpvuo...",
    "...orrqqqpudo...",
    "...orqqqqptbo...",
    "...oqxwwwpqqo...",
    "...oqqnmrpqqo...",
    "...opqqqqqqpo...",
    "....oOPPPPOo....",
    "....oOPPoPPo....",
    "....oOPPoPPo....",
    "...oTUToTUUTo...",
    "...oSTSoSTTTSo..",
    "....ooo.ooooo...",
]

W = [
    "......oo........",
    "....ooDDooo.....",
    "...oDDDDCCCo....",
    "..oDDDCCCCCCo...",
    "..oDCCBCCCBBo...",
    "..oCCBBCBBBBo...",
    "...okkkkBCBBo...",
    "...omonmkBBAo...",
    "...ollmmmkBAo...",
    "....okmmlkAo....",
    "...ossxxwrrro...",
    "...oyxprqqqqo...",
    "...ovuprqqqqo...",
    "...oedprqqqqo...",
    "...odcprqqqqo...",
    "...obbpwwwxqo...",
    "...oqqprnmrqo...",
    "...opqqqqqqpo...",
    "....oOPPPPOo....",
    "....oPPoPPOo....",
    "....oPPoPPOo....",
    "...oTUUToTUTo...",
    "..oSTTTSoSTSo...",
    "...ooooo.ooo....",
]


def lower(frame):
    """1 px settle that keeps the jacket hem (row 17): the top leg row is dropped instead
    (eng.lower would drop the hem and bring the hands onto the trousers)."""
    return ["." * 16] + frame[0:18] + frame[19:24]


def walk(base, legs):
    """Rigid walk: neither arm swings. Motion is the legs plus the shared 1 px contact bob."""
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


# --- Extra animation sets (tasks 8.1-8.2, approved 2026-10-02) ----------------------------------------------
# Same format as the Engineer's (engineer_sprites.EXTRA): the approved idle frames plus hand-placed
# stamps. IDLE and WALK above are never edited. Vale stays stiff: arms stay at the sides except where
# a set needs them, and the head moves in whole 1 px steps.
stamp, stamps, dip, tilt = eng.stamp, eng.stamps, eng.dip, eng.tilt

# The audit: a pale sheet with a dark rim and one copper clip (the Executive copper, never the marker).
AUDIT5 = ["oocoo", "owwwo", "oxxxo", "ooooo"]                       # 5x4, held low: copper clip, text line
AUDIT6 = ["oocooo", "owwwwo", "oxxxxo", "owwwwo", "oooooo"]          # 6x5, held out: nearer the player
AUDIT_BACK = ["oooo", "owwo", "owwo", "oooo"]                        # N: the back of the sheet


def sag(frame):
    """First softening step: the shoulders drop 1 px. The hard top corners of row 10 are cut, so the
    shoulder line steps down to a chamfer. Torso and legs stay put."""
    row = list(frame[10])
    cols = [i for i, ch in enumerate(row) if ch != "."]
    a, b = cols[0], cols[-1]
    row[a], row[b] = ".", "."
    row[a + 1], row[b - 1] = "o", "o"
    return frame[:10] + ["".join(row)] + frame[11:]


# Facial stamps per facing: (level brow, mouth corners). Eyes are the sprite's single ink pixels, so the
# stern look is a brow pixel on the forehead row above them and mouth corners that drop onto the chin.
FROWN = {"s": [(6, 9, ["B"]), (9, 6, ["k"]), (9, 9, ["k"])],
         "e": [(6, 9, ["BB"]), (9, 9, ["k"])],
         "w": [(6, 5, ["BB"]), (9, 6, ["k"])]}


def _extra():
    s0, n0, e0, w0 = S, N, E, W
    # ---- 8.1 interact: offering or receiving the audit (reach, then hold it out; it grows: it is nearer) ----
    # S: the sheet is carried at the wearer's right (screen-left), the hand grips its lower edge.
    s_i0 = stamps(s0, (0, 12, AUDIT5), (2, 16, ["nm"]))
    s_i1 = stamps(s0, (0, 11, AUDIT6), (1, 16, ["nm"]), (0, 16, ["o"]))
    # E: held out toward the facing, hand beside it.
    e_i0 = stamps(e0, (11, 12, AUDIT5), (10, 16, ["n"]))
    e_i1 = stamps(e0, (10, 11, AUDIT6), (9, 16, ["nm"]))
    # W: the same toward the left.
    w_i0 = stamps(w0, (0, 12, AUDIT5), (5, 16, ["n"]))
    w_i1 = stamps(w0, (0, 11, AUDIT6), (6, 16, ["nm"]))
    # N: the back of the sheet shows past the shoulder.
    n_i0 = stamps(n0, (0, 12, AUDIT_BACK))
    n_i1 = stamps(n0, (0, 11, AUDIT_BACK), (0, 15, ["oooo"]))
    interact = {"s": [s_i0, s_i1], "n": [n_i0, n_i1], "e": [e_i0, e_i1], "w": [w_i0, w_i1]}

    # ---- 8.2 reaction: displeased (stiff). The head bows a notch, the brow furrows and the corners of the
    # mouth drop; then the fists clench (hands darken to the skin shadow) and the whole figure holds. ---------
    def fists(f):
        return stamps(f, (2, 16, ["lk"]), (12, 16, ["kl"]))
    displeased = {}
    for fac, g in (("s", s0), ("e", e0), ("w", w0)):
        d0 = stamps(g, *FROWN[fac])
        d1 = dip(d0)
        d2 = lower(fists(d1)) if fac == "s" else lower(d1)
        displeased[fac] = [d0, d1, d2]
    displeased["n"] = [n0, dip(n0), lower(dip(n0))]

    # ---- 8.2 reaction: reconsidering (the first softening). The head tilts a notch, then the shoulders drop 1 px
    # and it settles: the softened silhouette of repair 1. -------------------------------------------------------
    reconsider = {}
    for fac, g, dx in (("s", s0, -1), ("n", n0, 1), ("e", e0, -1), ("w", w0, 1)):
        r0 = tilt(g, dx)
        r1 = sag(r0)
        r2 = lower(sag(g))
        reconsider[fac] = [r0, r1, r2]
    return {"interact": interact, "react_displeased": displeased, "react_reconsidering": reconsider}


EXTRA = _extra()
EXTRA_MS = {"interact": 250, "react_displeased": 300, "react_reconsidering": 300}
EXTRA_ASYMMETRIC = {"interact"}
EXTRA_MODE = {"interact": "once", "react_displeased": "once", "react_reconsidering": "once"}  # play, then hold the last frame
