# Ada — night caretaker

**Status:** art complete, 2026-10-02. Idle ×4 and walk ×4 approved by the director; interact, two reactions and the 48×48 portrait (neutral, concerned, pleased) approved by the director. The pixel spec [ADA_SPEC.md](../../art-direction/cast/ADA_SPEC.md) and [PORTRAITS_SPEC.md](../../art-direction/portraits/PORTRAITS_SPEC.md) are canonical where they differ from this brief. Shared rules: [README](README.md).

## Identity

| | |
| --- | --- |
| Role | Night caretaker who sees what happens when staff leave. Gives Act IV quests (17–19) and the **Desk for Dawn** side quest. Teaches how to leave practice mode safely. |
| Personality | Direct, kind, practical about recovery. Calm. |
| Pronouns | Not specified; use they/them until decided |
| Signature prop | **Warm lantern** |

Sources: `levels.md` cast table, Night Shift row, levels 17–19.

## Silhouette and costume

- **Long coat**: the only long hem in the cast.
- **Warm lantern** carried in one hand.
- **Calm posture**; steady gestures in otherwise still rooms.
- **Warm rim light**: the lantern lights the character's edge against the dark floor.

### Look

The documents set no skin, hair, or coat colors. The Night Shift palette exists only in words: deep indigo, plum, muted silver, warm pools of light.

| Part | Status | Provisional mapping (until the Night Shift hex sheet exists) |
| --- | --- | --- |
| Hair | **Open** | Distinct from the rest of the cast; must separate from indigo floors |
| Skin | **Open** | Distinct from the rest of the cast |
| Coat | **Open** | Must separate in value from indigo/plum floors. Avoid the violet ramp (reserved for glitches). |
| Lantern | From docs (warm) | Housing in ink `#343650` `#535971`; light in brass `#E1AC62` `#F5D580` |
| Rim light | From docs | 1 px warm brass edge on the lantern side only |

## Sprite (16×24)

- Coat hem stops just above the feet, so the walk still shows foot placement and the anchor stays readable.
- Lantern: solid housing first, then a 1–2 px warm centre with **one or two hard-edged glow steps** at most (STYLE_BIBLE §7). Glow never erases the silhouette.
- Lantern on a fixed hand means **E and W are drawn separately**.
- Night readability: keep strong edge light and character contrast even in the darkest rooms (`docs/game-design.md`).

## Animation

| Set | Spec | Source |
| --- | --- | --- |
| Idle ×4 | Very restrained; lantern still | Cast table |
| Walk ×4 | 4–6 frames, unhurried; coat sways 1 px | Standard |
| **Walk alongside** | Escorts the player for a short stretch after the vestibule opens | Level 17 |
| Interact | **Steady gesture**, e.g. raising the lantern toward an object | Cast table |
| Reaction ×2 | **Assumption:** (a) calm nod; (b) serious, explaining the recovery steps | Derived |

## Portrait (48×48)

**Assumption:** expressions follow their voice:

1. Calm (default)
2. Serious / instructive (practice-mode safety and recovery)
3. Warm (break room and service corridor lit)

The lantern's warm light on one side of the face is consistent across variants.

## Placement and states

| When | Change |
| --- | --- |
| Level 17 | Meets the player in the warmly lit break room; walks alongside after the security glass opens |
| Level 18 | Opens the north stair |
| Level 19 | Night seal; break room and service corridor light up |
| Level 20 | Arrives at the atrium (silhouette first, then sprite) |

## Assumptions

1. The rim light is drawn into the sprite as a fixed 1 px edge, not a runtime effect.
2. The reactions and portraits are derived from their voice.

## Open questions

1. Skin, hair, and coat colors.
2. The Night Shift hex palette.
3. Pronouns.
