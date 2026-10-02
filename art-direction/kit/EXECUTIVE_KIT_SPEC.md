# Executive environment kit and the atrium tree (task 7.4)

**Status:** Approved by the director 2026-10-02.

> **Rich finish (2026-10-02):** this kit was drawn before the rich finish and is queued for re-render (OpenSpec change `adopt-rich-finish`). New and redrawn pieces follow `../rich-finish/RICH_FINISH_SPEC.md`: vivid world palette, deeper ink (`#0E1020` outline), leaf-fan foliage, light passes. Footprints, collision and layers in this spec do not change.

**Sources:** `openspec/changes/complete-art-production/` (environment-kit spec, design decisions 3 and 4), STYLE_BIBLE §3, §6 and §7, PALETTES_SPEC.md (Executive ramps, decisions 5 and 7), `levels.md` Executive Floor and level 20, `docs/game-design.md` (district table, "Executive reference layout"), VALE_SPEC.md, RECORDS_KIT_SPEC.md (the method). **Director decision** marks choices the designer proposes for the director to record.

Same atlas format, tools and method as Records. Orientation, Records and the shared tooling are untouched: `kitlib.py`, `shared_pieces.py`, `build_kit.py`, `check_atlas.py`, `records_kit.py` and `orientation_kit.py` have no edits (`build_kit.py` still ends `ZERO DIFF`, `check_atlas.py` ends `ATLAS CHECK PASSED`).

## Deliverables

| File | What it is |
| --- | --- |
| `executive_kit.py` | Executive recipes: exact hex swap of Orientation pieces (`recolour_rect`, local), shared pieces drawn with Executive ramps, Executive-only pieces, the landmark, the atlas JSON |
| `build_executive.py` | Writes every output below, then runs the programmatic review and exits 1 on any failure |
| `executive-atlas.png` / `.json` | 63 entries on a 640×1072 px sheet, 16 px grid, validated by `check_atlas.py` |
| `executive-atlas-sheet.png` | Every entry at ×4 with footprint, collision, anchor and contact shadow |
| `executive-landmark-states.png` | The atrium tree before, after and the changed pixels (2355 px) at ×4 |
| `executive-reference-room.json` | The walkable room as a cell layout: floor grid plus 119 placements, atlas data only |
| `executive-reference-room-native.png`, `-1366x768.png` | Before state, Vale in the well and the Engineer on the route, native 320×192 and the ×4 view |
| `executive-reference-room-keyboard-inset.png` | The same ×4 view with the keyboard inset overlaid |
| `executive-reference-room-after-native.png`, `-after-1366x768.png` | After state: landmark after, final door open, windows in daylight, lamps pulsing |
| `executive-reference-room-route.png` | Review overlay: blocked cells, the BFS route and the inset |
| `executive-vale-wall-check.png` | Diagnostic: Vale idle S against the navy north wall, the alcove, the east wall mass and the navy sofa |

Rebuild: `python3 build_executive.py`. Check: `python3 check_atlas.py`. Both need Pillow and numpy.

## Contents

| Group | Entries |
| --- | --- |
| Floor | `floor_j/h/v/p`, `floor_chip` (Orientation tiles recoloured to the pale limestone ramp), `route_inlay`, `route_inlay_v` (floor step 1), `route_arrow_e`, `route_arrow_n` (copper, new) |
| Walls | `wall_n_plain` (navy face, sky-glass cap trim), `wall_n_window_a/b` (daylight), `wall_n_window_a_dim/b_dim` (overcast), `wall_n_alcove` (brighter navy, copper nameplate bar), `wall_e_plain` (navy side plane), `wall_n_trim` (copper picture rail, new) |
| Door | `final_door_closed/_half/_open`, state set `final_door` |
| Lamp | `lamp`, `lamp_off`, `lamp_glow_on`, `lamp_glow_pulse`, state set `lamp` |
| Reused props | `desk_a/b`, `chair` (navy), `sofa` (navy), `bench` (walnut), `side_table`, `pot_plant_a` to `_d` |
| Shared kit | `shelf_1x1`, `shelf_2x1_a/b` (walnut bookcase), `partition_1x1/_2x1` (sky glass), `terminal_desk` (reception console), `cabinet_1x1/_2x1` (walnut credenza), `light_shaft_cool`, `light_shaft_warm` |
| Executive-only | `boardroom_table` (4×2), `boardroom_chair`, `glass_rail_1x1`, `glass_rail_2x1`, `glass_rail_side` |
| State sets | `final_door`, `lamp`, `window_a`, `window_b` (overcast, daylight), `window_light` (cool shaft, warm shaft) |
| Landmark | 14 parts, landmark `atrium_tree` |

