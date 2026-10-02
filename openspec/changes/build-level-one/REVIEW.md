# Final review: build-level-one (task 7.4)

Reviewed on branch `feat/game-integration`. Evidence: `cd game && node --test tests/` ends `tests 312, pass 311, fail 0, skipped 1, todo 0` (the one skip is the opt-in full art rebuild); `design/levels/validate_levels.py --all` ends `0 errors, 0 warnings`; browser run at 1366x768 and 1920x1080 with screenshots in `game/tests/e2e/screenshots/` (JPEG). Accessibility rows: `game/tests/checks/ACCESSIBILITY.md`. Result key: pass, partly, fail.

Not verified: `art-direction/build_all.py` (task 6.5 final line). `build_glitches.py`, step of that script, ran for 27 minutes at 100 percent CPU with no output and again exceeded 150 s on its own; both runs were stopped and the tree was left clean. Nothing in `art-direction/` was touched by this branch. See follow-up F1.

## game-ui

| Requirement / Scenario | Result | Evidence |
| --- | --- | --- |
| The UI follows the UI kit | pass | `tests/ui/css.test.js`, `tests/checks/a11y.test.js`; screenshots `setup-*`, `journal-*`, `layout-help-*`, `settings-*` compared with `art-direction/ui-kit/screens/*.png` (setup and calibration are one panel as in the kit) |
| Scenario: Token use | pass | `tests/ui/css.test.js` (no colour literals, kit tokens only) |
| Instructions use the hint grammar | pass | `tests/ui/components.test.js` (hint line text); `popup-1366x768.jpg`, `lap-leg1-edge-arrow-*.jpg` show action, key, "Hint: ..." |
| Scenario: Ivo's lap instruction | pass | dialogue text from level data; `tests/ui` lap line test; `lap-in-progress-*.jpg` |
| The keyboard inset teaches position, hold order, output and effect | partly | four cells on guided and variation scenes (`tests/e2e/integration.test.js` vm:inset test, `lap-*.jpg`); never covers the avatar (`tests/checks/inset.test.js`); current target shown as an edge arrow when covered or off the stage. The kit's first-use behaviour (opens once per binding, closes on first output) is not built: the inset stays open for the whole scene (F2) |
| Scenario: Recall scene | pass | e2e `recallInset === null`, `recallFloorMarkers === 0`; `recall-no-inset-no-markers-*.jpg` |
| Layout help is rendered from the layout manifest | pass | `tests/input/layout-manifest.test.js`, `tests/ui/screens.test.js`; all four tabs and both variants in `layout-help-*.jpg`; fits at 1366x768 with a card open on every key (measured, 0 px overflow) |
| Scenario: Manifest drives the screen | pass | `tests/ui/screens.test.js` (changing a manifest entry changes the legend) |
| Accessibility and display | pass | ACCESSIBILITY.md rows 1 to 20 |
| Scenario: Reduced motion | pass | `tests/engine/animation.test.js`, `world.test.js`; Settings toggle reaches the world (`integration.test.js`) |
| Scenario: Screen reader | pass | `#live` shows "Objective: ..." after each step (page); `tests/ui/mount.test.js` |
| Sound is out of scope and off | pass | `tests/skeleton.test.js`, `a11y.test.js` (no Audio API) |
| Scenario: Fresh load | pass | no audio element in the page |

## world-runtime

| Requirement / Scenario | Result | Evidence |
| --- | --- | --- |
| The game loads level data and art as static files | pass | `tests/engine/loader.test.js`; page loads from `python3 game/tools/serve.py` |
| Scenario: Cold start | pass | setup screen appears; no console error in the final runs |
| Scenario: Missing file | pass | `integration.test.js` (removed kit entry gives the error scene naming the map file, kind `shape`; missing `world.json` names it, kind `missing`); `pipeline.test.js` negative test |
| Fixed logical view with integer zoom | pass | `tests/engine/renderer.test.js`; stage `scale(1.5)` at 1920x1080 with a 1920 px backing store, no scaling at 1366x768 |
| Scenario: Laptop size | pass | `setup-1366x768.jpg`, `lap-*-1366x768.jpg` |
| Scenario: Window resize | pass | live resize 1366 to 1920 in the page kept the avatar cell and the open layers; `renderer.test.js` |
| Layered rendering in the style-bible order | pass | `renderer.test.js` layer order and y-sort tests |
| Scenario: Actor behind and in front of a prop | pass | `renderer.test.js` (avatar after Ivo below him) |
| Scenario: State change | pass | `world.test.js`; `world-changes-after-completion-*.jpg` (turnstile lane lit) |
| Camera follows the avatar inside the bounds | pass | `tests/engine/movement.test.js`, `tests/ui/inset-route.test.js` |
| Scenario: Near a map edge | pass | clamped camera on the west walkway in `lap-leg1-edge-arrow-*.jpg` |
| Per-cell collision from level data | pass | `world.test.js`, `movement.test.js` |
| Scenario: Wall and prop / Gate opens | pass | `world.test.js` gate tests; turnstile lane walkable after completion |
| Avatar and character animation follow the atlas contract | pass | `tests/engine/animation.test.js` |
| Scenario: Walking a cell | pass | `movement.test.js` (16 steps per cell, aligned) |
| A small scene state machine drives play | pass | `tests/runtime/machine-scenes.test.js` |
| Scenario: Open and close Layout help | pass | `machine-scenes.test.js`; e2e `layoutHelpRoundTrip` |
| Level rules run from level data only | pass | `tests/runtime/rules.test.js`, `scenario.test.js` |
| Scenario: Level 01 completes | pass | e2e world-changes test; `level-complete-glitch-appears-*.jpg` |
| Progress persists locally | pass | `evidence-progress.test.js`; reset by mouse in the page returned to setup |
| Scenario: Reload mid-level | partly | step, avatar and world state restore (e2e reload tests, page reload); the game resumes directly, there is no "continue" prompt (F3) |
| Scenario: Storage blocked | partly | in-memory fallback and one warning toast (`evidence-progress.test.js`, e2e blocked storage); the toast was not seen in the page |

