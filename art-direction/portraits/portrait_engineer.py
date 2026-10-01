"""Engineer portraits, 48x48 logical px, three expressions.

Status: Candidate, pending director review. Spec: PORTRAITS_SPEC.md, rules: PORTRAIT_RULES.md.
Every key is a key of engineer_sprites.PAL, so the portrait wears the world sprite's
ramps exactly (hair ABCD, skin klmn, jacket pqrs, collar wxy, badge bcd). No extra steps.
Ruler:  0123456789012345 0123456789012345 0123456789012345  (the axis falls between 23|24)
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, "..", "gate1"))
import engineer_sprites as spr  # noqa: E402  (the world sprite owns the ramps)
import portrait_template as T  # noqa: E402

PAL = dict(spr.PAL)
SLOTS = spr.SLOTS
EXTRA = {}          # portrait-only keys {key: {"hex", "ramp", "why"}}; none (PORTRAIT_RULES.md "Extra steps")
BROW = "B"          # brows use the hair's second-darkest step
HAIR_SKIN_SEPARATED = False
TILT = {}           # per-expression tilt overrides (default: portrait_template.TILT)
STAMPS = {}         # per-expression character stamps (row, col, rows)
SPRITE = spr        # world sprite module, used by the review sheet

BASE = T.parse([
    "................ ................ ................",
    "................ ....AA....AA.... ................",
    "................ ...ADDAAAACCA... ................",
    "................ .AADDDDCCCCCCAA. ................",
    "...............A ADDDDBCCCCCCBCBo o...............",
    "..............AD DDDDCCBBCCCCCBBC Bo..............",
    ".............ADB DDDCCCCCBBCCCCCB CBo.............",
    "............ADDD BBCCCCCCCCBBCCCC CCBo............",
    "...........ADDDD CCBBCCCCCCCCBBCC CCCBo...........",
    "............ADCC CCCCBBCCCCCCCCCC CCCBo...........",
    "............ABCC CCCCCCBBCCCCCCCC CCCCBo..........",
    ".............ACC CBBBCCCCCCCCCCCC CCCCBo..........",
    ".............ACC BlllBBCCCCCCCCCC CCCCBo..........",
    ".............ACB lnnnllCCCCCCCCCC CCCCBo..........",
    ".............ABl nnnnnBCCBBCCCBCC CBCCBo..........",
    ".............oln nnnnnlBBllBBBlBB BlCCBo..........",
    ".............onn nnnnnnllmmlllmll lmCBo...........",
    ".............onn nnnnnnnmmmmmmmmm llCBo...........",
    "...........kkonn nnnnnnnmmmmmmmmm llCBo...........",
    "..........knmonn nnnnnnmmmmmmmmmm llBBo...........",
    "..........knmonn nnnnnnmmmmmmmmmm lloBo...........",
    "..........knlonn nnnnnmmmmmmmmmml llommo..........",
    "..........kmlonn nnnnnmmmmmmmmmml llolmo..........",
    "..........kmmonn nnnnmmmmmmmmmmml llolmo..........",
    "..........kmmknn nnnnmmmmmmmmmmml llomlo..........",
    "...........oo.on nnnmmmmmmmmmmmll loomlo..........",
    "..............on nnnmmmmmmmmmmmll lo.oo...........",
    "...............k nnmmmmmmmmmmmlll o...............",
    "...............k nnmmmmmmmmmmmmll o...............",
    "................ kmmmmmmmmmmmmllo ................",
    "................ .kmmmlllllllllo. ................",
    "................ ..ollllllllllo.. ................",
    "................ ...ollllllllo... ................",
    "................ ...ollllllllo... ................",
    "................ oooommmmmmlloooo ................",
    "............oooo rxyyyrrrrrrwxxxq oooo............",
    ".........pppssss srxyyyrrrrwxxxqq qqqqooo.........",
    "......pppsssssrr rrrxyyyrrwxxxqqq qqqqqqqooo......",
    "....ppsssssrrrrr rrrrrxyywwxrrbqq qqqqqqqqqqoo....",
    "...pssrrrrrrrrrr rrrrrrrrrrrrqqbq qqqqqqqqqqqqo...",
    "..pssrrrrrrrrrrr rrrrrrrrrrrrqqqb qqqqqqqqqqqqqo..",
    ".pssrrrrrrrrrqrr rrrrrrrrqrrqqqqq bbqqqqqqqqqqqqo.",
    ".pssrrrrrrrrrqrr rrrrrrrrqrrqqqqq bbbbqqqqqqqqqqo.",
    ".ossrrrrrrrrrqrr rrrrrrrrqrqqqqqq bcdbqqqqqqqqqqo.",
    ".ossrrrrrrrrrqrr rrrrrrrrqrqqqqqq bccbqqqqqqqqqqo.",
    ".ossrrrrrrrrrqrr rrrrrrrrqqqqqqqq qqqqqqqqqqqqqqo.",
    ".ossrrrrrrrrrqrr rrrrrrrrqqqqqqqq qqqqqqqqqqqqqqo.",
    ".ossrrrrrrrrrqrr rrrrrrrrqqqqqqqq qqqqqqqqqqqqqqo.",
])

EXPRESSIONS = {e: T.compose(BASE, e, SLOTS["skin"], BROW, STAMPS.get(e, ()), TILT.get(e),
                            SLOTS["hair"] if HAIR_SKIN_SEPARATED else None) for e in T.KIT}
