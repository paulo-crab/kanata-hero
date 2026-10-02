"""Mira's six delivery patches as overlay data on the approved world sprite and portrait.

Status: world patches approved by the director 2026-10-02; PORTRAIT_PATCHES re-placed for the chibi portraits (pending director review). Spec: MIRA_PATCHES_SPEC.md.
Does not edit mira_sprites.py: every state is built by painting the patches onto the
approved frames. State k (0..6) shows patches 1..k, added in route order (mira.md "Patch
states"). Coordinates are for a frame at rest (idle frame 0, dy = 0); the 1 px settle
(idle frame 1, walk contact frames 0 and 2) paints the same pixels one row lower, which
is exactly how mira_sprites.lower() moves her torso, so no patch ever changes shape.
Patches sit on jacket pixels only: never on the head rows, the strap, the bag or the outline.
"""
import os
import sys
import types

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, "..", "gate1"))
import mira_sprites as spr  # noqa: E402

# Patch-only keys. Every hex is already in Mira's palette or the brass ramp; the new keys exist
# so the glint limits of the base frames (z, H, f: 1 px each) are not spent by patches.
PATCH_PAL = {
    "i": "#F6B18E",  # peach (coral light step), the "paper" colour
    "j": "#B2CE78",  # lime (garden light step)
    "g": "#EDCB7A",  # pale gold (ochre glint step)
    "a": "#E1AC62",  # brass light
    "b": "#F5D580",  # brass glint
}
PAL = dict(spr.PAL)
PAL.update(PATCH_PAL)
JACKET = set("wxyzEFGH")  # keys a patch may sit on (idle frame 0, before painting)

# World patches: facing -> [(x, y, key), ...] at rest. 1-2 px each.
# Layout rule: patches 1-3 are a tidy stack of 2 px bars on the green panel (light colours that
# pop on green), patches 4-6 a second stack on the ochre panel (navy, pale gold, brass over navy).
# W shows only ochre near the camera, so its stacks sit on ochre. Coordinates differ per facing
# because the panels, the strap and the bag move; each patch keeps one colour identity everywhere.
PATCHES = [
    {"id": "first_delivery", "name": "First Delivery", "earned": "Morning Mail (after level 02)", "district": "Orientation",
     "design": "peach bar", "world": {
         "s": [(3, 11, "i"), (4, 11, "i")],
         "n": [(11, 11, "i"), (12, 11, "i")],
         "e": [(3, 11, "i"), (4, 11, "i")],
         "w": [(4, 11, "i"), (5, 11, "i")]}},
    {"id": "clear_address", "name": "Clear Address", "earned": "Courier Loop (after level 07)", "district": "Records",
     "design": "lime bar", "world": {
         "s": [(3, 13, "j"), (4, 13, "j")],
         "n": [(10, 13, "j"), (11, 13, "j")],
         "e": [(3, 13, "j"), (4, 13, "j")],
         "w": [(4, 13, "j"), (5, 13, "j")]}},
    {"id": "archive_loop", "name": "Archive Loop", "earned": "Lost Folios (after level 11)", "district": "Records",
     "design": "brass bar", "world": {
         "s": [(4, 15, "a"), (5, 15, "a")],
         "n": [(9, 15, "a"), (10, 15, "a")],
         "e": [(6, 15, "a"), (7, 15, "a")],
         "w": [(10, 11, "a"), (11, 11, "a")]}},
    {"id": "signed_and_sent", "name": "Signed and Sent", "earned": "Payroll Run (after level 13)", "district": "Systems",
     "design": "navy bar", "world": {
         "s": [(11, 11, "O"), (12, 11, "O")],
         "n": [(3, 11, "O"), (4, 11, "O")],
         "e": [(10, 11, "O"), (11, 11, "O")],
         "w": [(10, 13, "O"), (11, 13, "O")]}},
    {"id": "signal_keeper", "name": "Signal Keeper", "earned": "Glyph Dispatch (after level 16)", "district": "Systems",
     "design": "pale gold bar", "world": {
         "s": [(11, 13, "g"), (12, 13, "g")],
         "n": [(3, 13, "g"), (4, 13, "g")],
         "e": [(10, 13, "g"), (11, 13, "g")],
         "w": [(8, 14, "g"), (9, 14, "g")]}},
    {"id": "night_courier", "name": "Night Courier", "earned": "Lights-Out Delivery (after level 18)", "district": "Night Shift",
     "design": "brass glint beside navy", "world": {
         "s": [(9, 12, "b"), (10, 12, "O")],
         "n": [(5, 12, "b"), (6, 12, "O")],
         "e": [(8, 12, "b"), (9, 12, "O")],
         "w": [(9, 16, "b"), (10, 16, "O")]}},
]


