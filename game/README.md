# Kanata Hero game

Static browser game for level 1 (the Orientation hub and level 01 "The Lobby"). Plain HTML, CSS and JavaScript (native ES modules), no bundler, no runtime dependency. The module contracts are in [`CONTRACTS.md`](CONTRACTS.md); the plan is `openspec/changes/build-level-one/`.

## Run

The game reads data and art from `/design/**` and `/art-direction/**` by path, so serve the **repository root**:

```bash
python3 game/tools/serve.py          # or: cd game && npm run serve
# open http://127.0.0.1:8000/game/index.html
```

Any static server rooted at the repo root works (`python3 -m http.server`), but `serve.py` guarantees the MIME types for `.json`, `.png`, `.mjs`.

## Test

```bash
cd game && node --test tests/        # or: npm test (Node 20+, built-in runner, no dependencies)
```

## Layout

| Path | Owner |
| --- | --- |
| `src/shared/` | bus, clocks, errors, layout constants (contracts) |
| `src/engine/` | loader, atlas, renderer, camera, collision, actors (A) |
| `src/input/` | interpreter, bindings, calibration, layout manifest, hint gate (B) |
| `src/runtime/` | scene machine, rules, dialogue, evidence, progress (C) |
| `src/ui/`, `css/` | DOM components and styles (D) |
| `tests/`, `tools/` | tests and `serve.py` (F) |
