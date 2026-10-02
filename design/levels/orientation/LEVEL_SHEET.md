# Orientation level sheet

28 x 18 cells (448 x 288 px), garden hub, camera bounds the whole map. Data: `district.json`, `map.json`, `levels/01..06`, `mira/02-morning-mail.json`, `coverage.json`. Validate with `python design/levels/validate_levels.py design/levels/orientation`.

## Map at a glance

`#` blocked, `.` walkable, `G` gate cell (blocked until its level opens it), `T` terminal, `N` npc, `M` Mira, `A` artifact, `s` route stop or sign, `E` elevator panel, `g` glitch, `D` door. Placements and art are in `map.json`; this view is the collision grid with interactions on top.

```
    0         1         2       
    0123456789012345678901234567
 0  ############################
 1  ############################
 2  ###...##.##.TTTT##.......T##
 3  ##.##..#.##A.........###..##
 4  ##.....#.sN..............###
 5  ##.....#..................GG
 6  #####GG#..#....#..........GG
 7  ##TTT......#G###..........GG
 8  ##.........#G###........M###
 9  ##.........#G###...M....ss##
10  #E.#TTTs...#G###...sTTT#.###
11  ##..N#.#...........#.#....##
12  ##.................#########
13  ##.................G....####
14  ##........s.N.....gG.M....##
15  ##.......##....TTT.#..###.##
16  ###......#..T.T...T#.....T##
17  ############################
```

- **Hub in one camera view.** The garden (landmark, footprint x11-15, y7-10) sits in the middle with a 2 to 3 cell wide loop: bands x8-9 (west), x17-18 (east), y4-5 (north), y12-13 (south). In one 20 x 11 cell view you see the printer to the north, the east corridor to the Records door, the mailroom entrance (turnstile) southeast and the reception desk south. The elevator (southwest), the clock room (northwest) and the two desks are one short walk away.
- **Hub, short branch, task room, changed return route.** Printer branch (02): the task light steadies on the way back. Clock room (03): the glass door slides aside and the room becomes walkable. Left desk (04) and right desk (05): lamp and corridor stripe light, pinboard turns human. Review table (06): east door and garden cut-through open.
- **Level 01's first loop has no obstacles.** The loop is counter-clockwise (right along row 12, up column 17, left along row 5, down column 9). Every route cell has a free 2 x 2 block (the validator enforces it). The garden lamps block (10,6) and (15,6) as in the kit; the route never touches them.
- **Camera.** 320 x 180 view, avatar feet at screen (160,100), clamped to the map. At x4 on a 1366 x 768 screen the stage is 1280 x 720.

## Entrance-to-review route (main)

Each row is a validated BFS route; corners are listed. Gates opened by earlier levels are open for later segments (turnstile after 01, clock-room door after 03). Walk lengths are in cells.

| Level | Leg | Cell path (corners) | Cells |
| --- | --- | --- | --- |
| orientation-01 | elevator, then the counter-clockwise garden loop along row 12 (right, up, left, down), then to Ivo | (2,12) -> (17,12) -> (17,5) -> (9,5) -> (9,12) -> (12,12) -> (12,13) | 41 |
| orientation-02 | reception to the badge printer by the west and north bands | (12,13) -> (12,12) -> (9,12) -> (9,5) -> (13,5) -> (13,3) | 17 |
| orientation-03 | printer to the scheduling form wall at the clock room | (13,3) -> (13,4) -> (8,4) -> (8,8) -> (3,8) | 15 |
| orientation-04 | clock room to the left desk | (3,8) -> (7,8) -> (7,10) | 6 |
| orientation-05 | left desk to the right desk around the south band | (7,10) -> (8,10) -> (8,12) -> (17,12) -> (17,10) -> (19,10) | 16 |
| orientation-06 | right desk to the garden review table | (19,10) -> (18,10) -> (18,13) -> (15,13) -> (15,14) | 8 |

Notes: level 01's route is the guided loop (right, up, left, down), then the four desk stops (north (9,4), west (7,10), south (9,14), east (19,10) in that order), then the recall walk to Ivo at the north desk (11,4) and back to reception (12,13). Level 02 goes from reception to the printer at (13,3). Level 03's form wall is approached from (3,8). Levels 04 and 05 stop in front of their desks at (7,10) and (19,10). Level 06's review table is approached from (15,14); the Records door is then reached from (25,6).

## Mira route: Morning Mail (after level 02)

