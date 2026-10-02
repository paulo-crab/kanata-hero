# Records environment kit and the circular archive desk (task 7.1)

**Status:** Approved by the director 2026-10-02.

**Sources:** `openspec/changes/complete-art-production/` (environment-kit spec, design decisions 3 and 4), STYLE_BIBLE §3, §6 and §7, PALETTES_SPEC.md (Records ramps), `levels.md` Records rows and levels 07 to 11, `docs/game-design.md` (district table, "Records reference layout", "Asset and level handoff"), ORIENTATION_KIT_SPEC.md (the atlas format). **Director decision** marks choices made under the delegated authority; here they are the designer's proposals for the director to record.

This is the "walkable Records composition built from the shared kit" that validates the pipeline before Systems, Night Shift and Executive. Same atlas format and tooling as Orientation; the Orientation build is untouched (all nine zero-diff comparisons and every Orientation output hash are identical).

## Deliverables

| File | What it is |
| --- | --- |
| `shared_pieces.py` | District-agnostic new pieces as drawing functions taking a `Pal`: `shelf`, `partition`, `terminal_desk`, `cabinet`, `light_shaft`. A later district recolours them by passing its own ramps. |
| `records_kit.py` | Records recipes: hex-swap of Orientation pieces, capture of the shared pieces, route arrows, the file wall, the landmark parts, the atlas JSON |
| `build_records.py` | Writes every output below, then runs the programmatic review and exits 1 on any failure |
| `records-atlas.png` / `.json` | 48 entries on a 640×320 px sheet, 16 px grid, validated by `check_atlas.py` |
| `records-atlas-sheet.png` | Every entry at ×4 with footprint, collision, anchor and contact shadow |
| `records-landmark-states.png` | The archive desk before, after and the changed pixels (1399 px) at ×4 |
| `records-reference-room.json` | The walkable room as a cell layout: floor grid plus 105 placements, atlas data only |
| `records-reference-room-native.png`, `-1366x768.png` | The room, before state, with the Engineer on the route, native 320×192 and the ×4 view |
| `records-reference-room-keyboard-inset.png` | The same ×4 view with the keyboard inset rectangle overlaid |
| `records-reference-room-after-native.png`, `-after-1366x768.png` | After state: landmark after, door open, file wall open, lamps pulsing |
| `records-reference-room-route.png` | Review overlay: blocked cells, the BFS route and the inset |

Rebuild: `python3 build_records.py`. Check: `python3 check_atlas.py` (now also checks `*-reference-room.json`). Both need Pillow and numpy. Backward-compatible edits to approved tooling: `build_kit.atlas_sheet` takes optional `rank_fn`, `sections`, `title` and `out` (defaults reproduce the Orientation sheet byte for byte); `check_atlas.py` also globs `*-reference-room.json`. `kitlib.py` is unchanged.

## Contents

| Group | Entries |
| --- | --- |
| Floor | `floor_j/h/v/p`, `floor_chip` (Orientation tiles recoloured to the Records floor ramp), `route_inlay`, `route_inlay_v` (the line in floor step 1), `route_arrow_e`, `route_arrow_n` (cherry arrows, new) |
| Walls | `wall_n_plain`, `wall_n_window_a/b`, `wall_e_plain` (recoloured: linen face, sea-blue glass) |
| Door | `archive_door_closed/_half/_open`, state set `archive_door` |
| Lamp | `lamp`, `lamp_off`, `lamp_glow_on`, `lamp_glow_pulse`, state set `lamp` |
| Reused props | `desk_a/b`, `chair`, `pot_plant_a` to `_d` |
| New shared kit | `shelf_1x1`, `shelf_2x1_a/b`, `partition_1x1`, `partition_2x1`, `terminal_desk`, `cabinet_1x1`, `cabinet_2x1`, `light_shaft` |
| File wall | `file_wall_closed`, `file_wall_open`, `file_wall_rail`, state set `file_wall` |
| Landmark | `archive_ring_inlay`, `archive_desk_back`, `archive_desk_front`, `archive_desk_items`, `archive_ledger_before/_after`, `archive_folders_before/_after`, `archive_ring_glow_after`; landmark `archive_desk` |

