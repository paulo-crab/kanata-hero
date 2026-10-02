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
12. **Scope.** The first round was idle ×4 and walk ×4. The EXTRA sets followed (interact, puzzled, anxious), then the working poses and the stool prop (see "Working poses and the stool" at the end).

## Acceptance criteria

Automated (`check_gate1.py hal_sprites`): 24 frames, 0 failures. It covers 16×24, row 23, mass within 20%, no marker hex or violet, head keys, the darkest hair step, light hair against skin, the glint limit and the stride edge.

Coordinator review (to be ticked by the director):
- [x] Reads as a different person from the Engineer, Ivo and Mira at 1×
- [x] The roll reads as a rolled tool bag in all four facings
- [x] Hair is not a helmet: tufts, uneven fringe, ears and nape
- [x] Hal reads on the Systems floor in `hal-in-systems.png`

## Extra animation sets (approved by the director 2026-10-02)

`EXTRA`, `EXTRA_MS`, `EXTRA_ASYMMETRIC` in `hal_sprites.py`, in the format of the Engineer's, Ivo's and Mira's. Every frame is a raw base grid plus hand-placed stamps, with `finish()` painting the roll afterwards (so the roll keeps its shape). `IDLE` and `WALK` are byte-identical to the approved set (dumped and diffed). `build_cast.py hal` writes the extra rows to `hal-atlas.png/json`, the frames to `hal-sheet.png`, and `hal-extra.gif`. `check_gate1.py hal_sprites`: 56 frames (24 base + 32 extra), 0 failures.

| Set | Facings | Frames | Timing | Mode |
| --- | --- | --- | --- | --- |
| `interact` | S N E W | 2 | 250 ms | once, holds the last frame |
| `react_puzzled` | S N E W | 3 | 300 ms | once, holds the last frame |
| `react_anxious` | S N E W | 3 | 300 ms | once, holds the last frame |

Decisions:

1. **Interact is "using a tool at a panel".** In S and N the free glove lifts a steel tool (an ink-ramp shaft and tip, 2–3 px, with an outline) toward the panel, one row higher on the second frame. In E and W the forearm (stone sleeve) comes forward past the belt, the glove passes the front edge and the tool points ahead. The roll stays under the other arm.
2. **Reactions from hal.md.** Puzzled is hal.md's "head tilt / scratch": the head tilts 1 px, then the free glove comes up open, then the body settles 1 px. The scratch itself is dropped, because a glove beside the head would break the rule that rows 0–9 hold only hair, skin and outline keys. Anxious is the "Anxious" portrait state: the head sinks onto the shoulders (1 px, then 2 px) and the body settles. The second reaction is anxious, because relief and focus have no pose in hal.md.
3. **No head-row exceptions and no new hexes.** Gloves and tools stay on row 10 or below, and every key is already in `PAL`. `H` is never used in an extra frame.
4. **Asymmetric sets.** `interact` and `react_puzzled` move an arm off the anchor, so they use the checker's relaxed mass tolerance (`EXTRA_ASYMMETRIC`).
5. **Crouched repair and seated-on-stool** (the other hal.md poses) came with the stool prop, which is a separate sprite: see "Working poses and the stool".

## Working poses and the stool (poses branch)

`hal_sprites.py` adds three EXTRA sets and the stool prop. Each pose is the base head moved down (head rows stay hair, skin and outline only, rows 0-9) over hand-placed rows; `check_gate1.py hal_sprites`: 94 frames (24 base + 70 extra), 0 failures, no new `EXTRA_ASYMMETRIC` entry (all inside the strict 20 % tolerance). The tool roll is painted by hand for these poses (it lies on the near thigh when Hal is low) and stays orange-only, `H` 1 px.

| Set | Facings | Frames | Timing | Mode | Atlas rows |
| --- | --- | --- | --- | --- | --- |
| `crouch_repair` | S N E W | 4 | 220 ms | loop | 20-23 |
| `seated_stool` | S E W | 2 | 600 ms | loop | 24-26 |
| `false_panel_pull` | S N E W | 4 | 260 ms | once, hold last | 27-30 |

Atlas names: `hal_crouch_repair_<f>`, `hal_seated_stool_<f>`, `hal_false_panel_pull_<f>`. The stool prop is in `hal-props-atlas.png/.json` (kit atlas format, validated by `kit/check_atlas.py` from `build_hal_room.py`).

### Decisions

