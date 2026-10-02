# Glitches — misregistered office objects

**Status:** art approved by the director 2026-10-02. The pixel spec [GLITCHES_SPEC.md](../../art-direction/glitches/GLITCHES_SPEC.md) is canonical where it differs from this brief, and [ART_HANDOFF.md](../../art-direction/ART_HANDOFF.md) indexes the files. Shared rules: [README](README.md).

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
| Repaired | Snaps back into register for one frame (160 ms, play once), then becomes the ordinary prop and stops roaming (decided 2026-10-02; drawn) |

Keep them out of text-editing focus areas. A wrong key gets a local reaction, never a full-screen effect.

## Variants and districts (decided 2026-10-02)

The three silhouettes are reused. A variant swaps the violet steps or changes the behaviour numbers; it never changes the art. Full tables, hexes and the data contract: [GLITCHES_SPEC.md](../../art-direction/glitches/GLITCHES_SPEC.md) "Variants and districts"; the same data is in `glitches-atlas.json` under `variants` and `districts`, keyed by district id.

- **Palette variants:** `standard` (fix a token), `plum` (choose a route), `dusk` (edit a code fragment), each with a lifted `dark_steps` ramp for the Night Shift floor. The colour is a second cue for the duel kind; the shape cue still carries the meaning.
- **Behaviour variants:** `drift` (calm), `patrol` (the approved baseline), `stutter` and `lurk` (uncanny, quiet), `settle` (relief): roam speed, path shape, pause pattern, misregister cadence and amplitude.
- **Ramp:** Orientation calm (1), Records the uncanny begins (2), Systems the peak (3), Night Shift the deepest and quietest (4), Executive relief (1).

| District | First glitch | Archetypes (from level) | Per room |
| --- | --- | --- | --- |
| `orientation` | level 01, the harmless paper fold (`form`, `standard`, `drift`) | form (01), stapler (04) | 1 |
| `records` | level 08 Filing Drift (`form`, `standard`, `drift`); level 07 is glitch-free | form (08), chair (09), stapler (10) | 2 |
| `systems` | level 12 Payroll IDs (`stapler`, `standard`, `patrol`) | stapler (12), form (13), chair (14) | 3 |
| `nightshift` | level 18 No Old Keys (`chair`, `standard`, `lurk`); level 17 is glitch-free | chair (18), form (19), stapler (19) | 2 |
| `executive` | level 20, one per incident branch (`settle`), each in its duel's palette | form (The Name), chair (The Route), stapler (The Count) | 1 |

## Don'ts

- No faces, teeth, claws, or hostile creatures.
- No HP bars or combat interface.
- Not Pace: Pace is the system and has no violet.

## Open questions

1. ~~Final choice of the three archetypes~~ Decided 2026-10-02: displaced stapler, duplicate chair shadow and folded form (`art-direction/glitches/GLITCHES_SPEC.md`).
2. ~~What a repaired glitch becomes~~ Decided 2026-10-02: it snaps into register for one frame, then stays as the ordinary prop and stops roaming. Both are drawn.
3. ~~Which palette and behaviour variants appear in which district~~ Decided 2026-10-02: see "Variants and districts" above.
