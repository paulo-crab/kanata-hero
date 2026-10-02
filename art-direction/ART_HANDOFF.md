# Kanata Hero: art handoff for developers

**Status:** approved art set, 2026-10-02. This is the single entry point for developer agents building the browser game described in `docs/game-design.md`. It indexes every approved asset, explains each file format, and says how to rebuild everything. Rules live in `art-direction/STYLE_BIBLE.md`; the capability contracts are the five specs of the OpenSpec change `complete-art-production` (`art-style-foundation`, `character-sprites`, `environment-kit`, `ui-presentation`, `art-asset-handoff`).

You should never need to invent a visual. If something you need is missing, it is a gap in this handoff: raise it, don't draw it.

## 1. Ground rules for the renderer

- **Rich finish (2026-10-02).** The world is moving to a vivid palette with deeper darks, leaf-fan foliage and a lighting pass, still on the 16 px grid. The assets indexed below were approved before it and are being re-rendered (OpenSpec change `adopt-rich-finish`); until a file's spec says otherwise, treat colour values in this handoff as the pre-finish ones. Anchors, footprints, collision, layers, timing and file formats do not change. The outline colour becomes `#0E1020`. See [`rich-finish/RICH_FINISH_SPEC.md`](rich-finish/RICH_FINISH_SPEC.md).

- **Grid and view.** 16×16 px tiles, a 320×180 logical view, nearest-neighbour integer zoom only: ×4 on 1366×768 (a 1280×720 stage, letterboxed) and ×6 on 1920×1080. An optional wider view is 427×240 at ×3. Never scale fractionally or smooth.
- **Draw order** (STYLE_BIBLE §6): `floor` → `rear_wall` → `floor_marking` → `rear_prop` → `shadow` → `actor` → `front_prop` → `light` → DOM UI. Within `rear_prop`, `actor` and `front_prop`, sort by the anchor's y (entries with `y_sort: true`). No parallax or horizon layer.
- **Contact shadows** under people and glitches are drawn by the renderer at the anchor, not baked into frames (`#535971` outer, `#343650` core; see `gate1/build_gate1.py` `contact_shadow`). Under the rich finish these become `#3A4160` outer and `#1C2038` core (`rich-finish/RICH_FINISH_SPEC.md`). Environment props bake theirs (`contact_shadow` rect in the atlas entry).
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

**Vale softening states.** Sets `s1_*` to `s3_*` (idle, walk, interact) are named `vale_s<k>_<set>_<facing>`; the renderer uses `k = min(repairs, 3)` and the base `vale_<set>_<facing>` for 0. Walk-like extra sets carry `px_per_frame` and `contact_frames`. Entries may carry `softening_state`, `prop`, `prop_atlas`, `stool_cell_in_frame_px` and `stool_sprite_in_frame_px`. **Hal poses** (`crouch_repair`, `seated_stool`, `false_panel_pull`) and the stool prop are in `cast/hal-atlas.json` and `cast/hal-props-atlas.json`; see `cast/HAL_SPEC.md` for the seat offset.

### 3.2 Background workers (`cast/bgworker_a-atlas.*`, `cast/bgworker_b-atlas.*`)

Same format as 3.1, plus `palettes` (colourways `slate`, `olive`, `ash`, each with its own atlas PNG `-atlas-<palette>.png`), `variants` (phone, coffee, typing idles), `silhouette` (`-atlas-silhouette.png`, `-atlas-silhouette-lit.png`) and `sync`: until level 06, workers share one walk clock with no offset; afterwards each starts its idles at a random 0–999 ms offset.

### 3.3 Mira's patches (`cast/mira-patches-atlas.*`)

States 0–6 of Mira's world frames, cumulative (state k wears patches 1..k). `patches` lists each patch's id, name, the quest that earns it, and its portrait icon. Swap the whole Mira atlas block by state.

### 3.4 Glitches (`glitches/glitches-atlas.*`)