Mira moves into the mailroom (21,14) when level 02 completes. Start (20,14) at the counter. Checkpoints: mm.cp.west (7,10) -> mm.cp.north (9,4) -> mm.cp.east (19,10). The route is a loop around the garden with no hidden door: out through the open turnstile (19,13-14), west along the south band, up to the west desk, along the north band to the north desk, down the east band to the east desk, back to the mailroom. The loop is 48 cells of walking by BFS. A wrong slip is corrected at its checkpoint with no penalty. The first clean run records a baseline and grants the First Delivery patch and a mail tray; a medal needs a clean run about 5% faster at the same or better accuracy. Nothing here gates the story.

## Backtracking route

| Id | Available | Leg | Cell path (corners) | Cells |
| --- | --- | --- | --- | --- |
| `bt.north-to-reception` | orientation-06 | printer straight down the garden cut-through to reception | (12,3) -> (12,13) | 10 |
| `bt.records-to-elevator` | always | Records door back to the elevator by the north and west bands | (25,6) -> (18,6) -> (18,5) -> (9,5) -> (9,12) -> (2,12) | 31 |

The elevator always works. The Records door shows the Orientation seal it needs (RECORDS mat plus door sign) and the lit garden route back to the elevator stays visible. After level 06 the garden cut-through (column x12, y7-10) saves 6 cells between the printer and reception (16 around the garden, 10 through it). Because the loop is a rectangle, the cut-through does not shorten any route between opposite corners (every monotone path is already the same length); it only helps north-south crossings that line up with column 12. Walks to Mira in the southeast are not shortened (see the contradictions list in the producer report).

## Before and after

| Level | Before | After | Visible changes (data) |
| --- | --- | --- | --- |
| 01 The Lobby | Turnstile barred, Ivo waving on a script, two workers pacing the same loop in step beside the arrival, Pace arrows around the garden. | Turnstile open to the mailroom, Ivo nodding instead of waving, garden markers gold, a folded form wandering the south lobby. | placement_state `turnstile` closed->open; npc_pose `ivo` start->post_nod; gate `g.turnstile` closed->open |
| 02 Badge Printer | The north task light pulses unsteadily, the printer spits generic names, Mira waits by the Records door, Ivo's tablet is calm. | The task light is steady, cards print in varied colors, Mira has moved into the southeast mailroom, Ivo's tablet starts flashing for the broken scheduling form. | light_state `ls.printer-steady` pulse->on; npc_pose `mira` start->mailroom; npc_pose `ivo` post_nod->tablet |
| 03 The Clock | The twin clock shows two different times, the clock room's glass door is closed, Ivo's tablet flashes. | Both faces agree, the glass door has slid aside and the room is walkable, Ivo's tablet is steady. | placement_state `clock_twin` unsynced->synced; placement_state `conf_door` closed->open; npc_pose `ivo` tablet->steady |
| 04 Left Desk | The cherry desk is dark and the corridor stripe beside it is off. | The desk lamp and the corridor stripe light together; the approved sheets are done. | placement_state `lamp_desk_left` off->on; placement_state `lamp_corridor_w` off->on; light_state `ls.desk-left-lit` off->on |
| 05 Right Desk | The mirror desk is dark; the wall pinboard is symmetrical and empty; Mira waits in the mailroom. | The right desk lamp is warm, the pinboard is lopsided and human with a map pointing at the review desk, Mira heads back to the mailroom. | light_state `ls.desk-right-lit` off->on; placement_state `pinboard` before->after; npc_pose `mira` right_desk->mailroom |
| 06 The Other Keyboard | The east Records door is closed with its seal sign, the garden is closed on every side, the two workers pace in step. | The Records door is open, a flagstone cut-through opens the garden's south rim and a north rim, the garden lamps pulse and coral blooms appear, the workers idle independently, Ivo laughs. | placement_state `records_door` closed->open; landmark_state `garden` before->after; npc_pose `worker_a` start->relaxed; npc_pose `ivo` steady->laugh; gate `g.garden-cutthrough` closed->open |

The kit's `orientation-garden-states.png` shows the garden landmark before and after; no full-room before/after image exists yet because there is no game renderer. Level 06 changes the garden, the door, the workers and Ivo in one beat.

## Lighting states

