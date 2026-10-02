"""Background worker, body B ("long hair"): frames hand-placed at 16x24 logical px.

Status: Approved by the director 2026-10-02. Spec: BACKGROUND_WORKERS_SPEC.md.
A 12 px sweater silhouette under a centre-parted, chin-to-shoulder cut whose ends
flick out unevenly (with the ear tucked on the worker's left), an under-shirt hem
peeking below the sweater, and a level stance. No signature prop. Palette swaps
live in bgworker_common.PALETTES; the key layout never changes.
"""
import bgworker_common as common
from bgworker_common import (LEGS_IDLE_N, LEGS_IDLE_S, LEGS_N, LEGS_S, PALETTES, SILHOUETTE_LIT_PAL,  # noqa: F401
                             SILHOUETTE_PAL, SLOTS, lower, make_pal, silhouette, silhouette_lit, stamp, variant,
                             walk_front_back, walk_side)

PAL = common.PAL

S = [
    "................",
    ".....oooooo.....",
    "....oDDCCCBo....",
    "...oDDCCCCBBo...",
    "..oDDCCDCCCBBo..",
    "..oCDCCCCCCBBo..",
    "..oCCBklllBBBo..",
    "..oBBnommomBBo..",
    "..oBBnmmmmmlBo..",
    "..oBCklmmlkCBo..",
    "...oBsxnnxsBo...",
    "..ossrrrrrrqqo..",
    "..osprrqrrrpqo..",
    "..osprrqrrrpqo..",
    "..osprrqrrrpqo..",
    "..ompqwxxwqpmo..",
    "..oloOPPPPOolo..",
    "....oOPPOPPOo...",
] + LEGS_IDLE_S

N = [
    "................",
    ".....oooooo.....",
    "....oDDCCCBo....",
    "...oDDCCCCBBo...",
    "..oDDCCDCCCBBo..",
    "..oCDCCCCCCBBo..",
    "..oCCCCCBCCBBo..",
    "..oCCBCCCCBBBo..",
    "..oCBCCBBCBBBo..",
    "..oBCCCBBCCBBo..",
    "..oBCBCCBBCBBo..",
    "..osBCBBCBBCso..",
    "..ospBBCBBBpqo..",
    "..osprrBBrrpqo..",
    "..osprrrrrrpqo..",
    "..ompqwxxwqpmo..",
    "..oloOPPPPOolo..",
    "....oOPPOPPOo...",
] + LEGS_IDLE_N

E_HEAD = [
    "................",
    ".....ooooo......",
    "....oDDCCCoo....",
    "...oDDCCCCCCo...",
    "..oDDCCCCCCBBo..",
    "..oCDCCCCCBBBo..",
    "..oCCCCBlllko...",
    "..oCCBBBnomno...",
    "..oCBBBBmmmmo...",
    "..oCBBBBlmmlo...",
    "..oCBBBsxxqo....",
    "..oCBBsrrxrqo...",
]
E_ARMS = (
    [   # neutral
        "..oCBrprqqqqo...",
        "..oBsrprqqqqo...",
        "...osrprqqqqo...",
        "...osrpmmqqqo...",
        "....oOPlmPOo....",
    ],
    [   # arm swung back
        "..oCBrprqqqqo...",
        "..oBsprqqqqqo...",
        "...oprqqqqqqo...",
        "...ommqqqqqqo...",
        "...olmPPPPOo....",
    ],
    [   # arm swung forward
        "..oCBrprqqqqo...",
        "..oBsrqprqqqo...",
        "...osrqqprqqo...",
        "...osrqqqqmmo...",
        "....oOPPPPlmo...",
    ],
)
E_HEM = "....oOPPPPOo...."

