# Vertical slice: the exact file list

The first implementation slice (`docs/game-design.md`, "Implementation slices" item 1) is: setup and calibration, a walkable Orientation hub, an inventory manifest, quests 1 to 3, one NPC dialogue flow, the Morning Mail speed side quest, Standard mode, local progress, physical-key diagrams, the Layout help screen and confidence-aware input feedback. This file lists what makes that up and in what order the player meets it. Everything below is in this repository; nothing needs inventing.

## Files

### Level data (`design/levels/`)

| File | Role in the slice |
| --- | --- |
| `SCHEMA.md`, `level-data.schema.json` | The data contract; the loader and any editor read these. |
| `validate_levels.py` | Run in CI: `python design/levels/validate_levels.py design/levels/orientation` must exit 0. |
| `gesture-inventory.json` | The inventory manifest (68 rows, B01 to V06) with ids, layers, inputs, outputs, confidence labels and the level that introduces each row. The Layout help and the journal's per-gesture evidence read it. |
| `world.json` | Districts, elevator stops, links, seals, the Mira route index, and every persistent state id (levels done, seals, artifacts, patches, flags). The progress store keys come from here. |
| `orientation/district.json` | Hub, entrances, exits, elevator, light states, ambient note, the Plant Tags side quest, Pace signs. |
| `orientation/map.json` | Floor grid, placements, derived collision, gates (turnstile, clock-room door, Records door, garden cut-through), zones, interactions, NPCs, routes, spawns, art gaps. |
| `orientation/levels/01-the-lobby.json`, `02-badge-printer.json`, `03-the-clock.json` | The three slice quests, with steps, scenes, dialogue, triggers and state changes. |
| `orientation/mira/02-morning-mail.json` | The Morning Mail speed side quest (checkpoints, scenes, dialogue, baseline note). |
| `orientation/coverage.json` | Guided, variation and recall evidence per owned gesture; the progress model's evidence rows start from it. |
| `orientation/levels/04..06-*.json` | Present and validated, but not required: the hub already contains their desks and the review table. In the slice their interactions show a "coming later" card and the Records door stays closed. |
| `orientation/LEVEL_SHEET.md`, `NEEDS_ART.md` | Routes, camera and inset notes; the props that need art. |

### Art (`art-direction/`, see `ART_HANDOFF.md`)

