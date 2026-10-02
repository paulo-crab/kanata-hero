# Glitches — sprite specification (stapler, chair shadow, folded form)

**Status:** Approved by the director 2026-10-02.

> **Rich finish (2026-10-02):** only the outline colour changes (`#0E1020`); glitch violet is unchanged. Queued under OpenSpec change `adopt-rich-finish`; see `../rich-finish/RICH_FINISH_SPEC.md`.

**Sources:** `design/characters/glitches.md`, `docs/game-design.md` (sprite table, interaction silhouettes), `levels.md` (level 01 paper-fold glitch), STYLE_BIBLE §3, §7 ("Devices / anomalies: solid housing first, then an emissive centre; glow never erases the silhouette"). **Director decision** marks choices made under the art-direction authority the player delegated.

## Deliverables

| File | What it is |
| --- | --- |
| `glitch_sprites.py` | Palette, hand-placed key-grid layers, frame composition, per-archetype metadata (footprint, anchor, shadow, timing, movement, ordinary-prop collision). The pixel source of truth: roam, misregister, repaired (snap) and ordinary frames. |
| `glitch_variants.py` | The variant catalogue and the district contract as data: palette variants, behaviour variants, the five-district table, the chair recolour. |
| `check_glitches.py` | Automated checks (stdlib only), including the repaired frames, the ordinary props, the variants and the spec/atlas agreement |
| `build_glitches.py` | Writes every output below |
| `glitches-sheet.png` | All 24 frames at ×8, ×2 and ×1 with anchors marked (repaired and ordinary side by side), plus a greyscale read test |
| `glitches-before-after.png` | Per archetype: glitch rest, misregister, snap, ordinary prop, at ×8 and ×4 |
| `glitches-variants-sheet.png` | The three palette variants on a light floor and as `dark_steps` on the Night Shift floor |
| `glitches-atlas.png` / `.json` | Native atlas (128×192), one row per animation, with frame size, anchor, footprint, frames, ms, movement; the ordinary props (footprint, collision, anchor); the repair rule; the variant catalogue; the district table |
| `glitches-in-room.png` | The approved review room at ×4 (1366×768) with all three glitches on the floor around the route |
| `glitches-in-room-native.png` | The same 320×180 logical view |
| `glitches-in-room-repaired.png` | The same room after the repairs: the three ordinary props, ×4 |
| `glitches-in-nightshift.png`, `glitches-in-nightshift-repaired.png` | The Night Shift reference room at ×4 (1280×768): glitches in `dark_steps` (standard, plum and dusk) with the district's chair recolour, then the ordinary props |
| `glitches-roam.gif` | The three roaming and flickering in the room, ×6 crop, 4.8 s loop |
| `glitches-repair.gif` | Glitch, snap (160 ms), ordinary prop, per archetype in turn, ×6 crop, 4.8 s loop |

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
- **Repaired** (decision 11, drawn in the second round): play `<archetype>_repaired` once, 1 frame, 160 ms, at the glitch's current anchor, then swap to `<archetype>_ordinary` at the same anchor and stop roaming. See "Repaired frames and ordinary props" below for the cue of each snap and the renderer format.

## Rendering rules and how they are enforced

