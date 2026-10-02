# Spec Delta

## Purpose

Defines the rich finish for world art: a vivid palette, leaf-fan foliage, a detailed garden and flat-step lighting on the existing 16 px grid, so every room reads closer to the approved reference without adding objects.

## ADDED Requirements

### Requirement: Vivid world palette
World art SHALL use the rich-finish v2 ramps for ink, wood, glass, garden green, brass and coral, and the ink ramp SHALL be shared by every district. The outline default SHALL be `#0E1020`. Stone SHALL keep its base values. Every v2 step SHALL be at least CIE76 dE 10 from each of the UI marker hexes (`#19AFA2`, `#EC776D`, `#9876D5`, `#E6B750`).

#### Scenario: Marker distance check
- **WHEN** the palette checker runs on the v2 ramps
- **THEN** no step is within dE 10 of a marker hex and the check passes

#### Scenario: Deeper darks
- **WHEN** a finished room frame is measured
- **THEN** its darkest pixel is no lighter than 10% HSL lightness

### Requirement: Leaf-fan foliage
Foliage SHALL be built from pointed leaf fans in five tones, with a dark edge between overlapping leaves, a shaded back layer behind a lit front layer, and a lit upper-left edge without a ring. Large canopies SHALL be built from several smaller fans. Foliage SHALL NOT be drawn as smooth blobs.

#### Scenario: Reviewing a plant
- **WHEN** a planter plant is viewed at ×4
- **THEN** individual leaves, a highlight on the sunlit side and a darker edge between leaves are visible

### Requirement: Detailed garden set
A garden landmark SHALL include a trunk with a root flare, bark streaks, a lit left edge and limbs that show through the canopy; a pond with ripple arcs, a sheen band and a lily with a flower; grey rocks with a moss cap and a crack; a deep green bed shaded in dark green under the canopy; grass tufts; white flowers with orange centres; benches either side; and lamps at its corners. Planters SHALL be blue with a lit lip, a metal band with bolts, orange mulch and a leaf fan.

#### Scenario: Garden quest states
- **WHEN** the garden switches from its before to its after state
- **THEN** it uses the same parts, nothing shifts by a pixel, and at least two visible things change

### Requirement: Flat-step light passes
Rooms SHALL be lit by passes applied after the room is drawn and recoloured, in this order: slab tone drift with sparse floor wear; a cast shadow patch from every non-floor object; a larger canopy shadow from trees; two warm glow steps on the floor around each lamp; diagonal window-light bands. Every pass SHALL use flat colour steps. The east wall mass SHALL cast no shadow.

#### Scenario: No gradients
- **WHEN** a lit room is audited
- **THEN** every pixel belongs to a flat step and no pixel is blended between steps

### Requirement: Limited single-pixel noise
The only permitted isolated single pixels besides eyes, sparks, buttons and glints SHALL be floor wear specks (at most 2% of plain floor pixels) and sparkle pixels on sunlit leaf tips. Faces, outlines, UI and every other material SHALL NOT use single-pixel noise.

#### Scenario: Floor speck budget
- **WHEN** a plain floor area is measured
- **THEN** wear specks cover no more than 2% of its pixels

### Requirement: Re-render preserves metadata
Re-rendering an asset for the rich finish SHALL NOT change its frame size, anchor, footprint, collision mask, draw layer, animation timing or file format. Only colours, foliage and light passes change.

#### Scenario: Atlas diff
- **WHEN** a kit atlas JSON is compared before and after its re-render
- **THEN** every footprint, collision string, layer, anchor and animation timing is identical, and only entry rectangles that moved because of repacking differ

### Requirement: Modest dressing only
The rich finish MAY dress review rooms with planters and benches on free cells, clear of route corridors and without changing level data or gameplay footprints, to reach the dressing level of Mock 2.1. It SHALL NOT add set pieces, lounges or other furniture, and SHALL NOT add material detail such as wood grain, brick joints, wall seams, monitor text or slab bevels.

#### Scenario: Layout comparison
- **WHEN** a re-rendered room's placements are compared with the approved layout
- **THEN** the only additions are planters and benches, and collision of every route cell and every level-data footprint is unchanged
