# Executive Floor: level sheet

30 x 20 cells (480 x 320 px), camera bounds the whole map. Kit: `art-direction/kit/executive-atlas.json`. Level 20 Exit Interview (review and epilogue); no Mira route (she arrives for the finale). Data: `map.json`, `levels/20-exit-interview.json`, `district.json`, `coverage.json`.

## Plan (initial state; `#` blocked, `T` terminal, `S` sign, `D` door, `E` elevator, `A` artifact, `n` NPC interaction, `g` glitch, `m` Mira, `w` coworker arrival cell)

```
   012345678901234567890123456789
 0 ##############################
 1 ############EEEE##############
 2 .###..#####S....TT######..####
 3 .#..TT.##............#..TT..##
 4 .#SS....#............#....SS##
 5 .#.....g#..........###.g....##
 6 ..##..##..............##..####
 7 ...#..#..#........#....#..#.##
 8 ...#..#....#######...A.#..####
 9 ......#....#.###.#....n.m...DD
10 ...........#.###.#....#.#...DD
11 ...##....#.#..n..##.#.......DD
12 ...........##...##.#n#n#n..###
13 #........#..................##
14 ............................##
15 ..##........#..#.....w...w..##
16 ..........###..####.#..w....##
17 .##.#....#SS.......#.....w..##
18 .........#..g.##.TT#.##w....##
19 ......#..#...##....#.......###
```

- **Atrium (hub).** The tree stands in a sunken well at `(11..17, 8..12)`; Vale waits inside the rail at `(14,11)` and is approached from the steps at `(14,12)`. Four lamp posts mark the well corners. Copper floor lines (kit inlay) run with jogs and dead ends until The Route is repaired.
- **Elevator (north wall, centre).** A north-wall 3 x 3 module at (12-14,0-1) with its call panel at (15,0) and the lit mat on row 2; arrival `(13,3)`, looking south down the atrium onto the tree. **The final door** is on the east wall at rows 9-11 and is first seen on the walk around the ring. Closed until the third repair; daylight terrace beyond. The old east-wall doorway at (28-29,15-17) is plain wall.
- **Three branches, any order.** Each is hub, short branch, task room, back to the ring:
  - **The Name** (north-west): branch `(4-5, 6-8)`, room `(2-7, 2-5)`, terminal `(4,3)`, Pace board `(2,4)`.
  - **The Route** (north-east): branch `(24-25, 6-8)`, room `(22-27, 2-5)`, terminal `(24,3)`, Pace board `(26,4)`.
  - **The Count** (south): branch `(13-14, 15-16)`, room `(10-18, 17-19)`, terminal `(17,18)`, Pace board `(10,17)`.
- **North wall.** Reception console `(16,2)` for Names on the Wall (moved east to make room for the elevator mat), credenza `(11,2)` for the operations cards.
- **Open spaces.** The ring is at least two cells wide everywhere on the main route (validator-checked). The south-west lounge (x 0-8, y 15-19) is decor only because the keyboard inset covers that corner.

## Routes

| Route | From to | Path |
| --- | --- | --- |
| Main 20 | `(13,3)` to `(14,12)` | arrival, west along y 3, south down the west side of the atrium (x 10 and 8), east along y 14 and up the steps to Vale |
| Backtrack: epilogue | `(14,12)` to `(27,10)` | east along the straightened copper line to the final door approach |
| Backtrack: elevator | `(14,12)` to `(13,3)` | back to the elevator by the same west side; always open |

Every branch has a clear way back to the ring (a two-cell-wide short branch). There is no Mira route: `routes.mira` is empty.

## Vale: softening by number of repairs (not by branch)

| Repairs | World pose (`poses_by_state`) | Portrait | Cue |
| --- | --- | --- | --- |
| 0 (start) | `vale_idle_s` (rigid) | neutral | the opening and every branch line before the first repair |
| 1 | `vale_s1_idle_s` (shoulders drop 1 px; `vale_react_reconsidering_s` may play once as the step in) | concerned (evidence) | each repaired branch's evidence beats Pace's summary |
| 2 | `vale_s2_idle_s` (arms relax, weight on one leg) | pleased | after the second repair |
| 3 | `vale_s3_idle_s` (open asymmetric stance) | softened | after the third repair, the audit release, Names on the Wall |
| epilogue (`epilogue`) | `vale_s3_interact_s` (releasing the audit) | softened | the epilogue audit release |

How the rules read the count with AND-only conditions: one trigger per branch (`tr-20-<branch>-repaired`), then `tr-20-count1-*` (any one), `tr-20-count2-*` (each pair) and `tr-20-count3` (all three), listed lowest first. `npc_state` ops never move an NPC to an earlier state (states are ordered as listed in `poses_by_state`) and a dialogue plays at most once per save, so a later trigger that is also true is harmless.

## Coworker arrivals (defined order)

