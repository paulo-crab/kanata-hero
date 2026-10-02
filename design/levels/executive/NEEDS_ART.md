# Executive Floor: art gaps

Props and poses the Executive kit does not have yet. The map props are placed with `art_gap: true` and declared in `art_gap_entries`.

Wave 2: the kit quest props now cover `branch_name_*`, `branch_route_*`, `branch_count_*` and `place_*`, and the cast atlas draws Vale's states (`vale_s1_*`, `vale_s2_*`, `vale_s3_*`); the map and the NPC data use those names (see `LEVEL_SHEET.md`, "Wave 2 reconciliation"). What is left:

| Name | Level | What it is | Why rearranging the kit cannot cover it |
| --- | --- | --- | --- |
| `elevator_closed` | arrival (20) | 3x3 north-wall module at (12,0), closed, Executive palette (copper frame, navy wall mass); collision `111/111/000`, rows 0-1 wall, row 2 the lit mat | The kit has only `final_door_*`, which must stay distinct from the elevator so the entry reads as an arrival and the final door as the exit. |
| `elevator_half` | arrival | same module, half open (blocks) | state set `elevator` |
| `elevator_open` | arrival | same module, open (collision `111/101/000`: the centre cell of row 1 walks in) | state set `elevator` |
| `elevator_call_panel` | arrival | 1x2 wall call panel one cell east of the module at (15,0), placed with offset [4, 9] | needed for the elevator interaction marker; every stop is lit by now |
| `artifact_public_audit_copy` | 20 (after) | a bound audit copy on the side table | the optional artifact needs a marker prop (`artifact_<slug>`, generic artifact builder); the close-up reuses the shared document frame |

## Notes that are not map gaps

- **Silhouettes for named cast.** Ivo, Noor, Hal, Ada and Mira arrive as silhouettes first. Only the background workers have silhouette atlases; for the named five this is a renderer treatment of the sprite alpha (fill `#343650`, contour `#202337`, lit edge `#535971`, the bgworker silhouette ramp), no new frames needed.
- **Player desk decoration** `desk_name_plaque` (reward of Names on the Wall): a small plaque for the player's desk; not placed on the map.
- **Pace signage.** `pace_directory_repeat` (three branch boards), `pace_directory` (hub) and their `optional` epilogue variants are Pace-atlas entries placed by name. The epilogue swap to `pace_directory_optional` is declared in `district.json` `pace_signs` (`after_level`), because the Pace atlas has no state set.
- **Atrium landmark split.** The kit landmark `atrium_tree` is placed as its registered parts at one cell with gap state sets over kit entries (`atrium_inlay`, `atrium_nameplates`, `atrium_pots`), so each repair can change one feature. No new pixels. The kit's landmark states `repaired_name`, `repaired_route`, `repaired_count` and their combinations are not used because the parts already swap one by one.
- **Name plate position.** `branch_name` sits on the north wall at (4,0) in place of the two windows at x 4-7 (win_a_1, win_b_1 removed), so the Name room has a plain wall behind the plate; the count repair switches the other ten windows to daylight.
- **Glitches.** The three branch glitches are renderer-placed sprites in the district palette variants (`standard` form, `plum` chair, `dusk` stapler, behaviour `settle`); no new art. Each repaired object stays as the ordinary prop.
