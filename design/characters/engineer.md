# Engineer — player avatar

**Status:** gate 1 character. **Gate 1 APPROVED by the player 2026-10-02:** [`art-direction/gate1/`](../../art-direction/gate1/GATE1_ENGINEER_SPEC.md). Only four idle facings and one walk cycle until the player approves (STYLE_BIBLE §8). Shared rules: [README](README.md).

## Identity

| | |
| --- | --- |
| Role | A software engineer on a late shift, called in to repair a run of small office incidents. Coworkers remember their work. |
| Personality | Observant and competent; mostly defined by the player's choices. Their journal records evidence rather than speeches. |
| Pronouns | Not specified; the player defines the character. Sheets use they/them. |
| Where seen | Everywhere. Arrives by the Orientation elevator (southwest of the garden). |

Sources: `levels.md` cast table; `docs/game-design.md` "Characters and UI"; STYLE_BIBLE §5.

## Silhouette and costume

- **Customizable** hair, skin, and clothing color **within one consistent silhouette**. Customization never changes the body outline.
- Feels observant and capable, with an **asymmetric stance**. Hair and clothing must be identifiable even at 1×.
- Must not read as a generic cursor, a front-facing icon, or a big round head on a rectangular coat.
- **Badge:** the Engineer's own badge is a story object. Quest 02 restores it at the badge printer. A small brass badge on a lanyard at the chest is permitted (the bible allows a badge to mark a role), but the sprite must read without it.

### Default look (provisional, from the scale-test placeholder)

| Part | Provisional ramp | Notes |
| --- | --- | --- |
| Hair | `#2B1E26` `#4A2E2E` `#6E4434` `#93603F` | Short, with a swept top lifting to the right; visible crown |
| Skin | `#6E4433` `#9C6448` `#C98B62` `#E8B184` | |
| Jacket | `#1B4450` `#25707A` `#3A9C9C` `#7CCFC2` | Placeholder muted teal; allowed under STYLE_BIBLE §3 (all steps ≤ 60% HSL saturation). |
| Shirt collar | `#C7B7A0` `#E2D6C2` `#F4F2EC` | Small V at the neck |
| Trousers | `#202337` `#2C3352` `#3E4870` `#59658F` | Navy |
| Shoes | `#523D4C` `#85565A` `#BA785F` | Wood/terracotta ramp |
| Badge + lanyard | `#705056` `#AC7655` `#E1AC62` | 1×2 px badge, 1 px lanyard line |

The approved overhead concept (08) shows small, readable people with dark hair crowns, blue/teal-toned tops, and dark trousers. The default should sit comfortably in that crowd while staying clearly the protagonist.

### Customization slots

| Slot | What changes | Constraint |
| --- | --- | --- |
| Skin | Full 4-tone ramp swap | Inclusive set of ramps; each must keep face/hair separation at 1× |
| Hair | Ramp swap | **Assumption:** color only. The docs say "custom hair", but the silhouette must stay stable, so any hair *shape* variants are open (open question 2). |
| Clothing | Jacket and trouser ramps | Never violet. Avoid saturated teal, coral, or gold large enough to read as an interaction marker. |

## Sprite (16×24)

- Head ~9–10 px, torso ~7–8, legs/feet ~6–7. One-cell footprint, bottom-centre feet anchor, compact blue-purple contact shadow.
- Face: two eye pixels and a hair-shadow line across the forehead.
- Stance: weight slightly on one leg (the placeholder offsets the feet by about 1 px vertically). Arms hang just clear of the torso so the silhouette doesn't become a block.
- Selective outline per the README. Lit top-left edges use each part's own dark tone.

## Animation

| Set | Spec | Source |
| --- | --- | --- |
| Idle ×4 facings | Readable, restrained loop | Game spec, bible §5 |
| Turn | **Quick** directional turn; must feel immediate on each Caps+H/J/K/L press | Game spec |
| Walk ×4 facings | 4–6 frames, **purposeful**, with deliberate foot placement | Game spec, `levels.md` |
| Interact | At terminals, NPCs, artifacts | Standard set |
| Reaction: **concerned** | Readable pose | `levels.md` |
| Reaction: **satisfied** | Readable pose | `levels.md` |

Camera keeps the avatar slightly below centre and clear of the keyboard inset, which covers about the bottom third of the left side.

## Portrait (48×48)

Expression variants. **Assumption:** the docs ask for "a few" but name none for the Engineer, so this set follows from the two named reactions:

1. Neutral / observant (default)
2. Concerned
3. Satisfied

The portrait must use the same customization ramps as the world sprite.

## Gate 1 checklist

- [x] Four idle facings at 16×24, native (`art-direction/gate1/engineer_sprites.py`)
- [x] One walk cycle (east; one direction is enough for the gate; all four before atlas work)
- [x] Placed in the `scale-test/` Orientation scene at ×4 on 1366×768: door, terminal, one NPC, two-cell route, keyboard inset open (`gate1-scene-1366x768.png`, `gate1-walk-1366x768.gif`)
- [x] Judged against references 02, 04, 07, 08 for silhouette, expression, material separation, floor contact, interaction contrast
- [x] Player approval recorded before any other character starts (approved 2026-10-02)

## Assumptions

1. Customization is a color/ramp swap on one fixed sprite set (smallest reading of "within a consistent silhouette").
2. The default colors are the scale-test placeholders until the gate approves or replaces them.
3. The badge is drawn by default because the story centres on restoring it. It is removable without breaking the read.

## Open questions

1. ~~**Jacket teal vs. terminal teal.**~~ **Decided 2026-10-01:** keep the muted teal. Every teal-hued step stays at or below 60% HSL saturation and never uses `#19AFA2` (STYLE_BIBLE §3). The same limit applies to every jacket customization option.
2. **Hair shapes.** Is "custom hair" color only, or a small set of shapes that fit the fixed outline? **Interim (Director decision, 2026-10-01):** color only until decided; shape variants are not drawn.
3. **Customization UI.** Where and when does the player customize (setup screen, or at the badge printer)? Not specified.
