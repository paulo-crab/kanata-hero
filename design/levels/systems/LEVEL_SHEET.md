# Systems district: level sheet

38x24 cells (608x384 px). Camera 320x180 px inside `camera_bounds` (0,0,38,24). Kit `art-direction/kit/systems-atlas.json`. Data: `district.json`, `map.json`, `levels/12` to `16`, `mira/13`, `mira/16`, `coverage.json`. Validated with `validate_levels.py systems`.

## Map in one view

```
      0         1         2         3       
      01234567890123456789012345678901234567
y00   ######################################
y01   ######################################
y02   #.....####.##.##..####....##........##
y03   #.......GG..........##.@..####.##.####
y04   ##......GG..........##....##........##
y05   ##......GG..........###...GG..@.....##
y06   ##..##..##GG###GG#####....GG......####
y07   ##......##GG###GG#####....GG.......###
y08   ##......##..##............###..#....##
y09   #.......##..m#...........#############
y10   #......###..#.MMMMMM......############
y11   #.......##....MMMMMM......########.###
y12   #....##.....#.MMMMMM.....###.......###
y13   #.#..........#MMMMMM#.....##....##..##
y14   #................@..................##
y15   ##########..........................##
y16   ########.....#.....................###
y17   ##.##.....................##........##
y18   ##........................##..##....##
y19   #.......###..............###........##
y20   #.......###...........##..##........##
y21   #.......###..#..........#.##........##
y22   ##...#####.#.............####......###
y23   ######################################
```

`#` blocked in the initial state (walls, props, machine body), `.` walkable, `G` gate cell (blocked until its level opens it), `M` machine footprint, `@` spawn, `m` Mira at the chute. Rooms: alarm hall x1-7 y2-14; ledger room x1-7 y17-22; formula room x10-19 y2-5; hub x10-25 y8-22 with the gallery x22-25 y2-7 (the elevator module is on its north wall, x22-24); relay room x28-35 y2-8; payroll wing x28-35 y11-22.

Hub, short branch, task room, changed return: the **east branch** (cobalt conduit along row 14, gap y14-16) goes to the payroll wing (12); the **west branch** (mint conduit along row 14, gap y12-14) goes to the alarm hall (14), with the short **ledger branch** (gap y16-18) to the ledger room (13); the **glass bridge** (x15-16, y6-7) leads over the machine's north strip to the formula room (15) and the **return walkway** (x10-11, y6-7) comes down beside Mira's chute; the **relay room** (16) lies beyond all three, behind the relay door.

## Entrance to review route

Cells are `(x,y)`. Waypoints are the corners of the BFS path; every cell has a free 2x2 block (main path is at least two cells wide).

| Level | Segment | Path (corners) | Cells |
| --- | --- | --- | --- |
| 12 | Elevator to the payroll keypad: south down the gallery and the hub's east side, east along row 16 and through the payroll gap | (23,3) > (23,16) > (32,16) > (32,14) | 25 |
| 13 | Payroll wing to the refund ledger: back through the gap, west along row 18 and the ledger branch | (32,14) > (32,16) > (21,16) > (21,18) > (3,18) | 34 |
| 14 | Ledger room to the alarm label desk: back out the ledger branch, north along the west strip, through the alarm gap | (3,18) > (10,18) > (10,13) > (5,13) | 18 |
| 15 | Alarm hall to the formula console: through the hall and the maintenance door (open after 14) to the formula room | (5,13) > (3,13) > (3,4) > (14,4) > (14,3) | 24 |
| 16 | Formula room to the relay review console: over the glass bridge, along the north strip, up the gallery and through the relay door | (14,3) > (16,3) > (16,8) > (25,8) > (25,6) > (33,6) > (33,7) > (34,7) | 29 |

Full walk, elevator arrival (23,3) to the review console approach (34,7), by the segments above with every gate open. Gates opened by earlier levels: bridge and return walkway after 12, maintenance door after 14, relay door after 15. Before its gate opens, each locked route shows what it needs: the Pace sign at the bridge head (`bridge-sign`), the door sign plates (three conduit families, one lit per branch) and the glass beside the relay door that already shows the machine.

## Mira routes

Mira stands at the mail chute (12,9) on the hub's west strip, visible from the elevator and from the bridge landing, until level 16, then moves to the relay room (29,7). Both routes are optional, untimed for the first baseline, with an immediate correction at each checkpoint.

| Route | After | Start | Checkpoints | Loop | Reward |
| --- | --- | --- | --- | --- | --- |
| `payroll-run` (Payroll Run) | 13 | (11,9) | payroll tray (32,14), ledger desk (3,18), formula dropbox (12,3); home over the bridge and return walkway | east branch, ledger room, glass bridge and return walkway (opened by 12) | patch `signed_and_sent` |
| `glyph-dispatch` (Glyph Dispatch) | 16 | (30,8) | payroll tray (32,14), alarm card (5,13), formula wall (14,3), relay desk C (34,4) | full Systems loop: east branch, alarm hall, maintenance door, formula room, bridge, gallery, relay | patch `signal_keeper`, miniature relay decoration |

