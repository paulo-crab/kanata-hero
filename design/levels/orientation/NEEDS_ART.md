# Orientation: art still needed beyond the kit

Wave 2 reconciled this district with the real kit (`art-direction/kit/orientation-atlas.json`, 101 entries and 10 state sets on this branch's base). Every prop that earlier versions of this file listed now exists in the atlas under its kit name, and `map.json` places it by that name with the kit's footprint and state sets: `elevator_*`, `elevator_call_panel`, `turnstile_*`, `clock_twin_*`, `conference_glass_door_*`, `projected_form_wall`, `stamp_a` to `stamp_h`, `pinboard_empty/_before/_after`, `desk_left_cherry`, `desk_right_mirror`, `review_table`, `keyboard_macbook`, `keyboard_spare`, `mail_board` with `mail_medals`, `mail_tray`, `artifact_unissued_badge`, `artifact_training_card`, `artifact_mirror_card`, `artifact_first_route_receipt`, `lamp_warm` and `corridor_stripe`. Collision is derived from the kit footprints, not from this team's guesses.

The garden cut-through needs no extra piece: it is the garden landmark's own `after` state (parts `garden_base_open` and `garden_north_rim_open`, which open column x12, y7-10), so `map.json` has no separate north-rim placement.

Only three names are still flagged `art_gap`, and all three are **already built on the branch `feat/art-orientation-completion`** (commit bb00f66; `ORIENTATION_KIT_SPEC.md` decisions 27-31) but are not in the atlas of this branch's base, so the validator cannot see them yet. Each is placed with `art_gap: true` and declared in `art_gap_entries` with exactly the footprint and collision the kit branch uses, so the derived collision is already the final one. **After that branch merges**, run `python design/levels/validate_levels.py --drop-solved-gaps orientation`: it removes the flags and declarations of every gap the atlas now covers (until then the flags are the only way to keep this district valid).

| Name | Level | Footprint | Collision | Layer | States | Purpose | Status |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `wall_w_plain` | 01 | 2x1 | 11 | rear_wall | single | West wall side plane on rows 2 to 16 (x0-1), two cells thick, mirror of `wall_e_plain`. | In the kit branch (30x16 px). Flag only until it merges. |
| `seating_nook_after` | 06 | 3x2 | 111/110 | rear_prop (y-sorted) | state set `seating_nook`: `hidden`, `shown` | The previously hidden seating nook of the `levels.md` revisit payoff. Placed at (20,7), east of the garden beside the Records corridor, where the old east sofa and side table stood; hidden before level 06, shown by `ls.garden-wake`. | In the kit branch with its state set. Flag only until it merges. |
| `seating_nook_glow` | 06 | 3x2 | 000/000 | light | drawn in `shown` | Lamp pool of the nook, drawn together with `seating_nook_after`. | In the kit branch. Declared only because the state set lists it. |

## Notes for the kit team and the implementation

- **Elevator.** The north-wall module (3x3 at x2-4, y0-2) is placed with the kit's `elevator` state set. The avatar arrives on the LIFT mat at (3,2); the open car is the centre cell (3,1). The kit's open state `111/101/000` makes the car a one-cell recess, not a through passage, which is what the arrival needs. Because `wall_w_plain` is two cells thick (x0-1), the module starts at x2.
- **Meeting-room door.** `conference_glass_door_*` uses the same module shape on the north wall at x18-20. Its open state also leaves only a one-cell recess behind the glass, so the "clock room" of earlier drafts is now a recess rather than a walkable room; nothing in the levels needs more.
- **Turnstile.** The kit's 3x1 turnstile sits in the mailroom's north partition line at x22-24 with the lane at (23,12). Its open state leaves a one-cell lane between the pedestals (the kit's design); no main-route cell passes through it.
- **Records door.** `records_door` is used as before at x26-27, y5-7; `wall_e_plain` is omitted on those rows so the door's collision governs.
- **Seating convention.** Chairs are empty (no seated workers in Orientation), so `desk_a_front` and `desk_b_front` are not placed.
