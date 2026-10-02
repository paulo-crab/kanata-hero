# Executive environment kit and the atrium tree (task 7.4)

**Status:** Approved by the director 2026-10-02.

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

## Quest props (level 20: the three incident branches and the arriving coworkers' places)

**Status:** built 2026-10-02 by the district-kits team (branch `feat/art-district-quest-props`). The audit of every named prop is [QUEST_PROP_AUDIT.md](QUEST_PROP_AUDIT.md) (rows E1 to E11); this section is the Executive half of its "New" rows. The 63 entries above, the reference room and every file listed in the first table are unchanged (the atlas gained 11 entries after the landmark parts, so no earlier rect moved; the landmark's `before` and `after` parts lists are byte for byte the same, and a build assertion checks it). Drawing helpers shared with the other districts (the 3x5 font, the folding stool, the Mira satchel) live in `quest_props.py`; the Executive recipes are in the "quest props" section of `executive_kit.py`.

New outputs: `executive-quest-props-room.json` (a second composition built only from `executive-atlas`, 80 placements), `executive-quest-props-before-native.png` and `-before-1366x768.png` (the three branches unrepaired, the final door closed), `executive-quest-props-partial-native.png` and `-partial-1366x768.png` (The Name and The Count repaired, The Route not: the three branches are independent), and `executive-quest-props-after-native.png` and `-after-1366x768.png` (all three repaired, the final door open, the five coworkers standing at their places). The atlas is now 74 entries and 8 state sets. `build_executive.py` runs the quest review (below) and exits 1 on a failure.

### Entries

| Entry | Size px | Footprint, collision | Layer | y_sort | Anchor | Contact shadow |
| --- | --- | --- | --- | --- | --- | --- |
| `branch_name_before` | 40x12 | 3x1, `000` | rear_wall | no | [24, 16] | none |
| `branch_name_after` | 40x12 | 3x1, `000` | rear_wall | no | [24, 16] | none |
| `branch_route_before` | 64x32 | 4x2, `0000/0000` | floor_marking | no | [32, 32] | none |
| `branch_route_after` | 64x32 | 4x2, `0000/0000` | floor_marking | no | [32, 32] | none |
| `branch_count_before` | 34x29 | 2x1, `11` | rear_prop | yes | [16, 27] | [3, 27, 29, 2] |
| `branch_count_after` | 34x29 | 2x1, `11` | rear_prop | yes | [16, 27] | [3, 27, 29, 2] |
| `place_ivo` | 13x23 | 1x1, `1` | rear_prop | yes | [7, 21] | [2, 21, 11, 2] |
| `place_noor` | 18x22 | 1x1, `1` | rear_prop | yes | [8, 20] | [1, 20, 17, 2] |
| `place_hal` | 14x14 | 1x1, `1` | rear_prop | yes | [7, 14] | [2, 13, 10, 1] |
| `place_ada` | 14x18 | 1x1, `1` | rear_prop | yes | [7, 16] | [1, 16, 9, 2] |
| `place_mira` | 16x18 | 1x1, `1` | rear_prop | yes | [7, 15] | [1, 16, 15, 2] |

State sets (each pair is cropped to one shared box): `branch_name`, `branch_route`, `branch_count` (each before, after). The landmark `atrium_tree` gains six states, so all eight combinations of the three branches are addressable: `repaired_name`, `repaired_route`, `repaired_count`, `repaired_name_route`, `repaired_name_count`, `repaired_route_count` (`before` is none, `after` is all three).

| Branch | Level 20 line | Branch prop | Atrium feature (landmark state) |
| --- | --- | --- | --- |
| The Name (a renamed department) | "nameplates become distinct" | `branch_name`: a 40x12 copper wall plate. Before: Pace's replacement, three orderly pale bars. After: the original name in irregular lettering after a small doorway crest. | `repaired_name`: the planter's five nameplates become distinct |
| The Route (a rewarded detour) | "copper floor lines straighten into useful paths" | `branch_route`: a 4x2 copper floor line, west edge to east edge. Before: an S of right angles with knots at the corners. After: one straight line with four east-pointing chevrons. Walkable; lay several end to end. | `repaired_route`: the well's copper lines straighten, and the four corner pots go from identical clipped cubes to varied shrubs (the "repeated geometry becomes varied" of the district row) |
| The Count (a corrected total) | "window views resolve into real daylight" | `branch_count`: a 2x1 tally board on two walnut feet. Before: four bars that do not add up and a dull "47". After: "52" in a copper plate with a green tick. | `repaired_count`: the warm daylight pool on the well floor and the lamps pulse; in the room, switch the `window_a`, `window_b` and `window_light` sets to `daylight` |

The after state of the landmark is the union of the three branches' changes; the build proves each branch changes only its own parts, each pair is the union of its two branches, and `after` is all three.

| Place | What it is |
| --- | --- |
| `place_ivo` | A reception lectern with his tablet on the slanted top |
| `place_noor` | A small walnut table with her stamp and a file tray of copper-tabbed folders |
| `place_hal` | His folding stool with the tool roll leaning on it (the shared `quest_props.folding_stool`, Executive ramps) |
| `place_ada` | A copper lantern stand with a lit lantern on a hook arm |
| `place_mira` | A round navy cushion with her courier satchel and its copper strap |

Each is one cell, blocks its cell, and sits where an arriving coworker stands: the coworker is a silhouette first (the cast atlases' silhouettes) and then the real sprite, both the cast team's. The after render shows the five sprites in front of their places.

### Review (`build_executive.py`, quest room)

| Check | Result |
| --- | --- |
| Coverage | all 11 new entries are drawn in the room |
| Corridor | with the final door open a two-cell-wide walkway of 14 steps from (10,10) to (17,4); closed, none; the corridor cells are free of props |
| Landmark states | eight states; each single branch changes only its own parts; each pair and `after` are the union of their branches |
| Places | the five places block their own cells and leave the corridor rows (4-5, cols 10-17) free |
| Inset | well, tree, Vale, door, nameplate, places, route line, tally board: none intersect the keyboard inset |
| Palette | the existing check covers the atlas: every colour is an Executive ramp step (28 colours, unchanged), no violet, no marker hex |
| Layout | `check_atlas.check_layout` on `executive-quest-props-room.json` is clean |

### Director decisions (quest props)

1. **The three branches are independent states of one landmark.** levels.md lets the player do them in any order and says each changes one atrium feature, so the landmark gets a state for every combination instead of a single after. The existing `before` and `after` lists are unchanged.
2. **Each branch also has its own prop in its own short branch.** The atrium features are inside the well; the branch is a separate small area with the record to repair, so each gets a nameplate, a floor line or a tally board that shows its before and after on its own.
3. **The repeated-geometry pots follow The Route.** levels.md puts "repeated geometry becomes varied" in the district row without naming a branch; a detour is the repeated geometry of the three, so the pots vary with it.
4. **The Count carries the daylight, with the lamps.** The pool is one part, so The Count's landmark state also pulses the lamps (the schema asks for at least two visible changes per state). The window sets stay separate state sets in the room.
5. **Places are props, not people.** The "arriving coworkers' places" are the objects the coworkers stand at; the silhouettes and sprites already exist in the cast atlases. The proof room draws the five sprites only in the after state.
6. **Lettering is pseudo-text.** The restored nameplate is irregular runs of pale glyph blocks, not readable letters, so the art never names a department the level data has not chosen.
7. **Names on the Wall reuses the nameplate.** The side quest's credit list is a row of `branch_name_before` and `branch_name_after` plates; no extra entry.


## District integration (wave 2)

Branch `feat/art-district-integration`. Proof room: `executive-integration-room.json` and `executive-integration-proof-{before,after}-{native,1366x768}.png` (three elevators in the copper-and-navy ramps with the call panel, a seated worker behind `desk_a` with its occluder, the audit copy on `desk_b`, the name plaque on a side table).

| New entry | Footprint, collision | Layer | Notes |
| --- | --- | --- | --- |
| `elevator_closed/_half/_open` (set `elevator`), `elevator_call_panel` | 3x3 and 1x2 | rear_wall | Orientation geometry; copper casing, navy wall mass. Stays distinct from `final_door_*` (sky-glass leaves, sunrise sign, daylit terrace) |
| `desk_a_front`, `desk_b_front` | 2x1, `00` | front_prop | Cut from the district desk (paper = the limestone floor ramp), asserted pixel-equal |
| `artifact_public_audit_copy` | 1x1, `0` | front_prop | `artifact_prop` with limestone paper |
| `desk_name_plaque` | 1x1, `0` | front_prop | Reward desk decoration (Names on the Wall), 14x9, copper plate with three name lines on a walnut base; never placed on the map |

Not covered here: Vale softening states 2 and 3 and the silhouettes of the named cast (cast team and renderer, unchanged). The level data declares a 2x3 east-wall elevator; the kit module is the 3x3 north-wall slice, so the map must adopt it.
