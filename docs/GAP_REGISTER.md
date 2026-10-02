# Kanata Hero: gap register (producer, 2026-10-02)

Result of the producer's review of the art-direction deck against the repo. Every gap was verified in the repo before it was assigned. All wave-1 work lives on local feature branches that stack on `feat/art-production` and are merged only after human review.

## Wave 1: gaps, owners, branches, status

| # | Gap | Owner | Blocks first slice | Branch | Status |
| --- | --- | --- | --- | --- | --- |
| G1 | Layout help drew only the `nav` tab | Art director, UI | Yes | `feat/ui-layout-help-and-screens` | Closed (merged) |
| G2 | No specs for setup/calibration, terminal/editor scene, input feedback, artifact frame, elevator map, seals/toast, Mira results, settings | Art director, UI | Yes (setup, editor scene, feedback) | same | Closed (merged) |
| G3 | Orientation quest props missing (elevator, turnstile, clock, stamps, pinboard, review table, mailroom) | Art director, Orientation kit | Yes | `feat/art-orientation-quest-props` | Closed (merged) |
| G4 | Shared elevator, desk-front occluders, artifact builder | Art director, Orientation kit | No | same | Closed (merged) |
| G5 | Quest props for Records, Systems, Night Shift, Executive | Art director, district kits | No | `feat/art-district-quest-props` | Closed (merged) (optional artifacts open) |
| G6 | No level data for any district | Level designers (4 sessions) | Yes (Orientation, schema, inventory) | `feat/levels-orientation-foundation`, `feat/levels-records`, `feat/levels-systems`, `feat/levels-nightshift-executive` | Closed (merged, reconciled with the art in wave 2) |
| G7 | Vale softening states 1-3 | Character designers | No | `feat/cast-vale-hal-poses` | Closed (merged) |
| G8 | Hal crouch, seated, panel pull, stool prop | Character designers | No | same | Closed (merged) |
| G9 | Glitch repaired frames, ordinary props, variant and district table | Character designers | Adjacent | `feat/cast-glitch-repair-variants` | Closed (merged) |
| G10 | Seated background workers | Character designers | No | none yet | Closed (merged, south-facing only) |
| G11 | Deck and handoff called unfinished art "deliberate" | Producer | No | `docs/producer-gap-register` | Closed (section 7 rewritten, deck slide updated) |

Merge order: the base `feat/art-production` first, then the eight team branches in any order (their files are disjoint; the level branches share only the validator on `feat/levels-orientation-foundation`), then `docs/producer-gap-register` last (its handoff text describes the merged state).

## Wave 2 (done, merged 2026-10-02; kept for the record)

1. Orientation integration: replace `art_gap` entries that now exist in the kit with real atlas names; move the elevator onto a lift core (the kit draws north-wall modules, the data puts it on the west wall); add `garden_north_rim_open` and `wall_w_plain` to the kit; place the hidden seating nook.
2. Kit integration: register the elevator, desk-front occluders and artifact props in the Records, Systems, Night Shift and Executive kits; draw the ten remaining optional artifacts; add the Records props the level data still names (`cabinet_gate_*`, `cabinet_labels_*`, `archive_ledger_mark_*`, address door panel); add the Systems machine states after levels 12, 13 and 14 and the Orientation `garden` after-state through route.
3. Name reconciliation: `mail_chute_*` (Records data) vs `courier_chute_*` (kit); the duplicate stool (`folding_stool` in the Systems kit, `stool_folding` in the Hal prop atlas; keep the Hal geometry, the seat offset depends on it); Systems and Night Shift `art_gap` names vs the quest-prop names.
4. Level data to the art: glitch placements to the district table (Systems first glitch is level 12, a stapler; variants `standard`, `plum`, `dusk`); Hal and Vale animation names replace the stand-ins; a link for the false-panel stop (`link.panel.systems-nightshift`); schema `any_of` or `count` trigger atoms and a first-class "NPC not yet present" state.
5. Seated background workers drawn to the seat convention in `kit/ORIENTATION_KIT_SPEC.md`.
6. Fix the validator errors that appear only once the art and level branches are merged together (trial merge of all ten branches: art build 43/43, level validator 30 errors, none in Night Shift or Executive): Orientation collision grid vs the real elevator, turnstile and conference-door footprints (16); Records ladder states (`parked`, `moved` vs `closed`, `open`) (3); Systems `formula_wall` states (`dim`, `clause_1` to `clause_6` vs `dark`, `half`, `lit`) and four collision cells near the machine (11). Then add `design/levels/validate_levels.py --all` to `art-direction/build_all.py` (producer decision) so this cannot drift again.

## Needs a human decision

- Approve or reject the new Orientation kit section (its spec says "pending the producer's review") and the other approvals the director would normally record.
- Fourteen Systems hints and four Night Shift/Executive hints were derived from the gesture inventory, not copied from `levels.md`; check them against `~/.config/kanata/kanata.kbd`.
- The layout manifest for Layout help (derived from `kanata.kbd`) is not created; it belongs to the implementation change.
- Records: the review terminal sits in the far-east chamber and the circular desk lights up on the seal; confirm that reading of `levels.md` level 11.
- UI keys not defined by the game spec: Focused-mode "Show hint", interact, journal, back, elevator (see `UI_KIT_SPEC.md`).
- The deck's ask slide says "38 commits on feat/art-production"; the branch has 40.

## Handoff text to apply once the branches are merged

These edits touch files that name paths created by the branches, so they cannot live on this branch (`check_handoff.py` would fail).

- ART_HANDOFF section 3.1: Vale softening states are sets `s1_*` to `s3_*` (idle, walk, interact) named `vale_s<k>_<set>_<facing>`; the renderer uses `k = min(repairs, 3)` and the base `vale_<set>_<facing>` for 0. Walk-like extra sets carry `px_per_frame` and `contact_frames`. Entries may carry `softening_state`, `prop`, `prop_atlas`, `stool_cell_in_frame_px`, `stool_sprite_in_frame_px`.
- ART_HANDOFF section 3.4: repaired is `<a>_repaired` (1 frame, 160 ms, play once) then `<a>_ordinary` (static, with `archetypes.<a>.ordinary`); the atlas is 128x192; `variants` and `districts.<id>` are the level-data contract.
- ART_HANDOFF section 3.5: state sets also include `elevator`, `turnstile`, `clock_twin`, `conference_door`, `pinboard`, `mail_medals` (0-6), `lamp_warm`, `corridor_stripe` and the district quest-prop sets; north-wall doors (`repair_door`, `north_stair`) replace two plain wall tiles and must not sit above plain wall collision.
- ART_HANDOFF section 4: UI screens beyond the stage are rendered in `ui-kit/screens/`; `reference.html#s-<id>` shows one screen.
- ART_HANDOFF section 5: add the generated files named in each branch's report (Orientation quest room and proof sheets, district `*-quest-props-*` renders and `quest_props.py`, `ui-kit/screens/*.png`, `kit_screens.py`, `kit_screens2.py`, `cast/hal-props-atlas.*`, Vale and Hal review renders) and a level-data row pointing at `design/levels/SCHEMA.md`.
- PRODUCTION_STATUS: one Approved row per branch (dated, director), plus the lesson "a prop's light fill must not match the floor it stands on" (the stone stool vanished on porcelain).
- README: document-map row for `design/levels/` (SCHEMA.md owns the contract); decisions-log lines for the Records level layout, the Vale facings decision (all four facings per state), the glitch district table, and UI screens.
