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
