# Orientation environment kit: tile and prop atlas

**Status:** Approved by the director 2026-10-02.

**Sources:** `openspec/changes/complete-art-production/` (environment-kit spec, design decision 3), STYLE_BIBLE §3 and §6, `levels.md` Orientation rows and levels 01 and 06, `gate1/environment.py` (the approved room). **Director decision** marks choices made under the delegated art-direction authority.

The atlas is **extracted** from the approved room, not redrawn. Each piece is made by calling the approved drawing function from `environment.py` on two sentinel backgrounds and keeping the pixels it painted. The extraction asserts the piece does not depend on what is underneath it. `build_room.py` then rebuilds the room from the atlas and layout and proves a **zero-pixel diff**. Nothing in `gate1/` is edited.

## Deliverables

| File | What it is |
| --- | --- |
| `kitlib.py` | Generic helpers reused by every district: capture, pack, atlas loader, layout renderer, collision grid |
| `orientation_kit.py` | Orientation extraction recipes and the new art (lamp off and pulse, garden "after" parts, shelving and partitions) |
| `atlas.schema.json` | JSON Schema for any `*-atlas.json` (generic) |
| `check_atlas.py` | Validates every `*-atlas.json` and `*-review-room.json` in this folder |
| `build_kit.py` | Writes every output below, then runs the zero-diff proof |
| `build_room.py` | Rebuilds the room from atlas plus layout and compares it with the approved room and scene |
| `orientation-atlas.png` / `.json` | 53 entries on a 640×368 px sheet, 16 px grid |
| `orientation-review-room.json` | Cell layout: floor grid plus 129 placements |
| `orientation-atlas-sheet.png` | Every entry at ×4 with footprint, collision, anchor, shadow and labels |
| `orientation-garden-states.png` | Garden before, after and changed pixels at ×4 |
| `orientation-review-room-native.png`, `-1366x768.png` | The room and the Gate 1 still, drawn from the atlas |

Rebuild: `python3 build_kit.py`. Check: `python3 check_atlas.py`. Both need Pillow and numpy; `jsonschema` is used when installed, and a built-in validator otherwise.

## Atlas JSON format (reused by every district kit)

```
{ "kit": "orientation", "image": "orientation-atlas.png", "tile": 16,
  "layers": [floor, rear_wall, floor_marking, rear_prop, shadow, actor, front_prop, light],
  "entries": [ ... ], "animations": { ... }, "landmarks": { ... } }
```

**Entry** (one sprite):

| Field | Meaning |
| --- | --- |
| `name` | `lower_snake_case`, unique |
| `kind` | `tile`, `wall`, `door`, `prop`, `light` or `landmark_part` |
| `rect` | `[x, y, w, h]` in the PNG, all multiples of 16. The content sits at the rect's top-left. |
| `size_px` | Tight content size inside the rect. It rounds up to exactly the rect, so no cell is wasted. |
| `footprint` | `cells: [w, h]` in 16 px cells and `origin_px: [x, y]`, the footprint's top-left corner in sprite pixels (may be negative) |
| `collision` | One string per footprint row, one character per cell: `1` blocks, `0` walks |
| `layer` | One of the eight STYLE_BIBLE §6 layers |
| `y_sort` | True: the renderer sorts it against actors by anchor y, so a person passes behind a desk or plant |
| `anchor` | Floor contact point in sprite pixels: bottom-centre of the footprint |
| `contact_shadow` | `[x, y, w, h]` in sprite pixels where the baked shadow sits (omitted when none) |
| `composite` | `{"mode":"over"}` (default) or `{"mode":"where_color","color":"#F0DEC0"}`: draw only where the destination is exactly that colour |
| `tags`, `note` | Free text for developers |

**Placement.** A layout places an entry by its *footprint origin*: `px = cell * 16 + offset` and the sprite is drawn at `px - footprint.origin_px`. Offsets (0 to 15 px) are visual only. Collision applies to the placement cell, never the offset. Draw order is layer order, then list order within a layer.

