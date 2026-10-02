"""Vale (executive liaison) frames, hand-placed at 16x24 logical px.

Status: Approved by the director 2026-10-02. Built on the person rules approved at Gate 1
(art-direction/gate1/GATE1_ENGINEER_SPEC.md) and the cast frame rule (cast/IVO_SPEC.md).
Spec: VALE_SPEC.md. This is softening state 0 (0 repairs): rigid, square shoulders, arms tight,
feet together. States 1-3 (shoulders drop, arms relax, open asymmetric stance) are EXTRA sets
`s1_*`..`s3_*`, derived from these frames (see "Softening states" below and VALE_SPEC.md).
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
    "o": "#0E1020",
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
    """First softening step: the shoulders drop 1 px. The outer part of the hard shoulder line (row 10) is
    taken off: 3 px per side on S and N (the 14 px suit line), 2 px per side on E and W (the 10 px profile),
    so the line now starts at the neck's width and steps down onto row 11. Torso and legs stay put."""
    row = frame[10]
    cols = [i for i, ch in enumerate(row) if ch != "."]
    a, b = cols[0], cols[-1]
    n = 3 if a == 1 else 2
    r = list(row)
    for i in range(a, a + n):
        r[i] = "."
    for i in range(b - n + 1, b + 1):
        r[i] = "."
    r[a + n], r[b - n] = "o", "o"
    return frame[:10] + ["".join(r)] + frame[11:]


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


# --- Softening states 1-3 (idle, walk and interact for every facing) -----------------------------------------
# vale.md: four states that follow the NUMBER of repairs completed (the player picks the branch order). State 0
# is the approved IDLE/WALK above. Each state k = 1..3 is derived from the approved frames by the transforms
# below, so the identity (suit, badge, tie, hair, head rows) never forks. Every facing has its own idle (2),
# walk (4) and interact (2) so the renderer swaps whole animation sets by state: `vale_s<k>_<set>_<facing>`.
#   1  shoulders drop 1 px (`sag`: the outer shoulder line comes off row 10; identical to the end of
#        react_reconsidering)
#   2  + right shoulder lower, forearms angle away from the torso, weight on one leg (S/N: the far foot rests
#        back and out; E/W: the front foot steps forward), the near hand drifts forward in profile
#   3  + both shoulders slope in a round line (no corners left), arms open from the elbow (rows 13-16), the
#        stance opens (feet apart, one knee out), the head leans, the collar opens and the knot drops
# Walk stiffness eases: state 0-1 swing nothing, state 2 swings one arm 1 px, state 3 swings both arms and the
# head sways on the contact frames. Asymmetric poses mirror between S (screen-right is Vale's left) and N.
def _set(fr, y, row):
    assert len(row) == 16, (y, row)
    return fr[:y] + [row] + fr[y + 1:]


def _put(fr, y, x, s):
    return _set(fr, y, fr[y][:x] + s + fr[y][x + len(s):])


def _mirror(rows):
    return [r[::-1] for r in rows]


def shoulder_slope(fr, side):
    """Second shoulder step (state 2): one shoulder (S: screen-right, Vale's left; N: screen-left) rounds off
    on row 11 as well, so it sits a row lower than the other. S/N only."""
    r11 = fr[11]
    if side == "r":
        return _set(fr, 11, r11[0:12] + "q" + "o" + "..")
    return _set(fr, 11, "..os" + "r" + r11[5:])


def round_shoulders(fr):
    """Third shoulder step (state 3): both corners round off on row 11 (neck -> row 10 -> row 11 -> sleeve),
    so no hard corner is left in the shoulder line. S/N only."""
    r11 = fr[11]
    return _set(fr, 11, "..os" + "r" + r11[5:12] + "q" + "o" + "..")


def arms_out(fr, left=True, right=True, rows=(14, 15, 16)):
    """S/N: the forearms angle 1 px away from the torso (an outline line separates arm and body)."""
    out = list(fr)
    for y in rows:
        r = list(out[y])
        if left:
            r[0:3], r[3] = r[1:4], "o"
        if right:
            r[13:16], r[12] = r[12:15], "o"
        out[y] = "".join(r)
    return out


