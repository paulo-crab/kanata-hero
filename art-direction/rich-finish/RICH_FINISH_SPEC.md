# Rich finish: the art direction update (Mock 2.1)

**Status:** Approved 2026-10-02. The board asked for the world to sit closer to the graphics of reference 08 and for more detail on what is already there, not more objects. The player confirmed the 16 px grid and chose Mock 2.1 as the direction.

**Authority.** This file amends `STYLE_BIBLE.md` where it says so (the amendments are listed in "Rule changes"). Where this file and the bible disagree, this file wins until the bible is next revised. Everything the bible does not mention stays as it was.

**Reference implementation.** The code that drew the mock-ups is in this folder. `m2.build(organic=True)` is the approved Mock 2.1, and the other builds are records of what was tried. Production assets re-use the same recipe; they do not copy these scripts.

## What was decided

| Question | Decision |
| --- | --- |
| Pixel grid | **16 px stays.** 16×16 tiles, 16×24 people, 48×48 portraits, 320×180 view. The finer 32 px grid (Mock 2.4) is rejected. |
| Direction | **Mock 2.1**: vivid palette, deeper darks, leaf-fan foliage and a detailed garden, plus the light and atmosphere of Mock 1. |
| More objects | **No.** Mock 3 (lounge, parcels, extra planters) is not adopted. Room layouts stay as they are. |
| Material detail | **Not adopted** (Mock 2.2: wood grain, brick joints, monitor text, lamp housings, wall seams, slab bevels). It may return later as a separate decision. |
| Wider camera | **Undecided.** It stays the optional whole-number zoom setting described in `docs/game-design.md` (427×240 at ×3 on 1366×768, 480×270 at ×4 on 1920×1080). |

## The finish: what it is made of

### 1. World palette v2

World art (props, kits, landmarks, furniture, foliage, glass, lamps) uses these ramps in place of the matching Orientation ramps in STYLE_BIBLE §3. Stone keeps the §3 values (floor, walls and joints); the table is exact-hex, so builds recolour by exact match.

| Ramp | Replaces (shadow to light) | v2 (shadow to light) | Use |
| --- | --- | --- | --- |
| Ink | `#202337` `#343650` `#535971` `#777A8C` | `#0E1020` `#1C2038` `#3A4160` `#6A7392` | Outline `#0E1020`, cool shadows |
| Wood | `#523D4C` `#85565A` `#BA785F` `#E4AA73` | `#3A2216` `#7C4220` `#B8671F` `#E69A3A` | Desks, benches, counters, bark |
| Glass / water | `#203A50` `#366479` `#5AA3AE` `#A0DDD4` | `#0F3550` `#1D7396` `#3CBAD6` `#A8F0EE` | Windows, screens, pond |
| Garden green | `#21484A` `#326D60` `#5FA06D` `#B2CE78` | `#134A22` `#1F7A2B` `#3FA832` `#7BD23C` | Remapped foliage; leaves use the five tones below |
| Brass / gold | `#705056` `#AC7655` `#E1AC62` `#F5D580` | `#7A4A2A` `#C98A3A` `#FFC83D` `#FFF0A0` | Lamps, door frame, mat |
| Coral | `#71394F` `#B65761` `#E67A70` `#F6B18E` | `#7A2E40` `#C8485A` `#F26A5A` `#FFB38A` | Chairs and seats |

Foliage and garden extras that exist only in v2:

| Name | Hexes | Use |
| --- | --- | --- |
| Foliage outline | `#0B2B17` | Dark edge behind leaves |
| Foliage tones | `#134A22` `#1F7A2B` `#3FA832` `#7BD23C` `#C4F061` | Five tones, deepest to sunlit tip |
| Planter | `#16223C` `#26395E` `#3D5C8E`, lit lip `#6F92C4`, bolts `#8FB0DA` | Blue planters, as in 08 |
| Mulch and accents | `#5A3418`, `#9A5A22`, `#E8892B` | Soil, mulch, orange flecks |
| Rocks | `#2B2F3A` `#565B66` `#8A8F99` `#B8BDC6` | Grey rocks (replace the navy ones) |
| Moss | `#4E8F2E` | Rock caps |
| Flowers | petals `#FFF6EA`, shade `#E9D2C0`, centre `#E8892B`, pink `#F7B6C8`, yellow `#FFD84A` | Garden flowers |

