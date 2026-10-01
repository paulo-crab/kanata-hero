# Spec Delta

## Purpose

Defines the crisp DOM/CSS interface drawn over the pixel world: tokens, the keyboard teaching inset, dialogue, HUD and markers, so the learning UI stays readable and consistent.

## ADDED Requirements

### Requirement: UI is crisp DOM over pixel art
Text, keycaps, dialogue and panels SHALL be DOM/CSS elements over the canvas, not pixel art. Body text SHALL use a modern sans-serif, code and key outputs a monospaced face, and body text SHALL NOT use a pixel font. Panels SHALL be opaque or nearly opaque. Text SHALL be at least 16 CSS px by default.

#### Scenario: Dialogue over a detailed room
- **WHEN** a dialogue panel opens over the garden landmark
- **THEN** its text is drawn by the DOM at 16 CSS px or larger on an opaque panel and stays legible

### Requirement: Design tokens
The UI SHALL use a published token set: ink `#182B38`, paper `#F4F2EC`, terminal teal `#19AFA2`, conversation coral `#EC776D`, glitch violet `#9876D5`, discovery gold `#E6B750`, plus spacing, radius and type scales. Tokens MAY be adjusted after contrast checks, but their roles SHALL stay constant.

#### Scenario: New component
- **WHEN** a developer builds a new UI component
- **THEN** it takes its colours and spacing only from the token set

### Requirement: Keyboard teaching inset
The inset SHALL show the physical key position, the hold order, the emitted output and the in-game effect as four separate pieces of information. It SHALL use keycap components, not ASCII, and occupy the bottom-left of the view without covering the avatar or the current target.

#### Scenario: Teaching a move
- **WHEN** the game teaches "Move east"
- **THEN** the inset shows a held Caps keycap plus an L keycap, the output "Right arrow", and the effect "Step east"

### Requirement: Markers combine shape and colour
Interaction markers SHALL be distinguishable by shape alone: a speech bubble for conversation, a monitor for terminals, a diamond with a doorway for routes, a folded page for glitches. Colour alone SHALL NOT carry meaning.

#### Scenario: Colour-blind read
- **WHEN** the scene is viewed in greyscale
- **THEN** every marker type is still identifiable by its shape