# Standing legs (rows 18-23) per state. S: weight on the screen-left leg; the screen-right foot rests out.
LEGS_STAND = {
    ("s", 2): ["....oOPPoPPOo...", "....oOPPoPPOo...", "....oOPPoOPPOo..",
               "...oTUUTooTUUTo.", "...oSTTSo.oSTTSo", "....oooo...oooo."],
    ("s", 3): ["....oOPPoPPOo...", "....oOPPoPPOo...", "....oOPPoOPPOo..",
               "...oTUUTo.oTUUTo", "...oSTTSo.oSTTSo", "....oooo...oooo."],
    # E: weight on the back leg, the front foot steps forward (2 px at state 2, 3 px at state 3)
    ("e", 2): ["....oOPPPPOo....", "....oOPPoPPo....", "....oOPPooPPo...",
               "...oTUTo.oTUUTo.", "...oSTSo.oSTTTSo", "....ooo...ooooo."],
    ("e", 3): ["....oOPPPPOo....", "....oOPPoPPo....", "....oOPPo.oPPo..",
               "...oTUTo..oTUUTo", "...oSTSo..oSTTTS", "....ooo....oooo."],
}
LEGS_STAND[("n", 2)] = [r.translate(eng.HEEL) for r in _mirror(LEGS_STAND[("s", 2)])]
LEGS_STAND[("n", 3)] = [r.translate(eng.HEEL) for r in _mirror(LEGS_STAND[("s", 3)])]
LEGS_STAND[("w", 2)] = _mirror(LEGS_STAND[("e", 2)])
LEGS_STAND[("w", 3)] = _mirror(LEGS_STAND[("e", 3)])

# Near-hand cluster in profile (cuff row 15 + hand row 16): columns of the cuff by facing.
CUFF = {"e": (5, 8), "w": (7, 10)}


def hand_shift(fr, facing, dx):
    """E/W: move the cuff and hand cluster dx px forward (E: right, W: left) with the jacket fill behind it."""
    if dx == 0:
        return fr
    sgn = 1 if facing == "e" else -1
    if facing == "w":
        dx = min(dx, 1)   # further forward the cuff would cover the badge
    a, b = CUFF[facing]
    out = list(fr)
    for y in (15, 16):
        r = list(out[y])
        seg = r[a:b + 1]
        for i in range(a, b + 1):
            r[i] = "q"
        for i, ch in enumerate(seg):
            r[a + i + sgn * dx] = ch
        out[y] = "".join(r)
    return out


def loosen_collar(fr, facing):
    """State 3: the top button is open and the knot has slipped: shirt shows where the knot sat."""
    if facing == "s":
        fr = _put(fr, 12, 6, "xxxw")
        return _put(fr, 13, 7, "vu")
    if facing == "e":
        fr = _put(fr, 12, 10, "xw")
        return _put(fr, 13, 10, "vd")
    if facing == "w":
        return _put(fr, 12, 4, "xx")
    return fr


def state_body(k, facing, arms=None, hand=None, tiltdx=0):
    """The upper body (rows 0-17) of state k for a facing, before legs. `arms` = (left, right, rows) overrides
    the standing arm pose for S/N; `hand` overrides the forward hand offset for E/W; `tiltdx` the head lean."""
    base = {"s": S, "n": N, "e": E, "w": W}[facing]
    f = base
    if k >= 1:
        f = sag(f)
    if facing in "sn":
        if k == 2:
            f = shoulder_slope(f, "r" if facing == "s" else "l")
        if k == 3:
            f = round_shoulders(f)
        if arms is None:
            arms = (k >= 2, k >= 2, (14, 15, 16) if k == 2 else (13, 14, 15, 16))
        if arms[0] or arms[1]:
            f = arms_out(f, arms[0], arms[1], arms[2])
    else:
        if hand is None:
            hand = {0: 0, 1: 0, 2: 1, 3: 2}[k]
        f = hand_shift(f, facing, hand)
    if k >= 3:
        f = loosen_collar(f, facing)
    if tiltdx:
        f = tilt(f, tiltdx)
    return f[:18]


LEAN = {3: {"s": 1, "n": -1, "e": 1, "w": -1}}


def stand(k, facing):
    """The resting pose of state k (the `IDLE` frame 0 equivalent)."""
    if k == 0:
        return {"s": S, "n": N, "e": E, "w": W}[facing]
    body = state_body(k, facing, tiltdx=LEAN.get(k, {}).get(facing, 0))
    if k == 1:
        return body + {"s": S, "n": N, "e": E, "w": W}[facing][18:]
    return body + LEGS_STAND[(facing, k)]


def state_idle(k):
    return {f: [stand(k, f), lower(stand(k, f))] for f in "snew"}


