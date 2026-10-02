# Systems environment kit and the routing machine (task 7.2)

**Status:** Approved by the director 2026-10-02.

**Sources:** `openspec/changes/complete-art-production/` (environment-kit spec, design decisions 3 and 4), STYLE_BIBLE §3, §6 and §7, PALETTES_SPEC.md (Systems ramps), `levels.md` Systems row and levels 12 to 16, `docs/game-design.md` (district table, "Systems reference layout"), RECORDS_KIT_SPEC.md and ORIENTATION_KIT_SPEC.md (the atlas format and method), `design/characters/hal.md` (flavour: utility vest, orange tool roll, folding stool). **Director decision** marks choices that need recording.

Same atlas format and tooling as Orientation and Records. No shared file was edited: `kitlib.py`, `shared_pieces.py`, `build_kit.py`, `check_atlas.py`, `records_kit.py` and `orientation_kit.py` are untouched. `build_systems.py` imports the renderer, BFS and screen helpers from `build_records.py`.

## Deliverables

| File | What it is |
| --- | --- |
| `systems_kit.py` | Systems recipes: hex-swap of Orientation pieces, capture of the shared pieces, conduit channels, racks, status board, bridge pieces, route arrows, the landmark, the atlas JSON |
| `build_systems.py` | Writes every output below, then runs the programmatic review and exits 1 on any failure |
| `systems-atlas.png` / `.json` | 78 entries on a 640×848 px sheet, 16 px grid, 14 state sets, validated by `check_atlas.py` |
| `systems-atlas-sheet.png` | Every entry at ×4 with footprint, collision, anchor and contact shadow |
| `systems-landmark-states.png` | The routing machine before, after and the changed pixels (2553 px) at ×4 |
| `systems-reference-room.json` | The walkable room as a cell layout: floor grid plus 117 placements, atlas data only |
| `systems-reference-room-native.png`, `-1366x768.png` | The room, before state, Engineer on the route, native 320×192 and the ×4 view |
| `systems-reference-room-keyboard-inset.png` | The same ×4 view with the keyboard inset overlaid |
| `systems-reference-room-after-native.png`, `-after-1366x768.png` | After state: machine after, door open, every conduit lit, lamps pulsing |
| `systems-reference-room-route.png` | Review overlay: blocked cells, the BFS route and the inset |

Rebuild: `python3 build_systems.py`. Check: `python3 check_atlas.py` (picks up `systems-atlas.json` and `systems-reference-room.json` by its existing globs). Both need Pillow and numpy.

## Palette

Systems ramps only (PALETTES_SPEC): 28 colours (ink shared, porcelain floor, steel-blue wall, cobalt glass, cool-sand wood, mint foliage, safety-orange accent). No violet, no marker hex, in particular no `#19AFA2`. Screens and devices use the cobalt glass ramp and the mint circuit ramp. Safety orange is trim only: hazard stripes, warning plates, rail tops, door sign chevron, and one conduit family. It measures 1.2% of the room's pixels.

## Contents

| Group | Entries |
| --- | --- |
| Floor | `floor_j/h/v/p`, `floor_chip` (Orientation tiles recoloured to porcelain), `route_inlay`, `route_inlay_v` (line in floor step 1) |
| Wayfinding | `route_arrow_e`, `route_arrow_n` (cobalt, new) |
| Conduits (new, drawn) | `conduit_{h,v,ne,nw}_{cobalt,mint,orange}` and the same with `_lit`: 24 tiles, and 12 state sets of the same names (`off`, `lit`) |
| Walls | `wall_n_plain`, `wall_n_window_a/b`, `wall_e_plain` (recoloured: steel-blue face, cobalt glass); `status_board` (new) |
| Door | `service_door_closed/_half/_open`, state set `service_door` |
| Lamp | `lamp`, `lamp_off`, `lamp_glow_on`, `lamp_glow_pulse`, state set `lamp` |
| Reused props | `desk_a/b`, `chair`, `pot_plant_a/b` |
| Shared kit (Systems ramps) | `shelf_1x1`, `shelf_2x1_a/b`, `partition_1x1`, `partition_2x1`, `terminal_desk`, `cabinet_1x1`, `cabinet_2x1` |
| New props | `rack_1x1`, `rack_2x1_a/b`, `bridge_deck`, `bridge_rail` |
| Landmark | 15 parts (below), landmark `routing_machine` |

Not included: the shared `light_shaft` (the floor is already the lightest step, so daylight cannot lighten it), `file_wall`, and the Orientation mat and garden pieces.

## New pieces

