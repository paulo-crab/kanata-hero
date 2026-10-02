# Portrait rules (48×48 chibi icon)

**Status:** Candidate, pending director review. Player decision 2026-10-02: direction C, "Chibi icon", replaces the earlier realistic head-and-shoulders portraits (too serious, too real). These rules apply to every recurring character's dialogue portrait and extend the person rules in the [Gate 1 spec](../gate1/GATE1_ENGINEER_SPEC.md). Geometry and helpers live in `chibi.py`; per-character choices in [PORTRAIT_PERSONAS.md](PORTRAIT_PERSONAS.md). The template sheet is `portrait-template.png`.

## Frame and display

| Item | Rule |
| --- | --- |
| Size | 48×48 logical px (3×3 world tiles) |
| Zoom | The world's integer zoom: ×4 on 1366×768 (192×192 screen px), ×6 on 1920×1080. Never fractional. |
| Background | Transparent. The dialogue panel provides the plate. No baked backdrop, frame or shadow. |
| Facing | Front view. Asymmetry comes from the hair, the costume and the persona's habits. |
| Margins | Row 0 and columns 0 and 47 stay empty. The body runs off the bottom edge (row 47 has pixels, nothing is outlined below it). |
| Axis | The face axis is the edge between columns 23 and 24. |

## Framing (portrait pixels, 0-indexed)

| Part | Standard rule | Persona variation |
| --- | --- | --- |
| Hair top outline | Row 1 at the highest (a tuft or a bun reaches it) | |
| Head | Oversized and round: rows 3-36, up to 36 px wide (cols 6-41) | Hal 40 wide, rows 5-36; Noor 32 wide, rows 3-38; Vale flat top and chin; Ivo wide jaw; Mira pointed chin |
| Brows | Row 19 (17-22 when raised or angled) | per persona |
| Eyes | Block rows 22-25, left cols 14-17, right cols 30-33, 16 px apart | Ivo and Vale 3 rows; Mira 5 rows; Noor shifted to rows 24-26; Hal 5×5 when anxious |
| Blush | Two small patches at rows 27-28, cols 9-12 and 35-38 | size 2×2 to 5×2; none for Vale at rest |
| Mouth | Rows 28-30, centred on the axis, big and readable | per persona |
| Shoulders | Tiny, in rows 38-47, cols 8-39 | Ivo cols 5-42; Noor rows 40-47, cols 10-37; Vale square from row 38; Hal cols 5-42 |
| Neck, ears | None: the head sits on the shoulders (the chin line is the head outline) | |

## Shading and light

Light comes from the upper left. Shading is **flat**: one skin fill (the lightest skin step `n`) and one crescent of shade (`m`) down the lower right, growing toward the jaw, plus a one-pixel shade under the fringe. Hair has a lit upper left (`D`), a body (`C`), a dark right edge (`B`) and a few strand lines. Clothing: lit left edge, mid body, shade on the right. Hard pixels only: no gradients, no dithering.

**Skin budget: two ramp steps** on the portrait (fill and shade). The blush key is counted apart and may be a skin step or another sprite key.

## Outline

`#202337`, closed around the whole silhouette, added around each layer as it is painted (body, head, hair). The head also takes an outline over the body (the chin line). A ramp's darkest step never fills an area (contours, occlusion edges and thin lines only). The checker flags any opaque pixel that touches transparency and is not outline ink.

## Eyes

Dots with a glint. The glint is the lightest pale key of the sprite's PAL, recorded in the module's `EXTRA` (it adds no hex). Closed eyes are `.oo.` over `o..o` arcs (happy) or `o..o` over `.oo.` (serene). Brows use the character's `BROW` key; where the hair is as dark as the skin the brow is outline ink.

## Expression system

| | |
| --- | --- |
| Standard | `neutral`, `concerned`, `pleased` for every character (the dialogue system needs them). A brief's own names map onto them in `PORTRAIT_PERSONAS.md`. |
| Signature | Zero or one per character, named `<name>_<signature>`, only where the docs clearly support one: `ivo_laugh`, `mira_grin`, `noor_unimpressed`, `hal_puzzled`, `vale_softened`. |
| Built from | Stamps in the module's `FACE` dict: brows, eyes, mouth, blush, plus a personal tic. Shoulders (rows 38-47) never change between expressions. |
| Differences | Expressions of one character differ by at least 12 px; any two characters' faces differ by at least 14 feature px in each standard expression. |

## Persona-driven variation

Each character differs from the others in head shape, hair silhouette, costume, **and** in the face: eye shape, brow habit, mouth habit, blush size and one tic (PORTRAIT_PERSONAS.md). The Engineer is the baseline: standard round head, standard dot eyes, standard mouths. Nobody is mean or hostile; concern reads as worry, question or firmness, never anger. Vale's arc shows in the face: rigid neutral (no blush), restrained pleased (corners up one pixel), and `vale_softened` as the first real softening.

## Palette

1. **Same ramps as the world sprite.** Every portrait key is a key of that character's sprite `PAL` with the same hex. Modules import the sprite module and copy its `PAL`; they never define a hex of their own.
2. **Extra steps.** `EXTRA` records only pale eye-glint keys that already exist in the PAL.
3. **Patch keys.** Mira's patch icons use `mira_patches.PATCH_PAL` (five keys whose hexes already exist in her PAL or the brass ramp); they appear only on patched portraits.
4. **Markers.** No UI marker hex (`#19AFA2`, `#EC776D`, `#9876D5`, `#E6B750`), no violet, teal-hued clothing at or below 60% saturation, gold small. Glint limits of the world sprite apply multiplied by 4.
5. **Hair never reads as a helmet:** crown tufts or scallops, notches, an uneven fringe.

## Authoring and checking

1. Write the character module: `HEAD` (`head_spans`), `BODY`, `cloth()`, `PROPS`, `HAIR` (`rle_hair` or `block_hair`), `FACE` stamps, `SKIN` tokens, `SIGNATURES`, `PROP_KEYS`, `TAGLINE`. `chibi.build` composes the expressions.
2. `python3 check_portraits.py`, then `python3 build_portraits.py`, and read `portraits-compare.png` and `portraits-sheet.png` at ×4.

The checker covers: size, palette identity with the sprite, recorded glint extras, markers and violet, closed outline, empty margins, an oversized head, the skin budget, the darkest-step rule, hair, clothing and prop identity, glint limits, teal saturation, expressions differing, identical shoulders, no two characters sharing a face, Mira's bun notch and blush, and Mira's six patch states (icons on the jacket, apart from each other, each adding at least 5 px).
