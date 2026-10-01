# AGENTS.md

## Project

Kanata Hero is a planned browser game that teaches the user's Kanata keyboard
layout through a top-down office adventure. No game code exists yet; this
repository currently holds design, level, and art-direction documents for a
later OpenSpec implementation. See `README.md` for the document map and which
file owns which topic.

## Tech stack (planned implementation)

- Plain HTML, CSS, and JavaScript — static assets, no backend, no framework.
- Canvas 2D for the layered sprite world; DOM/CSS for dialogue, editor scenes,
  and keyboard diagrams.
- `localStorage` for progress, settings, and best scores.
- Deterministic level/gesture schema, with an input interpreter kept separate
  from level rules, and a small state machine driving scenes.
- Full spec: `docs/game-design.md` (owns curriculum, gesture inventory,
  scoring, and hint grammar). Planning artifacts live under `openspec/`.

## Git conventions

- Never add a "Co-authored-by" (or any co-author) line to commit messages or
  PR descriptions, under any circumstance.
- Keep commit messages and PR descriptions brief.
- Use Conventional Commits for commit subject lines (e.g. `feat:`, `fix:`,
  `docs:`, `chore:`, `refactor:`).
- `main` is protected: always create a feature branch for any new feature or
  unit of work and open a PR; never work or commit directly on `main`.
