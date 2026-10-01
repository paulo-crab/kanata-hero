# Proposal

## Why

The design documents describe the whole game: five districts, a recurring cast, glitches, the UI and a keyboard teaching layer. Only the Orientation vertical slice has approved art so far: the Engineer, Ivo, Mira and the review room. Developer agents need a complete, consistent, machine-readable asset set, and specs they can implement against, so they never have to invent visuals.

## What Changes

- The rules already approved at Gate 1 and in the style bible become specs: scale, palette, marker colours, light and contour, and draw order.
- Every recurring character (Engineer, Ivo, Mira, Noor, Hal, Ada, Vale) gets approved 16×24 sprites: idle ×4 and walk ×4 first, then interact, reaction and story-specific sets, and 48×48 portraits.
- Background workers, three glitch archetypes and Pace's signage are drawn.
- Each of the five districts gets a palette hex sheet, a reusable tile and prop atlas with collision and layer metadata, and its one landmark with before and after quest states.
- The DOM/CSS UI is specified as design tokens and components: keycap, keyboard inset, dialogue panel, HUD, prompts, journal and Layout help.
- A developer handoff document indexes every asset, file format, anchor, layer, palette token and rebuild step.
- The interim planning folder `art-direction/production/` is retired in favour of this change. `art-direction/PRODUCTION_STATUS.md` remains the pipeline guide and points here.

## Capabilities

### New Capabilities
- `art-style-foundation`: the visual contract every asset must satisfy. It covers the grid and scale, the integer display zoom, the palette and district palettes, interaction-marker colour rules, light and contour rules, and layer draw order.
- `character-sprites`: the person-sprite contract. It covers frame, anchor, facings, idle and walk timing, the cast frame rule, hair and prop readability, customization by ramp swap, portraits, the source-of-truth format and the automated checks.
- `environment-kit`: tiles, props, landmarks and quest-state art per district. It covers the atlas format, cell footprints and collision, door and light states, and composition rules (routes, doors, landmark budget).
- `ui-presentation`: the crisp DOM/CSS layer over the pixel world. It covers tokens, the keyboard teaching inset, dialogue, HUD, interaction markers by shape and colour, and readability at 1366×768.
- `art-asset-handoff`: what developer agents receive. It covers the asset index, atlas and metadata formats, rebuild commands, and the rule that PNG and JSON files are generated outputs.

### Modified Capabilities

None. `openspec/specs/` is empty.

## Impact

- Files are added and updated under `art-direction/` (gate1, cast, environment, ui) and `design/characters/`.
- New decisions are logged in `README.md`, and STYLE_BIBLE §3 gains district palettes.
- The scripts need Python with Pillow and numpy.
- No game code is written. The output is assets and specifications for the later OpenSpec implementation of the browser game described in `docs/game-design.md`.
