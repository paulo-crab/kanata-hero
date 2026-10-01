"""Noor portraits, 48x48 logical px, three expressions.

Status: Approved by the director 2026-10-02. Spec: PORTRAITS_SPEC.md, rules: PORTRAIT_RULES.md.
Every key is a key of noor_sprites.PAL (hair ABCD blue-black, skin klmn light olive, shirt pqrs grey
oatmeal, coral folder cdef edge `d`/`e`/`f`, sea-blue tabs ghjJ). No extra steps. The hair is the sprite's short
swept crop: two crown tufts with a notch between them, light strand clusters from the upper left, a stepped
hairline on the right, a left lock, and both ears showing. The shoulders are narrower than the template.
Ruler:  0123456789012345 0123456789012345 0123456789012345  (the axis falls between 23|24)
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, "..", "cast"))
sys.path.insert(0, os.path.join(HERE, "..", "gate1"))
import noor_sprites as spr  # noqa: E402  (the world sprite owns the ramps)
import portrait_template as T  # noqa: E402

PAL = dict(spr.PAL)
SLOTS = spr.SLOTS
EXTRA = {}          # portrait-only keys {key: {"hex", "ramp", "why"}}; none
BROW = "A"          # the hair's mid steps sit within 13 L* of the skin, so brows use the darkest hair step
HAIR_SKIN_SEPARATED = True   # light hair (BCD) never touches l, m or n: a k shadow or an A tip separates them
TILT = {"neutral": [], "concerned": [(0, 11, -1)], "pleased": [(0, 11, 1)]}   # the crown tilts; the fringe stays put
STAMPS = {}
SPRITE = spr

BASE = T.parse([
    "................ ................ ................",
    "................ ..ooo......oooo. ................",
    "................ .oDDCo....oDCCBo ................",
    "...............o ooDDDCooooDCCCBB o...............",
    "..............AD DDDDCCDDCCCCCCBB Bo..............",
    ".............ADD DDCCCDDDCCCCBCCB BBo.............",
    "............ADDD CCCDDCCCCCBCCCCB BBBo............",
    "...........oADDC CCDDCCCCCCCBCCCB BBBo............",
    "............ADCC CDDCCCCCBCCCCCCB BBBo............",
    "............ADCC DDCCCCCCCBCCCCBB BBBBo...........",
    "............oCCC DCCCCCCCBCCCCBBB BBBo............",
    "............oCCC CCCCCBCCCCCBBBBB BBBo............",
    "............oDCC CCCCBBCCCCBBAABB AABo............",
    "............oCCC CCCCBBAAAAAAmmAA llo.............",
    "............oCCC CCCBBBnnmmmmmmmA llo.............",
    "............oBBB BBBnnnnnnmmmmmmm llo.............",
    ".............oAA nAnnnnnmmmmmmmmm llo.............",
    ".............onn nnnnnnmmmmmmmmmm llo.............",
    "...........kkonn nnnnnnnmmmmmmmmm lloooo..........",
    "..........knmonn nnnnnnmmmmmmmmmm llolmo..........",
    "..........knmonn nnnnnnmmmmmmmmmm llolmo..........",
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
    "..ooo..ooo...... ...ollllllllo... ................",
    ".ojJjooeeeo..... oooommmmmmlloooo ................",
    ".oooooooooo...pp ssspmmmmmmllprqq oo..............",
    ".offeeeeeedpppss ssrrpmmmmllprrqq qqooo...........",
    ".offJJJJeppssssr rrrrrpmmllprrqqq qqqqqoo.........",
    ".offhhhppsssrrrr rrrrrrpmlprqqqqq qqqqqqqoo.......",
    ".offeepssrrrrrrr rrrrrrrpprrrqqqq qqqqqqqqqo......",
    ".oeeepssrrqrrrrr rrrrrrrqrrrqqqqq qqqqqqqqqqo.....",
    ".oeeepssrrqrrrrr rrrrrrrqrrrqqqqq qqqqqqqqqqo.....",
    ".oeeepssrrqrrrrr rrrrrrrsrrrqqqqq qqqqqqqqqqo.....",
    ".oeeepssrrqrrrrr rrrrrrrqrrrqqqqq qqqqqqqqqqo.....",
    ".oeeepssrrqrrrrr rrrrrrrqrrrqqqqq qqqqqqqqqqo.....",
    ".oeeepssrrqrrrrr rrrrrrrsrrrqqqqq qqqqqqqqqqo.....",
    ".oeeepssrrqrrrrr rrrrrrrqrrrqqqqq qqqqqqqqqqo.....",
    ".oeeepssrrqrrrrr rrrrrrrqrrrqqqqq qqqqqqqqqqp.....",
])

EXPRESSIONS = {e: T.compose(BASE, e, SLOTS["skin"], BROW, STAMPS.get(e, ()), TILT.get(e),
                            SLOTS["hair"] if HAIR_SKIN_SEPARATED else None) for e in T.KIT}
