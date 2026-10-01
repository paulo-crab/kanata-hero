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