**Marker safety, checked.** Every v2 step is at least CIE76 dE 10 from the four UI marker hexes (`#19AFA2`, `#EC776D`, `#9876D5`, `#E6B750`). The old coral step `#E67A70` was dE 4.0 from the conversation marker, so v2 improves on it. Markers still keep their distinct shapes.

### 2. Foliage: leaf fans

Foliage is built from pointed leaf fans, not blobs.

- A fan is `count + 2` leaves radiating from one centre at slightly jittered angles. Each leaf is a teardrop (length `L` = `rad` × 0.95–1.25, half-width about `0.36 L`) with a one-pixel vein along its axis.
- Each leaf uses five tones lit from the upper left: highlight on the lit side, the lightest tone on the tip, and shade on the far side. A dark `#0B2B17` edge separates leaves where they overlap, and the lit upper-left edge has no ring.
- **Two layers.** A shaded back layer (one tone down, offset about 0.6 px, 0.9 of the radius) sits behind the lit front layer.
- **Large canopies** are built from seven smaller fans (radius about 0.5 of the canopy radius), not from one big fan.
- **Sparkles.** About 30% of the upper-left edge pixels of the front layer become `#C4F061`, single pixels on sunlit tips. This is an allowed single-pixel use (see "Rule changes").

### 3. The garden set

The Orientation garden has these parts, all inside the existing garden footprint:

- **Tree.** A trunk with a root flare and roots creeping along the bed, bark streaks (about 16% of trunk pixels in the darkest bark tone), a lit left edge in the highest wood tone, and two short limbs that show through gaps in the canopy.
- **Pond.** Ripple arcs on the lit side in `#A8F0EE`, a sheen band in `#3CBAD6`, lily pads, and one lily flower (pink with an orange centre).
- **Rocks.** Grey, shaded, with a moss cap and a one-pixel crack.
- **Ground.** A deep green bed (`#134A22`), shaded under the canopy in dark green (never navy), with grass tufts of three blades.
- **Flowers.** White flowers with orange centres, and every second one has a pair of yellow dots.
- **Benches** on both sides of the garden (vertical planks: three wood tones, a lit left edge), **lamps** at three corners.
- **Planters** everywhere are the blue planters: a lit top lip, a shaded right side and base, a metal band with two bolts, orange mulch under a leaf fan with two orange flecks.

### 4. Light and atmosphere

Applied as passes after the room is drawn and recoloured, in this order. All are flat colour steps; none is a gradient.

1. **Slab variation.** On the 32 px running-bond slabs, 28% of slabs drop a step (add -7, -9, -12) and 22% rise one (add +5, +5, +4). Sparse wear: 1.8% of plain-floor pixels take add -14, -16, -20.
2. **Cast shadows.** Every non-floor object casts a flat shadow patch onto the floor, offset 4 px right and 3 px down, with multipliers 0.80, 0.78, 0.86 (a warm floor shadow tinted cool). The east wall mass casts none.
3. **Canopy shadow.** The tree casts a larger patch, offset 10 px right and 8 px down, multipliers 0.84, 0.84, 0.90, onto the floor only.
4. **Lamp glow.** Two hard-edged steps on the floor around each lamp, on an ellipse with vertical stretch 1.25: radius 26 adds (9, 6, -3), radius 12 adds (16, 11, -6).
5. **Window light.** Diagonal bands from the north windows at slope 0.5 down to y 150, width 26. The band adds (11, 9, 2) and its centre half adds a further (9, 7, 1). The reference uses three windows (x 38, 212, 244).
6. **Deeper darks.** The ink ramp is deeper (v2 above). The darkest pixel in a frame is about 9% lightness, against 17% before.

## Rule changes

These amend `STYLE_BIBLE.md` (the bible now points here).

