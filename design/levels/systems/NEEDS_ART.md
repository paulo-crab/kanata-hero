# Systems district: art needs

No `art_gap` remains: every prop in `map.json` is an entry in `art-direction/kit/systems-atlas.json` (as extended by `feat/art-district-integration`), so `art_gap_entries` is empty. Names in use: `elevator_closed/_half/_open` and `elevator_call_panel` (3 x 3 north-wall module at (22,0), panel at (25,0)), `routing_node_dark/_lit`, `refund_ledger_charge/_refund`, `alarm_board_blank/_labeled_1..6`, `formula_wall_dim/_clause_1..6/_lit`, `payroll_keypad_*`, `refund_sign_*`, `calc_display_*`, `bridge_span_*`, `bridge_shutter_*`, `courier_chute_*`, `folding_stool`, the four `artifact_*` overlays, the `routing_machine` landmark with `before`, `after_12`, `after_13`, `after_14`, `after`, and the reward items `mira_decor_signed_sent` and `mira_decor_relay` (not placed).

## Requests (the names exist, the art needs one more thing)

- **Bridge span orientation.** `bridge_span_retracted/_extended` is drawn for an east-west run (pit in columns 1-2 of 4, end stubs at columns 0 and 3). Both Systems bridges (the glass bridge at (14-17,6-7) and the return walkway at (9-12,6-7)) run north-south. The map places the pit on the old gate footprint and lets the stubs sit under the bridge rails and the partition. A north-south variant (a 2 x 4 piece with the same two states, pit in rows 1-2) would read correctly; otherwise the bridges need re-laying east-west.
- **Shutter pair.** `bridge_shutter_closed/_open` is a 2 x 2 piece; the bridge head is four cells wide, so two placements (`bridge_shutter`, `bridge_shutter_b`) share one state.
- **Alarm strip.** `alarm_strip_merged/_separated/_muted` is not placed: the alarm hall's north wall holds the `alarm_board` and the Pace sign. The `muted` look is reserved for the Quiet Alarm side quest, which the level schema cannot yet attach a state change to (the side quest has no trigger list).
- **Doubled signals.** The payroll wall nodes and the `payroll_keypad` show the same progress, and the refund wall ledger, `refund_sign` and `calc_display` the same flip; drop the companions if the proof render reads as too busy.

## Hal poses (drawn)

`hal_crouch_repair_e` (levels 12 and 13, `repair_hub`, `ledger_repair`), `hal_seated_stool_s` (end of 13, `ledger_seated`; the renderer draws `stool_folding` from `hal-props-atlas.json` under him) and `hal_false_panel_pull_n` (16, `panel_pull`, one-shot; on frame 2 the machine part `routing_panel_closed` swaps for `routing_panel_open`). Drawn reactions used as designed: `hal_react_puzzled_e/_s` (12 and 15), `hal_react_anxious_s` (start of 14), `hal_idle_s` (settled focus after the 14 fix).

## Reward decoration (not a placement)

Glyph Dispatch gives `mira_decor_relay`, a miniature relay for the player's desk, and Payroll Run `mira_decor_signed_sent` (both kit entries, one cell, set on a desk top); neither is placed on this map.
