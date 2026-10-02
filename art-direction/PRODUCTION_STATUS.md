# Kanata Hero — art production status

This is the living production file. **Developers start at [ART_HANDOFF.md](ART_HANDOFF.md)**, which indexes every approved asset and its formats; `build_all.py` rebuilds and checks everything. Any agent continuing the art work should read this first, then [STYLE_BIBLE.md](STYLE_BIBLE.md) and the approved specs listed below. Update it after every approval.

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
| Glitches: displaced stapler, duplicate chair shadow, folded form (roam + misregister) | [glitches/GLITCHES_SPEC.md](glitches/GLITCHES_SPEC.md) | glitches/glitch_sprites.py | 2026-10-02 (director) |
| Portrait template and rules; Engineer, Ivo, Mira portraits (neutral, concerned, pleased); Mira's six patches. **Superseded 2026-10-02** by the chibi set (row below). | [portraits/PORTRAITS_SPEC.md](portraits/PORTRAITS_SPEC.md), [portraits/PORTRAIT_RULES.md](portraits/PORTRAIT_RULES.md), [cast/MIRA_PATCHES_SPEC.md](cast/MIRA_PATCHES_SPEC.md) | portraits/portrait_*.py, cast/mira_patches.py | 2026-10-02 (director) |
| Vale: idle ×4, walk ×4 (softening state 0) | [cast/VALE_SPEC.md](cast/VALE_SPEC.md) | cast/vale_sprites.py | 2026-10-02 (director) |
| Ada: idle ×4, walk ×4, lantern rim-light ruling | [cast/ADA_SPEC.md](cast/ADA_SPEC.md) | cast/ada_sprites.py | 2026-10-02 (director) |
| Hal: idle ×4, walk ×4 | [cast/HAL_SPEC.md](cast/HAL_SPEC.md) | cast/hal_sprites.py | 2026-10-02 (director) |
| Records kit (48 entries), circular archive desk before/after, walkable reference room | [kit/RECORDS_KIT_SPEC.md](kit/RECORDS_KIT_SPEC.md) | kit/shared_pieces.py, kit/records_kit.py | 2026-10-02 (director) |
| Vale: interact, displeased and reconsidering reactions; 48×48 portrait (neutral, concerned, restrained pleased) | cast/VALE_SPEC.md (Extra sets), portraits/PORTRAITS_SPEC.md (Vale) | EXTRA in cast/vale_sprites.py, portraits/portrait_vale.py | 2026-10-02 (director) |
| Noor: idle ×4, walk ×4 | [cast/NOOR_SPEC.md](cast/NOOR_SPEC.md) | cast/noor_sprites.py | 2026-10-02 (director) |
| Hal: interact, puzzled and anxious reactions; 48×48 portrait | cast/HAL_SPEC.md (Extra sets), portraits/PORTRAITS_SPEC.md (Hal) | EXTRA in cast/hal_sprites.py, portraits/portrait_hal.py | 2026-10-02 (director) |
| Ada: interact (lantern lift), nod and explaining reactions; 48×48 portrait | cast/ADA_SPEC.md (Extra sets), portraits/PORTRAITS_SPEC.md (Ada) | EXTRA in cast/ada_sprites.py, portraits/portrait_ada.py | 2026-10-02 (director) |
| Noor: stamp-down interact, unimpressed and satisfied reactions, posture_upright; 48×48 portrait | cast/NOOR_SPEC.md (Extra sets), portraits/PORTRAITS_SPEC.md (Noor) | EXTRA in cast/noor_sprites.py, portraits/portrait_noor.py | 2026-10-02 (director) |
| Systems kit (78 entries, 14 state sets), routing machine before/after, reference room | [kit/SYSTEMS_KIT_SPEC.md](kit/SYSTEMS_KIT_SPEC.md) | kit/systems_kit.py | 2026-10-02 (director) |
| Executive kit (63 entries), atrium tree before/after, reference room | [kit/EXECUTIVE_KIT_SPEC.md](kit/EXECUTIVE_KIT_SPEC.md) | kit/executive_kit.py | 2026-10-02 (director) |
| Night Shift kit (61 entries), long interior window before/after, reference room, readability report | [kit/NIGHTSHIFT_KIT_SPEC.md](kit/NIGHTSHIFT_KIT_SPEC.md) | kit/nightshift_kit.py | 2026-10-02 (director) |
| Developer handoff: asset index, formats, anchors, layers, tokens, rebuild (build_all.py, check_handoff.py) | [ART_HANDOFF.md](ART_HANDOFF.md) | build_all.py, check_handoff.py | 2026-10-02 (director) |
| Final consistency pass: Orientation shelving and partitions added (53 entries), statuses, briefs, Pace layer names, handoff | ART_HANDOFF.md, kit/ORIENTATION_KIT_SPEC.md | kit/orientation_kit.py | 2026-10-02 (director) |
| Chibi portraits (direction C) for all seven: neutral, concerned, pleased, plus signatures `ivo_laugh`, `mira_grin`, `noor_unimpressed`, `hal_puzzled`, `vale_softened`; Mira's patches re-placed. Replaces every earlier 48×48 portrait. | [portraits/PORTRAITS_SPEC.md](portraits/PORTRAITS_SPEC.md), [portraits/PORTRAIT_PERSONAS.md](portraits/PORTRAIT_PERSONAS.md) | portraits/chibi.py, portraits/portrait_*.py | 2026-10-02 (player) |
| Night Shift edge light revised (player): cool moonlight on the floor, warm head and shoulders in lamp pools and from Ada's lantern | palettes/PALETTES_SPEC.md, kit/NIGHTSHIFT_KIT_SPEC.md, cast/ADA_SPEC.md | palettes/night_rim.py | 2026-10-02 (director) |

## Plan

The plan lives in the OpenSpec change [`complete-art-production`](../openspec/changes/complete-art-production/): `proposal.md` (why and what), `design.md` (cross-cutting decisions), `specs/` (five capability contracts) and `tasks.md` (numbered checkboxes). Tick a task only when its review has passed and its decision records are written. Work the first unticked task unless a dependency says otherwise. The interim `art-direction/production/` folder is retired and must not be used.

## Carry-forward lessons (player feedback)

- Small props must read as what they are: give them a bezel or frame, a lit face, a detail, and a hand on them where it fits. This came from Ivo's tablet.
- Hair must never read as a helmet: tufts and strand clusters, an uneven fringe, and ears or nape showing. Never a flat rim line. This came from Ivo.
- Doors must read as doors: an opening you can see through or a sliding glass door, a frame, lamps, and a lit mat with lettering. This came from the review room.
- Match the finish and density of reference 08, not the sparse scale-test.
- Rim and edge lights on characters stay quiet and ambient, never a bright full-edge halo. The warm cream Night Shift rim read like a "selected" highlight and sat close to discovery gold. It became a cool moonlight edge on the open floor, applied only where it beats the plain outline, plus a warm edge on the head and shoulders only where a warm source lights someone (lamp pools, Ada's lantern) (2026-10-02). This came from the Night Shift review.
