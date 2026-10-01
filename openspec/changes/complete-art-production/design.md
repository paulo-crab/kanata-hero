# Design

## Context

See proposal.md for motivation. The Orientation slice already shows the pipeline works:

- **Characters** are hand-placed key grids in Python modules: `art-direction/gate1/engineer_sprites.py`, `art-direction/cast/ivo_sprites.py` and `art-direction/cast/mira_sprites.py`. Each module has a `PAL` and `SLOTS`, and its `IDLE` and `WALK` frames are composed from shared leg poses.
- **The environment** is a procedural palette-only drawing module, `art-direction/gate1/environment.py`.
- **Checks** come from `art-direction/gate1/check_gate1.py`.
- **Builds** come from `art-direction/cast/build_cast.py` (sheet, atlas, walk GIF) and `art-direction/gate1/build_gate1.py` (review room, still and GIF).
- **Approval.** The player has delegated all art decisions and gate approvals to the art director, who self-reviews. Commits go to the `feat/art-production` branch. PRs are never merged without human review.

## Goals / Non-Goals

**Goals:**
- Finish every asset family in the specs using the proven pipeline, so quality and format stay uniform.
- Make the environment reusable: replace the one-off review-room drawing with an atlas that developers can lay out from tile data.
- Leave a handoff that lets developer agents implement without reading this session's history.

**Non-Goals:**
- No game code, runtime renderer or level data. Those belong to the implementation change in `docs/game-design.md` "Implementation slices".
- No audio, and no full 20-quest level maps. Kits and one reference room per district suffice.
- No bespoke art per quest (game-design "Asset and level handoff").

## Decisions

1. **Pixels as code, PNGs as outputs.** Every frame is a 16-character-per-row key grid, and every environment piece is a drawing function using palette constants.
   - *Why:* hand-placed pixels are exact, diffable and reviewable in PRs. Customization is a ramp swap by construction. Checks run on the source.
   - *Alternative:* image-model generation, which can't hold a 16 px grid or a fixed palette. Rejected.
2. **One generic checker extended per rule.** New rules are opt-in module flags (`HAIR_SKIN_SEPARATED`, `GLINT_LIMITS`), so approved assets keep passing.
   - *Alternative:* per-character checkers, which drift apart. Rejected.
3. **Environment atlas by extraction, not redraw.** Task group 3 turns `environment.py`'s pieces into named atlas entries with metadata and then rebuilds the review room from the atlas. The approved room is the regression test.
   - *Alternative:* draw a fresh tile set, which risks drifting from the player-approved finish. Rejected.
4. **District palettes before district assets.** Each district's hex sheet is made by deriving 4-step ramps from the words in the game-design district table, checked for marker collisions and floor contrast, then appended to STYLE_BIBLE §3.
5. **Order: finish what's on screen first.**
   - First, Orientation context (background workers, glitches, Pace) and the Orientation kit.
   - Then palettes, followed by the remaining cast and the district kits.
   - Then extra animation sets, portraits and UI, ending with the handoff.
   - *Why:* each step unblocks the next. The vertical slice in `docs/game-design.md` needs Orientation complete first.
6. **Review.** Each asset gets the automated check, a coordinator review of the ×8 sheet and the ×4 in-context render, and for any new pattern a Sonnet validator pass. There are at most three cycles. Approvals are written to the asset spec, the brief and the README log, then committed.
7. **UI as a spec, not pixels.** UI components are specified as tokens and HTML/CSS structure with a static reference page. They are not drawn into the world, as the UI spec requires.

## Risks / Trade-offs

- [Python modules get long as sets grow] → Keep one module per character or district. Share leg poses, `lower()` and overlay helpers.
- [Self-approval misses what the player would catch] → Carry the player's past feedback forward as checks and review items: prop readability, helmet hair, doors. Keep the validator pass for new patterns.
- [District palettes invented from words] → Derive them from the canonical district descriptions, test contrast and markers numerically, and record each as a Director decision that the player can overrule.
- [Token or context limits mid-run] → `art-direction/PRODUCTION_STATUS.md` and this change's `tasks.md` hold the state. Commit after each approved task.

## Migration Plan

Retire `art-direction/production/` (the interim planning files) in favour of this change. Repoint `PRODUCTION_STATUS.md` at `openspec/changes/complete-art-production/tasks.md`. On completion, archive the change so the five specs land in `openspec/specs/` for the implementation work.

## Open Questions

- How many background-worker body variants each district needs (background-workers.md open question 1). Two bodies × three palettes is assumed. This only changes counts, not the approach.
