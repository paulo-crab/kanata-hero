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