All 23 held-Space outputs are carried by Glyph Dispatch: S01 to S11 at the payroll tray (every digit and the minus), S12 to S17 at the alarm card, S18 to S23 at the formula wall; the relay typo repairs with Caps (N05, N04, N13).

## Backtracking routes

| Route | After | From to | Path (corners) |
| --- | --- | --- | --- |
| `bridge-return-loop` | systems-12 | (14,3) to (11,9) | (14,3) > (14,5) > (11,5) > (11,9) |
| `alarm-to-formula-door` | systems-14 | (4,7) to (14,3) | (4,7) > (7,7) > (7,4) > (14,4) > (14,3) |
| `relay-home` | systems-15 | (34,7) to (23,3) | (34,7) > (33,7) > (33,6) > (24,6) > (24,3) > (23,3) |

Every room has a way home: all task rooms open onto the hub, the elevator (22..24,0..2) returns to unlocked districts, and the relay room's door is a plain walk back to the hub spine. Revisit payoff: lit conduits show the way to the old branches, the bridge loop makes the north rooms reachable without crossing the hub strip, and the service walkway beside the machine (20..21,11..12) opens after the review.

## Before and after

| Level | Before | After (at least two visible changes) |
| --- | --- | --- |
| 12 Payroll IDs | payroll keypad `off`, retracted bridge and walkway, dim payroll lamp, Hal puzzled | keypad `half` after the fifth digit and `lit` after the tenth, cobalt conduit lit, bridge and return walkway extended, lamp on, Hal at crouched repair (`hal_crouch_repair_e`) |
| 13 Negative Balance | `refund_sign` red and `calc_display` charge, warning lamp pulses wide, courier chute idle, Hal crouched | `refund_sign` green and `calc_display` refund, steady warning lamp, courier chute ready, Hal seated on his stool (`hal_seated_stool_s`), ledger lamp on; Mira offers Payroll Run |
| 14 Alarm Glyphs | `alarm_strip` merged (six identical lights), shut maintenance door, Hal anxious | `alarm_strip` separated (six hues, six pictograms), open maintenance door, mint conduit lit, alarm lamp on, Hal settled |
| 15 Formula Room | `formula_wall` dark, closed bridge shutters, shut relay door | wall `half` after the third clause and `lit` after the recall, open shutters (sight line to the machine), open relay door, orange conduit lit, Hal puzzled at the score |
| 16 Crossed Wires (review) | machine `before`, dark relay conduits, Mira at the chute | machine `after` (walkway, false panel open on the Night Shift stop), three relay conduit families lit, hub lamps pulse, Mira in the relay room, Systems seal |

## Lighting states (`district.json` light_states)

`circuit-cobalt-lit` (t12-complete), `warning-steady` (t13-complete), `circuit-mint-lit` (t14-complete), `circuit-orange-sightline` (t15-complete), `all-circuits` (t16-complete). Lamps use the atlas `lamp` state set: `off` until a room's quest completes, `on` steady, `pulse` (wider glow) after the review. Safety orange stays on trim and one conduit family only.

## Keyboard-inset conflicts

Model: avatar feet at screen (160,100); the camera clamps at the map edges; inset logical x 4-147, y 103-176 (stage x 16-588, y 412-704 at x4). The validator's check (first approach cell of every interaction) finds no conflict. Cells it does not check:

- `systems-elevator`: the module is on the north wall at the head of the gallery, so the camera is top-clamped and the avatar on the mat (22..24,2) or at the arrival cell (23,3) is well above the inset. The call panel `elevator_panel` is approached from (25,2), also clear.
- Ledger room (zone-ledger), rows 19 to 22 at x 1..7: the camera is clamped at the bottom-left there, so an avatar standing in those cells is under the inset. The room's tasks are at rows 17 and 18 (desk `ledger-terminal`, approach (3..4,18), target north; `hal-ledger`, approach (3,18); `refund-slip-glitch`, approach (6,18), target north), all clear. Rows 19 to 22 hold only decoration (shelf, plant, lamp) and nothing required.
- NPC positions that change with `move_npc` are all at rows at or above their approach row, so the targets stay at or above the avatar.

Every other interaction approaches a target that is north of, or level with, the avatar, or lies where the camera scrolls (x >= 10) or is right of the inset. No required cell is under the inset.

## Data conventions and notes for developers

