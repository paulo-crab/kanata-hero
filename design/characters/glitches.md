# Glitches — misregistered office objects

**Status:** after gate 1. Shared rules: [README](README.md).

## Identity

| | |
| --- | --- |
| What they are | Misregistered office objects in some rooms. Not monsters. |
| Behavior | Roaming. Touching one opens a short, **untimed, turn-based repair duel**: fix a token, choose a route, or edit a code fragment. Immediate retry; no random ambushes or speed gate. |
| First appearance | A harmless **paper-fold glitch** in level 01, after the movement tutorial |

Sources: `docs/game-design.md` world, sprite table; `levels.md` story, level 01; STYLE_BIBLE §3, §7.

## Archetypes

Start with **three reusable silhouettes**. The docs offer these as examples ("such as"):

| Archetype | Silhouette idea | Size |
| --- | --- | --- |
| **Displaced stapler** | An ordinary stapler slightly offset from its own shadow or outline | 16 px |
| **Duplicate chair shadow** | A chair shadow with no chair, or two shadows on one chair | 16–32 px |
| **Folded form** | A sheet of paper folded wrongly; the level 01 paper-fold glitch | 16 px |

Size range: **16–32 logical px**, depending on role. Distinguish encounters with **palette and behavior variants**, not new art.

## Rendering

- **Violet / anomaly ramp only:** `#413755` `#67547C` `#9477AF` `#C3A6D6` (UI anchor `#9876D5`). Glitches are the only thing in the world that uses violet.
- **Solid housing first**, then a violet emissive centre. **Glow never erases the silhouette.** At most one or two hard-edged glow steps.
- Base object colors come from the normal prop kit (stone, ink, paper). Violet marks the misregistration, so the object stays recognizable.
- They **move or animate against the floor**. That motion is one of the three interaction silhouettes (NPCs stand in open cells, terminals glow in furniture, glitches move).
- Violet must pair with a distinct **shape cue** (for example, the offset outline), so color never carries meaning alone.
- No dithering on outlines; no scanlines, chromatic aberration, or CRT effects.

## Animation

**Assumption:** the docs specify movement and animation but no frame counts:

| Set | Spec |
| --- | --- |
| Roam | Small looping drift or hop along the floor, 2–4 frames |
| Misregister | A 1–2 px offset flicker between the object and its outline or shadow |
| Repaired | Snaps back into register, then becomes an ordinary prop or disappears |

Keep them out of text-editing focus areas. A wrong key gets a local reaction, never a full-screen effect.

## Don'ts

- No faces, teeth, claws, or hostile creatures.
- No HP bars or combat interface.
- Not Pace: Pace is the system and has no violet.

## Open questions

1. Final choice of the three archetypes, and which variants appear in which district.
2. What a repaired glitch becomes: an ordinary prop, or gone.
