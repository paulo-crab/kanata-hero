# Orientation environment kit: tile and prop atlas

**Status:** Approved by the director 2026-10-02. The quest-prop section and decisions 16 to 26 were added later by the Orientation kit team and are pending the producer's review.

> **Rich finish (2026-10-02):** this kit was drawn before the rich finish and is queued for re-render (OpenSpec change `adopt-rich-finish`). New and redrawn pieces follow `../rich-finish/RICH_FINISH_SPEC.md`: vivid world palette, deeper ink (`#0E1020` outline), leaf-fan foliage, light passes. Footprints, collision and layers in this spec do not change.

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
| `orientation_quest.py` | The 48 quest-prop entries and 8 new state sets (not a build step; `orientation_kit.build_pieces()` appends them) |
| `orientation_quest_room.py` | Quest-prop proofs and checks (not a build step; `build_kit.py` calls it) |
| `shared_pieces.py` | Also holds the wave-2 builders: `elevator_doors`, `elevator_call_panel`, `desk_a`, `desk_front`, `artifact_prop` (additive; no earlier function changed) |
| `orientation-atlas.png` / `.json` | 101 entries (53 original, 48 quest props appended last) on a 640×464 px sheet, 16 px grid, 10 state sets |
| `orientation-review-room.json` | Cell layout: floor grid plus 129 placements |
| `orientation-atlas-sheet.png` | Every entry at ×4 with footprint, collision, anchor, shadow and labels |
| `orientation-garden-states.png` | Garden before, after and changed pixels at ×4 |
| `orientation-review-room-native.png`, `-1366x768.png` | The room and the Gate 1 still, drawn from the atlas |
| `orientation-quest-reference-room.json` | Proof layout, 26×15 cells (416×240 px = the optional 427×240 view at ×3), 93 placements, every P0 prop placed |
| `orientation-quest-room-before-native.png` / `-1366x768.png` | Proof room at the start: elevator open, turnstile and glass door shut, board empty, lamps off |
| `orientation-quest-room-after-native.png` / `-1366x768.png` | Proof room at the end of Orientation: turnstile open, clock synced, glass door open, board human, lamps lit |
| `orientation-quest-states.png` | Every state of the 9 quest state sets at ×4, with changed pixels and separate regions per swap |
| `orientation-seated-fit.png` | `desk_a_front` over a stand-in worker, and the covered rows of the 16×24 frame |
| `orientation-shared-builders-proof.png` | The shared builders drawn in the Records palette: elevator door set, call panel, desk occluder, all 14 artifacts |

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

## Quest props (levels 01 to 06 and Morning Mail)

**Contract.** These names and state-set names are what the level designers reference. All 48 entries are appended after the 53 original ones, so every earlier entry keeps its exact pixels, metadata and atlas rect (the zero-diff room rebuild is unchanged). Footprint is in cells; collision rows are top to bottom, `1` blocks. "Wall" entries replace three `wall_n_plain` columns (doors) or overlay the wall face (no collision of their own; the plain wall blocks). Wall overlays go on the wall face at y = 9 px below the wall top, like `wall_n_window_a`. Every entry carries its contact shadow where it has one; wall slices bake the wall's cast shadow in rows 32-33.

