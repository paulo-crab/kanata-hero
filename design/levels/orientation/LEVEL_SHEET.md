# Orientation level sheet

28 x 18 cells (448 x 288 px), garden hub, camera bounds the whole map. Data: `district.json`, `map.json`, `levels/01..06`, `mira/02-morning-mail.json`, `coverage.json`. Validate with `python design/levels/validate_levels.py design/levels/orientation`. Wave 2 rebuilt the layout on the real kit (`orientation-atlas.json`) with the arrival elevator on the north wall, west end (a player decision); collision is derived from the kit footprints.

## Map at a glance

`#` blocked, `.` walkable, `G` gate cell (blocked until its level opens it), `T` terminal, `N` npc, `M` Mira, `A` artifact, `s` route stop or sign, `E` elevator panel, `g` glitch. Placements and art are in `map.json`; this view is the collision grid with interactions on top.

```
    0         1         2       
    0123456789012345678901234567
 0  #####E######################
 1  #####E#############G#TTTT###
 2  ##.......##.TTTT##.......T##
 3  ##...N...##A..............##
 4  ##.......sN..............###
 5  ##........................GG
 6  ###.......#....#..........GG
 7  ##.........#G###..........GG
 8  ##.........#G###........M###
 9  ##.........#G###...M....ss##
10  ##..#TTs...#G###...sTT#..###
11  ##....#..............#....##
12  ##.................####G####
13  ##.................####...##
14  ##........s.N.....g#.M....##
15  ##.......##....TTT.#..###.##
16  ###......#..T.T...T#.....T##
17  ############################
```

- **North wall, west to east.** Elevator module x2-4 (wall rows 0-1 plus the lit LIFT mat row y2; the car is the centre cell (3,1)), call panel x5, pinboard x6-8, window x9-10, printer alcove x11-15, twin clock x16-17, meeting-room door module x18-20 (MEET mat row y2, gate cell (19,1)), projected scheduling form x21-24, Pace sign x25-26. The window, panel, pinboard, twin clock, form and sign are wall overlays; the north wall under them stays blocked.
- **Hub in one camera view.** The garden (landmark, footprint x11-15, y7-10) sits in the middle with a 2 to 3 cell wide loop: bands x8-9 (west), x17-18 (east), y4-5 (north), y12-13 (south). In one 20 x 11 cell view you see the printer and the meeting-room door to the north, the east corridor to the Records door, the mailroom (southeast) and the reception desk (south). The elevator, the pinboard and the two desks are one short walk away.
- **Hub, short branch, task room, changed return route.** Printer branch (02): the task light steadies on the way back. Meeting-room branch (03): the glass door slides aside, the clock agrees. Left desk (04) and right desk (05): lamp and corridor stripe light, the pinboard fills and then turns human. Review table (06): east door, garden cut-through and seating nook open.
- **Level 01's first lap has no obstacles.** The lap is counter-clockwise from the arrival mat: down the west walkway (x3), right along row 12, up column 17, left along row 5. Every route cell has a free 2 x 2 block (the validator enforces it). The garden lamps block (10,6), (15,6) and (15,9) as in the kit; the route never touches them.
- **Modules are recesses, not passages.** The kit's open elevator and open meeting-room door leave only the centre cell of the middle row walkable (`111/101/000`), so each is a one-cell recess behind the mat. The turnstile (`101` open) is a one-cell lane between two pedestals; nothing on the main route passes through it.
- **Camera.** 320 x 180 view, avatar feet at screen (160,100), clamped to the map. At x4 on a 1366 x 768 screen the stage is 1280 x 720.

## Entrance-to-review route (main)

Each row is a validated BFS route; corners are listed. Gates opened by earlier levels are open for later segments (turnstile after 01, meeting-room door after 03). Walk lengths are in cells.

