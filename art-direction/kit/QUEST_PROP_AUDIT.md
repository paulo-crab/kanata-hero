# Quest prop audit: Records, Systems, Night Shift, Executive

**Status:** written 2026-10-02 by the district-kits team (branch `feat/art-district-quest-props`). Sources: `levels.md` levels 07 to 20 ("Art and state" lines, the District table, the Side quests table, Mira's routes table), the four district kit specs, and the four atlases as they were before this change.

**How to read it.** Each row is one prop or visible state that `levels.md` names. *In atlas now* names the existing entry when one already reads as the thing. *Class* is one of:

- **Rearrangement**: no new art. The level designer places existing entries (a different count, position or state).
- **New**: a new atlas entry (or a pair or triple of state entries). The exact names are in the last column and are the names level data should use.
- **Other team**: not drawn in the district atlases (cast sprites, the DOM UI, the generic artifact builder or the elevator, which the Orientation team owns, or the Pace atlas).

The levels brief says a named prop is normally a rearrangement or small variant of the kit. New art was added only where rearrangement cannot read as the thing (a door that shows an address, a sign that flips, a bridge that is absent and then present).

State sets follow `<thing>_<state>` (for example `refund_sign_red`, `refund_sign_green`) and a state set (`animations` entry) is named after the thing without the state. Every new entry has footprint, collision, layer, anchor, `y_sort` (props), contact shadow (props) and, where the quest changes a visible state, a state set. Specs: see the "Quest props" section of each `*_KIT_SPEC.md`. Proof renders: `<district>-quest-props-before-*.png` and `-after-*.png` (native and 1366x768).

## Records (levels 07 to 11, Mira after 07 and 11)

| # | Level | Named in levels.md | In atlas now | Class | New entries or how to build it |
| --- | --- | --- | --- | --- | --- |
| R1 | 07 | "High archive door with two clear text windows, visible cursor and deletion side" (the repair door on the entrance route) | `archive_door_*` is the east-wall sliding door with a RECORDS sign, no text windows | New | `repair_door_closed`, `repair_door_half`, `repair_door_open`; state set `repair_door` (2x2 wall door: two text windows, cursor, deletion side) |
| R2 | 07 | "The door retracts" | `archive_door` state set (closed, half, open) | Rearrangement | `repair_door` plays closed, half, open the same way |
| R3 | 07 | "shelf-end lights change to gold" | `lamp` (floor lamp) cannot sit on a shelf end; gold is a UI marker hex and never appears in world art | New | `shelf_end_light_off`, `shelf_end_light_on`; state set `shelf_end_light` (linen and peach light, not gold) |
| R4 | 07 | "Mira appears beside the chute" | none | New | `courier_chute_idle`, `courier_chute_ready`; state set `courier_chute` (ready = lit indicator and a letter in the slot) |
| R5 | 07 | "Noor steps out from behind the desk" | `archive_desk_*` has the one-cell opening | Other team (Noor's sprite and pose) | none |
| R6 | 08 | "Long cherry cabinets" | `cabinet_2x1`, `cabinet_1x1` | Rearrangement | run several `cabinet_2x1` side by side |
| R7 | 08 | "sea-blue folders with offset labels ... Repaired folders align" | `archive_folders_before/after` is the desk's colour state, not an alignment state | New | `folder_rack_drift`, `folder_rack_aligned`; state set `folder_rack` |
| R8 | 08 | "ceiling ring reflected on polished floor" | `archive_ring_inlay`, `archive_ring_glow_after` | Rearrangement | landmark `archive_desk` |
| R9 | 08 | "a left branch opens" | `file_wall` state set | Rearrangement | a second `file_wall` instance across the left branch |
| R10 | 08 | "Noor's stamp mark changes from rejected to accepted" | `archive_ledger_before/after` | Rearrangement | landmark `archive_desk` |
| R11 | 08 | Optional artifact Carbon copy A | none | Other team (generic artifact builder, wave 2) | none |
| R12 | 09 | "Two-sided ledger table" with "both ends lit" when the margins are correct | `desk_a` is a one-person desk | New | `ledger_table_before`, `ledger_table_after`; state set `ledger_table` (before: sign-offs in the middle, ends dark; after: sign-offs at both margins, both end lamps lit) |
| R13 | 09 | "a thin beam of daylight across its full width" | `light_shaft` | Rearrangement | two `light_shaft` placements side by side over the table |
| R14 | 09 | "a rolling ladder moves to reveal the upper gallery" | none | New | `rolling_ladder_closed`, `rolling_ladder_open`; state set `rolling_ladder` (closed blocks the gallery stair, open leaves a two-cell way) |
| R15 | 09 | Optional artifact Margin stamp | none | Other team | none |
| R16 | 10 | "stacked binders" in a tall gallery | `shelf_*` (file boxes in runs) | Rearrangement | stack `shelf_2x1_a/_b` runs |
| R17 | 10 | "an elevator-like rolling shelf" | `file_wall` rail, `rolling_ladder` rail run | Rearrangement | `rolling_ladder_*` (rail-mounted shelving) is the rolling shelf; the gallery stair is its opening |
| R18 | 10 | "high window shafts" | `wall_n_window_a/b`, `light_shaft` | Rearrangement | place as in the Records reference room |
| R19 | 10 | "Correct citations bring light to the upper desk" | `lamp` state set (off, on, pulse), `desk_a` | Rearrangement | `desk_a` with a `lamp` set switching off to on |
| R20 | 10 | "open the review chamber" | `archive_door` state set | Rearrangement | `archive_door` at the chamber |
| R21 | 10 | "Noor places the original report beside the summary" | `desk_a` paper | New | `report_table_before`, `report_table_after`; state set `report_table` (one grey summary, then summary plus the original) |
| R22 | 10 | Optional artifact Uncut index | none | Other team | none |
| R23 | 11 | "Circular review desk beneath the luminous ring" | landmark `archive_desk` | In atlas | none |
| R24 | 11 | selected text "in a spacious editor panel"; Records seal | none | Other team (DOM UI) | none |
| R25 | 11 | "Shelves slide apart to expose a corridor back to Mira" | `file_wall` | In atlas | none |
| R26 | 11 | "folder labels regain coral and sea-blue variation" | `archive_folders_after` | In atlas | none |
| R27 | 11 | Optional artifact Noor's annotation | none | Other team | none |
| R28 | Mira after 07 | Courier Loop route: "past the repair door and chute"; Clear Address patch; "the sliding file wall later provides a legitimate shorter route" | `file_wall`; patch is a Mira atlas frame | New (decor) | `mira_decor_courier_loop` (desk plaque for the route), plus R1 and R4 |
| R29 | Mira after 11 | Lost Folios: "Archive Loop patch and a desk folder", the reopened archive loop | `file_wall` | New (decor) | `mira_decor_archive_folder` |
| R30 | Side quest | Misfiled Minute (no prop); "earlier log cabinets can be reopened" | `cabinet_2x1` | Rearrangement | none |

## Systems (levels 12 to 16, Mira after 13 and 16)

| # | Level | Named in levels.md | In atlas now | Class | New entries or how to build it |
| --- | --- | --- | --- | --- | --- |
| S1 | 12 | Payroll wing: "glass-backed ID trays and ten individually lit routing nodes" (the relocated payroll keypad) | landmark `routing_nodes_*` (ten nodes on the machine only) | New | `payroll_keypad_off`, `payroll_keypad_half`, `payroll_keypad_lit`; state set `payroll_keypad` (glass-backed ID tray and ten key nodes: none, five, ten lit) |
| S2 | 12 | "Each correct node lights a conduit" | `conduit_*_<family>` state sets (off, lit) | In atlas | none |
| S3 | 12 | "the first completed batch extends a bridge and return walkway toward Mira's chute" | `bridge_deck`, `bridge_rail`, `routing_walkway_after` (always present) | New | `bridge_span_retracted`, `bridge_span_extended`; state set `bridge_span` (a pit with end stubs, then a walkable deck); rails stay `bridge_rail` |
| S4 | 12 | Optional artifact ID envelope | none | Other team | none |
| S5 | 13, Mira after 13 | "nearby chute", "the Systems chute" | none | New | `courier_chute_idle`, `courier_chute_ready` (Systems palette) |
| S6 | 13 | "Smaller side room with orange sign markers" and "Refund sign flips to green" | none | New | `refund_sign_red`, `refund_sign_green`; state set `refund_sign` (red-orange plate with a plus, then mint plate with a minus; Systems has no pure red or green, so red is the safety-orange trim step and green the mint circuit step) |
| S7 | 13 | "inset calculator display", "a clearly reversible ledger" | none | New | `calc_display_charge`, `calc_display_refund`; state set `calc_display` (an inset display with the sign and digits, an open ledger beside it) |
| S8 | 13 | "the machine's warning light steadies" | `routing_beacon_before/after` | In atlas | none |
| S9 | 13 | "Hal sits instead of crouching" | none (Hal's folding stool is in his brief) | New | `folding_stool` (stool with the orange tool roll); Hal's pose is the cast team's |
| S10 | 14 | "six distinct alert lights and pictograms above porcelain panels"; "Correct labels separate the alarms into six hues" (alarm strips) | `status_board` (three families, two lights each, always lit) | New | `alarm_strip_merged`, `alarm_strip_separated`, `alarm_strip_muted`; state set `alarm_strip` (six identical lights and blank plates; six lights and pictograms; one light muted for the Quiet Alarm side quest) |
| S11 | 14 | "open a maintenance door" | `service_door` state set | Rearrangement | `service_door` in the alarm hall |
| S12 | 14 | Hal's portrait changes concerned to pleased | portraits atlas | Other team | none |
| S13 | 14 | Optional artifact Alarm strip (paper) | none | Other team | none |
| S14 | 15 | "Glass bridge" | `bridge_deck`, `bridge_rail` | In atlas | none |
| S15 | 15 | "bridge shutters open" | `wall_n_window_a/b` has no shutters | New | `bridge_shutter_closed`, `bridge_shutter_open`; state set `bridge_shutter` (a 2x2 window wall overlay) |
| S16 | 15 | "large formula wall ... connected parts of the formula illuminate" | none | New | `formula_wall_dark`, `formula_wall_half`, `formula_wall_lit`; state set `formula_wall` (six clause boxes joined by traces: none, three, six lit) |
| S17 | 15 | "hanging planters reflected in the floor" | `pot_plant_a/_b` (mint planters) | Rearrangement | `pot_plant_a/_b` on the bridge deck near the formula wall |
| S18 | 15 | "a clean sight line back to the routing machine" | none | Rearrangement | layout only |
| S19 | 15 | Optional artifact Scoring proof | none | Other team | none |
| S20 | 16 | "Relay room around a broad window onto the hub machine; three conduit families stay visually separate" | `wall_n_window_a/b`, `conduit_*` | Rearrangement | three `wall_n_window` placements side by side; conduits as in the reference room |
| S21 | 16 | "The machine lights in an intelligible sequence", "a service walkway opens", "Hal pulls down a false panel" | `conduit_*` lit, `routing_walkway_after`, `routing_panel_open` | In atlas | none |
| S22 | 16 | Optional artifact Original routing diagram | none | Other team | none |
| S23 | Mira after 13 | Payroll Run: "Signed and Sent patch" | patch is a Mira atlas frame | New (decor) | `mira_decor_signed_sent` |
| S24 | Mira after 16 | Glyph Dispatch: "a miniature relay decoration" | none | New (decor) | `mira_decor_relay` |
| S25 | Side quest | Quiet Alarm (mute one alert) | none | New | covered by `alarm_strip_muted` |

## Night Shift (levels 17 to 19, Mira after 18)

| # | Level | Named in levels.md | In atlas now | Class | New entries or how to build it |
| --- | --- | --- | --- | --- | --- |
| N1 | 17 | "Break-room kettle, noticeboard, lamp pools" | `break_counter`, `wall_n_noticeboard`, `pool_*` | In atlas | none |
| N2 | 17, 19 | The break room's warm-light state ("warmly lit", then "break room ... light up") | `break_counter` has a lit lamp in every use; `pool_break_*` is a separate pair | New | `break_counter_dim`, `pool_breaktop_fill`, `pool_breaktop_seam`; state set `break_room` (dim counter, then lit counter with its pool) |
| N3 | 17 | "a vestibule with a clear back exit", "the security glass opens" | `vestibule_gate_closed/_open` | In atlas (glass) | none for the glass |
| N4 | 17 | vestibule security props: card reader and exit | readers are baked into `vestibule_gate_*` | New | `reader_pedestal_locked`, `reader_pedestal_open`; state set `reader_pedestal`; `exit_sign_dim`, `exit_sign_lit`; state set `exit_sign` |
| N5 | 17 | "Ada walks alongside"; exit instruction card pinned to the HUD | none | Other team (cast, DOM UI) | none |
| N6 | 18 | "Repeated rows of desks initially look identical" | `desk_dead_a/b`, `station_a/b` | In atlas | none |
| N7 | 18 | "the Caps route uses varied lamp and carpet cues" | lamps and pools exist; no carpet | New | `carpet_cue_a`, `carpet_cue_b`, `carpet_cue_c` (three rugs, three patterns); lamps are `lamp`, `pool_*` |
| N8 | 18 | "the old route's stations are visibly silent" | `desk_dead_a/b` | In atlas | none |
| N9 | 18 | "Each repaired ticket wakes a different office lamp" | `lamp` state set, `station_a/b` | In atlas | none |
| N10 | 18 | "a coworker silhouette appears behind the interior window" | `window_figs` | In atlas | none |
| N11 | 18 | "Ada opens the north stair" | `service_door` carries a stair sign on the east wall only | New | `north_stair_closed`, `north_stair_open`; state set `north_stair` (2x2 north-wall door: lock grille, then folded grille and a stair) |
| N12 | 18, 19 | "service corridor", "Lights-Out Delivery on the return route"; the corridor "lights up" | `service_door`, `pool_route_*`, `lamp` | New | `courier_chute_idle`, `courier_chute_ready` (Night Shift palette); state set `corridor_light` (unlit lamp, then lamp with a route pool) |
| N13 | 19 | "Quiet archive-like room ... one warm ledger lamp against deep indigo" | `ledger_desk`, `pool_ledger_*`, `shelf_*` | In atlas | none |
| N14 | 19 | "silhouettes start moving independently" | `window_figs` | In atlas | none |
| N15 | 19 | "the elevator reveals the Executive Floor" | none | Other team (elevator) | none |
| N16 | 19 | Optional artifact Ada's shift book | none | Other team | none |
| N17 | Mira after 18 | Lights-Out Delivery: Night Courier patch | patch is a Mira atlas frame | New (decor) | `mira_decor_night_courier` |
| N18 | Side quest | Desk for Dawn (handover note) | `ledger_desk` | Rearrangement | none |

## Executive Floor (level 20)

| # | Level | Named in levels.md | In atlas now | Class | New entries or how to build it |
| --- | --- | --- | --- | --- | --- |
| E1 | 20 | "Vale waits beneath the atrium tree" | landmark `atrium_tree` | In atlas | none |
| E2 | 20 | Branch **The Name** (a renamed department); "nameplates become distinct" | `atrium_nameplates_before/after` only inside the landmark's single before and after states | New | `branch_name_before`, `branch_name_after`; state set `branch_name` (a wall nameplate: Pace's bars, then the original name); landmark states `repaired_name` and combinations (below) |
| E3 | 20 | Branch **The Route** (a rewarded detour); "copper floor lines straighten into useful paths" | `atrium_inlay_before/after` inside the landmark | New | `branch_route_before`, `branch_route_after`; state set `branch_route` (a copper detour loop, then a straight line with chevrons); landmark state `repaired_route` |
| E4 | 20 | Branch **The Count** (a corrected total); "window views resolve into real daylight" | `window_a/b`, `window_light`, `atrium_daylight_after` | New | `branch_count_before`, `branch_count_after`; state set `branch_count` (a tally board with a wrong total, then a corrected one); landmark state `repaired_count` and the existing `window_a/b`, `window_light` sets |
| E5 | 20 | Three branches "in any order" | the landmark has only `before` and `after` | New (states) | landmark `atrium_tree` gains states `repaired_name`, `repaired_route`, `repaired_count`, `repaired_name_route`, `repaired_name_count`, `repaired_route_count` (all eight combinations are now addressable) |
| E6 | 20 | "Ivo, Noor, Hal, Ada, and Mira arrive as silhouettes first, then as recognizable sprites": arriving coworkers' places | none (silhouettes are in the cast atlases) | New | `place_ivo`, `place_noor`, `place_hal`, `place_ada`, `place_mira` (one prop per coworker where they stand; sprites and silhouettes are the cast team's) |
| E7 | 20 | "After three accurate repairs, the visible final door opens" | `final_door` state set | In atlas | none |
| E8 | 20 | "Pace's signs become optional guidance" | Pace atlas | Other team | none |
| E9 | 20 | Seal, "Vale releases the raw audit to every floor" | none | Other team (DOM UI) | none |
| E10 | 20 | Optional artifact Public audit copy | none | Other team | none |
| E11 | Side quest | Names on the Wall (a staff credit list) | `wall_n_alcove`, `branch_name_*` plates | Rearrangement | a row of `branch_name_before/_after` plates |

## Open

Filled in at the end of the build; see the "Open" section of the producer report. Optional artifacts (R11, R15, R22, R27, S4, S13, S19, S22, N16, E10) are not drawn here: the generic artifact builder owns the close-up and its map placement and is integrated in wave 2.