| Entry | Footprint | Collision | Layer | y_sort | Size px | Contact shadow `[x,y,w,h]` |
| --- | --- | --- | --- | --- | --- | --- |
| `elevator_closed` | 3×3 | `111/111/000` | rear_wall | no | 48×48 | [0,32,48,2] |
| `elevator_half` | 3×3 | `111/111/000` | rear_wall | no | 48×48 | [0,32,48,2] |
| `elevator_open` | 3×3 | `111/101/000` (centre cell walks in) | rear_wall | no | 48×48 | [0,32,48,2] |
| `elevator_call_panel` | 1×2 | `0/0` | rear_wall | no | 12×22 | none (wall overlay) |
| `turnstile_closed` | 3×1 | `111` | rear_prop | yes | 48×30 | [4,27,43,2] |
| `turnstile_open` | 3×1 | `101` | rear_prop | yes | 48×30 | [4,27,43,2] |
| `turnstile_lane_lit` | 3×1 | `000` | floor_marking | no | 48×16 | none |
| `clock_twin_unsynced` / `clock_twin_synced` | 2×2 | `00/00` | rear_wall | no | 30×20 | none (wall overlay) |
| `conference_glass_door_closed` / `_half` | 3×3 | `111/111/000` | rear_wall | no | 48×48 | [0,32,48,2] |
| `conference_glass_door_open` | 3×3 | `111/101/000` | rear_wall | no | 48×48 | [0,32,48,2] |
| `projected_form_wall` | 4×2 | `0000/0000` | rear_wall | no | 62×22 | none (wall overlay) |
| `stamp_a` to `stamp_d` (left desk), `stamp_e` to `stamp_h` (right desk) | 1×1 | `0` | front_prop | no | 8×9 | [1,8,7,1] |
| `pinboard_empty` / `_before` / `_after` | 3×2 | `000/000` | rear_wall | no | 48×23 | none (wall overlay) |
| `desk_left_cherry`, `desk_right_mirror` | 2×1 | `11` | rear_prop | yes | 37×24 | [2,22,35,2] |
| `desk_a_front`, `desk_b_front` | 2×1 | `00` | front_prop | yes | 35×13 | none |
| `review_table` | 3×1 | `111` | rear_prop | yes | 51×19 | [2,16,49,2] |
| `keyboard_macbook` | 1×1 | `0` | front_prop | no | 14×11 | [1,9,13,1] |
| `keyboard_spare` | 2×1 | `00` | front_prop | no | 24×13 | [1,11,23,1] |
| `mail_board` | 3×1 | `111` | rear_prop | yes | 48×33 | [3,30,45,2] |
| `mail_medals_1` to `mail_medals_6` | 3×1 | `000` | rear_prop | yes | 48×33 | none (overlay of `mail_board`) |
| `mail_tray`, `desk_folder` | 1×1 | `0` | front_prop | no | 14×10 | [1,9,12,1], [2,9,11,1] |
| `route_stripe_lit` | 1×1 | `0` | floor_marking | no | 16×3 (origin y 1) | none |
| `lamp_warm`, `lamp_warm_glow_on`, `lamp_warm_glow_pulse` | 1×1 | `1`, `0`, `0` | rear_prop, light, light | yes, no, no | 5×14, 11×10, 13×13 | [1,13,4,1] on `lamp_warm` |
| `artifact_unissued_badge`, `artifact_training_card`, `artifact_mirror_card`, `artifact_first_route_receipt` | 1×1 | `0` | front_prop | no | 16×16 | one row under the item |

**State sets** (state names are the contract; `play` order is the door animation order, 120 ms per frame):

| State set | States (default first) | Entries per state |
| --- | --- | --- |
| `elevator` | `closed`, `half`, `open` (blocked: true, true, false) | `elevator_closed`, `elevator_half`, `elevator_open` |
| `turnstile` | `closed`, `open` | `turnstile_closed`; `turnstile_open` + `turnstile_lane_lit` |
| `clock_twin` | `unsynced`, `synced` | `clock_twin_unsynced`; `clock_twin_synced` |
| `conference_door` | `closed`, `half`, `open` | `conference_glass_door_closed`, `_half`, `_open` |
| `pinboard` | `empty`, `before`, `after` | `pinboard_empty`; `pinboard_before`; `pinboard_after` |
| `mail_medals` | `0` to `6` | `mail_board`; for k ≥ 1 also `mail_medals_k` |
| `lamp_warm` | `on`, `off`, `pulse` | `lamp_warm` + glow; `lamp_off`; `lamp_warm` + pulse glow |
| `corridor_stripe` | `unlit`, `lit` | `route_inlay`; `route_stripe_lit` |
| `lamp` (existing) | `on`, `off`, `pulse` | unchanged: the left desk's floor lamp is this set |