| Level | Leg | Cell path (corners) | Cells |
| --- | --- | --- | --- |
| orientation-01 | arrival mat, then the counter-clockwise lap (down the west walkway, right along row 12, up column 17, left along row 5), then back to Ivo at reception | (3,2) -> (3,12) -> (17,12) -> (17,5) -> (9,5) -> (9,12) -> (12,12) -> (12,13) | 50 |
| orientation-02 | reception to the badge printer by the west and north bands | (12,13) -> (12,12) -> (9,12) -> (9,5) -> (13,5) -> (13,3) | 17 |
| orientation-03 | printer along the north band to the projected scheduling form beside the meeting-room door | (13,3) -> (13,4) -> (24,4) -> (24,2) | 14 |
| orientation-04 | form wall back along the north band, down the west band to the left desk | (24,2) -> (24,4) -> (8,4) -> (8,10) -> (7,10) | 25 |
| orientation-05 | left desk to the right desk around the south band | (7,10) -> (8,10) -> (8,12) -> (17,12) -> (17,10) -> (19,10) | 16 |
| orientation-06 | right desk to the garden review table | (19,10) -> (18,10) -> (18,13) -> (15,13) -> (15,14) | 8 |

Notes: level 01's route is the guided lap, then the four desk stops (north (9,4), west (7,10), south (10,14), east (19,10) in that order), then the recall walk to Ivo at the north desk (11,4) and back to reception (12,13). Level 02 goes from reception to the printer at (13,3). Level 03's projected form is approached from (24,2) (or (22,2)), a long walk east along the north band that is the price of keeping the elevator at the west end. Levels 04 and 05 stop in front of their desks at (7,10) and (19,10). Level 06's review table is approached from (15,14); the Records door is then reached from (25,6).

## Mira route: Morning Mail (after level 02)

Mira moves into the mailroom (21,14) when level 02 completes. Start (20,14) at the counter. Checkpoints: mm.cp.west (7,10) -> mm.cp.north (9,4) -> mm.cp.east (19,10). The route is a loop around the garden with no hidden door: out through the open turnstile lane (23,12), west to the west desk, along the north band to the north desk, down the east band to the east desk, back through the lane to the mailroom. The loop is 64 cells of walking by BFS. A wrong slip is corrected at its checkpoint with no penalty. The first clean run records a baseline and grants the First Delivery patch and a mail tray; a medal needs a clean run about 5% faster at the same or better accuracy, and each cleared Mira route adds one medal to the mailroom's `mail_board`. Nothing here gates the story.

## Backtracking route

| Id | Available | Leg | Cell path (corners) | Cells |
| --- | --- | --- | --- | --- |
| `bt.north-to-reception` | orientation-06 | printer straight down the garden cut-through to reception | (12,3) -> (12,13) | 10 |
| `bt.records-to-elevator` | always | Records door back to the elevator by the north band and the west walkway | (25,6) -> (18,6) -> (18,5) -> (3,5) -> (3,2) | 26 |

