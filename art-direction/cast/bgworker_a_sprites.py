"""Background worker, body A ("slim"): frames hand-placed at 16x24 logical px.

Status: Approved by the director 2026-10-02. Spec: BACKGROUND_WORKERS_SPEC.md.
Narrow 10 px shoulders, a short side-parted crop with ears showing, a collared
shirt, hands at the hips and a level stance. No signature prop. Palette swaps
live in bgworker_common.PALETTES; the key layout never changes.
"""
import bgworker_common as common
from bgworker_common import (LEGS_IDLE_N, LEGS_IDLE_S, LEGS_N, LEGS_S, PALETTES, SILHOUETTE_LIT_PAL,  # noqa: F401
                             SILHOUETTE_PAL, SLOTS, lower, make_pal, silhouette, silhouette_lit, stamp, variant,
                             walk_front_back, walk_side)

PAL = common.PAL

# Light comes from the upper left. The side part is on the worker's left.
S = [
    ".......oo.......",
    ".....ooDDoo.....",
    "....oCDDCCBo....",
    "...oCDDCCCBBo...",
    "...oCCBCCBCBo...",
    "...oBCCBBCBBo...",
    "...oBkAkkkkBo...",
    "...olnommomlo...",
    "...olnmmmmmlo...",
    "....ollmmllo....",
    "...osrxnnxrqo...",
    "...osrrxxrrqo...",
    "...osprqrrpqo...",
    "...osprqrrpqo...",
    "...osprqrrpqo...",
    "...omprqrrpmo...",
    "...oloOPPOolo...",
    "....oOPPOPPOo...",
] + LEGS_IDLE_S

N = [
    ".......oo.......",
    ".....ooDDoo.....",
    "....oCDDCCBo....",
    "...oCDCCCCBBo...",
    "...oCCCBBCBBo...",
    "...oCBCCBBBBo...",
    "...oBCBBBCBBo...",
    "...oBCBBBBBBo...",
    "...olBBBBBBlo...",
    "....oBlmmlBo....",
    "...osrxxxxrqo...",
    "...osrrrrrrqo...",
    "...osprrqrpqo...",
    "...osprrqrpqo...",
    "...osprrrrpqo...",
    "...omprrrrpmo...",
    "...oloOPPOolo...",
    "....oOPPOPPOo...",
] + LEGS_IDLE_N

E_HEAD = [
    "......ooo.......",
    ".....oCDDooo....",
    "....oCDDCCCCo...",
    "...oCDDCCCCBBo..",
    "...oCCCCCBBBo...",
    "...oCCCBCBBBo...",
    "...oBCCBlllko...",
    "...oBBBlnomno...",
    "...oBBBlmmmmo...",
    "....oBBlmmlo....",
    "....osrrxxqo....",
    "...osrrrrxrqo...",
]
E_ARMS = (
    [   # neutral: arm hangs at the hip
        "...osrprqqqqo...",
        "...osrprqqqqo...",
        "...osrprqqqqo...",
        "...osrpmmqqqo...",
        "....oOPlmPOo....",
    ],
    [   # arm swung back
        "...osrprqqqqo...",
        "...osprqqqqqo...",
        "...oprqqqqqqo...",
        "...ommqqqqqqo...",
        "...olmPPPPOo....",
    ],
    [   # arm swung forward
        "...osrprqqqqo...",
        "...osrqprqqqo...",
        "...osrqqprqqo...",
        "...osrqqqqmmo...",
        "....oOPPPPlmo...",
    ],
)
E_HEM = "....oOPPPPOo...."

# West is drawn on its own (light stays upper left), not mirrored from east.
W_HEAD = [
    ".......ooo......",
    "....oooCDDo.....",
    "...oCDDCCCCo....",
    "..oCDDCCCCBBo...",
    "...oCCCCCBBBo...",
    "...oCCCBCBBBo...",
    "...olllkBCCBo...",
    "...olnomnBBBo...",
    "...olmmmmBBBo...",
    "....olmmlBBo....",
    "....osxxrrqo....",
    "...osrxrrrrqo...",
]
W_ARMS = (
    [   # neutral
        "...osrrqrpqqo...",
        "...osrrqrpqqo...",
        "...osrrqrpqqo...",
        "...osrrmmpqqo...",
        "....oOPlmPOo....",
    ],
    [   # arm swung back (screen-right)
        "...osrrqrpqqo...",
        "...osrrqqrpqo...",
        "...osrrqqqrpo...",
        "...osrrqqqmmo...",
        "....oOPPPPlmo...",
    ],
    [   # arm swung forward (screen-left)
        "...osrrqrpqqo...",
        "...osrqrpqqqo...",
        "...osqrpqqqqo...",
        "...ommqqqqqqo...",
        "...omlPPPPOo....",
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


# Individual idles (post-review state: the loops have broken, each worker settles into their own pose).
IDLE_VARIANTS = {
    # phone check: both hands up at the chest, the screen content scrolls between frames
    "phone_s": variant(S, {
        12: "...ospggggpqo...", 13: "...osmgjjgmqo...", 14: "...osmgjhgmqo...",
        15: "...ospggggpqo...", 16: "...osoOPPOoqo...",
    }, alt={13: "...osmgjhgmqo...", 14: "...osmgjjgmqo..."}),
    # coffee: a mug in the near hand, the other hand at the hip
    "coffee_s": variant(S, {
        13: "...osriSirpqo...", 14: "...osmfffepqo...", 15: "...osreeerpmo...", 16: "...osoOPPOolo...",
    }),
    # typing at air: both hands in front of the belly, alternating
    "typing_s": variant(S, {
        13: "...osprrmmpqo...", 14: "...ospmmrrpqo...", 15: "...osprqrrpqo...", 16: "...osoOPPOoqo...",
    }, alt={13: "...ospmmrrpqo...", 14: "...osprrmmpqo..."}),
}


# Seated at a desk. Faces S, the camera-side view from behind the desk. The desk-front occluder hides
# rows 15 and below, so hands, phone and mug live in rows 11-14 and the waist and legs below are the
# standing ones. Typing hands alternate rather than rest on the keys, because the keyboard itself is
# hidden behind the monitor housing.
_HIPS = {15: "...osprqrrpqo...", 16: "...osoOPPOoqo..."}
SEATED = {
    "idle": common.seated(S, {**_HIPS, 13: "...osprqrrpqo...", 14: "...ospmrrmpqo..."}),
    "typing": common.seated(S, {**_HIPS, 13: "...ospmrrrpqo...", 14: "...osprrrmpqo..."},
                            alt={13: "...osprrrmpqo...", 14: "...ospmrrrpqo..."}, settle=False),
    "phone": common.seated(S, {**_HIPS, 11: "...osrggggrqo...", 12: "...osmgjjgmqo...",
                               13: "...osmgjhgmqo...", 14: "...osrggggrqo..."},
                           alt={12: "...osmgjhgmqo...", 13: "...osmgjjgmqo..."}, settle=False),
    "coffee": common.seated(S, {**_HIPS, 11: "...osriSirpqo...", 12: "...osmfffepqo...",
                                13: "...osreeerpmo...", 14: "...osprqrrpqo..."}),
}
EXTRA = {f"seated_{k}": {"s": v} for k, v in SEATED.items()}
EXTRA_MS = {f"seated_{k}": (250 if k == "typing" else 500) for k in SEATED}