| Rule | `check_glitches.py` |
| --- | --- |
| 16 px grid, 16–32 px, footprint matches frame, 2–4 roam and 1–2 misregister frames, no duplicate frames | per archetype |
| Only allowed hexes; no UI marker hex (`#9876D5` included); violet is exactly the four-step ramp | palette |
| Solid housing first: every opaque pixel touching transparency is an outline or dark step (`#202337`, `#343650`, `#413755`) | contour. A violet fill pixel may touch transparency only as a 1 px ghost line (never part of a 2×2 violet block). |
| Glow never erases the silhouette: glow pixels (`#9477AF`, `#C3A6D6`) never touch transparency | glow |
| Glow is at most two hard steps, limited per frame | 12 px (16 wide) or 20 px (32 wide); at most 4 px of the hot step |
| Darkest violet is a contour only: a pixel with all eight neighbours violet is rejected | contour |
| Violet in every glitch frame (roam, misregister, repaired); none in an ordinary prop | violet |
| Misregister differs from the roam rest frame | misregister |
| One snap frame per archetype, at least 12 px from the roam rest frame and 6 px from the ordinary prop, at least 8 violet px, housing equal to the ordinary prop's, violet never on the prop's silhouette edge | repaired |
| One static ordinary frame per archetype: no violet, no glow, a blocking collision cell holds pixels | ordinary |
| Anchor `base_bc` (w/2, h) in the sprite table and the atlas JSON; no glitch frame is mirror-symmetric | anchor, mirror |
| Variants and districts, and the spec table and atlas JSON agree with `glitch_variants.py` | variants, districts |
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
11. **Repaired state: one frame snapping into register, then the ordinary prop.** The stapler's outline ghost aligns with its body and the slot glow goes out (one frame, the arm and ghost coincide); the chair's wrong shadow vanishes, leaving only the chair and its normal shadow; the form unfolds flat (the flap lies in the page's plane, no violet). After that frame the glitch becomes the ordinary prop: the stapler, the chair and the paper stay on the floor as plain objects with the renderer's contact shadow, and stop roaming. This closes glitches.md open question 2. The snap frames and the ordinary props are drawn (decisions 12–15).
12. **The snap frame keeps a trace of violet, the ordinary prop none.** A one-frame flash with no violet at all would be invisible between a glitch and a plain prop, so the snap is the ordinary prop plus a thin violet "register" mark that sits inside or outside the silhouette, never on its edge (stapler: a 1 px ring hugging the body and a dim `bbb` slot instead of the glow; chair: the wrong shadow lying flat as a low slab at the chair's foot and a 1 px line under the seat; form: the sheet lies flat with a 2 px violet crease where the fold was and a glowing centre). The glow is partly out, the offsets are gone: that is "in register". The ordinary props have no violet and no glow.
13. **160 ms, play once.** Four 40 ms ticks (the roam and misregister frames are 80–200 ms): long enough to be read at ×4, short enough to be a snap. A single global value, `REPAIRED_MS`.
14. **The ordinary props are district-neutral office objects.** Stapler: the ink ramp. Sheet: the paper ramp, flat, the cut corner restored and five printed lines (the folded form's two lines stay where they were). Chair: the coral task chair with only its single, correct shadow, which the renderer draws. They are never tinted by the floor. The only district change is the chair upholstery: every district kit already recolours the chair by an exact hex swap, so the renderer applies that same swap (`districts.<id>.chair_recolour`, coral steps 1–3 to steps 1–3 of the Records/Systems glass ramp or the Night Shift/Executive wall ramp) to every chair frame, glitch or ordinary. The district light pass (lamp pools, Night Shift lighting masks) applies to them like any prop.
15. **Collision and footprint of the ordinary props.** Stapler (2×1 cells) and sheet (1×1): walkable decor, `["00"]` and `["0"]`; nobody should be blocked by a stapler or a sheet of paper once the glitch is gone. Chair (2×1): `["01"]`, it blocks its own right-hand cell only (the left cell is empty floor, where the wrong shadow used to lie). Layer `actor`, `y_sort` true, anchor `base_bc`, same contact shadow rect as the glitch.
16. **Variants are exact hex swaps and data only** (decision 10). The three palettes map to the three repair-duel kinds in `docs/game-design.md` (fix a token: `standard`; choose a route: `plum`; edit a code fragment: `dusk`), so the colour is a second, redundant cue for what the duel will ask. The behaviours are numbers over the frames that already exist.
17. **A `dark_steps` ramp for the dark floor.** On the Night Shift floor (`#4C5865` fill, `#364049` slab) the standard fill `#67547C` is 1.1:1, which loses the wrong shadow and the ghost lines. Each variant therefore carries a lifted four-step ramp (lightness about 0.46, 0.60, 0.72, 0.86, same hue and saturation as the variant) used in the whole Night Shift district, so the cue shapes read: fill 2.0–2.3:1 on the floor fill and 2.9–3.3:1 on the slab (the Night Shift people-rim standard is 2.4:1). Still a violet in the 225–320 degree band, at least dE 23 from every UI marker, never `#9876D5`.
18. **District assignment is director policy where `levels.md` is silent.** `levels.md` mentions glitches only as the story's "misregistered office objects", the tone arc (curious and welcoming, quietly uncanny, humane relief) and level 01's "harmless paper-fold glitch ... after the tutorial". Everything else (first level per district, archetypes, variants, counts) is a director decision grounded in each level's own story, recorded below.

## Repaired frames and ordinary props

| | Stapler | Chair shadow | Folded form |
| --- | --- | --- | --- |
| Glitch (roam rest) | body with a 1 px violet outline ghost offset (3, 1), glowing slot | chair plus the wrong shadow up-left | page with the top-right corner folded the wrong way, violet flap |
| **Snap** (`<archetype>_repaired`, 1 frame, 160 ms, play once) | arm back on its base, a 1 px violet ring hugging the body (the ghost has collapsed onto it), the slot glow out (a dim violet slot) | the wrong shadow has come to rest: a low flat slab at the chair's left foot and a 1 px line under the seat; nothing violet up and to the left | the sheet lies flat, the cut corner back; a 2 px violet crease along the old fold with a two-pixel glow centre |
| **Ordinary prop** (`<archetype>_ordinary`, static) | the same stapler, the slot a plain dark groove | the task chair alone (renderer shadow only) | a flat sheet with five printed lines |
| Footprint, collision | 2×1, `["00"]` | 2×1, `["01"]` | 1×1, `["0"]` |
| Cue that isn't colour | the ring and the aligned body | the shadow lying under the chair, not away from it | the flat outline: no cut corner |

At ×4 the three snaps are read against the roam frame and the ordinary prop in `glitches-before-after.png` (×8 above, ×4 below) and in `glitches-repair.gif`. The check requires each snap to be at least 12 px different from the roam rest frame and 6 px from the ordinary prop, with at least 8 violet px.

### Renderer playback format (repaired → swap)

1. The repair duel succeeds. Stop the roam (keep the glitch's current anchor `x, y`), remove the violet marker and the interaction outline.
2. Draw `<archetype>_repaired` (atlas row `animations.<archetype>_repaired`, one frame) at that anchor for `ms` (160). Draw the archetype's renderer contact shadow as for the glitch.
3. Then draw `<archetype>_ordinary` (row `animations.<archetype>_ordinary`, `static`) at the same anchor, forever, with the collision from `archetypes.<archetype>.ordinary.collision` (one string per footprint row, one character per cell, `1` blocks). Persist "repaired" per room so the room keeps the ordinary prop on later visits.
4. Both frames use the same frame size and `base_bc` anchor as the glitch, so nothing shifts. Never mirror them.
5. Apply the district chair recolour (chair only) and, for a glitch, the palette variant (below). The ordinary props have no violet to swap.

JSON: `animations.<a>_repaired` has `frames: 1, ms: 160, loop: false, play: "once", then: "<a>_ordinary"`; `archetypes.<a>.ordinary` has `animation`, `row`, `footprint {cells, origin_px}`, `collision`, `layer`, `y_sort`, `anchor`, `contact_shadow`, `flippable: false`. The top-level `repair` object restates the rule.

## Variants and districts

Everything below is data in `glitch_variants.py`, written into `glitches-atlas.json` under `variants` and `districts`; the check keeps this spec, the data and the JSON in agreement.

### Palette variants (alternate violet step sets)

The sprites are drawn in the standard violet. A variant is an exact hex swap of the four steps (`variants.palettes.<id>.swap`, or `swap_dark` in a `dark_floor` district), applied to every frame of the glitch. The three silhouettes never change.

| Variant | Duel it signals | Steps (contour, fill, glow, hot core) | `dark_steps` (Night Shift floor) |
| --- | --- | --- | --- |
| `standard` | fix a token | `#413755` `#67547C` `#9477AF` `#C3A6D6` | `#6D5C8E` `#9885AD` `#B8A5CA` `#DECEE8` |
| `plum` | choose a route | `#553458` `#80507D` `#B373AC` `#D9A3CE` | `#8E5793` `#B181AE` `#CDA2C8` `#EACCE4` |
| `dusk` | edit a code fragment | `#333459` `#534E82` `#7B71B5` `#AFA2DA` | `#555795` `#8480B2` `#A8A1CE` `#D3CCEB` |

`plum` is the standard ramp's hue plus 36 degrees (warmer), `dusk` minus 22 degrees (cooler); lightness is unchanged. Checked: hue 225–320 degrees, step order dark to light, every step at least dE 10 from teal, coral, violet and gold markers (the closest is dE 17), fill and glow at least dE 9 from the standard step, `dark_steps` contrast on the Night Shift floor.

### Behaviour variants

| Behaviour | Tone | `roam_ms` stapler / chair / form | Path | Pause | Misregister (every, amplitude) |
| --- | --- | --- | --- | --- | --- |
| `drift` | calm | 160 / 280 / 160 | `hover`, 24 px | after 2 cycles, hold 1200 ms | every 3.6–6.0 s, `low` (frame 0) |
| `patrol` | uncanny | 120 / 200 / 120 (the approved baseline) | `line`, 64 px | none | every 1.2–2.4 s, `normal` (frames 0, 1) |
| `stutter` | uncanny | 120 / 200 / 120 | `line`, 48 px | after 3 cycles, hold 480 ms, a burst on each pause | every 2.4–3.6 s, `high` (frames 0, 1, 0, 1) |
| `lurk` | quiet | 200 / 280 / 200 | `edge`, 32 px | after 1 cycle, hold 2400 ms | every 4.8–7.2 s, `high` |
| `settle` | relief | 240 / 360 / 240 | `hover`, 16 px | after 1 cycle, hold 3200 ms | never on its own, `low`; on contact only |

- `roam_ms` replaces the roam animation's `ms`; the frames and `move_px_per_frame` are unchanged (every value is a multiple of the 40 ms tick). A cycle is the four roam frames.
- Paths: `hover` patrols out and back within the lane around its home cell, `line` patrols a lane, `edge` is a line hugging a wall or furniture edge (the lamp pool's rim at night). A lane never crosses the main route and never blocks a one-cell passage.
- Misregister `frames` are indices into `<archetype>_misregister`, each shown for 80 ms. On contact, before the duel opens, always play `contact_frames` `[0, 1]` whatever the behaviour.

### District table (data contract, keyed by district id)

Intensity ramp: 1 calm (curious and welcoming), 2 the uncanny begins, 3 the machine's peak, 4 the deepest and quietest (fewer, slower, in the dark), 1 again for relief. Level designers read `districts.<id>` in `glitches-atlas.json` for the same data. A level may use an archetype only from its `from_level`; a palette or behaviour only from its `*_from_level`. The district's first glitch is its first encounter. "Safe" levels hold no glitch. `max_per_room` is the most live glitches in one room.

<!-- districts:start -->
| District id | Levels, tone | Intensity, count | First glitch | Archetypes: from level (palettes; behaviours) | Held back until, and why |
| --- | --- | --- | --- | --- | --- |
| `orientation` | L1-6, calm | intensity 1, max 1 per room | L01 form standard drift | form from L01 (`standard`; `drift`)<br>stapler from L04 (`standard`; `drift`) | `standard` and `drift` from L01. Level 01's harmless paper fold, repaired after the movement tutorial; a stapler at a desk edge from 04 (the desk levels). No chair shadow: the wrong shadow is the uncanny one and waits for Records. |
| `records` | L7-11, uncanny | intensity 2, max 2 per room | L08 form standard drift | form from L08 (`standard`, `plum`; `drift`, `patrol`)<br>chair from L09 (`standard`, `plum`; `drift`, `patrol`)<br>stapler from L10 (`standard`; `patrol`) | `standard` and `drift` from L08, `plum` and `patrol` from L10 (The Long Report's route choice). Level 07 is safe: the door and its panels are the challenge. Level 08 (Filing Drift) is where addresses and folded forms drift; the chair shadow joins in 09 (The Margins). |
| `systems` | L12-16, uncanny | intensity 3, max 3 per room | L12 stapler standard patrol | stapler from L12 (`standard`, `plum`, `dusk`; `patrol`, `stutter`)<br>form from L13 (`standard`, `plum`; `patrol`, `stutter`)<br>chair from L14 (`standard`, `plum`, `dusk`; `patrol`, `stutter`) | `standard` and `patrol` from L12, `plum` from L13, `stutter` from L14 (Alarm Glyphs), `dusk` from L15 (the Formula Room's code fragments). The peak: the routing machine duplicates work, so all three archetypes and the most per room. |
| `nightshift` | L17-19, quiet | intensity 4, max 2 per room | L18 chair standard lurk | chair from L18 (`standard`, `plum`, `dusk`; `lurk`, `stutter`)<br>form from L19 (`standard`, `plum`, `dusk`; `lurk`, `stutter`)<br>stapler from L19 (`standard`, `plum`, `dusk`; `lurk`) | `standard`, `plum`, `lurk` from L18, `dusk` and `stutter` from L19. Level 17 is safe: the break room and the vestibule teach the exit and hold no glitch. Always `dark_steps`. The deepest uncanny at the lowest volume: fewer per room, slow, in the edges of lamp pools. The chair's wrong shadow first, among rows of identical desks. |
| `executive` | L20, relief | intensity 1, max 1 per room | L20 form standard settle | form from L20 (`standard`; `settle`)<br>chair from L20 (`plum`; `settle`)<br>stapler from L20 (`dusk`; `settle`) | One still glitch per incident branch, in the palette of its duel: The Name is the form (token), The Route the chair (route), The Count the stapler (code). Each is repaired in the branch and stays behind as an ordinary prop that the restored atrium keeps. |
<!-- districts:end -->

Notes for the level designers:
- **Orientation:** the paper fold in level 01 is `form` + `standard` + `drift`, one per room, and nothing else in the garden loop. It is harmless: no timer, immediate retry, the tutorial is already over.
- **Quiet levels:** `quiet_levels` in the JSON (Records 07, Night Shift 17) are levels that must not place a glitch.
- **Night Shift:** `palette_steps` is `dark_steps` for the whole district; the chair also takes the district's `chair_recolour` (indigo).
- **Executive:** the three branches are `districts.executive.branches` (`The Name` form, `The Route` chair, `The Count` stapler). The repaired ordinary prop stays in the atrium in the restored state.
- Earlier floors keep their ordinary props after the repair (the game's "earlier floors retain their changed state").

## Acceptance criteria

Automated (`check_glitches.py`):
- [x] 24 frames (roam, misregister, repaired, ordinary), each the archetype's 16×16 or 32×16 size, none touching the left, right or top border
- [x] Only allowed hexes, no UI marker hex, violet is the four-step ramp
- [x] Every silhouette pixel is an outline or dark step (a ghost line excepted)
- [x] Glow pixels never touch transparency, at most two glow steps, within the per-frame limit
- [x] Violet in every glitch frame (snap included); none in an ordinary prop; misregister frames differ from the roam rest frame
- [x] Each snap differs from the roam rest, the misregister frames and the ordinary prop; its housing is the prop's; violet never on the silhouette edge
- [x] Anchor `base_bc` and `flippable: false` in the sprite table and the atlas JSON; no glitch frame is mirror-symmetric
- [x] Rest silhouettes differ in greyscale
- [x] Palette variants (hue band, markers, order, dark-floor contrast), behaviours (ticks, frames), district table (ids, ramp, first glitch, chair recolour), and the spec table and atlas JSON agree with `glitch_variants.py`

Coordinator review:
- [x] Each reads as the mundane object first and "wrong" second, in the room at ×4
- [x] The three are distinguishable in greyscale at 1×
- [x] Glow never erases a silhouette
- [x] No faces, teeth, claws or hostile creature read
- [x] Violet appears nowhere else in the room (and nowhere on an ordinary prop)
- [x] Each archetype has a visible before and after at ×4 (`glitches-before-after.png`); the snap is distinguishable from the roam and ordinary frames
- [x] Two districts rendered in room: Orientation (`glitches-in-room*.png`) and Night Shift (`glitches-in-nightshift*.png`, dark_steps and recoloured chair)

## Open points for the director

- Closed in the second round (2026-10-02): the repaired frames and ordinary props are drawn; the palette and behaviour variants are catalogued; the district assignment is decided (glitches.md open question 1 closed).
- Still open for implementation, not art: the chair's `chair_recolour` is an upholstery swap the renderer must apply to chair frames; Night Shift lighting masks over the ordinary props are the renderer's; level designers choose, per room, which allowed palette and behaviour to place, within `districts.<id>`.
- The snap frame's cue is deliberately small (decision 12): if it reads too quiet in the real engine at 160 ms, lengthen `REPAIRED_MS` to 240 (still a multiple of 40) rather than redrawing.
- Review history: the folded form was approved unchanged. The stapler and the chair shadow were revised after the director's review of the first candidate (reasons in decisions 2 and 4).
- The chair shadow's read in the room at ×4 is the item to look at: the shadow must read as a flat shadow lying toward the light, not as an object.
- `build_gate1.frame_rgba` is fixed at 16×24, so `build_glitches.py` has a small general `rgba()` helper. A proposed generalisation for `build_gate1.py` is `h, w = len(frame), len(frame[0])` in place of the fixed `(24, 16, 4)`; that edit was not made here.
