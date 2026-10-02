# Executive Floor: art gaps

Props and poses the Executive kit does not have yet. The map props are placed with `art_gap: true` and declared in `art_gap_entries`.

| Name | Level | What it is | Why rearranging the kit cannot cover it |
| --- | --- | --- | --- |
| `elevator_closed` | arrival (20) | 2x3 east-wall elevator door, closed, Executive palette (copper frame, navy wall mass) | The kit has only `final_door_*`, which must stay distinct from the elevator so the entry reads as an arrival and the final door as the exit. |
| `elevator_half` | arrival | same door, half open (blocks) | state set `elevator` |
| `elevator_open` | arrival | same door, open (walkable) | state set `elevator` |
| `elevator_call_panel` | arrival | 1x1 wall call panel beside the door | needed for the elevator interaction marker; every stop is lit by now |
| `artifact_public_audit_copy` | 20 (after) | a bound audit copy on the side table | the optional artifact needs a marker prop; the close-up reuses the shared document frame |

## Notes that are not map gaps

- **Vale softening states 2 and 3** (ART_HANDOFF known gap): `vale_idle_s_soften_2` (arms relax away from the body, weight on one leg) and `vale_idle_s_soften_3` (loosened silhouette, open asymmetric stance), plus the walk loop for state 3. `poses_by_state` uses `vale_react_reconsidering_s` as a stand-in for states 2 and 3 because pose names must exist in the atlas.
- **Silhouettes for named cast.** Ivo, Noor, Hal, Ada and Mira arrive as silhouettes first. Only the background workers have silhouette atlases; for the named five this is a renderer treatment of the sprite alpha (fill `#343650`, contour `#202337`, lit edge `#535971`, the bgworker silhouette ramp), no new frames needed.
- **Player desk decoration** `desk_name_plaque` (reward of Names on the Wall): a small plaque for the player's desk; not placed on the map.
- **Pace signage.** `pace_directory_repeat` (three branch boards), `pace_directory` (hub) and their `optional` epilogue variants are Pace-atlas entries placed by name. The epilogue swap to `pace_directory_optional` is declared in `district.json` `pace_signs` (`after_level`), because the Pace atlas has no state set.
- **Atrium landmark split.** The kit landmark `atrium_tree` is placed as its registered parts at one cell with gap state sets over kit entries (`atrium_inlay`, `atrium_nameplates`, `atrium_pots`), so each repair can change one feature. No new pixels.
