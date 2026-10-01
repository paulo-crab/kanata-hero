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
