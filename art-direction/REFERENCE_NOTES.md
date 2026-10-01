# Player-provided visual references — 2026-10-01

**Current production reading:** [STYLE_BIBLE.md](STYLE_BIBLE.md) sets the reference hierarchy, the decided 16×16 / 16×24 scale, and the production review gate. This file only records what each reference image teaches. The seven supplied screenshots are secondary to the approved overhead Kanata Hero image.

Images 01–07 were supplied by the player and copied unchanged to `art-direction/references/`. Image 08 is the player-approved Kanata Hero overhead concept generated during this discussion. They are **inspiration**, not source assets for the game. Translate the visual principles below into original office architecture, sprites, props, and UI. Do not trace or reproduce characters, buildings, tiles, iconography, HUDs, logos, or fantasy objects. Image 03 has a visible website watermark and must never be used as a production image.

| ID | File | What the team should study | What does not transfer |
| --- | --- | --- | --- |
| 01 | `references/01-route-readability.png` | Walkable paths read at first glance; avatar and interaction target remain recognizable within a broad top-down scene; terrain value separates route and obstacle. | Outdoor grass, cliffs, enemies, and game HUD. |
| 02 | `references/02-crisp-pixel-shapes.png` | Confident pixel clusters, dark contour control, vivid but organized local color, small expressive figures, props that announce their function. | Farm, fantasy buildings, combat cues, and lettering. |
| 03 | `references/03-modular-town.png` | Repeated modules create a coherent place; generous circulation and clustered landmarks keep navigation legible. | Roofs, houses, vegetation shapes, watermark, and its lower-detail character treatment. |
| 04 | `references/04-material-depth.png` | Strongest environment craft reference: top and side planes, contact shadows, repeated paving motifs, layered entrances, believable object height, and clean walkable space at game scale. | Market stalls, town buildings, fantasy costumes, or direct palette sampling. |
| 05 | `references/05-light-and-ui-contrast.png` | Local pools of light and foliage contrast; dark, opaque UI frames keep commands readable over detailed game art. | Combat interface, HP/MP bars, forest, and characters. Our game uses calm modern DOM text and untimed repairs. |
| 06 | `references/06-prop-atlas.png` | A small kit of consistently lit, scale-matched objects can populate many rooms; each prop has clear top/side planes and a readable shadow. | Fantasy furniture, banners, statues, grass background, and exact silhouettes. |
| 07 | `references/07-focal-richness.png` | High-end color separation, lively pixel clusters, expressive pose, and carefully layered foliage. Apply this degree of richness to the indoor garden landmark and selected hero moments. | Crowded combat scene, effects density, fantasy cast, and detail level on every ordinary tile. |
| 08 | `references/08-approved-overhead-direction.png` | **Chosen Kanata Hero direction:** high overhead orthographic camera, a compact garden with a clear walking ring, small game-scale characters, modular office props, and rough retro pixels. | It is a generated concept, not an exact tile map, frame-size proof, collision layer, or asset atlas. |

## Combined direction for Kanata Hero

The first drafts missed the references: the characters looked like flat front-facing icons, and the lobby looked like a labeled floor plan. The next visual gate must look like a playable, three-quarter pixel-art office. Use the depth and materials of 04, the clean prop grammar of 06, the path clarity of 01/03, the controlled sprite contrast of 02, and the focal finish of 07. Keep the visual production budget in `docs/game-design.md`: one rich landmark per district, a reusable office kit for ordinary rooms, 16×16 floor cells, 16×24 people on one-cell footprints, and readable UI at 1366×768.

For Orientation, make the garden **lush but spatially contained**. The office remains welcoming in daylight; uncanny repetition is subtle. The new art must show depth through visible wall faces, planter side planes, shadows, floor material transitions, and character contact with the ground. Labels and diagram arrows may exist on a separate planning overlay but should not carry the gameplay composition.

## Review gate

The current gate is [STYLE_BIBLE §8](STYLE_BIBLE.md#8-production-review-gate): the Engineer's four idle facings and one walk cycle at 16×24 in the `scale-test/` scene at ×4 on 1366×768. An earlier gate based on 48×64 sprites is retired. The rejected first studies remain process records only.
