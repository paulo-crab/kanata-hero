# Tasks

Workstreams own disjoint folders: **A** `game/src/engine/`, **B** `game/src/input/`, **C** `game/src/runtime/`, **D** `game/src/ui/` and `game/css/`, **F** `game/tests/` and `game/tools/`. Group 1 (contracts) must finish before groups 2 to 6 start; groups 2 to 5 run in parallel on separate feature branches; group 6 verifies; group 7 integrates. Each task states how to verify it.

## 1. Contracts and skeleton (one session, first)

- [ ] 1.1 Write `game/CONTRACTS.md`: module interfaces and event shapes for engine, input, runtime and ui (interpreter event `{output, text, confidence, repeat, t}`, scene interface `enter/handle/update/exit` with owned keys, rule-runtime intents, UI view-models, progress document shape, fake-clock hooks). Verify: each requirement of the four specs maps to at least one named interface; reviewed by the producer.
- [ ] 1.2 Create `game/index.html`, `game/css/`, empty module folders with an `index.js` per module exporting its contract stub, `game/package.json` (dev-only: scripts `test`, `serve`), and `game/README.md` (how to serve from the repo root). Verify: `node --test` runs and passes on the stub; the page loads from `python3 -m http.server` with no console errors.
- [ ] 1.3 Add `game/tools/serve.py` (static server rooted at the repo, correct MIME types for `.json`, `.png`, `.mjs`). Verify: `curl` returns the Orientation `map.json` and an atlas PNG with the right types.

## 2. Engine (workstream A)

- [ ] 2.1 Data loader: fetch and parse the Orientation `district.json`, `map.json`, level 01 JSON, `world.json`, gesture inventory and manifest; fail with a message naming the file. Verify: unit tests with good and broken fixtures; the real files load.
- [ ] 2.2 Atlas loader and animation player for kit, cast, glitch, Pace and portrait atlases per `ART_HANDOFF.md` section 3 (frames, anchors, state sets, play modes, reduced-motion hold). Verify: a test renders frame indices for `ivo_wave_s`, `engineer` walk and `elevator` closed/half/open from the real JSON.
- [ ] 2.3 Canvas renderer at 320x180 with integer zoom, letterbox, nearest-neighbour, the style-bible layer order, y-sorting, contact shadows and state-set drawing; DOM stage at 1280x720. Verify: screenshot of the Orientation hub at 1366x768 matches `art-direction/kit/orientation-review-room-1366x768.png` composition; resizing across x4/x6 keeps state.
- [ ] 2.4 Camera with feet at (160,100) and clamp to `camera_bounds`; collision grid from `map.json` plus gate states; grid-stepped movement with held-key repeat and fixed timestep. Verify: unit tests for walls, gates, edges and determinism (same script, same positions).
- [ ] 2.5 Actors: avatar, Ivo, Mira, background workers (sync loop), glitch roaming with the repaired snap frame, ordinary-prop swap. Verify: a scripted walk renders the four directions; the glitch repair sequence plays snap then prop.

## 3. Input interpreter and calibration logic (workstream B)

- [ ] 3.1 Interpreter: `KeyboardEvent` to logical outputs with confidence labels from the manifest, no layer or physical-key claims, `preventDefault` only on the active play surface, Tab never trapped. Verify: tests with recorded event sequences for Caps + H (ArrowLeft), tap Caps (Escape), Return, typed letters, reserved keys.
- [ ] 3.2 Key bindings table from `design/ui-key-bindings.md` as data, scene-aware (Return by state, Esc rules, Q only in the world, Backtick as Hint, `?` for Layout help) with the reserved-text rule. Verify: tests for every row of the bindings table, including Q typed in a label scene and Esc in the open world.
- [ ] 3.3 Calibration engine for the five steps, statuses `not started`, `observed output`, `skipped`, skip-one and skip-all, keyboard type (MacBook, Microsoft Alt as Command and Windows as Option). Verify: scripted runs for all-observed, partial skip and full skip; stored result round-trips.
- [ ] 3.4 Layout manifest consumer: query keys, layers, tap and tap-hold, XX silence, keyboard variant, per-gesture verification. Verify: tests asserting every manifest key id used by the UI tabs resolves; `generate_manifest.py --check` still passes.
- [ ] 3.5 Hint-use recording and the recall-scene star-forfeit card contract. Verify: unit tests for guided (no loss) and recall (loss after confirmation).

## 4. Scenes and level rules (workstream C)