**Quest-state swaps** (each must change at least two separate visible regions; `orientation-quest-states.png` and `build_kit.py` count them, NPC poses are level data and not counted):

| Level | Swap | Visible changes (regions) |
| --- | --- | --- |
| 01 | `turnstile` `closed` to `open` | flaps fold away, both pedestal stripes light, lit lane inlay appears (3) |
| 03 | `clock_twin` `unsynced` to `synced` + `conference_door` `closed` to `open` | right face's hands move, status lamp lights, glass leaves slide aside (3) |
| 04 | `pinboard` `empty` to `before` + `lamp` `off` to `on` + `corridor_stripe` `unlit` to `lit` | four sheets join the board, the floor lamp wakes, the stripe lights (5) |
| 05 | `pinboard` `before` to `after` + `lamp_warm` `off` to `on` | the board turns asymmetrical with a map arrow, the warm lamp wakes (2) |
| 02 | `mail_medals` `0` to `k` | one medal per clean Morning Mail baseline, then one per later route (Mira's six patches) |

**Seated workers and the desk occluders.** Convention (seat behind the desk, worker faces the camera): the `chair` entry is placed at **desk origin + (8, −12) px** and the worker's 16×24 frame is anchored (`feet_bc`) at **desk origin + (16, 4) px**, i.e. the chair footprint's bottom-centre. The frame then spans desk-relative y −20 to +3 and x +8 to +23. `desk_a_front` / `desk_b_front` are the desk's own pixels (the monitor housing and the first 8 px of top plane, y −5 to +7, x 0 to 34), cut from `desk_a` / `desk_b` and drawn on `front_prop` after actors, so they are seamless over the desk (the build asserts zero differing pixels). Place them at the desk origin, after the actors and after `desk_a` / `desk_b`. Rows of the 16×24 worker frame they hide (`#` hidden, `.` visible; rows 0-14 never touched):

```
rows 0-14   ................   head, shoulders, arms, torso to the waist stay visible
rows 15-19  .##############.   waist to knees hidden behind the monitor; columns 0 and 15 stay visible
rows 20-23  ################   knees and feet hidden behind the desk top
```

So a seated worker sprite draws the head, shoulders, both forearms resting forward and the torso down to row 14 (row 14 is the lowest row guaranteed visible); anything below row 15 is hidden and need not be drawn. Elbows or a hand on a mouse may use columns 0 and 15 down to row 19. `orientation-seated-fit.png` shows it with a stand-in worker.

**Corridor stripe and lamps.** `route_inlay` is the unlit stripe; `route_stripe_lit` is a 3 px brass band whose centre row falls on the inlay's row (its footprint origin is already 1 px up), and `corridor_stripe` swaps them. The left desk's lamp is the existing `lamp` set (`off` to `on`) placed beside the desk, switched together with the stripe at level 04. The right desk's warmer lamp is `lamp_warm` (peach head, amber glow; same three states, the off state reuses `lamp_off`).

**Stamp positions.** `desk_left_cherry` and `desk_right_mirror` carry a four-slot tray along the front of the top plane. Place stamps at desk origin + (2, 1), (10, 1), (18, 1), (26, 1) px; `stamp_a` to `stamp_d` on the left desk, `stamp_e` to `stamp_h` on the right desk. Review table: place `keyboard_macbook` at +(3, 1) and `keyboard_spare` at +(22, 2).

**Artifacts.** The four Orientation artifacts are 16×16 (body about 11×11) documents, outlined, with a baked contact shadow and one shared faint cue: a small pale-blue glint (glass step 3) at the upper left. They have no collision; lay them on a desk, table or blocked cell, not on a route cell. The glint is the only inspectable cue in the art; the game may add its own marker. The other ten artifacts named in levels.md exist only as the shared builder `artifact_prop(r, x0, y0, pal, kind)` and appear in `orientation-shared-builders-proof.png` (Records palette).

**Shared builders for wave 2** (all in `shared_pieces.py`, parametrised by `Pal`): `elevator_doors(r, x0, y0, pal, t, mat)`, `elevator_call_panel`, `desk_a(r, x0, y0, pal, seed)` (pixel-identical to `env.desk` with the Orientation palette), `desk_front`, `artifact_prop` with `ARTIFACT_KINDS`, plus helpers `wall_slice`, `lit_mat`, `sconce`, `text5`, `line`. Wave 2 can either call them with the district `Pal` or hex-swap the Orientation entries as the Records kit already does for desks; both give the same shape. The desk occluder is cut at an origin whose (x + y) mod 3 equals the room desks' (the plant's lit tips depend on it).

