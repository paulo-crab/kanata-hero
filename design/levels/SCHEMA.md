# Level data schema

**Schema version 0.2** (`level-data.schema.json` carries `x-schema-version`; `world.json` `version` is 0.2). Version 0.2 adds, all backward compatible (every 0.1 file stays valid): the dialogue `modal` flag and the Hint key rules, the `any_of` and `count` condition atoms, the reserved NPC state `absent` with `initial_state`, the reserved-key rule for scene tasks, the `panel` link kind with `link.panel.systems-nightshift`, `visible_when` checking, and two validator modes (`--selftest`, `--drop-solved-gaps`). The key bindings come from [`design/ui-key-bindings.md`](../ui-key-bindings.md).

The contract every district's level data follows. The machine-readable form is [`level-data.schema.json`](level-data.schema.json); [`validate_levels.py`](validate_levels.py) checks the shapes and the cross-file rules below. The game loads this data as plain JSON. Nothing here describes art: props are referenced by name from the kit atlas, and a prop the kit does not have yet is declared as an `art_gap`.

Sources: `docs/game-design.md` ("Asset and level handoff", gesture inventory, hint grammar), `levels.md` (stories, per-district handoff checklist, portrait cue map), `art-direction/ART_HANDOFF.md` §3.5 to §3.8 (kit, room layouts, Pace, portraits).

```
python design/levels/validate_levels.py design/levels/orientation   # one district
python design/levels/validate_levels.py --all                       # every district that exists
python design/levels/validate_levels.py --all -v --strict           # list warnings; fail on them
python design/levels/validate_levels.py --selftest                  # mutation tests for the 0.2 rules (26 cases) and the layout checks (31 cases)
python design/levels/validate_levels.py --drop-solved-gaps orientation   # after a kit branch lands: drop art_gap flags the atlas now covers
```

The script resolves paths from its own location, so it runs the same from any worktree. It needs Python 3 and `jsonschema` (the art pipeline venv has it).

## Layout

Orientation team only: `SCHEMA.md`, `level-data.schema.json`, `validate_levels.py`, `gesture-inventory.json`, `world.json`, `SLICE.md`.

Per district `<id>/` with id one of `orientation | records | systems | nightshift | executive`:

| File | Content |
| --- | --- |
| `district.json` | identity, kit path, camera bounds, hub, entrances, exits, elevator, light states, ambient note, optional side quests |
| `map.json` | floor grid, placements, collision, zones, interactions, NPCs, routes, spawns, gates, art gaps |
| `levels/<NN>-<slug>.json` | one per main level (NN = 01..20 across the campaign; each district owns its range) |
| `mira/<NN>-<route-slug>.json` | one per Mira route; NN is the number of the level it follows |
| `coverage.json` | guided / variation / recall evidence per owned gesture |
| `LEVEL_SHEET.md` | one page: routes, before/after, lighting, keyboard-inset conflicts |
| `NEEDS_ART.md` | every `art_gap` prop and why the kit cannot cover it |

## Coordinates and the camera

- Cells are 16 x 16 px. `[x, y]` with the origin at the top-left. Map sizes come from `levels.md` ("World and art rules").
- The camera is 320 x 180 px (20 x 11.25 cells) and scrolls inside `camera_bounds` (cells). The avatar's feet sit at screen (160, 100), so the route ahead stays visible; the camera clamps at the bounds.
- The keyboard inset covers stage x 16 to 588, y about 412 to 704 at x4, which is logical x 4 to 147, y 103 to 176. The validator replays the camera for the first approach cell of every interaction and warns where the avatar or the target falls inside that rectangle. Every such interaction id must be named in a "Keyboard-inset conflicts" section of `LEVEL_SHEET.md`.
- Placement `cell` is the footprint's top-left cell. `offset` (0 to 15 px) is visual only; collision always uses the cell.

## world.json (global, Orientation team)

