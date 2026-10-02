# Records level sheet

One page for the Records district (levels 07 to 11, Mira's Courier Loop and Lost Folios, the Misfiled Minute side quest). Data lives beside this file: `district.json`, `map.json`, `levels/`, `mira/`, `coverage.json`. Size 36 x 16 cells (two screens joined), camera bounds the whole map, cells 16 px, `[x, y]` from the top-left.

## Shape

Initial state, every gate closed. `#` blocked, `.` walkable. Letters mark interaction footprints: `T` terminal, `R` Mira-route desk or shelf, `D` gate (door, cabinets, ladder, file wall), `N` Noor, `M` Mira, `a` artifact, `E` elevator, `s` sign, `g` glitch, `P` door panel.

```
    0         1         2         3     
    012345678901234567890123456789012345
 0  ####################################
 1  ####################################
 2  ..EEss####TTRR#####TT###TT####.TT.##
 3  .....####....##.............DD....##
 4  RR....##......#a............DD....##
 5  #.....##a.....#.RR..........DDRR..##
 6  .....P#####DD#########DD######.#..##
 7  ......DD......##...........###....##
 8  ......DD....................##....##
 9  ......DD.........#.######...##a..###
10  .....####..........#####....###DD###
11  ##########R..##....##N##...###....##
12  #########....a#..#.##.###.....#...##
13  ########..g...#.................Ms##
14  ########....TT#............#......##
15  ##########TT###RR#......#RR.###...##
```

Regions: annex x 0-5, y 2-10; margin room x 8-13, y 2-5; foyer and hub x 8-27, y 7-15 (circular desk x 19-23, y 9-12); log room x 8-13, y 12-15; gallery x 15-27, y 2-5; review chamber x 30-33, y 2-9; Mira's chute pocket x 30-33, y 11-15.

- **Annex** (x 0-5, y 2-10): the entrance on the open west edge (rows 8-9), the elevator on the north wall, a Pace directory, a courier desk, and the repair door's address panel at (5,6). The repair door is the east wall of the annex at (6-7, 7-9), on the entrance route, so nobody reaches the archive without passing it.
- **Hub** (x 8-27, y 7-15): the foyer then the ring around the circular desk (landmark `archive_desk` at (19,9), clerk space (21,11)). The desk's four ring lamps and the gaps between prop rows keep every ring passage two cells wide.
- **Branches** follow hub, short branch, task room, changed return route: the log room (08) is a three-cell-deep branch south of the foyer through a two-cell gap at (11-12,11); the margin room (09) opens north of the foyer once the cabinets square up at (11-12,6); the gallery (10) opens above the hub where the ladder rolls aside at (22-23,6); the review chamber (11) is the far-east room behind the door at (28-29,3-5).
- **Loop.** The sliding file wall at (29-34,10) closes the south of the review chamber; Mira's chute pocket (x 30-33, y 11-15) is on the other side and is also open to the hub through (28-29, 12-14). The wall is visible from the pocket from the first visit and from the chamber when the player arrives, so players remember it. After level 11 it opens a two-cell corridor at (31-32,10).

## Entrance-to-review route (every gate opened by the previous level)

| Level | From | To | Waypoints | Length |
| --- | --- | --- | --- | --- |
| records-07 | (0,8) | (5,7) | (0,8) -> (5,8) -> (5,7) | 6 |
| records-08 | (5,7) | (12,13) | (5,7) -> (12,7) -> (12,13) | 13 |
| records-09 | (12,13) | (10,3) | (12,13) -> (11,13) -> (11,5) -> (10,5) -> (10,3) | 12 |
| records-10 | (10,3) | (19,3) | (10,3) -> (12,3) -> (12,7) -> (13,7) -> (13,8) -> (22,8) -> (22,5) -> (19,5) -> (19,3) | 25 |
| records-11 | (19,3) | (31,3) | (19,3) -> (31,3) | 12 |

Every route cell has a free 2 x 2 block; the validator replays this. Gate cells are blocked in the initial collision grid and listed under `gates` in `map.json`: `gate_repair_door` opens after 07, `gate_margin` after 08, `gate_ladder` after 09, `gate_review_door` after 10, `gate_file_wall` after 11.

## Mira routes

- **Courier Loop** (after 07, patch Clear Address): start (32,12) beside the chute, then (25,14), (15,14), (1,3), (33,12): east hub desk, west hub desk, annex desk past the repair door, back to the chute. A late slip joins at the review chamber desk (30,5) once level 10 opens the chamber; before level 11 the way from the review terminal back to the chute runs through the gallery and hub (28 cells), after it the file wall gives a two-cell corridor straight to the chute (10 cells), which is the backtrack route `file_wall_loop`.
- **Lost Folios** (after 11, patch Archive Loop): start (32,12), then (16,4), (12,3), (10,10), (33,12): through the opened file wall to the rolling shelf in the gallery, down through the ladder gap to the margin-room ledger desk, out to the divider cabinet by the foyer, home to the chute. It is a closed loop that needs the file wall.

## Backtracking

| Id | From | To | After | Cells |
| --- | --- | --- | --- | --- |
| `return_to_entrance` | (31,3) | (0,8) | - | 36 |
| `file_wall_loop` | (31,3) | (32,12) | records-11 | 10 |
| `hub_to_elevator` | (21,14) | (2,3) | - | 30 |

The elevator at (2,2) is reachable from the hub through the open repair door; the way home to Orientation is the open west edge from the first minute. A locked gate always shows its blocker in place (door, parked ladder, crooked cabinets, file wall) and a visible route back.

## Before and after (levels.md 07 to 11)

| After level | Visible changes |
| --- | --- |
| 07 | Repair door `repair_door` closed to open; Noor steps out to (21,13); shelf-end and chute lamps wake; Mira appears beside the chute. |
| 08 | Log cabinets `log_cabinet` offset to aligned labels; ledger mark `archive_ledger_mark` rejected to accepted; margin-room cabinets `margin_gate` misaligned to aligned; Noor stamps in the margin room. |
| 09 | Ledger lamps off to on; ladder `ladder_gate` parked to moved; Noor moves to the gallery. |
| 10 | Review chamber door closed to open; upper lamp on; Noor waits in the chamber. |
| 11 | `archive_desk` landmark before to after (coral, sea-blue and linen folders, ring pool, four pulsing ring lamps, stamped ledger); `file_wall` closed to open; chute active; Noor fully upright at the hub; Systems elevator stop opens. |

Noor's posture ladder uses the three-frame `posture_upright` set once per cabinet step: stooped (frame 0) at the start and through 07, one step less stooped after 09, base idle after 11.

## Lighting states

| Id | When | Changes |
| --- | --- | --- |
| `shelf_ends_awake` | 07 | five lamps off to on |
| `margin_lamps_lit` | 09 | two ledger lamps off to on, plus the window beam already falling on the table |
| `upper_desk_lit` | 10 | upper desk lamp off to on |
| `ring_pool_lit` | 11 | landmark `archive_desk` after: ring glow on the floor, four ring lamps pulse |

Gold is a UI marker colour and never appears in art, so shelf-end and ring lights use the lamp and the linen glow steps (kit decisions 2 and 10).

## Keyboard-inset conflicts

The keyboard inset covers logical x 4-147, y 103-176 at x4 in the bottom-left. The camera follows the avatar (feet at screen 160,100) and clamps at the map edge, so only the bottom-left corner of the map can put the avatar or target in the inset.

- The entrance `from_orientation` (0,8) and the annex route are above row 11, so the camera is not clamped to the bottom-left there; no required interaction is placed in the bottom-left 9 x 5 cells of the map. Log-room cells at x 8-9 and y 12-15 are dead space: the terminals, the cabinet recall and the artifact are at x 10 or more.
- Interactions whose first approach cell or target falls inside the inset (documented, not required for the main route unless noted):
  - `repair_door`: approach (5,8), target overlaps the inset; avatar feet at screen 88,100. The door is passive (it opens when the level completes and the player never needs to read it), the lowest row of the door sprite sits behind the inset when the avatar stands at the approach cell, and the address panel `door_panel` at (5,6), where the level is actually played, is clear.

Each task scene is a DOM overlay and the diagram sits in the inset, so the world only has to keep the avatar and the target clear; the annex and foyer routes do.

## Decisions

1. **Size and shape.** 36 x 16 (576 cells), a little over two 20 x 12 screens, so the camera needs one horizontal scroll and the gallery sits directly above the hub as levels.md asks.
2. **One door per progress step.** The kit has two gate pieces (`archive_door`, `file_wall`). The repair door (07) and the review chamber door (10) reuse `archive_door`, the file wall closes the loop (11), and the cabinet gate (08) and ladder (09) are art gaps with open and closed states.
3. **Collision is the initial state.** Gates start blocked and are listed with the level that opens them; the validator opens them for later levels.
4. **Noor follows the work.** She stays at the hub for 07 and 08, stamps in the margin room, waits in the gallery for 10 and in the chamber for 11, and returns upright to the hub, so her unimpressed line is delivered where Pace's claim is. Her single hub conversation interaction exists for the start position only.
5. **Landmark.** The ring desk is placed once with the kit's two states, before and after. Level 08's accepted mark is a small overlay gap that crops from the kit's ledger parts, so the landmark after state still means level 11 only.
6. **Hint lines** are copied from levels.md in the three-part hint grammar; every hint line uses the neutral portrait. The portrait key for Noor's signature is `unimpressed` (key `noor_unimpressed`).
7. **Control + D.** Caps+X sends Control + D, which the panel's editor treats as forward delete; the feedback line names Control + D as the observed output.
8. **N21 coverage.** levels.md lists N21 under both 06 and 11; Records 11 carries all three phases for it so coverage holds either way.

