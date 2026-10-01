# Mira — sprite specification (idle ×4, walk ×4)

**Status:** REVIEW_REQUIRED. The player reviews this set.

**Sources:** `design/characters/mira.md`, `design/characters/README.md`, `levels.md` (cast table and Mira routes), STYLE_BIBLE §3–7. The shared person rules come from the approved [Gate 1 spec](../gate1/GATE1_ENGINEER_SPEC.md): frame, anchor, idle and walk timing, the contour-only darkest step, and the renderer-drawn shadow. The cast frame rule comes from the approved [Ivo spec](IVO_SPEC.md). **Director decision** marks choices made under the art-direction authority the player delegated.

## Deliverables

| File | What it is |
| --- | --- |
| `mira_sprites.py` | Hand-placed 16×24 key grids, the palette and the bag overlay. This is the pixel source of truth. |
| `mira-sheet.png` | All 24 frames at ×8, ×2 and ×1, with the anchor marked |
| `mira-walks.gif` | The four walk cycles looping at ×6 |
| `mira-atlas.png` / `.json` | Native atlas. Rows S N E W idle, then S N E W walk. |
| `mira-in-room.png` | Mira at the mail counter in the review room, at ×4 |

Rebuild with `python3 build_cast.py mira`. Check with `python3 ../gate1/check_gate1.py mira_sprites`.

## Silhouette (how Mira differs from the Engineer and Ivo at 1×)

| | Engineer | Ivo | Mira |
| --- | --- | --- | --- |
| Head top | swept brown hair | short silver cap | a high dark puff that rises above the crown, separated from it by a 1 px notch |
| Torso | teal jacket | broad terracotta cardigan | a two-panel jacket: green on her right side and sleeve, ochre on the main panel |
| Prop | optional badge | tablet held flat | coral strap from her right shoulder to a buckled coral bag on her left hip |
| Posture | asymmetric stance | level stance | leans into her facing direction: the head sits 1 px ahead of the body in E and W, and her feet are staggered |
| Walk | shared stride | shared stride, arms still | a longer side-view stride (contacts one column wider) with the same 4 × 133 ms timing |

## Director decisions

1. **Frame.** Following the cast rule, everything stays inside 16×24. The bag breaks the jacket outline on her left hip but not the frame.
2. **Panel side.** The green panel is on her right, following mira.md's text. The scale-test placeholder had it on her left, and that version is retired.
3. **Hair puff.** It is fixed to her own left, consistent with the Engineer's sweep: screen-right facing S, screen-left facing N, and at the back of the head facing E or W. The notch between puff and crown is drawn in outline ink, because it's an overlap edge.
4. **Bag.**
   - It is drawn once per facing and painted onto every frame.
   - Its parts are a `#E67A70` lit lip with one `#F6B18E` glint, a `#71394F` flap line, an ink buckle (`#777A8C`), a `#B65761` body and a dark frame.
   - The body never uses `#E67A70`, which matches the conversation marker, the coral chairs and the counter's strap.
   - Facing S it is on the screen-right hip. Facing N you see its back on the screen-left hip. Facing W it is on the near hip, forward of the body edge. Facing E it is on the far hip, showing behind her back.
5. **Coral is hers.** Coral appears only on the bag and strap. Her shoes use the ink ramp, which resolves mira.md assumption 2. This does not limit the colours of her future patches.
6. **Strap.** A 1 px `#E67A70` diagonal runs from her right shoulder to the bag, with a `#71394F` shadow step on its lower-right side. It crosses only the mid-dark panel steps, `#9A6A3E` and `#326D60`, so it stays clear.
7. **Panel tones.**
   - Below the shoulders the ochre fills with `#9A6A3E` and the green with `#326D60`. The lit `#C99A4E` / `#5FA06D` steps stay on the shoulder rows.
   - `#EDCB7A` appears on at most 1 px, so the large ochre panel never reads as the gold marker.
   - `#B2CE78` appears on at most 1 px, so the green panel can't merge with foliage tips.
8. **Face.** Her hair and skin have almost the same luminance, so only her lighter skin steps (`#85563F`, `#A9744F`) touch hair.
   - The fringe underside is the darkest hair step, which acts as the hair-shadow line.
   - Her eyes sit on `#A9744F`.
   - There is no shadow row at the chin. One was tried and rejected because it read as a beard at ×4.
9. **Bob.** S and N drop row 17. E and W drop the top leg row, so the bag's base row survives the settle.
10. **Patches.** The base set has none, because the first patch is earned after level 02. The six patch designs stay open. Patches will be 1–2 px clusters on the bag flap and the jacket, added as states.
11. **Room.** The slate planter that crowded her hair puff moved from (278,126) to (238,126).
12. **Scope.** This round is idle ×4 and walk ×4. Interact, reactions, patches and the Night Shift strap exception (mira.md open question 2) come later.

## Acceptance criteria

Automated (`check_gate1.py mira_sprites`):
- [x] 24 frames, each 16×24, with a pixel on row 23 and mass within 20 % across the 7|8 anchor
- [x] No UI marker hex and no violet. Teal-hued steps at or below 60 % saturation.
- [x] Head rows use only hair, skin and outline keys
- [x] The darkest hair step appears only on contour and occlusion edges

Coordinator review:
- [x] Reads as a different person from the Engineer and Ivo at 1× and at ×4
- [x] Bag on her left hip in every facing, drawn separately for E and W, with a flap line and buckle
- [x] Strap readable as a clean diagonal in S, N, E and W
- [x] The puff reads as hair, not as a helmet or a hat, and the ears and temples show
- [x] Distinct from the mail counter, the planter and the coral chairs in the room

Player:
- [ ] Mira reviewed in the room and on the sheet