Everything uses the Records ramps only: 26 colours (ink shared, floor, wall, glass, wood, foliage, accent). No violet, no marker hex, no brass.

## New shared pieces

- **Shelving** (1×1, 2×1; footprint is the bottom 16 px, the sprite is 28 px tall). Top plane with a lit edge, front face with three bays, uprights, boards and a kick plate. File boxes are placed in runs of two to four boxes of one colour (coral, linen, sea blue, cherry), each a body, a lit top row, a shaded side and a linen label, with gaps between runs. No per-pixel noise.
- **Glass partition** (1×1, 2×1). Dark frame with a lit cap, a cool pane that darkens toward the floor, one stepped reflection band per pane, a middle post for the 2×1, a floor rail.
- **Terminal desk** (2×1). The ink terminal housing is drawn first, then the bezel, then the screen: one body step and one lit step in the glass ramp (`#527F94`, `#8DB6C2`), plus one hard glow step on the desk top. Never `#19AFA2`.
- **Cabinet** (1×1, 2×1). Cherry body, a paper stack on the top plane, three drawers with label plates and pulls.
- **Light shaft** (4×3 cells, layer `light`, composite `where_color` on the bare floor fill). Two bands of daylight to the lower right from a window pair, one hard linen step.
- **File wall.** Two 2×1 shelf units on a floor rail. Closed: cells 1 to 4 of 6 block (`011110`). Open: the units have slid one cell outward (`110011`) and cells 2 and 3 are a two-cell corridor. State set `file_wall`, with the rail entry in both states.

## Door

`archive_door_*` are Orientation's sliding glass door recoloured by an exact swap, with the PALETTES_SPEC decision 5 rule: the frame is cherry wood (not brass), the RECORDS sign is a linen plate with a coral folder icon. States and collision are unchanged: closed and half block (`11`/`11`/`11`), open walks. The open doorway measures 99 luma against 55 for the adjacent east wall (check in `build_records.py`).

## Landmark: the circular archive desk

128×96 px (8×6 cells), the same pixel size as the rest of the world, nine registered full-size parts and four lamps. The desk is a 80×56 px ellipse (5×4 cell footprint at origin (24, 20) in the box) with a one-cell opening in the south arc, a cherry top plane with an inlaid line, a panelled face with label plates, and a linen mat in the clerk's space. The luminous ceiling ring shows as sea-blue floor inlay rings.

