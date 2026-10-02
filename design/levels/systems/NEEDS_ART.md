# Systems district: art needs

Props the Systems atlas (`art-direction/kit/systems-atlas.json`) lacks. Each is declared in `map.json` under `art_gap_entries` (and `art_gap_state_sets` where it changes state) and placed with `art_gap: true`. Everything else in the map is an atlas entry reused by name: walls, partitions, racks, shelves, cabinets, terminal desks, planters, lamps, conduits (three families, off and lit), `service_door`, `bridge_rail`, `status_board`, and the `routing_machine` landmark.

## Props

| Prop (exact names) | Kind and footprint | Level | Why rearranging the existing kit cannot cover it |
| --- | --- | --- | --- |
| `elevator_closed`, `elevator_half`, `elevator_open` | elevator (state set), 3x1 blocked | all (arrival) | The Systems atlas has no elevator. Same prop as Orientation's `elevator_closed/_half/_open` recoloured to the Systems ramps; no combination of walls, doors and cabinets reads as an arrival lift. |
| `elevator_call_panel` | 1x1 blocked, rear_wall | all | Call panel beside the lift (Orientation prop name, Systems ramps). |
| `routing_node_dark`, `routing_node_lit` | routing_node (state set), 1x1 wall overlay, placed ten times | 12 | Ten individually lit nodes on the payroll wing wall, one per digit. The landmark's `routing_nodes_before/_after` can only switch all ten at once; the quest needs one lamp per correct digit. |
| `refund_ledger_charge`, `refund_ledger_refund` | refund_ledger (state set), 2x1 wall overlay | 13 | Inset calculator and ledger display with orange sign markers: charge in orange, refund in green. No atlas entry shows reversible text or a green/orange state. |
| `alarm_board_blank`, `alarm_board_labeled_1`, `alarm_board_labeled_2`, `alarm_board_labeled_3`, `alarm_board_labeled_4`, `alarm_board_labeled_5`, `alarm_board_labeled_6` | alarm_board (state set), 3x2 wall overlay | 14 | Six pictograms and six hues that return one at a time. The kit's `status_board` has six lights in only the three family colours and no pictogram slots or label states. |
| `formula_wall_dim`, `formula_wall_clause_1`, `formula_wall_clause_2`, `formula_wall_clause_3`, `formula_wall_clause_4`, `formula_wall_clause_5`, `formula_wall_clause_6`, `formula_wall_lit` | formula_wall (state set), 8x2 wall overlay | 15 | The large formula wall whose connected clauses light as each becomes valid. Nothing in the kit carries text clauses or a progressive lit state. |
| `bridge_span_retracted`, `bridge_span_extended` | bridge_span (state set), 2x2, retracted blocks, extended is walkable; used twice | 12 | The glass bridge and the return walkway extend after the first payroll batch. Existing `bridge_deck` and `bridge_rail` tiles cover the extended look (4 deck tiles); the retracted shutter plates and the state switch are new. |
| `bridge_shutter_closed`, `bridge_shutter_open` | bridge_shutter (state set), 4x1 overlay | 15 | Louvred shutters across the bridge head that open for a clean sight line to the machine. No atlas piece hides or reveals a view. |
| `folding_stool_folded`, `folding_stool_open` | folding_stool (state set), 1x1 | 13 | Hal's folding stool, folded then open for him to sit on (hal.md: a separate prop sprite). |
| `artifact_id_envelope` | 1x1 overlay on a shelf | 12 | ID envelope map prop; the close-up shares the single document frame. |
| `artifact_alarm_strip` | 1x1 overlay on a rack | 14 | Alarm strip map prop. |
| `artifact_scoring_proof` | 1x1 overlay on a shelf | 15 | Scoring proof map prop. |
| `artifact_original_routing_diagram` | 1x1 overlay on a cabinet | 16 | Original routing diagram map prop (levels.md lists it for level 16; the brief named three artifacts). |

## Hal poses (cast atlas, not map props)

`cast/hal-atlas.json` has idle, walk, interact and the puzzled and anxious reactions. These beats are not drawn (HAL_SPEC scope note), so the data names a drawn proxy animation and the producer should replace it when the poses land:

| Beat | Data state | Proxy animation now | Wanted |
| --- | --- | --- | --- |
| Crouched repair at the machine and in the ledger room (levels 12, 13) | `systems-12` | `hal_interact_e` | `hal_crouch_repair_e` (and s/n/w) |
| Seated on the stool at the end of 13 | `systems-13` | `hal_idle_s` | `hal_seated_stool_s` |
| Pulls down the false panel (16) | `panel_pull` | `hal_interact_n` | `hal_pull_panel_n`, one-shot |

Drawn poses used as designed: `hal_react_puzzled_e/_s` (12 and 15), `hal_react_anxious_s` (start of 14), `hal_idle_s` (settled focus after the 14 fix).

## Intermediate landmark states (request, not a gap)

The `routing_machine` landmark only has `before` and `after`, and level ops can only set one of those. Levels 12 to 14 therefore light the machine's surroundings (node lamps, conduits, warning lamp, room lamps) and the whole machine lights at level 16. The atlas already splits the machine into registered parts (`routing_nodes`, `routing_stubs`, `routing_beacon`, `routing_ports`, `routing_core`, `routing_walkway_after`, `routing_panel_open`); defining landmark states `after_12` (nodes, stubs), `after_13` (+ beacon) and `after_14` (+ ports) from those parts would let the machine itself light per level with no new pixels.

## Reward decoration (not a placement)

Glyph Dispatch gives a **miniature relay decoration** for the player's desk (levels.md). It is a desk decoration, not a map prop, so it has no `art_gap` entry; it needs a small desk sprite alongside the other courier desk items (mail tray, desk folder).
