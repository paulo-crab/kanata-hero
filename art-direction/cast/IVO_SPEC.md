# Ivo — sprite specification (idle ×4, walk ×4)

**Status:** APPROVED by the player on 2026-10-02. The Director decisions below are canon for Ivo, and the cast frame rule applies to every person.

**Sources:** `design/characters/ivo.md`, `design/characters/README.md`, `levels.md` cast table and levels 01–06, STYLE_BIBLE §3–7. Every shared person rule follows the approved Gate 1 contract in [GATE1_ENGINEER_SPEC.md](../gate1/GATE1_ENGINEER_SPEC.md): frame, anchor, idle and walk timing, contour-only darkest step, and renderer-drawn shadow. **Director decision** marks choices made under the art-direction authority the player delegated.

## Deliverables

| File | What it is |
| --- | --- |
| `ivo_sprites.py` | Hand-placed 16×24 key grids and the palette. This is the pixel source of truth. |
| `ivo-sheet.png` | All 24 frames at ×8, ×2 and ×1, with the anchor marked |
| `ivo-walks.gif` | The four walk cycles looping at ×6 |
| `ivo-atlas.png` / `.json` | Native atlas. Rows S N E W idle, then S N E W walk. |
| `../gate1/gate1-scene-1366x768.png` | Ivo in the review room at his Level 01 spot, beside the printer |
| `ivo-furniture-test.png` | Ivo idling beside the bench, a desk and the sofa, the wood-ramp separation test |

Rebuild with `python3 build_cast.py ivo`. Check with `python3 ../gate1/check_gate1.py ivo_sprites`.

## Silhouette (how Ivo differs from the Engineer at 1×)

| | Engineer (approved) | Ivo |
| --- | --- | --- |
| Shoulders, S and N | 12 px | 14 px (columns 1–14), the widest in the cast |
| Taper | jacket to legs, about 1.5 : 1 | cardigan to legs, about 1.75 : 1, a trapezoid |
| Hem | row 16, at the waist | row 17, over the hips |
| Hair | brown, swept to the character's left, with a forelock | short silver hair: a tufted crown with strand clusters, a fringe tip dipping into a forehead shadow, and ears showing below the hair at the sides, so it never reads as a helmet |
| Head | rows 0–9, 10 px wide | rows 1–9, 10 px wide: the same head width as the Engineer, 1 px shorter |
| Stance | asymmetric; the unweighted foot may sit 1 px up | level: both feet rest on row 23 (ivo.md "level stance") |
| Prop | optional badge | 5×4 tablet held flat at the chest: dark bezel, bright screen, a thumb on the edge |

## Director decisions

1. **Frame width (decided for the whole cast).** Every person stays inside the 16×24 frame. Ivo's tablet is held against the front of the body, not out to the side. This amends ivo.md's "held out / extends to the side", because a side-held tablet beside a 14 px cardigan would overhang the frame.
2. **Tablet side.** Always in Ivo's left hand.
   - S: at screen-right, chest to hip.
   - N: its back shows at screen-left, in ink.
   - E and W: in front of the torso, at the leading edge.
3. **Tablet colour (closes ivo.md open question 1).**
   - It is held flat at the chest, so from above its whole face shows. It is a 5×4 rectangle: a dark `#203A50` bezel, a bright `#5AA3AE` screen with one `#366479` content line, and Ivo's thumb on the near edge. An earlier 4×3 version with no bezel was rejected because it didn't read as a tablet.
   - The `#A0DDD4` glint is limited to 1 px.
   - The tablet never uses `#19AFA2`, never has a step above 60 % HSL saturation, and never has a halo.
   - The back is ink.
   - The base set is steady. The Level 03 flash is a later variant that alternates glass steps only.
4. **Hair/skin separation.** Ivo's silver steps match the luminance of his pale skin, so the hair never touches lit skin directly. The forehead gets a soft skin shadow (`#8A5A4A`) under the fringe, with one darker fringe tip (`#535971`) dipping into it, and the same shadow frames the ears and nape. A flat grey rim was tried and rejected because it made the hair read as a helmet. Light hair never touches light skin without a darker pixel between them. `check_gate1.py` enforces this with the module flag `HAIR_SKIN_SEPARATED`.
5. **Ochre strip.** It uses mostly `#9A6A3E` / `#C99A4E`, with `#EDCB7A` on 1 px only, so it can't read as the gold discovery marker. In S it runs from row 10 to row 14, bordered by dark cardigan edges (`#523D4C`) that read as the open front, and the cardigan closes below. It is shorter in E and W, where the tablet covers it.
6. **Furniture separation.** The cardigan shares the wood ramp with the desks, bench and sofa. Ivo's outer contour stays `#202337`, and only short top-left runs swap to `#523D4C`. The silver hair, navy legs, ochre strip and glass tablet carry the read. This was tested beside the bench, a desk and the sofa.
7. **Walk and bob.** Ivo uses the shared timing and leg poses: 4 × 133 ms, contacts on frames 0 and 2, and a 1 px bob. Unlike the Engineer, neither arm swings. The tablet arm and the free arm stay still, which gives the measured pace. Ivo's bob drops the top leg row instead of the hem row, so the cardigan keeps its taper on idle frame 1 and on contact frames. A slower NPC speed is left to the engine.
8. **Scope.** This round is idle ×4 and walk ×4. The scripted wave, nod, unscripted laugh, interact and Level 03 flash come later.

## Acceptance criteria

Automated (`check_gate1.py ivo_sprites`):
- [x] 24 frames, each 16×24, with a pixel on row 23 and mass within 20 % across the 7|8 anchor
- [x] No UI marker hex and no violet. Teal-hued steps at or below 60 % saturation.
- [x] Head rows use only hair, skin and outline keys
- [x] The darkest hair step appears only on contour and occlusion edges
- [x] Light hair never touches light skin

Review history: two specialist reviews (character, style), then continuity cycle 1 (FAIL: hair/skin contacts, a dark tablet, an 8 px head, a long strip, the hem lost on bob, and no furniture render). All were fixed in cycle 2, along with a checkered hair pattern caught in the coordinator's own review.

Coordinator review:
- [x] Reads as a different person from the Engineer at 1×: shoulders, taper, hem, hair and stance
- [x] Tablet reads as a device (bezel, screen, thumb), is 5×4 in S, E and W, and shows its back in N, on Ivo's left in every facing, with E and W drawn separately
- [x] Distinct from the bench, desk and sofa at native scale
- [x] Not readable as a terminal or a gold marker

Player:
- [x] Ivo reviewed in the room and on the sheet (approved 2026-10-02, after a tablet and hair revision)
