# Hal — sprite specification (idle ×4, walk ×4)

**Status:** Approved by the director 2026-10-02.

**Sources:** `design/characters/hal.md`, `levels.md` (cast table, Systems row, levels 12–16), `palettes/PALETTES_SPEC.md` (Hal's skin and hair ramps), STYLE_BIBLE §3–7. The shared person rules come from the approved [Gate 1 spec](../gate1/GATE1_ENGINEER_SPEC.md); the cast frame rule comes from [IVO_SPEC.md](IVO_SPEC.md). **Director decision** marks choices made under the delegated art-direction authority.

## Deliverables

| File | What it is |
| --- | --- |
| `hal_sprites.py` | Hand-placed 16×24 key grids, the palette and the roll overlay. Pixel source of truth. Hair and skin are read from `CAST_RAMPS["hal"]`, never retyped. |
| `hal-sheet.png` | All 24 frames at ×8, ×2 and ×1, anchor marked |
| `hal-walks.gif` | The four walk cycles looping at ×6 |
| `hal-atlas.png` / `.json` | Native atlas. Rows S N E W idle, then S N E W walk. |
| `build_hal_room.py` → `hal-in-systems.png` | A Systems-palette room at ×4 (the review room recoloured with `build_palettes.palette_swap`, 0 unmapped pixels, people drawn after the swap), with Hal beside the Engineer for scale |

Rebuild: `cd art-direction/cast && python3 build_cast.py hal && python3 build_hal_room.py`. Check: `cd art-direction/gate1 && python3 check_gate1.py hal_sprites`.

## Silhouette (how Hal differs from the Engineer and Ivo at 1×)

| | Engineer | Ivo | Hal |
| --- | --- | --- | --- |
| Height | rows 0–23 | rows 1–23 | rows 2–23, with tuft tips on row 1: a lower figure |
| Head | brown swept hair | silver cap | sandy-blond dome with two tufts, an uneven fringe over a dark brow, ears and nape showing; 3 hair rows over a 5-row face |
| Torso | teal jacket | broad terracotta cardigan | cobalt utility vest over warm-stone sleeves, 12 px wide, chest seam and pocket |
| Hands | 1 px | 1 px | 3×2 slate gloves with a lit knuckle: the largest hands in the cast |
| Prop | optional badge | 5×4 tablet | safety-orange tool roll with cream cord bands, under his left arm |
| Legs | navy | navy | charcoal trousers, brown boots, the shared leg poses |

## Director decisions

1. **Frame.** Everything stays inside 16×24. The roll is held against the body, not out to the side (cast frame rule).
2. **The tool roll is the carried prop; the stool stays a separate prop** (hal.md assumption 2). The roll is tucked under Hal's left arm and points forward. S and N see it lying along his side (3-wide cylinder, cream cord bands, end cap in S). E and W see its length protruding past the belt, with two ink-grey tool tips at the front end. It is painted by `finish()` after the body, as Mira's bag is, so it keeps its shape on the 1 px settle. This enlarges hal.md's 3×1–2 px cluster, because a cluster that small did not read as a roll.
3. **Orange.** The roll uses the Systems accent ramp (`#7A2F1B #C2521A #F2842B #FFB36B`). Hal's clothes use no orange, so the roll is the only orange on him. `#FFB36B` is limited to 1 px (`GLINT_LIMITS`), so the roll can't read as the gold marker.
4. **Vest colour.** Steel cobalt `#1B2A58 #2D4585 #4767AD #86A4DA`, hue 219–225° (outside the teal band), at most 53% saturation. It is greyer and lighter than the Systems cobalt equipment (`#2347B0 #2F63D9`), so Hal doesn't merge with the machine, and its fill is 7.7:1 against the porcelain floor. It is not Ivo's tablet glass and not the Engineer's teal.
5. **Sleeves.** Warm stone `#8F8372 #C7B7A0 #E6DBC8`, from hal.md's porcelain. The darker steps keep the sleeve from vanishing on the near-white Systems floor.
6. **Gloves.** The ink ramp (`#343650 #535971 #777A8C`): distinct from skin, vest and the orange. 3×2 plus an outline. This replaces hal.md's "one value darker than the vest", which merged with the vest.
7. **Trousers and boots.** Neutral charcoal `#353539 #4F4F55` (not navy, so he differs from the Engineer, Ivo and Mira) and brown leather boots `#3A2A28 #664636 #8E6244`.
8. **Hair and skin (`HAIR_SKIN_SEPARATED = True`).** Sandy hair and golden skin are 13 L* apart, so light hair never touches lit skin. A dark `k` forehead shadow and brow sit under the fringe, the fringe has `A` tips and two light locks that sit only over a brow `k`, and the ears and nape are `k`. There is no flat rim line, so it doesn't read as a helmet.
9. **Tufts.** Two outline-capped tufts rise from a round dome (the crown is 6, 8 then 10 px wide), so the head is not a block.
10. **Director revisions (6.2 review).**
    - Face: each eye sits in a lit-skin socket (`n` on the brow, cheek and side pixels around it, `k` brow line kept under the fringe). In E and W one eye sits beside a lit cheek in front. No new hexes.
    - N hair: two spikes matching S, a notch on each side of the dome, `B` strand clusters running down-right, and a tapered nape (hair 4 px wide on the last row with a dark `A` hairline, `k` ears beside it, neck skin below).
    - E and W gloves: a dark `g` cuff line where the glove meets the sleeve, a lit `j` knuckle on the upper left, a lit `j` thumb that sticks out past the glove with a notch below it, and the glove grips the rear end of the roll. Only ink-ramp hexes.
    - N body rows 12-13 were one pixel too wide and are fixed.
11. **Walk.** The shared timing and legs: 4 × 133 ms, contacts on frames 0 and 2, a 1 px bob that drops the top leg row (`eng.lower`), no arm swing (the arm is under the roll). The stride stays off columns 0 and 15.
12. **Scope.** Idle ×4 and walk ×4 only. Crouched repair, seated, puzzled, the false-panel pull, the stool, the portraits and the EXTRA sets come later.

## Acceptance criteria

Automated (`check_gate1.py hal_sprites`): 24 frames, 0 failures. It covers 16×24, row 23, mass within 20%, no marker hex or violet, head keys, the darkest hair step, light hair against skin, the glint limit and the stride edge.

Coordinator review (to be ticked by the director):
- [x] Reads as a different person from the Engineer, Ivo and Mira at 1×
- [x] The roll reads as a rolled tool bag in all four facings
- [x] Hair is not a helmet: tufts, uneven fringe, ears and nape
- [x] Hal reads on the Systems floor in `hal-in-systems.png`