## Director decisions (quest props)

16. **Elevator is a north-wall slice.** The camera only shows north-facing faces, so the 3×3 module (wall rows 0-1, lit LIFT mat row 2) goes into a wall band. For the south-west arrival, build a short interior wall (a lift core) with the door facing south; the proof room does this.
17. **Doors keep the Records door's grammar.** Closed, half, open at 120 ms; frame, lamps, a see-through opening and a lit mat with lettering (`LIFT`, `MEET`). The conference door uses a dark glass frame, the elevator a brass casing.
18. **The turnstile gates only when the level data says so.** `turnstile_open` adds a lit floor inlay (`turnstile_lane_lit`, floor_marking) because anything drawn on the y-sorted pedestal layer would paint over a person standing in the lane. The closed state blocks all three cells, the open state only the pedestals.
19. **Stamps sit on `front_prop`, no y-sort.** They lie on a desk top and must draw after the desk and never behind it. Eight 8×9 px silhouettes: mushroom, T handle, rocker, dater box (left); hook, cone, dater wheel, pen (right). The build fails if any pair of silhouettes overlaps 80% or more.
20. **Pinboard has three states.** `empty` is added so level 04's "each approved sheet joins" has a starting frame. `before` is mirror symmetric about the vertical axis (checked on every non-cork pixel); `after` is not.
21. **Desk variants.** `desk_left_cherry` is deeper and redder than `desk_a` (cherry, from the wood and coral ramps), with a small monitor kept clear of the stamps. `desk_right_mirror` mirrors the layout. Neither has a chair or a lamp.
22. **Warm lamp.** The right desk's lamp is a recolour of the approved lamp (peach head, amber glow), not baked into the desk, so it can wake like the left one.
23. **Medals.** `mail_board` is a free-standing board (a wall is not always behind the mailroom) with six slots; each overlay adds one medal in Mira's patch colours limited to the palette (peach, lime, warm wood, ink, pale brass, glass).
24. **Seating convention.** See above. The desk occluder is the desk's own pixels, so nothing can drift, and its covered rows are measured by the build rather than assumed.
25. **Artifact count.** levels.md names 14 optional artifacts, not 15: Unissued badge, Training card, Mirror card, First route receipt, Carbon copy A, Margin stamp, Uncut index, Noor's annotation, ID envelope, Alarm strip, Scoring proof, Original routing diagram, Ada's shift book, Public audit copy. All 14 are in `artifact_prop`; four are in the atlas, ten are proof only.
26. **Palette.** The 48 new entries use 28 distinct colours, all from the Orientation ramps (ink, stone, glass, wood, foliage, brass, coral); no teal, coral, violet or gold marker hex, checked by `check_atlas.py` (markers) and `orientation_quest_room.py` (palette).

**Proof checks** (all in `build_kit.py`, exit 1 on failure): new colours inside the Orientation palette; stamp silhouettes pairwise distinct; `pinboard_before` symmetric and `pinboard_after` not; every level swap above changes at least two separate regions; the seat-coverage rows above; `desk_a_front` and `desk_b_front` identical to the desks; and on the proof room's collision grid, with the turnstile closed only the lobby is reachable from the elevator mat, with it open the left desk, player's desk, right desk, review table, garden and mail counter all are. `check_atlas.py` also now fails a state set whose states draw the same entries.

