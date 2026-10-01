"""Vale portraits, 48x48 logical px, three expressions.

Status: Candidate, pending director review. Spec: PORTRAITS_SPEC.md, rules: PORTRAIT_RULES.md.
Every key is a key of vale_sprites.PAL (hair ABCD graphite, skin klmn ivory, suit pqrs, shirt wxy,
tie tuv, copper badge bcde). No extra steps. The hair keeps the sprite's cowlick, skin-coloured side
part, uneven fringe and ears; the shoulders are square, as on the sprite.
Ruler:  0123456789012345 0123456789012345 0123456789012345  (the axis falls between 23|24)
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, "..", "cast"))
sys.path.insert(0, os.path.join(HERE, "..", "gate1"))
import vale_sprites as spr  # noqa: E402  (the world sprite owns the ramps)
import portrait_template as T  # noqa: E402

PAL = dict(spr.PAL)
SLOTS = spr.SLOTS
EXTRA = {}          # portrait-only keys {key: {"hex", "ramp", "why"}}; none
BROW = "B"          # brows use the hair's second-darkest step: the graphite hair is far darker than the skin
HAIR_SKIN_SEPARATED = False   # graphite hair is 29 L* darker than the skin fill: no equal-luminance contact
TILT = {"neutral": [], "concerned": [(0, 10, -1)], "pleased": [(0, 10, 1)]}   # the crown tilts; the fringe (rows 11-17) stays put
# Vale's pleased is restrained, an almost-smile: the kit's closed eyes and wide smile are replaced by the
# neutral open eyes and a 1 px deep mouth with the corners barely lifted (stamp keys: s/t/u are skin steps).
STAMPS = {"pleased": [
    (19, 17, [".oo.", "soos"]), (19, 27, [".oo.", "soos"]),
    (26, 20, ["tttttttt", "tttttttt", "tttttttt"]),
    (26, 21, ["u"]), (26, 26, ["u"]), (27, 22, ["uuuu"]), (28, 23, ["ss"]),
]}
SPRITE = spr        # world sprite module, used by the review sheet

BASE = T.parse([
    "................ ................ ................",
    "................ ........AAAAooo. ................",
    "................ ....AAAACCDCCCCo oo..............",
    "................ .AAACCCCCCCDCCCC CCoo............",
    "...............A ADCCCCCCDBCCDCCB CCCCo...........",
    "..............AD DCCCCkCCCDCCCDCC CCCCCo..........",
    ".............ADD CDCCBkCCCCDCCCCC BCCCCo..........",
    "............ADCB DCCCkBCCCCCBCCCC CBCCCo..........",
    "...........ADCCD BCCCkCBCCCCCBCCC CCBCCo..........",
    "...........ACCCC CBCCkCCBCCCCCBCC CCCBCo..........",
    "............ACCC CCBkCCCCBCCCCCBC CCCCo...........",
    "............ABCC CAABCCCCCBCCCCCB CCCCo...........",
    "............ACBC lllCBCCCCCBCCCCC BCCBo...........",
    "............ACCB nnnllllCCCAACCCC CBBBo...........",
    "............ACCC nnnnnnnCCCllCCCC AACBo...........",
    "............ACCC nnnnnnnCCCmmAAAl llBo............",
    "............ACAA nnnnnnnAAAmmlllm llAo............",
    ".............oll nnnnnnnlllmmmmmm llo.............",
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
    "................ ...ollllllllo... ................",
    "................ oooommmmmmlloooo ................",
    "........oooooooo sswxxxyyyxxxxwrr oooooooo........",
    "..oooooossssssss ssswxxxxxxxxwrrr rrrrrrrroooooo..",
    ".osrrrrrrrrrrrrr rrrrwxvuutxwqqqq qqqqqqqqqqqqqqo.",
    ".osqqqqqqoqqqqqq rrrrrwvuutwqqqqq qqqqqqoqqqqqqqo.",
    ".osqqqqqqoqqqqqq rrrrrpuuutpqqqqq qqqqqqoqqqqqqqo.",
    ".osqqqqqqoqqqqqq rrrrrpuuutpqqqpe dddpqqoqqqqqqqo.",
    ".osqqqqqqoqqqqqq rrrrrpuuutpqqqpd cccpqqoqqqqqqqo.",
    ".osqqqqqqoqqqqqq rrrrrpuuutpqqqpd cccpqqoqqqqqqqo.",
    ".osqqqqqqoqqqqqq rrrrrpuuutpqqqpc ccbpqqoqqqqqqqo.",
    ".orqqqqqqoqqqqqq rrrrrpuuutpqqqpb bbbpqqoqqqqqqqo.",
    ".orqqqqqqoqqqqqq rrrrrpuutpqqqqqq qqqqqqoqqqqqqqo.",
    ".orqqqqqqoqqqqqq rrrrrpuutpqqqqqq qqqqqqoqqqqqqqo.",
    ".orqqqqqqqqqqqqq rrrrrpuutpqqqqqq qqqqqqqqqqqqqqo.",
]) 

EXPRESSIONS = {e: T.compose(BASE, e, SLOTS["skin"], BROW, STAMPS.get(e, ()), TILT.get(e),
                            SLOTS["hair"] if HAIR_SKIN_SEPARATED else None) for e in T.KIT}
