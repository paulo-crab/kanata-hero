# Orientation: art still needed beyond the kit

Wave 2 reconciled this district with the real kit (`art-direction/kit/orientation-atlas.json`). Every prop that earlier versions of this file listed now exists in the atlas under its kit name, and `map.json` places it by that name with the kit's footprint and state sets: `elevator_*`, `elevator_call_panel`, `turnstile_*`, `clock_twin_*`, `conference_glass_door_*`, `projected_form_wall`, `stamp_a` to `stamp_h`, `pinboard_empty/_before/_after`, `desk_left_cherry`, `desk_right_mirror`, `review_table`, `keyboard_macbook`, `keyboard_spare`, `mail_board` with `mail_medals`, `mail_tray`, `artifact_unissued_badge`, `artifact_training_card`, `artifact_mirror_card`, `artifact_first_route_receipt`, `lamp_warm` and `corridor_stripe`. Collision is derived from the kit footprints, not from this team's guesses.

The garden cut-through needs no extra piece: it is the garden landmark's own `after` state (parts `garden_base_open` and `garden_north_rim_open`, which open column x12, y7-10), so `map.json` has no separate north-rim placement.

No names are flagged `art_gap` any more. The last three (`wall_w_plain`, `seating_nook_after`, `seating_nook_glow`) were built by the Orientation kit completion (`ORIENTATION_KIT_SPEC.md` decisions 27-31) and the flags were cleared with `validate_levels.py --drop-solved-gaps orientation`.

## Notes for the kit team and the implementation

- **Elevator.** The north-wall module (3x3 at x2-4, y0-2) is placed with the kit's `elevator` state set. The avatar arrives on the LIFT mat at (3,2); the open car is the centre cell (3,1). The kit's open state `111/101/000` makes the car a one-cell recess, not a through passage, which is what the arrival needs. Because `wall_w_plain` is two cells thick (x0-1), the module starts at x2.
- **Meeting-room door.** `conference_glass_door_*` uses the same module shape on the north wall at x18-20. Its open state also leaves only a one-cell recess behind the glass, so the "clock room" of earlier drafts is now a recess rather than a walkable room; nothing in the levels needs more.
- **Turnstile.** The kit's 3x1 turnstile sits in the mailroom's north partition line at x22-24 with the lane at (23,12). Its open state leaves a one-cell lane between the pedestals (the kit's design); no main-route cell passes through it.
- **Records door.** `records_door` is used as before at x26-27, y5-7; `wall_e_plain` is omitted on those rows so the door's collision governs.
- **Seating convention.** Chairs are empty (no seated workers in Orientation), so `desk_a_front` and `desk_b_front` are not placed.
