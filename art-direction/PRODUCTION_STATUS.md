# Kanata Hero — art production status

This is the living handoff file. Any agent continuing the art work should read this first, then [STYLE_BIBLE.md](STYLE_BIBLE.md) and the approved specs listed below. Update it after every approval.

**Authority.** Since 2026-10-02 the player has delegated every art-direction decision and gate approval to the art director. The director self-reviews: automated checks, then a coordinator review, plus a Sonnet validator pass when useful. When the review passes, the director approves, records the result, and moves on. Never mark something approved unless its review passed.

**Goal.** Finish the game's art design and hand it off as assets and documentation that developer agents can build from.

## How the pipeline works

1. Read the brief in `design/characters/<name>.md`, or the relevant district section of `levels.md` and `docs/game-design.md`.
2. Optionally get specialist reviews (character, style). Then decide the open points and record them as Director decisions in the asset spec.
3. Hand-place pixels as key grids in a `*_sprites.py` module: `PAL`, `SLOTS`, `IDLE`, `WALK`, and optionally `GLINT_LIMITS` and `HAIR_SKIN_SEPARATED`. Shared leg poses and `lower()` live in `gate1/engineer_sprites.py`.
4. Check with `python3 art-direction/gate1/check_gate1.py <module>`. It tests frame size, row 23, anchor balance, marker colours and violet, the teal saturation limit, head keys, the contour-only darkest step, hair against skin, glint counts and the stride edge.
5. Build:
   - `cd art-direction/cast && python3 build_cast.py <name>` writes the sheet, the atlas PNG and JSON, and the walk GIF.
   - `cd art-direction/gate1 && python3 build_gate1.py` writes the review room.
6. Review the renders at ×8 and in the room at ×4, fix what fails, write `<NAME>_SPEC.md`, and record the decisions in the brief and the README decisions log.

**Python environment.** The scripts need Pillow and numpy. This session used a throwaway virtualenv. Recreate it with `python3 -m venv .venv && .venv/bin/pip install pillow numpy`.

## Approved

| Asset | Spec | Pixels | Approved |
| --- | --- | --- | --- |
| Style foundation (scale, palette, rules) | STYLE_BIBLE.md, README decisions | — | 2026-10-01 |
| Engineer: idle ×4, walk ×4 | [gate1/GATE1_ENGINEER_SPEC.md](gate1/GATE1_ENGINEER_SPEC.md) | gate1/engineer_sprites.py | 2026-10-02 (player) |
| Orientation review room, the environment quality bar | gate1 spec, "Scene" | gate1/environment.py | 2026-10-02 (player) |
| Ivo: idle ×4, walk ×4 | [cast/IVO_SPEC.md](cast/IVO_SPEC.md) | cast/ivo_sprites.py | 2026-10-02 (player) |
| Mira: idle ×4, walk ×4 | [cast/MIRA_SPEC.md](cast/MIRA_SPEC.md) | cast/mira_sprites.py | 2026-10-02 (director) |
| Pace: wayfinding icon and signage (18 pieces) | [pace/PACE_SPEC.md](pace/PACE_SPEC.md) | pace/pace_art.py | 2026-10-02 (director) |
| UI kit: tokens, contrast check, components, reference page | [ui-kit/UI_KIT_SPEC.md](ui-kit/UI_KIT_SPEC.md) | ui-kit/tokens.css, ui-kit/reference.html | 2026-10-02 (director) |
| District palettes (Records, Systems, Night Shift, Executive) and Noor/Hal/Ada/Vale skin and hair ramps | [palettes/PALETTES_SPEC.md](palettes/PALETTES_SPEC.md), STYLE_BIBLE §3 | palettes/district_palettes.py | 2026-10-02 (director) |
| Background workers: 2 bodies × 3 palettes, synced walk, idle variants, silhouettes | [cast/BACKGROUND_WORKERS_SPEC.md](cast/BACKGROUND_WORKERS_SPEC.md) | cast/bgworker_{common,a_sprites,b_sprites}.py | 2026-10-02 (director) |
| Orientation kit: 48-entry tile/prop atlas, JSON schema, garden before/after, room rebuilt from layout (zero diff) | [kit/ORIENTATION_KIT_SPEC.md](kit/ORIENTATION_KIT_SPEC.md) | kit/kitlib.py, kit/orientation_kit.py | 2026-10-02 (director) |
| Extra sets for the Engineer, Ivo and Mira: interact, two reactions each, Ivo wave/nod/laugh/tablet flash, Engineer quick turn | gate1 spec, IVO_SPEC, MIRA_SPEC (Extra animation sets) | EXTRA in engineer_sprites.py, ivo_sprites.py, mira_sprites.py | 2026-10-02 (director) |

## Plan

The plan lives in the OpenSpec change [`complete-art-production`](../openspec/changes/complete-art-production/): `proposal.md` (why and what), `design.md` (cross-cutting decisions), `specs/` (five capability contracts) and `tasks.md` (numbered checkboxes). Tick a task only when its review has passed and its decision records are written. Work the first unticked task unless a dependency says otherwise. The interim `art-direction/production/` folder is retired and must not be used.

## Carry-forward lessons (player feedback)

- Small props must read as what they are: give them a bezel or frame, a lit face, a detail, and a hand on them where it fits. This came from Ivo's tablet.
- Hair must never read as a helmet: tufts and strand clusters, an uneven fringe, and ears or nape showing. Never a flat rim line. This came from Ivo.
- Doors must read as doors: an opening you can see through or a sliding glass door, a frame, lamps, and a lit mat with lettering. This came from the review room.
- Match the finish and density of reference 08, not the sparse scale-test.
