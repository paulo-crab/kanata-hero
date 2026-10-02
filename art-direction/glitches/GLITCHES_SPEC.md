# Glitches — sprite specification (stapler, chair shadow, folded form)

**Status:** Approved by the director 2026-10-02.

> **Rich finish (2026-10-02):** only the outline colour changes (`#0E1020`); glitch violet is unchanged. Queued under OpenSpec change `adopt-rich-finish`; see `../rich-finish/RICH_FINISH_SPEC.md`.

**Sources:** `design/characters/glitches.md`, `docs/game-design.md` (sprite table, interaction silhouettes), `levels.md` (level 01 paper-fold glitch), STYLE_BIBLE §3, §7 ("Devices / anomalies: solid housing first, then an emissive centre; glow never erases the silhouette"). **Director decision** marks choices made under the art-direction authority the player delegated.

## Deliverables

| File | What it is |
| --- | --- |
| `glitch_sprites.py` | Palette, hand-placed key-grid layers, frame composition, per-archetype metadata (footprint, anchor, shadow, timing, movement). The pixel source of truth. |
| `check_glitches.py` | Automated checks (stdlib only) |
| `build_glitches.py` | Writes every output below |
| `glitches-sheet.png` | All 18 frames at ×8, ×2 and ×1 with anchors marked, plus a greyscale read test |
| `glitches-atlas.png` / `.json` | Native atlas (128×96), one row per animation, with frame size, anchor, footprint, frames, ms, movement |
| `glitches-in-room.png` | The approved review room at ×4 (1366×768) with all three glitches on the floor around the route |
| `glitches-in-room-native.png` | The same 320×180 logical view |
| `glitches-roam.gif` | The three roaming and flickering in the room, ×6 crop, 4.8 s loop |

Check: `python3 check_glitches.py`. Build: `python3 build_glitches.py` (Pillow and numpy). Both run from this folder.

## The three archetypes

| | Stapler | Chair shadow | Folded form |
| --- | --- | --- | --- |
| Frame / footprint | 32×16, 2×1 cells | 32×16, 2×1 cells | 16×16, 1×1 cell |
| Mundane object | a desk stapler, about 24×9 px: raised hinge block at the rear, a metal/ink-grey top arm with a lit top plane (`#777A8C`) and a darker front face, a rounded nose, a dark base plate | the room's coral task chair at the right of the frame (12×11, the same chair as the desks) with its normal ink contact shadow drawn by the renderer | a sheet of paper with two ink lines of print |
| The anomaly (violet) | a 1 px violet outline ghost of the whole body, offset (3, 1), and a glowing staple slot (3 px) at the nose | a second, wrong shadow cast toward the upper left, the direction of the light: flat, low, no top plane. A skewed seat parallelogram 5 px tall, a backrest strip, short leg strokes. Contour `#413755`, fill `#67547C`, one-step `#9477AF` core on the seat. | the top-right corner folded the wrong way: the flap shows a violet back with a glowing core |
| Roam (4 frames) | hop: rest, rise 2 px, apex 3 px, land 1 px. The ghost stays on the floor. 120 ms per frame. Travels 4 px per 480 ms cycle (frames 1 and 2 carry 2 px each). | the chair drifts 1 px per frame; the wrong shadow drifts 1–2 px away up-left, stretches one row taller (frames 1 and 2), then settles back. 200 ms per frame, 4 px per 800 ms. | flutter: flap closed, half, edge-on, half while the page lifts 0, 1, 2, 0 px. 120 ms per frame. Travels 4 px per 480 ms cycle. |
| Misregister (2 frames, 80 ms each) | the arm slips off its base by (2, −1) then (−1, −2); its home outline stays behind in violet | the wrong shadow jumps away from the chair base by (−2, 0) then (−1, −2) | the print slips +2 / −1 px with a violet duplicate line; the flap slips (1, −1) |
| Cue that isn't colour | the offset outline | a second shadow lying the wrong way (toward the light) | the folded corner's diagonal |