**State sets** (`animations`): `{kind: "state_set", default, states: {name: {entries: [...], blocked?}}, play?, loop?, ms_per_frame}`. A state is the list of entries drawn together at one placement point. A layout placement uses `{"anim": name, "state": s}`. Collision comes from the entries of the active state, so an open door stops blocking.

**Landmarks**: `{size_px, footprint_origin_px, default_state, states: {name: {parts: [...], lamps?}}}`. Every part is a full-size sprite registered at the same origin. A state is an ordered list of parts. The landmark is placed at one footprint origin with `{"landmark": name, "state": s}`.

**Layout file** (`<district>-review-room.json`): `{atlas, size_cells, states, floor: {legend, rows}, placements: [{entry|anim|landmark, cell, offset?, state?}]}`.

## Contents (Orientation)

| Group | Entries |
| --- | --- |
| Floor | `floor_j`, `floor_h`, `floor_v`, `floor_p` (16 px slab cells: joint on the top row and left column, top row only, left column only, plain), `floor_chip` (2×1 px wear mark) |
| Floor markings | `route_inlay` (route guide line), `records_mat` (RECORDS mat), `garden_ring` (ring path with corner squares) |
| Walls | `wall_n_plain` (cap and trim top plane, stone face, baseboard, wall shadow), `wall_n_window_a/b` (glass bay overlays), `wall_n_alcove` (printer alcove with plaque), `wall_e_plain` (east side plane) |
| Door | `records_door_closed`, `_half`, `_open`; state set `records_door` |
| Lamp | `lamp`, `lamp_off`, `lamp_glow_on`, `lamp_glow_pulse`; state set `lamp` (off, on, pulse) |
| Props | `pot_plant_a` to `_l` (12 leaf layouts), `sofa`, `side_table`, `printer`, `desk_a/b`, `chair`, `bench`, `mail_counter` |
| Shelving and partitions | `shelf_1x1`, `shelf_2x1_a/b`, `partition_1x1`, `partition_2x1` (`rear_prop`, `y_sort`, tags `shelving` / `partition`). Not placed in the review room |
| Garden parts | `garden_ring`, `garden_base`, `garden_foliage`, `garden_rocks`, `garden_centrepiece`, `garden_canopy_shadow`, `garden_blooms`, `garden_after_path`, `garden_after_blooms` |

Placing the desk gives a 2×1 footprint (`11`), layer `rear_prop`, `y_sort`, and a contact shadow at `[2, 21, 35, 2]` in its sprite. The mail counter is `front_prop`, so people walk behind it.

## Garden landmark: before and after

The landmark is the nine garden parts plus the `lamp` state set at three positions. States: **before** is the approved room. **after** adds `garden_after_path` and `garden_after_blooms` and switches the three lamps from `on` to `pulse`.

| Change after the quest | How |
| --- | --- |
| Reopened cut-through | A built opening in the south rim and three flagstones leading into the clearing. Opening: end caps (left cap with a lit top plane and lit side tone, right cap with a shaded side plane, both with the `#202337` contour on the cut face), a two-tone stepped threshold (`STONE[2]` nosing, `STONE[1]` riser) and an inlaid path strip (lit left edge, shaded right edge) that the first flagstone meets, so the route visibly runs through. Matches levels.md level 06: "the garden cut-through unlocks". |
| New bloom cluster | Three coral blooms on green tufts with brass centres, and four single-pixel brass glints |
| Lamps wake | All three garden lamps use the wider pulse glow |

Same 128×100 px landmark box, same palette. The two states differ in **518 px** (`orientation-garden-states.png`). The only new palette use is existing ramps.

## Regression proof (build_room.py)

`build_room.py` compares, with the door closed, half open and open:

1. The rebuilt room against the approved room (`env.draw` plus `env.mail_counter`).
2. `build_gate1.scene()` with `environment.draw` and `mail_counter` swapped for the atlas renderer, against the original `scene()`, including Ivo, Mira, the Engineer and the markers.
3. The ×4 1366×768 screens of those scenes.

Final result: **0 differing pixels in all nine comparisons.**

## Director decisions