`districts` (id, name, order, level range, size, elevator stop with its `link` and the seal that unlocks it, review level, Mira route ids); `links` (every door, panel or elevator connection a district's `entrances`, `exits` and `elevator` refer to by id; `between` names the districts it joins; a door or panel link may carry `cells`, the cell in each district, which an exit on that link must match: `link.orientation-records` is Orientation (26,6) and Records (0,8)). Link kinds are `elevator`, `door` and `panel`. A `panel` link is a hidden panel between two districts: it must carry a cell for each district and the `seal_required` that reveals it. `link.panel.systems-nightshift` is the false panel Hal pulls down on the Systems machine (Systems seal) to reach the Night Shift elevator stop. Its cells are **placeholders**: the Systems exit is parked at (22,3) and the Night Shift entrance at the Night Shift elevator arrival (31,16). The Systems team places the real panel cell and updates this link; until a Systems exit names the link, nothing checks the cell; `seals` (levels 06, 11, 16, 19, 20; the first four each unlock the next stop, the fifth records completion); `mira_routes` (the global index: id, district, `available_after`, patch); `state_ids` (the ids persistent progress may hold: levels done, seals, artifacts, patches, cleared Mira routes, flags). A district file may only name ids that exist here.

## gesture-inventory.json

One row per `docs/game-design.md` inventory entry B01 to B15, N01 to N21, S01 to S26, V01 to V06: `id, layer, input, output, notes, source_line` (line in `game-design.md`), `introduced_in` (level number from the "Cover ..." line of `levels.md`), `reviewed_in`, `external_only`, `player_confirmed`, `confidence`. The validator reports inventory rows no level links to; rows owned by a district that has not landed yet are warnings, rows owned by a validated district are errors.

**Link to the layout manifest (inventory version 0.2).** A top-level `manifest` field names `design/layout/layout-manifest.json`, which links every inventory id to the keys and layers that produce it, with the observed-output rule, the verification method (`observed`, `player_confirmed`, `external_only`, from `confidence`) and the lesson ids (`introduced_in` and `reviewed_in`). `validate_levels.py --all` runs `design/layout/check_layout.py`, which fails when the two files disagree (ids, lessons, verification, `source_line` pointing at the right row of `docs/game-design.md`), when a link's expectation is false against the parsed `kanata.kbd`, when `design/ui-key-bindings.md` or a hint line in `levels.md` or the level data names a gesture the config does not produce, and when the UI kit's Layout help tabs drift from the manifest (known differences are listed in `design/layout/kit-known-mismatches.json`). `--selftest` also runs the 31 layout cases that break a binding on purpose. See `design/layout/README.md`.

## district.json

`id, name, size_cells, kit` (path to the atlas JSON), `palette`, `camera_bounds {x,y,w,h}`, `hub_cell`, `entrances` (id, cell, facing, `from {district, link}`), `exits` (id, cell, `to {district, link}`, optional `gate`), `elevator` (cell, facing, `placement` id, `link`, `arrival_cell`), `light_states` (id, description, `applies_when` = a trigger id, `changes` = list of placement and state), `ambient` (sound-design note from `levels.md`). Optional: `side_quests` (accuracy side quest with its own scenes), `pace_signs`, `notes`.

## map.json

- `size_cells`, `floor` (row strings, one key char per cell) and `floor_legend` (char to kit floor entry).
- `placements`: `{id, entry | landmark, cell, offset?, state_set?, state?, art_gap?}`. `entry` is the entry drawn in the initial state and must exist in the district atlas or the Pace atlas. `state_set` names an atlas state set (door, lamp, ...) the placement belongs to and `state` its initial state; `entry` must be drawn in that state. Landmarks place the garden-style registered parts.
- **Art gaps.** A prop the atlas lacks is placed with `art_gap: true` and declared once in `art_gap_entries` (footprint cells and collision rows, layer, purpose, states). Gap state sets (a nook that appears) go in `art_gap_state_sets`. Each gap is a warning and must be listed in `NEEDS_ART.md` with its name in backticks. A gap that mirrors a piece the kit team has built on a branch that is not merged yet carries the kit's exact name and footprint, so nothing changes when it lands: the validator then warns that the gap exists in the atlas, and `--drop-solved-gaps <district>` removes the flags and declarations it covers.
- `collision`: row strings, `1` blocked and `0` walkable, for the initial state. It must equal exactly the union of every placement's footprint collision (state-set placements use the active state's entries, landmarks use their parts and lamps, art gaps their declared footprint) plus `implicit_walls` (`[x, y, w, h]` rects the camera never shows).
- `gates`: `{id, kind: door | shortcut, cells, opens_after (level id), placement?, visible_change}`. Gate cells start blocked and become walkable once the named level is complete. Route checks open a gate for any level whose number is greater than `opens_after`.
- `zones`: `{id, kind: hub | branch | task_room | corridor | review, rect: [x,y,w,h], level?}`.
- `interactions`: `{id, kind: npc | terminal | artifact | door | glitch | mira | elevator | sign, cells, marker: conversation | terminal | route | glitch | none, approach: [{cell, facing}], scene_id?, dialogue_id?, level?, requires?, npc?, placement?}`. `cells` is the footprint; `approach` is where the player stands and must be walkable and adjacent. `requires` entries are `level:<id>`, `seal:<id>`, `flag:<id>`, `artifact:<id>` or `mira:<route id>`. `visible_when` (free text) says when the interaction is active, for example `level:orientation-02` or `npc_state:ivo=north` (an NPC interaction that follows the NPC to a state's cell). A value starting `npc_state:` is checked: `npc_state:<npc id>=<state>` with an optional trailing `*` prefix match, naming an existing NPC and state. Route stops and checkpoint markers are `sign` interactions on walkable cells and need no `approach`.
- `npcs`: `{id, character, start_cell, facing, initial_state?, patrol?, poses_by_state, cells_by_state?}`. Pose names must exist in the character's atlas. State keys are NPC-local names; `initial_state` (default `start`) is the state the NPC holds at the start and must exist. A trigger switches state with `npc_state`; the game stores the current state per NPC in progress data. **Not present yet:** the reserved state `absent` is the first-class "NPC not in the district yet" state. Its pose is `null` (the only state allowed one), it has no cell, nothing is drawn and no interaction can show (`visible_when: npc_state:<npc>=absent` is rejected). An NPC may start `absent` (`initial_state: "absent"`), and then some level trigger must bring it in with an `npc_state` op, or the validator reports it. `start_cell` stays the cell where it first appears. Background workers on a shared walk clock use `patrol` and `patrol_clock: "shared"` until the state that drops the clock.
- `routes`: `main` (one segment per level: `from`, `to`, contiguous 4-neighbour `cells`; every cell needs a free 2 x 2 block unless the segment sets `min_width: 1`, only where `levels.md` allows), `backtrack` (the return route and any shortcut, with `after`), `mira` (route id to checkpoint cells).
- `spawns`: `{id, cell, facing, when}`.

## levels/NN-slug.json

`id` (`<district>-NN`), `number`, `title`, `district`, `kind` (`main` | `review`), `requires`, `story` (2 to 3 sentences), `steps`, `gestures`, `terminal_scenes`, `dialogue`, `triggers`, `state_changes`, `rewards`, `optional_artifact`, `glitch`, `pace_copy`, `review_notes` (the 1366 x 768 plus keyboard-inset note).

- `steps`: `{id, objective (action first), interaction (map id or null), completes_when}`.
- **Condition grammar** (`completes_when`, trigger `when`, dialogue `when`): atoms joined with ` & ` (all must hold). Atoms: `scene_success:<scene id>`, `dialogue_done:<id>`, `interact:<interaction id>`, `step_done:<step id>`, `step_start:<step id>`, `reach_cell:<x>,<y>`, `level_complete:<level id>`, `trigger:<id>`, `request:<dialogue id>`, `state:<start | level id | flag id>`, `player_confirm:<scene id>`, and two group atoms:
  - `any_of:<atom>|<atom>|...` holds when any one alternative holds, e.g. `any_of:scene_success:a|scene_success:b`.
  - `count:<n>:<atom>|<atom>|...` holds when at least `n` alternatives hold, e.g. `count:2:scene_success:a|scene_success:b|scene_success:c`.
  A group needs two or more alternatives, `n` is a positive integer no larger than the number of alternatives, groups do not nest, they never contain `request:`, and `&` joins a group to other atoms but never appears inside one.
  `dialogue_done:<id>` on a conversation line is met when the player continues past its last line (or skips); on an instruction line (below) it is met when the line's `hint.key` is observed.
  `request:<dialogue id>` means the player pressed the **Hint key** (Backtick, `event.code === 'Backquote'`) on the named line. It is only ever the whole `when` of an `on_request` line (see `dialogue`), never a step or trigger condition. In Violento it is honoured only during a gesture's introduction, and in a recall scene it costs that scene's third star (guided and variation scenes are unaffected).
- `gestures`: `{id (inventory id), phases: [guided | variation | recall], scene_id}`. One entry per gesture and scene.
- `terminal_scenes`: `{id, kind: editor | form | log | keypad | label | walk, task_summary, success_criteria, retry: "instant", position_cue, confidence?, task}`. `task` is the concrete definition a developer implements: for `label`, `form`, `editor`, `keypad` and `log` it needs one of `target`, `targets`, `items`, `steps` or `lines`. Keys used by Orientation: `prompt`, `initial`, `target`, `targets`, `items`, `accepts` (what output counts), `rejects` (what must not appear), `feedback` (per-failure messages that name the observed output), `layout`. A recall scene states `position_cue: false`. **Reserved keys:** `?` (Layout help) and Backtick (Hint) are commands in every typing scene, so no scene may require the player to type either. The validator rejects a backtick or `?` (or a key name such as `Backquote`, `Backtick`, `grave`) in a task's `target`, `targets`, `lines`, `accepts`, `items[].target` or `steps[].accepts`; prompts and questions shown to the player may still contain a question mark.
- `dialogue`: `{id, speaker, speaker_kind?, portrait, text, hint, when?, cue?, on_request?, modal?}`. `portrait` is the expression suffix: `neutral`, `concerned`, `pleased`, or the signature suffix (`laugh`, `grin`, `unimpressed`, `puzzled`, `softened`). The validator looks up `<speaker>_<portrait>` in `portraits-atlas.json`, so Noor's `noor_unimpressed` is written `unimpressed`. Choose the expression from the `levels.md` portrait cue map (`cue` records the row). Cards, signs and panels are object speakers with `portrait: null`. Every hint line is neutral. **Modes:** `modal` says whether a line is a conversation line (`true`: it owns Return = Continue and Esc = Skip and pauses the world) or an instruction line (`false`: it carries the step's action, takes no keys, leaves the world live and closes when the step's `completes_when` is met). When absent it defaults to `true` for a line with `hint: null` and `false` for a line with a hint; a line with a hint must not be `modal: true`. Orientation sets the flag explicitly on every line. **Hint key requests:** an `on_request: true` line answers a Hint key press; its `when` is exactly `request:<dialogue id>` and it must carry a hint (it repeats the hint). `request:` appears nowhere else. `hint` is `{action, key, gesture}` or `null`: `action` is the full first sentence ("To walk to the west desk, you need to press Left Arrow."), `key` the conventional key (it must appear in `action`), `gesture` the Kanata hint text after "Hint:". Copy hint lines from `levels.md`; never invent gesture claims.
- `triggers`: `{id, when, then: [ops]}` (`when` uses the condition grammar above, without `request:`). Ops: `set_state {target placement, state}`, `npc_state {npc, state}` (switches pose and, when `cells_by_state` has that state, the cell), `unlock_gate {gate}`, `light_state {light_state}`, `start_dialogue {dialogue}`, `spawn_glitch {interaction}`, `set_flag {flag}`, `complete_level {level}`, `grant {kind, id}`, `journal {text}`.
- `state_changes`: `{before, after, visible_changes}`. A main or review level lists at least two `visible_changes`, each `{kind: placement_state | landmark_state | npc_pose | light_state | gate, target, from?, to}` naming something that exists in the district.
- `rewards`: `seal`, `artifact`, `patch`, `desk_decoration`, `unlocks`. `optional_artifact`: `{id, name, interaction, placement?, caption (2 to 4 lines), engineer_portrait?}`. `glitch`: archetype (`stapler | chair | form`), `variant`, `cell`. `pace_copy`: signage lines with a Pace state (`default | repeat | optional`).
- No field may be named like a time limit (`time_limit`, `timeout`, `countdown`, `deadline`, `timer`, `seconds`, ...). Story levels are untimed.

## mira/NN-route.json

`id, name, district, available_after, skills_required, start_cell, checkpoints [{id, cell, task, scene_id, correction: "immediate, no penalty"}], destinations, medal_rule: "clean baseline then personal target, never gates story", reward_patch, desk_decoration, map_design_note`, plus the route's `terminal_scenes`, `gestures` and `dialogue`. The `id`, `available_after` and patch must match `world.json`; checkpoint cells must match `map.routes.mira` and be reachable.

## coverage.json

`{district, levels: {<level id>: {owned: [ids], gestures: {<id>: {guided, variation, recall}}}}, mira, uncovered: []}`. `owned` must equal the inventory rows whose `introduced_in` is that level. Each of `guided`, `variation`, `recall` is a scene id that the level, route or side quest claims for that gesture and phase in its `gestures` list; the variation scene comes after the guided scene and the recall scene after the variation scene (scene order is level number, then position in the level; Mira and side-quest scenes sort just after their level); the recall scene declares `position_cue: false`. Gestures flagged `external_only` need at least one scene but not three phases. `uncovered` must be empty.

## Rules every district satisfies

1. Each new-skill site follows hub, short branch, task room, changed return route. The elevator returns to unlocked districts; a locked door shows the seal it needs and a visible route back.
2. Story quests are untimed, have no speed threshold, no blind route and no OS shortcut the browser cannot observe; every route has a clear way home; the practice toggle-out instruction is visible in Night Shift.
3. A completed main quest changes at least two visible elements.
4. The main route from entrance to review is walkable (BFS over `collision`, with gates opened by earlier levels) and at least two cells wide.
5. Gesture ids exist in the inventory. Every gesture a level owns has guided, variation and recall.
6. `levels.md` is edited only by the Orientation team; other teams report contradictions.