**Split for depth.** `archive_desk_back` (rear_prop, carries the whole desk's collision `11111/11111/11011/11011`) and `archive_desk_front` (front_prop, no collision) divide the ring at its centre line, so a person inside the ring stands between them and the near edge hides their legs. Items sit only on the back half, so the front arc can never cover them.

| Change after the Records review | How |
| --- | --- |
| Folder labels regain colour | `archive_folders_before` (every folder and tab one dull linen) swaps for `archive_folders_after` (coral, sea blue and linen folders with lit label tabs). levels.md 11 |
| The luminous ring lights its floor pool | `archive_ring_glow_after`, one linen step inside the inlay, `where_color` on the bare floor fill. levels.md 11 and game-design (luminous ceiling ring) |
| The ledger mark is accepted | `archive_ledger_before` (coral cross) swaps for `archive_ledger_after` (tick and stamped seal). levels.md 08 "stamp mark changes from rejected to accepted" |
| Ring lamps wake | all four lamps switch from the steady glow to the wider pulse glow |

The two states differ in **1399 px** (`records-landmark-states.png`). The only palette is Records ramps.

## Reference room

20×12 cells (320×192, the view is 320×180). Built only from atlas entries by `kitlib.render_layout` in three passes (back layers, the Engineer, front layers). The main route enters at the bottom (cells 10-11), runs north, turns east along rows 4-5 and ends at the door, marked by two inlay lines and cherry arrows. Along it: the landmark at cell (3, 3), north-wall shelving and cabinets, the file wall, planters, lamps, two windows with light shafts, and a south-east work nook of three glass partitions, a terminal desk and a plain desk. Floor is slab cells with 18 wear chips and no other texture.

Programmatic review (`build_records.py`, all pass):

| Check | Result |
| --- | --- |
| BFS over 2×2 windows on the collision grid, door open | a two-cell-wide corridor of 14 steps from (10,10) to (17,4), 30 route cells, all free of props |
| Door closed | no route (the door state drives the collision) |
| File wall | closed blocks cols 13-16; open leaves cols 14-15 free |
| Keyboard inset (view x 5-125, y 126.5-175) | landmark, ring, door, terminal desk, route start and corner, file wall: none intersect it |
| Doorway brightness | open doorway 99 luma vs adjacent wall 55 |
| Palette | all 26 atlas colours are Records ramp steps, none violet; `check_atlas.py` rejects the four marker hexes |
| Atlas | `ATLAS CHECK PASSED` (schema, grid, hard pixels, collision, anchors, state sets, landmark change count, layout references) |

## Director decisions (proposed)

1. **Reuse by exact hex swap, not redraw.** Floor, walls, windows, door, lamp, desk, chair and planters are the approved Orientation pieces recoloured; the swap raises on any unmapped pixel. They keep their approved shapes, footprints and state sets.
2. **Wayfinding in cherry, not brass.** Per PALETTES_SPEC decision 5 the door frame and the route arrows use the wood ramp; the sign plate is linen with a coral folder. The Orientation RECORDS mat is not reused (the Records entrance has no door to mark); two cherry arrows and inlay lines do its job.
3. **Route inlay is one floor step darker than Orientation's** (floor step 1 instead of step 2) because the Records floor is darker and cooler. Without that the line vanished next to the slab joints.
4. **Chair is sea-blue**, not coral, so the cherry desk and coral files are not all one hue.
5. **Shelving is sea-blue metal** (the glass ramp's body steps), with coral, linen, sea-blue and cherry boxes in clusters, matching "sea-blue shelving, linen labels, coral folders, cherry cabinets".
6. **Landmark after state** (levels.md leaves it open for 11): folders recoloured, floor pool lit, ledger stamped, lamps pulse. These follow level 11's "folder labels regain coral and sea-blue variation" and "beneath the luminous ring", and level 08's stamp mark. Shelf-end gold lights are not drawn (marker gold is forbidden on art); the lamp states cover wake behaviour.
7. **File wall is a kit state set, not part of the landmark.** levels.md 11 slides the shelves apart after the review. It is placed in the reference room at (12, 2). The implementation can place it wherever the return loop to Mira's chute lies.
8. **Back and front desk parts.** The ring is split at its centre line so an actor in the ring is occluded correctly; collision lives on the back part only.
9. **Footprint rounding.** The desk's 25% rule gives `11111/11111/11011/11011`: the clerk's space is the cell above the opening and the opening cell. Level data may override.
10. **Lamp glow is a linen step** (`#EBE7D6`) composited on the bare floor fill `#BCD0D4`, not brass, for the same reason as decision 2.
11. **Light shaft is a new composited light entry** so daylight can fall on bare floor only and never recolour joints, props or inlays.
12. **Entrance is an open edge.** The room has no south wall: the map continues, like Orientation's bottom edge. The door is on the east wall as in Orientation and is the exit to the next room.

## Known gaps and notes

- The doorway interior keeps Orientation's shapes recoloured with the Records glass ramp, so the room beyond reads dark blue. It is brighter than its walls but not luminous. A Records-specific interior (the pale floor continuing) would need a region-aware recolour.
- The desk's `contact_shadow` rectangle is the bounding box of a ring-shaped shadow, so it is a loose hint.
- The atlas sheet shows each landmark part alone; `records-landmark-states.png` shows them composed.
- `terminal_desk`, `cabinet` and `partition` footprints round the body to cells; chairs and planters block.

## Quest props (levels 07 to 11, Mira's routes after 07 and 11)

**Status:** built 2026-10-02 by the district-kits team (branch `feat/art-district-quest-props`). The audit of every named prop is [QUEST_PROP_AUDIT.md](QUEST_PROP_AUDIT.md) (rows R1 to R30); this section is the Records half of its "New" rows. The 48 entries above, the reference room and every file listed in the first table are unchanged (the atlas gained 17 entries after the landmark parts, so no earlier rect moved). Drawing helpers shared with the other three districts live in `quest_props.py`; the Records recipes are in the "quest props" section of `records_kit.py`.

New outputs: `records-quest-props-room.json` (a second composition built only from `records-atlas`, 92 placements), `records-quest-props-before-native.png` and `-before-1366x768.png` (every new prop in its first state, Mira beside the chute, the Engineer in the corridor), and `records-quest-props-after-native.png` and `-after-1366x768.png` (every state set switched: door open, shelf lights on, chute ready, folders aligned, ledger lit, ladder rolled, original report down). The atlas is now 65 entries and 10 state sets. `build_records.py` runs the same programmatic review for this room (below) and exits 1 on a failure.

### Entries

| Entry | Size px | Footprint, collision | Layer | y_sort | Anchor | Contact shadow |
| --- | --- | --- | --- | --- | --- | --- |
| `repair_door_closed` | 32x34 | 2x2, `11/11` | rear_wall | no | [16, 32] | [0, 32, 32, 2] |
| `repair_door_half` | 32x34 | 2x2, `11/11` | rear_wall | no | [16, 32] | [0, 32, 32, 2] |
| `repair_door_open` | 32x34 | 2x2, `00/00` | rear_wall | no | [16, 32] | none |
| `shelf_end_light_off` | 6x12 | 1x1, `0` | rear_prop | yes | [3, 12] | none |
| `shelf_end_light_on` | 6x12 | 1x1, `0` | rear_prop | yes | [3, 12] | none |
| `courier_chute_idle` | 34x30 | 2x1, `11` | rear_prop | yes | [16, 28] | [1, 28, 33, 2] |
| `courier_chute_ready` | 34x30 | 2x1, `11` | rear_prop | yes | [16, 28] | [1, 28, 33, 2] |
| `folder_rack_drift` | 34x24 | 2x1, `11` | rear_prop | yes | [16, 22] | [1, 22, 33, 2] |
| `folder_rack_aligned` | 34x24 | 2x1, `11` | rear_prop | yes | [16, 22] | [1, 22, 33, 2] |
| `ledger_table_before` | 66x18 | 4x1, `1111` | rear_prop | yes | [32, 16] | [1, 16, 65, 2] |
| `ledger_table_after` | 66x18 | 4x1, `1111` | rear_prop | yes | [32, 16] | [1, 16, 65, 2] |
| `rolling_ladder_closed` | 66x34 | 4x1, `1111` | rear_prop | yes | [32, 32] | [1, 32, 65, 2] |
| `rolling_ladder_open` | 66x34 | 4x1, `1001` | rear_prop | yes | [32, 32] | [1, 32, 65, 2] |
| `report_table_before` | 36x18 | 2x1, `11` | rear_prop | yes | [16, 16] | [1, 16, 35, 2] |
| `report_table_after` | 36x18 | 2x1, `11` | rear_prop | yes | [16, 16] | [1, 16, 35, 2] |
| `mira_decor_courier_loop` | 12x12 | 1x1, `0` | rear_prop | yes | [6, 12] | none |
| `mira_decor_archive_folder` | 12x9 | 1x1, `0` | rear_prop | yes | [6, 9] | none |

State sets (switching entries inside a set never moves a pixel: each pair is cropped to one shared box): `repair_door` (closed, half, open; 120 ms per state), `shelf_end_light` (off, on), `courier_chute` (idle, ready), `folder_rack` (drift, aligned), `ledger_table` (before, after), `rolling_ladder` (closed, open; blocked is true when closed), `report_table` (before, after).

| Prop | What it is |
| --- | --- |
| Repair door (level 07) | A north-wall door that replaces two plain wall tiles (it carries the wall's own cap, 34 px tall). A display band holds two clear text windows: the address line with a coral cursor between typed characters, and the two sides of the cursor (a Backspace chevron to the left, a Forward Delete chevron to the right). Below, two cherry leaves with glass panes; half slides them 6 px into the jamb pockets, open 12 px, showing a lit archive with shelf-end stripes and a mat. No flashing failure state. Do not put plain wall tiles under it: open leaves rows 0-1 of its cells walkable. |
| Shelf-end light (07) | A 6x12 strip: dull sea-blue glass off, a linen core with a peach edge on. Gold is a UI marker hex and never appears in world art, so the "gold" of levels.md is linen and peach here (decision 6 above still holds). |
| Courier chute (07, 11) | Mira's chute, 2x1: a metal cabinet with a coral-lipped slot, a tube rising into the ceiling, a catch tray with a stack of slips, an indicator lamp. Ready (Mira has a route): a slip stands in the slot and the lamp is lit coral. |
| Folder rack (08) | A low cherry rack with six sea-blue folders behind a front lip. Drift: tabs at uneven heights and shifts, dull labels. Aligned: one tab line in a regular rhythm, linen labels with a coral mark. |
| Ledger table (09) | A 4-cell cherry table with one long open folio. Before: both sign-offs in the middle, dull wood. After: sign-offs at both margins, both ends lit (lit wood, bright pages). Lay one or two `light_shaft` entries across it for the beam of daylight. |
| Rolling ladder (09, 10) | A 4-cell gallery wall: a shelf cell at each end, a two-cell opening onto the stair to the upper gallery, a rail with wheels and a cherry ladder. Closed: the ladder stands across the opening and all four cells block. Open: it has rolled in front of the left shelf (about 19 px) and cells 1-2 are free. Also the "elevator-like rolling shelf" of level 10. |
| Report table (10) | A 2-cell cherry table with Pace's grey summary (three orderly bars). After: the original report lies beside it (cherry cover, coral spine, linen label). |
| Mira decor | Courier Loop: a linen medal with a coral loop arrow on a small stand. Archive Loop: a coral desk folder with a lit tab and a sheet showing. One cell, no collision, set on a desk, cabinet or table top. |

### Review (`build_records.py`, quest room)

| Check | Result |
| --- | --- |
| Coverage | all 17 new entries are drawn in the room (a placed state set counts all its states, so the door's half frame is covered) |
| Corridor | with the door open a two-cell-wide walkway of 11 steps from (8,10) to (8,0) (the door's cells); with it closed there is none |
| Props | the corridor cells are free of props |
| Inset | door, tables, chute, ladder, rack, shelf lights, corridor start: none intersect the keyboard inset |
| Palette | the existing check covers the atlas: every colour is a Records ramp step (27 colours now), no violet, `check_atlas.py` rejects the four marker hexes |
| Layout | `check_atlas.check_layout` on `records-quest-props-room.json` is clean |

### Director decisions (quest props)

1. **The repair door is a front-facing door, not a recolour of `archive_door`.** The existing door is an east-wall door seen from the side with a RECORDS sign. The brief's door asks for two text windows, a visible cursor and the deletion side, so it is a new north-wall door; a level designer can use either orientation for any door.
2. **The text windows are a display band above the leaves, not on them.** The leaves slide away; the windows stay so the player can keep reading the address while the door answers.
3. **No gold on shelf-end lights.** Linen with a peach edge reads as lit against the sea-blue strip and keeps the marker hex out of world art.
4. **`rolling_ladder` doubles as the elevator-like rolling shelf of level 10.** It is a rail-mounted shelf run with a movable ladder; the stair opening is the gallery access. One entry pair, no separate lift.
5. **Mira's chute is one cabinet per district, recoloured by palette.** The drawing is shared (`quest_props.courier_chute`), so Records, Systems and Night Shift chutes read as the same object.
6. **Decor is a desk decoration, not a furniture entry.** Courier Loop and Archive Loop are 12 px objects set on a desk top; levels.md names the Archive Loop "desk folder" explicitly, the Courier Loop token is the matching plaque for the first route.
7. **State pairs share a crop box.** `folder_rack_drift` has taller tabs than `folder_rack_aligned`; both are cropped to one box so the rack body never shifts when the state swaps.


## District integration (wave 2)

Branch `feat/art-district-integration`. Proof room: `records-integration-room.json` and `records-integration-proof-{before,after}-{native,1366x768}.png` (three elevators closed, half and open with the call panel, a seated worker behind `desk_a` with its occluder over the actor, an artifact on `desk_b` and three on cabinets, the cabinet gate, the log cabinets, the address panel, the ledger mark on a desk).

| New entry | Footprint, collision | Layer | Notes |
| --- | --- | --- | --- |
| `elevator_closed`, `elevator_half`, `elevator_open` (state set `elevator`) | 3x3, `111/111/000` (open `111/101/000`) | rear_wall | Orientation's module (`shared_pieces.elevator_doors`) in the Records ramps; geometry asserted equal to `orientation-atlas.json` |
| `elevator_call_panel` | 1x2, `0/0` | rear_wall | `shared_pieces.elevator_call_panel`, Records ramps |
| `desk_a_front`, `desk_b_front` | 2x1, `00` | front_prop | Cut from the district desk at the Orientation fit rows (monitor plus 8 px of top plane); the build asserts zero differing pixels against `desk_a` / `desk_b` |
| `artifact_carbon_copy_a`, `artifact_margin_stamp`, `artifact_uncut_index`, `artifact_noor_annotation` | 1x1, `0` | front_prop | `shared_pieces.artifact_prop`, 16x16 with glint cue. The slug is `noor_annotation` (data name); the drawing kind is `noors_annotation` |
| `cabinet_gate_misaligned` / `cabinet_gate_aligned` (state set `cabinet_gate`) | 2x1, `11` / `00` | rear_prop | Two file cabinets pushed crooked across the doorway, then squared and pushed 14 px back. Same sprite box in both states |
| `cabinet_labels_offset` / `cabinet_labels_aligned` (state set `cabinet_labels`) | 2x1, `11` | rear_prop | Cherry log cabinet, sea-blue folders with linen tabs at uneven shifts, then on one line with a coral mark |
| `archive_ledger_mark_rejected` / `archive_ledger_mark_accepted` (state set `ledger_mark`) | 1x1, `0` | rear_prop | Opaque 12x7 overlay, the landmark's own ledger pixels (build asserts equality with `archive_ledger_before` / `_after`). Place at the landmark footprint origin + (26, 4), after the landmark parts. It covers the landmark ledger, so level 08 can accept the mark before the folders and ring change at level 11 |
| `door_panel_address_idle` | 1x1, `1` | rear_prop | Wall plate 15x27: two text windows (address line with cursor; Backspace and Forward Delete sides), slot, dull idle lamp |

Decisions: (1) The ledger mark is a full-ledger overlay, not a bare mark, so a state swap can never show two marks. (2) `mail_chute_*` and `rolling_ladder_parked/moved` in the level data are the kit's `courier_chute_idle/ready` and `rolling_ladder_closed/open` (art names win); no new entries. (3) Records has no occluder gaps: both desks get fronts. (4) The level data declares the elevator as 2x1 with collision `11`; the kit module is 3x3 per the player's decision, so the map must adopt the 3x3 footprint.