## Orientation completion (wave 2): west wall, garden through-route, seating nook

Five entries and one state set are appended after the quest props (group 13 in the atlas sheet), so every earlier entry keeps its pixels, metadata and rect; the review room still rebuilds with zero differing pixels. The atlas is now 106 entries. New outputs: `orientation-completion-reference-room.json` (14x8 proof layout), `orientation-completion-room-native.png`, `orientation-completion-proof.png` (elevator corner, west wall, garden collision with the walked route, nook hidden and shown).

| Entry | Footprint | Collision | Layer | y_sort | Size px | Notes |
| --- | --- | --- | --- | --- | --- | --- |
| `wall_w_plain` | 2x1 | `11` | rear_wall | no | 30x16 | West side plane, tiles vertically; contact shadow `[28,0,2,16]` on the floor. Content starts at the cell edge. |
| `garden_base_open` | 5x4 | `10111` x4 | rear_prop | no | 128x100 | Pixel-identical to `garden_base`; column 1 walks. |
| `garden_north_rim_open` | 5x4 (landmark part) | all `0` | rear_prop | no | 128x100 | North rim opening cut through the crown. |
| `seating_nook_after` | 3x2 | `111/110` | rear_prop | yes | composition | Sofa, side table, planter and lamp from existing sprites. |
| `seating_nook_glow` | 3x2 | `000/000` | light | no | 11x10 | The nook lamp's pool, `where_color` on lit floor, registered at the nook origin. |

State set `seating_nook`: `hidden` (no entries, blocks nothing; the default) and `shown` (`seating_nook_after`, `seating_nook_glow`). The schema now allows a state with an empty entry list.

**Garden landmark, after state.** Parts are now `garden_ring`, `garden_base_open`, foliage, rocks, centrepiece, canopy shadow, blooms, `garden_after_path`, `garden_after_blooms`, `garden_north_rim_open` (drawn last), lamps `pulse`. The before state is unchanged. Collision: the landmark is still placed at one footprint origin (5x4 cells); after the quest cell column 1 (rows 0 to 3) walks and the other 15 bed cells block. For level data placing the garden at cell (11,7) that is cells (12,7) to (12,10). In the proof room's grid, before the quest the walk from the cell above the column to the cell below it takes 13 steps round the ring; after, 5 steps straight through. Against the current `design/levels/orientation/map.json` (informational report in the build): printer approach (13,3) to Ivo's post (12,13) drops from 17 to 11 steps through the column; walks that already take the west or east band tie (north desk to south desk, to Mira).

## Director decisions (completion)

27. **`wall_w_plain` is not a flipped east wall.** Light is upper-left: the east wall's inner face looks into the light and carries the lit trim on its inner edge; the west wall's inner face is in shade, so the trim sits on the outer edge, the inner edge is dark, and a 2 px shadow falls east onto the floor like the north wall's. It is 2 cells thick (collision `11`), so a west-end elevator module starts at cell x 2, not 0.
28. **The north rim opening is a landmark part, not a 1x1 floor marking.** The crown covers the rim; only a part drawn after the centrepiece can cut through it. Level data should drop the separate `garden_north_rim` placement at (12,6) and use the landmark `after` state; the strip still reaches the ring at (12,6).
29. **Collision opens through a second base entry.** Collision is the union of the state's parts and parts only add blocks, so the after state swaps `garden_base` for `garden_base_open` (same pixels) rather than changing the before state's block.
30. **Seating nook position is level data.** The nook is one registered composition with its own lamp pool. The proof room puts it east of the garden ring; the level designers place it where the map has a free 3x2.
31. **Elevator mat needs no `lift_hall_floor` strip.** In the Orientation palette the mat is brass `#F5D580` with a `#E1AC62` edge and dark lettering on `#F0DEC0` floor; it reads clearly at x4 and x1 (`orientation-completion-proof.png`), so no extra floor piece was added.