1. **Extraction by capture.** Pieces come from running the approved drawing functions on two sentinel backgrounds, so they match the room by construction, and `environment.py` stays untouched. A piece that depends on the pixels under it fails the build.
2. **Off-grid positions use pixel offsets.** The room is not on the 16 px grid (desks at x 16, the alcove at 134, the ring at 72, glass bays at 6, 38, 84 and so on). Placements carry 0 to 15 px offsets, and sprites were not redrawn to fit. This is recorded, not hidden.
3. **Walls are decomposed, not slabbed.** The north wall is one repeatable `wall_n_plain` column plus overlay modules (two window phases, the alcove). The east wall is a vertically tiling `wall_e_plain` plus the door entries. The door entries overpaint the wall where the opening is. Overlays carry no collision, because the plain wall does.
4. **The glow is a separate light entry with a conditional composite.** The approved halo only recolours lit floor (`#F0DEC0`), so `lamp_glow_*` use `where_color`. They never wash over joints, inlays, props or walls.
5. **Wear chips live on the `floor` layer** so walls and props cover them, as in the room. 58 chip placements come from the room's own random sequence.
6. **The RECORDS mat is 3 px shorter than in the room.** Its last three columns are the door threshold, which `records_door_*` draws. This keeps the layer order (walls, then floor markings) with no overlap.
7. **Door states.** Closed, half open (leaves slid 8 px) and open (15 px). Closed and half block `11`/`11`/`11`; open does not. The renderer plays the frames forward on approach and backward on leave, about 120 ms each.
8. **Lamp states.** `on` is the approved look. `pulse` is the same single brass step at radius 6.4 instead of 5.2, for an idle breathing loop (about 600 ms each). `off` recolours the head's brass steps to the ink ramp. Wake is `off` to `on`.
9. **Garden "before" is the approved room; "after" is decided here.** The Orientation rows put the cut-through (level 06: "the garden cut-through unlocks") and the lamp wake after level 06, and the garden stays obstacle-free before it. I chose three visible changes: a reopened cut-through, a brass-glint bloom cluster, and the lamp pulse glow. The hidden seating nook is not drawn. It is a layout item for the implementation.
10. **Landmark parts are registered full-size sprites.** All share one origin, so a state is just a part list and switching state never shifts a pixel. The cost is atlas area, which is small.
11. **Footprint rounding.** Footprints round the body to the nearest cell: the 34 px desk is 2 cells, the 52 px counter 3, the 60 px printer 4. Chairs and plants block. Level data may override.
12. **Pot plants.** The 12 planters differ only in leaf layout (seeded), so they are 12 entries `pot_plant_a` to `_l`, the same as the room. A district that wants fewer variants can reuse a subset.
13. **Known gaps against the environment-kit spec.** The approved Orientation room has no shelving, free-standing glass partition or separate terminal desk. Glass is the north wall bays and the printer is the terminal. Records and later district kits add shelving and partitions, and decision 15 later adds them to this atlas too. The separate terminal desk is still absent here.
14. **Cut-through opening, finished (director review).** The first version was a flat floor-coloured rectangle and read as missing pixels. It is now a built opening: end caps with contour on the cut faces, a two-tone threshold step and an inlaid strip that continues the flagstones. Still the registered part `garden_after_path`, before state untouched. The opening sits at x 112 to 128, y 124 to 134, which the keyboard inset partly covers at ×4. It is a bonus change; the blooms and lamps stay visible. Move it in the implementation level layout if needed. The part carries its own floor pixels, so the slab joint that crosses the opening in the floor layer is hidden there.
15. **Shelving and partitions added for spec coverage, not placed in the review room.** The environment-kit spec requires both in every district atlas, and the approved room has neither. Five entries (`shelf_1x1`, `shelf_2x1_a/b`, `partition_1x1`, `partition_2x1`) are drawn with the shared `shared_pieces.py` functions in the Orientation palette: blue-glass frames, warm stone, wood and brass file boxes (coral and garden green are rare slots). They are appended in their own sheet section after the garden, so every earlier entry keeps its exact pixels, metadata and atlas rect; the review-room layout is unchanged and the rebuild still shows zero differing pixels. Atlas colours stay inside the Orientation palette (27 distinct, no marker hexes, no violet). Level layouts may place them freely.
