# Night Shift: art gaps

Props the Night Shift kit does not have yet. All are placed in `map.json` with `art_gap: true` and declared in `art_gap_entries`; the producer reconciles names with the art teams.

Wave 2: the kit quest props now cover `reader_pedestal_*`, `exit_sign_*`, `north_stair_*` (replaces the `service_door` stand-in at the ledger's west door), `carpet_cue_*`, `break_counter_dim` with the `break_room` set, and `courier_chute_idle/_ready`; the map uses those names (see `LEVEL_SHEET.md`, "Wave 2 reconciliation"). What is left:

| Name | Level | What it is | Why rearranging the kit cannot cover it |
| --- | --- | --- | --- |
| `elevator_closed` | arrival (17) | 3x3 north-wall module at (26,11), doors closed, Night Shift palette (collision `111/111/000`; rows 0-1 wall, row 2 the lit mat) | The Orientation elevator is drawn; this is its Night Shift hex swap and no Night Shift entry reads as a lift. |
| `elevator_half` | arrival | same module, half open (blocks) | state set `elevator` (closed, half, open at 120 ms per frame) |
| `elevator_open` | arrival | same module, open (collision `111/101/000`: the centre cell of row 1 walks in) | state set `elevator` |
| `elevator_call_panel` | 17-19 | 1x2 wall call panel one cell east of the module at (29,11), placed with offset [4, 9], Executive stop dark | Needed so the Executive stop can be revealed after level 19 |
| `elevator_call_panel_executive_lit` | 19 | the same panel with the Executive stop lit (state set `elevator_panel`: `base`, `executive_lit`) | the visible change that "the elevator reveals the Executive Floor" |
| `wall_w_plain` | 18-19 | 1x1 west-wall side plane (inner face of the wall between the service corridor and the hall) | `wall_e_plain` shows the wrong face from inside the corridor and cannot be mirrored: light is upper-left. Placed at `(27,y)`, six cells. |
| `artifact_ada_shift_book` | 19 | small closed book on the ledger desk | The optional artifact needs a marker prop (`artifact_<slug>`, generic artifact builder); the document close-up reuses the shared frame |

## Notes that are not map gaps

- **Player desk decoration** `desk_dawn_lamp` (reward of Desk for Dawn): a small lamp for the player's desk, drawn like the other desk decorations (mail tray, desk folder). It is never placed on this map. Mira's reward item is the kit's `mira_decor_night_courier`, also not placed.
- **Pace signage.** `pace_floor_chevron_n/e` (route A), `pace_directory_repeat` and `pace_wall_sign_2x1_repeat` are Pace-atlas entries placed as-is. Their stone and blue palette is not recoloured for the dark floor; if the Pace set gets a Night Shift lit-edge pass, these placements pick it up by name.
- **Silhouettes.** The ledger and corridor figures use `bgworker_a/b` silhouette atlases (`-atlas-silhouette-lit.png`), already delivered. Ada's lantern rim is baked into her sprite.
- **Mira's patches.** Mira shows the patch state for the routes cleared so far (mira-patches atlas, states 0-5 when she offers Lights-Out, 6 after the baseline).
- **Second reader pedestal.** The kit flanks a gate with two pedestals; the map places one (`reader_vestibule` at (19,12)). A second at (24,12) would sit on the noticeboard wall.
- **Corridor light set.** The kit's `corridor_light` (lamp plus route pool) is not used; the corridor lamps stay on the `lamp` set.
- **Chair glitch.** The chair at (10,12) is drawn in `dark_steps` with the district chair recolour (renderer treatment, `glitches-atlas.json`); no new art.
