# Executive Floor: art gaps

None. Every prop in `map.json` is an entry in `art-direction/kit/executive-atlas.json` (as extended by `feat/art-district-integration`); `art_gap_entries` is empty. Names in use: `elevator_closed/_half/_open` and `elevator_call_panel` (3 x 3 north-wall module at (12,0), panel at (15,0)), `branch_name_*`, `branch_route_*`, `branch_count_*`, `place_ivo/_noor/_hal/_ada/_mira`, `artifact_public_audit_copy` (on the side table at (21,8)), the Vale sets `vale_s1_*`, `vale_s2_*`, `vale_s3_*` and the reward item `desk_name_plaque` (never placed).

## Notes that are not map gaps

- **Silhouettes for named cast.** Ivo, Noor, Hal, Ada and Mira arrive as silhouettes first. Only the background workers have silhouette atlases; for the named five this is a renderer treatment of the sprite alpha (fill `#343650`, contour `#202337`, lit edge `#535971`, the bgworker silhouette ramp), no new frames needed.
- **Pace signage.** `pace_directory_repeat` (three branch boards), `pace_directory` (hub) and their `optional` epilogue variants are Pace-atlas entries placed by name. The epilogue swap to `pace_directory_optional` is declared in `district.json` `pace_signs` (`after_level`), because the Pace atlas has no state set.
- **Atrium landmark split.** The kit landmark `atrium_tree` is placed as its registered parts at one cell with gap state sets over kit entries (`atrium_inlay`, `atrium_nameplates`, `atrium_pots`), so each repair can change one feature. No new pixels. The kit's landmark states `repaired_name`, `repaired_route`, `repaired_count` and their combinations are not used because the parts already swap one by one.
- **Name plate position.** `branch_name` sits on the north wall at (4,0) in place of the two windows at x 4-7 (win_a_1, win_b_1 removed), so the Name room has a plain wall behind the plate; the count repair switches the other ten windows to daylight.
- **Glitches.** The three branch glitches are renderer-placed sprites in the district palette variants (`standard` form, `plum` chair, `dusk` stapler, behaviour `settle`); no new art. Each repaired object stays as the ordinary prop.
- `desk_a_front`/`desk_b_front` occluders are not placed: nobody sits at a desk on this floor.