The elevator always works. The Records door shows the Orientation seal it needs (RECORDS mat plus door sign) and the lit garden route back to the elevator stays visible. After level 06 the garden cut-through (column x12, y7-10, the garden landmark's `after` state) saves 6 cells between the printer and reception (16 around the garden, 10 through it). Because the loop is a rectangle, the cut-through does not shorten any route between opposite corners; it only helps north-south crossings that line up with column 12. Walks to Mira in the southeast are not shortened.

## Before and after

| Level | Before | After | Visible changes (data) |
| --- | --- | --- | --- |
| 01 The Lobby | Turnstile barred, Ivo waving on a script, two workers pacing the same loop in step beside the arrival walkway, Pace arrows around the garden. | Turnstile open to the mailroom, Ivo nodding instead of waving, garden markers gold, a folded form wandering the south lobby. | placement_state `turnstile` closed->open; npc_pose `ivo` start->post_nod; gate `g.turnstile` closed->open |
| 02 Badge Printer | The north task light pulses unsteadily, the printer spits generic names, Mira waits by the Records door, Ivo's tablet is calm. | The task light is steady, cards print in varied colors, Mira has moved into the southeast mailroom, Ivo's tablet starts flashing for the broken scheduling form. | light_state `ls.printer-steady` pulse->on; npc_pose `mira` start->mailroom; npc_pose `ivo` post_nod->tablet |
| 03 The Clock | The twin clock shows two different times, the meeting room's glass door is closed, Ivo's tablet flashes. | Both faces agree, the glass door has slid aside, Ivo's tablet is steady. | placement_state `clock_twin` unsynced->synced; placement_state `conf_door` closed->open; npc_pose `ivo` tablet->steady |
| 04 Left Desk | The cherry desk is dark, the corridor stripe beside it is unlit and the pinboard beside the elevator is empty. | The desk lamp wakes, the stripe lights and the four approved sheets join the pinboard. | placement_state `lamp_desk_left` off->on; placement_state `stripe_left_1` unlit->lit (with `stripe_left_2`, `_3`); placement_state `pinboard` empty->before; light_state `ls.desk-left-lit` off->on |
| 05 Right Desk | The mirror desk is dark; the pinboard holds the symmetrical set of sheets; Mira waits in the mailroom. | The right desk lamp is warm and its stripe is lit, the pinboard is lopsided and human with a map pointing at the review desk, Mira heads back to the mailroom. | light_state `ls.desk-right-lit` off->on; placement_state `lamp_desk_right` off->on; placement_state `pinboard` before->after; npc_pose `mira` right_desk->mailroom |
| 06 The Other Keyboard | The east Records door is closed with its seal sign, the garden is closed on every side, the two workers pace in step. | The Records door is open, the garden's after state opens a flagstone cut-through along column x12, the garden lamps pulse, coral blooms appear, the seating nook is revealed, the workers idle independently, Ivo laughs. | placement_state `records_door` closed->open; landmark_state `garden` before->after; placement_state `seating_nook` hidden->shown; npc_pose `worker_a` start->relaxed; npc_pose `ivo` steady->laugh; gate `g.garden-cutthrough` closed->open |

The kit's `orientation-quest-states.png` shows every state set of levels 01 to 06; no full-room before/after image exists yet because there is no game renderer.

## Lighting states

| Id | Description | Trigger | Changes |
| --- | --- | --- | --- |
| `ls.printer-steady` | The north task light stops pulsing and holds steady. | `o02.t.printer-steady` | `lamp_printer`->on |
| `ls.desk-left-lit` | The left desk lamp wakes and the corridor stripe beside it lights together. | `o04.t.left-lit` | `lamp_desk_left`->on, `stripe_left_1..3`->lit |
| `ls.desk-right-lit` | The right desk gets its warmer lamp (`lamp_warm`) and its corridor stripe. | `o05.t.right-lit` | `lamp_desk_right`->on, `stripe_right_1..3`->lit |
| `ls.garden-wake` | Garden lamps wake to the wider pulse glow, coral blooms appear, the cut-through opens along column x12 and the seating nook is revealed. | `o06.t.seal` | `garden`->after, `seating_nook`->shown |

The district's base light is the kit's skylit reception with warm desk lamps. Lamps use the kit state sets `lamp` and `lamp_warm` (`off`, `on`, `pulse`), the stripes `corridor_stripe` (`unlit`, `lit`), the garden the landmark states `before` and `after`.

## Keyboard-inset conflicts

Checked with the validator's camera model (avatar feet at screen (160,100), camera clamped to the map, inset x 4-147 and y 103-176 in logical pixels). **No conflicts to document:** no interaction has its avatar or its target inside the inset, and no main-route or Mira checkpoint cell puts the avatar under it. The move to the north wall helped: the arrival mat (3,2), Ivo's greeting at (5,3) and the elevator call panel (5,0) sit at the top-left of the stage, well above the inset. The first lap's west walkway ends on row 12, where the camera clamps at the south edge and the avatar's feet stay at screen y 100 (just above the inset's top edge at 103); rows 13 and below are never on a route. The review table's approach is (15,14), so its left edge is at screen x 152.

Where the inset still covers decorative floor: rows 13 to 16 west of x10 (the empty south-west room, the reception desk's west end, the south wall planters) sit behind the inset when it is open and the camera is clamped at the south-west corner. Nothing required happens there. Re-run `validate_levels.py` after moving any interaction; it reports new conflicts and requires them to be listed here by interaction id.

## Not placed (and why)

- **Full-room before/after screenshots.** Not produced (no game code).
- **`desk_folder`.** It is the Lost Folios reward in Records.
- **`desk_a_front`, `desk_b_front`.** The seated-worker occluders are for a worker behind a desk; Orientation has no seated workers.

## Decisions (and why)

1. **Counter-clockwise lap starting at the elevator.** Down, right, up, left. The arrival is now at the top-left, so the lap starts with a Down leg along the west walkway (x3) and reuses the original three legs (right along row 12, up column 17, left along row 5); it ends at (9,5) beside the north desk, where the four-stop route begins. The Pace arrows around the garden already point counter-clockwise. levels.md's order is H, J, K, L; the lesson order is J, L, K, H.
2. **Labels in levels 02 to 03 are lowercase.** Shift (F or J hold) is only introduced at the Left Desk, so no earlier scene may require a capital.
3. **Three scenes inside a walk.** The desk label (variation for B06) is triggered at the west stop inside the four-stop route. It sits after `o01-four-stops` in the scene list so the validator's order rule works.
4. **Right Command evidence is output-observed.** Right Command + K and Caps + K both emit Up Arrow, so scene `o06-rcmd-guided` cannot tell them apart; the journal records the route the player says they used. The Microsoft path is player-confirmed and never blocks the seal.
5. **Held Space and held Tab demonstrations.** The scratch field in `o03-guided-space` shows the digit a held Space produces, then clears itself. Held Tab (Homerow) is `player-confirmed` with a skip option.
6. **Local stamp shortcuts.** Level 04 and 05 stamps use in-game local shortcuts (Shift + K, Command + I, Option + K, Control + L, and the mirror set) in a safe editor; none is an OS shortcut and none is a claim about Kanata beyond the hold-then-opposite-hand rule.
7. **Elevator on the north wall, west end (player decision).** A 3x3 module at x2-4, starting at x2 because `wall_w_plain` is two cells thick. The arrival cell is the mat cell (3,2). It also keeps the keyboard inset clear. The old south-west rows 11-13 are given back to the west block.
8. **Meeting room and form on the north wall's east side.** The kit's wall modules (elevator, meeting-room door, pinboard, twin clock, form) all hang on a north wall face, so the clock cluster moved from the north-west to x16-24, east of the printer. The open door is a one-cell recess, so the old "walkable clock room" became a visible change of door and clock only.
9. **Horizontal turnstile.** The kit's 3x1 turnstile sits in the mailroom's north partition line (x22-24, lane (23,12)); the west partition is now solid. The lane is one cell wide, as the kit draws it, and is not on the main route.
10. **Garden cut-through is the garden's `after` state** (column x12, y7-10). There is no separate north-rim placement; the kit's `garden_base_open` and `garden_north_rim_open` parts carry it.
11. **Seating nook at (20,7).** A hidden 3x2 east of the garden, where the earlier east sofa and side table stood; `ls.garden-wake` shows it. It is an `art_gap` flag until the kit branch merges.
12. **The pinboard sits beside the arrival** (x6-8): it is empty on arrival, fills with sheets after level 04 and turns human after level 05, so the player sees it every time they take the elevator.
13. **Ivo's states.** `start` (wave beside the elevator mat), `post_wave`, `north`, `post_nod`, `tablet`, `steady`, `laugh`. The nod replaces the wave after the 01 route; the tablet flashes from the end of 02 until 03; the laugh is after the 06 seal. Portraits follow the cue map.
14. **Plant Tags** is in `district.json` as a district side quest (five identical planters, lowercase labels). The gate to start it is level 02 so it can be done before the review.
15. **Key introductions in level 01.** Ivo introduces Q (journal), Backtick (hint) and `?` (Layout help) right after the popup, as non-modal instruction lines in the hint grammar (`o01.s.keys`); `dialogue_done` on such a line is met when its key is observed.