Everything uses Executive ramps only: 28 colours (ink shared, floor, wall, glass, wood, foliage, accent). No violet, no marker hex, no brass.

## Recolouring

`recolour_rect` is a local exact hex swap (Records' version plus rectangle rules, so a rule can remap ink steps inside one area). It raises on any pixel without a mapping, so nothing is guessed. The door interior, sign and wall mass are rule rectangles, not redraws; only the sign icon (about 40 px) is overpainted.

## Landmark: the atrium tree

176×160 px (11×10 cells), the same pixel size as the rest of the world, 14 registered full-size parts and four lamps. A tall single specimen: a slim walnut trunk with a fork and a root flare, and a tall oval crown of 15 leaf clusters (about 38 px wide, 50 tall), in a raised round planter (48×28 top plane, 11 px face with a copper band and five nameplates), inside a sunken atrium well (112×80 px, 7×5 cells, octagonal coping, a shaded inner north face, a bright floor with a thin copper ring inlay, three steps down the south gap) edged by a glass balustrade with copper caps. It differs from Orientation's garden in silhouette (tall oval, narrow trunk, against a wide low dome), in setting (round planter in a railed well with steps, against a rectangular bed with a stream inside a ring path) and in ramp use (pale stone, copper and glass, against warm stone).

**Collision** (carried by `atrium_planter`): `1111111/1011101/1011101/1000001/1100011`. The rail ring blocks, the planter blocks two rows, the three south cells are the steps, and the floor around the planter is a walkable circuit. The footprint origin sits 4 px below the well's visual top so that the collision rows lie under the visual rail rows.

**Split for depth.** The canopy is its own part (it draws over the rail and trunk, and a renderer can sway it). `atrium_rail_front` (the south runs and newel posts) is `front_prop`, so a person on the steps passes behind the rail ends. Everything else is `rear_prop` and y-sorts as one unit.

| Change after the three repairs | How |
| --- | --- |
| Copper floor lines straighten | `atrium_inlay_before` (right-angle jogs, knots and dead-end stubs) swaps for `atrium_inlay_after` (three straight lines with chevrons to the box edge). levels.md 20 |
| Nameplates become distinct | `atrium_nameplates_before` (five identical blank pale plates) swaps for `_after` (different widths, copper, navy and pale, each with its own mark). levels.md 20 |
| Repeated geometry becomes varied | `atrium_pots_before` (four identical clipped box cubes) swaps for `_after` (four soft shrubs of different sizes with copper blossoms). levels.md district row |
| Window light warms | `atrium_daylight_after`: a pale pool on the well floor, `where_color` on the well floor step. The room also switches `window_a/b` to daylight and `window_light` to the warm shaft. levels.md 20 |
| Lamps wake | all four lamps switch from the steady glow to the wider pulse glow |

The two states differ in **2355 px** (`executive-landmark-states.png`, which also shows the room around the landmark). The final door is a separate state set (`final_door`), not part of the landmark: it opens after all three repairs.

## Door

`final_door_*` are Orientation's sliding glass door recoloured by exact swap, with the PALETTES_SPEC decision 5 rule: copper frame, sky-glass leaves. The sign is a copper plate with a sunrise icon (a pale disc rising on a copper horizon, copper rays) in place of the folder. Beyond the leaves is a daylit terrace (pale floor with joints and a clipped hedge), so "the final door opens to daylight". The door's wall mass uses the navy wall ramp so the door sits in one navy wall. States and collision are unchanged: closed and half block, open walks. The open doorway measures 197 luma against 54 for the adjacent east wall.

## Reference room

20×12 cells (320×192, the view is 320×180), three passes as in Records. The main route enters at the bottom (cols 10-11), runs north, turns east along rows 4-5 and ends at the final door (visible from the entry). Along it: the atrium well at cell (2, 3) with Vale beside the planter, a bookcase and credenza, the reception alcove and console on the north wall, a south-east boardroom (three glass partitions, the long table, three navy chairs) and a south-west navy lounge (sofa, side table, bench) under the keyboard inset as decoration. Floor is slab cells with 18 wear chips. Windows are state sets: overcast in the before state, daylight in the after state.

Programmatic review (`build_executive.py`, all pass):

| Check | Result |
| --- | --- |
| BFS over 2×2 windows on the collision grid, door open | a two-cell-wide corridor of 14 steps from (10,10) to (17,4), 30 route cells, all free of props |
| Door closed | no route |
| Well collision | rail ring, planter, open steps match the declared mask; the steps are free cells |
| Keyboard inset (view x 5-125, y 126.5-175) | well footprint and steps, planter and tree, Vale, door, console, route start and corner, table: none intersect it |
| Doorway brightness | open doorway 197 luma vs adjacent wall 54 |
| Door wall mass | the wall above the door and the plain east wall share the navy mass colour |
| Palette | all 28 atlas colours are Executive ramp steps, none violet; `check_atlas.py` rejects the four marker hexes |
| Vale against walls | ink contour dE76 from every navy surface he stands against: north face 26.6, alcove 37.2, east mass 13.3, seating 13.3 (all at least 8) |
| Floor margin | Vale and the Engineer are at least 16 px below the north wall and 24 px from the east wall; the floor row in front of the north furniture along the corridor is clear |
| Landmark | 7 parts differ between states, and the lamps switch |
| Atlas | `ATLAS CHECK PASSED` (schema, grid, hard pixels, collision, anchors, state sets, landmark change count, layout references) |

## Director decisions (proposed)

1. **Reuse by exact hex swap, not redraw.** Floor, walls, windows, door, lamp, desks, chair, sofa, bench and planters are the approved Orientation pieces recoloured by `recolour_rect`, which raises on any unmapped pixel. Only the door sign icon is overpainted.
2. **East wall is navy, not ink.** Records leaves the east wall as Orientation's ink mass. Here the ink steps in `wall_e_plain` and above the door map to the navy wall ramp (PALETTES_SPEC decision 7 and the brief's "dark navy walls"), so both walls match and Vale's suit has to separate from navy everywhere, which the lit-edge step does.
3. **Copper is wayfinding and trim; neutral stone marks route edges.** Per PALETTES_SPEC decision 5 the door frame, arrows, rails and trim use the copper ramp. The route edge lines stay in floor step 1, so the copper floor lines belong to the landmark and can straighten.
4. **Landmark is a tall single tree in a railed well**, so it differs from the garden in silhouette and setting. The crown is built with the approved `env.leaves` renderer on the Executive foliage ramp.
5. **After state, tied to levels.md 20:** straightened copper lines, distinct nameplates, varied geometry (pots), warm daylight (pool and window states), lamps pulse. Five visible changes (the check needs two).
6. **Window views are state sets, not landmark parts.** The windows are in the wall, so `window_a/b` (overcast and daylight) and `window_light` (cool and warm shaft) switch with the room state; the landmark carries the pool.
7. **Overcast is flat, daylight reflects.** The dim windows swap the glass steps for the two darkest and drop the reflection band; the cool shaft is a floor-lifting pale sky blue that barely reads on the pale floor, by design.
8. **Collision shape.** The well's footprint is 7×5 with a blocked rail ring, a two-row planter and a three-cell step opening; it is one entry's mask, so a level can override. The four-cell side runs are not separately blocked.
9. **Daylight pool is `where_color` on the well floor step.** It paints only on the bare well floor, so it never washes the ring inlay, planter or rails. The pool is pale stone (the lightest floor step), not peach: peach read as an orange ring.
10. **Planter nameplates are 4 px tall.** At ×4 they read as five plates before (identical, pale) and five different plates after. A smaller size vanished into the face.
11. **Door beyond is a daylit terrace.** The Orientation interior grid maps to pale floor and joints, and the cabinet maps to a clipped hedge, so the open door reads as daylight against the navy wall without new art.
12. **Keyboard inset.** Required elements stay above view y 126.5. The well sits at footprint (32, 48) and its south steps end at y 126; decorative pieces (the lounge, the south-west pots) sit under the inset.
13. **Shared pieces use Pal clones.** The bookcase and credenza pass a `Pal` copy with the paper ramp (floor) for labels and, for the bookcase, walnut for the frame. `shared_pieces.py` is unchanged.

## Known gaps and notes

- The doorway interior is only about 20 px wide because it keeps Orientation's door geometry; the terrace reads as a bright strip beside the leaves.
- Nameplates are small. They read at ×4 by colour, and their marks are single pixels.
- `atrium_planter`'s `contact_shadow` is the bounding box of an elliptical shadow, a loose hint.
- The east and west side rails are one 6 px run per side, not cell-aligned entries. They are placed by the landmark, and `glass_rail_side` is the kit's separate cell version.
- `light_shaft_cool` is nearly the floor colour. If the director wants overcast to read more clearly, use a darker floor step for a shaded band instead.
