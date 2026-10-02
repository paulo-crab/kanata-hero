# Night Shift environment kit and the long interior window (task 7.3)

**Status:** Approved by the director 2026-10-02.

> **Rich finish (2026-10-02):** this kit was drawn before the rich finish and is queued for re-render (OpenSpec change `adopt-rich-finish`). New and redrawn pieces follow `../rich-finish/RICH_FINISH_SPEC.md`: vivid world palette, deeper ink (`#0E1020` outline), leaf-fan foliage, light passes. Footprints, collision and layers in this spec do not change.

**Sources:** `openspec/changes/complete-art-production/` (environment-kit spec), STYLE_BIBLE §3, §6 and §7, PALETTES_SPEC.md (Night Shift ramps and the edge-light rule), ADA_SPEC.md (rim ruling, draw order), `levels.md` Night Shift rows and levels 17 to 19, `docs/game-design.md` ("Night Shift reference layout"), RECORDS_KIT_SPEC.md (the method). **Director decision** marks choices that need recording; here they are the designer's proposals.

Same atlas format, tooling and method as Records. `kitlib.py`, `shared_pieces.py`, `build_kit.py`, `check_atlas.py`, `records_kit.py` and `orientation_kit.py` are untouched.

## Deliverables

| File | What it is |
| --- | --- |
| `nightshift_kit.py` | Recipes: hex swap of Orientation pieces, the Night Shift shadow and lit-edge passes, shared pieces, lamp pools, the Night Shift pieces, the landmark, the atlas JSON |
| `build_nightshift.py` | Writes every output below, then runs the programmatic review and exits 1 on any failure |
| `nightshift-atlas.png` / `.json` | 61 entries on a 640×352 px sheet, 16 px grid, validated by `check_atlas.py` |
| `nightshift-atlas-sheet.png` | Every entry at ×4 with footprint, collision, anchor and contact shadow |
| `nightshift-landmark-states.png` | The window before, after and the changed pixels (3977 px) at ×3 |
| `nightshift-reference-room.json` | The walkable room: floor grid plus 130 placements, atlas data only |
| `nightshift-reference-room-native.png`, `-1366x768.png`, `-keyboard-inset.png` | Before state with the Engineer, Ada and Mira, native 320×192 and the ×4 view, with and without the inset |
| `nightshift-reference-room-after-native.png`, `-after-1366x768.png` | After state: window after, service door and gate open, stations lit, lamps pulsing |
| `nightshift-reference-room-route.png` | Review overlay: blocked cells, both BFS routes and the inset |
| `nightshift-readability.png` / `.json` | People at ×8 on the floor fill and in a pool with the measured contrast, and furniture crops; all numbers |

Rebuild: `python3 build_nightshift.py`. Check: `python3 check_atlas.py` (also checks `*-reference-room.json`). Both need Pillow and numpy.

## How the kit reads on a dark floor

The floor fill `#4C5865` is 2.1:1 against the ink outline, so the Orientation shapes cannot carry a silhouette. Two passes run on every piece (`nightshift_kit.py`):

1. **Shadows re-keyed.** Orientation's contact shadows use ink steps 2 and 3, which are lighter than this floor and would read as a glow. Inside each entry's `contact_shadow` rect they become floor step 0 (nearest the base) and `#202337`. `env.Room.cast` is patched the same way for the pieces drawn here. Brightest shadow pixel: luminance 0.018 against 0.095 for the fill.
2. **Lit edge.** Every upper-left silhouette pixel (transparent above or to the left) that is below 3:1 against the fill becomes muted silver (glass step 3, `#D0D4E4`, 4.9:1). Pixels already bright enough are kept. The top-left outline of a desk, partition, counter, chair, lamp post and planter is therefore a 1 px light step; ragged leaf outlines drop isolated lit pixels so they read as runs, not frost. Tiling walls light only their top edge, so tile joints show no ticks.

People get the renderer's rim by the per-pixel rules `night_rim` (`palettes/night_rim.py`, re-exported as `nightshift_kit.night_rim`): cool moonlight (`#8E96B8`, glass step 2) on the open floor; where a warm source lights someone (a lamp pool, Ada's lantern) the warm edge `#F9D79A` limited to the head and shoulders (sprite rows 0-12, `WARM_RIM_ROWS`). Props get silver, so a person and a piece of furniture never share an edge colour. Player decisions, 2026-10-02: the earlier warm `#F9D79A` people rim everywhere read as a "selected" highlight and sat near discovery gold. An upper-left person pixel is recoloured to the moonlight only if it is `#202337` or below 3:1 against the scene behind it and the rim contrasts with that background more than the pixel does: cool on the slate (2.49:1 against 2.13:1), ink kept on the body inside a pool (4.19:1 against 1.27:1). Over a pool colour, head and shoulders ink becomes warm when that reaches 2.5:1 (2.68:1 on `#B8745A`). Ada's baked lantern rim (R) is warm and baked on the lantern side of her head and shoulders only. The landmark's coworker silhouettes behind the lit window keep their warm rim (`RIM`, accent step 3), because the room behind them is lit; `PEOPLE_RIM` is the separate constant for people.

