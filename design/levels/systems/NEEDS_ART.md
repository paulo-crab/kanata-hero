# Systems district: art needs

Props the Systems atlas (`art-direction/kit/systems-atlas.json`) lacks. Each is declared in `map.json` under `art_gap_entries` (and `art_gap_state_sets` where it changes state) and placed with `art_gap: true`. Everything else in the map is an atlas entry reused by name: walls, partitions, racks, shelves, cabinets, terminal desks, planters, lamps, conduits (three families, off and lit), `service_door`, `bridge_rail`, `status_board`, the `routing_machine` landmark and, since wave 2, the quest props `payroll_keypad_*`, `bridge_span_*`, `bridge_shutter_*`, `refund_sign_*`, `calc_display_*`, `alarm_strip_*`, `courier_chute_*`, `formula_wall_*` and `folding_stool` (mapping in `LEVEL_SHEET.md`, "Wave 2 reconciliation").

## Props

| Prop (exact names) | Kind and footprint | Level | Why rearranging the existing kit cannot cover it |
| --- | --- | --- | --- |
| `elevator_closed`, `elevator_half`, `elevator_open` | elevator (state set), 3x3, collision `111/111/000` (open: `111/101/000`) | all (arrival) | North-wall module at (22,0), same geometry as Orientation's `elevator_closed/_half/_open`, recoloured to the Systems ramps; the kit team is adding it to `systems-atlas.json`. No combination of walls, doors and cabinets reads as an arrival lift. |
| `elevator_call_panel` | 1x2 wall overlay, collision `00/00`, placed with offset [4, 9] | all | Call panel one cell east of the lift at (25,0) (Orientation prop name, Systems ramps). |
| `artifact_id_envelope` | 1x1 overlay on a shelf | 12 | ID envelope map prop (`artifact_<slug>`, generic artifact builder); the close-up shares the single document frame. |
| `artifact_alarm_strip` | 1x1 overlay on a rack | 14 | Alarm strip map prop. |
| `artifact_scoring_proof` | 1x1 overlay on a shelf | 15 | Scoring proof map prop. |
| `artifact_original_routing_diagram` | 1x1 overlay on a cabinet | 16 | Original routing diagram map prop (levels.md lists it for level 16; the brief named three artifacts). |

## Requests (names exist, the art needs one more thing)

- **Bridge span orientation.** `bridge_span_retracted/_extended` is drawn for an east-west run (pit in columns 1-2 of 4, end stubs at columns 0 and 3). Both Systems bridges (the glass bridge at (14-17,6-7) and the return walkway at (9-12,6-7)) run north-south. The map places the pit on the old gate footprint and lets the stubs sit under the bridge rails and the partition. A north-south variant (a 2x4 piece with the same two states, pit in rows 1-2) would read correctly; otherwise the bridges need re-laying east-west.
- **Intermediate machine states.** The `routing_machine` landmark only has `before` and `after`, and level ops can only set one of those. Levels 12 to 14 therefore light the machine's surroundings (keypad nodes, conduits, warning lamp, room lamps) and the whole machine lights at level 16. The atlas already splits the machine into registered parts (`routing_nodes`, `routing_stubs`, `routing_beacon`, `routing_ports`, `routing_core`, `routing_walkway_after`, `routing_panel_open`); landmark states `after_12` (nodes, stubs), `after_13` (+ beacon) and `after_14` (+ ports) would let the machine itself light per level with no new pixels. The kit team is adding them; level data switches to them (`routing_machine` state `after_12` etc.) once they land.
- **Formula wall and payroll keypad steps.** The kit has three steps each (`dark/half/lit`, `off/half/lit`) where the quests have six clauses and ten digits. The data maps them as documented in the level sheet; intermediate steps (`formula_wall_clause_1` to `_5`, `payroll_keypad` per digit) are not needed unless the director wants every clause or digit to light on the wall itself.
- **Shutter pair.** `bridge_shutter_closed/_open` is a 2x2 piece; the bridge head is four cells wide, so two placements (`bridge_shutter`, `bridge_shutter_b`) share one state.

## Hal poses and stool (resolved)

The cast atlas now draws the beats: `hal_crouch_repair_e` (levels 12 and 13, `repair_hub`, `ledger_repair`), `hal_seated_stool_s` (end of 13, `ledger_seated`; the renderer draws `stool_folding` from `hal-props-atlas.json` under him) and `hal_false_panel_pull_n` (16, `panel_pull`, one-shot; on frame 2 the machine part `routing_panel_closed` swaps for `routing_panel_open`). Drawn reactions used as designed: `hal_react_puzzled_e/_s` (12 and 15), `hal_react_anxious_s` (start of 14), `hal_idle_s` (settled focus after the 14 fix).

## Reward decoration (not a placement)

Glyph Dispatch gives `mira_decor_relay`, a miniature relay for the player's desk, and Payroll Run `mira_decor_signed_sent` (both kit entries, one cell, set on a desk top); neither is placed on this map.
