# Night Shift: art gaps

None. Every prop in `map.json` is an entry in `art-direction/kit/nightshift-atlas.json` (as extended by `feat/art-district-integration`), so `art_gap_entries` is empty. Names in use: `elevator_closed/_half/_open`, `elevator_call_panel` and `elevator_call_panel_executive_lit` (set `elevator_panel`: `base`, `executive_lit`), a 3 x 3 north-wall module at (26,11) with its panel at (29,11); `wall_w_plain` (six placements at (27,y)), `artifact_ada_shift_book` (on the ledger desk), `reader_pedestal_*`, `exit_sign_*`, `north_stair_*`, `carpet_cue_*`, `break_counter_dim` with the `break_room` set, `courier_chute_*`.

## Notes that are not map gaps

- **Player desk decoration** `desk_dawn_lamp` (reward of Desk for Dawn) is a kit entry used as a reward item, never placed on this map. Mira's reward item is `mira_decor_night_courier`, also not placed.
- **Pace signage.** `pace_floor_chevron_n/e` (route A), `pace_directory_repeat` and `pace_wall_sign_2x1_repeat` are Pace-atlas entries placed as-is. Their stone and blue palette is not recoloured for the dark floor; if the Pace set gets a Night Shift lit-edge pass, these placements pick it up by name.
- **Silhouettes.** The ledger and corridor figures use `bgworker_a/b` silhouette atlases (`-atlas-silhouette-lit.png`), already delivered. Ada's lantern rim is baked into her sprite.
- **Mira's patches.** Mira shows the patch state for the routes cleared so far (mira-patches atlas, states 0-5 when she offers Lights-Out, 6 after the baseline).
- **Second reader pedestal.** The kit flanks a gate with two pedestals; the map places one (`reader_vestibule` at (19,12)). A second at (24,12) would sit on the noticeboard wall.
- **Corridor light set.** The kit's `corridor_light` (lamp plus route pool) is not used; the corridor lamps stay on the `lamp` set.
- **Chair glitch.** The chair at (10,12) is drawn in `dark_steps` with the district chair recolour (renderer treatment, `glitches-atlas.json`); no new art.
- Night Shift has no `desk_a`/`desk_b`, so there are no desk occluders to place.
