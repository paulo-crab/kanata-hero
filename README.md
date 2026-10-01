# Kanata Hero — document map

Kanata Hero is a planned browser game that teaches this machine's Kanata keyboard layout through a top-down office adventure. No game code exists yet; this repository holds the design, level, and art-direction documents for a later OpenSpec implementation.

## Which document owns what

When documents disagree, the owner below wins. Fix the other document instead of working around the disagreement.

| Topic | Owner | Notes |
| --- | --- | --- |
| Actual key behavior | `~/.config/kanata/kanata.kbd` (symlink target in the dotfiles repo) | The only layout source of truth. Not its README. Reconcile the docs whenever it changes. |
| Curriculum, gesture inventory (B/N/S/V IDs), scoring, browser rules | [`docs/game-design.md`](docs/game-design.md) | Product spec, v0.7. Owns the hint grammar for NPC and artifact key prompts. A versioned layout manifest is planned but not yet created. |
| Story, cast, per-level briefs, side quests, Mira routes | [`levels.md`](levels.md) | Refers to the gesture IDs in the game spec. |
| Visual style for new art: camera, palette, pixel rules, scale prototype | [`art-direction/STYLE_BIBLE.md`](art-direction/STYLE_BIBLE.md) | Primary visual authority: [`references/08-approved-overhead-direction.png`](art-direction/references/08-approved-overhead-direction.png). Summary board: [`STYLE_BOARD.html`](art-direction/STYLE_BOARD.html). |
| Current art workflow and gates | [`art-direction/ART_BRIEF.md`](art-direction/ART_BRIEF.md) | Read after the bible. |
| What each reference image teaches | [`art-direction/REFERENCE_NOTES.md`](art-direction/REFERENCE_NOTES.md) | Its scale numbers and review gate are superseded by the bible. |

### Historical records (do not use as direction)

- `art-direction/STYLE_DECISION.md`: superseded by the bible.
- `art-direction/REVIEW.md`: the art review log.
- `art-direction/director-sketches/NOTES.md`: concept prompts; the images are deleted except 08.
- `art-direction/ui/README_v2.md`: rejected UI study; the previews are deleted.
- `art-direction/character-current/`: all Engineer and cast studies, including the 72×96 experiments. Discarded.
- Scripts in `characters/`, `environment/`, `ui/`, and `director-sketches/` are rejected generators. Don't run or reuse them.

## Decisions

**Production in progress:** see [`art-direction/PRODUCTION_STATUS.md`](art-direction/PRODUCTION_STATUS.md) for the plan, what is done, and how to continue. Since 2026-10-02 the player has delegated gate approvals to the art director, who self-reviews and approves.


- **Scale (decided 2026-10-01):** 16×16 tiles, 16×24 people, 48×48 portraits, a 320×180 view scaled by whole numbers (×4 on 1366×768, ×6 on 1920×1080). Chosen by the player from [`art-direction/scale-test/`](art-direction/scale-test/). Recorded in the game spec, `levels.md`, the style bible, style board, and art brief.
- **Clothing vs. interaction markers (decided 2026-10-01):** muted teal is allowed on clothing (hue 160°–200° steps at or below 60% HSL saturation, never a marker hex); no person wears violet. Recorded in STYLE_BIBLE §3, the character README, and `engineer.md`.
- **Gate 1 animation contract (decided 2026-10-01):** anchor on the pixel edge between columns 7 and 8, feet on row 23; walk 4 frames × 133 ms per direction, 2 cells per cycle; idle 2 frames × 500 ms. Recorded in STYLE_BIBLE §5; may be revised after the gate.
- **Style foundation reconciliation (2026-10-01):** `REFERENCE_NOTES.md` no longer carries 32×32 / 48×64 sizes or its old gate; `docs/game-design.md` now matches the bible on selective outlines, hard-edged light, and draw order.
- **Engineer Gate 1 candidate (2026-10-01):** hand-placed frames, scene and sheets in [`art-direction/gate1/`](art-direction/gate1/GATE1_ENGINEER_SPEC.md). The spec lists its Director decisions: hair sweep side, badge visibility, idle and walk motion, foot offset, contact-shadow shape, tone rule, and color-only hair customization. **Approved by the player 2026-10-02.** Its Director decisions are canon, and the review room in `environment.py` (08-finish floor, walls, garden, sliding glass Records door with a RECORDS mat) is the environment quality bar. Other characters may now start, one at a time, through the same review workflow.
- **Cast frame rule (decided 2026-10-02):** every person sprite stays inside 16×24, and props are held against the body, never overhanging. **Ivo** idle ×4 and walk ×4 were built under the Gate 1 contract (`art-direction/cast/IVO_SPEC.md`) and were **approved by the player 2026-10-02**, after a revision that made the tablet a bezelled device held flat and took the helmet look out of the hair.
- **Mira** idle ×4 and walk ×4 were built and **approved 2026-10-02** (`art-direction/cast/MIRA_SPEC.md`). All three Orientation people in the review room now use hand-placed cast sprites.
- **Old art drafts discarded** by the player. They stay on disk until moved to the Trash; nothing may reference them.
- **Pace** wayfinding icon and signage (stone-ring badge with a blue-glass screen, wall/floor/directory pieces, no lettering, no marker colours) **approved by the director 2026-10-02** (`art-direction/pace/PACE_SPEC.md`). The small wall plate reads slightly like a monitor; it is accepted because it sits on a wall, away from desks.
- **UI kit** (`art-direction/ui-kit/`) **approved by the director 2026-10-02**. The six anchor hexes keep their roles. Lighter text tokens (`#36C3B6`, `#F2928A`, `#B79FEA`) carry teal, coral and violet text at WCAG AA. No text sits on violet fills. Body text is 18 px, with a 16 px minimum. A held key is never shown by colour alone. Markers are a speech bubble, a monitor, a diamond with a doorway and a folded page, and stay distinct in greyscale. The inset header names the `nav` layer and holds the timing. Proposed key bindings: Return to continue, Esc to skip, Tab for the journal, `?` for Layout help. Layout help draws only the `nav` tab; the other tabs are specified in `COMPONENTS.md`.
- **District palettes and new cast ramps approved by the director 2026-10-02** (`art-direction/palettes/PALETTES_SPEC.md`, STYLE_BIBLE §3). Each district has 8 ramps × 4 steps, with the ink and violet ramps shared verbatim. Floor and wall steps may never fall in the violet family (hue 260–320° above 12% saturation), so glitches keep violet to themselves. Night Shift has a cool slate floor; people there get a 1 px `#F9D79A` rim on the upper-left contour. Systems' mint foliage counts as a device ramp. Floor contrast is tested on the outline (3:1 or better) and on at least 45% of body pixels, not on every mid tone. Revised once: the plum Night Shift floor became slate, and Ada's burgundy skin became deep warm brown.
- **Background workers approved by the director 2026-10-02** (`art-direction/cast/BACKGROUND_WORKERS_SPEC.md`). There are two prop-free bodies (A slim with a side-parted crop, B with a longer centre-parted cut) in three colourways: slate, olive and ash. Clothing stays at 30% saturation or below so workers recede behind the named cast. Until level 06, workers play the standard walk on one shared clock; after it, they play idles at random offsets. Each body has three individual idles (phone, coffee, typing) and two silhouette variants for figures seen through glass. Seated work waits for the desk occluders.

