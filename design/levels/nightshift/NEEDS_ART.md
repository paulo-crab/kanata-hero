# Night Shift: art gaps

Props the Night Shift kit does not have yet. All are placed in `map.json` with `art_gap: true` and declared in `art_gap_entries`; the producer reconciles names with the art teams.

| Name | Level | What it is | Why rearranging the kit cannot cover it |
| --- | --- | --- | --- |
| `elevator_closed` | arrival (17) | 2x3 east-wall elevator door, closed, Night Shift palette | The kit has only the `service_door` set (a stair sign). The Orientation elevator is being drawn; this is its Night Shift hex swap. |
| `elevator_half` | arrival | same door, half open (blocks) | state set `elevator` (closed, half, open at 120 ms per frame) |
| `elevator_open` | arrival | same door, open (walkable) | state set `elevator` |
| `elevator_call_panel` | 17-19 | 1x1 wall call panel beside the door, Executive stop dark | Needed so the Executive stop can be revealed after level 19 |
| `elevator_call_panel_executive_lit` | 19 | the same panel with the Executive stop lit | the visible change that "the elevator reveals the Executive Floor" |
| `wall_w_plain` | 18-19 | 1x1 west-wall side plane (inner face of the wall between the service corridor and the hall) | `wall_e_plain` shows the wrong face from inside the corridor and cannot be mirrored: light is upper-left. Placed at `(27,y)`, six cells. |
| `artifact_ada_shift_book` | 19 | small closed book on the ledger desk | The optional artifact needs a marker prop; the document close-up reuses the shared frame |

## Notes that are not map gaps

- **Player desk decoration** `desk_dawn_lamp` (reward of Desk for Dawn): a small lamp for the player's desk, drawn like the other desk decorations (mail tray, desk folder). It is never placed on this map.
- **Pace signage.** `pace_floor_chevron_n/e` (route A), `pace_directory_repeat` and `pace_wall_sign_2x1_repeat` are Pace-atlas entries placed as-is. Their stone and blue palette is not recoloured for the dark floor; if the Pace set gets a Night Shift lit-edge pass, these placements pick it up by name.
- **Silhouettes.** The ledger and corridor figures use `bgworker_a/b` silhouette atlases (`-atlas-silhouette-lit.png`), already delivered. Ada's lantern rim is baked into her sprite.
- **Mira's patches.** Mira shows the patch state for the routes cleared so far (mira-patches atlas, states 0-5 when she offers Lights-Out, 6 after the baseline).
