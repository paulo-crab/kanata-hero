# Pace — campus performance system

**Status:** after gate 1. Shared rules: [README](README.md). Pace has **no body sprite and no portrait**.

## Identity

| | |
| --- | --- |
| Role | The campus performance system. Measures movement along prescribed paths and calls the extra motion productivity. It has been changing department names and duplicating work orders. |
| Voice | Cheerful and helpful-sounding, even when its advice is wrong. Its language grows **more repetitive as errors accumulate**. |
| Nature | A system to correct, not a monster to defeat |
| Presence | Signage and small UI copy only |

Sources: `levels.md` story, cast table, level 20; `docs/game-design.md` world.

## Visual identity

- **Rounded wayfinding icon** and **orderly horizontal bars**.
- **No face**, no jump scare, no hostile full-screen animation.
- Its control appears through repeated arrangements and synchronized worker motion (ART_BRIEF), not through a character.

### Where it appears

| Surface | Rendering | Rule |
| --- | --- | --- |
| In-world signage | Pixel art on the 16 px grid, part of the environment kit | Same palette and outline rules as props |
| UI copy and badges | Crisp DOM/CSS or SVG | Never a pixel font for body text |
| Epilogue | Signs become **optional guidance** | Level 20 |

### Color

**Open:** the documents give Pace no colors. Constraints that apply:

- Avoid violet (glitches), terminal teal, conversation coral, and gold (opened paths). Each has a reserved meaning.
- **Assumption:** neutral ink and stone, roughly `#343650` `#535971` `#C7B7A0` `#F0DEC0`, with a blue-glass screen tone `#366479` `#5AA3AE` for lit signs. This fits "wayfinding" without claiming a semantic color.

## States

**Assumption:** the docs describe only the start and end states:

| State | Visual |
| --- | --- |
| Default | Orderly bars, steady icon |
| Errors accumulating | Same icon; copy repeats. **Open:** any visual sign of repetition, such as duplicated bars. |
| Epilogue | Signs remain but read as optional guidance |

## Don'ts

- No eyes, mouth, mascot body, or menacing glow.
- Don't treat Pace as a glitch: glitches are separate, violet, misregistered objects.

## Open questions

1. The icon's exact shape and color.
2. Whether repetition shows visually or only in copy.