- Kit: `kit/orientation-atlas.png` and `.json` (floor, walls, windows, alcove, `records_door`, `lamp`, planters, `sofa`, `side_table`, `printer`, `desk_a`, `desk_b`, `chair`, `bench`, `mail_counter`, partitions, `route_inlay`, `records_mat`, the `garden` landmark). Layout reference: `kit/orientation-review-room.json` and `kit/kitlib.py` (collision rules).
- **Props not in the atlas yet** (placed with `art_gap: true`; draw a footprint rectangle in the layer's colour until the kit team ships them): see `orientation/NEEDS_ART.md`. The slice needs these art states to be visible from the start or at slice milestones: `elevator_*`, `elevator_call_panel`, `wall_w_plain`, `turnstile_*`, `clock_twin_*`, `conference_glass_door_*`, `projected_form_wall`, `mail_board`, `mail_tray`, plus (always visible in the hub) `desk_left_cherry`, `desk_right_mirror`, `stamp_a..h`, `pinboard_before`, `review_table`, `keyboard_*`. Hidden-until-later pieces are `artifact_*` and `garden_north_rim_open`.
- Cast: `gate1/engineer-full-atlas.*` (the avatar), `cast/ivo-atlas.*`, `cast/mira-atlas.*`, `cast/bgworker_a-atlas.*`, `cast/bgworker_b-atlas.*`; `glitches/glitches-atlas.*` (the `form` archetype for the optional folded-form repair); `pace/pace-atlas.*` (signs and floor arrows); `portraits/portraits-atlas.*` (neutral, concerned, pleased, `ivo_laugh`, `mira_grin`).
- UI: `ui-kit/tokens.css` and `ui-kit/COMPONENTS.md`.

### Not part of the slice

Records, Systems, Night Shift and Executive districts; levels 04 to 06 as playable quests (data is present); the elevator map beyond the Orientation stop; Mira's other routes.

## Scene order

1. **Setup and calibration.** MacBook or Microsoft keyboard diagram; calibration of Caps + H, Caps + N, Space + A, Space + Q and a home-row Shift hold; practice toggle-out instructions (`docs/game-design.md`, "Browser behavior and accessibility"). Not level data; it sets the flags `setup-done`, `calibration-done`, `keyboard-macbook` or `keyboard-microsoft` in `world.json`.
2. **Hub, arrival.** `orientation/map.json` spawn `arrival` at (2,12); the elevator plays closed, half, open and the avatar steps out. Ivo's greeting starts level 01.
3. **Level 01, The Lobby.** `popup` (tap Caps), `loop` (four arrows), `four-stops` (with the `desk-label` scene at the west desk), `unprompted` (recall walk to Ivo), optional `fold` glitch after.
4. **Level 02, Badge Printer.** Four label scenes at the printer; Mira appears in the mailroom; Plant Tags becomes available.
5. **Level 03, The Clock.** Three guided form scenes (Space, Tab, modifier-first), the variation form and the recall form; the clock room opens.
6. **Morning Mail.** Mira in the mailroom (21,14); three slip checkpoints; baseline, First Delivery patch and the mail tray. Standard mode throughout.

## UI components each scene needs

Names from `art-direction/ui-kit/COMPONENTS.md`. Components being specified right now by the UI team are marked (new).

| Scene | Components |
| --- | --- |
| Setup and calibration | Setup and calibration screen (new), Keycap, Keyboard teaching inset, Layout help (reachable with `?`). |
| Hub and every walk scene | HUD (objective, seal count), Interaction prompt, Markers (coral conversation, teal terminal, gold route, violet glitch), Keyboard teaching inset (position cue on guided and variation scenes only), Quest journal (main, optional and Mira headings), Layout help, Elevator map (new) from the call panel. |
| Dialogue | Dialogue panel with the chibi portraits; hint lines render the action, the key and the gesture by difficulty (Standard shows all three, Focused on request, Violento action only). |
| Terminal and editor scenes (`label`, `form`, `editor`, `keypad`, `log`) | Terminal and editor scene (new): reading column, strong cursor, field focus ring, scratch field with auto-clear, practice region with announced Tab trap and Escape exit. Confidence feedback (new): three separate lines for physical gesture shown, logical output observed, effect in the game, plus the confidence label (`output-observed`, `player-confirmed`, `external-only`). |
| Held Space, held Tab, Homerow | Confidence feedback with the player-confirm buttons (opened / did not open / skip) and the 220 ms and 250 ms hold rings in the Keyboard teaching inset. |
| Optional artifacts (unissued badge) | Artifact close-up (new): shared document frame, caption of two to four lines, engineer portrait (concerned). |
| Mira route | Journal "Optional speed" heading, checkpoint markers on the world map after a first attempt, baseline line ("records the duration as a baseline"). |

## The Ivo dialogue flow (levels 01 to 03)

One flow per level, in this order: greeting, task (hint object shown by difficulty), hint on request, success, then the world change. After level 01's route Ivo's pose changes from `ivo_wave_s` to `ivo_nod_s`; during level 03 his tablet flashes (`ivo_tablet_flash_s`) until the clock synchronizes. Portraits follow the `levels.md` cue map: neutral everywhere except pleased when the clock hands synchronize. Hint lines are always neutral. Hint-bearing entries carry `hint: {action, key, gesture}`; entries marked "on request" repeat the hint when the player asks.

### Level 01

| Id | Speaker | Text | Hint | When |
| --- | --- | --- | --- | --- |
| `o01.d.welcome` | ivo (neutral) | Welcome to the Department of Motion. I'm Ivo, reception. Before your first ticket I need ... | no | `step_start:o01.s.arrive` |
| `o01.d.popup` | ivo (neutral) | To close the welcome popup, you need to press Escape. | yes | `step_start:o01.s.popup` |
| `o01.d.popup-again` | ivo (neutral) | To close the welcome popup, you need to press Escape. | yes (on request) | `request:o01.d.popup` |
| `o01.d.popup-done` | ivo (neutral) | Good. The popup is gone and the lobby is yours to walk. | no | `scene_success:o01-popup` |
| `o01.d.loop-right` | ivo (neutral) | To walk to the east side of the garden, you need to press Right Arrow. | yes | `step_start:o01.s.loop` |
| `o01.d.loop-up` | ivo (neutral) | To walk north along the garden's east edge, you need to press Up Arrow. | yes | `reach_cell:17,12` |
| `o01.d.loop-left` | ivo (neutral) | To walk west along the north edge, you need to press Left Arrow. | yes | `reach_cell:17,5` |
| `o01.d.loop-down` | ivo (neutral) | To walk south along the west edge, you need to press Down Arrow. | yes | `reach_cell:9,5` |
| `o01.d.loop-done` | ivo (neutral) | That is one full lap, in four directions. Now the desks. | no | `scene_success:o01-loop` |
| `o01.d.stops` | ivo (neutral) | Please visit the north desk, the west desk, the south desk and the east desk, in that order. | no | `step_start:o01.s.stops` |
| `o01.d.west` | ivo (neutral) | To walk to the west desk, you need to press Left Arrow. | yes | `reach_cell:9,4` |
| `o01.d.label` | ivo (neutral) | To label the west desk, you need to press W, E, S, T. | yes | `reach_cell:7,10` |
| `o01.d.stops-done` | ivo (neutral) | That is all four desks. Wait there; I will come to you. | no | `scene_success:o01-four-stops` |
| `o01.d.recall` | ivo (neutral) | Come and find me at the north desk, then meet me back at reception. | no | `step_start:o01.s.recall` |
| `o01.d.recall-hint` | ivo (neutral) | To reach Ivo at the north desk, you need to press Up Arrow, then Left Arrow. | yes (on request) | `request:o01.d.recall` |
| `o01.d.reminder` | popup | Badge reminder: please collect your badge at the printer. | no | `` |
| `o01.d.thanks` | ivo (neutral) | Thank you. Four desks, four directions. The turnstile is open now, and I have stopped wav... | no | `scene_success:o01-unprompted` |
| `o01.d.pace-sign` | pace_sign | Approved route: follow the arrows. Efficiency is a pleasant habit. | no | `` |
| `o01.d.fold-intro` | ivo (neutral) | A folded form is wandering the south side. It is harmless; it only needs a letter. | no | `trigger:o01.t.route-done` |
| `o01.d.fold-move` | form_card | To move to the end of the word, you need to press Right Arrow. | yes | `interact:glitch_lobby` |
| `o01.d.fold-type` | form_card | To finish the word, you need to press Y. | yes | `scene_success:o01-fold` |

### Level 02

| Id | Speaker | Text | Hint | When |
| --- | --- | --- | --- | --- |
| `o02.d.ask` | ivo (neutral) | The badge printer keeps printing generic names. Please restore my badge and three coworke... | no | `step_start:o02.s.talk` |
| `o02.d.hint-b` | printer_card | To print the `b` in Bea's name, you need to press B. | yes | `step_start:o02.s.guided` |
| `o02.d.hint-w` | printer_card | To print the `w` in Wren's name, you need to press W. | yes | `step_start:o02.s.guided` |
| `o02.d.hint-r` | printer_card | To print the `r` in Wren's name, you need to press R. | yes | `step_start:o02.s.guided` |
| `o02.d.hint-n` | printer_card | To print the `n` in Wren's name, you need to press N. | yes | `step_start:o02.s.guided` |
| `o02.d.hint-u` | printer_card | To print the `u` in Umi's name, you need to press U. | yes | `step_start:o02.s.guided` |
| `o02.d.hint-m` | printer_card | To print the `m` in Umi's name, you need to press M. | yes | `step_start:o02.s.guided` |
| `o02.d.hint-t` | printer_card | To print the `t` in Kit's name, you need to press T. | yes | `step_start:o02.s.guided` |
| `o02.d.hint-x` | printer_card | To print the `x` in Xan's name, you need to press X. | yes | `step_start:o02.s.guided` |
| `o02.d.hint-v` | printer_card | To print the `v` in Tove's name, you need to press V. | yes | `step_start:o02.s.guided` |
| `o02.d.hint-40` | printer_card | To print badge number 40, you need to press 4, then 0. | yes | `step_start:o02.s.guided` |
| `o02.d.hint-comma` | printer_card | To separate the two names, you need to press comma. | yes | `step_start:o02.s.guided` |
| `o02.d.hint-request` | ivo (neutral) | To print the `b` in Bea's name, you need to press B. | yes (on request) | `request:o02.d.hint-b` |
| `o02.d.success` | ivo (neutral) | Every card says what it should. The task light has steadied. Mira is in the mailroom if y... | no | `scene_success:o02-recall` |
| `o02.d.mira-early` | mira (neutral) | Once the printer is honest, find me in the mailroom. I will teach you the loop. | no | `interact:mira_early` |
| `o02.d.badge-note` | engineer (concerned) | The old badge names a department that does not match today's sign. | no | `interact:artifact_unissued_badge` |

### Level 03

| Id | Speaker | Text | Hint | When |
| --- | --- | --- | --- | --- |
| `o03.d.ask` | ivo (neutral) | The meeting-room clock disagrees with itself, and my scheduling form lost its spaces and ... | no | `step_start:o03.s.talk` |
| `o03.d.space` | ivo (neutral) | To separate the two times, you need to press Space. | yes | `step_start:o03.s.guided` |
| `o03.d.tab` | ivo (neutral) | To move to the next field, you need to press Tab. | yes | `scene_success:o03-guided-space` |
| `o03.d.shift-tab` | ivo (neutral) | To move back a field, you need to press Shift + Tab. | yes | `scene_success:o03-guided-tab` |
| `o03.d.space-request` | ivo (neutral) | To separate the two times, you need to press Space. | yes (on request) | `request:o03.d.space` |
| `o03.d.homerow` | ivo (neutral) | If Homerow opened, tell the form so; if not, tell it that too. Neither answer changes the... | no | `scene_success:o03-guided-space` |
| `o03.d.success` | ivo (pleased) | The hands agree. Two times, one clock, and my tablet has stopped flashing. | no | `scene_success:o03-recall` |

### Morning Mail

| Id | Speaker | Text | Hint | When |
| --- | --- | --- | --- | --- |
| `mm.d.intro` | mira (grin) | Mira, courier. Learn the loop first: three slips, three desks. No clock this time; I only... | no | `interact:mira` |
| `mm.d.offer` | mira (neutral) | Take the slips from the tray whenever you are ready. | no | `dialogue_done:mm.d.intro` |
| `mm.d.hint-west` | slip_card | To write the number on the west slip, you need to press 0, then 4. | yes | `interact:mm_checkpoint_west` |
| `mm.d.hint-north` | slip_card | To write the u in the north slip, you need to press U. | yes | `interact:mm_checkpoint_north` |
| `mm.d.hint-east` | slip_card | To separate the east slip's two names, you need to press comma. | yes | `interact:mm_checkpoint_east` |
| `mm.d.fix` | mira (neutral) | That slip says something else. Try the letters again; nothing is lost. | no | `interact:mira` |
| `mm.d.baseline` | mira (pleased) | Clean run. That is your baseline, and I'll sew on the patch. A quicker loop is there if y... | no | `interact:mira` |

## Scenes and their tasks

| Scene | Kind | Cue | Summary |
| --- | --- | --- | --- |
| `o01-popup` | form | cue | A welcome popup covers the lobby. Tap Caps once to close it; holding Caps and pressing a second key is not the |
| `o01-loop` | walk | cue | Walk once around the garden, one direction at a time: right, up, left, down. Each leg ends on a lit floor mark |
| `o01-four-stops` | walk | cue | Visit the north, west, south and east desks in that order. Floor markers show where each desk is, not which ke |
| `o01-desk-label` | label | cue | At the west desk a label prompt asks for the desk's name. Caps may still be held from walking: release it, the |
| `o01-unprompted` | walk | no cue | Ivo has gone to the north desk: walk to him with no markers, then back to reception when he returns. A badge r |
| `o01-fold` | editor | cue | Optional glitch repair: a folded form in the south lobby shows the word lobb. Move to the end of the word with |
| `o02-guided-mapped` | label | cue | Print the engineer's badge and three coworkers' labels, then a badge number and a two-name card, one plain map |
| `o02-guided-home` | label | cue | Type the home-row keys as plain letters: asdf, jkl; and two names that use them. |
| `o02-variation` | label | cue | Print three mixed labels that roll across home-row keys on one hand and mix in digits and a comma; rolls must  |
| `o02-recall` | label | no cue | Print one shuffled label with every mapped plain key and the home row, with no highlighted keys. |
| `o03-guided-space` | form | cue | Separate two times with a tapped Space, then see what a held Space does in a scratch field (digits, not a spac |
| `o03-guided-tab` | form | cue | Fill three fields moving with a tapped Tab; then hold Tab once and confirm what happened outside the page. |
| `o03-guided-modfirst` | form | cue | Hold a modifier before Space or Tab and see that both stay ordinary: Shift + Tab moves back a field, Shift + S |
| `o03-variation` | form | cue | Correct two appointment lines that are missing spaces and tabs, using tapped Space, tapped Tab, and one Shift  |
| `o03-recall` | form | no cue | Fill a fresh appointment line with no highlighted keys: a two-word title, a time, a room, and one back-step. |
| `mm-west` | label | no cue | Type the label on the west desk's slip and deliver it. |
| `mm-north` | label | no cue | Type the label on the north desk's slip and deliver it. |
| `mm-east` | label | no cue | Type the label on the east desk's slip and deliver it. |

Every scene has instant retry, a concrete `task` object (targets, accepted outputs, feedback strings that name the observed output) and success criteria. The recall scenes (`o01-unprompted`, `o02-recall`, `o03-recall`) declare `position_cue: false`.

## Progress and storage

Persist only ids from `world.json` `state_ids`: `levels_done`, `seals`, `artifacts`, `patches`, `mira_routes_cleared`, `flags`, plus per-NPC state names (`ivo`: `start`, `post_wave`, `north`, `post_nod`, `tablet`, `steady`, `laugh`; `mira`: `start`, `mailroom`, `right_desk`) and the Morning Mail baseline run (duration and accuracy). All of it goes to `localStorage`; nothing is needed for basic offline play.

## Open items

- **Art gaps.** 35 prop entries (28 placed kinds) need kit art; see `orientation/NEEDS_ART.md`. The slice can run with footprint rectangles.
- **Setup and calibration, terminal and editor scene, confidence feedback, artifact close-up and elevator map** are being specified by the UI team now; the data here names the fields they need (`task`, `confidence`, `position_cue`, player-confirm steps) but not their layout.
- **Mira's patched portraits.** After the first clean baseline Mira wears patch 1; the dialogue data uses the base expressions, so the runtime should swap to the `mira_patch1_*` rows of `portraits-atlas.json` after `first_delivery`.
- **Right Command evidence.** Right Command + H/J/K/L and Caps + H/J/K/L produce the same arrows, so level 06's route comparison is output-observed only (not part of the slice).
- **Garden cut-through** needs one extra art piece (`garden_north_rim_open`) to be a through route; not part of the slice.
- **Walk-scene details** such as marker sprites for the loop corners reuse `route_inlay`; a dedicated marker piece is optional.
