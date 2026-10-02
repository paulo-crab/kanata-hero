# Kanata Hero — visual style bible

**Status:** governs all new art, 2026-10-01. **Scale decided:** 16×16 tiles and 16×24 people on a 320×180 view, chosen by the player from the side-by-side test in [`scale-test/`](scale-test/). The earlier 48×48 / 72×96 prototype and all previous character and environment drafts are retired. `docs/game-design.md` and `levels.md` carry the same numbers.

**Primary visual authority:** [08 — approved overhead direction](references/08-approved-overhead-direction.png). Match its high overhead camera, office setting, open walking routes, compact garden landmark, warm floor, blue glass, and small readable people. The seven player screenshots are secondary craft references. [Visual board](STYLE_BOARD.html) shows the hierarchy, palette, and scale together.

> Asset brief: “Use the approved overhead Kanata Hero image as the authoritative composition and world-style reference. Preserve its camera, visual hierarchy, warm/cool palette relationship, pixel density, selective outlines, and gameplay readability. Use the seven player screenshots for additional pixel craft, material depth, and character expression. Draw original office assets that belong to the same game.”

## 1. The visual contract

Kanata Hero is an **overhead, orthographic, three-quarter pixel-art adventure** in a contemporary office. It uses the craft of a strong SNES-era game: hard square pixels, hand-placed clusters, restrained color ramps, readable silhouettes, and selective dark contours. It does not imitate a side-scrolling fantasy world. Translate worn stone, moss, wood, and brass into paving, the indoor garden, furniture, and wayfinding trim. Teal devices and violet anomalies take the place of magical glow.

All world art shares **one pixel grid**. Draw at native logical resolution with integer coordinates. Render with nearest-neighbor sampling and integer zoom. Do not paint a high-resolution picture and apply a pixel filter. No gradients, antialiasing, soft brushes, smooth vector curves, photoreal surfaces, bloom haze, scanlines, or stray single-pixel noise. A single isolated pixel is permitted when it carries a specific eye, spark, button, or glint.

The world can be richly colored without making every tile busy. Characters and a district landmark receive the most deliberate clusters. Ordinary floors and repeatable furniture stay simpler so routes and interactions remain clear.

## 2. Reference hierarchy

| Reference | Use for | Boundary |
| --- | --- | --- |
| **08 approved overhead** | Camera, office palette relationship, garden/ring composition, pixel density, play-space hierarchy | Concept only; no tracing or use as a tile map |
| 01 route readability | Clear walkable routes and target contrast | No outdoor terrain or HUD |
| 02 crisp pixel shapes | Cluster discipline, lively local color, small readable figures | No copied farm assets |
| 03 modular town | Repetition, circulation, landmark spacing | No roofs, buildings, or watermark |
| 04 material depth | Top/side planes, contact shadows, paving, character scale in scene | No market assets |
| 05 light and UI contrast | Local light emphasis and opaque UI readability | No combat interface |
| 06 prop atlas | Consistent prop scale and light direction | No fantasy furniture |
| 07 focal richness | Expressive character pixels and one rich garden/hero moment | Not the density of every room |

The secondary screenshots never overrule the primary image's camera or office setting. Do not copy characters, tiles, buildings, icons, logos, or composition fragments from any reference.

## 3. Palette

Use the following **32-color starting palette** for Orientation. It is a production palette, not an SNES hardware emulation or a limit on all five districts. Reserve the bright accents for their meaning. Each ordinary sprite or prop should use a compact subset, usually three or four tones per material.

