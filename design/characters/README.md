# Kanata Hero — character design sheets

**Status:** draft art direction, 2026-10-01. One file per character, compiled from the project documents. These sheets add no new lore. Anything a source document does not state is marked **Assumption** or **Open**, and must be approved before it becomes canon.

## Source order

When sources disagree, this order wins (the order the art-director brief sets, matched to the [document map](../../README.md)):

1. **Art direction:** [`art-direction/STYLE_BIBLE.md`](../../art-direction/STYLE_BIBLE.md), then [`ART_BRIEF.md`](../../art-direction/ART_BRIEF.md), with [`references/08-approved-overhead-direction.png`](../../art-direction/references/08-approved-overhead-direction.png) as the primary visual authority.
2. **Character brief:** the recurring-cast table and per-level briefs in [`levels.md`](../../levels.md), plus "Characters and UI" in [`docs/game-design.md`](../../docs/game-design.md).
3. **Gameplay and animation:** "Camera, scale, and sprite rules" in `docs/game-design.md`.
4. **Level and world:** district tables in `levels.md` and `docs/game-design.md`.
5. **General notes:** [`REFERENCE_NOTES.md`](../../art-direction/REFERENCE_NOTES.md). Its 48×64 sprite size and review gate are **superseded** by the style bible.

The placeholder skin and hair ramps in [`scale-test/build_scale_test.py`](../../art-direction/scale-test/build_scale_test.py) are the only per-character colors on record. They are cited as **provisional**, not approved.

**Never use as reference:** `art-direction/character-current/`, `characters/`, `environment/`, `ui/`, `director-sketches/` (all rejected or discarded by the player).

## Index

| File | Character | Role | Production order |
| --- | --- | --- | --- |
| [engineer.md](engineer.md) | Engineer (player avatar) | Protagonist | **Gate 1:** produced first |
| [mira.md](mira.md) | Mira | Courier, optional speed routes | After gate |
| [ivo.md](ivo.md) | Ivo | Orientation reception lead | After gate |
| [noor.md](noor.md) | Noor | Records archive clerk | After gate |
| [hal.md](hal.md) | Hal | Systems technician | After gate |
| [ada.md](ada.md) | Ada | Night Shift caretaker | After gate |
| [vale.md](vale.md) | Vale | Executive liaison | After gate |
| [pace.md](pace.md) | Pace | Campus performance system (no body) | After gate |
| [glitches.md](glitches.md) | Glitches | Misregistered office objects (encounters) | After gate |
| [background-workers.md](background-workers.md) | Office workers | Ambient staff and silhouettes | After gate |

**Production gate (STYLE_BIBLE §8, ART_BRIEF):** only the Engineer's four idle facings and one walk cycle are produced now. They are shown at 16×24 in the `scale-test/` Orientation scene at ×4 on a 1366×768 screen, with a door, terminal, NPC, two-cell route, and keyboard inset. The player reviews that gate. Do not start any other sheet's sprites, portraits, or atlases until it passes.

## Shared rules for every person sprite

These apply to every human character. Individual sheets list only what differs.

### Frame, camera, scale

| Item | Rule |
| --- | --- |
| Camera | High three-quarter overhead, orthographic; north at screen top; no perspective convergence |
| World frame | **16×24 logical px** (1 × 1.5 cells), one-cell (16×16) ground footprint |
| Anchor | Feet at **bottom-centre**; contact shadow tied to it |
| Portrait | **48×48 logical px**, head and shoulders, same palette, shown at the world's scale factor |
| View / display | 320×180 logical; whole-number nearest-neighbour only (×4 on 1366×768, ×6 on 1920×1080) |
| Grid | One pixel grid for everything; never mix pixel sizes or scale sprites fractionally |

### Body construction (16×24)

- Head about 9–10 px high and 9–10 px wide, torso about 7–8, legs and feet about 6–7. These are checks, not a template.
- Visible hair crown and shoulder tops; a face seen from above.
- Short but articulated limbs; asymmetric, human stance (no front-facing icon, no oversized circular head on a rectangular coat).
- Face at 1× is **two eye pixels and a hair-shadow line**. Expression comes from pose and from the portraits.
- Hair, skin, jacket, trousers, and shoes each get **2–3 deliberate tones**.
- Costume detail stays subordinate to pose. A badge or strap may mark a role, but the character must read without it.
- Finish targets the richer 16-bit craft of references 02, 04, and 07: deliberate intermediate shades and expressive clusters. Do not copy the flat 8-bit blockouts.

### Pixel and light rules