## input-interpretation

| Requirement / Scenario | Result | Evidence |
| --- | --- | --- |
| The interpreter is independent of level rules | pass | `tests/input/interpreter.test.js` (no level imports) |
| Scenario: Same output, different routes | pass | `interpreter.test.js` |
| Observed output is never presented as detected gesture | pass | feedback shows "Output observed" and names the output only (`popup-wrong-output-*.jpg`); `hint-gate.test.js` confidence labels |
| Scenario: Held Space demonstration | partly | no level 01 scene needs it; the calibration vm carries `confirmable` (false: every calibration gesture is observable) and the UI has the control; `playerConfirm` routing exists in the interpreter but nothing in level 1 exercises it (F4) |
| Decided key bindings | pass | `tests/input/bindings.test.js`, one test per row of `design/ui-key-bindings.md` |
| Scenario: Journal key in a typing scene | pass | `bindings.test.js`, `machine-scenes.test.js` (label scene) |
| Scenario: Esc in the open world | pass | `evidence-progress.test.js` |
| Browser behaviour is scoped and escapable | pass | `interpreter.test.js` preventDefault tests; real Tab and Esc runs (ACCESSIBILITY rows 10, 11) |
| Scenario: Tab outside a practice region | pass | Tab in the hub moved focus stage, Journal chip, Layout help chip, stage |
| Calibration proves the setup without claiming detection | pass | `tests/input/calibration.test.js`, `integration.test.js` (diagram, Return on step 2, mouse step choice); `calibration-1366x768.jpg` |
| Scenario: Observed step | pass | "Observed output" chips in `calibration-1366x768.jpg` |
| Scenario: Skipped step | pass | `calibration.test.js`, `integration.test.js` |
| Hint use is recorded | pass | `hint-gate.test.js`, e2e stars test |
| Scenario: Hint in a guided scene | pass | `machine-scenes.test.js`; in the page the Hint key re-showed the instruction |
| Scenario: Hint in a recall scene | pass | e2e `hintCard.text` and two stars |

## level-one-experience

| Requirement / Scenario | Result | Evidence |
| --- | --- | --- |
| Setup and calibration come first | pass | `evidence-progress.test.js`; `setup-*.jpg` |
| Scenario: First visit | pass | e2e first scene is setup; page |
| Scenario: Returning player | partly | goes straight to the hub, no continue prompt (F3) |
| Arrival from the north-wall elevator | pass | e2e elevator closed, half, open, half state about 120 ms; `arrival-1366x768.jpg` |
| Scenario: New game | pass | avatar on the mat facing south, `o01.d.welcome` shows (`welcome-*.jpg`) |
| The hub is walkable and readable | pass | walked the lobby in the page at both sizes; inset check |
| Scenario: Walk the lobby | pass | `tests/checks/inset.test.js` strict (avatar never under the inset; target shown clear of it); `lap-*.jpg` |
| Level 01 plays through its steps in order | pass | e2e scenario (setup skip to recall) and the page played end to end at 1920x1080 with 3 stars |
| Scenario: Popup | pass | `popup-*.jpg`, e2e |
| Scenario: Wrong direction | pass | `machine-scenes.test.js`, e2e sloppy run (one star) |
| Scenario: Desk label | pass | `label-*.jpg`, `label-wrong-output-1366x768.jpg` |
| Scenario: Unprompted recall | pass | `recall-*.jpg`, e2e |
| Level 01 changes the world | pass | e2e (turnstile open, gate open, Ivo nod, gold markers, journal); `world-changes-after-completion-*.jpg` shows lit lane, nodding Ivo, gold check markers |
| Scenario: After the recall walk | pass | e2e; `journal-level-done-1366x768.jpg` |
| Optional glitch repair is harmless and untimed | partly | covered by `scenario.test.js` and `world.test.js` (snap frame, ordinary prop); the repair scene was not played in the page (F5) |
| Scenario: Repair | partly | as above |
| Evidence and stars for level 01 | pass | `evidence-progress.test.js`, e2e three star outcomes; page run gave 3 stars |
| Scenario: Clean recall without a hint | pass | e2e stars test |
| Level 01 can be left and resumed | pass | journal, Layout help, Controls and Settings opened and closed in the page; reload restored the level |
| Scenario: Layout help mid-level | pass | e2e `layoutHelpRoundTrip` |

## Follow-up tasks

- F1: run `art-direction/build_all.py` (44 steps) on a machine where `build_glitches.py` finishes, and report the final line. Owner: art pipeline.
- F2: first-use inset behaviour (open once per binding, close on first output or Esc, Hint reopens it). Owner: runtime and UI.
- F3: continue prompt on reload (the spec text allows "the hub or the continue prompt"; the world-runtime scenario says "offers to continue"). Owner: runtime and UI.
- F4: a level that uses a player-confirm control (held Space, held Tab) will need the confirm row wired from the scene; level 01 has none. Owner: levels 02 and later.
- F5: play the glitch repair scene in the page and add a screenshot. Owner: QA playtest (task 7.2).
- F6: task 7.2, the playtest on a real keyboard with the player's Kanata config, is not done; the `Backquote` code fallback and the Hint key were only driven with a test driver that sends no `code`.
- F7: the level sheet claims no inset conflict; update it (lap marker (3,12) and west desk (7,10) are covered by the inset in the camera model). Owner: level data.
