# Portrait rules (48×48 head and shoulders)

**Status:** Approved by the director 2026-10-02. These rules apply to every recurring character's dialogue portrait. They extend the person rules in the [Gate 1 spec](../gate1/GATE1_ENGINEER_SPEC.md) and the Portraits requirement in `openspec/changes/complete-art-production/specs/character-sprites/spec.md`. The template sheet is `portrait-template.png`; the geometry lives in `portrait_template.py`.

## Frame and display

| Item | Rule |
| --- | --- |
| Size | 48×48 logical px, which is 3×3 world tiles. Source rows are written as three 16-key blocks per row (`parse` strips the spaces). |
| Zoom | Shown at the world's integer zoom: ×4 on 1366×768 (192×192 screen px), ×6 on 1920×1080. Never fractional. |
| Background | Transparent. The dialogue panel provides the plate. Never bake a backdrop, a frame or a shadow into the portrait. |
| Facing | Front view, head and shoulders, the portrait of the sprite's S facing. Asymmetry comes from the hair and the costume, as on the sprite. |
| Margins | Row 0 and columns 0 and 47 stay empty. The body is cropped by the bottom edge. |

## Framing (portrait pixels, 0-indexed)

| Part | Rule |
| --- | --- |
| Hair top | Topmost outline row is row 1 (a tuft or a puff may reach it). The crown dome sits at rows 2–4. |
| Head box | Hair and head occupy columns 12–36 and rows 1–32 (25 × 32 px). The face fill is 20 px wide (columns 14–33) and runs from row 12 to row 31. |
| Hairline | Forehead skin begins at row 12–13. The fringe is uneven and may dip to row 16 at the sideburns. |
| Brows | Row 17 (rows 16–18 when raised or angled). |
| Eye line | Rows 19–20, a little over half way down the head. Left eye columns 17–20, right eye columns 27–30, 6 px apart. |
| Nose | Rows 22–24, centred on the axis. |
| Mouth | Rows 26–28 (row 27 at rest), columns 21–26. |
| Ears | Columns 11–12 and 35–36 around rows 19–24, always visible below the hair. |
| Chin and neck | Chin outline at row 32. The neck is 8 px wide (columns 20–27), rows 32–35, with a shadow under the chin. |
| Shoulder line | Clothing starts at row 35. The slope reaches the full width (columns 2–45) by row 40 or 41. A broader cast member may reach it earlier (Ivo: row 39). |
| Crop | Row 47 is the last row. No outline below it. The side outlines run down to it. |
| Axis | The face axis is the edge between columns 23 and 24. |

The 48×48 head is about 2.4 times the sprite's 10 px head, and the face keeps the sprite's reading: the same hair shape and colour, the same garment colours, the same prop colours.

## Light and shading

Light comes from the upper left. Shade in solid clusters, never gradients or dithering.

- Skin: the lightest step (`n`) on the upper-left planes (forehead, left cheek), the mid step (`m`) across the middle, the shadow step (`l`) on the two right-hand columns of the face, under the chin and on the neck. A cast shadow row (`l`, or `k` where hair and skin are close) sits directly under the fringe.
- Hair: the lit step (`D`) on the upper-left rim and a diagonal highlight band, the mid step across the mass, the shadow step (`B`) along the bottom and right edges and in a few 1 px strand lines. The darkest step (`A`) marks fringe tips and the underside of the fringe.
- Clothing: the lit step on the left shoulder slope and the left sleeve edge, the mid step across the chest, the shadow step right of a diagonal that runs down to the left.

## Outline

- The default outline is `#202337`.
- **Lit-edge swaps.** Along the upper-left silhouette, short runs may take the material's own darkest step (hair `A`, skin `k`, jacket's darkest). The right and lower silhouettes stay `#202337`.
- The seam between ear and cheek, and any place where two forms overlap, stays `#202337`.
- **Darkest-step rule.** A ramp's darkest step only ever sits on a contour or an occlusion edge. The checker flags it wherever all four neighbours belong to the same ramp.
- The silhouette is closed everywhere except the crop row: every opaque pixel that touches transparency is `#202337` or a contour swap.

