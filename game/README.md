# Kanata Hero game

Static browser game for level 1 (the Orientation hub and level 01 "The Lobby"). Plain HTML, CSS and JavaScript (native ES modules), no bundler, no runtime dependency. The module contracts are in [`CONTRACTS.md`](CONTRACTS.md); the plan and the final review are in `openspec/changes/build-level-one/` (`REVIEW.md`).

## Run

The game reads data and art from `/design/**` and `/art-direction/**` by path, so serve the **repository root**:

```bash
python3 game/tools/serve.py          # or: cd game && npm run serve   (add --port N to change 8000)
# open http://127.0.0.1:8000/game/index.html
```

Any static server rooted at the repo root works, but `serve.py` guarantees the MIME types for `.json`, `.png`, `.mjs` and sends `no-store`. A first visit shows setup and calibration (Esc skips both), then the arrival and Ivo. Progress is in `localStorage` under `kanata-hero:progress`; Settings, Reset progress clears it. `window.__kanataHero` exposes the running game for the browser checks.

## Boot

`src/main.js` exports `createGame({fetchFn, baseUrl, loadImage, clock, storage, headless})` (no canvas, DOM or `window` with `headless: true`; emits every `vm:*` topic; a `DataLoadError` becomes the `error` scene) and `bootBrowser()`, which adds the canvas renderer, the DOM UI, the window key listeners, the resize handler and the render loop. The stage is laid out at 1280x720 (x4); a larger world zoom (x6 at 1920x1080) scales the whole stage with CSS, the canvas backing store is `320 * zoom` wide.

## Test

```bash
cd game && node --test tests/        # or: npm test (Node 20+, built-in runner, no dependencies)
KH_FULL=1 KH_PY=/path/to/python node --test tests/checks/pipeline.test.js   # full art rebuild, needs Pillow, numpy, jsonschema
```

The only skipped test is the full art rebuild (it runs `art-direction/build_all.py`, normally about a minute, and needs the opt-in `KH_FULL=1`). `tests/e2e/level01.test.js` plays level 01 headlessly through `createGame` and the real data; `tests/e2e/integration.test.js` covers the mouse commands, the confirm-reset card, `vm:inset`, overlay stacking and the error scene.

## Browser checks (tasks 6.3, 7.1, 6.4)

1. Serve the repo root as above.
2. Open the page at 1366x768 and at 1920x1080 (Browser pane `resize_window`, or any browser window of that size). Play with the keyboard: Esc (skip setup), Return through Ivo, Esc (popup), `q`, `` ` ``, `?`, the arrows for the lap and the desks, `w e s t` at the west desk, the recall walk.
3. Checklist: no console error; the avatar and the current target are outside the keyboard inset (an edge arrow stands in for a covered or off-stage target); recall shows no inset and no markers; the turnstile, Ivo's nod and the gold markers show after completion.
4. Screenshots are in `tests/e2e/screenshots/` (JPEG, 800 px wide, as the Browser pane delivers them). `tools/browser-check.mjs --model-only` runs the same inset model without a browser; its live half needs Playwright, a dev-only tool that is not installed here.
5. A hidden browser pane throttles `requestAnimationFrame` to about 1 fps; keep the page visible when driving it.

Accessibility results: `tests/checks/ACCESSIBILITY.md`.

## Layout

| Path | Owner |
| --- | --- |
| `src/shared/` | bus, clocks, errors, layout constants (contracts) |
| `src/engine/` | loader, atlas, renderer, camera, collision, actors (A) |
| `src/input/` | interpreter, bindings, calibration, layout manifest, hint gate (B) |
| `src/runtime/` | scene machine, rules, dialogue, evidence, progress, inset view-model (C) |
| `src/ui/`, `css/` | DOM components and styles (D) |
| `tests/`, `tools/` | tests and `serve.py` (F) |

## Known gaps (owners)

- `map.json` npc `relaxed` states name poses the cast atlases lack (`bgworker_a_idle_phone_s`, `bgworker_b_idle_coffee_s`): art (cast atlases); not used by level 01.
- The level sheet says no keyboard-inset conflict exists; the camera model puts the lap marker (3,12) and the west desk (7,10) under the inset: level data owner may update `LEVEL_SHEET.md`. The game handles it with an edge arrow.
- No continue prompt on reload (the game resumes directly): follow-up in REVIEW.md.
