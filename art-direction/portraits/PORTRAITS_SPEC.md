# Portraits: Engineer, Ivo and Mira (three expressions each)

**Status:** Approved by the director 2026-10-02.

**Sources:** `design/characters/engineer.md`, `ivo.md`, `mira.md` (Portrait sections), the approved sprite modules and specs ([Gate 1](../gate1/GATE1_ENGINEER_SPEC.md), [Ivo](../cast/IVO_SPEC.md), [Mira](../cast/MIRA_SPEC.md)), STYLE_BIBLE §3–5 and §7, and [PORTRAIT_RULES.md](PORTRAIT_RULES.md). **Director decision** marks choices made for the director to record.

## Deliverables

| File | What it is |
| --- | --- |
| `PORTRAIT_RULES.md` | The rules: framing, light, outline, expression, palette, authoring |
| `portrait_template.py` | Shared geometry, the expression kit, the tilt table and the compose helpers |
| `portrait_engineer.py`, `portrait_ivo.py`, `portrait_mira.py` | Hand-placed 48×48 key grids (`BASE`) and the built `EXPRESSIONS`. They import their sprite module and copy its `PAL`. Mira's module also holds `with_patches`. |
| `check_portraits.py` | The automated check (27 grids: 9 expressions plus 18 of Mira's patched portraits) |
| `build_portraits.py` | Writes the three outputs below |
| `portrait-template.png` | Construction guides on a mannequin, the guides alone, and the kit on the mannequin, at ×4 |
| `portraits-sheet.png` | Each expression at ×4 beside the world sprite at ×4, with swatches of the keys used |
| `portraits-atlas.png` / `.json` | Native 48×48 cells. Columns: neutral, concerned, pleased. Rows: engineer, ivo, mira, then `mira_patch1`..`mira_patch6`. |

Rebuild with `cd art-direction/portraits && python3 build_portraits.py`. Check with `python3 check_portraits.py`. Mira's patch sheet is built from `../cast/build_mira_patches.py` ([MIRA_PATCHES_SPEC.md](../cast/MIRA_PATCHES_SPEC.md)).

## How each portrait matches its sprite

| | Engineer | Ivo | Mira |
| --- | --- | --- | --- |
| Hair | Brown `ABCD`, swept: tufts at the crown, a long right-hand fringe that hangs in short points, a short left temple | Silver `ABCD` in four strand clusters (lit tops on the left, darker toward the back), a notched silhouette, a toothed fringe with one centre forelock dipping lowest into a `k` forehead shadow, and side tufts that overlap the top of each ear | Dark `ABCD` crown with the high puff on her left (screen right), separated by a notch drawn in ink, and a fringe with a parting |
| Skin | `klmn` as the sprite | `klmn` as the sprite | `klmn` as the sprite |
| Clothing | Muted teal jacket `pqrs`, cream collar V `wxy` | Terracotta cardigan `pqrs` over the ochre shirt strip `xyz` | Green panel `EFGH` on her right (screen left), ochre panel `wxyz` on her left, zip between |
| Prop or accent | Brass badge on a lanyard `bcd` | Tablet corner at the lower right, bezel `g`, glass `j`/`h`, one `J` glint, a thumb | Coral strap `de` running from her right shoulder across the chest; the bag is off-frame below the crop |
| Identity at 1× | Swept hair, teal jacket | Silver hair, wide cardigan, tablet | Puff, two-panel jacket, strap |

## Director decisions

1. **One skull, three characters.** All portraits share the face geometry in `portrait_template.py` (face fill columns 14–33, eye line rows 19–20, chin row 32, shoulders from row 35). Characters differ by hair, costume, shading and prop, not by face layout. This is what makes the template reusable for Noor, Hal, Ada and Vale.
2. **Hair top at row 1, row 0 clear.** Headroom of one row keeps tufts and Mira's puff inside the frame.
3. **Eyes grow from the sprite's two pixels.** Each eye is 4×2: the sprite's ink pixels as the iris on a sclera drawn with the lightest skin step. No white is added, so no extra step is needed.
4. **Expression kit.** The three standard expressions are `neutral`, `concerned` and `pleased`, made of brows, eyes, mouth and a 1 px head tilt, as set out in the rules. The same kit serves every character, so the expressions read the same way across the cast.
5. **Mapping to the briefs.**
   - Engineer: neutral = observant, concerned = concerned, pleased = satisfied.
   - Ivo: neutral = polite and scripted, concerned = questioning, pleased = the warm smile that precedes the laugh. The laughing portrait is a later extra.
   - Mira: neutral = resting and ready, concerned = earnest (the erased-routes admission), pleased = proud. The playful grin extra is later.
6. **Mira leans.** Her neutral tilts the head right, concerned tilts left, pleased is level, on rows 0–10, which keeps the diagonal posture of the sprite. The default tilt covers rows 0–14.
7. **Ivo's hair is clusters, not a mound.** Four clusters are painted back to front, each with its own lit top and shadow underside (light from the upper left, darker toward the right). The silhouette is notched between clusters, the fringe is uneven (the centre forelock hangs 2–3 px below the other locks), and a side tuft overlaps the top of each ear. His tilt covers rows 0–11 only, so the fringe stays put. Ivo's hair never touches lit skin. His silver steps match his pale skin in value, so every skin pixel beside light hair takes `k`, as on the sprite (`HAIR_SKIN_SEPARATED`). The separation is re-applied after the head tilt. His brows use the hair's darkest step `A`, because mid-grey brows would merge with the skin.
8. **Mira's hair and skin.** Her hair and skin share luminance, so only the lighter skin steps (`m`, `n`) touch hair, and the fringe underside is the darkest hair step `A` as the hair-shadow line (`HAIR_TOUCH_SKIN`). The sleeve has no dark seam line, because a darkest-step line inside one ramp breaks the contour-only rule.
9. **Ivo's shoulders are broader than the template.** The cardigan slope reaches full width on row 39 instead of row 41, which keeps him the widest person in the cast. The rules allow this per character.
10. **Props.** The Engineer's badge hangs on a diagonal lanyard from the collar. Ivo's tablet shows its corner at the lower right with the sprite's colours (the glint stays 1 px). Mira's strap is the sprite's coral diagonal with its shadow step, and her bag stays off-frame.
11. **No extra palette steps.** Every portrait key is a key of its sprite's `PAL` with the same hex, and `EXTRA` is empty for all three. The only keys outside a sprite's `PAL` are Mira's five patch keys in `mira_patches.PATCH_PAL`. Relative to `mira_sprites.PAL`, exactly two hexes are additions, both from the brass ramp: `#E1AC62` (key `a`, brass light) and `#F5D580` (key `b`, brass glint). The other three keys reuse hexes already in her PAL (`i` = `#F6B18E`, `j` = `#B2CE78`, `g` = `#EDCB7A`). They appear only on patched portraits and patched world frames, never on the base portraits.
12. **Ear and cheek seams stay ink.** Where the ear overlaps the cheek the outline is `#202337`, not a darkest-step swap. This follows the style bible ("darkest ink only where silhouettes overlap") and the contour-only checker rule.
13. **Reuse.** The world sprite on the sheet is drawn with `build_gate1.frame_rgba`. That helper is hard-wired to 16×24, so `build_portraits.grid_img` is its 48×48 sibling.
14. **Mira's patches in the portrait.** Each patch is drawn as a 4–6 px icon on the jacket, in the same colours as its world patch: envelope, map pin, loop, check mark, signal bars and crescent with a star. See [MIRA_PATCHES_SPEC.md](../cast/MIRA_PATCHES_SPEC.md).

## Acceptance criteria

Automated (`check_portraits.py`):
- [x] 27 grids, each 48×48
- [x] Every key has the sprite's hex or is a recorded extra; no UI marker hex, no violet; teal jacket at or below 60% saturation
- [x] Closed silhouette, empty row 0 and side columns, no outline on the crop row
- [x] Darkest step of every ramp only on contours
- [x] Pale hair never touches lit skin (Ivo); only `m` and `n` touch hair (Mira)
- [x] The three expressions of each character differ by at least 40 px and share their shoulders
- [x] Mira's patch icons sit on the jacket and each adds at least 5 px

Coordinator review (to be completed by the director):
- [x] Each portrait reads as the same person as its sprite at ×4 (hair shape and colour, costume, prop)
- [x] Hair does not read as a helmet in any of the three
- [x] The three expressions are distinguishable at ×4 without the labels
- [x] Ramps match the sprite in `portraits-sheet.png`

Review history: one self-review pass of three cycles. Cycle 1 failed on a helmet-like Engineer fringe and a brick pattern of strand dashes (both redrawn as swept tufts and continuous strand lines), a flat Ivo hairline (redrawn as a toothed fringe), tilt seams that exposed tufts or put a darkest step inside hair (the tilt now starts at row 0 and the hair/skin separation runs after the tilt), and an ear seam in a darkest-step key (now ink). Cycle 2 passed the checker. Director review then required Ivo's crown to be rebuilt from strand clusters because the first version read as a smooth mound; it was, and the checker and sheet were rerun.

## Vale (task 9.3, approved by the director 2026-10-02)

**Status:** Approved by the director 2026-10-02. `portrait_vale.py` is built on the same template and checked by the same `check_portraits.py` (30 grids, 0 failures). `build_portraits.py` adds Vale to `portraits-sheet.png` (fourth row) and to `portraits-atlas.png`/`.json` (row `vale`, appended after the Mira patch rows so no existing row moves). Sources: `design/characters/vale.md`, `cast/vale_sprites.py`, `cast/VALE_SPEC.md`.

| | Vale |
| --- | --- |
| Hair | Graphite `ABCD`: the sprite's cowlick (a tuft above the crown, standing out of a lower crown), the 1 px skin-coloured side part (`k`) left of centre, diagonal strand lines sweeping to the right, a lit `D` band on the upper left, and an uneven fringe: a long centre lock, a short lock at the right, a high left lock, and temple points. The ears show below the hair. |
| Skin | `klmn` as the sprite (pale ivory) |
| Clothing | Navy suit `pqrs` with the hard, square shoulder line (full width on row 37, not 40–41), a lit `s` edge on the left shoulder and sleeve, `o` seams between sleeves and torso, and a cool-white shirt V `wxy` |
| Accent | Green tie `tuv` (the knot's `v` glint on 1 px) and the copper badge `bcde` on screen-right (4×5, one `e` glint), as the sprite |
| Identity at 1× | Square shoulders, dark swept hair with a part, green tie, copper badge |

### Vale decisions

15. **Hair matches the sprite's idea, not its pixels.** The sprite's three features survive at ×2.4: the cowlick, the side part and the uneven fringe. The 3× larger head allows strand lines, which carry the "not a helmet" read where the narrow graphite ramp gives little contrast. The fringe stays put under the tilt (the tilt covers rows 0–10, as Ivo's covers 0–11).
16. **Brows use `B`** (graphite shadow), because the lightest hair step is much darker than the skin and `A` would read as black bars.
17. **Square shoulders.** The shoulder line drops from the neck to full width in two steps (rows 35–37) instead of sloping to row 40–41. The rules allow a per-character override (Ivo, row 39). Vale is the only cast member with flat shoulders.
18. **Seams are ink.** The sleeve seams use `#202337`, not the suit's darkest step: an `p` line inside one ramp breaks the contour-only rule (as for Mira's sleeve). `p` appears only on the lapel edges, beside the tie and the badge.
19. **Pleased is restrained: an almost-smile.** The kit's closed eyes and wide smile would read as warm and open, which is wrong for Vale's arc ("starts rigid, softens"). The `pleased` portrait keeps the neutral open eyes and the arched brows, with a 4 px mouth whose corners rise 1 px (`STAMPS["pleased"]` in `portrait_vale.py`). It tilts right like the other characters. The three expressions differ by well over 40 px.
20. **Mapping to the brief.** vale.md names composed (rigid), unsettled (evidence shown) and resolved (releases the audit): neutral is composed, concerned is unsettled, pleased is resolved, shown as the almost-smile.
21. **No extra palette steps.** Every key is a key of `vale_sprites.PAL` with the same hex; `EXTRA` is empty. `HAIR_SKIN_SEPARATED` is off for the same reason as on the sprite (the graphite hair is 29 L* darker than the skin).

Review: `check_portraits.py` ended at 30 portraits checked, 0 failures. Cycles: the first version had a flat fringe line and a light, blocky hair mass, and failed the row-0 rule, the crop-row outline (side outlines on columns 2 and 45 instead of 1 and 46), the darkest-step rule (a `p` sleeve seam) and the open silhouette under the tilt; the hair was then rebuilt with strand lines and a toothed fringe, and the tilt boundary was moved to row 10 with matching edge columns on rows 10 and 11. Coordinator review (to be completed by the director):
- [ ] Vale reads as the same person as the sprite at ×4 (hair, tie, badge, shoulders)
- [ ] Hair does not read as a helmet
- [ ] Neutral, concerned and the almost-smile are distinguishable at ×4

## Hal (task 9.3, approved by the director 2026-10-02)

**Status:** Approved by the director 2026-10-02. `portrait_hal.py` holds the hand-placed 48×48 `BASE` and the three built expressions (`neutral`, `concerned`, `pleased`). It imports `hal_sprites` and copies its `PAL`. It is registered in `check_portraits.py` and `build_portraits.py` and in the atlas (the last row, `hal`). `python3 check_portraits.py` reports 0 failures.

| | Hal |
| --- | --- |
| Hair | Sandy blond `ABCD`: a dome with three outline-capped spikes at the crown (the sprite's two spikes, one more for the larger head), strand lines in `B` running down-right, an uneven fringe that dips to a `k` shadow row and fringe tips, side locks that stop above the ears, and ears showing below them |
| Skin | `klmn` as the sprite. Light on the upper left, shadow on the right columns. A lit-skin `n` socket surrounds each eye. |
| Clothing | Cobalt utility vest `pqrs` with a lit left shoulder slope, a stone shirt V at the neck (`wxy`), a zip line in `q`, a chest pocket on the left, and stone sleeves at both edges |
| Prop | The orange tool roll `EFGH` at the lower right, under his left arm: a cream cord band, two steel tool tips (`h`, `j`) poking out of the top, one `H` glint. Its bottom row has no side outline, because the crop row carries none. |

Director decisions:

1. **One skull.** The face fill, eye line, mouth and chin are the shared template geometry, built on the Ivo head with Hal's own hair and torso.
2. **Brows use outline ink `o`.** Hair `A` is as dark as his skin `m`, so it would vanish, and the skin's darkest step `k` as a 5 px line fails the contour-only rule (all four neighbours are skin). Ink gives clear brows on his skin at ×4.
3. **Eyes in lit sockets.** The `BASE` carries `n` on rows 18–21 around the right eye (the left side is already lit), so the template's eye stamps sit on the lightest skin step. This follows the sprite revision.
4. **Hair and skin (`HAIR_SKIN_SEPARATED = True`).** Blond and golden skin are 13 L* apart, so light hair never touches `l`, `m` or `n`: the fringe shadow and the temples take `k`, as on the sprite. The tilt covers rows 0–11 only (crown tilts, fringe stays), as for Ivo.
5. **Vest slope and silhouette.** The slope is stepped with `#202337` outline along the upper edges, reaching full width on row 41 (the template's default).
6. **No extra palette steps.** `EXTRA` is empty. Every key is a key of `hal_sprites.PAL` with the same hex; the zip line uses `q` and not `p`, so the vest's darkest step stays on seams beside the stone collar and sleeves.
7. **Mapping to the brief.** Neutral is focused and practical, concerned is anxious (hal.md "Anxious", before the Alarm Glyphs fix), pleased is the settled "Focused" look after it. hal.md's third portrait, puzzled, is a later extra built with `STAMPS`.

## Ada (task 9.3, approved by the director 2026-10-02)

**Status:** Approved by the director 2026-10-02. `portrait_ada.py` holds the hand-placed 48×48 `BASE` and the three built expressions (`neutral`, `concerned`, `pleased`). Check: `check_portraits.py` ends at `36 portraits checked, 0 failures`. The sheet row and the atlas row are named `ada`.

| | Ada |
| --- | --- |
| Hair | Warm white `ABCD`, a fluffy crop built from clusters: three crown tufts with notches between them, a stepped outline with two side notches, lit `D` tops on the upper left of each cluster, `B` strand lines where clusters meet, and a fringe of uneven locks whose tips are `A` over an `l` cast-shadow row. Ears show below the hair. |
| Skin | `klmn` as the sprite, the deepest in the cast. Light on the upper left; a lit `n` band runs across both brow bones, the nose bridge and both cheekbones, so each eye sits in a lit socket. The right columns of the face and the neck take `l`. |
| Clothing | Moss coat `pqrs`: a lit left shoulder slope, a V neck of `l` skin with `p` edges, two lapel creases and a placket in `q`, two `w` buttons |
| Prop | The lantern's top at the lower right: a hand (`n m l`) on the ring, a cap with a `w` lit lip, and a glass of `g` core (5 px) and `f` glow in a `u`/`v` frame. It is cropped by the bottom edge. |

Director decisions (proposals):

1. **One skull.** The face fill, eye line, mouth and chin are the shared template geometry, built on the Ivo skeleton, with Ada's own hair, face shading and torso.
2. **Eyes and brows read on deep skin.** The eyes are the kit's 4×2 stamps with the lightest skin step `n` as the sclera. To make them read, the `BASE` puts `n` on row 18 across both brow bones, on the nose bridge (rows 19–21) and on rows 21–22 under both eyes. The neutral and pleased eyes, and the concerned heavy lids with their `l` under-eye shadow, therefore sit in a lit socket. The brows use the hair's mid step `B` (warm-white brows): `A` is too close to her skin in value, and the checker allows light hair beside skin here.
3. **Expression mapping (ada.md).** Neutral is calm, concerned is serious and instructive (practice-mode safety and recovery), pleased is warm (break room and service corridor lit). The kit's pleased arcs and smile read as warm on her face and need no override. The default tilt stays (concerned left, pleased right).
4. **Hair is clusters, not a cap.** Cluster centres are shaded individually, so light falls from the upper left on each tuft. The outline is notched on the crown and on both sides, and the fringe is uneven (the centre forelock hangs lowest). The 25 px hair box leaves ears visible.
5. **Hair and skin (`HAIR_SKIN_SEPARATED = False`).** Warm-white hair and deep skin are 21.9 L* apart (PALETTES_SPEC decision 9), so no separator is needed and the brows can use `B`. The fringe still sits on an `l` shadow row so the hair reads as lifted off the forehead, as for the others.
6. **No face rim, recorded.** A 1 px `R` column down the right cheek was tried to carry the lantern's rim (ada.md "warm light on one side of the face"). At ×8 it read as an earring beside the ear, so the portrait carries the lantern as a prop at the lower right instead and no `R` appears on the face. The `R` key stays a sprite-only key.
7. **Coat and slope.** The slope is stepped with `#202337` along its upper edges and reaches full width on row 41 (the template's default). The lapel creases and the placket use `q`, not `p`: a `p` line inside one ramp breaks the contour-only rule, as for Mira's sleeve and Vale's seams.
8. **Lantern.** `g` is limited to 8 px by the sprite's glint limit times four (5 used). The lantern is the sprite's colours exactly, and its frame uses the ink steps `u`, `v`, `w` as the sprite does.
9. **No extra palette steps.** `EXTRA` is empty. Every key is a key of `ada_sprites.PAL` with the same hex.

Review: `check_portraits.py` ended at 36 portraits checked, 0 failures. Cycles: the first version had a rectangular hair block that read as a cap and a noisy dither of `B` and `C` (rebuilt as shaded clusters with notches), `p` lapel lines and a `p` placket that failed the contour-only rule (now `q`), tuft pixels on the clear row 1 (moved to rows 2–3), and dark eyes lost in a dark face (the `n` brow-bone and cheekbone bands).

Coordinator review (to be completed by the director):
- [ ] Ada reads as the same person as the sprite at ×4 (hair, coat, lantern)
- [ ] Hair does not read as a helmet or a cap
- [ ] Eyes and brows read on her skin in all three expressions
- [ ] Neutral, concerned and pleased are distinguishable at ×4

## Noor (task 9.3, approved by the director 2026-10-02)

**Status:** Approved by the director 2026-10-02. `portrait_noor.py` is built on the same template and checked by the same `check_portraits.py` (39 grids, 0 failures). `build_portraits.py` adds Noor to `portraits-sheet.png` (last row) and to `portraits-atlas.png`/`.json` (row `noor`, appended after the existing rows so no row moves). Sources: `design/characters/noor.md`, `cast/noor_sprites.py`, `cast/NOOR_SPEC.md`.

| | Noor |
| --- | --- |
| Hair | Blue-black `ABCD`: the sprite's short swept crop with two crown tufts of different sizes and a notch between them, light `D` strand bands from the upper left, a stepped `A` hairline on the right with a dipping tip, a heavy left lock with uneven tips, and both ears showing |
| Skin | `klmn` as the sprite (light olive) |
| Clothing | Grey-oatmeal shirt `pqrs`: a narrow slope (full width on row 40, columns 5–42), a V neck flanked by the dark `p` neck line, a centre placket, sleeve seams in `q`, and a lit `s` left shoulder |
| Accent | The coral folder from the sprite sits behind her left (screen-left) shoulder: two tabs (sea-blue `j`/`J` and coral `e`), a coral face with a pale `f` highlight and a sea-blue label |
| Identity at 1× | Blue-black crop with tufts, pale shirt with a neck line, the folder behind the shoulder |

### Noor decisions

22. **Narrow shoulders.** The slope reaches full width on row 40 at columns 5–42, 6 px narrower than the template, because Noor is the narrowest person in the cast. The rules allow a per-character override (Ivo is wider, Vale is square).
23. **Hair is a crop, not a mound.** The sprite's tufts, stepped hairline and left lock survive. The strand bands carry the "not a helmet" read, the notch between the crown tufts breaks the top silhouette, and the ears show. The tilt covers rows 0–11 only, so the fringe stays put (as Ivo's and Vale's).
24. **Hair against skin.** The ramp gap is narrow (13 L*), so `HAIR_SKIN_SEPARATED` is on: skin touching light hair becomes `k`, and the right-hand hairline is the darkest step `A`. Brows use `A` so they do not take a `k` halo.
25. **Stamp not shown.** The stamp sits at her left hip on the sprite, below the portrait crop. Only the folder hint fits at the shoulder. Its pale `f` face is limited to 8 px (the sprite's limit of 8 times 4 is 32).
26. **Mapping to the brief.** noor.md: dry neutral is `neutral`, skeptical or defiant is `concerned`, quietly satisfied is `pleased`. The kit's closed eyes and smile read as warm but small on the narrow face, which suits her.
27. **No extra palette steps.** Every key is a key of `noor_sprites.PAL` with the same hex; `EXTRA` is empty.

Review: `check_portraits.py` ended at 39 portraits checked, 0 failures. The first run failed on `A` used as fill in the hairline tip (two stacked `A` rows); the tip's upper row is now `B`. Coordinator review (to be completed by the director):
- [ ] Noor reads as the same person as the sprite at ×4 (hair, shirt, neck line, folder)
- [ ] Hair does not read as a helmet
- [ ] Neutral, concerned and pleased are distinguishable at ×4