## Expression

The sprite's face is two eye pixels and a hair-shadow line. The portrait grows both without changing identity: eyes are 4×2 with the sprite's ink pixel as the iris on a lit-skin sclera, and the hair-shadow line becomes the underside of the fringe. Expression comes from four things:

| Part | How it varies |
| --- | --- |
| Brows | Level at rest. Concerned: inner ends raised (rows 16–18). Pleased: soft arch with lowered outer ends. Brows use the character's `BROW` key. |
| Eyes | Neutral: open (lid arc over iris). Concerned: heavy flat lid, iris, shadow under the eye. Pleased: closed arcs. |
| Mouth | Neutral: level line with a lit lower lip. Concerned: short line with corners dropping. Pleased: a wide smile with corners up. |
| Head tilt | Whole rows 0–14 shift 1 px: left for concerned, right for pleased. Shoulders never move. A character may override the rows and directions (Mira leans: neutral right, concerned left, pleased level; rows 0–10). |

The three **standard expressions** every recurring character needs are `neutral`, `concerned` and `pleased`. A brief's own names map onto them in the character's spec (Engineer's "satisfied" is `pleased`). **Character-specific extras** (Ivo's laughing, Mira's playful grin) are added as extra entries in the module's `EXPRESSIONS`, built with `portrait_template.stamp` from the module's own stamp list. They obey every other rule, and `check_portraits.py` checks every entry in `EXPRESSIONS`.

## Palette

1. **Same ramps as the world sprite.** Every portrait key is a key of that character's sprite `PAL`, with the same hex. The portrait modules import the sprite module and copy its `PAL`; they never define a hex of their own.
2. **Extra steps.** A portrait may add at most **one** extra step per ramp, and only if it is recorded in the module's `EXTRA` dict as `{key: {"hex", "ramp", "why"}}` and in the character's spec. `check_portraits.py` fails an unrecorded key and a second extra on one ramp. This round adds none.
3. **Customization.** The Engineer's portrait uses only the slot keys (hair `ABCD`, skin `klmn`, jacket `pqrs`) plus the fixed collar and badge keys. A ramp swap on the sprite's `PAL` therefore recolours the portrait as well.
4. **Markers.** No UI marker hex (`#19AFA2`, `#EC776D`, `#9876D5`, `#E6B750`), no violet on a person, and teal-hued clothing stays at or below 60% HSL saturation. Gold stays small: the sprite's glint limits apply to the portrait multiplied by 4.
5. **Hair and skin.** Hair never reads as a helmet: tufts, an uneven fringe, ears visible. Where a character's hair and skin are close in value the module says how they are separated: pale hair never touches the lit skin steps (`HAIR_SKIN_SEPARATED`, as on the sprite), or only named skin steps touch hair (`HAIR_TOUCH_SKIN`).

## Authoring and checking

1. Write the character's `BASE` (hair, skin shading, ears, neck, clothing, props) as a 48-row key grid with the facial features left plain. Use only the sprite's keys.
2. `EXPRESSIONS` is built by `portrait_template.compose(BASE, expression, skin_keys, brow_key, stamps, tilt, hair)`. The kit's stamps sit at the guide coordinates above, so do not move the face features. Move or add a character stamp only through the module's `STAMPS`.
3. Run `python3 check_portraits.py`, then `python3 build_portraits.py` and read `portraits-sheet.png`. Review at ×4 beside the world sprite.
4. Record the character's decisions in its spec. New characters (task 9.3) follow `PORTRAITS_SPEC.md`.

The checker covers: size, palette identity with the sprite, recorded extras, markers and violet, closed outline, empty margins, no outline on the crop row, the darkest-step rule, hair against skin, glint limits, teal saturation, expressions differing by at least 40 px, identical shoulders across expressions, and (for Mira) patch icons sitting on the jacket and each adding at least 5 px.
