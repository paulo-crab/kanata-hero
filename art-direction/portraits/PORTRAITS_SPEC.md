# Portraits: seven characters, chibi direction C

**Status:** Candidate, pending director review.

**Sources:** player decision 2026-10-02 (direction C, "Chibi icon"; "each person should have their own emotion/reactions"), `design/characters/*.md`, `levels.md`, `docs/game-design.md`, the approved sprite modules, STYLE_BIBLE §3-5 and §7, [PORTRAIT_RULES.md](PORTRAIT_RULES.md), [PORTRAIT_PERSONAS.md](PORTRAIT_PERSONAS.md). The exploration that led to the choice is in `explore/` (kept as a record). The previous realistic portraits are replaced.

## Deliverables

| File | What it is |
| --- | --- |
| `PORTRAIT_PERSONAS.md` | Per character: physical cues, emotional profile, neutral/concerned/pleased pixel choices, signature |
| `PORTRAIT_RULES.md` | Framing, shading, eyes, outline, expression system, persona-driven variation, palette |
| `chibi.py` | Shared style module: geometry, composition, tokens, rendering. Replaces `portrait_template.py` (deleted). |
| `portrait_engineer.py` .. `portrait_vale.py` | One module per character: head, body, costume, hair, face stamps, signature. They import their sprite module and copy its `PAL`. Mira's also holds `with_patches`. |
| `check_portraits.py` | The automated check (50 grids: 26 expressions plus 24 of Mira's patched portraits) |
| `build_portraits.py` | Writes the outputs below |
| `portrait-template.png` | Guides on the standard head, blank guides, the seven head silhouettes, notes |
| `portraits-sheet.png` | Per character: world sprite (S idle) and each expression at ×4, tagline, key swatches |
| `portraits-compare.png` | One row per expression type, all seven characters (the personality check) |
| `portraits-dialogue.png` | Each character in a mock dialogue panel with a levels.md line, a different expression each |
| `portraits-atlas.png` / `.json` | Native 48×48 cells. Columns: neutral, concerned, pleased, signature. Rows as before (engineer, ivo, mira, mira_patch1..6, vale, hal, ada, noor). |

Rebuild: `cd art-direction/portraits && python3 build_portraits.py`. Check: `python3 check_portraits.py`. Mira's patch sheet: `../cast/build_mira_patches.py` ([MIRA_PATCHES_SPEC.md](../cast/MIRA_PATCHES_SPEC.md)).

Atlas JSON keeps its format: `frame`, `columns`, `rows`, `zoom`, `origin`, `mira_patch_rows`, `portraits` (`<name>_<expression>` rects). New keys: `signature_column` (3), `signatures` (name to expression), `signature_keys`, `style`. A signature entry is `<row>_<name>` (`ivo_laugh`, `mira_grin`, `mira_patch3_grin`, `noor_unimpressed`, `hal_puzzled`, `vale_softened`); Engineer and Ada leave the cell empty.

## Persona summary

| | Head | Hair | Costume cue | Persona in one line | Signature |
| --- | --- | --- | --- | --- | --- |
| Engineer | standard round | brown swept, long right fringe | teal jacket, badge | observant baseline; left brow a pixel high | none |
| Ivo | wide soft jaw | silver clusters, side tufts | cardigan, tablet | polite and exact; small oval eyes, laugh lines | `ivo_laugh` |
| Mira | pointed chin | dome plus a separate bun | green/ochre jacket, coral strap | playful; cocked brow, smirk, sparkle eyes | `mira_grin` |
| Noor | tall, narrow | blue-black crop, two tufts | linen shirt, coral folder | dry and defiant; half-lids, mismatched brows | `noor_unimpressed` |
| Hal | broad, low | sandy mop, three spikes | cobalt vest, tool roll | practical, anxious, focused; slanted brows, sweat | `hal_puzzled` |
| Ada | soft round | warm-white scalloped cloud | moss coat, lantern | calm and kind; heavy lids, serene mouth | none |
| Vale | square, flat | graphite, cowlick, part | navy suit, tie, badge | rigid, softening; squared eyes, no blush at rest | `vale_softened` |

## Director decisions

1. **Direction C.** The player chose the Chibi icon from the exploration: oversized round head, tiny shoulders, flat shading (fill plus one crescent), dot eyes with a glint, big mouths, round cheeks with blush.
2. **One shared style module.** `chibi.py` generalises `explore_common.py` and `style_c.py`. It replaces `portrait_template.py`. A character module sets only head shape, hair, costume, props and its own face stamps.
3. **Persona-driven faces.** Each character differs in eye shape, brow habit, mouth habit, blush size and one tic, grounded in the docs (PORTRAIT_PERSONAS.md). The Engineer is the unmarked baseline.
4. **Skin budget two.** The fill is the lightest skin step and the shade the next; the blush key is counted apart. Blush keys: Engineer `U`, Ivo `l`, Mira `D`, Noor `f`, Hal `U`, Ada `T`, Vale `l`.
5. **Glints are recorded sprite keys.** The eye glint is a pale key already in each PAL (`y`, `D`, `r`, `s`, `y`, `D`, `y`), recorded in `EXTRA`. No hex is added.
6. **Mira's bun is separate.** The bun is a ball with its own ink arc and a V notch at the crown; the dome never merges into it. The checker counts the interior ink pixels.
7. **Mira's blush is not the strap coral.** No skin step reads as blush on her skin (`l` reads as a bruise, `m` and `x` as freckles), so the blush is the plum-brown hair step `D` (`#6B5058`), the nearest non-coral step. The checker fails if a coral key appears on her face. Her signature tongue is the one place the coral appears in the mouth.
8. **Mira's patches re-placed.** The six icons moved to the new tiny shoulders (MIRA_PATCHES_SPEC decision 10). The strap's dark right edge is one column wide so icons stay clear.
9. **Ada's warm side light.** Carried by the lantern prop and by a warm blush. No face rim is drawn (as before: a 1 px rim read as an earring).
10. **Hal's brows use outline ink** (`o`): his hair is as dark as his skin. Noor's and Ivo's brows use the hair's darkest step as a thin line (never a fill).
11. **Vale's arc.** Neutral has no blush and a dead-level mouth; pleased is restrained (brows up a pixel, mouth corners up a pixel, faint blush); `vale_softened` is the first real softening.
12. **Signatures only where the docs support them.** Ivo's laugh (cast table), Mira's playful grin (mira.md), Noor's unimpressed reaction (noor.md), Hal's puzzled reaction (hal.md), Vale's softening (vale.md). Engineer and Ada: none specified.
13. **Dropped from the realistic rules:** the 1 px head tilt, lit-edge outline swaps, the ear and neck rows, and the hair-against-skin separators. In the flat style the fringe's shade row and the hair hexes carry that separation. The darkest-step contour rule stays.
14. **Dialogue lines** are from levels.md (Ivo level 01, Mira level 05, Noor level 08, Hal level 12, Ada level 18, Vale level 20, the Engineer's journal from the Unissued badge artifact), one expression each.

## Acceptance criteria

Automated (`check_portraits.py`, 50 portraits, 0 failures):
- [x] 48×48, sprite-PAL keys with the same hex, recorded pale glints only
- [x] No UI marker hex, no violet, teal clothing at or below 60% saturation
- [x] Closed outline, clear row 0 and side columns, the body reaches row 47
- [x] Oversized head, skin budget two, darkest step on contours only
- [x] Hair ramp, clothing and prop keys present
- [x] Three standard expressions plus signatures, differing; shoulders identical
- [x] No two characters share a face (feature masks)
- [x] Mira's bun notch, blush off the coral, six patch states

Coordinator review (to be completed by the director):
- [ ] The seven read as one style at ×4 (`portraits-compare.png`)
- [ ] The seven read as seven personalities; no two concerned or pleased faces look alike
- [ ] Each portrait reads as the same person as its sprite (hair, costume, prop)
- [ ] Hair never reads as a helmet
- [ ] Mira's six patch icons are distinct at ×4 (`../cast/mira-patches-sheet.png`)

Review history: one self-review pass. The first rollout had Ivo's and Hal's hair as flat caps (rebuilt as clusters and spikes), a stray hair row beyond Noor's head, Mira's blush as a dark bruise (now `D`), brows lost on Hal's skin (now ink), a Hal pocket in the darkest vest step (now `q`), and Vale's pleased too close to neutral (brows lifted).
