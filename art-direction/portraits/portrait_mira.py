"""Mira portraits, 48x48 logical px, three expressions, plus the six patch states.

Status: Approved by the director 2026-10-02. Spec: PORTRAITS_SPEC.md, rules: PORTRAIT_RULES.md.
Every key is a key of mira_sprites.PAL (hair ABCD, skin klmn, ochre panel wxyz, green panel
EFGH, coral strap and bag cdef). No extra steps. Patch overlays come from
../cast/mira_patches.py (PORTRAIT_PATCHES) and are applied by `with_patches`.
Ruler:  0123456789012345 0123456789012345 0123456789012345  (the axis falls between 23|24)
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, "..", "cast"))
sys.path.insert(0, os.path.join(HERE, "..", "gate1"))
import mira_sprites as spr  # noqa: E402
import portrait_template as T  # noqa: E402

PAL = dict(spr.PAL)
SLOTS = spr.SLOTS
EXTRA = {}          # portrait-only keys {key: {"hex", "ramp", "why"}}; none
BROW = "B"
HAIR_SKIN_SEPARATED = False
HAIR_TOUCH_SKIN = "mn"       # her hair and skin share luminance: only the lighter skin steps touch hair; A is the hair's shadow line
TILT = {"neutral": [(0, 10, 1)], "concerned": [(0, 10, -1)], "pleased": []}   # she leans into motion (neutral and concerned lean opposite ways)
STAMPS = {}
SPRITE = spr

BASE = T.parse([
    "................ ................ ................",
    "................ ................ AAAA............",
    "................ ..............AA CCCBAA..........",
    "................ .AAAAAAAAAA..ACC DDCCCBA.........",
    "...............A ADDDDDDBCCCooCCD DDCCCCBo........",
    "..............AD DDDDBCCCBCCooCDD CCBCCCBo........",
    ".............ADD DDDDCBCCCBCCoBDC CBCBCCBo........",
    "............ADDD DBCCCCBCCCCCooCC CCCBBBo.........",
    "............ADDD DCBCCCCBCCBCCCCC CBBooo..........",
    "............ADDC CCCCCCCCBCCBCCCC CCBo............",
    "............ADCC CCCCCCCCCCCCBCCC CCBo............",
    "............ACCC CCCCCCCCCCCCCBCC CCBo............",
    "............ACCC CAACCCCCCCCCCCCA CCBo............",
    "............ACCC AnnAACCCAACCCCAm ACBo............",
    "............ACCA nnnnnACAnmAACAmm mABo............",
    "............oCAn nnnnnnAnnmmmAmmm mmBo............",
    "............oBnn nnnnnnnnnmmmmmmm mmo.............",
    ".............onn nnnnnnnmmmmmmmmm mmo.............",
    "...........kkonn nnnnnnnmmmmmmmmm mmooo...........",
    "..........knmonn nnnnnnmmmmmmmmmm mmommo..........",
    "..........knmonn nnnnnnmmmmmmmmmm llommo..........",
    "..........knlonn nnnnnmmmmmmmmmmm llommo..........",
    "..........kmlonn nnnnnmmmmmmmmmmm llolmo..........",
    "..........kmmonn nnnnmmmmmmmmmmmm llollo..........",
    "..........kmmknn nnnnmmmmmmmmmmml llomlo..........",
    "...........oo.on nnnmmmmmmmmmmmll lo.oo...........",
    "..............on nnnmmmmmmmmmmmll lo..............",
    "...............k nnmmmmmmmmmmmlll o...............",
    "...............k nnmmmmmmmmmmmmll o...............",
    "................ kmmmmmmmmmmmmllo ................",
    "................ .kmmmlllllllllo. ................",
    "................ ..ollllllllllo.. ................",
    "................ ...ollllllllo... ................",
    "................ ...ollllllllo... ................",
    "................ oooommmmmmlloooo ................",
    "............oooo GGGGGFFFyyyyyyyy oooo............",
    ".........EEEGeed GGGGGFFFyyyyyyyx xxxxooo.........",
    "......EEEGGGGGGe edFGGFFFxxyyxxxx xxxxxxwooo......",
    "....EEGGGGGGFFFF eedFFFFExxxxxxxx xxxxxxxxxwoo....",
    "...EGGFFFFFFFFFF FFeedFFExxxxxxxx xxxxxxxxxxxwo...",
    "..EGGFFFFFFFFFFF FFFeedFExxxxxxxx xxxxxxxxxxxxwo..",
    ".EGGFFFFFFFFFFFF FFFFFeedxxxxxxxx xxxxxxxxxxxxxwo.",
    ".EGGFFFFFFFFFFFF FFFFFFFeedxxxxxx xxxxxxxxxxxxxwo.",
    ".oGGFFFFFFFFFFFF FFFFFFFEeedxxxxx xxxxxxxxxxxxxwo.",
    ".oGGFFFFFFFFFFFF FFFFFFFExxeedxxx xxxxxxxxxxxxxwo.",
    ".oGGFFFFFFFFFFFF FFFFFFFExxxeedxx xxxxxxxxxxxxxwo.",
    ".oGGFFFFFFFFFFFF FFFFFFFExxxxxeed xxxxxxxxxxxxxwo.",
    ".oGGFFFFFFFFFFFF FFFFFFFExxxxxxxe edxxxxxxxxxxxwo.",
])

EXPRESSIONS = {e: T.compose(BASE, e, SLOTS["skin"], BROW, STAMPS.get(e, ()), TILT.get(e),
                            SLOTS["hair"] if HAIR_SKIN_SEPARATED else None) for e in T.KIT}

import mira_patches as patches  # noqa: E402  (../cast, already on sys.path)

# Patch icons use mira_patches.PATCH_PAL keys (hexes already in her palette or the brass ramp).
PATCH_PAL = dict(PAL)
PATCH_PAL.update(patches.PATCH_PAL)


def with_patches(grid, k):
    """The portrait wearing patches 1..k (0 returns the grid unchanged)."""
    return patches.portrait_patches(grid, k)
