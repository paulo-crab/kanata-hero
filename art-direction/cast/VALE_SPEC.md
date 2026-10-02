# Vale — sprite specification (idle ×4, walk ×4)

**Status:** Approved by the director 2026-10-02.

> **Rich finish (2026-10-02):** the outline colour is now `#0E1020` and the ink shoe ramp and renderer shadow move to the deeper ink ramp (`#1C2038` `#3A4160` `#6A7392`). Clothing, skin and hair ramps in this spec stay as approved. The sprites are queued for that recolour (OpenSpec change `adopt-rich-finish`); see `../rich-finish/RICH_FINISH_SPEC.md`.

**Sources:** `design/characters/vale.md`, `design/characters/README.md`, `levels.md` cast table and level 20, `art-direction/palettes/PALETTES_SPEC.md` (Executive palette and `CAST_RAMPS["vale"]`), STYLE_BIBLE §3–7. Every shared person rule follows the approved Gate 1 contract in [GATE1_ENGINEER_SPEC.md](../gate1/GATE1_ENGINEER_SPEC.md): frame, anchor, idle and walk timing, contour-only darkest step, and renderer-drawn shadow. The cast frame rule comes from [IVO_SPEC.md](IVO_SPEC.md). **Director decision** marks choices made under the art-direction authority the player delegated.

This delivery is softening **state 0 (0 repairs)**: rigid, square shoulders, arms tight, feet together. The three later states and the interact and reaction sets are left out for now (EXTRA sets, later).

## Deliverables

| File | What it is |
| --- | --- |
| `vale_sprites.py` | Hand-placed 16×24 key grids and the palette. This is the pixel source of truth. Skin and hair ramps are read from `CAST_RAMPS["vale"]`; the tie and badge ramps from the Executive district ramps. |
| `vale-sheet.png` | All 24 frames at ×8, ×2 and ×1, with the anchor marked |
| `vale-walks.gif` | The four walk cycles looping at ×6 |
| `vale-atlas.png` / `.json` | Native atlas. Rows S N E W idle, then S N E W walk. |
| `build_vale_room.py` | Writes the in-context render below. Reuses `palette_swap` and `shadow` from `../palettes/build_palettes.py` (not edited). |
| `vale-in-executive.png` | An Executive-palette atrium at ×4 on 1366×768: Vale idle S and walk frames beside the Engineer, Vale against a plain navy wall panel, a glass bay and the brighter alcove wall, and against the navy seating. The tree is Orientation's garden recoloured. A 1× strip of the frames sits in the bottom margin. |

Rebuild with `python3 build_cast.py vale` and `python3 build_vale_room.py` (Pillow and numpy). Check with `python3 ../gate1/check_gate1.py vale_sprites`.

## Silhouette (how Vale differs from the Engineer, Ivo and Mira at 1×)

| | Engineer | Ivo | Mira | Vale |
| --- | --- | --- | --- | --- |
| Shoulders, S and N | 12 px, rounded | 14 px, rounded top row | 14 px, rounded | 14 px (columns 1–14) with a **flat top row and hard corners**, the only square shoulders in the cast |
| Taper | jacket to legs | trapezoid, widest at the hem | puff and bag | inverted: 14 px shoulders, a 12 px hem (row 17), 9 px trousers. A suit V |
| Arms | swing | still, tablet | swing, bag | tight to the body and still: a 1 px seam line separates each sleeve from the torso, cuffs and hands at the hips |
| Hair | brown, swept | silver cap with tufts | plum-black puff | dark graphite: a 2 px cowlick tuft above the crown, a skin-coloured side part, a 1 px pompadour overhang on the swept side, an uneven fringe |
| Prop | optional badge | tablet | bag | copper badge on the lapel, with a green tie beside it |
| Stance | asymmetric | level | leaning | level, feet together (rigid) |
| Colour | teal jacket | terracotta | ochre and green | **navy suit**, cool white shirt, walnut shoes |

## Director decisions