# Walk: legs are the shared cycles; the upper body comes from the state (arms, hand and head are set per frame).
WALK_LEGS = {"s": eng.LEGS_S, "n": eng.LEGS_N, "e": SIDE_LEGS,
             "w": [[r[::-1] for r in lg] for lg in SIDE_LEGS]}


def walk_frame(k, facing, i):
    """Walk frame i (0 and 2 contact, 1 and 3 passing) of state k. Contacts are settled 1 px (`lower`)."""
    contact = i % 2 == 0
    left_fwd = i == 0   # S/N contact 0: screen-left foot forward, so the screen-right arm swings
    arms = hand = None
    tiltdx = 0
    if facing in "sn":
        if k <= 1:
            arms = (False, False, ())
        elif k == 2:
            arms = (not left_fwd, left_fwd, (14, 15, 16)) if contact else (False, False, ())
        else:
            arms = (not left_fwd, left_fwd, (13, 14, 15, 16)) if contact else (True, True, (14, 15, 16))
            if contact:
                tiltdx = (1 if left_fwd else -1) * (1 if facing == "s" else -1)
    else:
        hand = {0: 0, 1: 0, 2: (-1, 0, 1, 0)[i], 3: (-1, 1, 2, 1)[i]}[k]
        if k == 3 and contact:
            tiltdx = (-1 if i == 0 else 1) * (1 if facing == "e" else -1)
    base = state_body(k, facing, arms=arms, hand=hand, tiltdx=tiltdx)
    fr = base + WALK_LEGS[facing][i]
    return lower(fr) if contact else fr


def state_walk(k):
    return {f: [walk_frame(k, f, i) for i in range(4)] for f in "snew"}


def state_interact(k):
    """The audit hand-over on the state's own frames (same stamps as state 0; the sheet covers the arm area)."""
    s0, n0, e0, w0 = (stand(k, f) for f in "snew")
    out = _extra_interact(s0, n0, e0, w0)
    return out


def _extra_interact(s0, n0, e0, w0):
    return {
        "s": [stamps(s0, (0, 12, AUDIT5)), stamps(s0, (0, 11, AUDIT6))],
        "n": [stamps(n0, (0, 12, AUDIT_BACK)), stamps(n0, (0, 11, AUDIT_BACK), (0, 15, ["oooo"]))],
        "e": [stamps(e0, (11, 12, AUDIT5), (10, 16, ["n"])), stamps(e0, (10, 11, AUDIT6), (9, 16, ["nm"]))],
        "w": [stamps(w0, (0, 12, AUDIT5), (5, 16, ["n"])), stamps(w0, (0, 11, AUDIT6), (6, 16, ["nm"]))],
    }


def _states():
    sets = {}
    for k in (1, 2, 3):
        sets[f"s{k}_idle"] = state_idle(k)
        sets[f"s{k}_walk"] = state_walk(k)
        sets[f"s{k}_interact"] = state_interact(k)
    return sets


EXTRA = _extra()
EXTRA.update(_states())
EXTRA_MS = {"interact": 250, "react_displeased": 300, "react_reconsidering": 300}
EXTRA_ASYMMETRIC = {"interact"}
EXTRA_MODE = {"interact": "once", "react_displeased": "once", "react_reconsidering": "once"}  # play, then hold the last frame
EXTRA_WALK = set()
EXTRA_META = {}
for _k in (1, 2, 3):
    for _s in ("idle", "walk", "interact"):
        EXTRA_META[f"s{_k}_{_s}"] = {"softening_state": _k,
                                     "note": f"replaces vale_{_s}_<facing> while {_k} "
                                             f"{'repair is' if _k == 1 else 'repairs are'} done"}
for _k in (1, 2, 3):
    EXTRA_MS.update({f"s{_k}_idle": 500, f"s{_k}_walk": 133, f"s{_k}_interact": 250})
    EXTRA_MODE.update({f"s{_k}_idle": "loop", f"s{_k}_walk": "loop", f"s{_k}_interact": "once"})
    EXTRA_WALK.add(f"s{_k}_walk")
# The state sets stay inside the strict 20 % anchor-mass tolerance (worst case 0.19, state 3 interact W): none needs
# the relaxed EXTRA_ASYMMETRIC mechanism.

# check_gate1.py applies the stride-edge rule (legs never touch columns 0 and 15) only to the base walks, so the
# state walks assert it here, at import.
for _name in EXTRA_WALK:
    for _f, _frames in EXTRA[_name].items():
        for _i, _fr in enumerate(_frames):
            assert all(r[0] == "." and r[15] == "." for r in _fr[18:]), f"{_name} {_f} {_i}: stride touches the edge"

