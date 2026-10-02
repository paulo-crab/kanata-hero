# Proposal

## Why

Kanata Hero has complete design, art and level data but no game code. Level 1 (the Orientation hub and level 01 "The Lobby") is the smallest piece that proves the engine, the input interpreter, the UI layer and the art working together, and it exposes the integration risks early. All inputs now exist: the rich-finish atlases, the UI kit, validated level data, the layout manifest and the key bindings.

## What Changes

- Add a static browser game under `game/`: plain HTML, CSS and JavaScript, no backend and no framework, served as static assets.
- Add a world runtime: level-data loader, atlas loader, layered Canvas 2D renderer at a fixed 320x180 view with integer zoom, camera, per-cell collision, actors and animation.
- Add an input interpreter, separate from level rules, that turns browser key events into observed outputs with confidence labels, applies the decided key bindings and drives the calibration.
- Add a scene state machine and level-rule runtime: setup, calibration, arrival, hub, dialogue, walk and form scenes, trigger and state-change execution, localStorage progress.
- Add the DOM/CSS UI layer built from the UI kit: dialogue panel with portraits, keyboard teaching inset, HUD, interaction prompt, markers, journal, Layout help rendered from the layout manifest, setup and calibration screen, confidence feedback, Controls.
- Deliver level 1 end to end: setup and calibration, arrival from the north-wall elevator, the walkable Orientation hub, level 01 with Ivo (popup, four-arrow loop, four stops, desk label, unprompted recall walk, optional folded-form glitch), world changes after the level.
- Add automated tests (headless unit tests for the interpreter, loader, collision and rules; browser checks at 1366x768 and 1920x1080 with the keyboard inset open; accessibility checks).
- Recorded decisions: the default camera is the fixed 320x180 view (427x240 is a later optional setting); using the Hint key in a recall scene forfeits the third star; Violento is out of scope; sound is out of scope and stays off.

Non-goals: levels 02 to 20 as playable quests (their data exists but is not loaded), Mira routes, the elevator map beyond the Orientation stop, Violento mode, sound, export and import of progress, other districts' art.

## Capabilities

### New Capabilities

- `world-runtime`: data loading, rendering, camera, collision, actors, scene state machine, level-rule execution, progress persistence.
- `input-interpretation`: browser key events to observed outputs with confidence, key bindings, calibration, reserved keys and the practice-layer honesty rules.
- `level-one-experience`: what the player sees and can do from first load through level 01 and its world changes.
- `game-ui`: the DOM/CSS layer, Layout help from the manifest, accessibility and display requirements.

### Modified Capabilities

None. The existing art capabilities (`art-asset-handoff`, `environment-kit`, `character-sprites`, `ui-presentation`) are consumed unchanged; any gap found while building goes back to the art or level teams.

## Impact

- New top-level folder `game/`; no existing file changes except `README.md` (document map row) and `AGENTS.md` only if the run instructions are added.
- Reads, never edits: `art-direction/**` atlases and `ui-kit` tokens, `design/levels/**`, `design/layout/layout-manifest.json`, `design/ui-key-bindings.md`.
- Keeps `art-direction/build_all.py` (44 steps) and `design/levels/validate_levels.py --all` green.
- Dev-only tooling: Node (v26 present) for the test runner; no runtime dependency is added.
