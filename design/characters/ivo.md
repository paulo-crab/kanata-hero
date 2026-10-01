# Ivo — reception lead

**Status:** idle ×4 and walk ×4 **APPROVED by the player 2026-10-02**: [`art-direction/cast/IVO_SPEC.md`](../../art-direction/cast/IVO_SPEC.md). Shared rules: [README](README.md).

## Identity

| | |
| --- | --- |
| Role | Orientation reception lead. Gives the Act I quests (01–06) and the **Plant Tags** side quest. |
| Personality | Precise. Believes clear instructions help people; begins to question the repeated onboarding scripts. |
| Pronouns | Not specified; use they/them until decided |
| Signature prop | **Rectangular tablet** |

Sources: `levels.md` cast table, levels 01–06, side quests; `docs/game-design.md` "Camera, scale, and sprite rules".

## Silhouette and costume

- **Broad cardigan silhouette**: the widest torso in the cast.
- **Rectangular tablet**, held in the left hand against the front of the body (Director decision 2026-10-02: every person stays inside the 16×24 frame), readable at 1×.
- Concept 08 shows a grey-haired figure holding a light tablet beside the garden, which matches.

### Look (provisional, from the scale-test placeholder)

| Part | Provisional ramp | Notes |
| --- | --- | --- |
| Hair | `#535971` `#8C8F9C` `#BFC0C6` `#E6E4E0` | Silver-grey, close to the head |
| Skin | `#8A5A4A` `#C08870` `#E3B094` `#F6D2B8` | |
| Cardigan | `#523D4C` `#85565A` `#BA785F` `#E4AA73` | Wood/terracotta (matches Orientation's terracotta upholstery) |
| Shirt (front opening) | `#5C4038` `#9A6A3E` `#C99A4E` `#EDCB7A` | Ochre strip down the centre |
| Trousers | `#202337` `#2C3352` `#3E4870` `#59658F` | Navy |
| Shoes | Ink ramp | |
| Tablet | Blue glass `#203A50`–`#A0DDD4` | Screen line in teal (see open question 1) |

## Sprite (16×24)

- Cardigan spans nearly the full 16 px width at the shoulders. The legs are slightly narrower, so the shape tapers.
- The tablet is held flat at the chest and drawn as a 5×4 px rectangle with a dark bezel, a bright screen and a thumb on the edge (Director decision 2026-10-02, after the player found the 4×3 version unreadable). It's the read-at-a-glance prop. It shows at screen-right facing S, as an ink back at screen-left facing N, and at the leading edge facing E or W.
- Upright, orderly posture. Their precision shows in a level stance, not in detail.
- Tablet held on one fixed side means **E and W are drawn separately**.

## Animation

| Set | Spec | Source |
| --- | --- | --- |
| Idle ×4 | Restrained; tablet held | Standard |
| Walk ×4 | 4–6 frames, measured pace | Standard |
| Interact | Tablet raised toward the player | Standard |
| **Scripted greeting wave** | Mechanical, repeatable | Level 01 |
| **Nod** | Replaces the scripted wave after the Lobby route | Level 01 |
| **Unscripted laugh** | The wave becomes a laugh after the Orientation review | Cast table |
| Tablet flashing | Screen flashes until The Clock is solved, then stops | Level 03 |

## Portrait (48×48)

**Assumption:** expressions follow their arc, since none are named:

1. Polite, scripted smile (default)
2. Questioning (doubting the onboarding script)
3. Laughing (post-review)

## Placement and states

| When | Change |
| --- | --- |
| Level 01 | At the lobby route; scripted wave → nod. Turnstile opens. |
| Level 03 | Tablet stops flashing |
| Level 06 | Brings a spare keyboard to the garden review table; afterwards the laugh replaces the wave |
| Level 20 | Arrives at the atrium (silhouette first, then sprite) |

## Assumptions

1. Colors and hair shape follow the scale-test placeholder.
2. The portrait set is derived from their story arc.

## Open questions

1. ~~**Tablet screen color.**~~ **Decided 2026-10-02:** blue glass. It never uses `#19AFA2`, the glint is limited to 1 px, and there is no halo. The Level 03 flash alternates glass steps only.
2. Pronouns.
