# Records: art gaps

None. Every prop in `map.json` is an entry in `art-direction/kit/records-atlas.json` (as extended by the district integration branch `feat/art-district-integration`), so the map declares no `art_gap` and `art_gap_entries` is empty.

Names in use that the kit provides: `elevator_closed/_half/_open` and `elevator_call_panel` (a 3 x 3 north-wall module at (0,0), panel at (3,0), offset [4, 9]), `repair_door_*`, `shelf_end_light_*`, `courier_chute_idle/_ready`, `folder_rack_*`, `ledger_table_*`, `report_table_*`, `rolling_ladder_closed/_open`, `cabinet_gate_misaligned/_aligned`, `cabinet_labels_offset/_aligned`, `archive_ledger_mark_rejected/_accepted`, `door_panel_address_idle` and the four `artifact_*` overlays. The artifacts are `front_prop` overlays with no collision, so each sits on a desk, shelf or terminal that already blocks its cell.

## Notes for the renderer and the kit team

- The repair door is a front-facing 2 x 2 piece set in the east passage of the annex, with a plain `wall_e_plain` sill under it at (6,9). The kit says not to put plain wall tiles under the door: the sill is on row 9, below the door's two rows, so the open state is unaffected.
- `archive_door` is reused for the review chamber door and shows the RECORDS sign, which would read better without it on an inner door.
- Shelf-end lights sit as overlays above shelf cells; the offsets follow the kit's quest-prop room and may need a pixel nudge in the proof render.
- The kit has an east-wall piece only. The map places `wall_e_plain` as the east face of the annex, the hub and the chamber, and keeps every west-facing boundary a shelf or cabinet run, so no west-wall piece is needed.
- Pace signs and the directory use the Pace atlas (`pace_wall_sign_2x1`, `pace_directory`); the later states are `_repeat` swaps.
- Mira's desk decorations `mira_decor_courier_loop` and `mira_decor_archive_folder` are kit entries used as reward items, not map placements.
- `desk_a_front` and `desk_b_front` (front occluders for seated people) are not placed: no one sits at a Records desk in the data.