1. **Suit ramp.** `#262B46` (p, contour and seams) `#3C4465` (q, fill) `#566089` (r, lit fill) `#9AA6C8` (s, lit edge). The hue is 224–230° like the Executive wall, but the saturation is 22–29 % against the wall's 38–47 %, so the suit reads as ink navy beside the royal-navy wall. Distance (dE76) from the wall ramp: q is 12.5 / 15.7 / 22.7 / 28.9 from wall steps 0–3 and s is 19.5 from step 3 (`#6B84BE`). This closes the palette spec's note that the wall's darkest step is dE 7 from the placeholder suit.
2. **Lit edge.** The `s` step is a 1 px edge only: the top of both shoulders (with `r` on the right shoulder), the left arm's outer column on S and N, the back edge on E and W. It never fills an area. The `#202337` outline wraps the whole sprite, so `s` never touches the wall directly, and it keeps the jacket separate from the baseboard and the navy seating (tested in the render).
3. **Trousers.** Own values (`#2A2F4C` / `#3A4162`), a step darker than the jacket, instead of the shared placeholder `#2C3352` / `#3E4870`. Same fabric as the jacket, with the jacket hem (row 17) and the shoes separating them.
4. **Shirt.** Cool white (`#A9B0C6` `#DDE2EC`, one `#F4F2EC` tip), not the warm pale stone vale.md assumed. Vale's skin is warm ivory (`#E9CDAE`), and a warm stone collar merged with the neck in the first pass.
5. **Tie.** Living green from the Executive foliage ramp (`#1B4A34` `#2F7A45`, with `#5FAF55` on 1 px as the knot's lit corner). It ties Vale to the atrium. Hue 140–150°, outside the teal range and 32+ dE from the teal marker. The tie is the hook for the later softening states (it loosens).
6. **Copper badge.** A 2×3 tag on Vale's left lapel, drawn from the Executive copper ramp: `#5E2F2B` frame at the foot, `#A4573A` and `#D88149` face, `#F2B98A` glint on 1 px. Dark seam lines frame it on both sides. S shows it on screen-right. W shows it in full on the near chest. E shows a 1×2 sliver on the far lapel's edge, and N shows none. It is the only warm accent on the figure. The copper is dE 27–30 from the gold marker (it never uses the marker hex), which closes vale.md assumption 2 (copper on the brass ramp) with the true copper.
7. **Hair.** The fixed graphite ramp (`CAST_RAMPS["vale"]`). The graphite steps are close together, so structure comes from shape and not from contrast:
   - a cowlick tuft above the crown (row 0), kept in all four facings;
   - a skin-coloured side part, 2 px, on S;
   - a 1 px pompadour overhang on the swept side (screen-right on S, screen-left on N, front on E and W);
   - an uneven fringe with one darkest tip dipping into the forehead shadow;
   - the nape, with a tapered hairline, visible on N.
   A uniform cap with a flat fringe line was tried first and read as a bowl. Two tufts were tried and read as horns. The set is a single cowlick.
8. **Hair and skin.** `HAIR_SKIN_SEPARATED = False`. The graphite fill steps are 29 L* darker than the lightest skin fill, so hair never touches skin of equal luminance, and the flag stays off. The ramps themselves were checked in task 5.2.
9. **Shoes.** Walnut from the Executive wood ramp (`#3A2630` `#5E3B38` `#8A5A45`). They read on the pale floor and in front of the navy seating, and no other cast member has brown shoes.
10. **Rigid walk (state 0).** The shared 4 × 133 ms cycle with contacts on frames 0 and 2 and a 1 px bob. Neither arm swings. The legs and bob are the whole motion, which gives vale.md's "stiff at state 0". The side stride stays inside columns 2–14.
11. **Settle.** `lower()` is Ivo's: it drops the top leg row, not the hem row, so the jacket keeps its hem and the cuffs keep clear of the trousers. `eng.lower` would drop row 17 and bring the hands onto the trousers.
12. **Pronouns.** Left unmarked (they/them): the face is a plain composed one (flat mouth, no lashes, no facial hair), and the cut is a suit, not a gendered silhouette.
13. **Glints.** `GLINT_LIMITS = {"e": 1, "v": 1, "y": 3}` (the copper glint, the knot highlight, the lightest shirt step), enforced by the checker.
14. **Scope.** This round is idle ×4 and walk ×4 at state 0. The three softening states (shoulders drop 1 px; arms relax with weight on one leg; open asymmetric stance), interact and the two reactions come later as EXTRA sets on these frames.

## Acceptance criteria

Automated (`check_gate1.py vale_sprites`: 24 frames checked, 0 failures):
- [x] 24 frames, each 16×24, with a pixel on row 23 and mass within 20 % across the 7|8 anchor
- [x] No UI marker hex and no violet. Jacket steps at hue 224–230°, outside the teal range.
- [x] Head rows use only hair, skin and outline keys
- [x] The darkest hair step appears only on contour and occlusion edges
- [x] Glint counts within `GLINT_LIMITS`, and the stride never touches columns 0 or 15

Coordinator review (to be ticked by the director after looking at `vale-sheet.png` and `vale-in-executive.png`):
- [x] Reads as a different person from the Engineer, Ivo and Mira at 1×: square shoulders, navy suit, graphite cowlick, copper tag
- [x] The copper badge reads as a badge (frame, lit face, glint) in S and W, and a sliver on E
- [x] Hair does not read as a helmet in any of the four facings
- [x] The suit separates from the Executive wall panel, the glass bay, the alcove wall and the navy seating, and carries the silhouette on the pale floor
- [x] The rigid walk reads as stiff and still-armed, and the side stride stays clear of the frame edge
- [x] Gold stays small, with no teal-hued or violet clothing

## Extra animation sets (approved by the director 2026-10-02)

Tasks 8.1 (interact) and 8.2 (reactions). Same format as the Engineer, Ivo and Mira: `EXTRA`, `EXTRA_MS`, `EXTRA_MODE` and `EXTRA_ASYMMETRIC` in `vale_sprites.py`, built from the approved idle frames plus hand-placed stamps. `IDLE`, `WALK` and `PAL` are unchanged (dumped and diffed before and after). `build_cast.py vale` adds `vale-extra.gif`, the extra rows of `vale-atlas.png`/`.json` (rows 8–19) and the extra frames on `vale-sheet.png`. `check_gate1.py vale_sprites`: 56 frames checked (24 base + 32 extra), 0 failures.

| Set | Facings | Frames | Timing | Mode |
| --- | --- | --- | --- | --- |
| `interact` | S N E W | 2 | 250 ms | once, hold last |
| `react_displeased` | S N E W | 3 | 300 ms | once, hold last |
| `react_reconsidering` | S N E W | 3 | 300 ms | once, hold last |

### Extra decisions

15. **Interact: the audit.** vale.md says "receiving or releasing the audit". Vale carries a 5×4 pale sheet low, then holds a 6×5 sheet out (it grows because it is nearer the player, as Ivo's tablet does). The sheet is a dark rim, alternating `w`/`x` lines read as text, and one `c` copper clip on the top edge. S: at Vale's right (screen-left), the hand grips its lower edge. E and W: held out toward the facing. N: only the back of the sheet shows past the shoulder. The sheet stays inside 16×24, so it uses columns 0–5 on S, W and N. It uses no new key, and `y` stays inside its glint limit. `EXTRA_ASYMMETRIC` includes `interact`.
16. **Reaction: displeased (stiff).** vale.md's "composed" is the idle, so reaction (a) is the stiff counterpart: the head bows a notch (`dip`), a level brow pixel is added above the eyes, and the mouth corners drop onto the chin. On S the fists clench on the last frame (hands take the skin shadow steps) and the figure settles 1 px (`lower`). The face is the sprite's single ink pixels, so it reads through the brow and mouth, not through eye shape. A 2 px dark furrow was tried and read as an eye patch; it was dropped.
17. **Reaction: reconsidering (the first softening).** vale.md's reaction (b) is "unsettled on seeing raw evidence". It is the first step of the arc, so it plays the first softening state's change: the head tilts 1 px, the hard corners of the shoulder line are cut (`sag`: the shoulders drop 1 px), and the figure settles. The last frame is the state-1 silhouette, so the same `sag` can be applied to the idle frames when the engine switches to repair 1.
18. **Held frame.** Both reactions end on a frame that is a valid resting pose; the engine holds it until the dialogue closes.
19. **Open.** The state 2 and 3 poses (arms relax, weight on one leg, open stance) and the portrait expressions are still to do. N has no face, so its reactions only move the head and shoulders.