Greyscale read at 1×: the stapler is a long, low dark bar with a taller hinge block (24×9, housing luma 0.24), the chair is a compact mid-tone block (12×11, 0.38) with a flat dark shadow beside it, and the form is a tall bright page (11×13, 0.56). The shadow has no top plane and is darker than the floor. The check compares housing silhouettes and luma, and the sheet shows the three in greyscale.

## Frame, anchor and playback rules (for the renderer)

- **Anchor:** the pixel edge at the bottom centre of the frame (form x = 8; stapler and chair x = 16; y = 16). Objects rest on rows 14–15, ghosts included (the stapler and chair rest on row 14). Nothing touches the left, right or top border, so the offsets never clip.
- **Contact shadow:** drawn by the renderer under the real object, not baked in. The atlas JSON gives `x0`, `x1` and `row` per archetype. Shrink it by 2 px while the frame is lifted by 2 px or more (`lift_px` per frame). The chair's wrong shadow is part of the sprite; the chair's normal shadow is the renderer's (`x0` 20, `x1` 30).
- **Not flippable.** Light comes from the upper left, so the frames are never mirrored. Glitches move sideways and the same frames play in both directions.
- **Roam** loops forever while the glitch moves along its lane. `move_px_per_frame` is the horizontal travel applied when each frame starts.
- **Misregister** is a flicker: show each of its 1–2 frames once for its ms, then return to the roam frame. Trigger it every 1.2–2.4 s while roaming, and on contact before the duel opens. It is a local reaction, never a full-screen effect.
- **Repaired** (Director decision 11): one frame snapping into register, then the ordinary prop. The frame is not drawn in this round; it is a later task (decision 11).

## Rendering rules and how they are enforced

| Rule | `check_glitches.py` |
| --- | --- |
| 16 px grid, 16–32 px, footprint matches frame, 2–4 roam and 1–2 misregister frames, no duplicate frames | per archetype |
| Only allowed hexes; no UI marker hex (`#9876D5` included); violet is exactly the four-step ramp | palette |
| Solid housing first: every opaque pixel touching transparency is an outline or dark step (`#202337`, `#343650`, `#413755`) | contour. A violet fill pixel may touch transparency only as a 1 px ghost line (never part of a 2×2 violet block). |
| Glow never erases the silhouette: glow pixels (`#9477AF`, `#C3A6D6`) never touch transparency | glow |
| Glow is at most two hard steps, limited per frame | 12 px (16 wide) or 20 px (32 wide); at most 4 px of the hot step |
| Darkest violet is a contour only: a pixel with all eight neighbours violet is rejected | contour |
| Violet in every frame | violet |
| Misregister differs from the roam rest frame | misregister |
| Different housing silhouettes (overlap ≤ 0.45 aligned at the base) or a housing luma gap of 0.15 at 1× | read |

