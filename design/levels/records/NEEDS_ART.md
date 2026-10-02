# Records: art the kit does not cover yet

Every `art_gap` placement in `map.json`, with why rearranging the Records kit cannot cover it. Names are exact and declared in `art_gap_entries`. Pieces marked state-set arrive together. Footprints below are the cells and collision the map already assumes.

Wave 2: the kit quest props now cover `repair_door_*`, `shelf_end_light_*`, `courier_chute_idle/_ready`, `folder_rack_*`, `ledger_table_*`, `report_table_*` and `rolling_ladder_closed/_open`; the map uses those names (see `LEVEL_SHEET.md`, decision 9) and no longer declares gaps for the ladder or the chute. What is left is below, all in the hands of the kit team's wave 2.

| Prop (state set) | Level | Footprint | Why the kit cannot cover it |
| --- | --- | --- | --- |
| `elevator_closed` | shared | 3 x 3, collision `111/111/000` | The Records stop of the elevator, a north-wall module at (0,0) like Orientation's: `elevator_closed`, `elevator_half`, `elevator_open` (state set `elevator`). Rows 0-1 are wall, row 2 is the lit mat. No elevator exists in `records-atlas.json` yet; the kit team is adding the Records recolour. |
| `elevator_half` | - | 3 x 3, collision `111/111/000` | State of the set above. |
| `elevator_open` | - | 3 x 3, collision `111/101/000` | State of the set above; the centre cell of row 1 walks into the cab. |
| `elevator_call_panel` | shared | 1 x 2, collision `00/00` | Wall call panel one cell east of the elevator, placed at (3,0) with offset [4, 9]. Same prop as Orientation's, Records recolour. |
| `door_panel_address_idle` | 07 | 1 x 1, collision 1 | The wall panel with two text windows beside the repair door at (5,6), the level 07 terminal. `terminal_desk` is a desk, and a wall-mounted face is needed. (The kit's `repair_door_*` shows its own address band, but the terminal interaction needs a panel the player stands at.) |
| `cabinet_gate_misaligned` | 08 | 2 x 1, collision 11 | Gate for the margin-room doorway: `cabinet_gate_misaligned` and `cabinet_gate_aligned` (state set `cabinet_gate`). The kit's cabinets do not change state; the file wall is a six-cell piece reserved for the review loop. |
| `cabinet_gate_aligned` | - | 2 x 1, collision 00 | State of the set above. |
| `cabinet_labels_offset` | 08 | 2 x 1, collision 11 | Cherry log cabinets whose label tabs sit offset and then line up: `cabinet_labels_offset` and `cabinet_labels_aligned` (state set `cabinet_labels`). The kit's `cabinet_2x1` has one static state. The log room also holds one `folder_rack` (`log_folders`) that aligns at the same moment. |
| `cabinet_labels_aligned` | - | 2 x 1, collision 11 | State of the set above. |
| `archive_ledger_mark_rejected` | 08 | 1 x 1, collision 0 | A small overlay on the circular desk ledger: `archive_ledger_mark_rejected` and `archive_ledger_mark_accepted` (state set `ledger_mark`). The landmark only swaps its ledger together with the folders and ring at level 11, but levels.md 08 wants the stamp mark accepted earlier. Both overlays can be cropped from `archive_ledger_before` and `archive_ledger_after`; or add a landmark state that holds the after ledger with the before folders, and drop this gap. |
| `archive_ledger_mark_accepted` | - | 1 x 1, collision 0 | State of the set above. |
| `artifact_carbon_copy_a` | 08 | 1 x 1, collision 1 | Optional artifact stand, Carbon copy A. Artifacts are `artifact_<slug>` props from the generic artifact builder (`shared_pieces.artifact_prop`); the kit team is adding them to each district atlas. |
| `artifact_margin_stamp` | 09 | 1 x 1, collision 1 | Optional artifact stand, Margin stamp. |
| `artifact_uncut_index` | 10 | 1 x 1, collision 1 | Optional artifact stand, Uncut index. |
| `artifact_noor_annotation` | 11 | 1 x 1, collision 1 | Optional artifact stand, Noor's annotation. |

State sets declared as gaps: `elevator`, `cabinet_gate`, `cabinet_labels`, `ledger_mark`.

## Assumptions the map makes about these pieces

- The elevator is the Orientation 3 x 3 module: it blocks rows 0-1 of its three columns, row 2 is walkable mat, and only the open state frees the centre cell of row 1. The avatar steps out to arrival cell (1,3).
- Cabinet gate blocks both doorway cells while closed and none while open.
- Artifact stands are one cell and block it; the player approaches from an adjacent cell.
- The ledger mark overlay is walkable (collision 0) and sits on the desk top at (21,10).

## Not gaps, but worth a glance

- `archive_door` is reused for the review chamber door; it shows the RECORDS sign, which would read better without it on an inner door. The repair door now uses the kit's `repair_door_*`.
- The repair door is a front-facing 2 x 2 piece set in the east passage of the annex, with a plain `wall_e_plain` sill under it at (6,9). The kit says not to put plain wall tiles under the door: the sill sits on row 9, below the door's two rows, so the open state is unaffected.
- Shelf-end lights sit as overlays above shelf cells; the offsets follow the kit's quest-prop room and may need a pixel nudge in the proof render.
- The kit has an east-wall piece only. The map places `wall_e_plain` as the east face of the annex, the hub and the chamber, and keeps every west-facing boundary a shelf or cabinet run, so no west-wall piece is needed.
- Pace signs and the directory use the Pace atlas (`pace_wall_sign_2x1`, `pace_directory`); the later states are `_repeat` swaps.
- Mira's desk decorations `mira_decor_courier_loop` and `mira_decor_archive_folder` are kit entries used as reward items, not map placements.
