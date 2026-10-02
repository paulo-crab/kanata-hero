# Night Shift: level sheet

34 x 20 cells (544 x 320 px), camera bounds the whole map. Kit: `art-direction/kit/nightshift-atlas.json`. Levels 17 Lockdown Drill, 18 No Old Keys, 19 The Ledger (review). Data: `map.json`, `levels/`, `mira/`, `district.json`, `coverage.json`.

## Plan (initial state; `#` blocked, `T` terminal, `S` sign, `D` door, `E` elevator, `A` artifact, `a` Ada, `m` Mira, `w` coworker silhouette)

```
   0123456789012345678901234567890123
 0 ##################################
 1 ######################SS##########
 2 ....#.###...TT#.####T...TT##....##
 3 ..#...........TT##.#......###...##
 4 ................DD...TA...DD....##
 5 .##..SS##TT#....DD........DD.w..##
 6 .#...#.#.###...nDD..TT.w..DD...###
 7 .##..####.##...###........##....##
 8 .#...#.#.TT#..TT############....##
 9 ..........................###...##
10 .............S.........n.###..w.##
11 .########.........##....####....##
12 .#.#.#.#......##..##DDDD##SS...###
13 .########.........#TT....#......##
14 .#.#.#.#..........#....TT#....m.##
15 #########.........#......#.###..EE
16 .........#........#.........a...EE
17 .........#..####..#.###.........EE
18 .........#........#....TT.TT.TT###
19 .........#........##....#......###
```

- **Break room (hub, x 19-31, y 13-19, south-east).** The elevator is on the east wall (arrival `(31,16)`); Ada waits by the kettle `(28,16)`; consoles, the exit-card noticeboard and the Desk for Dawn station are all at x >= 23 so they clear the keyboard inset. The lower-left of the room (x 19-23, y 16-19) is decor only. Glass on the west wall (x 18).
- **Vestibule (x 19-24, y 13-14, inside the break room).** Keypad console, a leave console and a four-cell security gate in the wall line at y 12. Open state leaves a two-cell walkway (`(21,12)` and `(22,12)`); the clear back exit is the whole open break room behind it.
- **Hall (north-west and centre).** Strip along y 9-10 from the landing to both routes. **Route B (lit, Caps route):** lane x 12-13 north to the door landing x 14-15, y 4-6, with pools, arrows, inlay lines and five ticket lamps. **Route A (old):** lane x 3-4 north then east under the window; rows of identical dead desks, Pace chevrons, no pools. The long interior window (x 3-14, y 0-1) is the landmark; the recall desk sits at its east end.
- **Ledger (north-centre, x 18-25, y 2-7).** West door (north stair) and east door (service) on the kit `service_door` state set, glass partitions to the south so the silhouette and the warm lamp read from the hall.
- **Service corridor (east, x 28-31, y 2-12).** From the ledger's east door south into the break room beside Mira; lamps and silhouettes wake at 19.
- **South-west storage block (x 0-9, y 15-19).** Closed with shelves; the keyboard inset covers that corner at x4, so nothing playable is there.

## Routes (cell paths are in `map.json` `routes`)

| Route | From to | Path |
| --- | --- | --- |
| Main 17 | `(31,16)` to `(22,13)` | arrival, west across the break room along y 16, then north through the nook |
| Main 18 | `(22,13)` to `(15,5)` | through the open glass `(22,12)`, landing `(22,11)`, strip west to `(13,9)`, lane B north to `(13,5)`, east to the stair door landing `(15,5)` |
| Main 19 (review) | `(15,5)` to `(20,5)` | through the open north stair door `(16-17,5)` to the ledger terminal |
| Backtrack: corridor | `(25,5)` to `(30,14)` | ledger east door `(26-27,5)`, corridor `(28,5)` south to `(29,12)`, into the break room; never crosses the silent stations |
| Backtrack: hall | `(15,5)` to `(29,17)` | down lane B, strip east, glass, break room to the consoles and the elevator |
| Mira: Lights-Out Delivery | `(29,14)` start | checkpoints (29,17) (21,13) (14,9) (12,3) (21,5) (28,5), back to `(29,14)`; loop of 64 cells (validator info) |

Every main-route cell has a free 2x2 block (validator-checked with the vestibule glass open for 18 and the stair door open for 19). The way home is always the break room and its elevator; the exit card is on the HUD, the noticeboard and the ledger noticeboard.

## Before and after

| Level | Before | After (visible changes) |
| --- | --- | --- |
| 17 | Glass closed, hall dark | Gate `vestibule_gate` closed to open, `lamp_landing` off to on, Ada walks to the landing |
| 18 | Identical dead desks, five lamps off, doors closed | `lamp_b1..b5` wake one per scene, `station_b1` lights, `door_stair` and `door_service` open, `worker_ledger` silhouette behind the ledger glass |
| 19 | Window dark, corridor off, panel dark | `long_window` before to after (lit break room, silhouettes a/b, spill bands), all end lamps pulse, `lamp_c1..c4` pulse, `elevator_panel` shows the Executive stop, `station_dawn` lit, corridor coworkers walk |

## Lighting states (`district.json`)

`ls-17-glass-open`, `ls-18-ticket-1..5`, `ls-18-stair-open`, `ls-19-lit`. Pools follow the kit: warm pool under each lit station and the landing, route inlay and arrows on route B only. Warm head-and-shoulders rim for people inside pools, cool rim on the open floor (ART_HANDOFF Night Shift rim pass); props get silver edges. Desk and station states: `station_a/b` dead to lit (the Desk for Dawn desk lights with the level 19 break-room lighting).

## Practice and Violento rules in the data

- Every practice scene is labelled `player-confirmed` or `mixed`; held-Space use is never claimed as observed. Unconfirmed runs stay playable and the journal records them as output-observed only (`n18-t0`, `n19-t0`).
- Physical Right Command navigation is unavailable under practice; the hints use tap-hold Caps (XX rule). Physical minus and equals still pass through; the ledger asks for the layer anyway (hint copy from levels.md).
- B13 (reload) and V06 (last resort) are operations cards, never performed in a scored scene. The emergency exit is described as quitting Kanata, not a toggle.

## Trigger and condition grammar used

Conditions follow `SCHEMA.md` (`scene_success`, `dialogue_done`, `interact`, `step_start`, `reach_cell`, `player_confirm`, `trigger`). Triggers use the schema ops (`set_state`, `npc_state`, `unlock_gate`, `light_state`, `start_dialogue`, `set_flag`, `complete_level`, `grant`, `journal`). `set_flag` carries `value` (true/false) for `practice-confirmed`. NPC state keys are NPC-local (`ada`: start, landing, stair, lit); `npc_state` switches pose and cell together, and a state named `start` on a late-arriving worker means not yet present (not drawn).

## Keyboard-inset conflicts

Checked with the validator camera model (avatar feet at screen (160,100), clamped to the map; inset x 4-147, y 103-176 at 320 x 180) for every approach cell, not only the first. **No interaction has a conflict.** How it was kept clear:
- Break-room interactions are at x >= 23 and the camera clamps to the south-east corner, so targets that would sit lower-left of the avatar are never approached from the east.
- Hall terminals are approached from the north or south in the same column.
- Approach cells that would put a target under the inset were removed from `int-console-leave` (`(24,13)`), `int-ledger-final` (`(21,5)`) and `int-dawn-desk` (`(24,17)`); the remaining approaches are checked.
- Unavoidable spot: the avatar walking the south-west of the map (x < 10, y >= 15) would sit under the inset. That corner is a closed storage block, so no route enters it.
