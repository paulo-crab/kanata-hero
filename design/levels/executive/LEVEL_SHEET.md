# Executive Floor: level sheet

30 x 20 cells (480 x 320 px), camera bounds the whole map. Kit: `art-direction/kit/executive-atlas.json`. Level 20 Exit Interview (review and epilogue); no Mira route (she arrives for the finale). Data: `map.json`, `levels/20-exit-interview.json`, `district.json`, `coverage.json`.

## Plan (initial state; `#` blocked, `T` terminal, `S` sign, `D` door, `E` elevator, `A` artifact, `n` NPC interaction, `m` Mira, `w` coworker arrival cell)

```
   012345678901234567890123456789
 0 ##############################
 1 ##############################
 2 .###..#####S.TT..###.###..####
 3 .#..TT.##............#..TT..##
 4 .#SS....#............#....SS##
 5 .#......#..........###......##
 6 ..##..##..............##..####
 7 ...#..#..#........#....#..#.##
 8 ...#..#....#######...A.#..####
 9 ......#....#.###.#....n.m...DD
10 ...........#.###.#..........DD
11 ...##....#.#..w..##.#.......DD
12 ...........##...##..n.n.n..###
13 #........#..................##
14 ............................##
15 ..##........#..#.....w...w..EE
16 ..........###..####.#..w....EE
17 .##.#....#SS.......#.....a..EE
18 .........#.......TT#.##m....##
19 ......#..#...##....#.......###
```

- **Atrium (hub).** The tree stands in a sunken well at `(11..17, 8..12)`; Vale waits inside the rail at `(14,11)` and is approached from the steps at `(14,12)`. Four lamp posts mark the well corners. Copper floor lines (kit inlay) run with jogs and dead ends until The Route is repaired.
- **Elevator (south-east).** Arrival `(27,16)`, door on the east wall. **The final door** is on the same wall at rows 9-11, three rows above the arrival, so it shares the entry camera view (clamped south-east view: rows 9-19, columns 10-29). Closed until the third repair; daylight terrace beyond.
- **Three branches, any order.** Each is hub, short branch, task room, back to the ring:
  - **The Name** (north-west): branch `(4-5, 6-8)`, room `(2-7, 2-5)`, terminal `(4,3)`, Pace board `(2,4)`.
  - **The Route** (north-east): branch `(24-25, 6-8)`, room `(22-27, 2-5)`, terminal `(24,3)`, Pace board `(26,4)`.
  - **The Count** (south): branch `(13-14, 15-16)`, room `(10-18, 17-19)`, terminal `(17,18)`, Pace board `(10,17)`.
- **Alcove (north).** Reception console `(13,2)` for Names on the Wall, credenza `(11,2)` for the operations cards.
- **Open spaces.** The ring is at least two cells wide everywhere on the main route (validator-checked). The south-west lounge (x 0-8, y 15-19) is decor only because the keyboard inset covers that corner.

## Routes

| Route | From to | Path |
| --- | --- | --- |
| Main 20 | `(27,16)` to `(14,12)` | arrival, north to the ring, west along y 13-14, up the steps to Vale (the final door is in view the whole way) |
| Backtrack: epilogue | `(14,12)` to `(27,10)` | east along the straightened copper line to the final door approach |
| Backtrack: elevator | `(14,12)` to `(27,16)` | back to the elevator; always open |

Every branch has a clear way back to the ring (a two-cell-wide short branch). There is no Mira route: `routes.mira` is empty.

## Vale: softening by number of repairs (not by branch)

| Repairs | World pose (`poses_by_state`) | Portrait | Cue |
| --- | --- | --- | --- |
| 0 (start) | `vale_idle_s` (rigid) | neutral | the opening and every branch line before the first repair |
| 1 | `vale_react_reconsidering_s`, last frame held (shoulders drop 1 px) | concerned (evidence) | each repaired branch's evidence beats Pace's summary |
| 2 | stand-in: same pose (arms relax, weight on one leg is undrawn) | pleased | after the second repair |
| 3 | stand-in: same pose (open asymmetric stance is undrawn) | softened | after the third repair, the audit release, Names on the Wall |
| epilogue (`executive-20`) | `vale_interact_s` (releasing the audit) | softened | the epilogue audit release |

How the rules read the count with AND-only conditions: one trigger per branch (`tr-20-<branch>-repaired`), then `tr-20-count1-*` (any one), `tr-20-count2-*` (each pair) and `tr-20-count3` (all three), listed lowest first. NPC ops never move an NPC to an earlier state and a dialogue plays at most once per save, so a later trigger that is also true is harmless.

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
| Nameplates on the planter become distinct | The Name | `atrium_nameplates` before to after |
| Copper floor lines straighten into three paths | The Route | `atrium_inlay` before to after |
| Windows resolve to daylight, warm shafts, a daylight pool, soft shrubs | The Count | `win_a_*`, `win_b_*`, `shaft_*` overcast to daylight; `atrium_pots` before to after |
| Final door opens, all lamps pulse, coworkers by the door | third repair | `final_door` closed to open; lamps on to pulse |
| Pace signs become optional guidance | the final audit | Pace atlas `optional` entries (`pace_signs` with `after_level`) |

## Lighting states (`district.json`)

`ls-20-name-repaired`, `ls-20-route-repaired`, `ls-20-count-repaired`, `ls-20-door-open`, `ls-20-epilogue`. Daylight is the kit `window_a/b` and `window_light` state sets plus the landmark daylight pool; there is no extra light layer.

## Epilogue and the ending

After `tr-20-audit-done` (seal Department of Motion) the same map stays walkable in its restored state; the ending never needs a courier medal. Mira's optional final scene is `int-mira-final` (pleased), available when the epilogue is reached and every courier route has been cleared (its `requires` list the six routes). Names on the Wall and the Public audit copy are available after level 20. The operations cards stay available at the credenza.

## Keyboard-inset conflicts

Checked with the validator camera model (avatar feet at screen (160,100), clamped to the map; inset x 4-147, y 103-176 at 320 x 180) for every approach cell. **No interaction has a conflict.** The two secondary approaches that would have put a target under the inset (`(18,17)` for `int-terminal-count`, `(11,18)` for `int-pace-count`) were removed; the remaining ones keep the target in the avatar's column or to its right. The unavoidable spot is the south-west corner (x < 9, y >= 15), where the avatar would sit under the inset; it holds only decor and no route enters it.
