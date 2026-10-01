"""Ada portraits, 48x48 logical px, three expressions.

Status: Approved by the director 2026-10-02. Spec: PORTRAITS_SPEC.md (Ada section), rules: PORTRAIT_RULES.md.
Every key is a key of ada_sprites.PAL (hair ABCD warm white, skin klmn deep brown, coat pqrs moss,
lantern housing uvw, lantern light fg). No extra steps. The coat, boots and lantern colours are the
sprite's; the portrait shows the lantern's top at the lower right, as the sprite carries it.
Ruler:  0123456789012345 0123456789012345 0123456789012345  (the axis falls between 23|24)
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, "..", "cast"))
sys.path.insert(0, os.path.join(HERE, "..", "gate1"))
import ada_sprites as spr  # noqa: E402
import portrait_template as T  # noqa: E402

PAL = dict(spr.PAL)
SLOTS = spr.SLOTS
EXTRA = {}          # portrait-only keys {key: {"hex", "ramp", "why"}}; none
BROW = "B"          # warm-white brows (hair mid step) read clearly on deep skin
HAIR_SKIN_SEPARATED = False   # hair and skin differ by more than 21 L*; the fringe still sits on an l shadow row
TILT = {}
STAMPS = {}
SPRITE = spr

BASE = T.parse([
    "................ ................ ................",
    "................ .ooo....ooo..... ................",
    "...............o oDDCo..oDDCo...o oo..............",
    "..............oD DDCCCooDDCCCoooB DDo.............",
    "..............oD DCCCCCDDCCCCCCCB DDCo............",
    ".............oDD CCCCCBDCCCCCCCBD DCCCo...........",
    "............ADBC CCCCCCBCCCCCBBBD DCCCo...........",
    "...........ADDDB CCCCCBBCCCCBBBDD CCCCCo..........",
    "...........ADDCC BCCCBBBCBCBBBBDC CCCCo...........",
    "............ADCC CBCBDDCCCCCBBDDC CCCCBo..........",
    "............ACCC CBDDCCCCCCCCBDCC CCCBBo..........",
    "...........ADCCC CBCCCCCCCCBBBCCC CCBBBo..........",
    "............ACCC BBCCCCCCBBBBBCCC CCBBo...........",
    ".............ACC BBBACCCBBBBBBAAC CBCo............",
    ".............ACB BBllBBBBBllBBllB BBCo............",
    "............ooBB llnnlllAABkllmml lBAo............",
    "...........oCCBB nnnnnnnllkmmmmmm mBBBo...........",
    "...........oCBBl nnnnnnnmmmmmmmmm llBBo...........",
    "..........knBBBn nnnnnnnnnnnnnnnn lkBBko..........",
    "..........knAonn nnnnnnnnnnmmmmmm lkBAmo..........",
    "..........knlonn nnnnnnnnnnmmmmmm llommo..........",
    "..........kmlonn nnnnnnnnnnnnnnnl llolmo..........",
    "..........kmmonn nnnnnmmmmmmnnnnl llolmo..........",
    "..........kmmonn nnnnmmmmmmmmmmml llomlo..........",
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
    "...............o oooommmmmmlloooo o...............",
    "...............o ssspmmmmmmmmprqq o...............",
    "...........ooooo rqsspllllllprrqq ooooo...........",
    "........oooorrrr rrqsspllllprrqqq qqqqoooo........",
    ".....oooorrrrrrr rrrqsspllprrqrqq qqqqnnmmooo.....",
    "...ooosrrrrrrrrr rrrrqrrqrrrqrqqq qqqqnmmlqqooo...",
    "..oossrrrrrrrrrr rrrrrqrqrrqrqqqq qqqqmmllqqqqoo..",
    ".posrrrrrrrrrrrr rrrrrrqqrqrqqqqq qqquuuuuuqqqqoo.",
    ".pssrrrrrrrrrrrr rrrrrrrqwrrqqqqq quwwwwwwwvuqqqo.",
    ".pssrrrrrrrrrrrr rrrrrrrqrrrqqqqq quvvvvvvvvuqqqo.",
    ".pssrrrrrrrrrrrr rrrrrrrqrrrqqqqq qugggfffffuqqqo.",
    ".pssrrrrrrrrrrrr rrrrrrrqwrrqqqqq quggfffffvuqqqo.",
    ".ossrrrrrrrrrrrr rrrrrrrqrrrqqqqq qufffffffvuqqqo.",
    ".ossrrrrrrrrrrrr rrrrrrrqrrrqqqqq qufffffffvuqqqo.",
])

EXPRESSIONS = {e: T.compose(BASE, e, SLOTS["skin"], BROW, STAMPS.get(e, ()), TILT.get(e),
                            SLOTS["hair"] if HAIR_SKIN_SEPARATED else None) for e in T.KIT}
