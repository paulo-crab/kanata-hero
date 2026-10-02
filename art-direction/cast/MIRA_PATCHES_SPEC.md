# Mira's six delivery patches: world sprite and portrait

**Status:** World sprite patches approved by the director 2026-10-02. Portrait icons re-placed for the chibi portraits 2026-10-02 (Candidate, pending director review).

> **Rich finish (2026-10-02):** the outline colour is now `#0E1020` and the ink shoe ramp and renderer shadow move to the deeper ink ramp (`#1C2038` `#3A4160` `#6A7392`). Clothing, skin and hair ramps in this spec stay as approved. The sprites are queued for that recolour (OpenSpec change `adopt-rich-finish`); see `../rich-finish/RICH_FINISH_SPEC.md`.

**Sources:** `design/characters/mira.md` ("Patch states"), `levels.md` ("Mira's repeatable speed routes"), the approved [MIRA_SPEC.md](MIRA_SPEC.md) and `mira_sprites.py`, and the portrait rules in [../portraits/PORTRAIT_RULES.md](../portraits/PORTRAIT_RULES.md). **Director decision** marks choices made for the director to record.

## Deliverables

| File | What it is |
| --- | --- |
| `mira_patches.py` | Overlay data and helpers. It paints patches onto the approved frames; `mira_sprites.py` is not edited. It holds `PATCHES` (world), `PORTRAIT_PATCHES` (icons), `state_frames(k)`, `patch_frame`, `portrait_patches` and `module_for_state(k)`. |
| `check_mira_patches.py` | Runs `check_gate1.py` unmodified on each of the seven states, then the patch placement and distinctness rules |
| `build_mira_patches.py` | Writes the two outputs below |
| `mira-patches-sheet.png` | ×4 strips of states 0–6 for S, E, W and N, the portrait strip at ×4, an ×8 jacket close-up for S and E, and the patch table |
| `mira-patches-atlas.png` / `.json` | Native atlas: seven blocks (state 0..6) of 64×192 px, each laid out like `mira-atlas.png` (rows S N E W idle, then S N E W walk) |
| `../portraits/portrait_mira.py` | `with_patches(grid, k)` paints the portrait icons; `mira-patch1`..`6` rows are in `../portraits/portraits-atlas.png` |

Rebuild with `cd art-direction/cast && python3 build_mira_patches.py`. Check with `python3 check_mira_patches.py`.

## How it works

- State *k* (0 to 6) wears patches 1 to *k*, added in route order. State 0 is exactly the approved sprite (the checker asserts it).
- A patch is 2 px on the world sprite, listed per facing as `(x, y, key)` for a frame at rest. The 1 px settle (idle frame 1, walk contact frames 0 and 2) paints the same pixels one row lower, which is how `mira_sprites.lower()` moves her torso. A patch therefore never changes shape and the bag swing never touches it.
- Patches sit on jacket pixels only: never the head rows, the strap, the bag or the outline. The checker reads the approved frame under every patch pixel.
- Colours come from Mira's ramps or the brass ramp. Five patch-only keys (`i`, `j`, `g`, `a`, `b`) carry hexes that already exist, so the base frames' glint limits (`z`, `H`, `f`: 1 px each) are not spent by patches.

## The six patches

| # | Patch | Earned on | District | World (2 px) | Portrait icon |
| --- | --- | --- | --- | --- | --- |
| 1 | First Delivery | Morning Mail (after level 02) | Orientation | peach `#F6B18E` bar | envelope: peach body, coral flap, 6×4 |
| 2 | Clear Address | Courier Loop (after level 07) | Records | lime `#B2CE78` bar | map pin: lime ring, green hole, 5×4 |
| 3 | Archive Loop | Lost Folios (after level 11) | Records | brass `#E1AC62` bar | loop: brass ring with a `#F5D580` glint, 5×4 |
| 4 | Signed and Sent | Payroll Run (after level 13) | Systems | navy `#2C3352` bar | check mark in navy ink, 6×4 |
| 5 | Signal Keeper | Glyph Dispatch (after level 16) | Systems | pale gold `#EDCB7A` bar | three rising pale-gold bars, 5×4 |
| 6 | Night Courier | Lights-Out Delivery (after level 18) | Night Shift | brass `#F5D580` glint beside a navy pixel | navy crescent with a brass star, 5×4 |

World sites at rest (idle frame 0 coordinates):

