# Mira — sprite specification (idle ×4, walk ×4)

**Status:** APPROVED 2026-10-02 by the art director, under the player's standing delegation to self-review and approve. The Director decisions below are canon for Mira.

**Sources:** `design/characters/mira.md`, `design/characters/README.md`, `levels.md` (cast table and Mira routes), STYLE_BIBLE §3–7. The shared person rules come from the approved [Gate 1 spec](../gate1/GATE1_ENGINEER_SPEC.md): frame, anchor, idle and walk timing, the contour-only darkest step, and the renderer-drawn shadow. The cast frame rule comes from the approved [Ivo spec](IVO_SPEC.md). **Director decision** marks choices made under the art-direction authority the player delegated.

## Deliverables

| File | What it is |
| --- | --- |
| `mira_sprites.py` | Hand-placed 16×24 key grids, the palette and the bag overlay. This is the pixel source of truth. |
| `mira-sheet.png` | All 24 frames at ×8, ×2 and ×1, with the anchor marked |
| `mira-walks.gif` | The four walk cycles looping at ×6 |
| `mira-atlas.png` / `.json` | Native atlas. Rows S N E W idle, then S N E W walk. |
| `mira-in-room.png` | Mira at the mail counter in the review room, at ×4 |
| `mira-clear-floor.png` | Every facing plus walk contacts on open floor, with no counter hiding the bag or feet |

Rebuild with `python3 build_cast.py mira`. Check with `python3 ../gate1/check_gate1.py mira_sprites`.

## Silhouette (how Mira differs from the Engineer and Ivo at 1×)

| | Engineer | Ivo | Mira |
| --- | --- | --- | --- |
| Head top | swept brown hair | short silver cap | a high dark puff that rises above the crown, separated from it by a 1 px notch |
| Torso | teal jacket | broad terracotta cardigan | a two-panel jacket: green on her right side and sleeve, ochre on the main panel |
| Prop | optional badge | tablet held flat | coral strap from her right shoulder to a buckled coral bag on her left hip |
| Posture | asymmetric stance | level stance | leans into her facing direction: the head sits 1 px ahead of the body in E and W, and her feet are staggered |
| Walk | shared stride | shared stride, arms still | the shared overhead stride with her trailing heel lifting off on contacts, and a 1 px bag swing |

## Director decisions

1. **Frame.** Following the cast rule, everything stays inside 16×24. The bag breaks the jacket outline on her left hip but not the frame.
2. **Panel side.** The green panel is on her right, following mira.md's text. The scale-test placeholder had it on her left, and that version is retired.
3. **Hair puff.** It is fixed to her own left, consistent with the Engineer's sweep: screen-right facing S, screen-left facing N, and at the back of the head facing E or W. The notch between puff and crown is drawn in outline ink, because it's an overlap edge.
4. **Bag.**
   - It is drawn once per facing and painted onto every frame.
   - Its parts are a `#E67A70` lit lip with one `#F6B18E` glint, a `#71394F` flap line, an ink buckle (`#777A8C`), a `#B65761` body and a dark frame.
   - The body never uses `#E67A70`, which matches the conversation marker, the coral chairs and the counter's strap.
   - Facing S it is on the screen-right hip. Facing N you see its back on the screen-left hip. Facing W it is on the near hip, forward of the body edge. Facing E it is on the far hip, showing behind her back as the same bag at 5×5.
   - On contacts and the idle settle the bag moves down with her body as a whole, so it never changes shape.
   - On passing frames it swings 1 px: inward in S and N, backward in E and W. This implements mira.md's "bag swings 1 px" and keeps the stride rule.
   - Reference 08's courier carries an orange bag on screen-right seen from behind. mira.md's text (left hip, coral) is followed. The reference is a concept, not a frame source.
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
9. **Bob and stride.** Every facing's settle drops the top leg row. The side walk stays inside the approved Gate 1 overhead limit (the feet never touch columns 0 or 15). This overrides mira.md's "longer step", because the approved overhead-camera rule outranks the brief. Her extra energy comes from the trailing heel lifting off the floor on contact frames. `check_gate1.py` now enforces the stride edge and her glint limits (`GLINT_LIMITS`).
10. **Patches.** The base set has none, because the first patch is earned after level 02. The six patch designs stay open. Patches will be 1–2 px clusters on the bag flap and the jacket, added as states.
11. **Room.** The slate planter that crowded her hair puff moved from (278,126) to (238,126).
12. **Scope.** This round is idle ×4 and walk ×4. Interact, reactions, patches and the Night Shift strap exception (mira.md open question 2) come later.