- **Floor conduit channels.** A flush steel trench 8 px wide with a rim (shadow side top and left) and a 4 px conduit core. Three families, kept visually separate by hue: **cobalt** (payroll, east), **mint** (alarm, west), **orange** (formula and bridge). Unlit, the core uses the family's two darker steps; lit, its two lighter steps. Shapes: straight h and v (with clamp collars) and two corners, `ne` (arms north and east) and `nw` (north and west). A lit run is a rename or a state switch, so the implementation can light segments one per about 150 ms from the hub outward. The two south and north corners are not drawn; add them if a level needs them.
- **Server rack** (1×1, 2×1 a and b; sprite 28 px tall, footprint the bottom 16 px). Cobalt top plane with a cooling grille, four porcelain blades per cell with mint status lights and occasional orange warnings, and one patch row with hanging cables in the three family colours.
- **Status board.** A wall overlay, 48×22 px: cobalt rim, porcelain label strip, six indicator lights in the family colours. The alarm hall fixture.
- **Bridge deck and rail.** `bridge_deck` is a walkable slatted tile. `bridge_rail` is a glass balustrade with an orange top rail that blocks its cell. They stand for the glass bridge and service-walkway edge, and are placed as a gallery in the room.
- **Door.** Orientation's sliding door, recoloured by exact swap with PALETTES_SPEC decision 5: sand frame, cobalt leaves, a porcelain sign plate with an orange chevron. States and collision are unchanged. The half and open states swap the room beyond to a lit porcelain corridor (a region rule inside the swap), because the cobalt interior was darker than the steel-blue wall. Open doorway 149 luma against 55 for the east wall.

## Landmark: the routing machine

160×144 px (10×9 cells), the same pixel size as the rest of the world. A cobalt chassis 96×64 px (6×4 cell footprint at origin (32, 40) in the box, collision `111111` ×4) with a top plane (two porcelain service hatches, a glass dome with its core, rear vents, a beacon mast, an orange riser), a face with ten node sockets, three recesses (west port, false panel, east port) and a hazard-striped base. 15 registered full-size parts.

| Part | Layer | In |
| --- | --- | --- |
| `routing_deck_plate` | floor_marking | both |
| `routing_machine` (body, shadow, collision) | rear_prop | both |
| `routing_stubs_before/_after` | floor_marking | before / after |
| `routing_core_before/_after` | rear_prop | before / after |
| `routing_nodes_before/_after` | rear_prop | before / after |
| `routing_beacon_before/_after` | rear_prop | before / after |
| `routing_ports_before/_after` | rear_prop | before / after |
| `routing_panel_closed/_open` | rear_prop | before / after |
| `routing_walkway_after` | floor_marking | after only |

The machine is tall, so it stays one y-sorted `rear_prop`: a person north of it is drawn first and the body covers them, which is right.

| Change after the Systems review | How |
| --- | --- |
| Ten routing nodes light | dark nodes swap for lit mint nodes with a pale head. levels.md 12 |
| The dome core lights every circuit | hub, ring and three spokes, one per family (mint west, cobalt east, orange north). levels.md 16 "lights in an intelligible sequence" |
| The warning light steadies | orange beacon with a halo swaps for a calm mint head. levels.md 13 |
| Ports, riser and floor stubs light | dull steps swap for lit steps. levels.md 12 and 16 "each correct node lights a conduit" |
| A service walkway opens | a grated deck with orange hazard edges along the route. levels.md 16 |
| The false panel drops open | a closed porcelain hatch swaps for a hanging flap and a lit cavity with the Night Shift elevator stop (two doors and call arrows). levels.md 16 |
| Lamps wake | all four lamps go from the steady glow to the wider pulse glow |

The two states differ in **2553 px** (`systems-landmark-states.png`).

## Reference room

20×12 cells (320×192; the view is 320×180). Built only from atlas entries by `kitlib.render_layout` in three passes. The main route enters at the bottom (cells 10-11), runs north, turns east along rows 4-5 and ends at the door, marked by cobalt arrows and two inlay lines. Along it: the machine at cell (3, 3); a status board and two rack groups on the north wall; the three conduit runs (mint west to the alarm terminal, cobalt east, crossing the route as flush channels, to the payroll terminal, orange east and up toward the wall); two terminal desks; a locker; parts shelving; a short bridge gallery of deck tiles and rails in the south-east; three mint-lit planters; two windows; lamps. Conduits are anim placements, so the room's after state lights them by state (`conduit_*` to `lit`) with no layout change.

Programmatic review (`build_systems.py`, all pass):

