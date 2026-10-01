# Spec Delta

## Purpose

Defines the contract for every person sprite (player avatar, named cast, background workers) so characters animate, compose and read consistently in the game.

## ADDED Requirements

### Requirement: Person frame and anchor
Every person sprite frame SHALL be exactly 16×24 logical px on a one-cell footprint. The anchor `feet_bc` SHALL be the pixel edge between columns 7 and 8 under row 23. The planted foot SHALL rest on row 23 in every frame. Every visible pixel, including held props and bags, SHALL stay inside the frame.

#### Scenario: Placing a sprite
- **WHEN** a renderer places a sprite at a cell position
- **THEN** it aligns the frame so the anchor edge lands on the foot position, and no part of the sprite extends beyond the 16×24 frame

### Requirement: Facings and animation timing
Each recurring character SHALL provide S, N, E and W facings. E and W SHALL be drawn separately whenever the character has asymmetric detail. Idle SHALL be 2 frames × 500 ms, with frame 1 lowering the head and torso 1 px while the feet stay fixed. Walk SHALL be 4 frames × 133 ms, with contacts on frames 0 and 2 lowered 1 px. One cycle SHALL cover 2 cells (8 px per frame). Walk strides SHALL NOT touch columns 0 or 15.

#### Scenario: Walking one cycle east
- **WHEN** a character walks one full cycle east
- **THEN** it plays 4 frames at 133 ms, moves 32 px in 8 px steps, and its feet never reach the frame's edge columns

### Requirement: Readable silhouettes and props
Each recurring character SHALL be identifiable at native 1× by silhouette, hair, clothing and signature prop, not by colour alone. Hair SHALL NOT read as a helmet. Signature props SHALL read as the object they depict. Hair SHALL NOT touch skin of equal luminance without a darker separating pixel.

#### Scenario: Small prop review
- **WHEN** a signature prop such as a tablet or bag is reviewed at ×4 in the review room
- **THEN** it shows a frame or edge, a lit face and an identifying detail, and reviewers can name the object

### Requirement: Customization by ramp swap
The player avatar's customization SHALL change only colour ramps (skin, hair colour, jacket, trousers) on one fixed set of frames. The silhouette, anchor, timing and key layout SHALL NOT change. Customization options SHALL obey the marker-colour rules.

#### Scenario: Changing jacket colour
- **WHEN** the player selects another jacket ramp
- **THEN** only jacket pixels change colour and every frame keeps the same opaque mask

### Requirement: Portraits
Each recurring character SHALL have 48×48 logical px head-and-shoulders portraits with at least three expressions. They SHALL use the same palette and ramps as the world sprite and be shown at the world's zoom factor.

#### Scenario: Dialogue opens
- **WHEN** a dialogue line from a recurring character is shown
- **THEN** a 48×48 portrait of that character in the line's expression is available at the same zoom as the world

### Requirement: Automated sprite checks
Every sprite module SHALL pass the person-sprite checker before review. The checker covers frame size, the row-23 pixel, anchor mass balance within 20%, marker and violet colours, teal saturation, head keys, darkest-step use, hair against skin (when flagged), glint limits (when declared) and stride edges.

#### Scenario: Check fails
- **WHEN** the checker reports any failure for a module
- **THEN** the sprite is not approved until the failure is fixed or the rule is consciously changed and recorded