## Open decisions

1. **Optional keymap change.** The practice layer already silences digits 1–0. Silencing minus/equals as well is optional, separate from the game, and must never be required.

## Reconciliation log — 2026-10-01

Checked all documents against each other and against the live `kanata.kbd`, the Kanata binary, and the launchd service definition.

**Keymap accuracy (game spec v0.5 → v0.6, plus `levels.md`)**
- The practice layer was changed at 16:29 that day to silence physical digits 1–0, which also blocks `! @ # $ % ^ & * ( )` from the number row. The spec still described the number row as fully unenforced, and level 19 repeated that. Both now describe what is blocked (digits) and what still passes through (minus, equals, and so `-` `_` `=` `+`). V05 evidence stays player-confirmed because the browser can't see physical keys or the active layer.
- Physical Left Control+Space+Escape had been called "not implemented by the layers." It is Kanata's built-in emergency exit. It quits Kanata and stops all remapping, and with this service setup Kanata stays off until restarted. V06 and level 17 now describe it that way.
- Layer identifiers now match the config: `base`, `nav`, `numbers-symbols`, `practice`. The spec had written `normal`.
- N19 selection now says to engage the F/J Shift hold before Caps, because F is a literal `f` and J is Down while Caps is held.
- Every other inventory row (B01–B15, N01–N21, S01–S26, V01–V04) matched the config.

**Cross-document alignment**
- "Serene, windowless office" contradicted the daylight, skylights, and window views elsewhere. The art review log had already flagged this. Changed to a daylit office whose window views are not quite right.
- Courier patches: the game spec's example session gave the patch for a faster run, while the other passages give it on the first clean baseline and give a medal for the faster run. Aligned everything to baseline → patch and faster clean run → optional medal. The `levels.md` Mira-table header now says this.
- "One Mira route per district" and "Mira in each district" didn't match the six routes listed, which give two each to Records and Systems and none to the Executive Floor. Reworded to match the table.
- "One piece of optional lore per district" didn't match the several artifacts most districts have. Reworded.
- Per-quest coverage in the game spec now matches `levels.md`: quest 6 adds N21, quest 17 adds B13, and quest 20 names the final seal.
- The Executive atrium had "one NPC per branch" (3) against the five coworkers who arrive. Reworded.
- `levels.md` said the Systems review reveals "the bridge and return walkway", which levels 12 and 15 already open. It now says the review opens the service walkway and the Night Shift stop.
- The game spec now names the cast (Ivo, Noor, Hal, Ada, Vale) and Pace, and points to `levels.md`.

**Visual references and status**
- The game spec and `levels.md` described reference images that aren't in the repository ("first new image", "dungeon image", "supplied screenshot"). They now cite the numbered files in `art-direction/references/`.
- Both docs now point to the style bible and flag the open scale decision, without changing the planning numbers.
- `STYLE_DECISION.md` said no draft images remained, but the `character-current/` studies exist. Corrected.
- `ui/README_v2.md` linked to deleted previews and had no status. It is now marked rejected and historical.
- Each character review file now has a status banner that matches `ART_BRIEF.md`.
- Checked and found consistent: the `STYLE_BOARD.html` palette matches the bible's 32 colors exactly, and the scale arithmetic holds (1.5×2 tiles; 640×480 ≈ 13×10 cells at 48 px).