`archetypes` (stapler, chair, form) give the frame size, footprint, `base_bc` anchor, renderer contact shadow (`x0`, `x1`, `row`) and `flippable: false` (light is upper-left, so never mirror). `animations` (`<archetype>_roam`, `<archetype>_misregister`) give row, x, y, frames, ms, loop and per-frame movement (`move_px_per_frame`, `lift_px`). Repaired: play `<archetype>_repaired` (1 frame, 160 ms, play once) at the glitch's anchor, then swap to `<archetype>_ordinary` (static; `archetypes.<a>.ordinary` has its footprint, collision and anchor) and stop roaming. The atlas is 128x192. `variants` (palettes with `swap` and `swap_dark`, behaviours) and `districts.<id>` (keys `orientation`, `records`, `systems`, `nightshift`, `executive`) are the level-data contract; see `glitches/GLITCHES_SPEC.md`.

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
- Quest-prop state sets beyond doors and lamps include `elevator`, `turnstile`, `clock_twin`, `conference_door`, `pinboard`, `mail_medals` (states 0-6), `lamp_warm`, `corridor_stripe` and the district quest-prop sets listed in each kit spec's "Quest props" section and in `kit/QUEST_PROP_AUDIT.md`. North-wall doors (`repair_door`, `north_stair`) replace two plain wall tiles and must not sit above plain wall collision. The elevator is a 3x3 north-wall module. Seated workers pair with `desk_a_front` and `desk_b_front` (fit rows in `kit/ORIENTATION_KIT_SPEC.md`).
- **Landmarks** are full-size layered parts registered at one origin (`footprint_origin_px`). A quest state is a list of parts drawn in order, so switching state never shifts a pixel. `changes_after` lists what the after state changes.

### 3.6 Room layouts (`kit/<district>-reference-room.json`)

A cell grid of floor keys (`floor.legend` maps keys to floor entries) plus `placements`: `{"cell": [x, y], "offset": [dx, dy], "entry": "<name>"}` at the entry's footprint origin, 0–15 px offsets allowed. Draw order is layer order, then list order. `states` names the state set defaults. `kit/kitlib.py` holds the reference renderer and collision-grid builder; `kit/build_room.py` proves the Orientation layout rebuilds the approved room with zero differing pixels.

### 3.7 Pace signage (`pace/pace-atlas.*`)

Entries with `rect`, `footprint_cells`, `origin_px`, `anchor`, `layer`, `collision_cells` (list of blocked [x, y] cells) and `state` (`default`, `repeat` for the uncanny repetition, `optional` for the epilogue). Placement: sprite top-left = footprint cell top-left minus `origin_px`.

### 3.8 Portraits (`portraits/portraits-atlas.*`)