| Patch | S | N | E | W |
| --- | --- | --- | --- | --- |
| 1 First Delivery | (3,11) i, (4,11) i | (11,11) i, (12,11) i | (3,11) i, (4,11) i | (4,11) i, (5,11) i |
| 2 Clear Address | (3,13) j, (4,13) j | (10,13) j, (11,13) j | (3,13) j, (4,13) j | (4,13) j, (5,13) j |
| 3 Archive Loop | (4,15) a, (5,15) a | (9,15) a, (10,15) a | (6,15) a, (7,15) a | (10,11) a, (11,11) a |
| 4 Signed and Sent | (11,11) O, (12,11) O | (3,11) O, (4,11) O | (10,11) O, (11,11) O | (10,13) O, (11,13) O |
| 5 Signal Keeper | (11,13) g, (12,13) g | (3,13) g, (4,13) g | (10,13) g, (11,13) g | (8,14) g, (9,14) g |
| 6 Night Courier | (9,12) b, (10,12) O | (5,12) b, (6,12) O | (8,12) b, (9,12) O | (9,16) b, (10,16) O |

Portrait icon positions on the chibi shoulders (top row, left column): 1 at (44,9), 2 at (40,18), 3 at (40,25), 4 at (40,31), 5 at (44,26), 6 at (44,32). Patches 1 and 2 sit on the green panel either side of the strap; patches 3 to 6 sit in two rows on the ochre panel, clear of the zip (column 24) and of the dark right edge (column 39).

## Director decisions

1. **Cumulative states.** State *k* shows patches 1..*k*, because mira.md says the outfit gains a patch after each clean baseline and keeps them. The patch order is the route order.
2. **Two tidy stacks, not scatter.** Patches 1 to 3 form a stack of 2 px bars on the green panel (light colours that pop on green), patches 4 to 6 a second stack on the ochre panel. The first version scattered single pixels and read as confetti at ×4. W shows only ochre near the camera, so both stacks sit on ochre there. Coordinates differ per facing because the panels, strap and bag move, but each patch keeps one colour identity in every facing.
3. **Overlay, not a fork.** The patches are data over `mira_sprites` frames, so a change to the approved sprite flows through. State 0 equals the approved frames.
4. **Colour identity carries the design.** At 16×24 each patch is 2 px, so the six designs differ by colour and by the portrait icon, not by shape. Coral stays Mira's strap and bag colour (the approved decision 5 allows patch colours outside it), and the peach patch is the only coral-family patch.
5. **Marker discipline.** No patch uses a UI marker hex or violet. Brass appears on patches 3 and 6 only (at most 4 brass px per frame), and light patch colours stay at or below 9 px per frame.
6. **New keys carry existing hexes.** `i`, `j`, `g`, `a` and `b` map to hexes already in Mira's palette or the brass ramp, so the sprite's glint limits stay meaningful and each patch is counted separately. `module_for_state(k)` sets their limits (`i`, `j`, `g`, `a` at 2 px, `b` at 1 px).
7. **Portrait icons.** Each patch is a 4–6 px icon with a frame or outline, a lit face and a detail where it fits (envelope flap, pin hole, loop glint, check, bars, star), in the world patch's colours. The portrait shows them clearly, as mira.md asks.
8. **No change to bag, strap or head.** Patches never touch rows 0–9, the strap, the bag or the outline.
9. **Scope.** Patches on the bag flap are not drawn: the flap swings and a patch there would change shape on the passing frames. The Night Shift strap exception (mira.md open question 2) stays open.
10. **Portrait icons re-placed (chibi).** The chibi portrait has tiny shoulders (rows 38-47, cols 8-39), so the six icons were re-placed there. Only the portrait positions changed: the colours, the icon shapes and the world-sprite patches (`PATCHES`) are untouched. The ochre panel's dark right edge is one column wide and its light zip one column, so icons stay on mid ochre. The checker confirms each icon pixel lies on a jacket key, no icons touch, and each adds at least 5 px.

## Acceptance criteria

Automated (`check_mira_patches.py`):
- [x] `check_gate1.py` passes on all seven states (24 frames each): frame size, row 23, anchor mass within 20%, markers and violet, teal saturation, head keys, contour-only darkest step, glint limits, stride edge
- [x] Every patch is 1–2 px and sits on a jacket pixel of the approved frame; no patch touches another
- [x] Each state differs from the previous by 1–2 px in every one of the 24 frames
- [x] Brass at most 4 px and light patch colours at most 9 px in any frame; state 0 equals the approved frames
- [x] `check_portraits.py`: each portrait state is a valid portrait, each icon sits on the jacket and each adds at least 5 px

Coordinator review (to be completed by the director):
- [x] Each state is visibly distinct from the previous at ×4 in S and E (`mira-patches-sheet.png`)
- [x] Patches read as sewn-on patches, not noise, and Mira stays recognisable at 1×
- [x] The portrait strip shows six distinct icons

Review history: cycle 1 scattered single pixels across both panels and failed the readability review (confetti, invisible navy). It was redrawn as two stacks of 2 px bars (decision 2). Cycle 2 failed on glint keys limited to 0 and touching patches in W, and cycle 3 passed the checks.
