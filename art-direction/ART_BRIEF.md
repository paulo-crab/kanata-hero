# Kanata Hero — current art direction

Read `STYLE_BIBLE.md` first, then this file, `../docs/game-design.md`, `../levels.md`, and `REFERENCE_NOTES.md`. The [document map](../README.md) lists every document's status. The approved overhead image is the primary authority; the other seven are secondary. Files under `characters/`, `environment/`, `ui/`, and `director-sketches/` are rejected scripts or historical notes. Do not inspect, run, edit, or reuse them as art direction.

## Chosen look

`references/08-approved-overhead-direction.png` is the visual target the player chose. Use its high, orthographic, retro RPG camera; unmistakable walking loop; small readable people; sharp pixel clusters; and compact garden landmark. The seven player screenshots in `references/01`–`07` provide supporting principles recorded in `REFERENCE_NOTES.md`. Translate them into original office art; do not reproduce their game assets.

Keep one logical pixel scale across world and cast: **16×16 tiles, 16×24 people, a 320×180 view at whole-number scale** (decided 2026-10-01; see `scale-test/`). **Character finish targets the richer 16-bit pixel craftsmanship in references 02, 04, and 07, not the flat 8-bit-like blockouts in `character-current/`.** Give faces, hair, clothing, stance, and props deliberate intermediate shades and expressive pixel clusters while keeping crisp edges and the same logical resolution. Ordinary rooms use a small modular kit of stone floor, glass wall, desk, shelf, door, planter, and terminal shapes. Give each district one carefully colored landmark at the same pixel resolution. Avoid glossy reflections, painterly lighting, and a dense plant or prop at every cell.

At a 1366×768 laptop composition (×4), keep the avatar, two-cell routes, exits, NPCs, and task marker legible when the keyboard inset is open. The visible cell count may vary responsively. UI text and key diagrams stay crisp modern DOM/CSS elements, separate from world pixels. Teal terminals, coral conversations, violet glitches, and gold opened paths also need distinct icons or silhouettes.

Orientation starts warm and welcoming. Pace's control appears through repeated arrangements and synchronized worker motion; its correction opens a garden cut-through and Records door, lights devices, and lets workers relax. Story interactions are untimed. Mira's courier routes are the optional speed activity.

## Current workflow

The player has discarded all earlier character and environment drafts, including every 72×96 Engineer experiment; do not use anything in `character-current/`, `characters/`, `environment/`, `ui/`, or `director-sketches/` as reference. New work starts from `scale-test/`, which sets the 16 px layout, palette use, and on-screen size with placeholder art. Next gate: the Engineer's four idle facings and one walk cycle at 16×24 in that scene at ×4 on 1366×768, judged against references 02, 04, 07, and 08, before the rest of the cast, portraits, atlases, environment, or UI.
