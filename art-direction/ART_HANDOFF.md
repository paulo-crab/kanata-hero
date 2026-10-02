# Kanata Hero: art handoff for developers

**Status:** approved art set, 2026-10-02. This is the single entry point for developer agents building the browser game described in `docs/game-design.md`. It indexes every approved asset, explains each file format, and says how to rebuild everything. Rules live in `art-direction/STYLE_BIBLE.md`; the capability contracts are the five specs of the OpenSpec change `complete-art-production` (`art-style-foundation`, `character-sprites`, `environment-kit`, `ui-presentation`, `art-asset-handoff`).

You should never need to invent a visual. If something you need is missing, it is a gap in this handoff: raise it, don't draw it.

## 1. Ground rules for the renderer

- **Grid and view.** 16×16 px tiles, a 320×180 logical view, nearest-neighbour integer zoom only: ×4 on 1366×768 (a 1280×720 stage, letterboxed) and ×6 on 1920×1080. An optional wider view is 427×240 at ×3. Never scale fractionally or smooth.
- **Draw order** (STYLE_BIBLE §6): `floor` → `rear_wall` → `floor_marking` → `rear_prop` → `shadow` → `actor` → `front_prop` → `light` → DOM UI. Within `rear_prop`, `actor` and `front_prop`, sort by the anchor's y (entries with `y_sort: true`). No parallax or horizon layer.
- **Contact shadows** under people and glitches are drawn by the renderer at the anchor, not baked into frames (`#535971` outer, `#343650` core; see `gate1/build_gate1.py` `contact_shadow`). Environment props bake theirs (`contact_shadow` rect in the atlas entry).
- **Night Shift rim pass.** Cool moonlight on the open floor; where a warm source lights someone (a lamp pool, Ada's lantern) the warm edge is limited to the head and shoulders (player decisions 2026-10-02; the warm `#F9D79A` rim everywhere read as a selection highlight near discovery gold). The rule is per pixel and reads the scene under the sprite frame: for each upper-left silhouette pixel (a transparent pixel above or to its left), take the background pixel at that transparent neighbour (above, else left). (1) Moonlight: recolour the pixel to `#8E96B8` (glass step 2, `NIGHT_RIM` in `palettes/district_palettes.py`) only if it is `#202337` or below 3:1 against that background AND the rim contrasts with it more than the pixel does; on the slate floor (`#4C5865`) it shows (2.49:1 against 2.13:1). (2) Warm light: if the background is a lamp-pool colour (accent steps 0 and 1) and the pixel is on sprite rows 0-12 (`WARM_RIM_ROWS = 13`, head and shoulders), ink becomes `#F9D79A` when that reaches 2.5:1 against the pool (2.68:1 on `#B8745A`); rows 13-23 keep the ink outline (4.19:1). The reference implementation is `night_rim(sprite_rgba, background_rgb_patch, rim_hex)` in `palettes/night_rim.py` (also `nightshift_kit.night_rim`; `night_rim_on_scene` cuts the patch from the canvas). Pixels that are already `#F9D79A` (Ada's baked lantern rim, key `R`, now on the lantern side of her head and shoulders, rows 5-10) are left alone, and the landmark's window silhouettes keep their own warm rim (they are backlit by the lit room). Props get a silver top-left edge (`#D0D4E4`) instead, so people and furniture never share an edge colour. See `cast/ADA_SPEC.md`, `kit/NIGHTSHIFT_KIT_SPEC.md` and `palettes/PALETTES_SPEC.md`.
- **Lights** with `composite.mode: "where_color"` paint only over pixels of the given floor colour (lamp glows never wash over joints or props).
- **Colour meaning.** Teal `#19AFA2` terminals, coral `#EC776D` conversations, violet `#9876D5` glitches, gold `#E6B750` opened routes. These are UI marker hexes and never appear in world art. Markers are also distinct by shape (speech bubble, monitor, diamond with doorway, folded page); see `ui-kit/COMPONENTS.md`.
- **Reduced motion.** Hold idle frame 0 instead of looping idles, and hold Ivo's tablet flash on its dim frame.

## 2. Anchors

| Asset family | Anchor | Meaning |
| --- | --- | --- |
| People (16×24) | `feet_bc` (8, 24) | The pixel edge between columns 7 and 8, under row 23. Place it on the foot position. The planted foot is always on row 23. |
| Glitches | `base_bc` (w/2, h) | Bottom-centre pixel edge of the frame. |
| Environment entries | `anchor` [x, y] in the entry | Sprite-local point used for y-sorting; `footprint.origin_px` places the sprite relative to its footprint's top-left cell. |
| Pace signage | `footprint_bl` | Bottom-left pixel corner of the footprint. |
| Portraits (48×48) | top-left | The top-left of the 48×48 cell sits on the dialogue panel's portrait slot, at world zoom (192×192 CSS px at ×4). |

