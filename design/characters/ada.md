# Ada — night caretaker

**Status:** art complete, 2026-10-02. Idle ×4 and walk ×4 approved by the director; interact, two reactions and the 48×48 chibi portraits (neutral, concerned, pleased) approved by the player 2026-10-02. The pixel spec [ADA_SPEC.md](../../art-direction/cast/ADA_SPEC.md) and [PORTRAITS_SPEC.md](../../art-direction/portraits/PORTRAITS_SPEC.md) are canonical where they differ from this brief. Shared rules: [README](README.md).

## Identity

| | |
| --- | --- |
| Role | Night caretaker who sees what happens when staff leave. Gives Act IV quests (17–19) and the **Desk for Dawn** side quest. Teaches how to leave practice mode safely. |
| Personality | Direct, kind, practical about recovery. Calm. |
| Pronouns | she/her (decided by the player 2026-10-02, matching `levels.md`) |
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

## Portrait (48×48, chibi)

Chibi direction C, approved by the player 2026-10-02: oversized round head, tiny shoulders, flat shading, dot eyes. Pixel choices: [PORTRAIT_PERSONAS.md](../../art-direction/portraits/PORTRAIT_PERSONAS.md); atlas keys: `art-direction/portraits/portraits-atlas.json`. **When each face appears** is owned by the [Portrait cue map in `levels.md`](../../levels.md#portrait-cue-map); this table mirrors it, and `levels.md` wins if they differ. A line uses neutral unless a cue says otherwise, including every hint line.

| Atlas key | Reads as | Story cue |
| --- | --- | --- |
| `ada_neutral` | Calm (heavy lids) | The 17 greeting; 18 "a locked tool need not mean a locked route" |
| `ada_concerned` | Serious, instructive | 17 practice-exit and emergency-exit explanation; Desk for Dawn |
| `ada_pleased` | Warm (closed eyes, widest blush) | 17 once the player confirms understanding and Ada walks alongside; 19 when the break room lights |

No signature expression (none specified). The lantern at the lower right carries the warm side light; no face rim.

## Placement and states

| When | Change |
| --- | --- |
| Level 17 | Meets the player in the warmly lit break room; walks alongside after the security glass opens |
| Level 18 | Opens the north stair |
| Level 19 | Night seal; break room and service corridor light up |
| Level 20 | Arrives at the atrium (silhouette first, then sprite) |

## Assumptions

1. The rim light is drawn into the sprite as a fixed 1 px edge, not a runtime effect.
2. The reactions and portraits are derived from her voice; portrait story cues now live in the `levels.md` Portrait cue map.

## Open questions

1. Skin, hair, and coat colors.
2. The Night Shift hex palette.
3. ~~Pronouns.~~ Decided 2026-10-02: she/her.