- [ ] 4.1 Scene state machine: setup, calibration, arrival, hub, dialogue (modal and non-modal), walk scene, label and form scenes, editor (glitch) scene, Layout help, journal, Controls, error; key ownership per scene; focus restore on return. Verify: transition table tests; open and close Layout help leaves hub state unchanged.
- [ ] 4.2 Rule runtime: trigger atoms (`step_start`, `reach_cell`, `scene_success`, `dialogue_done`, `request`, `any_of`, `count`, `visible_when`), operations (set state, NPC state, unlock gate, rewards), fail-on-unsupported at load. Verify: tests over level 01's real triggers; unsupported op fails the load.
- [ ] 4.3 Scene kinds used by level 01: `form` (popup), `walk` (lap, four stops, unprompted recall with markers off), `label` (west desk), `editor` (folded-form glitch repair, untimed, instant retry). Verify: scripted headless play of each scene's success and wrong-input paths against the real level data.
- [ ] 4.4 Dialogue runtime with Ivo's flow (greeting, instruction lines, hint on request, success, world change), modal versus non-modal ownership of Esc and Return, portrait cues from the data. Verify: the dialogue order test against `design/levels/SLICE.md` level 01 table.
- [ ] 4.5 Evidence and stars: per gesture and phase evidence, hint use, clean-run measure (every task-critical output correct and at least 95 % of actions correct), stars 1/2/3 with the recall-without-hints rule. Verify: tests for the three star outcomes.
- [ ] 4.6 Progress store: one versioned `localStorage` document, ids from `world.json`, continue prompt, reset with confirmation, in-memory fallback. Verify: tests with a throwing storage; reload mid-level restores the step and world state.
- [ ] 4.7 World changes after level 01: turnstile open, Ivo nod, garden markers teal to gold, mailroom gate unlock, journal entry. Verify: scenario test asserts all four state changes and that at least two are visible in a screenshot.

## 5. UI layer (workstream D)

- [ ] 5.1 Tokens and base: import `art-direction/ui-kit/tokens.css` by reference, stage 1280x720, z-layers, focus ring, live region. Verify: stylesheet lint shows kit tokens only; screen-reader live region announces an objective change.
- [ ] 5.2 Components: keycap, dialogue panel with portraits, HUD, interaction prompt, markers (four shapes), keyboard teaching inset (four cells, guided and variation only, avoids avatar and target). Verify: screenshots at 1366x768 compared with the kit's reference renders; inset never overlaps avatar or target in the level 01 route.
- [ ] 5.3 Setup and calibration screens, Controls screen, first-use inset, confidence feedback, toast. Verify: screenshots match `ui-kit/screens/*.png` structure; skip paths reachable by keyboard.
- [ ] 5.4 Layout help rendered from the manifest: four tabs, MacBook and Microsoft variants, key detail card, XX keys, toggle-out sequence, emergency exit shown as unverified, keyboard-only navigation. Verify: a DOM test that changing a manifest entry changes the legend; the existing `design/layout` consistency check still passes.
- [ ] 5.5 Journal (main, optional, Mira headings; level 01 state, "Ride to the hub" row), HUD seal count, artifact frame not needed. Verify: screenshot of journal with level 01 active and done.
- [ ] 5.6 Settings: reduced motion (OS and setting), larger text, high contrast, reset progress with confirmation, keyboard type; no audio controls. Verify: toggling each setting changes the rendered output; no audio element exists.

## 6. Verification (workstream F, starts with group 2)

- [ ] 6.1 Test harness: `node --test` entry, fake clock, scripted input player, fixtures from the real data. Verify: `npm test` green on the stubs, then on every merged group.
- [ ] 6.2 Headless level 01 scenario: recorded input script plays setup skip, arrival, popup, lap, four stops, label, recall, world changes, with stars asserted. Verify: passes deterministically twice.
- [ ] 6.3 Browser checks at 1366x768 and 1920x1080 with the keyboard inset open: screenshots of arrival, lap, label, recall, Layout help; assertion that the avatar and current target are outside the inset rectangle (the level data's camera model). Verify: committed screenshots and a passing check; failures list the cell.
- [ ] 6.4 Accessibility pass: focus order, no keyboard trap, reduced motion, high contrast, larger text, live-region announcements, contrast against kit tokens, 16 px minimum text. Verify: a written checklist with results; failures filed as tasks.
- [ ] 6.5 Pipeline guard: confirm `art-direction/build_all.py` (44 steps) and `design/levels/validate_levels.py --all` still pass and that the game fails to load when an atlas name from the level data is removed. Verify: both commands green; the negative test fails as expected.

## 7. Integration and release

- [ ] 7.1 Integrate the four workstream branches in dependency order (engine, input, runtime, ui), resolve contract drift in `CONTRACTS.md`, and run the headless scenario and browser checks. Verify: groups 6.2 and 6.3 pass on the integrated branch.
- [ ] 7.2 Playtest level 01 from a cold start on a real keyboard with the player's Kanata config (MacBook), record issues. Verify: a playtest note listing each step passed, skipped or broken.
- [ ] 7.3 Documentation: add the `game/` row to the README document map, run instructions to `game/README.md`, and note any art or level-data gaps found back to their owners. Verify: README link resolves; gaps listed with owners.
- [ ] 7.4 Final review against the four specs (each requirement and scenario checked). Verify: a checklist in the change folder with pass or fail per scenario; unresolved items become follow-up tasks, not silent gaps.