## Acceptance criteria

Automated (`check_gate1.py mira_sprites`):
- [x] 24 frames, each 16×24, with a pixel on row 23 and mass within 20 % across the 7|8 anchor
- [x] No UI marker hex and no violet. Teal-hued steps at or below 60 % saturation.
- [x] Head rows use only hair, skin and outline keys
- [x] The darkest hair step appears only on contour and occlusion edges

Review history: two specialist reviews (character, style), then continuity cycle 1. It failed on five points: the green glint on 2 px, a dark unreadable E bag, a bag deformed by the bob, a stride wider than the Gate 1 limit, and the missing bag swing. Polish items were a flat N hair dome and weak puffs. All were fixed in cycle 2, and the coordinator review passed.

Coordinator review:
- [x] Reads as a different person from the Engineer and Ivo at 1× and at ×4
- [x] Bag on her left hip in every facing, drawn separately for E and W, with a flap line and buckle
- [x] Strap readable as a clean diagonal in S, N, E and W
- [x] The puff reads as hair, not as a helmet or a hat, and the ears and temples show
- [x] Distinct from the mail counter, the planter and the coral chairs in the room

Player:
- [x] Approved 2026-10-02 (self-review under the player's delegation)

## Extra animation sets (approved by the director 2026-10-02)

**Status:** Candidate, pending director review. Tasks 8.1 and 8.2. Idle and walk frames are unchanged (verified by dump and diff). Frames live in `mira_sprites.EXTRA`; format as in `gate1/GATE1_ENGINEER_SPEC.md` "Extra animation sets". Frames are built from the raw bagless grids plus stamps, then `finish()` paints strap shading and the bag, so the bag keeps its shape on lowered frames. `build_cast.py mira` appends the rows to `mira-atlas.png/.json`, adds the frames to `mira-sheet.png` and writes `mira-extra.gif`. Her patches are owned elsewhere and are not touched.

| Set | Facings | Frames | ms per frame | Mode | Pose |
| --- | --- | --- | --- | --- | --- |
| `interact` | S N E W | 2 | 250 | once | Handing over a letter. S: hands meet at the belt, then hold the letter up. E and W: the near arm reaches out, then the letter appears above the hand. N: the elbows flare, then the right hand is out with the letter |
| `react_pleased` | S N E W | 3 | 300 | once | A clean run. S: hands on hips, fist pump, settle. E and W: idle, fist pump, settle. N: hands on hips, breath |
| `react_confiding` | S N E W | 3 (N, E, W: 2) | 300 | once | The erased-routes admission: head bows; S adds a hand gripping the strap, then sags. Others bow only |

**Director decisions**

1. **Reactions chosen from the brief.** Pleased on a clean run and confiding for the route-copies scene, both from the Animation table in `design/characters/mira.md`. Reason: they are the two beats her story names.
2. **Paper keys.** `PAL` gains `r`, `s`, `q` (`#F4F2EC`, `#E2D6C2`, `#C7B7A0`) for the letter. No approved pixel uses them. Reason: the interact pose needs something to hand over, and her ramps have no off-white. The letter has a dark rim because the stone floor is pale.
3. **Coral stays on the bag and strap only.** The letter is cream, not coral or gold. The glint limits (`z`, `H`, `f` at most 1 px) hold on every extra frame.
4. **Check rules.** `interact` and `react_pleased` are in `EXTRA_ASYMMETRIC` (anchor-mass tolerance 30%). Letter and hand pixels sit on rows 10 and below, except dark rim pixels, because head rows may hold only hair, skin and outline.
5. **Lowered frames** use the approved idle-1 recipe (`lower()` on the raw grid, then `finish(..., dy=1)`).
