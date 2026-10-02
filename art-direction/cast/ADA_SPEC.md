# Ada — sprite specification (idle ×4, walk ×4) and lantern rim-light ruling

**Status:** Approved by the director 2026-10-02.

**Sources:** `design/characters/ada.md`, `design/characters/README.md`, `levels.md` cast table and Night Shift levels 17–19, STYLE_BIBLE §3–7, [PALETTES_SPEC.md](../palettes/PALETTES_SPEC.md) (Night Shift palette, edge-light rule, Ada's skin and hair ramps). Every shared person rule follows the approved Gate 1 contract in [GATE1_ENGINEER_SPEC.md](../gate1/GATE1_ENGINEER_SPEC.md): frame, anchor, idle and walk timing, contour-only darkest step, renderer-drawn shadow. The cast frame rule comes from [IVO_SPEC.md](IVO_SPEC.md). **Director decision** marks choices made under the art-direction authority the player delegated.

## Deliverables

| File | What it is |
| --- | --- |
| `ada_sprites.py` | Hand-placed 16×24 key grids, the palette, the hand-and-lantern overlay and the walk composer. This is the pixel source of truth. Skin and hair come from `CAST_RAMPS["ada"]`, the lantern light and boots from the Night Shift ramps. |
| `ada-sheet.png` | All 24 frames at ×8, ×2 and ×1, with the anchor marked (on the Orientation stone, as for every cast sheet) |
| `ada-walks.gif` | The four walk cycles looping at ×6 |
| `ada-atlas.png` / `.json` | Native atlas. Rows S N E W idle, then S N E W walk. |
| `build_ada_room.py` | The Night Shift room and the ruling render. It imports `palette_swap`, `lamp_pool`, `rim_light` and `shadow` from `palettes/build_palettes.py` and `night_rim_on_scene` from `palettes/night_rim.py` without editing them. |
| `ada-in-nightshift.png` | A Night Shift room at ×4 on 1366×768: Engineer idle S, Ada idle S, a walk frame inside a lamp pool, and Ada idle N and W |
| `ada-rim-ruling.png` | The ruling at ×8: renderer rim only (A) against the baked head-and-shoulder lantern rim plus the renderer rim (B), on the dark floor and inside a lamp pool |

Rebuild: `cd art-direction/cast && python3 build_cast.py ada && python3 build_ada_room.py`. Check: `cd art-direction/gate1 && python3 check_gate1.py ada_sprites`.

## Silhouette (how Ada differs from the Engineer and Ivo at 1×)

| | Engineer | Ivo | Ada |
| --- | --- | --- | --- |
| Shoulders, S and N | 12 px | 14 px | 12 px (columns 2–13) |
| Body shape | jacket to legs | cardigan trapezoid, hem on row 17 | a belted long coat that falls straight to row 17, then flares to 14 px on rows 18–19: the only hem below the hip in the cast. A dark hem band closes it; only one row of trouser and the boots show below. |
| Hair | brown, swept, forelock | short silver cap, tufted crown | warm-white crop, fluffy: three crown tufts with notches between them, 12 px wide on rows 3–4 against a 10 px face, strand clusters, a zigzag fringe, a visible nape in N |
| Skin | mid warm | pale | deep warm brown, the deepest in the cast |
| Prop | optional badge | 5×4 tablet at the chest | 5×6 lantern at the hip: ring, lit cap, glass, base, held by a hand on the ring |
| Stance | asymmetric | level | level and still: arms hang, nothing swings |

## Director decisions

1. **Lantern rim-light ruling: both, baked and renderer.** Ada's lantern adds 1 px of baked rim on her own sprite, on the contour beside the lantern, in addition to the renderer's Night Shift rim, which is a cool moonlight rim `#8E96B8` since the player decision of 2026-10-02 (see the amendment under decision 1 and the note at the end). The renderer rule stays authoritative for everything else.
   - **What is baked (amended 2026-10-02: head and shoulders only).** The outermost contour pixel on the lantern's side of sprite rows 5-10 (hair edge, cheek, jaw, first shoulder; `HEAD_RIM_ROWS`, `bake_head_rim`) turns from the outline `#202337` into the key `R`, which is `#F9D79A`, accent step 3: six pixels per frame at most. The lantern-side rows 13-18 of the first ruling are gone: the lower body keeps its plain `#202337` outline. In S and E the lantern is at screen-right, so the pixels run down the right edge of the head and shoulders. In N and W it is at screen-left, so they run down the left edge. The renderer's cool moonlight rim never touches `R`, so on the open floor Ada carries a warm edge on her lantern side of the head and shoulders and a cool edge elsewhere.
   - **Why bake (the renders, `ada-rim-ruling.png`; reasoning of the first ruling, now limited to the head and shoulders by the amendment above).** The renderer rim only lights contour pixels that have transparent pixels above or to the left. In S and E the lantern sits on the lower-right contour, which that rule never lights. With the renderer alone the edge nearest the light source stays a dark outline at 2.1:1 against the floor fill (1.5:1 against the slab mid step; the cool moonlight rim of 2026-10-02 only lifts that to 2.5:1), and the lantern looks like a painted-on tag. With the baked pixels the contour beside the lantern is lit at 5.3:1, so the lantern visibly lights the body, and the silhouette closes on the lantern side. Inside a lamp pool the baked pixels still read at 2.7:1 against `#B8745A`.
   - **Why not baked-only.** Ada also needs the full upper-left rim like every other person, so the renderer rule applies to her unchanged. Baking the whole contour would also hard-code a Night Shift effect into a sprite that stands in four other districts.
   - **Why the baked pixels cost nothing in the other facings.** In N and W the lantern is already on the upper-left contour, so the baked pixels land where the renderer would have put them. Night Shift shows the same result, and the sprite stays self-consistent in every other district.
   - **How the renderer combines both.** Draw order for a person in Night Shift: floor, lamp pools, contact shadow (floor step 0 outer, `#202337` core), then the sprite with the rim pass applied (`night_rim_on_scene`, judged against the scene under the frame), then the blit. The rim pass is the per-pixel moonlight rule (PALETTES_SPEC rule 1). It never recolours baked `R` pixels (`#F9D79A`), so no pixel is lit twice. The renderer must not recolour, dilate or draw extra pixels beside `R`. In Orientation, Records, Systems and Executive there is no rim pass, and the six `R` pixels remain as a pale lantern-lit edge. They are nearly invisible on those light floors.
   - **Constraints.** `R` is on contour pixels only, on rows 5-10, at most 6 px per frame (`GLINT_LIMITS`). Because `R` now sits on head rows, the module sets the opt-in flag `HEAD_EXTRA_KEYS = "R"` and `gate1/check_gate1.py` reads it (a 2-line, backward-compatible change) so Gate 1's head-key rule still holds for every other sprite, and never a step of its own: it must equal accent step 3 if the Night Shift ramp ever changes. The lantern's own glow (`f`, `g`) is separate and lives inside the housing.
2. **Outline stays ink on every edge.** Ivo swaps short top-left runs of his outline for his dark fill step. Ada does not: every silhouette pixel is `#202337`, so the renderer's rim pass can reach the whole upper-left contour on the dark floor (and keep the ink outline in a lamp pool). The darkest coat step `p` appears only on seams, the belt and the hem band.
3. **Frame and sides.** Everything stays inside 16×24. The lantern is in her left hand, held against the body, never out to the side (the cast frame rule). It is at screen-right in S, at screen-left in N (her left from behind), and at the leading edge in E (screen-right) and W (screen-left). E and W are drawn separately: light stays upper-left in both, so their shading is not mirrored.
4. **Coat colour (closes ada.md open question 3 for the coat).** A moss olive, hue 74–85°, never teal, never violet: `#3C482B` (seams, belt, hem band), `#87A05E` (body), `#A7BC7B` (lit panels), `#C9D69F` (lit shoulder and collar). Reasons:
   - *Value.* The Night Shift floor fill is L\* 36. The coat body is L\* 63, 2.5:1 against the fill, and its lit steps are 3.5:1 and 4.7:1. The first, darker olive was 1.0:1 on the floor and was rejected after the first room render.
   - *Hue.* Warm against the cool slate floor and indigo walls, so the coat reads as a person and not as part of the district. It is distinct from the Engineer's teal, Ivo's terracotta and Mira's ochre-and-green: Mira's greens are hue 133–167°, Ada's coat is 74–85°.
   - *Markers.* Every coat step is at least dE 36 from the gold marker and 49 from the teal marker.
5. **Lantern.** Housing first, then a lit face, then a 2-step hard glow.
   - It is 5 px wide and 6 px tall: a ring the hand grips, a cap with a lit lip, a glass of 3×3, and a base, all inside a dark `#343650` frame with `#535971` and `#777A8C` steps. Facing S, E or W the glass shows a `#F9D79A` core on 2 px and a `#E8A55F` glow on the rest.
   - Both light steps are Night Shift accent steps 3 and 2: dE 25.3 and 16.8 from the gold marker. This replaces the Orientation brass named in ada.md (`#E1AC62` is dE 13.5 from gold).
   - `g` is limited to 2 px per frame (`GLINT_LIMITS`). There is no halo, no third glow step, and no marker hex.
   - Facing N the glass faces away, so the lantern shows its frame, cap and a lit side panel on its outer edge, with one `g` pixel.
   - The hand is a 2 px `n m` pair on the ring. It keeps the prop from reading as a tag on the coat, as Ivo's thumb does for the tablet.
6. **Hair and face (revised after director review).** Warm-white `CAST_RAMPS` hair as a fluffy crop, not a cap or helmet.
   - *Silhouette.* The top edge is broken by three tufts at rows 1–2 with two outline notches between them, then widens to 12 px on rows 3–4 and steps to 10 px. In S, N, E and W alike.
   - *Inside the mass.* Two darker strand clusters (`B` pairs on a diagonal over `C`/`D`) show on rows 3–4, plus the zigzag fringe of the darkest hair step `A` over the forehead.
   - *Nape.* N keeps a visible nape (`k` ears, an `A` hairline, `l` neck).
   - *Separation.* The fringe row puts `k` under every light hair pixel and lit `n` under `A`, so light hair never touches skin (`HAIR_SKIN_SEPARATED = True`, enforced).
   - *Eyes (2 px in S, 1 px in E and W).* Each eye is `#202337` set in a socket of her lightest skin step `n`: `n` on the brow above (under an `A` fringe pixel), `n` on both sides, and `n` on the cheek below, with the nose bridge `n` between the eyes in S. In E and W the single eye has `n` above, behind and below, and the cheek in front of it is `n`. No new hex: `n` is the lightest step of her ramp, and the eye contrast comes from ringing the dark pixel with it rather than with `k`.
   - Her skin shades to `k`, `l` and `m` at the sides and chin.
7. **Boots and trousers.** The boots use the Night Shift wood ramp (`#5E3A3E` `#8C5A4A` `#BC8260`), warm against a cool floor. The ink ramp `#535971` would vanish on the dark floor. Her trousers are warm charcoal and show on one row only (row 20), because the coat hem comes down to row 19.
8. **Walk, hem and lantern bob.** Shared timing and leg poses: 4 × 133 ms, contacts on frames 0 and 2, a 1 px settle, the Gate 1 stride limits. Ada adds three things:
   - The coat sways 1 px (ada.md): on passing frames one side of the hem band tucks in by a pixel.
   - Her arms do not swing, as Ivo's.
   - The hem and boots stay put on a settle. `eng.lower` drops coat row 17, so the coat compresses above the hem and the long hem never moves. On contact frames the hand and lantern settle 1 px with the body. On idle frame 1 the lantern does not move at all (ada.md "lantern still"), which the build verifies pixel by pixel.
9. **Contrast numbers (idle S, outline excluded).** 26% of body pixels reach 3:1 against the Night Shift floor fill. The PALETTES_SPEC rule (c) at 45% applies to light floors. Night Shift passes by the edge-light rule, and for Ada by the rim plus the baked pixels. The dark skin, the dark housing and the seams hold the number down by design.
10. **Scope.** This round is idle ×4 and walk ×4. The interact gesture (raising the lantern toward an object), the two reactions, walking alongside the player at NPC speed, and every EXTRA set come later. The portrait and its lantern-lit side come with the portraits task. Pronouns stay untouched: nothing in the sprite assumes any.

## Acceptance criteria

Automated (`check_gate1.py ada_sprites`):
- [x] 24 frames, each 16×24, with a pixel on row 23 and mass within 20% across the 7|8 anchor
- [x] No UI marker hex and no violet. Teal-hued steps at or below 60% saturation (the coat is hue 74–85°).
- [x] Head rows use only hair, skin and outline keys, plus the baked rim `R` that Ada opts into (`HEAD_EXTRA_KEYS`)
- [x] The darkest hair step appears only on contour and occlusion edges
- [x] Light hair never touches light skin (`HAIR_SKIN_SEPARATED`)
- [x] Glint limits: `g` at most 2 px and `R` at most 6 px in every frame (`GLINT_LIMITS`)
- [x] Walk strides never touch columns 0 or 15

Coordinator review (to be ticked by the director after looking at `ada-sheet.png`, `ada-in-nightshift.png` and `ada-rim-ruling.png`):
- [x] Reads as a different person from the Engineer, Ivo and Mira at 1×: long coat, hair, deep skin, prop
- [x] The lantern reads as a lantern at ×4 (frame, lit glass, ring, hand), including from behind
- [x] The silhouette and edges read on the dark Night Shift floor and inside a lamp pool
- [x] The rim ruling is accepted

## Extra animation sets (approved by the director 2026-10-02)

Tasks 8.1 and 8.2. Same format as the Engineer's, Ivo's and Mira's: `EXTRA[set][facing]`, `EXTRA_MS`, `EXTRA_MODE` and `EXTRA_ASYMMETRIC` in `ada_sprites.py`, built into `ada-atlas.png` / `.json` (one row per set and facing, after the eight base rows), `ada-sheet.png` and `ada-extra.gif`. Check: `check_gate1.py ada_sprites` prints `55 frames checked (24 base + 31 extra), 0 failures`. `IDLE` and `WALK` are unchanged: a dump taken before and after matches pixel for pixel.

| Set | Facings | Frames | Timing | Mode |
| --- | --- | --- | --- | --- |
| `interact` | S N E W | 2 | 250 ms | once, hold last |
| `react_nod` (ada.md reaction a, "calm nod") | S N E W | 3 | 300 ms | once, hold last |
| `react_explaining` (reaction b, "serious, explaining the recovery steps") | S N E W | S 3, N 2, E 3, W 3 | 300 ms | once, hold last |

Director decisions (proposals):

1. **Built from the raw grids.** Extra frames start from the raw `S N E W` grids (coat, head, boots), apply stamps or `eng.dip`, and paint the hand and lantern last with `hold()`. The finished `IDLE` and `WALK` frames are never edited.
2. **Interact: raise the lantern toward a panel.** Frame 0 lifts the lantern 1 px and moves it 1 px toward the facing; frame 1 lifts it 2 px and moves it 2 px (S and E to screen-right, N and W to screen-left; N moves it 1 px). The hand follows on the ring. The ring never rises above row 10, so the head rows stay clean. In E and W the lantern leaves the body: it reaches column 14 in E and column 1 in W, and S reaches column 14.
3. **The baked rim stays on the head and shoulders (amended 2026-10-02).** The first version made the baked rim follow the lantern body, down to row 18. The player limited warm edges to the head and shoulders, so in every frame (idle, walk and all extra sets) `R` is baked by `bake_head_rim` on rows 5-10 on the lantern's side, whatever the lantern does. Raising the lantern in interact and explaining moves only the lantern; the rim stays put. The renderer's rim pass skips `R` explicitly.
4. **Lantern still during reactions.** In the nod and the explaining bow the head dips with `eng.dip` while the lantern, hand and rim stay at their rest position, as in the idle. Only the explaining set in E and W lifts the lantern (1 px, then 2 px), as a presenting gesture.
5. **Nod.** Head down 1 px, down 2 px, back to 1 px, on all four facings. It holds the last frame, so it ends slightly bowed, and the engine returns to idle.
6. **Explaining.** The head bows and holds. In S her free hand (her right, screen-left) leaves the hip, comes to the belt with the palm out (frame 1) and rises to the chest (frame 2): a 2×2 hand of `n m / m l` on the coat, with no outline, as on Mira's and Ivo's stamps. N only bows and settles 1 px, since her hands are out of sight. E and W present the lantern as described above, because her free hand is on the far side.
7. **Balance.** `interact` and `react_explaining` are listed in `EXTRA_ASYMMETRIC` because the raised lantern and the gesturing hand move mass off the anchor. The checker's relaxed tolerance of 30% applies to them.
8. **Not included.** Walk alongside (a base walk at NPC speed, engine side), expression variants beyond these two, and the light-up props of Night Shift levels 17–19 stay for later.

**Rim rule extended (director decision, 2026-10-02, task 7.3):** the renderer rim pass also lights any upper-left silhouette pixel below 3:1 against the Night Shift floor fill, not only `#202337` pixels (the Engineer's dark contour steps left 24% of his edge unlit). Baked `R` pixels are still never relit.

**Rim ruling amended (player decision, 2026-10-02, two steps):** people's renderer rim is no longer the warm `#F9D79A` (it read as a "selected" highlight and sat near discovery gold). It is a cool moonlight rim `#8E96B8` (Night Shift glass step 2) by a per-pixel rule: an upper-left silhouette pixel is recoloured only if it is `#202337` or below 3:1 against the scene behind it, and the rim contrasts with that background more than the pixel does. On the slate floor the rim shows (2.49:1 against the ink's 2.13:1); inside a lamp pool the ink outline stays (4.19:1 against the rim's 1.27:1). Second step, same day: "cool moonlight on the open floor; where a warm source lights someone (inside a lamp pool, Ada's lantern), the warm edge is limited to the head and shoulders". In a lamp pool the renderer draws the warm `#F9D79A` on the upper-left head and shoulders (rows 0-12, `WARM_RIM_ROWS`, 2.68:1 against `#B8745A`) and the body keeps its ink outline (4.19:1). Ada's baked lantern rim (R, `#F9D79A`) follows the same limit: it moved from the lantern rows (13-18) to the lantern-side head and shoulders (rows 5-10), and the renderer never recolours it. `ada-rim-ruling.png` shows both. Reference implementation: `night_rim` in `palettes/night_rim.py` (`nightshift_kit.night_rim`); `ada-in-nightshift.png` and `ada-rim-ruling.png` are rebuilt with it, and the ruling image's lantern-side comparison (A against B) is unchanged in meaning.
