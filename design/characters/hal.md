# Hal — systems technician

**Status:** art complete, 2026-10-02. Idle ×4 and walk ×4 approved by the director; interact, two reactions and the 48×48 chibi portraits (neutral, concerned, pleased, signature `hal_puzzled`) approved by the player 2026-10-02. The pixel spec [HAL_SPEC.md](../../art-direction/cast/HAL_SPEC.md) and [PORTRAITS_SPEC.md](../../art-direction/portraits/PORTRAITS_SPEC.md) are canonical where they differ from this brief. Shared rules: [README](README.md).

## Identity

| | |
| --- | --- |
| Role | Systems technician. Built parts of Pace's routing display and notices its wrong assumptions. Gives Act III quests (12–16) and the **Quiet Alarm** side quest. |
| Personality | Practical and hands-on; anxious when the system misbehaves, focused once a fix is in sight. |
| Pronouns | Not specified; use they/them until decided |
| Signature props | **Folding stool**, **orange tool roll** |

Sources: `levels.md` cast table, Systems row, levels 12–16.

## Silhouette and costume

- **Compact utility vest**: a compact, low silhouette that contrasts with Noor's height and Ivo's breadth.
- **Thick gloves**: hands read larger than the cast default.
- **Folding stool**, carried or set down.
- **Orange tool roll.**

### Look

The documents set no skin or hair colors and no base clothing color. The Systems palette exists only in words: cool porcelain, saturated cobalt, mint circuitry, safety orange.

| Part | Status | Provisional mapping (until the Systems hex sheet exists) |
| --- | --- | --- |
| Hair | **Open** | Distinct from the rest of the cast |
| Skin | **Open** | Distinct from the rest of the cast |
| Utility vest | Assumption | Cobalt, roughly blue glass `#203A50` `#366479` `#5AA3AE` |
| Undershirt / sleeves | Assumption | Porcelain, roughly warm stone `#C7B7A0` `#F0DEC0` |
| Gloves | **Open** | Not specified; keep distinct from skin |
| Tool roll | From docs (orange) | Safety orange is not yet in any ramp. Nearest Orientation tones: `#AC7655` `#E1AC62` (brass) or `#BA785F` `#E4AA73` (terracotta) |
| Stool | Assumption | Ink/metal tones `#343650` `#535971` `#777A8C` |

Keep the orange on the tool roll, so it doesn't read as gold "opened path".

## Sprite (16×24)

- Broad, short torso block with a vest edge visible at the shoulders. Legs at the low end of the 6–7 px range.
- Gloves as 2×2 px clusters, one value darker than the vest.
- Tool roll: a 3×1–2 px orange cluster at the belt or under one arm.
- Stool: separate prop sprite (one cell), so Hal can sit on it.

## Animation

| Set | Spec | Source |
| --- | --- | --- |
| Idle ×4 | Restrained | Standard |
| Walk ×4 | 4–6 frames | Standard |
| **Crouched repair** | Default working pose at machines | Cast table |
| **Seated on stool** | Replaces crouching after the refund sign is fixed | Level 13 |
| **Puzzled** reaction | Head tilt / scratch | Cast table |
| Pull down false panel | One-shot, reveals the Night Shift elevator stop | Level 16 |

## Portrait (48×48, chibi)

Chibi direction C, approved by the player 2026-10-02: oversized round head, tiny shoulders, flat shading, dot eyes. Pixel choices: [PORTRAIT_PERSONAS.md](../../art-direction/portraits/PORTRAIT_PERSONAS.md); atlas keys: `art-direction/portraits/portraits-atlas.json`. **When each face appears** is owned by the [Portrait cue map in `levels.md`](../../levels.md#portrait-cue-map); this table mirrors it, and `levels.md` wins if they differ. A line uses neutral unless a cue says otherwise, including every hint line.

| Atlas key | Reads as | Story cue |
| --- | --- | --- |
| `hal_neutral` | Focused, practical | Default; Quiet Alarm; the end of 13 (sits instead of crouching) |
| `hal_concerned` | Anxious (wide eyes, sweat bead) | 13 before the nightly run; the start of 14 |
| `hal_pleased` | Settled focus (eyes open) | The 14 fix; the 16 seal |
| `hal_puzzled` | Puzzled (signature) | 12 relocated keypad; 15 formula reveals the detour score on a display Hal built |

## Placement and states

| When | Change |
| --- | --- |
| Level 12 | At the routing machine; asks for IDs as printed |
| Level 13 | Crouch → sit on stool |
| Level 14 | Portrait anxious → focused (`hal_concerned` → `hal_pleased`) |
| Level 16 | Pulls down a false panel; Systems seal |
| Level 20 | Arrives at the atrium (silhouette first, then sprite) |

## Assumptions

1. Vest and undershirt colors follow Systems' listed materials.
2. The stool is a separate prop, not part of the walk sprite.

## Open questions

1. Skin, hair, and glove ramps.
2. The Systems hex palette, including a real safety orange.
3. Pronouns.
