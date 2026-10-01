"""Ivo portraits, 48x48 logical px, three expressions.

Status: Approved by the director 2026-10-02. Spec: PORTRAITS_SPEC.md, rules: PORTRAIT_RULES.md.
Every key is a key of ivo_sprites.PAL (hair ABCD silver, skin klmn, cardigan pqrs, shirt
strip xyz, tablet ghjJ). No extra steps. Ivo's shoulders are broader than the template
(the slope reaches full width on row 39), which PORTRAIT_RULES.md allows per character.
Ruler:  0123456789012345 0123456789012345 0123456789012345  (the axis falls between 23|24)
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, "..", "cast"))
sys.path.insert(0, os.path.join(HERE, "..", "gate1"))
import ivo_sprites as spr  # noqa: E402
import portrait_template as T  # noqa: E402

PAL = dict(spr.PAL)
SLOTS = spr.SLOTS
EXTRA = {}          # portrait-only keys {key: {"hex", "ramp", "why"}}; none
BROW = "A"          # silver hair would merge with pale skin, so brows use the hair's darkest step
HAIR_SKIN_SEPARATED = True   # light hair (BCD) never touches l, m or n: the k shadow separates them
TILT = {"neutral": [], "concerned": [(0, 11, -1)], "pleased": [(0, 11, 1)]}   # crown clusters tilt; the fringe stays put
STAMPS = {}
SPRITE = spr

BASE = T.parse([
    "................ ................ ................",
    "................ ....AAAA........ ................",
    "................ ...ADDDDAA.AAA.. ................",
    "...............A AAADDDDDDDACCCA. ................",
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
    "..........knBBkn nnnnnnnmmmmmmmmm lkBBko..........",
    "..........knAonn nnnnnnmmmmmmmmmm lkBAmo..........",
    "..........knlonn nnnnnnmmmmmmmmmm llommo..........",
    "..........kmlonn nnnnnmmmmmmmmmml llolmo..........",
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
    "..........ooooor rrrrpmmmmmmprrqq qooooo..........",
    "......ppppsssssr rrrrpxxxxxxprrqq qqqqqqoooo......",
    "...pppsssssrrrrr rrrrrpxxxxprrqqq qqqqqqqqqqooo...",
    "..psssssrrrrrrrr rrrrrpyzxxprrqqq qqqqqqqqqqqqqo..",
    ".pssrrrrrrrrrrrr rrrrrpyxxxprqqqq qqqqqqqqqqqqqqo.",
    ".pssrrrrrrrrrrrr rrrrrpyxxxprqqqq qqqqqqqqqqqqqqo.",
    ".pssrrrrrrrrrrrr rrrrrpyxxxpqqggg gggggggggggqqqo.",
    ".pssrrrrrrrrrrrr rrrrrpyxxxpqqgjJ jjjjjjjjjjgqqqo.",
    ".ossrrrrrrrrrrrr rrrrrpyxxxpqqgjj hhhhhhhjjjgqqqo.",
    ".ossrrrrrrrrrrrr rrrrrpyxxxpqmmjj jjjjjjjjjjgqqqo.",
    ".ossrrrrrrrrrrrr rrrrrpyxxxpqmmjj hhhhjjjjjjgqqqo.",
    ".ossrrrrrrrrrrrr rrrrrpyxxxpqqgjj jjjjjjjjjjgqqqo.",
    ".ossrrrrrrrrrrrr rrrrrpyxxxpqqgjj jjjjjjjjjjgqqqo.",
])

EXPRESSIONS = {e: T.compose(BASE, e, SLOTS["skin"], BROW, STAMPS.get(e, ()), TILT.get(e),
                            SLOTS["hair"] if HAIR_SKIN_SEPARATED else None) for e in T.KIT}