| Group | Shadow → mid → light | Use |
| --- | --- | --- |
| Ink / outline | `#202337` · `#343650` · `#535971` · `#777A8C` | Blue-purple contour, cool shadows |
| Warm stone | `#665D65` · `#968A85` · `#C7B7A0` · `#F0DEC0` | Floor, walls, warm highlights |
| Blue glass / metal | `#203A50` · `#366479` · `#5AA3AE` · `#A0DDD4` | Windows, partitions, terminals |
| Wood / terracotta | `#523D4C` · `#85565A` · `#BA785F` · `#E4AA73` | Desks, seats, warm trim |
| Garden green | `#21484A` · `#326D60` · `#5FA06D` · `#B2CE78` | Planters, leaves, moss |
| Brass / discovery | `#705056` · `#AC7655` · `#E1AC62` · `#F5D580` | Latches, wayfinding, opened routes |
| Coral / people | `#71394F` · `#B65761` · `#E67A70` · `#F6B18E` | Conversation accents, upholstery |
| Violet / anomaly | `#413755` · `#67547C` · `#9477AF` · `#C3A6D6` | Glitches only |

The outer outline defaults to **`#202337`**. Replace short sections with a material's dark tone on a lit edge; use the darkest ink only where silhouettes overlap or forms need separation. Avoid complete thick black rings. Top-left skylight and lamps use the warm stone/brass highlights; cast and recess shadows step through `#535971`, `#343650`, and `#202337`. Skin and hair need separate inclusive ramps chosen per character; do not treat one skin ramp as the entire cast's palette. UI semantic colors in the game brief remain functional anchors, even if world-art shades shift.

**Clothing vs. interaction markers (decided 2026-10-01).** No person wears violet. Teal may appear on clothing, including the Engineer's default jacket and its customization options, only as a muted ramp: every step with a hue between 160° and 200° keeps HSL saturation at or below 60% (terminal teal `#19AFA2` is about 75%), and no step uses a UI marker hex. Terminals stay distinct through their glow steps and their place inside furniture. Coral and gold on people keep their existing limits: coral is the people/upholstery family and the conversation marker is carried by the speech-bubble shape; gold stays small (badges, latches).

### District palettes (Director decision 2026-10-02)

Each district is 8 ramps of 4 steps, shadow to light, in the same roles as Orientation: ink, floor, wall, glass/metal, wood, foliage, accent and violet. **Ink and violet are copied verbatim into every district**, so contours, cool shadows and glitches look identical everywhere. Floor step 3 is the broad fill and step 2 the slab mid tone, the same indices `environment.py` uses for stone. The darkest step of a ramp goes on contours and joints only. Orientation keeps the table above (its walls share the stone ramp, and coral stays its people ramp). Full derivation, check results and the cast ramps: [palettes/PALETTES_SPEC.md](palettes/PALETTES_SPEC.md); hex sheet: [palettes/palettes-sheet.png](palettes/palettes-sheet.png).

| Ramp | Records | Systems | Night Shift | Executive |
| --- | --- | --- | --- | --- |
| floor | `#46606C` `#6C8996` `#92AEB8` `#BCD0D4` | `#7C8996` `#A2AEB9` `#C8D1D8` `#E8EDF0` | `#12161A` `#242C34` `#364049` `#4C5865` | `#8D8A86` `#B7B3AB` `#D9D5CB` `#F1EEE6` |
| wall | `#756F66` `#A09A8A` `#CDC8B4` `#EBE7D6` | `#3C4A66` `#55698A` `#7C90B0` `#AEBDD3` | `#1B2145` `#283063` `#38437F` `#5062A0` | `#1D2B52` `#2B4079` `#3F5A9E` `#6B84BE` |
| glass / metal | `#1F3745` `#31566A` `#527F94` `#8DB6C2` | `#172B66` `#2347B0` `#2F63D9` `#8CB0F2` | `#2C3560` `#4C5A8E` `#8E96B8` `#D0D4E4` | `#3B5F82` `#6A93B5` `#A5C8DD` `#E1F0F5` |
| wood | `#47202F` `#7B3442` `#A94C47` `#D08060` | `#4B4558` `#7E6F6A` `#B39A7E` `#DCC8A4` | `#3A2230` `#5E3A3E` `#8C5A4A` `#BC8260` | `#3A2630` `#5E3B38` `#8A5A45` `#B98862` |
| foliage | `#2C463F` `#476B59` `#7B9E7F` `#B8CC9E` | `#1D3F46` `#2C7A70` `#5ED0A8` `#B4F0D6` (mint circuitry) | `#1C3A38` `#2A5A4E` `#3F7A63` `#7EA880` | `#1B4A34` `#2F7A45` `#5FAF55` `#B6DB7A` |
| accent | `#6B2F45` `#A9414F` `#D4606A` `#F4B1A4` (coral files) | `#7A2F1B` `#C2521A` `#F2842B` `#FFB36B` (safety orange) | `#7A4A4A` `#B8745A` `#E8A55F` `#F9D79A` (lamp pools) | `#5E2F2B` `#A4573A` `#D88149` `#F2B98A` (copper) |