Current glow use: stapler 3 px, folded form 6 px, chair 5 px (the shadow's core) at the most.

## Palette

- Violet, for the anomaly only: `#413755` contour, `#67547C` fill, `#9477AF` glow, `#C3A6D6` hot core.
- Ink outline ramp: `#202337`, `#343650`, `#535971`, `#777A8C`.
- Stapler: the ink ramp only (`#777A8C` lit arm top, `#535971` arm and hinge, `#343650` front face and base, `#202337` contour).
- Chair: the coral upholstery ramp already on the room's chairs, `#B65761` `#E67A70` `#F6B18E`.
- Paper: `#C7B7A0` `#E2D6C2` `#F4F2EC`, the paper ramp the approved printer already uses.

## Director decisions

1. **The offset cue is a drawn shape, not a recolour.** The stapler has a 1 px violet outline ghost, the chair a wrong shadow lying the wrong way, the form a folded corner. Colour never carries the meaning alone.
2. **Chair uses the room's own coral chair kit,** with the wrong shadow as a separate flat shape. It is not a second object: it has no top plane, is 3–5 px tall at the seat, and lies toward the light. The first version (a violet duplicate chair) read as an ottoman next to the chair, and was replaced. The coral steps match the approved desk chairs and avoid `#EC776D`.
3. **The chair frame is 32×16 (2×1 cells)** so the shadow has room to lean and stretch up-left. The roam is the shadow drifting and stretching; the misregister is the shadow jumping 1–2 px away from the chair base.
4. **The stapler is 32×16 (2×1 cells), about 24×9 px, in the ink ramp.** The first 16×16 versions (terracotta wedge, then loaf) read as a sandwich at ×4. The dark base plate, the raised hinge block, the lit grey arm top, the rounded nose and the glowing slot give the stapler silhouette at ×4 and in greyscale.
5. **Violet housing before glow.** The slot, the shadow's core and the flap core sit inside a contour and violet fill; glow is at most two steps (the shadow uses one), and a check rejects any glow pixel on the silhouette.
6. **Misregister offsets are 1–2 px of one part:** the stapler's arm, the chair's wrong shadow, the form's print and flap. Stapler and form leave a violet outline or duplicate line behind; hard pixels only.
7. **Not flippable.** The upper-left light makes mirroring wrong, so roaming is sideways with the same frames.
8. **The scene's placeholder glitch marker is moved.** The room render hides the approved scene's glitch marker (drawn at a placeholder spot) and draws the same marker over the folded form. The marker module and the approved room are unchanged.
9. **Timing.** Roam frames are 120 ms (stapler, form) and 200 ms (chair); misregister frames are 80 ms. All are multiples of the GIF's 40 ms tick.
10. **Variants stay palette- and behaviour-only,** per glitches.md: the three silhouettes are reused, and a variant swaps the violet steps or the roam speed, never the art.
11. **Repaired state: one frame snapping into register, then the ordinary prop.** The stapler's outline ghost aligns with its body and the slot glow goes out (one frame, the arm and ghost coincide); the chair's wrong shadow vanishes, leaving only the chair and its normal shadow; the form unfolds flat (the flap lies in the page's plane, no violet). After that frame the glitch becomes the ordinary prop: the stapler, the chair and the paper stay on the floor as plain objects with the renderer's contact shadow, and stop roaming. This closes glitches.md open question 2. The hand-placed repaired frame (one per archetype) is not drawn in this round.

## Acceptance criteria

Automated (`check_glitches.py`):
- [x] 18 frames, each the archetype's 16×16 or 32×16 size, none touching the left, right or top border
- [x] Only allowed hexes, no UI marker hex, violet is the four-step ramp
- [x] Every silhouette pixel is an outline or dark step (a ghost line excepted)
- [x] Glow pixels never touch transparency, at most two glow steps, within the per-frame limit
- [x] Violet in every frame; misregister frames differ from the roam rest frame
- [x] Rest silhouettes differ in greyscale

Coordinator review (pending):
- [x] Each reads as the mundane object first and "wrong" second, in the room at ×4
- [x] The three are distinguishable in greyscale at 1×
- [x] Glow never erases a silhouette
- [x] No faces, teeth, claws or hostile creature read
- [x] Violet appears nowhere else in the room

## Open points for the director

- Review history: the folded form was approved unchanged. The stapler and the chair shadow were revised after the director's review of the first candidate (reasons in decisions 2 and 4).
- The chair shadow's read in the room at ×4 is the item to look at: the shadow must read as a flat shadow lying toward the light, not as an object.
- `build_gate1.frame_rgba` is fixed at 16×24, so `build_glitches.py` has a small general `rgba()` helper. A proposed generalisation for `build_gate1.py` is `h, w = len(frame), len(frame[0])` in place of the fixed `(24, 16, 4)`; that edit was not made here.
