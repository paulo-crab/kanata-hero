# Noor — archive clerk

**Status:** art complete, 2026-10-02. Idle ×4 and walk ×4 approved by the director; interact, two reactions and the 48×48 chibi portraits (neutral, concerned, pleased, signature `noor_unimpressed`) approved by the player 2026-10-02. The pixel spec [NOOR_SPEC.md](../../art-direction/cast/NOOR_SPEC.md) and [PORTRAITS_SPEC.md](../../art-direction/portraits/PORTRAITS_SPEC.md) are canonical where they differ from this brief. Shared rules: [README](README.md).

## Identity

| | |
| --- | --- |
| Role | Records archive clerk and keeper of the unaltered paper records. Gives Act II quests (07–11) and the **Misfiled Minute** side quest. |
| Personality | Precise, with dry humor; quietly defiant. Leaves notes like "equivalent" omitting the actual destination (artifact: *Noor's annotation*). |
| Pronouns | she/her (decided by the player 2026-10-02, matching `levels.md`) |
| Signature prop | **Cherry-wood stamp** and **file tabs** |

Sources: `levels.md` cast table, Records row, levels 07–11.

## Silhouette and costume

- **Tall, narrow silhouette**: the tallest-reading and narrowest person in the cast.
- **Rolled sleeves.**
- **Cherry-wood stamp**, plus file tabs carried or visible.
- Posture **straightens as the cabinets open** over Act II.

### Look

The documents set no clothing, skin, or hair colors for Noor. The Records palette exists only in words: desaturated sea blue, linen, cherry wood, coral files.

| Part | Status | Provisional mapping (until the Records hex sheet exists) |
| --- | --- | --- |
| Hair | **Open** | Choose a ramp distinct from Engineer, Ivo, Mira |
| Skin | **Open** | Choose a ramp distinct from the rest of the cast |
| Shirt (rolled sleeves) | Assumption | Linen, roughly warm stone `#968A85` `#C7B7A0` `#F0DEC0` |
| Lower garment | Assumption | Sea blue, roughly blue glass `#203A50` `#366479` `#5AA3AE` |
| Stamp | From docs | Cherry wood, roughly wood ramp `#523D4C` `#85565A` `#BA785F` |
| File tabs | Assumption | Coral and sea blue (matches "coral folders") |

## Sprite (16×24)

- "Tall" must fit the same 16×24 frame. Get height from **narrow shoulders** (about 2 px narrower than the cast default), longer legs (top of the 6–7 px range), and a head toward 9 px. Never exceed the frame or change the grid.
- Rolled sleeves show as a 1 px value break at mid-forearm, with skin below it.
- Stamp held at the hip as a 2×2 px cherry cluster with a darker base.
- **Early posture:** slight forward stoop over the desk. **Late posture:** upright (see states).

## Animation

| Set | Spec | Source |
| --- | --- | --- |
| Idle ×4 | Restrained; stamp at hand | Standard |
| Walk ×4 | 4–6 frames, economical stride | Standard |
| Interact / stamp | Stamp-down motion | Level 08 (rejected → accepted mark) |
| Step out from behind the desk | Once, after the door opens | Level 07 |
| Posture states | Stooped → upright, in steps as cabinets open | Cast table |
| Reaction ×2 | **Assumption:** (a) dry, unimpressed; (b) quiet satisfaction | Derived |

## Portrait (48×48, chibi)

Chibi direction C, approved by the player 2026-10-02: oversized round head, tiny shoulders, flat shading, dot eyes. Pixel choices: [PORTRAIT_PERSONAS.md](../../art-direction/portraits/PORTRAIT_PERSONAS.md); atlas keys: `art-direction/portraits/portraits-atlas.json`. **When each face appears** is owned by the [Portrait cue map in `levels.md`](../../levels.md#portrait-cue-map); this table mirrors it, and `levels.md` wins if they differ. A line uses neutral unless a cue says otherwise, including every hint line.

| Atlas key | Reads as | Story cue |
| --- | --- | --- |
| `noor_neutral` | Dry (half-lids, mismatched brows) | 07; the 08 instructions; Misfiled Minute |
| `noor_concerned` | Skeptical / defiant | 08 blaming the re-indexing; 11 sending the correction against Pace |
| `noor_pleased` | Quietly satisfied | 08 stamp changes to accepted; the 11 seal |
| `noor_unimpressed` | Flat lids, sidelong glance (signature) | Pace's claims: 09 moved sign-off, 10 "nobody reviewed" summary, 11 "equivalent" |

## Placement and states

| When | Change |
| --- | --- |
| Level 07 | Waits at the circular desk; steps out from behind it after the door retracts |
| Level 08 | Stamp mark changes from rejected to accepted |
| Level 10 | Places the original report beside the summary |
| Level 11 | Records seal; posture fully upright |
| Level 20 | Arrives at the atrium (silhouette first, then sprite) |

## Assumptions

1. The clothing mapping comes from Records' listed materials. No garment colors are stated in the docs.
2. The posture change is drawn as discrete states, not continuous blending.

## Open questions

1. Skin and hair ramps.
2. Garment type below the waist, and clothing colors.
3. The Records district hex palette.
4. ~~Pronouns.~~ Decided 2026-10-02: she/her.