- **Markers.** No step of any new district ramp is within CIE76 dE 10 of `#19AFA2`, `#EC776D`, `#9876D5` or `#E6B750`. Teal-hued steps (160-200 degrees) on non-device ramps stay at or below 60% saturation. `check_palettes.py` enforces both.
- **Night Shift is a dark-floor district.** The `#202337` outline cannot carry a silhouette on it, so people get a quiet 1 px hard cool moonlight rim in `#8E96B8` (glass step 2) on their upper-left contour, applied per pixel only where it beats the pixel's own contrast against the scene behind it (on the slate floor it replaces the ink outline at 2.5:1 against 2.1:1). Where a warm source lights someone, inside a lamp pool or by Ada's lantern, the warm edge `#F9D79A` (accent step 3) is limited to the head and shoulders (sprite rows 0-12) and the body keeps its ink outline (4.2:1 on a pool). The earlier warm rim everywhere read as a "selected" highlight next to discovery gold and was replaced by the player on 2026-10-02. The contact shadow is floor step 0 over `#202337`, and desks sit in lamp pools drawn as floor fill to accent step 1 with joints in accent step 0. Outline on a pool is 4.2:1. The floor is a cool slate (hue 210, at most 18% saturation) and is deliberately not plum or indigo: no floor or wall step in any district may sit in hue 260-320 degrees above 12% saturation, so violet stays the glitch colour and glitches pop hardest here.
- **Cast skin and hair.** Noor, Hal, Ada and Vale have their own ramps (see PALETTES_SPEC.md "Cast ramps"). Corresponding mid steps are at least dE 12 from every other cast member.

## 4. Camera, grid, and scale

| Element | Production rule |
| --- | --- |
| Camera | High three-quarter overhead, orthographic, north generally at screen top; no perspective convergence |
| Tile | **16×16 logical pixels**; collision is cell based |
| Person frame | **16×24 logical pixels** (1 × 1.5 cells), one-cell ground footprint, feet at the bottom-center anchor |
| Dialogue portrait | **48×48 logical pixels**, same palette, shown at the world's scale factor |
| Prop dimensions | One-cell small prop, two-cell desks and planters, multi-cell walls and garden |
| Logical view | **320×180** (20×11.25 cells) |
| Display | Whole-number nearest-neighbor scaling only: ×4 on 1366×768 (1280×720, letterboxed), ×6 on 1920×1080 |
| Review | The 1366×768 screen with the keyboard inset open, plus a nearest-neighbor ×8 sprite sheet for diagnosis |

This matches the approved overhead image, whose people measure about 16×22 logical pixels on roughly 16-pixel floor slabs. The test showed that 16×24 people stay distinct at laptop size through silhouette, hair, clothing, and props, and that the environment loses almost nothing against a 32-pixel grid at a quarter of the drawing cost. Every asset uses this one grid; never mix pixel sizes. A wider whole-number zoom setting (for example 427×240 at ×3) may show more cells, but sprite pixels must never become fractional or blurred.

## 5. Characters

