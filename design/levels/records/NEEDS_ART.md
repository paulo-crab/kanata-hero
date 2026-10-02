# Records: art the kit does not cover yet

Every `art_gap` placement in `map.json`, with why rearranging the Records kit cannot cover it. Names are exact and declared in `art_gap_entries`. Pieces marked state-set arrive together. Footprints below are the cells and collision the map already assumes.

| Prop (state set) | Level | Footprint | Why the kit cannot cover it |
| --- | --- | --- | --- |
| `elevator_closed` | shared | 2 x 1, collision 11 | The Records stop of the elevator: `elevator_closed`, `elevator_half`, `elevator_open` (state set `elevator`). Orientation's kit team draws the set; Records needs the same set recoloured. No elevator exists in `records-atlas.json`. |
| `elevator_half` | - | 2 x 1, collision 11 | State of the set above. |
| `elevator_open` | - | 2 x 1, collision 11 | State of the set above. |
| `door_panel_address_idle` | 07 | 1 x 1, collision 1 | The wall panel with two text windows beside the repair door. `terminal_desk` is a desk, and a door needs a wall-mounted face. |
| `cabinet_gate_misaligned` | 08 | 2 x 1, collision 11 | Gate for the margin-room doorway: `cabinet_gate_misaligned` and `cabinet_gate_aligned` (state set `cabinet_gate`). The kit's cabinets do not change state; the file wall is a six-cell piece reserved for the review loop. |
| `cabinet_gate_aligned` | - | 2 x 1, collision 00 | State of the set above. |
| `rolling_ladder_parked` | 09 | 2 x 1, collision 11 | Library ladder on the shelf rail: `rolling_ladder_parked` and `rolling_ladder_moved` (state set `rolling_ladder`). No ladder or movable doorway exists besides the file wall and doors. |
| `rolling_ladder_moved` | - | 2 x 1, collision 00 | State of the set above. |
| `cabinet_labels_offset` | 08 | 2 x 1, collision 11 | Cherry log cabinets whose label tabs sit offset and then line up: `cabinet_labels_offset` and `cabinet_labels_aligned` (state set `cabinet_labels`). The kit's `cabinet_2x1` has one static state. |
| `cabinet_labels_aligned` | - | 2 x 1, collision 11 | State of the set above. |
| `mail_chute_idle` | 07 and 11 | 1 x 1, collision 1 | Mira's wall chute with a blinking light: `mail_chute_idle` and `mail_chute_active` (state set `mail_chute`). It is her landmark and the Courier Loop's finish. |
| `mail_chute_active` | - | 1 x 1, collision 1 | State of the set above. |
| `archive_ledger_mark_rejected` | 08 | 1 x 1, collision 0 | A small overlay on the circular desk ledger: `archive_ledger_mark_rejected` and `archive_ledger_mark_accepted` (state set `ledger_mark`). The landmark only swaps its ledger together with the folders and ring at level 11, but levels.md 08 wants the stamp mark accepted earlier. Both overlays can be cropped from `archive_ledger_before` and `archive_ledger_after`; or add a landmark state that holds the after ledger with the before folders, and drop this gap. |
| `archive_ledger_mark_accepted` | - | 1 x 1, collision 0 | State of the set above. |
| `artifact_carbon_copy_a` | 08 | 1 x 1, collision 1 | Optional artifact stand, Carbon copy A. Artifacts are `artifact_<slug>` props; the kit has none for Records. |
| `artifact_margin_stamp` | 09 | 1 x 1, collision 1 | Optional artifact stand, Margin stamp. |
| `artifact_uncut_index` | 10 | 1 x 1, collision 1 | Optional artifact stand, Uncut index. |
| `artifact_noor_annotation` | 11 | 1 x 1, collision 1 | Optional artifact stand, Noor's annotation. |

State sets declared as gaps: `elevator`, `cabinet_gate`, `rolling_ladder`, `cabinet_labels`, `mail_chute`, `ledger_mark`.

## Assumptions the map makes about these pieces

- The elevator is 2 x 1 and blocks both cells, like a wall piece; the avatar steps out onto row 3.
- Cabinet gate and ladder block both doorway cells while closed and none while open (the moved ladder sits on the shelf line, in front of existing shelving).
- Artifact stands are one cell and block it; the player approaches from an adjacent cell.
- The ledger mark overlay is walkable (collision 0) and sits on the desk top at (21,10).

## Not gaps, but worth a glance

- `archive_door` is reused for the review chamber door as well as the repair door; both show the RECORDS sign. A variant without the sign for the chamber would read better.
- The kit has an east-wall piece only. The map places `wall_e_plain` as the east face of the annex, the hub and the chamber, and keeps every west-facing boundary a shelf or cabinet run, so no west-wall piece is needed.
- Pace signs and the directory use the Pace atlas (`pace_wall_sign_2x1`, `pace_directory`); the later states are `_repeat` swaps.