W_HEAD = [
    "................",
    "......ooooo.....",
    "....ooDDCCCo....",
    "...oDDCCCCCCo...",
    "..oDDCCCCCCBBo..",
    "..oCDCCCCCBBBo..",
    "...olllkCCCCBo..",
    "...onmonCCBBBo..",
    "...ommmmCBBBBo..",
    "...olmmlCBBBBo..",
    "....osxxqCBBBo..",
    "...osrxrrqCBBo..",
]
W_ARMS = (
    [
        "...orprqqqqCBo..",
        "...osrprqqqqBo..",
        "...osrprqqqqo...",
        "...osrpmmqqqo...",
        "....oOPlmPOo....",
    ],
    [
        "...orprqqqqCBo..",
        "...osprqqqqqBo..",
        "...oprqqqqqqo...",
        "...oqqqqqqmmo...",
        "....oOPPPPlmo...",
    ],
    [
        "...orprqqqqCBo..",
        "...osrqprqqqBo..",
        "...osrqqprqqo...",
        "...ommsrqqqqo...",
        "...olmPPPPOo....",
    ],
)

W_LEGS_IDLE = [r[::-1] for r in common.eng.E_LEGS]
E_IDLE = E_HEAD + E_ARMS[0] + common.eng.E_LEGS
W_IDLE = W_HEAD + W_ARMS[0] + W_LEGS_IDLE

IDLE = {f: [fr, lower(fr)] for f, fr in (("s", S), ("n", N), ("e", E_IDLE), ("w", W_IDLE))}
WALK = {
    "s": walk_front_back(S, LEGS_S),
    "n": walk_front_back(N, LEGS_N),
    "e": walk_side(E_HEAD, E_ARMS, E_HEM),
    "w": walk_side(W_HEAD, W_ARMS, E_HEM, west=True),
}


IDLE_VARIANTS = {
    "phone_s": variant(S, {
        12: "..osprggggrpqo..", 13: "..ospmgjjgmpqo..", 14: "..ospmgjhgmpqo..",
        15: "..osprggggrpqo..", 16: "..osoOPPPPOoqo..",
    }, alt={13: "..ospmgjhgmpqo..", 14: "..ospmgjjgmpqo.."}),
    "coffee_s": variant(S, {
        13: "..osprriSirrpqo.", 14: "..ospmfffeqpqo..", 15: "..ospreeerrpmo..", 16: "..osoOPPPPOolo..",
    }),
    "typing_s": variant(S, {
        13: "..osprrrmmrpqo..", 14: "..ospmmrrrrpqo..", 15: "..osprrrrrrpqo..", 16: "..osoOPPPPOoqo..",
    }, alt={13: "..ospmmrrrrpqo..", 14: "..osprrrmmrpqo.."}),
}


# Seated at a desk. See body A for the convention; the same rows carry the arms, with B's wider sleeves.
_HIPS = {15: "..ospqwxxwqpqo..", 16: "..osoOPPPPOoqo.."}
SEATED = {
    "idle": common.seated(S, {**_HIPS, 14: "..osprmrrmrpqo.."}),
    "typing": common.seated(S, {**_HIPS, 13: "..osprmrrrrpqo..", 14: "..osprrrrmrpqo.."},
                            alt={13: "..osprrrrmrpqo..", 14: "..osprmrrrrpqo.."}, settle=False),
    "phone": common.seated(S, {**_HIPS, 11: "..ossrggggrqqo..", 12: "..ospmgjjgmpqo..",
                               13: "..ospmgjhgmpqo..", 14: "..osprggggrpqo.."},
                           alt={12: "..ospmgjhgmpqo..", 13: "..ospmgjjgmpqo.."}, settle=False),
    "coffee": common.seated(S, {**_HIPS, 11: "..osprriSirrpqo.", 12: "..ospmfffeqpqo..",
                                13: "..ospreeerrpmo..", 14: "..osprrqrrrpqo.."}),
}
EXTRA = {f"seated_{k}": {"s": v} for k, v in SEATED.items()}
EXTRA_MS = {f"seated_{k}": (250 if k == "typing" else 500) for k in SEATED}