People have visible hair crowns and shoulder tops, a face seen from above, short but articulated limbs, and a contact shadow tied to the foot anchor. The Engineer should feel observant and capable, with an asymmetric stance and identifiable hair/clothing even at 1×. Do not make a front-facing icon with an oversized circular head and rectangular coat.

For a 16×24 frame, start with a head around 9–10 pixels high and 9–10 wide, a torso around 7–8, and legs/feet around 6–7. These are checks, not a rigid template. Let the silhouette occupy enough of the frame to read without clipping motion. Hair, skin, jacket, trousers, and shoes each use two or three deliberate tones; the face is two eye pixels and a hair-shadow line, so expression comes from pose and from the 48×48 portraits. Keep costume detail subordinate to the pose. A badge or strap may distinguish an office role, but the character must read without it.

Draw four directional facings with consistent volume. After the idle quality bar is approved, build 4–6 walk frames per direction, interact, and a small reusable reaction set. Do not produce an atlas from an unapproved single-facing concept. Evaluate native 1×, nearest 2×, and in the gameplay crop; the 2× view is for diagnosis, not the quality gate.

**Gate 1 animation contract (decided 2026-10-01; may be revised after the gate).** In every 16×24 frame the anchor is the bottom-centre point on the pixel edge between columns 7 and 8 (0-indexed), and the feet rest on row 23. Walk: 4 frames per direction at 133 ms each; one cycle covers 2 cells, about 3.75 cells per second. Idle: 2 frames at 500 ms each.

## 6. Environment and background layers

Use this draw order: **floor → rear walls and floor-height markings → rear props → contact shadows → actors → front props/occluders → local light accents → crisp DOM UI**. Walls and props have readable top planes, side planes, and contact shadows. A player can pass behind a front planter or desk edge without losing their foot anchor. No side-scrolling parallax or horizon layer.

Ordinary floor tiles use broad color groups and occasional wear clusters; do not fill every tile with texture. Repeat a small kit of stone floor, glass partition, wood desk, shelf, door, planter, and terminal. Vary arrangement and a few accents. Give each district **one** richer landmark, at the same pixel size as the rest of the world. In Orientation, the garden is lush but bounded; its walking ring and exits remain clear. Keep doors brighter than dead ends and interaction colors distinct from ambient decoration.

## 7. Light and materials

Use one clear light direction per room, normally warm light from the upper left. Shade by stepped, solid clusters: highlight, local midtone, cool shadow, deepest occlusion. No continuous gradients. Contact shadows are compact, blue-purple, and darkest at feet or furniture bases. A lamp or terminal may have one or two hard-edged glow steps; reserve broader effects for rare focal moments.

- **Stone / concrete:** broad slabs, sparse edge chips, a few two-tone joints; no all-over grain.
- **Glass:** dark frame, cooler pane, one stepped reflection band, visible interior separation.
- **Wood:** top plane warmer and lighter than side plane, a few grain clusters, dark underside.
- **Brass:** small warm highlight and dark edge; use sparingly for doors and wayfinding.
- **Foliage / moss:** leaf masses in 3–4 value groups, broken contour, clustered warm tips; no random single-pixel confetti.
- **Devices / anomalies:** solid housing first, then a teal or violet emissive center; glow never erases the silhouette.

Dithering is rare: one short transition on a large stone or shadow plane when a hard band would distract. Never dither faces, outlines, UI, or every material.

## 8. Production review gate

Before commissioning the cast or environment atlas, show the Engineer's four idle facings and one walk cycle in the 320×180 Orientation scene at ×4 on a 1366×768 screen, with a door, terminal, NPC, clear two-cell route, and the keyboard inset open. `scale-test/` is the starting composition; replace its placeholder art rather than starting from the retired drafts. Review silhouette, expression, material separation, contact with floor, interaction contrast, and whether a player can find the route without labels. The approved overhead image remains the world-style target. The user reviews this visual gate; only then does the team expand to other characters and assets.
