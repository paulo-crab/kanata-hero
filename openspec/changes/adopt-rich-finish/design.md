# Design

## Context

See proposal.md for motivation and `art-direction/rich-finish/RICH_FINISH_SPEC.md` for the finish itself. Today every kit, room and sprite is drawn by Python modules that hold exact hexes (`art-direction/kit/*_kit.py`, `gate1/environment.py`, `cast/*_sprites.py`) and are built by `build_all.py`. The finish was proved on one room by a post-process plus a few replaced drawing functions in `art-direction/rich-finish/` (`m2.build(organic=True)`), without touching the approved assets.

## Goals / Non-Goals

**Goals:**
- Re-render every approved asset to the finish with one shared implementation, so no two kits drift.
- Keep every contract that developers use: anchors, footprints, collision, layers, timing, formats.
- Keep the build deterministic and the checkers green.

**Non-Goals:**
- No set pieces or lounges (planters and benches only, on free cells), no material detail, no finer grid, no camera change.
- No change to clothing, skin or hair ramps, or to the UI tokens.

## Decisions

1. **Promote the reference implementation into one shared module** (`art-direction/kit/rich_finish.py`): the v2 remap, leaf fans, planters, garden parts and light passes. Kits call it; nothing copies the mock scripts. *Alternative:* edit each kit by hand, which would drift.
2. **Recolour by exact match, then light.** Rooms are drawn, remapped by exact hex to v2, then lit, as in the reference build. Sprites are recoloured at the source (the outline key and ink shoe ramp), not in a post-process, so atlases stay clean.
3. **Orientation first.** It proves the shared module against the approved room and the approved mock before the four districts follow.
4. **District foliage gets a fifth tone, not a new palette.** The district ramps stay as approved; each adds a sunlit tip and an edge tone, checked by the palette checker.
5. **Light passes are part of the room render, not the atlas.** Atlas entries stay unlit and reusable; the reference-room renderer applies the passes. Developers who composite rooms at runtime follow the pass order in the spec.
6. **Regression strategy.** `build_room.py` currently proves the rebuilt Orientation room is pixel-identical to the approved one. It is rebased onto the Mock 2.1 render, so the zero-difference test protects the new look.

## Risks / Trade-offs

- [Vivid world makes unchanged sprites look dull] → Review every character in the re-rendered rooms at ×4 (task 5.1) and record any ramp changes as a Director decision before changing them.
- [Marker colours drift closer to world colours] → The v2 ramps were checked at dE ≥ 10 and markers keep their shapes; the palette checker is extended so it stays true.
- [Parallel art branches (quest props, glitch variants, poses) touch the same kits] → Merge them first, then re-render once; do not recolour files that are still changing.
- [Light passes read differently over new room layouts] → Parameters are fixed in the spec; a layout change re-runs the passes, it does not retune them.

## Open Questions

- Whether the wider camera becomes the default. It changes none of the work in this change.