## 3. File formats

### 3.1 Person sprite atlases (`cast/<name>-atlas.png` + `.json`)

PNG, transparent background, 16×24 frames on a fixed grid. Rows are S N E W idle, then S N E W walk, then the `EXTRA` sets in source order. JSON:

```json
{"frame": {"w": 16, "h": 24}, "anchor": {"name": "feet_bc", "x": 8, "y": 24},
 "footprint_cells": [1, 1],
 "animations": {"ivo_walk_e": {"row": 6, "frames": 4, "ms": 133, "px_per_frame": 8, "contact_frames": [0, 2]}, "…": {}},
 "shadow": "drawn by the renderer at the anchor, not baked into frames"}
```

Animation names are `<name>_<set>_<facing>`: `idle` (2 × 500 ms, loop), `walk` (4 × 133 ms, loop, 8 px per frame, 2 cells per cycle), `interact` (2 × 250 ms, once), `react_<mood>` (3 × 300 ms, once, hold the last frame), plus character sets (Ivo `wave`, `nod`, `laugh`, `tablet_flash`; Engineer `turn_*`; Noor `posture_upright`). Each entry carries its own `ms` and, for extras, the play mode from the module's `EXTRA_MODE`.

The Engineer's full atlas is `gate1/engineer-full-atlas.png`/`.json` (built by `cast/build_cast.py engineer`). `gate1/engineer-atlas.*` is the Gate 1 idle and walk subset with identical rows 0–7.

**Avatar customization** is a ramp swap: replace the hexes of the `hair`, `skin`, `jacket` and `trousers` slots (`SLOTS` in `gate1/engineer_sprites.py`) on the same frames. The opaque mask never changes. Customization ramps obey the marker rules (teal-hued steps ≤ 60% saturation, no violet).

### 3.2 Background workers (`cast/bgworker_a-atlas.*`, `cast/bgworker_b-atlas.*`)

Same format as 3.1, plus `palettes` (colourways `slate`, `olive`, `ash`, each with its own atlas PNG `-atlas-<palette>.png`), `variants` (phone, coffee, typing idles), `silhouette` (`-atlas-silhouette.png`, `-atlas-silhouette-lit.png`) and `sync`: until level 06, workers share one walk clock with no offset; afterwards each starts its idles at a random 0–999 ms offset.

### 3.3 Mira's patches (`cast/mira-patches-atlas.*`)

States 0–6 of Mira's world frames, cumulative (state k wears patches 1..k). `patches` lists each patch's id, name, the quest that earns it, and its portrait icon. Swap the whole Mira atlas block by state.

### 3.4 Glitches (`glitches/glitches-atlas.*`)

`archetypes` (stapler, chair, form) give the frame size, footprint, `base_bc` anchor, renderer contact shadow (`x0`, `x1`, `row`) and `flippable: false` (light is upper-left, so never mirror). `animations` (`<archetype>_roam`, `<archetype>_misregister`) give row, x, y, frames, ms, loop and per-frame movement (`move_px_per_frame`, `lift_px`). Repaired: snap to register for one frame, then swap to the ordinary prop and stop roaming.

### 3.5 Environment kits (`kit/<district>-atlas.png` + `.json`)

Validated by `kit/atlas.schema.json` (`kit/check_atlas.py`). Top level: `tile` (16), `layers` (draw order above), `entries`, `animations` (state sets) and `landmarks`. Each entry:

```json
{"name": "desk_a", "kind": "prop", "rect": [336, 80, 48, 32], "size_px": [37, 23],
 "footprint": {"cells": [2, 1], "origin_px": [1, 5]}, "collision": ["11"],
 "layer": "rear_prop", "y_sort": true, "anchor": [17, 21], "composite": {"mode": "over"},
 "contact_shadow": [2, 21, 35, 2], "tags": ["desk"]}
```

- `collision` is one string per footprint row, one character per cell: `1` blocks movement, `0` is walkable.
- **State sets** (`animations`, `kind: "state_set"`): each state lists the entries to draw and, for doors, whether it blocks. Doors play `closed → half → open` on approach (120 ms per state) and backward on leave; only `open` is walkable. Lamps: `off`, `on`, `pulse`.
- **Landmarks** are full-size layered parts registered at one origin (`footprint_origin_px`). A quest state is a list of parts drawn in order, so switching state never shifts a pixel. `changes_after` lists what the after state changes.

### 3.6 Room layouts (`kit/<district>-reference-room.json`)

A cell grid of floor keys (`floor.legend` maps keys to floor entries) plus `placements`: `{"cell": [x, y], "offset": [dx, dy], "entry": "<name>"}` at the entry's footprint origin, 0–15 px offsets allowed. Draw order is layer order, then list order. `states` names the state set defaults. `kit/kitlib.py` holds the reference renderer and collision-grid builder; `kit/build_room.py` proves the Orientation layout rebuilds the approved room with zero differing pixels.