| Bible rule | Now |
| --- | --- |
| §3 outline default `#202337` | **`#0E1020`** for world art and for every sprite and prop. |
| §3 the 32-colour starting palette | Stays the **base** for stone and for sprite ramps that are not listed above. World art uses the v2 ramps. |
| §5 and §3 "2–3 tones per part", "3–4 tones per material" | Unchanged for people. **Foliage may use five tones** and the garden extras above. |
| §1 "no stray single-pixel noise" | Allowed, nothing else: **floor wear specks** (1.8% of plain floor) and **foliage sparkle pixels** on sunlit leaf tips. |
| §1 "no gradients" | Unchanged. Slab tone drift, shadows and glows are flat steps. |
| §7 contact shadows `#535971` `#343650` `#202337` | Renderer shadows under people and glitches become `#3A4160` (outer) and `#1C2038` (core). |
| §7 lamps "one or two hard-edged glow steps" | Unchanged, now applied on the floor around lamps (two steps). |
| §7 foliage "3–4 value groups" | Replaced by the five-tone leaf-fan recipe. |
| §6 "ordinary floors stay simpler" | Unchanged. Slab drift is a subtle tone change, not texture. |

## Not part of the finish

- More set pieces, extra planters or lounges (Mock 3). Layouts stay as drawn.
- Material detail: wood grain, brick joints on the rim, wall panel seams, slab bevels, monitor text, keyboards, lamp housings (Mock 2.2).
- A finer pixel grid (Mock 2.4), and any change of the default camera.
- Stepped edge falloff (the vignette in Mock 1). It was not in Mock 2.1.

## How to produce new art

1. **Read** this file, `STYLE_BIBLE.md` and the asset's brief.
2. **People and props.** Keep the key-grid modules. Change the outline key to `#0E1020`, and move the ink shoe ramp to the v2 ink ramp (`#1C2038` `#3A4160` `#6A7392`). Clothing, skin and hair ramps stay as approved. Re-run `check_gate1.py <module>`.
3. **Foliage and planters.** Use the leaf-fan recipe (`leaves_v4`, `pot_v4`, in `art_v4.py`) and the v2 colours; do not draw leaves by hand as blobs.
4. **Rooms.** Draw the room, recolour by exact hex to v2 (`art_v2.remap`), then run the light passes in the order above (`passes.py`, `m2.build`). Apply the garden set to every landmark that has plants or water.
5. **Other districts.** The district ramps in STYLE_BIBLE §3 stay. Ink is shared, so those rooms take the v2 ink ramp automatically. Their foliage ramps gain a fifth tone (a lighter tip step one notch above step 3) and a darker edge, and use the same leaf fans. Light passes are identical. Run `check_palettes.py` after adding any step.
6. **Check.** The person checker, `check_atlas.py`, `check_palettes.py`, and a visual review of the room at ×4 on 1366×768 against reference 08, using the comparison sheets in this folder.

## What this changes in existing assets

Every approved asset predates the finish. Nothing is wrong with it; it needs a re-render, tracked in the OpenSpec change `adopt-rich-finish`:

| Asset family | What changes |
| --- | --- |
| Orientation, Records, Systems, Night Shift and Executive kits and reference rooms | Foliage, planters, light passes, v2 ink; Orientation also gets the v2 wood, glass, brass and coral ramps |
| Orientation garden landmark and its quest states | Garden set above |
| All person sprites, background workers, atlases | Outline and renderer-shadow colours only |
| Glitches, Pace signage | Outline colour only |
| Portraits | Outline colour reviewed for consistency |
| UI kit world backgrounds | Re-rendered from the new room |
| `ART_HANDOFF.md` and the checkers | Colour tables and the outline rule |

## Files in this folder

| File | What it is |
| --- | --- |
| `m2.py` | `build(organic=True)` is Mock 2.1; the other flags record the other mocks |
| `passes.py` | The light passes: slab variation, cast shadows, lamp glow, window light |
| `art_v2.py`, `art_v4.py` | Palette remap, leaf fans, planters, trunk, pond, rocks, flowers |
| `base.py` | Renders today's approved Orientation scene as the starting point |
| `art_v3.py`, `m3_density.png` | Mock 3 (density), kept as a record; **not adopted** |
| `hr.py`, `m2_4_finer_grid_garden.png` | Mock 2.4 (32 px grid), kept as a record; **not adopted** |
| `sheets.py`, `sheets2.py`, `hr.py` | The comparison sheets (and the 32 px record) |
| `richness-comparison.png`, `detail-mocks.png` | Reference 08, today and the mocks side by side |
| `m2_1_organic.png` | The approved mock at ×4, full frame |
| `camera-default-vs-wide.png` | The camera comparison, kept for the open decision |

Run any script from this folder with the project's virtualenv (`python3 m2.py`); they import from `../gate1`, `../scale-test`, `../cast` and `../kit`.