# Portrait icons (chibi direction C): the same six colour identities drawn as 4-6 px icons on the
# tiny shoulders. The jacket is the green panel on the left of the portrait (the strap runs down
# from the upper left to the middle of the bottom edge) and the ochre panel on the right. Patches 1-2
# sit on the green panel either side of the strap, patches 3-6 in two rows on the ochre panel, each
# kept clear of the zip, the strap and the dark right edge. Each entry is (top row, left column,
# rows); "." leaves the jacket showing. Rows 38-47 are the shoulders.
PORTRAIT_PATCHES = [
    {"id": "first_delivery", "icon": "envelope: peach body, coral flap", "stamps": [(44, 9, [
        "diiiid",
        "idiidi",
        "iiddii",
        "iiiiii"])]},
    {"id": "clear_address", "icon": "map pin: lime ring, green hole", "stamps": [(40, 18, [
        ".jjj.",
        "jjFjj",
        ".jjj.",
        "..j.."])]},
    {"id": "archive_loop", "icon": "loop: brass ring with a glint", "stamps": [(40, 25, [
        ".aaa.",
        "a...a",
        "a...a",
        ".aab."])]},
    {"id": "signed_and_sent", "icon": "check mark in navy ink", "stamps": [(40, 31, [
        ".....O",
        "O...O.",
        ".O.O..",
        "..O..."])]},
    {"id": "signal_keeper", "icon": "three rising pale-gold bars", "stamps": [(44, 26, [
        "....g",
        "..g.g",
        "g.g.g",
        "g.g.g"])]},
    {"id": "night_courier", "icon": "navy crescent with a brass star", "stamps": [(44, 32, [
        "..OO.",
        ".b..O",
        "....O",
        "..OO."])]},
]


def portrait_patches(grid, k):
    """Paint patch icons 1..k onto a 48x48 portrait grid (non-'.' keys only)."""
    rows = [list(r) for r in grid]
    for patch in PORTRAIT_PATCHES[:k]:
        for top, left, art in patch["stamps"]:
            for dy, line in enumerate(art):
                for dx, ch in enumerate(line):
                    if ch != ".":
                        rows[top + dy][left + dx] = ch
    return ["".join(r) for r in rows]


def patch_frame(frame, facing, k, dy=0):
    """Paint patches 1..k onto a world frame. dy is the frame's settle offset (0 or 1)."""
    rows = [list(r) for r in frame]
    for patch in PATCHES[:k]:
        for x, y, key in patch["world"][facing]:
            rows[y + dy][x] = key
    return ["".join(r) for r in rows]


def settle(kind, i):
    """The settle offset of a frame in mira_sprites: idle 1, and walk contact frames 0 and 2."""
    return 1 if (kind == "idle" and i == 1) or (kind == "walk" and i % 2 == 0) else 0


def state_frames(k):
    idle = {f: [patch_frame(fr, f, k, settle("idle", i)) for i, fr in enumerate(frs)] for f, frs in spr.IDLE.items()}
    walk = {f: [patch_frame(fr, f, k, settle("walk", i)) for i, fr in enumerate(frs)] for f, frs in spr.WALK.items()}
    return idle, walk


def module_for_state(k):
    """A sprite-module-shaped object so check_gate1.py and build scripts can treat state k as a sprite."""
    idle, walk = state_frames(k)
    return types.SimpleNamespace(PAL=PAL, SLOTS=spr.SLOTS, IDLE=idle, WALK=walk,
                                 GLINT_LIMITS=dict(spr.GLINT_LIMITS, i=2, j=2, g=2, a=2, b=1))