### 3.7 Pace signage (`pace/pace-atlas.*`)

Entries with `rect`, `footprint_cells`, `origin_px`, `anchor`, `layer`, `collision_cells` (list of blocked [x, y] cells) and `state` (`default`, `repeat` for the uncanny repetition, `optional` for the epilogue). Placement: sprite top-left = footprint cell top-left minus `origin_px`.

### 3.8 Portraits (`portraits/portraits-atlas.*`)

48×48 cells in the chibi style (oversized round head, tiny shoulders). Columns: `neutral`, `concerned`, `pleased`, `signature` (`signature_column` is 3). `portraits` maps `<name>_<expression>` to its rect; a signature entry is `<row>_<name>`: `ivo_laugh`, `mira_grin`, `noor_unimpressed`, `hal_puzzled`, `vale_softened` (`signatures` lists them; Engineer and Ada have none and their cell is empty). `rows` gives the row order (Mira's patched states `mira_patch1`..`mira_patch6` follow her base row and carry the grin too). Each character has their own face habits (`portraits/PORTRAIT_PERSONAS.md`). Show them at the world's integer zoom, never fractionally. `portraits/portraits-dialogue.png` shows the intended use in a dialogue panel.

## 4. UI

The UI is crisp DOM/CSS over the canvas, not pixel art. Take every colour, spacing, radius and type size from `ui-kit/tokens.css`. The component contract is `ui-kit/COMPONENTS.md`. `ui-kit/reference.html` is the static reference page (stage at ×4, keyboard inset open, dialogue, HUD, prompt, markers, journal, Layout help; append `#grey` for the greyscale check). Body text is at least 16 CSS px. Teal, coral and violet text on panels use the lighter `--accent-*` tokens; never set text on violet fills. Key hints follow the hint grammar in `docs/game-design.md`: the action, then the conventional key, then the Kanata gesture.

## 5. Asset index

| Asset | Source module | Generated files | Spec |
| --- | --- | --- | --- |
| Engineer (player avatar) | `gate1/engineer_sprites.py` | `gate1/engineer-full-atlas.png`, `gate1/engineer-full-atlas.json`, `gate1/engineer-full-sheet.png`, `gate1/engineer-extra.gif` | `gate1/GATE1_ENGINEER_SPEC.md` |
| Ivo | `cast/ivo_sprites.py` | `cast/ivo-atlas.png`, `cast/ivo-atlas.json`, `cast/ivo-sheet.png`, `cast/ivo-extra.gif` | `cast/IVO_SPEC.md` |
| Mira | `cast/mira_sprites.py`, `cast/mira_patches.py` | `cast/mira-atlas.png`, `cast/mira-atlas.json`, `cast/mira-patches-atlas.png`, `cast/mira-patches-atlas.json` | `cast/MIRA_SPEC.md`, `cast/MIRA_PATCHES_SPEC.md` |
| Noor | `cast/noor_sprites.py` | `cast/noor-atlas.png`, `cast/noor-atlas.json`, `cast/noor-in-records.png` | `cast/NOOR_SPEC.md` |
| Hal | `cast/hal_sprites.py` | `cast/hal-atlas.png`, `cast/hal-atlas.json`, `cast/hal-in-systems.png` | `cast/HAL_SPEC.md` |
| Ada | `cast/ada_sprites.py` | `cast/ada-atlas.png`, `cast/ada-atlas.json`, `cast/ada-in-nightshift.png` | `cast/ADA_SPEC.md` |
| Vale | `cast/vale_sprites.py` | `cast/vale-atlas.png`, `cast/vale-atlas.json`, `cast/vale-in-executive.png` | `cast/VALE_SPEC.md` |
| Background workers | `cast/bgworker_common.py`, `cast/bgworker_a_sprites.py`, `cast/bgworker_b_sprites.py` | `cast/bgworker_a-atlas.json`, `cast/bgworker_b-atlas.json`, `cast/bgworker_*-atlas*.png` | `cast/BACKGROUND_WORKERS_SPEC.md` |
| Glitches | `glitches/glitch_sprites.py` | `glitches/glitches-atlas.png`, `glitches/glitches-atlas.json` | `glitches/GLITCHES_SPEC.md` |
| Pace signage | `pace/pace_art.py` | `pace/pace-atlas.png`, `pace/pace-atlas.json` | `pace/PACE_SPEC.md` |
| Portraits (all seven, chibi) | `portraits/chibi.py`, `portraits/portrait_*.py` | `portraits/portraits-atlas.png`, `portraits/portraits-atlas.json`, `portraits/portraits-dialogue.png` | `portraits/PORTRAITS_SPEC.md`, `portraits/PORTRAIT_RULES.md`, `portraits/PORTRAIT_PERSONAS.md` |
| Orientation kit and garden | `kit/kitlib.py`, `kit/orientation_kit.py` | `kit/orientation-atlas.png`, `kit/orientation-atlas.json`, `kit/orientation-review-room.json` | `kit/ORIENTATION_KIT_SPEC.md` |
| Records kit and archive desk | `kit/shared_pieces.py`, `kit/records_kit.py` | `kit/records-atlas.png`, `kit/records-atlas.json`, `kit/records-reference-room.json` | `kit/RECORDS_KIT_SPEC.md` |
| Systems kit and routing machine | `kit/systems_kit.py` | `kit/systems-atlas.png`, `kit/systems-atlas.json`, `kit/systems-reference-room.json` | `kit/SYSTEMS_KIT_SPEC.md` |
| Night Shift kit and long window | `kit/nightshift_kit.py` | `kit/nightshift-atlas.png`, `kit/nightshift-atlas.json`, `kit/nightshift-reference-room.json` | `kit/NIGHTSHIFT_KIT_SPEC.md` |
| Executive kit and atrium tree | `kit/executive_kit.py` | `kit/executive-atlas.png`, `kit/executive-atlas.json`, `kit/executive-reference-room.json` | `kit/EXECUTIVE_KIT_SPEC.md` |
| District palettes and cast ramps | `palettes/district_palettes.py` | `palettes/palettes-sheet.png` | `palettes/PALETTES_SPEC.md`, `STYLE_BIBLE.md` §3 |
| UI tokens and components | `ui-kit/tokens.css` | `ui-kit/reference.html`, `ui-kit/reference-1366x768.png` | `ui-kit/UI_KIT_SPEC.md`, `ui-kit/COMPONENTS.md` |

Approval dates and the decision behind each asset are in the README decisions log and `PRODUCTION_STATUS.md`.

## 6. Rebuilding

Requirements: Python 3 with Pillow and numpy (`python3 -m venv .venv && .venv/bin/pip install pillow numpy`, optionally `jsonschema`). Then, from the repo root:

```bash
.venv/bin/python art-direction/build_all.py
```

`build_all.py` runs every check and build in dependency order (palettes, sprites, cast, glitches, Pace, portraits, the five kits, the atlas schema check, the UI contrast check and reference page, and `check_handoff.py`, which confirms every file listed here exists). It exits non-zero if anything fails. The builds are deterministic: a full run on a clean checkout leaves `git status` unchanged.

PNG, GIF and JSON art files are generated outputs: change the source module, rebuild, and commit both. Never hand-edit an output.

## 7. Known gaps

Status after the producer's gap review of 2026-10-02 (register: `docs/GAP_REGISTER.md`). This section describes the repo once the wave-1 review branches are merged; nothing here is a deliberate scoping choice, each item is unfinished work.

Closed by the wave-1 branches (listed in the register with their branch names): Layout help on all four tabs and the screens the game spec requires (setup and calibration, terminal and editor scene, input feedback, artifact frame, elevator map, seals, toast, Mira's results, settings); Orientation quest props and the shared elevator, desk-front occluder and artifact builders; quest props for the four other districts; Vale softening states 1 to 3; Hal crouched repair, seated on stool, false-panel pull and the stool prop; glitch repaired frames, ordinary props and the variant and district table; level data for all five districts (schema, validator, gesture inventory, maps, collision, levels 01 to 20, Mira routes, coverage).

Still open:

- Seated background workers are not drawn. The desk-front occluders (`desk_a_front`, `desk_b_front`) exist and the seat convention is in `kit/ORIENTATION_KIT_SPEC.md`.
- The elevator, desk-front occluders and generic artifact builder exist in the Orientation kit and as shared builders; the four other district kits still need them registered (the level data lists them as `art_gap` props).
- The ten optional artifacts of Records, Systems, Night Shift and Executive have no map props yet (builder only).
- Art gaps named by the level designers are listed per district in `design/levels/<district>/NEEDS_ART.md`; several now exist under other names and need reconciling (for example `mail_chute_*` and `courier_chute_*`, the two stool sprites).
- UI: high-contrast and larger-text variants are described, not rendered; the Microsoft keyboard variant of Layout help is drawn for the base tab only and the practice tab for the MacBook only.
- Vale state 1 is a 1 px shoulder drop and is subtle at 1x; Hal's south-facing crouch is the weakest frame.
- Level data still to align with the art: Orientation `art_gap` entries that now exist in the kit, the elevator placement (kit draws a north-wall module), the garden cut-through (kit opens only the south rim), glitch placements against the district table, and the Hal and Vale animation names.