- `map.json` `collision` is the initial state. Gates (`gates`) open for any level whose number exceeds `opens_after`; the gate placements are state sets (`bridge_span` retracted/extended, `service_door` closed/open).
- Hal is one NPC. Each state sets pose and cell together (`npc_state`): `start` and `repair_hub` (hub), `ledger_repair` (`hal_crouch_repair_e`) and `ledger_seated` (`hal_seated_stool_s`) (ledger room), `alarm_anxious` and `alarm_settled` (alarm hall), `formula_idle` and `formula_puzzled` (formula room), `relay_idle` (relay room), `panel_pull` (`hal_false_panel_pull_n`, one-shot) and `panel_done` (machine face). Mira's states: `start` and `offering` (chute), `relay_pleased` (relay room, after 16). `visible_when` strings on NPC interactions read `npc:<id>=<state>`.
- The hub, ledger, alarm, formula and relay conversations are separate interactions bound to the same Hal (`hal-hub`, `hal-hub-13`, `hal-ledger`, `hal-alarm`, `hal-formula`, `hal-relay`); the one matching Hal's current state is live.
- Systems exit and entrance links: the false-panel entrance and exit use the world link `link.panel.systems-nightshift` (added to `world.json` by the Orientation team in the same wave; until that file merges, the validator reports it as unknown).
- Pace signs use the Pace atlas (`pace_wall_sign_2x1`, `pace_wall_sign_2x1_repeat`), listed in `district.json` `pace_signs`.
- Held-Space evidence is output-observed only: the UI says the output was observed, never that Space was held. Tap-hold Tab (Homerow) is explained and player-confirmed in the S25 lane, never scored.

## Contradictions found

- `levels.md` (Systems row) says the bridge and return walkway open in levels 12 and 15, while level 12 says the first batch extends both and level 15 says bridge shutters open. Read as: span and walkway extend at 12, shutters open at 15 (`bridge_span` and `bridge_shutter`).
- `levels.md` gives progressive machine lighting to levels 12 to 14 (nodes, warning light) but the atlas landmark has only `before` and `after`, and level ops can set only those; the data lights the surroundings and the whole machine at 16 (see NEEDS_ART.md).
- `levels.md` puts Mira's Payroll Run at the chute and Glyph Dispatch in the relay room; the data moves Mira from the chute to the relay room when level 16 completes. The brief names three Systems artifacts; `levels.md` and `world.json` also list the Original routing diagram (level 16), so all four are placed.
- `levels.md` does not say when Quiet Alarm becomes available; the data offers it after level 15 so the short expression can use `)`.

## Wave 2 reconciliation

1. **Kit names adopted.** Per-step props: `routing_node_dark/_lit` (ten wall nodes, one per digit), `refund_ledger_charge/_refund` (wall ledger), `alarm_board_blank/_labeled_1` to `_labeled_6`, `formula_wall_dim/_clause_1` to `_clause_6/_lit`, `folding_stool`, and the machine landmark states `after_12`, `after_13`, `after_14` (levels 12 to 14 now light the machine itself, then `after` at 16). Companion pieces the kit draws beside them: `payroll_keypad_off/_half/_lit` at (32,11) (half after digit 5, lit after digit 0, mirroring the nodes), `refund_sign_red/_green` at (1,16) and `calc_display_charge/_refund` at (5,16) beside the ledger, `courier_chute_idle/_ready` (replaces the cabinet stand-in; `ready` when Mira offers Payroll Run), `bridge_span_retracted/_extended`, `bridge_shutter_closed/_open` (a pair of 2 x 2 overlays across the bridge head: `bridge_shutter` and `bridge_shutter_b`), and the reward items `mira_decor_signed_sent` and `mira_decor_relay`. `alarm_strip_*` is not placed (the alarm hall's north wall has room for the board only); its `muted` state is reserved for the Quiet Alarm side quest.
2. **Formula wall.** The kit's wall is 6 x 2 cells and its set has `dim`, `clause_1` to `clause_6`, `lit` (and `dark`, `half`), so each guided clause lights its box and the recall passes to `lit`; the 8 x 2 gap is gone.
3. **Bridge spans.** The kit's 4 x 2 span is drawn for an east-west run with its pit in the middle two columns; the pit is placed on the old gate footprint ((15-16,6-7) and (10-11,6-7)), and the end stubs sit under the existing bridge rails and the partition. Both Systems bridges run north-south, so the art will need a rotated variant or a re-lay (request in NEEDS_ART.md).
4. **Elevator.** North-wall 3 x 3 module at (22,0) with its call panel at (25,0), arrival cell (23,3). Level 12 now starts at the head of the gallery and walks down the hub's east side to the payroll gap; the plant that stood at (22,2) moved to (22,5).
5. **Hal.** Poses are the drawn `hal_crouch_repair_e` (levels 12 and 13), `hal_seated_stool_s` (end of 13, with hal-props-atlas `stool_folding` under him; the placed `folding_stool` at (1,18) is hidden then) and `hal_false_panel_pull_n` (16, one-shot; on frame 2 the machine's `routing_panel_closed` part swaps for `routing_panel_open`).
6. **Glitches** (`glitches-atlas.json districts.systems`): level 12 `stapler` palette `standard` behaviour `patrol` at (29,19) (first Systems glitch, new); level 13 `form` `standard` `patrol`; level 14 `chair` `standard` `stutter` at (3,9). One per level (limit 3 per room). The level schema has no `behaviour` key, so the behaviour is in each glitch `note`.
7. **Artifacts** are the kit's `front_prop` overlays on the shelves and racks that already block their cells; none declares an `art_gap`.