| Check | Result |
| --- | --- |
| BFS over 2×2 windows on the collision grid, door open | a two-cell-wide corridor of 14 steps from (10,10) to (17,4), 30 route cells, all free of props |
| Door closed | no route |
| Machine and walkway | the 6×4 footprint blocks; the walkway cells and every conduit segment stay walkable |
| Keyboard inset (view x 5-125, y 126.5-175) | machine, beacon, walkway, door, both terminals, racks, board, route start and corner, orange uplink: none intersect it |
| Doorway brightness | open doorway 149 luma vs adjacent wall 55 |
| Palette | all 28 atlas colours are Systems ramp steps; no violet, no marker hex; no violet-family floor or wall step |
| Orange share | 1.21% of the room before, 1.28% after (limit 4%) |
| Atlas | `ATLAS CHECK PASSED`; `build_kit.py` still ends `ZERO DIFF` |

## Director decisions (proposed)

1. **Reuse by exact hex swap, not redraw.** Floor, walls, windows, door, lamp, desk, chair and planters are the approved Orientation pieces recoloured; the swap raises on any unmapped pixel. This build adds a pixel-region rule (the door's corridor) beside Records' row rule.
2. **Three conduit families by hue: cobalt, mint, orange.** They carry levels.md's "three conduit families stay visually separate" with the three accent ramps Systems already has, and echo the board lights, rack cables and dome spokes.
3. **Wayfinding in cobalt, orange kept for trim.** PALETTES_SPEC decision 5 puts wayfinding on the wood or glass ramps, and the brief keeps orange small. The route arrows are cobalt, the door frame is sand, orange is hazard stripes, warning plates, rail tops and one conduit.
4. **Route inlay uses floor step 1**, as in Records, so the line outranks the slab joints (step 2) on the near-white floor.
5. **Conduit corners limited to `ne` and `nw`.** The room needs only those; developers add `se` and `sw` through the same function.
6. **Lit state is a swap, not a glow layer.** The lit conduit is a separate entry plus a state set, because a conditional composite cannot carry a different pipe shape.
7. **Door interior in porcelain.** The recoloured cobalt interior was darker than the wall, so the half and open states show a lit corridor.
8. **Mint planters are device-lit and sparse** (PALETTES_SPEC decision 4). Two of the twelve layouts.
9. **Shelving, partition, terminal and cabinet reuse the shared pieces with the Systems ramps.** Shelves hold orange, steel, porcelain and sand bins (parts); the cabinet is a sand tool locker; the terminal desk has a steel-blue top and a cobalt face.
10. **Landmark after state** (levels.md leaves it open for 16): nodes, core, beacon, ports and stubs lit; walkway; false panel dropped on the elevator stop; lamps pulse. The bridge and return walkway opening earlier (levels 12 and 15) is a layout item using `bridge_deck` and `bridge_rail`.
11. **One y-sorted body.** The machine is not split into back and front parts because nothing walks inside it; collision is the full 6×4 footprint.
12. **Footprint.** The body is exactly 6×4 cells, so the collision is the whole block. Level data may open an access cell on the south face.
13. **Entrance is an open edge.** No south wall, as in Orientation and Records. The door is on the east wall as the exit to the next room (the Night Shift elevator stop is revealed on the machine's panel).
14. **No light shaft.** The porcelain floor fill is the lightest step, so daylight cannot lighten it. Lamp glow is a pale-mint step on the bare fill.

## Known gaps and notes

- `contact_shadow` for the machine is a bounding box of the cast strip below the body; the open flap casts its own shadow inside the panel part.
- The walkway part is registered at the machine's east flank on rows 4-5, so it follows the route's first segment. A level that places the machine elsewhere moves it with the landmark; the walkway cannot be repositioned alone.
- The bridge gallery in the room is a demonstration of the deck and rail pieces, not the formula room.
- The false panel flap hangs 4 px below the footprint. It is decoration, not collision.

## Quest props (levels 12 to 16, Mira's routes after 13 and 16)

**Status:** built 2026-10-02 by the district-kits team (branch `feat/art-district-quest-props`). The audit of every named prop is [QUEST_PROP_AUDIT.md](QUEST_PROP_AUDIT.md) (rows S1 to S25); this section is the Systems half of its "New" rows. The 78 entries above, the reference room and every file listed in the first table are unchanged (the atlas gained 22 entries after the landmark parts, so no earlier rect moved). Drawing helpers shared with the other districts (the courier chute, the Mira decorations, the 3x5 pixel font) live in `quest_props.py`; the Systems recipes are in the "quest props" section of `systems_kit.py`.

New outputs: `systems-quest-props-room.json` (a second composition built only from `systems-atlas`, 74 placements), `systems-quest-props-before-native.png` and `-before-1366x768.png` (every new prop in its first state, Hal near his stool, Mira beside the chute), and `systems-quest-props-after-native.png` and `-after-1366x768.png` (every state set switched: keypad lit, bridge extended, sign green, display reversed, alarms separated, shutters open, formula lit, chute ready). The atlas is now 100 entries and 22 state sets. `build_systems.py` runs the quest review (below) and exits 1 on a failure.

### Entries

| Entry | Size px | Footprint, collision | Layer | y_sort | Anchor | Contact shadow |
| --- | --- | --- | --- | --- | --- | --- |
| `payroll_keypad_off` | 34x32 | 2x1, `11` | rear_prop | yes | [16, 30] | [1, 30, 33, 2] |
| `payroll_keypad_half` | 34x32 | 2x1, `11` | rear_prop | yes | [16, 30] | [1, 30, 33, 2] |
| `payroll_keypad_lit` | 34x32 | 2x1, `11` | rear_prop | yes | [16, 30] | [1, 30, 33, 2] |
| `bridge_span_retracted` | 64x32 | 4x2, `0110/0110` | floor_marking | no | [32, 32] | none |
| `bridge_span_extended` | 64x32 | 4x2, `0000/0000` | floor_marking | no | [32, 32] | none |
| `refund_sign_red` | 24x14 | 2x1, `00` | rear_wall | no | [16, 16] | none |
| `refund_sign_green` | 24x14 | 2x1, `00` | rear_wall | no | [16, 16] | none |
| `calc_display_charge` | 36x18 | 2x1, `11` | rear_prop | yes | [16, 16] | [1, 16, 35, 2] |
| `calc_display_refund` | 36x18 | 2x1, `11` | rear_prop | yes | [16, 16] | [1, 16, 35, 2] |
| `folding_stool` | 14x14 | 1x1, `1` | rear_prop | yes | [7, 14] | [2, 13, 10, 1] |
| `alarm_strip_merged` | 64x18 | 4x2, `0000/0000` | rear_wall | no | [32, 32] | none |
| `alarm_strip_separated` | 64x18 | 4x2, `0000/0000` | rear_wall | no | [32, 32] | none |
| `alarm_strip_muted` | 64x18 | 4x2, `0000/0000` | rear_wall | no | [32, 32] | none |
| `bridge_shutter_closed` | 30x20 | 2x2, `00/00` | rear_wall | no | [16, 32] | none |
| `bridge_shutter_open` | 30x20 | 2x2, `00/00` | rear_wall | no | [16, 32] | none |
| `formula_wall_dark` | 96x22 | 6x2, `000000/000000` | rear_wall | no | [48, 32] | none |
| `formula_wall_half` | 96x22 | 6x2, `000000/000000` | rear_wall | no | [48, 32] | none |
| `formula_wall_lit` | 96x22 | 6x2, `000000/000000` | rear_wall | no | [48, 32] | none |
| `courier_chute_idle` | 34x30 | 2x1, `11` | rear_prop | yes | [16, 28] | [1, 28, 33, 2] |
| `courier_chute_ready` | 34x30 | 2x1, `11` | rear_prop | yes | [16, 28] | [1, 28, 33, 2] |
| `mira_decor_signed_sent` | 13x9 | 1x1, `0` | rear_prop | yes | [7, 9] | none |
| `mira_decor_relay` | 12x10 | 1x1, `0` | rear_prop | yes | [6, 10] | none |

State sets (each pair or triple is cropped to one shared box, so a swap never moves a pixel): `payroll_keypad` (off, half, lit), `bridge_span` (retracted blocks, extended walks), `refund_sign` (red, green), `calc_display` (charge, refund), `alarm_strip` (merged, separated, muted), `bridge_shutter` (closed, open), `formula_wall` (dark, half, lit), `courier_chute` (idle, ready).

| Prop | What it is |
| --- | --- |
| Payroll keypad (12) | A 2-cell console: a glass-backed ID tray with five cards (one with an orange stripe) behind a cobalt pane, a steel top plane with ten key nodes in two rows (digits 1-5, then 6-0), a cobalt face with ten progress lights. Off: all dark. Half: the first five lit mint. Lit: all ten. The machine's own ten nodes (landmark) and the `conduit_*` sets carry "each correct node lights a conduit". |
| Bridge span (12) | The glass bridge's span, 4x2 on the floor markings with orange hazard stripes on both long edges. Retracted: a deck tile at each end and an open trussed pit with a cobalt service conduit below, the middle two columns block. Extended: deck from end to end, walkable. Put `bridge_rail` entries on the rows above and below it. |
| Refund sign (13) | A 24x14 wall plate reading as a price tag. Red: a safety-orange plate with "+85" (the refund became a charge). Green: a mint plate with "-85". Systems has no pure red or green (decision 1 below). |
| Calculator display (13) | A 2-cell steel desk with a display sunk into the top and an open ledger beside it. Charge: "+85" with an orange plus and an orange ledger mark. Refund: "-85" with a mint minus and a mint mark. |
| Folding stool (13) | Hal's stool: a sand canvas seat on crossed steel legs with his orange tool roll leaning on it. Hal's pose is the cast team's. |
| Alarm strip (14) | A 64x18 wall overlay of six alert cells, each a lamp over a porcelain label plate. Merged: six identical cobalt lamps over blank plates. Separated: six lamps (blue, green, orange, sand, pale blue, pale green) and six pictograms (ring, triangle, square, diamond, cross, bar). Muted (Quiet Alarm): as separated with the sixth lamp dark and slashed. |
| Bridge shutter (15) | A 30x20 wall overlay in the window overlay's footprint. Closed: steel louvres over the pane. Open: the louvres stack at both sides and the cobalt pane shows. |
| Formula wall (15) | A 96x22 wall overlay of six clause boxes joined by traces, each holding one of `& * ( ) _ +` at double size. Dark, half (three boxes and their traces lit mint), lit. |
| Courier chute (13, 16, Mira) | Mira's chute, drawn once in `quest_props.courier_chute` for three districts: a cabinet with an orange-lipped slot, a tube rising into the ceiling, a catch tray, an indicator lamp. Ready: a slip in the slot and an orange lamp. |
| Mira decor | Signed and Sent: an envelope with a stamped seal and a signature line. Signal Keeper: a miniature relay (cobalt block, copper coil, two terminals, a mint LED). One cell, no collision, set on a desk or locker top. |

### Review (`build_systems.py`, quest room)

| Check | Result |
| --- | --- |
| Coverage | all 22 new entries are drawn in the room (a placed state set counts all its states, so the half and muted states are covered) |
| Bridge | retracted: the four pit cells block, the four end cells are free; extended: all eight cells free; a two-cell-wide walkway of 6 steps crosses it between the rails, and none crosses the retracted span |
| Inset | alarm strip, formula wall, sign, keypad, display, span, chute, shutters: none intersect the keyboard inset |
| Palette | the existing checks cover the atlas: every colour is a Systems ramp step (28 colours, unchanged), no violet, no marker hex; orange is still trim (1.2% before, 1.3% after, limit 4%) |
| Layout | `check_atlas.check_layout` on `systems-quest-props-room.json` is clean |

### Director decisions (quest props)

1. **Red and green are the orange and mint ramps.** Systems has neither a red nor a green. `refund_sign_red` uses the safety-orange trim steps and `refund_sign_green` the mint circuit steps; the plus or minus and the number carry the meaning, so colour is never the only cue. The names follow the brief.
2. **The payroll keypad folds the ID tray into one prop.** levels.md names "glass-backed ID trays" and "ten individually lit routing nodes" in the same wing; one console with a glass-backed tray, ten key nodes and ten progress lights covers both and keeps the wing to one entry set.
3. **Six alarm hues are three hues in two steps, plus sand.** The palette has blue, green and orange families; the sixth hue is the sand wood step. Each lamp also has its own pictogram, so the six are distinct by shape, which is what the level asks for ("six distinct alert lights and pictograms").
4. **The bridge span is floor art with its own collision.** The extended deck is the existing `bridge_deck` pattern, so a level using the old `bridge_deck` tiles and the new span matches. Rails stay separate `bridge_rail` entries so a designer can edge any run.
5. **Shutters and the formula wall are wall overlays.** They sit on the north wall face like the window overlays and the status board; the plain wall tiles keep the collision.
6. **The chute, the desk decorations and the 3x5 font are shared drawings.** They live in `quest_props.py` and take the district's `Pal`; Systems sets `PAL.paper` to the porcelain ramp (its wall ramp is steel blue) so slips and envelopes read as paper.
7. **State sets share a crop box.** Pairs and triples whose bounding boxes differ (the keypad's progress lights, the strip's lamps) are cropped to one box, so a state swap never shifts a pixel.
