"""Hal portraits, 48x48 logical px, three expressions.

Status: Approved by the director 2026-10-02. Spec: PORTRAITS_SPEC.md (Hal), rules: PORTRAIT_RULES.md.
Every key is a key of hal_sprites.PAL (hair ABCD sandy blond, skin klmn, vest pqrs, sleeves wxy,
roll EFGH, tool tips hj). No extra steps. The hair keeps the sprite's reading: a dome with spikes,
uneven fringe, ears showing. His brows use outline ink, because the blond hair steps and the golden
skin are close in value and the skin's own darkest step may not be used as fill.
Ruler:  0123456789012345 0123456789012345 0123456789012345  (the axis falls between 23|24)
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, "..", "cast"))
sys.path.insert(0, os.path.join(HERE, "..", "gate1"))
import hal_sprites as spr  # noqa: E402
import portrait_template as T  # noqa: E402

PAL = dict(spr.PAL)
SLOTS = spr.SLOTS
EXTRA = {}          # portrait-only keys {key: {"hex", "ramp", "why"}}; none
BROW = "o"          # brows use outline ink: hair A is as dark as his skin, and skin k may not be fill
HAIR_SKIN_SEPARATED = True   # light hair (BCD) never touches l, m or n: the k shadow separates them
TILT = {"neutral": [], "concerned": [(0, 11, -1)], "pleased": [(0, 11, 1)]}   # the crown tilts; the fringe stays put
STAMPS = {}
SPRITE = spr

BASE = T.parse([
    "................ ................ ................",
    "................ .AA...AA....oo.. ................",
    "................ ADDAAADCooooCBo. ................",
    "...............A DDDDDDCCDCBBCBo. ................",
    "..............AD DDDDCBCCDDCCCCCo ................",
    ".............ADD DDDCCBCCCBCCBCCC o...............",
    "............ADDC BCDCCCBCBCCCBCCC Co..............",
    "............ADCC BBCCCCBCBCCCCBBC CCo.............",
    "............ADCC CBCCCCCCBCCCCCBC CCCo............",
    "............ADCC CBCCCCCBCCCCCCBC BCCo............",
    "............ADCC CBCCCCCBCCCCCBCC BCBo............",
    "............ADCC CBCCBBBBCCBBBCCB CCBo............",
    "............ADCC CBBCCkCCCCCkCCCB CCCo............",
    ".............ACC CCkBCCBCCCCkBCBk BCCo............",
    ".............ACC CknkBAkCCCAmkAkm kBCo............",
    "............ooCA knnnknkBCBkmmmmm mkAo............",
    "...........oCCAn nnnnnnnkAkmmmmmm mkBBo...........",
    "...........oCBkn nnnnnnnmmmmmmmmm lkBBo...........",
    "..........knBBkn nnnnnnnmmmnnnnnn lkBBko..........",
    "..........knAonn nnnnnnmmmmnnnnnn lkBAmo..........",
    "..........knlonn nnnnnnmmmmnnnnnn llommo..........",
    "..........kmlonn nnnnnmmmmmnnnnnl llolmo..........",
    "..........kmmonn nnnnnmmmmmmmmmml llolmo..........",
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
    "...............o ssspxyyxxxxxpqqq o...............",
    "...........oooor rrrrpxxxxxxpqqqq qoooo...........",
    "........ooosrrrr rrrrrpxxxxprrqqq qqqqqooo........",
    ".....ooosrrrrrrr rrrrrrpppprrrrrr qqqqqqqqooo.....",
    "...oossrrrrrrrrr rrrrrrrqrrrrrrrr rqqqqqqqqqqoo...",
    "..osssrrrrrrrrrr rrrrrrrqrrrrrrrr rrqqqqqqqqqqqo..",
    ".oyxxprrrrrrrrrr rrrrrrrqrrrrrrrr rrqqqqqqqqpxxwo.",
    ".oyxxprrrrrqqqqq qqrrrrrqrrrrrrrr rrqqqjqhqjpxxwo.",
    ".oyxxprrrrrqrrrr rqrrrrrqrrrrrrrr rqqqoooooooxxwo.",
    ".oyxxprrrrrqrrrr rqrrrrrqrrrrrrrr rqqoHGFFFEEoxwo.",
    ".oyxxprrrrrqrrrr rqrrrrrqrrrrrrrr qqqoGyyyyyEoxwo.",
    ".oyxxprrrrrqqqqq qqrrrrrqrrrrrrrr qqqoGGFFFEEoxwo.",
    ".oyxxprrrrrrrrrr rrrrrrrqrrrrrrrq qqqGGFFFFEEExwo.",
])

EXPRESSIONS = {e: T.compose(BASE, e, SLOTS["skin"], BROW, STAMPS.get(e, ()), TILT.get(e),
                            SLOTS["hair"] if HAIR_SKIN_SEPARATED else None) for e in T.KIT}