48×48 cells in the chibi style (oversized round head, tiny shoulders). Columns: `neutral`, `concerned`, `pleased`, `signature` (`signature_column` is 3). `portraits` maps `<name>_<expression>` to its rect; a signature entry is `<row>_<name>`: `ivo_laugh`, `mira_grin`, `noor_unimpressed`, `hal_puzzled`, `vale_softened` (`signatures` lists them; Engineer and Ada have none and their cell is empty). `rows` gives the row order (Mira's patched states `mira_patch1`..`mira_patch6` follow her base row and carry the grin too). Each character has their own face habits (`portraits/PORTRAIT_PERSONAS.md`). Show them at the world's integer zoom, never fractionally. `portraits/portraits-dialogue.png` shows the intended use in a dialogue panel.

## 4. UI

The UI is crisp DOM/CSS over the canvas, not pixel art. Take every colour, spacing, radius and type size from `ui-kit/tokens.css`. The component contract is `ui-kit/COMPONENTS.md`. `ui-kit/reference.html` is the static reference page (stage at ×4, keyboard inset open, dialogue, HUD, prompt, markers, journal, Layout help on all four tabs, setup and calibration, terminal and editor scenes, input feedback, artifact frame, elevator map, seals and toast, Mira's results, settings, first-use and Controls; append `#grey` for the greyscale check, or `#s-<id>` for one screen); `ui-kit/screens/<id>-1366x768.png` is each screen's render. The interface keys (Return, Esc, arrows, Q, Backtick, `?`) are decided in `design/ui-key-bindings.md`; `ui-kit/bindings.py` is their source and is linted by `ui-kit/check_contrast.py`. Level data is specified in `design/levels/SCHEMA.md` and checked by `design/levels/validate_levels.py`. Body text is at least 16 CSS px. Teal, coral and violet text on panels use the lighter `--accent-*` tokens; never set text on violet fills. Key hints follow the hint grammar in `docs/game-design.md`: the action, then the conventional key, then the Kanata gesture.

## 5. Asset index

| Asset | Source module | Generated files | Spec |
| --- | --- | --- | --- |
| Engineer (player avatar) | `gate1/engineer_sprites.py` | `gate1/engineer-full-atlas.png`, `gate1/engineer-full-atlas.json`, `gate1/engineer-full-sheet.png`, `gate1/engineer-extra.gif` | `gate1/GATE1_ENGINEER_SPEC.md` |
| Ivo | `cast/ivo_sprites.py` | `cast/ivo-atlas.png`, `cast/ivo-atlas.json`, `cast/ivo-sheet.png`, `cast/ivo-extra.gif` | `cast/IVO_SPEC.md` |
| Mira | `cast/mira_sprites.py`, `cast/mira_patches.py` | `cast/mira-atlas.png`, `cast/mira-atlas.json`, `cast/mira-patches-atlas.png`, `cast/mira-patches-atlas.json` | `cast/MIRA_SPEC.md`, `cast/MIRA_PATCHES_SPEC.md` |
| Noor | `cast/noor_sprites.py` | `cast/noor-atlas.png`, `cast/noor-atlas.json`, `cast/noor-in-records.png` | `cast/NOOR_SPEC.md` |
| Hal | `cast/hal_sprites.py` | `cast/hal-atlas.png`, `cast/hal-atlas.json`, `cast/hal-in-systems.png`, `cast/hal-props-atlas.png`, `cast/hal-props-atlas.json`, `cast/hal-poses-in-systems.png` | `cast/HAL_SPEC.md` |
| Ada | `cast/ada_sprites.py` | `cast/ada-atlas.png`, `cast/ada-atlas.json`, `cast/ada-in-nightshift.png` | `cast/ADA_SPEC.md` |
| Vale | `cast/vale_sprites.py` | `cast/vale-atlas.png`, `cast/vale-atlas.json`, `cast/vale-in-executive.png`, `cast/vale-states-in-executive.png` | `cast/VALE_SPEC.md` |
| Background workers | `cast/bgworker_common.py`, `cast/bgworker_a_sprites.py`, `cast/bgworker_b_sprites.py` | `cast/bgworker_a-atlas.json`, `cast/bgworker_b-atlas.json`, `cast/bgworker_*-atlas*.png` | `cast/BACKGROUND_WORKERS_SPEC.md` |
| Glitches | `glitches/glitch_sprites.py` | `glitches/glitches-atlas.png`, `glitches/glitches-atlas.json`, `glitches/glitch_variants.py`, `glitches/glitches-repair.gif` | `glitches/GLITCHES_SPEC.md` |
| Pace signage | `pace/pace_art.py` | `pace/pace-atlas.png`, `pace/pace-atlas.json` | `pace/PACE_SPEC.md` |
| Portraits (all seven, chibi) | `portraits/chibi.py`, `portraits/portrait_*.py` | `portraits/portraits-atlas.png`, `portraits/portraits-atlas.json`, `portraits/portraits-dialogue.png` | `portraits/PORTRAITS_SPEC.md`, `portraits/PORTRAIT_RULES.md`, `portraits/PORTRAIT_PERSONAS.md` |
| Orientation kit and garden | `kit/kitlib.py`, `kit/orientation_kit.py` | `kit/orientation-atlas.png`, `kit/orientation-atlas.json`, `kit/orientation-review-room.json`, `kit/orientation_quest.py`, `kit/orientation-quest-reference-room.json`, `kit/orientation-quest-states.png` | `kit/ORIENTATION_KIT_SPEC.md` |
| Records kit and archive desk | `kit/shared_pieces.py`, `kit/records_kit.py` | `kit/records-atlas.png`, `kit/records-atlas.json`, `kit/records-reference-room.json` | `kit/RECORDS_KIT_SPEC.md` |
| Systems kit and routing machine | `kit/systems_kit.py` | `kit/systems-atlas.png`, `kit/systems-atlas.json`, `kit/systems-reference-room.json` | `kit/SYSTEMS_KIT_SPEC.md` |
| Night Shift kit and long window | `kit/nightshift_kit.py` | `kit/nightshift-atlas.png`, `kit/nightshift-atlas.json`, `kit/nightshift-reference-room.json` | `kit/NIGHTSHIFT_KIT_SPEC.md` |
| Executive kit and atrium tree | `kit/executive_kit.py` | `kit/executive-atlas.png`, `kit/executive-atlas.json`, `kit/executive-reference-room.json` | `kit/EXECUTIVE_KIT_SPEC.md` |
| District palettes and cast ramps | `palettes/district_palettes.py` | `palettes/palettes-sheet.png` | `palettes/PALETTES_SPEC.md`, `STYLE_BIBLE.md` §3 |
| UI tokens and components | `ui-kit/tokens.css` | `ui-kit/reference.html`, `ui-kit/reference-1366x768.png`, `ui-kit/screens/*.png`, `ui-kit/bindings.py`, `design/ui-key-bindings.md` | `ui-kit/UI_KIT_SPEC.md`, `ui-kit/COMPONENTS.md` |
| Level data (schema, validator, inventory, five districts) | `design/levels/validate_levels.py` | `design/levels/level-data.schema.json`, `design/levels/gesture-inventory.json`, `design/levels/world.json`, `design/levels/orientation/map.json` | `design/levels/SCHEMA.md` |

Approval dates and the decision behind each asset are in the README decisions log and `PRODUCTION_STATUS.md`.

## 6. Rebuilding

Requirements: Python 3 with Pillow and numpy (`python3 -m venv .venv && .venv/bin/pip install pillow numpy`, optionally `jsonschema`). Then, from the repo root:

```bash
.venv/bin/python art-direction/build_all.py
```

`build_all.py` runs every check and build in dependency order (palettes, sprites, cast, glitches, Pace, portraits, the five kits, the atlas schema check, the UI contrast check and reference page, and `design/levels/validate_levels.py --all`, which checks the level data against the atlases, and `check_handoff.py`, which confirms every file listed here exists). It exits non-zero if anything fails. The builds are deterministic: a full run on a clean checkout leaves `git status` unchanged.

PNG, GIF and JSON art files are generated outputs: change the source module, rebuild, and commit both. Never hand-edit an output.

## 7. Known gaps

- The whole asset set predates the rich finish and needs the re-render listed in OpenSpec change `adopt-rich-finish`. The recolour to the v2 ramps and ink is done in code; leaf-fan foliage, the garden parts and the light passes follow.

Status after wave 2 of the producer's gap review (2026-10-02; register: `docs/GAP_REGISTER.md`). Every gap of the art deck is closed: Layout help on all four tabs and the screens the game spec requires, quest props and landmark states for all five districts, the shared elevator, desk-front occluders and optional artifacts, Vale softening states and Hal's poses, glitch repair frames and the variant table, seated background workers, and level data for every district. What remains is polish and the next art direction.

- The rich finish (Mock 2.1; the art director's rich-finish spec, on the branch feat/art-rich-finish until it is reviewed) is the approved next look: every kit, sprite, glitch, Pace and portrait asset is to be re-rendered with its geometry, footprints, collision, layers and anchors unchanged, so the level data keeps validating. Until that lands the specs carry a "re-render needed" banner.
- UI: high-contrast and larger-text variants are described but not rendered; the Microsoft keyboard variant of Layout help is drawn for the base tab only and the practice tab for the MacBook only.
- Seated workers face south only (the kit has no camera-side chair and occluder); typing and phone detail is small at 1x because the occluder hides row 15 and below.
- Vale state 1 is a 1 px shoulder drop and subtle at 1x; Hal's south-facing crouch is the weakest frame.
- Level data: Systems bridges run north-south but `bridge_span` is drawn east-west; Quiet Alarm cannot set `alarm_strip_muted` because side quests have no trigger list; the schema's `glitch` object has one slot per level and no `behaviour` key (behaviour is in the note); the layout manifest for Layout help is not created.