| After | Arrive (silhouette at the arrive cell) | Then sprite at gather cell | Line |
| --- | --- | --- | --- |
| first repair | Ivo `(25,15)`, Noor `(23,16)` | Ivo `(24,12)`, Noor `(22,12)` once Vale's evidence line ends | Ivo laughs (`ivo_laugh`), Noor neutral |
| second repair | Hal `(21,15)`, Ada `(25,17)` | Hal `(20,12)`, Ada `(22,9)` once Vale's pleased line ends | Hal, Ada neutral |
| third repair | Mira `(23,18)` | Mira `(24,9)` once Vale's softened line ends, as the final door opens | Mira neutral; final scene pleased |

All five are by the final door when it opens. They walk in from the elevator side; a silhouette is the renderer treatment of the sprite (fill `#343650`, contour `#202337`, lit edge `#535971`).

## Before and after

| Change | Repair that causes it | State |
| --- | --- | --- |
| Nameplates on the planter become distinct; the Name room's wall plate shows the original name | The Name | `atrium_nameplates` and `branch_name` before to after |
| Copper floor lines straighten into three paths; the detour loop in the Route room straightens | The Route | `atrium_inlay` and `branch_route` before to after |
| Windows resolve to daylight, warm shafts, a daylight pool, soft shrubs; the tally board shows the corrected total | The Count | `win_a_*`, `win_b_*`, `shaft_*` overcast to daylight; `atrium_pots` and `branch_count` before to after |
| Final door opens, all lamps pulse, coworkers by the door | third repair | `final_door` closed to open; lamps on to pulse |
| Pace signs become optional guidance | the final audit | Pace atlas `optional` entries (`pace_signs` with `after_level`) |

## Lighting states (`district.json`)

`ls-20-name-repaired`, `ls-20-route-repaired`, `ls-20-count-repaired`, `ls-20-door-open`, `ls-20-epilogue`. Daylight is the kit `window_a/b` and `window_light` state sets plus the landmark daylight pool; there is no extra light layer.

## Mixed-layer review coverage (base, Caps, held Space, home-row modifiers)

What each scene claims in the level files (the validator replays this for the owned gestures; the mixed-layer reviews are claimed here too).

| Scene | Phase | Gestures |
| --- | --- | --- |
| `n20-t1-the-name` | variation (cue) | B01-B08, N01-N08, N13-N14, N17, N19-N20 |
| `n20-t2-the-route` | variation (cue) | B09-B12, N09-N12, N15-N16, N18, N21, S10 |
| `n20-t3-the-count` | variation (cue) | B01-B02, S01-S26 |
| `n20-t4-final-audit` | recall (no cue) | B01-B12, N01-N21, S01-S26 |
| `n20-t5-operations-cards` | recall (no cue) | B13-B14, V01, V06 |

## Epilogue and the ending

After `tr-20-audit-done` (seal Department of Motion) the same map stays walkable in its restored state; the ending never needs a courier medal. Mira's optional final scene is `int-mira-final` (pleased), available when the epilogue is reached and every courier route has been cleared (its `requires` list the six routes). Names on the Wall and the Public audit copy are available after level 20. The operations cards stay available at the credenza.

## Keyboard-inset conflicts

Checked with the validator camera model (avatar feet at screen (160,100), clamped to the map; inset x 4-147, y 103-176 at 320 x 180) for every approach cell. **No interaction has a conflict.** The two secondary approaches that would have put a target under the inset (`(18,17)` for `int-terminal-count`, `(11,18)` for `int-pace-count`) were removed; the remaining ones keep the target in the avatar's column or to its right. The unavoidable spot is the south-west corner (x < 9, y >= 15), where the avatar would sit under the inset; it holds only decor and no route enters it.

## Wave 2 reconciliation

1. **Kit names adopted.** `branch_name_*` (3 x 1 wall plate at (4,0) in the Name room, replacing the two windows at x 4-7 there), `branch_route_*` (4 x 2 floor marking at (22,4) in the Route room), `branch_count_*` (2 x 1 tally board at (14,18) in the Count room) and `place_ivo/_noor/_hal/_ada/_mira` (one prop beside each coworker's gather cell: Hal (19,12), Noor (21,12), Ivo (23,12), Ada (22,10), Mira (24,10)). The atrium stays registered parts with gap state sets over kit entries; the kit landmark states `repaired_*` are not needed because each repair already swaps one part. Windows now number ten (the two over the Name plate are walls).
2. **Elevator.** North wall at (12,0), panel (15,0), arrival (13,3); the reception console, north shelf and cabinet shifted east by up to two cells. The main route walks the west side of the atrium to Vale.
3. **Vale.** `vale_s1_idle_s`, `vale_s2_idle_s`, `vale_s3_idle_s` by repair count and `vale_s3_interact_s` for the epilogue; the single stand-in is gone.
4. **Glitches** (one per branch, `glitches-atlas.json districts.executive.branches`, behaviour `settle`, one per room): The Name a `form` (palette `standard`) at (7,5), The Route a `chair` (palette `plum`) at (23,5), The Count a `stapler` (palette `dusk`) at (12,18). Each has an optional untimed repair scene and stays behind as the ordinary prop. The schema holds one glitch per level, so the level `glitch` names The Name and the other two are carried by their interactions and scenes.
