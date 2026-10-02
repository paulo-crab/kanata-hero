# Mira — courier

**Status:** art complete, 2026-10-02. Idle ×4 and walk ×4 approved by the director; interact, two reactions and the 48×48 chibi portraits (neutral, concerned, pleased, signature `mira_grin`) approved by the player 2026-10-02. The pixel spec [MIRA_SPEC.md](../../art-direction/cast/MIRA_SPEC.md) and [PORTRAITS_SPEC.md](../../art-direction/portraits/PORTRAITS_SPEC.md) are canonical where they differ from this brief. Shared rules: [README](README.md).

## Identity

| | |
| --- | --- |
| Role | Courier who knows every shortcut. Gives the optional speed side quests in Orientation, Records, Systems, and Night Shift. Arrives at the Executive Floor only for the finale. |
| Personality | Playful at first; later admits she kept copies of routes Pace tried to erase. Her story is about learning a place well enough to move through it confidently. |
| Pronouns | She/her (as written in `levels.md` and `docs/game-design.md`) |
| Signature prop | **Coral messenger bag** |

Sources: `levels.md` cast table, Mira route table; `docs/game-design.md` "Characters and UI", side quests.

## Silhouette and costume

- **Messenger bag** with a **coral strap** worn diagonally across the torso. The strap must stay visible **even in dark rooms** (Night Shift).
- **Asymmetric jacket**: the two halves differ.
- **Energetic stride** and a **lively diagonal posture**: she leans into motion even at idle.
- **Distinctive coral accent**: the bag and strap are her identity color.
- **Delivery patches** are added one at a time on her outfit (see "Patch states").

### Look (provisional, from the scale-test placeholder)

| Part | Provisional ramp | Notes |
| --- | --- | --- |
| Hair | `#1E1A26` `#332833` `#4D3A44` `#6B5058` | High puff toward the upper right; strong crown read |
| Skin | `#3E2630` `#5E3A36` `#85563F` `#A9744F` | |
| Jacket, main panel | `#5C4038` `#9A6A3E` `#C99A4E` `#EDCB7A` | Ochre |
| Jacket, second panel | `#21484A` `#326D60` `#5FA06D` `#B2CE78` | Garden green, on her right side and sleeve |
| Strap, bag | `#71394F` `#B65761` `#E67A70` `#F6B18E` | Coral; strap runs from her right shoulder down to the bag at her left hip |
| Trousers | `#202337` `#2C3352` `#3E4870` `#59658F` | Navy |
| Shoes | Coral ramp, dark two tones | Placeholder choice; see assumption 2 |

Concept 08 shows a figure with an orange-coral bag at the southeast mail counter, which matches her mailroom position.

## Sprite (16×24)

- Diagonal lean: the head offsets about 1 px forward of the hips in her walking direction. Feet are staggered.
- Bag sits low on the hip and breaks the jacket outline on one side, inside the 16×24 frame (cast rule). It's the first thing read at 1×. It is drawn with a flap line and a buckle so it reads as a bag rather than a coral marker.
- Strap is a clean 1–2 px diagonal with a 1 px shadow step. No noise.
- Bag on a fixed body side means **E and W must be drawn separately**, not mirrored.

### Patch states

Six patches, one added per **first clean baseline** of each route:

| # | Patch | Earned on | District |
| --- | --- | --- | --- |
| 1 | First Delivery | Morning Mail | Orientation |
| 2 | Clear Address | Courier Loop | Records |
| 3 | Archive Loop | Lost Folios | Records |
| 4 | Signed and Sent | Payroll Run | Systems |
| 5 | Signal Keeper | Glyph Dispatch | Systems |
| 6 | Night Courier | Lights-Out Delivery | Night Shift |

At 16×24 each patch is a **1–2 px cluster** on the jacket or bag flap, so patches must be palette-limited and placed in order. Portraits show them clearly. **Open:** patch designs and colors are not specified.

## Animation

| Set | Spec |
| --- | --- |
| Idle ×4 | Restrained loop that keeps the diagonal lean; she looks ready to go |
| Walk ×4 | 4–6 frames; **energetic stride**, longer step than the cast default, bag swings 1 px |
| Interact | Handing over or sorting mail |
| Reaction ×2 | Reusable. **Assumption:** (a) playful/pleased on a clean run, (b) confiding/serious for the scene where she admits keeping route copies |

## Portrait (48×48, chibi)

Chibi direction C, approved by the player 2026-10-02: oversized round head, tiny shoulders, flat shading, dot eyes. Pixel choices: [PORTRAIT_PERSONAS.md](../../art-direction/portraits/PORTRAIT_PERSONAS.md); atlas keys: `art-direction/portraits/portraits-atlas.json`. **When each face appears** is owned by the [Portrait cue map in `levels.md`](../../levels.md#portrait-cue-map); this table mirrors it, and `levels.md` wins if they differ. A line uses neutral unless a cue says otherwise, including every hint line.

| Atlas key | Reads as | Story cue |
| --- | --- | --- |
| `mira_neutral` | Ready to go | Offering any route or a repeat run |
| `mira_concerned` | Earnest (glances away) | Lost Folios, sharing the copy she kept (the erased-routes admission); Lights-Out Delivery, asking the player to keep the safe route open |
| `mira_pleased` | Proud | Each patch, earned on a route's first clean baseline; her final story scene |
| `mira_grin` | Wink and tongue-out grin (signature) | 05 "one useful hand" joke; Morning Mail introduction |

Patched variants `mira_patchK_<expression>` (K = 1–6) replace the base row once patch K is earned.

## Placement and states

| District | Where | When |
| --- | --- | --- |
| Orientation | Southeast mailroom, on the return path | Moves there after quest 02 completes; offers **Morning Mail** |
| Records | Beside the mail chute on the hub route | Appears after quest 07; **Courier Loop**. **Lost Folios** after 11 |
| Systems | Mail chute near the Negative Balance room; relay room | **Payroll Run** after 13; **Glyph Dispatch** after 16 |
| Night Shift | On the return route near the break room | **Lights-Out Delivery** after 18 |
| Executive | Arrives with the others for the finale (silhouette first, then sprite) | Level 20 |

She must be visible from each district's main route. Her conversation marker uses the coral bubble *shape*, so her coral costume doesn't stand in for the marker. Medals can decorate the mailroom board (a prop, not part of her sprite).

## Assumptions

1. ~~Panel sides, strap direction, and hair puff follow the scale-test placeholder.~~ **Decided 2026-10-02:** the green panel is on her right, following the text above rather than the retired placeholder. The strap runs from her right shoulder to her left hip. The puff is fixed to her own left.
2. ~~Shoes in coral are a placeholder choice.~~ **Decided 2026-10-02:** the shoes use the ink ramp, so coral appears only on the bag and strap. This does not restrict future patch colours.
3. The reaction and portrait sets above are derived from story beats; portrait story cues now live in the `levels.md` Portrait cue map.

## Open questions

1. Patch shapes and colors for all six.
2. Whether the coral strap needs a Night Shift lighting exception (a brighter local step) to stay visible on indigo floors.