## Contents

| Group | Entries |
| --- | --- |
| Floor and route | `floor_j/h/v/p`, `floor_chip` (slate), `route_inlay`, `route_inlay_v` (silver line), `route_arrow_e`, `route_arrow_n` (warm, new) |
| Walls | `wall_n_plain` (lit cap), `wall_n_window_a/b` (silver frames), `wall_e_plain`, `wall_n_noticeboard` (new) |
| Service door | `service_door_closed/_half/_open`, state set `service_door` (Orientation's door, warm lamp-ramp frame, new stair sign) |
| Lamp | `lamp`, `lamp_off`, `lamp_glow_on`, `lamp_glow_pulse`, state set `lamp` |
| Lamp pools (new) | `pool_desk`, `pool_route`, `pool_door`, `pool_break`, `pool_ledger`, each as `_fill` and `_seam` (light layer) |
| Reused props | `desk_dead_a/b`, `desk_lit_a/b`, `chair`, `pot_plant_a` to `_d`, `sofa`, `side_table`; state sets `station_a/b` (dead to lit, with its pool) |
| Shared pieces | `shelf_1x1`, `shelf_2x1_a/b`, `partition_1x1/2x1`, `terminal_desk`, `cabinet_1x1` drawn with the Night Shift ramps |
| Night Shift pieces | `break_counter`, `ledger_desk`, `vestibule_gate_closed/_open` (state set `vestibule_gate`) |
| Landmark | `window_wall_base`, `window_panes_before/_after`, `window_figs_after_a/_b`, `window_glass`, `window_spill_after`, `window_spill_core_after`; landmark `interior_window`; state set `window_figs` |

Everything uses the 28 Night Shift ramp colours (ink shared). No violet, no marker hex. The recolour raises on any unmapped pixel.

## Lamp pools

A pool is two `light` entries with the same mask: `_fill` recolours the bare floor fill to accent step 1 (`#B8745A`), `_seam` the slab joints and chips to step 0, exactly the PALETTES_SPEC rule. They paint only on those two floor colours, so props, inlays, arrows and people are never washed. `pool_desk` and `pool_ledger` have their origin set so that placing them at the desk's cell centres them on it; the others centre on the placement point. `station_a/b` bundle desk and pool, so one state change wakes the whole island (level 18).

## Landmark: the long interior window

192×64 px (12×2 cells of wall plus the floor below it, 12×4 cells box), seven registered full-size parts and two end lamps. `window_wall_base` tiles the lit-cap wall, then a continuous glazing frame (silver head rail and left jamb, six 26 px panes, 4 px mullions, silver sill) and carries the whole run's collision (`1`×12 per row). Panes, silhouettes and glass are separate parts so a state is a list of parts.

| Change after (levels.md 18, 19) | How |
| --- | --- |
| The break room behind the glass lights warm | `window_panes_before` (dark indigo glass, empty room) swaps for `window_panes_after` (strip light, pale back wall, wainscot, lit floor, a mug shelf or a pendant lamp per pane) |
| Coworker silhouettes appear and move | `window_figs_after_a`: three ink busts (crop, bun, cap) with a warm rim (they are backlit by the lit room, so they keep it); frames `a` and `b` alternate at 700 ms as state set `window_figs` |
| Warm bands fall on the floor below | `window_spill_after` (accent 0) and `window_spill_core_after` (accent 1, only where the first is already drawn), `where_color` on the bare floor fill |
| End lamps wake | both lamps go from the steady glow to the pulse glow |

The two states differ in 3977 px in the room (`nightshift-landmark-states.png`). The reflection band of each pane with a silhouette sits on the right so it never crosses a head.

## Reference room

20×12 cells (view 320×180). Route B (the Caps route, cols 10 to 11 north, then east along rows 4 to 5 to the service door) is lit by three route pools, warm arrows, a doorway pool and silver inlay lines, and lined with lit stations and a terminal nook. Route A (the old route, cols 5 to 6) has only inlay lines, is lined with dark legacy stations and is closed by the vestibule gate. The ledger desk sits at the west end of the window wall, the break counter and noticeboard at the east end. The Engineer, Ada and Mira stand on the routes, drawn by the renderer in the ADA_SPEC order: contact shadow (floor step 0 outer, `#202337` core), sprite with the moonlight rim pass judged against the scene under it, then the paste; `light` layers last.

Programmatic review (`build_nightshift.py`, all pass):

| Check | Result |
| --- | --- |
| BFS 2×2 corridor on the collision grid, door open | route B, 14 steps from (10,10) to (17,4), 30 cells free of props |
| Door closed | no route |
| Gate | closed: route A has none, cols 4 to 7 block; open: a 2-cell corridor of 9 steps |
| Keyboard inset (view x 5 to 125, y 126.5 to 175) | landmark, door, gate, ledger desk, break counter, route B start and corner: none under it |
| Doorway brightness | open doorway 99 luma, adjacent wall 56 |
| Route against dead ends | route B 109 luma, dead ends 91, old route A 90 |
| Palette | 28 colours, all Night Shift ramp steps, no violet |
| Landmark | 5 parts differ plus the lamp state |
| Shadows | none lighter than the floor fill |
| Prop edges (atlas level) | all 32 prop and wall entries: every upper-left edge pixel at least 3:1 against the fill (or wall face) |
| Prop edges (in the room) | every free-standing prop against the floor under it: min 4.92:1 on the dark floor, min 2.50:1 inside a pool; overlays against the wall: min 8.40:1; wall top and trim: 4.92:1 |
| People | see below |
| Atlas | `ATLAS CHECK PASSED` |

## Strap and edge readability

Measured by `build_nightshift.py`, numbers in `nightshift-readability.json`, picture in `nightshift-readability.png`.

Idle S N E W, upper-left silhouette after the rim pass (moonlight `#8E96B8` on the floor; warm `#F9D79A` on head and shoulders in a pool):

| | Floor fill: edge min / coverage at 2.4:1 | Pool: head and shoulders min (warm) | Pool: body ink outline kept | Pool coverage (2.5 head, 4.0 body) | Shaded outline (fill / pool) |
| --- | --- | --- | --- | --- | --- |
| Engineer | 2.49:1 / 100% | 2.68:1 | 4.19:1 | 94% | 1.5 / 1.3 |
| Ada (baked R on head and shoulders) | 2.49:1 / 100% | 2.68:1 | 4.19:1 | 100% | 1.3 / 2.6 |
| Mira | 2.49:1 / 100% | 2.68:1 | 4.19:1 | 97% | 1.4 / 2.7 |

- **Gates (people, `build_nightshift.py`).** On the open floor every upper-left edge pixel of each person reaches at least 2.4:1 against the floor fill (the moonlight level; measured 2.49:1). Inside a pool the upper-left edge of the head and shoulders (rows 0-12) reaches at least 2.5:1 (warm rim, measured 2.68:1) and the body's ink outline (rows 13-23) is kept at at least 4.0:1 (measured 4.19:1). No edge pixel is worse than the plain outline on the floor or on the body rows in a pool (0 px). As placed in the room the same gates hold against the floor or pool actually under each pixel: floor min 2.49:1, pool head and shoulders min 2.68:1, pool body ink min 4.19:1.
- **Coverage, honestly.** Coverage is the share of the upper-left edge at or above the threshold. On the floor it is 100% for all three. In a pool the Engineer is 94% and Mira 97%: the remainder is body colours (skin and jacket steps near the terracotta pool, down to 1.64:1 and 1.87:1 for the whole body edge) that the rule cannot improve; the ink outline pixels themselves are all at 4.19:1. Ada's whole body edge is 4.19:1 because her outline is ink on every edge.
- **Earlier rules.** The first warm rim measured 5.26:1 on the floor and 2.68:1 in a pool but read as a selection highlight (decision 13); the moonlight-only version (decision 13) left pools with no warm edge at all, so decision 14 added the warm head and shoulders. The Engineer's contour-only darkest steps (hair A `#2B1E26`, jacket p `#1B4450`, down to 1.2:1) are covered by the extended rule: they become the moonlight rim on the floor.
`nightshift-rim-final.png` shows before (warm rim everywhere) and now at x4, on the slate and in a pool.
- **Strap.** Mira's coral strap and bag: lit steps `e` 2.6:1 and `f` 4.0:1 against the fill in every facing; `c` and `d` (1.2 and 1.6) are shading steps. Against the jacket it crosses it is 1.0 to 1.8:1, so it reads by hue, as in the approved renders. In a pool the strap loses against the terracotta floor (`e` 1.3:1), but the bag is closed by the ink outline (4.2:1 against a pool).
- **Furniture.** Silver edge 4.92:1 on the floor. Inside a pool it is 2.50:1, because no palette colour reaches 3:1 against `#B8745A` (white would be 2.5:1 too); the hue difference carries it.

## Director decisions (proposed)

1. **Reuse by exact hex swap, then two Night Shift passes.** Floor, walls, windows, door, lamp, desks, chair, planters, sofa and side table are the Orientation pieces recoloured; the swap raises on any unmapped pixel. The shadow re-key and the lit edge are the only additions, and they are deterministic functions of the pixels.
2. **Props get a silver edge, people a moonlight rim.** One colour per class keeps a person distinct from furniture at a glance. Silver is glass step 3 (`#D0D4E4`), the people's rim is glass step 2 (`#8E96B8`), both palette colours; in a pool the head and shoulders take the warm accent step 3 (decision 14). The warm people rim everywhere of the first version was replaced (decision 13).
3. **Contact shadows are darker than the floor.** Floor step 0 then `#202337`, the PALETTES_SPEC rule 2 applied to props and walls.
4. **In-pool contrast threshold.** Prop gates are 3:1 on the dark floor and 2.5:1 in a pool (silver 2.50). People gates are 2.4:1 on the floor (the moonlight rim), 2.5:1 for the warm head-and-shoulder rim in a pool and 4.0:1 for the kept body ink outline in a pool (decisions 13 and 14).
5. **Lamp pools are fill plus seam pairs.** A pool recolours the floor fill and the joints (PALETTES_SPEC rule 3), as two `where_color` entries; this is atlas data only, no schema change.
6. **Route language.** A lit route has pools, warm arrows and silver inlay lines; the old route has inlay only. Route B measures 109 luma against 91 for the dead ends.
7. **Doors: warm frame, silver glass.** The service door keeps Orientation's shapes with the brass ramp swapped for the lamp ramp; a stair icon replaces the folder on the sign (drawn over the recoloured plate). The doorway beyond reads as indigo-silver, not warm; the doorway pool does the warm work.
8. **Landmark is a window, not a free-standing prop.** The interior glazing of the break room is a 12-cell wall run with the base carrying collision. After state: lit room, silhouettes (frames a/b), spill bands, lamps pulse. levels.md leaves the after state open for 17; these follow levels 18 and 19.
9. **Stations are a state set.** `station_a/b` dead to lit bundle desk and pool so level 18 can wake them one at a time.
10. **Shelving and cabinet are in the kit for the ledger room** but the reference room shows only a cabinet. Boxes use warm, indigo, slate and wood clusters.
11. **Light shaft not included.** `shared_pieces.light_shaft` needs a lit colour at least as bright as the fill; no indigo step is, and the window spill covers the use.
12. **Renderer extension (applied, director decision 2026-10-02).** The people rim also lights any upper-left silhouette pixel below 3:1 against what is behind it, not only `#202337` pixels. It brings the Engineer to 100% on the floor and does not touch Ada's baked R. It now lives inside `night_rim` (the former `rim_light_ext` is gone).
13. **People rim is cool moonlight (player decision, 2026-10-02).** `#8E96B8` (glass step 2) replaces the warm `#F9D79A`, which read as a "selected" highlight and sat near discovery gold. Per-pixel rule: recolour an upper-left silhouette pixel only if it is `#202337` or below 3:1 against the scene behind it AND the rim beats the pixel's current contrast there. So the rim shows on the slate (2.49:1 against 2.13:1) and the ink outline stays in a pool (4.19:1 against 1.27:1). Ada's baked R and the landmark's window silhouettes stay warm. The single source of truth is `NIGHT_RIM` in `district_palettes.py`; the reference implementation is `night_rim` (`palettes/night_rim.py`); `PEOPLE_RIM` in `nightshift_kit.py` is the people constant, `RIM` the window one.
14. **Warm head and shoulders where a warm source lights someone (player decision, 2026-10-02).** "Cool moonlight on the open floor; where a warm source lights someone (inside a lamp pool, Ada's lantern), the warm edge is limited to the head and shoulders." `night_rim` therefore recolours head-and-shoulder rows (0 to `WARM_RIM_ROWS - 1` = 12) over a pool colour to `#F9D79A` when that reaches 2.5:1 (2.68:1), and rows 13-23 keep the ink outline. Ada's baked R follows the same limit (rows 5-10, lantern side). `check_gate1.py` gained the opt-in `HEAD_EXTRA_KEYS` read for it.

## Known gaps and notes

- Pool colour is a flat terracotta; the palette has no step between the fill and accent 1, so a pool cannot have a soft core.
- The doorway interior reads dark blue, brighter than its walls (99 against 56 luma) but not warm; a region-aware recolour would need a column mask.
- `pool_*` entries are not state sets: waking a pool means adding both entries to the layout (or using `station_a/b`).
- The reference room is one screen (20×12). The 34×20 floor of game-design is a level-data task; every piece needed for it is in the atlas.
