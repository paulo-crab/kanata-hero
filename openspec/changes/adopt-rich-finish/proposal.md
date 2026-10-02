# Proposal

## Why

The board reviewed the approved art against reference 08 and asked for a richer ambience: the world closer to 08's graphics, with more detail on what exists and no extra objects. The art director measured the gap (washed-out greens, shallow darks, no cast shadows or window light, flat foliage) and mocked three directions on the 16 px grid. The player confirmed 16 px and chose Mock 2.1. The direction is written down in `art-direction/rich-finish/RICH_FINISH_SPEC.md`; every approved asset predates it and needs a re-render before developers build on it.

## What Changes

- The world palette moves to the vivid v2 ramps (ink, wood, glass, green, brass, coral) with deeper darks and a `#0E1020` outline. Stone is unchanged.
- Foliage becomes leaf fans in five tones. The Orientation garden gets bark, limbs, pond ripples, mossy grey rocks, white flowers, benches and blue planters.
- Rooms get light passes: slab tone drift, cast shadows, a canopy shadow, lamp glow and window light, all in flat steps.
- Two single-pixel uses become allowed: floor wear specks and sunlit leaf tips.
- All existing kits, rooms, sprites, shadows and handoff tables are re-rendered or recoloured. Footprints, collision, anchors, layers and timing do not change.
- Not adopted: set pieces or lounges, material detail (wood grain, brick joints, monitor text), a finer pixel grid. Undecided and out of scope: a wider default camera.

## Capabilities

### New Capabilities
- `rich-finish`: the vivid world palette, leaf-fan foliage, garden set, light passes and single-pixel exceptions that every world asset follows, and the rule that a re-render never changes metadata.

### Modified Capabilities

None. The amended wording in `art-style-foundation` (palette, outline, hard-pixel rule) is edited directly in the unarchived change `complete-art-production`, because `openspec/specs/` is still empty.

## Impact

- Source modules under `art-direction/kit/`, `art-direction/cast/`, `art-direction/gate1/`, `art-direction/glitches/`, `art-direction/pace/`, `art-direction/palettes/`, `art-direction/portraits/` and `art-direction/ui-kit/`, and their generated PNG, GIF and JSON files.
- `art-direction/ART_HANDOFF.md` colour tables, `build_all.py` and the checkers.
- Branches with art work in flight (quest props, glitch variants, Vale and Hal poses) must merge in an order that avoids recolouring files twice.
- No game code.