- Hard square pixels, hand-placed clusters. No gradients, antialiasing, soft brushes, vector curves, bloom haze, or scanlines.
- A single isolated pixel only when it carries an eye, spark, button, or glint.
- Light from the **upper left**; step through highlight → midtone → cool shadow → deepest occlusion.
- Default outer outline is **`#202337`**. On lit edges, swap short runs for the material's own dark tone. Use the darkest ink only where silhouettes overlap. No complete thick black ring.
- Contact shadow: compact, blue-purple (`#535971` → `#343650` → `#202337`), darkest at the feet.
- No dithering on faces or outlines.

### Orientation production palette (STYLE_BIBLE §3)

| Group | Shadow → light | Reserved meaning |
| --- | --- | --- |
| Ink / outline | `#202337` `#343650` `#535971` `#777A8C` | Contour, cool shadow |
| Warm stone | `#665D65` `#968A85` `#C7B7A0` `#F0DEC0` | — |
| Blue glass / metal | `#203A50` `#366479` `#5AA3AE` `#A0DDD4` | — |
| Wood / terracotta | `#523D4C` `#85565A` `#BA785F` `#E4AA73` | — |
| Garden green | `#21484A` `#326D60` `#5FA06D` `#B2CE78` | — |
| Brass / discovery | `#705056` `#AC7655` `#E1AC62` `#F5D580` | Opened routes (use sparingly) |
| Coral / people | `#71394F` `#B65761` `#E67A70` `#F6B18E` | Conversation accents |
| Violet / anomaly | `#413755` `#67547C` `#9477AF` `#C3A6D6` | **Glitches only** |

Functional UI anchors (from `docs/game-design.md`): ink `#182B38`, paper `#F4F2EC`, terminal teal `#19AFA2`, conversation coral `#EC776D`, glitch violet `#9876D5`, discovery gold `#E6B750`. No person may wear violet. Teal on clothing must be a muted ramp (hue 160°–200° steps at or below 60% HSL saturation, never a marker hex), and gold stays small on people, so neither reads as an interaction marker (STYLE_BIBLE §3, decided 2026-10-01).

The Records, Systems, Night Shift, and Executive palettes exist only as words (`docs/game-design.md` district table). **Open:** those four palettes need hex sheets before their characters' clothing ramps are final. Until then, each sheet gives provisional mappings onto the 32 Orientation colors.

### Skin and hair

Every character needs separate skin and hair ramps (STYLE_BIBLE §3). Ramps recorded so far, all provisional (scale-test placeholders):

| Character | Skin ramp | Hair ramp |
| --- | --- | --- |
| Engineer (default) | `#6E4433` `#9C6448` `#C98B62` `#E8B184` | `#2B1E26` `#4A2E2E` `#6E4434` `#93603F` |
| Ivo | `#8A5A4A` `#C08870` `#E3B094` `#F6D2B8` | `#535971` `#8C8F9C` `#BFC0C6` `#E6E4E0` |
| Mira | `#3E2630` `#5E3A36` `#85563F` `#A9744F` | `#1E1A26` `#332833` `#4D3A44` `#6B5058` |
| Noor, Hal, Ada, Vale | **Open** | **Open** |

When choosing the open ramps, keep the cast inclusive and visually distinct from one another at 1×. Don't reuse one ramp across characters.

### Animation set (every recurring character)

- Four facings: **S, N, E, W**, consistent volume. Draw E and W separately for any character with asymmetric detail (bag side, jacket panel), so mirroring doesn't swap the detail.
- Idle (restrained loop), walk (**4–6 frames per direction** to start), interact, and **two reusable reaction poses**. Add frames only where a motion test shows a visible benefit.
- Timing should feel responsive to each keypress.
- Review at native 1×, nearest 2× (for diagnosis only), and in the gameplay crop with the keyboard inset open.

**Assumption (naming):** the docs ask for consistent animation and anchor names but don't set a format. Proposed: `<character>_<animation>_<facing>_<frame>`, for example `mira_walk_e_03`, with anchor `feet_bc`.

### Interaction cues around characters

- NPCs stand in open walking cells (terminals sit in furniture; glitches move on the floor).
- An NPC with an available conversation gets a coral marker with a distinct speech-bubble **shape**; color never carries meaning alone.
- An interaction outline appears when the player is in range.
- NPCs react visibly when a quest resolves (pose or position change).

### Don'ts for every character

- Don't add accessories, colors, weapons, clothing, abilities, or lore that the documents don't permit.
- Don't copy or trace characters from any reference image or named game.
- There is no combat: no weapons, HP bars, or attack poses.
- No ASCII, CRT, or scanline treatment.