6. **Crouched repair (default working pose at machines, levels 12-14).** A squat: the head sits at rows 8-16 (7-15 on E and W), two to three torso rows, short wide legs, boots on rows 22-23, roughly three quarters of the standing height. S: both gloves meet at the centre holding a steel tool (ink ramp) whose tip pokes down toward the panel; the roll lies on his right thigh (screen-right). E and W: the arm reaches forward at belt height with the tool (the interact arm), the roll lies across the near thigh. N: the back, with both gloves forward at shoulder height beside the body and the roll on the left. Loop of 4 × 220 ms: the tool extends and retracts (S, N: gloves up and down 1 px; E, W: the arm reaches 2 px further and back); S also leans the head 1 px on the third frame. N reads (the back view, tool hand pair, roll), so it is included.
7. **Seated on a stool (replaces crouching after the refund sign is fixed, end of level 13).** Facings S, E and W (S is the minimum; E and W show the stool best). Head rows 3-11 (a 2 px lower head than standing, with a short stool), torso rows 12-15, hips on row 17, thighs forward, boots on rows 21-23, feet on row 23. **Feet-on-row-23 rule for seated:** the planted foot is on row 23, exactly as standing, so the same anchor (8, 24) and shadow work. The two idle frames are a 600 ms breath: head and shoulders (rows 3-13) settle 1 px, hips and legs stay. The pose is the relaxed counterpart of the crouch: upright, hands at rest, roll on the thigh.
8. **The stool is a prop, not baked into Hal.** `stool_folding`: a folding stool, steel frame and dark canvas seat from the ink ramp (`o g h j`, so no new hex and no orange), 16 px wide (wider than Hal's hips, so the seat shows at his sides and the splayed legs show beside his boots). Sprite 16×10 px (the cell's rows 6-15), footprint 1×1 cell, `collision: ["1"]`, `layer: rear_prop`, `y_sort: true`, contact shadow baked on the last row (`[1, 9, 14, 1]`), kit convention for placement (`origin_px [0, -6]`, anchor `[8, 10]`: the footprint's bottom centre). The stool's own light edge is the ink ramp's lit step; it reads against the porcelain floor because its fabric is dark (a stone fabric vanished against the floor in the first pass).
9. **Seat offset and y-sort anchor.** Place the stool cell and Hal so the stool's footprint anchor and Hal's anchor coincide: Hal's anchor (8, 24) = the stool cell's bottom centre (8, 16). In Hal's frame the stool cell's top-left is at (0, 8) (`stool_cell_in_frame_px`), so its 16×10 sprite starts at (0, 14) (`stool_sprite_in_frame_px`); the seat is under frame rows 14-17 and the hips rest on row 17. Draw order: the stool in `rear_prop`, then Hal in `actor`, so Hal always draws over it (layer order wins over y-sort); both entries carry the same y-sort anchor y, so nothing else sorts between them. The seated set's atlas entries carry `prop`, `prop_atlas`, `stool_cell_in_frame_px` and `stool_sprite_in_frame_px`. The renderer swaps `hal_crouch_repair_*` for `hal_seated_stool_*` when the refund sign is fixed and spawns the stool at Hal's cell.
10. **False panel pull (one-shot, level 16).** 4 × 260 ms: reach (both gloves at shoulder height beside the head, an outline cap above them; E and W: the arm reaches forward at shoulder height), grip (gloves at chest height, the body settles 1 px), pull (gloves back at the belt, the head dips and the body settles) and rest (the standing idle frame, so the held last frame is a valid pose). N is the facing that matters: the routing machine's false panel is on its south face, so Hal stands south of it with his back to the camera. Swap the machine's panel part from `routing_panel_closed` to `routing_panel_open` (Systems kit) on frame 2, the pull. Gloves stay on row 10 or below, so the head-row rule holds without an exception.
11. **Tool roll.** Stays tucked under his left arm in every pose (screen-right on S, screen-left on N; across the near thigh on E and W when he is low). Orange appears only on the roll.
12. **Proof.** `hal-sheet.png` and `hal-extra.gif` include every new frame. `build_hal_room.py` adds `hal-poses-in-systems.png` (the real Systems reference room drawn from `kit/systems-atlas`, at ×4 on 1366×768: Hal crouching at the machine's west port and in the open floor facing S, E and W, seated on the stool S and E, and the four pull frames along the machine's face) and `hal-poses-x8.png` (every pose at ×8 for the silhouette read, the seated frames with the stool composed), and writes `hal-props-atlas.png/.json`.
13. **Atlas contract.** `build_cast.py` reads the opt-in `EXTRA_META` (merged into a set's atlas entries) and `EXTRA_WALK`; other characters do not define them, so their outputs are unchanged.

### Acceptance criteria (poses)

Automated: `check_gate1.py hal_sprites` 94 frames, 0 failures; `kit/check_atlas.py hal-props-atlas.json` passes (run from `build_hal_room.py`); `build_all.py` passes with a clean second run.

Coordinator review (checked by the poses team against `hal-poses-in-systems.png` and `hal-poses-x8.png`):
- [x] The seated pose visibly sits on the stool (seat beside the hips, legs of the stool beside the boots) and the stool is a separate prop
- [x] The crouch reads as repair at a panel (low squat, gloves and tool forward)
- [x] The pull reads as pulling something down (hands from shoulder height to belt, body settling)
- [x] Roll tucked under the left arm in every pose; no orange elsewhere
- [ ] The S crouch is the least clear of the set at 1× (gloves and tool are a few pixels); E, W and N read better. Director to confirm or ask for a redraw
