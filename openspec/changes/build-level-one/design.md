# Design

## Context

All inputs exist and are validated: level data (`design/levels/**`, schema 0.2, `validate_levels.py`), atlases and JSON (rich finish, `ART_HANDOFF.md` formats), the UI kit (`tokens.css`, `COMPONENTS.md`, `reference.html`, rendered screens), the layout manifest (`design/layout/layout-manifest.json`) and the key bindings (`design/ui-key-bindings.md`). There is no game code. The project rules (`AGENTS.md`, `docs/game-design.md` "Browser behavior"): plain HTML, CSS and JavaScript, static assets, no backend, no framework; Canvas 2D for the world, DOM/CSS for dialogue, editor scenes and keyboard diagrams; `localStorage`; a deterministic level schema; an input interpreter separate from level rules; a small state machine. See proposal.md for scope.

## Goals / Non-Goals

**Goals:**
- A game whose behaviour is decided by the data files, so levels 02 onward are data work plus new scene kinds, not engine rewrites.
- Pure, testable logic: interpreter, collision, rule runtime and progress run without a browser.
- Four teams can work in parallel in disjoint folders against written module contracts.

**Non-Goals:**
- A bundler, a framework, TypeScript, or a runtime dependency.
- Generalising scene kinds that level 01 does not use (`keypad`, `log`, held-Space and held-Tab scenes) beyond leaving clear extension points.
- Mobile or touch input.

## Decisions

1. **Layout.** `game/index.html`, `game/css/`, `game/src/{engine,input,runtime,ui}/`, `game/tests/`, `game/CONTRACTS.md`. Native ES modules, no bundler. The game is served from the repository root (`python3 -m http.server` or any static server) and reads data and art from `/design/**` and `/art-direction/**` by path; a later packaging step may copy them into a `dist/`. Alternative: copy assets into `game/assets` now. Rejected: it duplicates generated files and drifts from the art pipeline.
2. **Module boundaries (contracts first).** `engine` (loader, atlas, renderer, camera, collision, actors) knows nothing about keys or levels. `input` turns `KeyboardEvent` into `{output, text, confidence, repeat, t}` events and hosts calibration logic. `runtime` (scene machine, rule runtime, progress) consumes interpreter events and level JSON and emits intents (`move`, `say`, `setState`, `openScene`) to engine and UI through a small event bus. `ui` renders DOM components from runtime state. A written `game/CONTRACTS.md` (task group 1) fixes these interfaces before the parallel work starts.
3. **Fixed-timestep simulation with an injectable clock.** Update at a fixed 60 Hz step from `requestAnimationFrame` accumulation; tests drive the same step with a fake clock and scripted events. Movement is grid-stepped: a held arrow repeats cell steps, a cell step takes two walk frames per 8 px (16 px in 266 ms), alignment to the cell grid after every step. Alternative: free pixel movement with swept collision. Rejected: the data, routes and checks are all per cell and the style rule is deliberate foot placement.
4. **Level data is loaded raw and validated lightly at runtime.** `validate_levels.py` is the authority in CI; the browser loader checks only structure it needs (ids resolve, atlas names exist) and fails loudly. No second schema implementation.
5. **Rule runtime implements the schema's trigger atoms** (`step_start`, `reach_cell`, `scene_success`, `dialogue_done`, `request`, `any_of`, `count`, `visible_when`) and operations (set state, set NPC state, unlock gate, award). Unsupported operations used by loaded levels fail the load, so extending to level 02 is explicit.
6. **Interpreter honesty.** Outputs are keyed by `KeyboardEvent.key` (not `code`) because Kanata changes what the browser sees; physical position is never inferred. `Esc` from tap Caps and arrow keys from Caps + H, J, K, L arrive as ordinary events. Confidence labels come from the layout manifest's per-row verification (`observed`, `player_confirmed`, `external_only`).
7. **UI is hand-written DOM and CSS from the kit's reference markup.** `ui-kit/reference.html` and `kit_screens*.py` are the visual contract; components copy their structure and tokens. Layout help is generated from the manifest, not copied from the kit's drawings, and the existing consistency check keeps them aligned. A live region announces objectives and instructions.
8. **Progress.** A single JSON document under one `localStorage` key plus a schema version; keys and ids come from `world.json`. In-memory fallback when storage throws.
9. **Verification.** Node's built-in test runner (`node --test`) for unit and scenario tests (a recorded input script plays level 01 headlessly against the rule runtime). Browser checks (screenshots at 1366x768 and 1920x1080, inset overlap, focus order, axe-style contrast via the kit's tokens) use headless Chrome through Playwright as a dev-only tool, not a runtime dependency; if Playwright is rejected, the same checks run through the Browser pane manually and are recorded. `art-direction/build_all.py` and `validate_levels.py --all` stay green.
10. **Camera default.** 320x180 at integer zoom is the only view; 427x240 is deferred to a later setting (decided by the player).

## Risks / Trade-offs

- **Kanata timing in the browser.** Tap-hold Caps + N and others depend on the player's real config; the game only sees outputs. Mitigation: calibration with skip, observed-output wording, no timing in story scenes.
- **Browser capture.** Some keys (Tab, Command combos) are intercepted. Mitigation: bindings avoid them; a Tab practice region is out of this build.
- **Parallel integration.** Four teams on one contract can drift. Mitigation: `CONTRACTS.md` first, a shared fake-clock scenario test that exercises the whole stack, and a weekly-style integration task at the end of each group.
- **Data and art coupling.** Level data names atlas entries and footprints; the rich-finish re-render must not change them. Mitigation: `validate_levels.py --all` is in `build_all.py`; the game's loader fails on unknown names.
- **Scope creep.** Level 01 data already contains items for later levels (turnstile gate, Morning Mail introduction). They load but are inert until their levels are built.

## Open Questions

None blocking. Decided with the player: scope is level 1 only, the camera is 320x180, the work is split into parallel teams, Hint costs the third star in recall scenes only, Violento and sound are out. To confirm during build: whether Playwright is acceptable as a dev dependency (default yes).