| Id | Description | Trigger | Changes |
| --- | --- | --- | --- |
| `ls.printer-steady` | The north task light stops pulsing and holds steady. | `o02.t.printer-steady` | `lamp_printer`->on |
| `ls.desk-left-lit` | The left desk lamp and the adjacent corridor stripe light together. | `o04.t.left-lit` | `lamp_desk_left`->on, `lamp_corridor_w`->on |
| `ls.desk-right-lit` | The right desk gets a warmer lamp and its corridor stripe. | `o05.t.right-lit` | `lamp_desk_right`->on, `lamp_corridor_e`->on |
| `ls.garden-wake` | Garden lamps wake to the wider pulse glow, coral blooms appear and the cut-through opens (north rim too). | `o06.t.seal` | `garden`->after, `garden_north_rim`->open |

The district's base light is the kit's skylit reception with warm desk lamps. Lamps use the kit state set `lamp` (`off`, `on`, `pulse`); the garden uses the landmark states `before` and `after`.

## Keyboard-inset conflicts

Checked with the validator's camera model (avatar feet at screen (160,100), camera clamped to the map, inset x 4-147 and y 103-176 in logical pixels). **No conflicts to document:** no interaction has its avatar or its target inside the inset, and no main-route or Mira checkpoint cell puts the avatar under it. The layout was arranged for this: the elevator rows are 11-13 so the arrival cell (2,12) sits on the camera's south clamp edge (feet at screen y 100, just above the inset's top edge at 103), the first loop leg runs along row 12 for the same reason, the elevator call panel is on the wall above the elevator, the review table's approach is (15,14) so its left edge is at screen x 152, and the first plant tag is at x14.

Where the inset still covers decorative floor: rows 13-16 west of x10 (the shared-clock worker loops, the reception desk's west end, the south wall planters) sit behind the inset when it is open and the camera is clamped at the south-west corner. Nothing required happens there. Re-run `validate_levels.py` after moving any interaction; it reports new conflicts and requires them to be listed here by interaction id.

## Not placed (and why)

- **Previously hidden seating nook** (levels.md revisit payoff). The kit has `sofa`, `side_table` and a planter; place a nook in the garden's south-east bay after the cut-through opens. Left out here because the data has no "appears later" placement field and the nook adds no route or lesson.
- **Full-room before/after screenshots.** Not produced (no game code).
- **`desk_folder`.** It is the Lost Folios reward in Records.

## Decisions (and why)

1. **Counter-clockwise loop starting at the elevator.** Right, up, left, down. The player starts at the elevator and the loop is the shortest obstacle-free walk that uses all four arrows once; the west desk's Left Arrow line appears on the next stage, when the route shuffles. levels.md's order is H, J, K, L; the lesson order is L, K, H, J.
2. **Labels in levels 02 to 03 are lowercase.** Shift (F or J hold) is only introduced at the Left Desk, so no earlier scene may require a capital.
3. **Three scenes inside a walk.** The desk label (variation for B06) is triggered at the west stop inside the four-stop route. It sits after `o01-four-stops` in the scene list so the validator's order rule works.
4. **Right Command evidence is output-observed.** Right Command + K and Caps + K both emit Up Arrow, so scene `o06-rcmd-guided` cannot tell them apart; the journal records the route the player says they used. The Microsoft path is player-confirmed and never blocks the seal.
5. **Held Space and held Tab demonstrations.** The scratch field in `o03-guided-space` shows the digit a held Space produces, then clears itself. Held Tab (Homerow) is `player-confirmed` with a skip option.
6. **Local stamp shortcuts.** Level 04 and 05 stamps use in-game local shortcuts (Shift + K, Command + I, Option + K, Control + L, and the mirror set) in a safe editor; none is an OS shortcut and none is a claim about Kanata beyond the hold-then-opposite-hand rule.
7. **Elevator rows 11-13.** The brief says southwest; rows 11-13 of 18 are the south-west third, and the rows keep the arrival at the camera clamp edge so the keyboard inset never covers it.
8. **Garden cut-through is column x12.** The kit's south opening is at footprint column 1 (x12), so the through route is straight along x12 and needs one extra north-rim piece (art gap).
9. **Ivo's states.** `start` (wave at the elevator), `post_wave`, `north`, `post_nod`, `tablet`, `steady`, `laugh`. The nod replaces the wave after the 01 route; the tablet flashes from the end of 02 until 03; the laugh is after the 06 seal. Portraits follow the cue map.
10. **Plant Tags** is in `district.json` as a district side quest (five identical planters, lowercase labels). The gate to start it is level 02 so it can be done before the review.
