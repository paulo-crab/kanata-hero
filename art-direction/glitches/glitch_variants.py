"""Glitch variants and the district contract, as data (no new silhouettes).

Status: Approved by the director 2026-10-02. Spec: GLITCHES_SPEC.md ("Variants and districts").

Three tables, all written into glitches-atlas.json by build_glitches.py:

  PALETTE_VARIANTS  alternate violet step sets. The sprites are drawn in the standard violet
                    (#413755 #67547C #9477AF #C3A6D6); a variant is an exact hex swap of those four
                    steps. Each has a second ramp, `dark_steps`, for the dark Night Shift floor.
  BEHAVIOURS        how a glitch roams: speed, path shape, pause pattern, misregister cadence and
                    amplitude. They reuse the roam and misregister frames already drawn.
  DISTRICTS         which archetypes, palettes and behaviours may appear in which district, from which
                    level, the intensity ramp, and the district's first glitch. Keyed by district id.

Everything here is a rule or a number: the checks (check_glitches.py) validate it against the
sprites, the district palettes and GLITCHES_SPEC.md.
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "palettes"))
import district_palettes as dp  # noqa: E402

STANDARD_VIOLET = list(dp.VIOLET)   # a, b, c, d: contour, fill, glow, hot core

# ------------------------------------------------------------------ palette variants
# `steps` for light floors (Orientation, Records, Systems, Executive), `dark_steps` for the Night Shift
# floor (#364049 / #4C5865), where the standard ramp's fill falls below 1.1:1 against the floor.
# `duel` is the repair-duel kind the variant signals (docs/game-design.md: fix a token, choose a
# route, or edit a code fragment). Colour is a second cue: the shapes already say "glitch".
PALETTE_VARIANTS = {
    "standard": {
        "name": "Standard violet", "duel": "token",
        "steps": ["#413755", "#67547C", "#9477AF", "#C3A6D6"],
        "dark_steps": ["#6D5C8E", "#9885AD", "#B8A5CA", "#DECEE8"],
        "note": "The approved ramp, as drawn. A token repair: fix a mistyped word, label or address.",
    },
    "plum": {
        "name": "Plum", "duel": "route",
        "steps": ["#553458", "#80507D", "#B373AC", "#D9A3CE"],
        "dark_steps": ["#8E5793", "#B181AE", "#CDA2C8", "#EACCE4"],
        "note": "Warmer violet (hue +36 degrees). A route repair: choose the path through the records or the machine.",
    },
    "dusk": {
        "name": "Dusk", "duel": "code",
        "steps": ["#333459", "#534E82", "#7B71B5", "#AFA2DA"],
        "dark_steps": ["#555795", "#8480B2", "#A8A1CE", "#D3CCEB"],
        "note": "Cooler violet (hue -22 degrees). A code-fragment repair: edit a line or an expression.",
    },
}
# Violet hue band the variants must stay in (degrees), and the least distance from every UI marker (CIE76).
VIOLET_HUE_BAND = (225, 320)
MIN_DE_MARKER = 10.0
MIN_DE_VARIANT = 9.0        # from the standard step, on the fill and glow steps
DARK_FLOORS = {"fill": "#4C5865", "mid": "#364049"}   # Night Shift floor steps 3 and 2
DARK_MIN_CONTRAST = {"fill_b": 1.9, "mid_b": 2.8, "fill_c": 2.9}   # WCAG contrast of dark_steps b, c on the floor

# ------------------------------------------------------------------ behaviour variants
# roam_ms: milliseconds per roam frame, per archetype (every value a multiple of the 40 ms tick;
#          the baseline is 120 / 200 / 120). The frames and the px moved per frame do not change,
#          so the speed is move_px_per_cycle (4 px) over 4 frames x roam_ms.
# path:    shape "hover" patrols out and back within lane_px of its home cell; "line" patrols a lane of
#          lane_px; "edge" is a line that hugs a wall or furniture edge. The lane never crosses the
#          main route and never blocks a one-cell passage.
# pause:   after `after_cycles` full roam cycles, hold the roam rest frame (frame 0) for hold_ms. None = never.
# misregister: every_ms [lo, hi] draws a random wait between flickers (None = never on its own);
#          on_pause fires one flicker burst at the start of each pause; amplitude picks the frame
#          sequence below. Contact before the duel always plays CONTACT_FRAMES, whatever the variant.
AMPLITUDE_FRAMES = {"low": [0], "normal": [0, 1], "high": [0, 1, 0, 1]}   # misregister frame indices, 80 ms each
CONTACT_FRAMES = [0, 1]
BEHAVIOURS = {
    "drift": {
        "name": "Drift", "tone": "calm",
        "roam_ms": {"stapler": 160, "chair": 280, "form": 160},
        "path": {"shape": "hover", "lane_px": 24},
        "pause": {"after_cycles": 2, "hold_ms": 1200},
        "misregister": {"every_ms": [3600, 6000], "on_pause": False, "amplitude": "low"},
        "note": "Slow and tidy: a short hover with long rests and a rare, small flicker. The welcoming first meeting.",
    },
    "patrol": {
        "name": "Patrol", "tone": "uncanny",
        "roam_ms": {"stapler": 120, "chair": 200, "form": 120},
        "path": {"shape": "line", "lane_px": 64},
        "pause": None,
        "misregister": {"every_ms": [1200, 2400], "on_pause": False, "amplitude": "normal"},
        "note": "The approved baseline: a steady lane patrol and a flicker every 1.2-2.4 s.",
    },
    "stutter": {
        "name": "Stutter", "tone": "uncanny",
        "roam_ms": {"stapler": 120, "chair": 200, "form": 120},
        "path": {"shape": "line", "lane_px": 48},
        "pause": {"after_cycles": 3, "hold_ms": 480},
        "misregister": {"every_ms": [2400, 3600], "on_pause": True, "amplitude": "high"},
        "note": "Three smooth cycles, then it freezes and misregisters twice before moving on: the building hesitating.",
    },
    "lurk": {
        "name": "Lurk", "tone": "quiet",
        "roam_ms": {"stapler": 200, "chair": 280, "form": 200},
        "path": {"shape": "edge", "lane_px": 32},
        "pause": {"after_cycles": 1, "hold_ms": 2400},
        "misregister": {"every_ms": [4800, 7200], "on_pause": False, "amplitude": "high"},
        "note": "Slow, hugging the edge of a lamp pool, long stillness and a rare large flicker. The quiet floor's uncanny.",
    },
    "settle": {
        "name": "Settle", "tone": "relief",
        "roam_ms": {"stapler": 240, "chair": 360, "form": 240},
        "path": {"shape": "hover", "lane_px": 16},
        "pause": {"after_cycles": 1, "hold_ms": 3200},
        "misregister": {"every_ms": None, "on_pause": False, "amplitude": "low"},
        "note": "Barely moving and never flickering unprompted: a glitch that wants to be fixed. Misregisters on contact only.",
    },
}

# ------------------------------------------------------------------ the district contract
# Per district id: tone and intensity (1 calm, 2 uncanny begins, 3 peak, 4 deepest and quietest, back
# to 1 for relief), the most live glitches in one room, and per archetype the first level it may appear
# in, the palettes and behaviours allowed. `palette_from_level` / `behaviour_from_level` hold back a
# variant until the level that needs it. `first_glitch` is the district's first encounter.
# `quiet_levels` are levels that contain no glitch at all (a safe space).
DISTRICTS = {
    "orientation": {
        "levels": [1, 6], "tone": "calm", "intensity": 1, "max_per_room": 1,
        "archetypes": {
            "form": {"from_level": 1, "palettes": ["standard"], "behaviours": ["drift"]},
            "stapler": {"from_level": 4, "palettes": ["standard"], "behaviours": ["drift"]},
        },
        "palette_from_level": {"standard": 1},
        "behaviour_from_level": {"drift": 1},
        "first_glitch": {"level": 1, "archetype": "form", "palette": "standard", "behaviour": "drift"},
        "quiet_levels": [],
        "note": "Level 01's harmless paper fold, repaired after the movement tutorial; a stapler at a desk edge from 04. "
                "No chair shadow: the wrong shadow is the uncanny one and waits for Records.",
    },
    "records": {
        "levels": [7, 11], "tone": "uncanny", "intensity": 2, "max_per_room": 2,
        "archetypes": {
            "form": {"from_level": 8, "palettes": ["standard", "plum"], "behaviours": ["drift", "patrol"]},
            "chair": {"from_level": 9, "palettes": ["standard", "plum"], "behaviours": ["drift", "patrol"]},
            "stapler": {"from_level": 10, "palettes": ["standard"], "behaviours": ["patrol"]},
        },
        "palette_from_level": {"standard": 8, "plum": 10},
        "behaviour_from_level": {"drift": 8, "patrol": 10},
        "first_glitch": {"level": 8, "archetype": "form", "palette": "standard", "behaviour": "drift"},
        "quiet_levels": [7],
        "note": "Filing Drift: addresses and labels drift, and so does a folded form. Level 07's door has no glitch "
                "(its challenge is the door itself). Plum arrives with the long report's route choice.",
    },
    "systems": {
        "levels": [12, 16], "tone": "uncanny", "intensity": 3, "max_per_room": 3,
        "archetypes": {
            "stapler": {"from_level": 12, "palettes": ["standard", "plum", "dusk"], "behaviours": ["patrol", "stutter"]},
            "form": {"from_level": 13, "palettes": ["standard", "plum"], "behaviours": ["patrol", "stutter"]},
            "chair": {"from_level": 14, "palettes": ["standard", "plum", "dusk"], "behaviours": ["patrol", "stutter"]},
        },
        "palette_from_level": {"standard": 12, "plum": 13, "dusk": 15},
        "behaviour_from_level": {"patrol": 12, "stutter": 14},
        "first_glitch": {"level": 12, "archetype": "stapler", "palette": "standard", "behaviour": "patrol"},
        "quiet_levels": [],
        "note": "The peak: the routing machine duplicates work, so all three archetypes and the most per room. "
                "Dusk (code) waits for the Formula Room (15); the stutter starts at the Alarm Glyphs (14).",
    },
    "nightshift": {
        "levels": [17, 19], "tone": "quiet", "intensity": 4, "max_per_room": 2,
        "archetypes": {
            "chair": {"from_level": 18, "palettes": ["standard", "plum", "dusk"], "behaviours": ["lurk", "stutter"]},
            "form": {"from_level": 19, "palettes": ["standard", "plum", "dusk"], "behaviours": ["lurk", "stutter"]},
            "stapler": {"from_level": 19, "palettes": ["standard", "plum", "dusk"], "behaviours": ["lurk"]},
        },
        "palette_from_level": {"standard": 18, "plum": 18, "dusk": 19},
        "behaviour_from_level": {"lurk": 18, "stutter": 19},
        "first_glitch": {"level": 18, "archetype": "chair", "palette": "standard", "behaviour": "lurk"},
        "quiet_levels": [17],
        "dark_floor": True,
        "note": "The deepest uncanny at the lowest volume: fewer per room, slow, in the edges of lamp pools, drawn in the "
                "dark_steps ramp. The break room and vestibule (17) are glitch-free: a safe place to learn the exit.",
    },
    "executive": {
        "levels": [20, 20], "tone": "relief", "intensity": 1, "max_per_room": 1,
        "archetypes": {
            "form": {"from_level": 20, "palettes": ["standard"], "behaviours": ["settle"]},
            "chair": {"from_level": 20, "palettes": ["plum"], "behaviours": ["settle"]},
            "stapler": {"from_level": 20, "palettes": ["dusk"], "behaviours": ["settle"]},
        },
        "palette_from_level": {"standard": 20, "plum": 20, "dusk": 20},
        "behaviour_from_level": {"settle": 20},
        "first_glitch": {"level": 20, "archetype": "form", "palette": "standard", "behaviour": "settle"},
        "branches": {"The Name": "form", "The Route": "chair", "The Count": "stapler"},
        "quiet_levels": [],
        "note": "Relief: one still glitch per incident branch, each in the palette of its duel (token, route, code), "
                "and each stays behind as an ordinary prop that the restored atrium keeps.",
    },
}

# Ordinary props and the district: the stapler and the sheet are neutral office colours and need no
# change. The chair's upholstery is the Orientation coral; every district kit recolours its chair by the
# same exact swap, so the renderer applies that swap to every chair frame (ordinary, roam and repaired):
# coral steps 1..3 become steps 1..3 of the ramp named here. Violet is never touched by it.
CHAIR_SWAP_FROM = dp.ORIENTATION_EXTRA["coral"][1:4]
CHAIR_RAMP = {"orientation": None, "records": "glass", "systems": "glass", "nightshift": "wall", "executive": "wall"}


def chair_swap(district):
    """{coral hex: district hex} for steps 1..3, or {} for Orientation (the coral chair as drawn)."""
    role = CHAIR_RAMP[district]
    if role is None:
        return {}
    ramp = dp.DISTRICTS[district][role]
    return {src: ramp[1 + i] for i, src in enumerate(CHAIR_SWAP_FROM)}


def violet_for(variant, dark=False):
    v = PALETTE_VARIANTS[variant]
    return v["dark_steps" if dark else "steps"]


def palette_swap(variant, dark=False):
    """{standard hex: variant hex} for the four violet steps."""
    return dict(zip(STANDARD_VIOLET, violet_for(variant, dark)))


def expand_misregister(behaviour):
    m = dict(BEHAVIOURS[behaviour]["misregister"])
    m["frames"] = AMPLITUDE_FRAMES[m["amplitude"]]
    return m
