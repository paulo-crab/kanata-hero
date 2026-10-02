# Spec Delta

## Purpose
Defines the DOM and CSS layer over the world: which components exist, that they follow the UI kit, and the accessibility and display rules they must meet.

## ADDED Requirements

### Requirement: The UI follows the UI kit
Every UI component SHALL take colours, spacing, radii, type sizes and layers from `art-direction/ui-kit/tokens.css` and follow `art-direction/ui-kit/COMPONENTS.md`: keycap, keyboard teaching inset, dialogue panel with portrait, HUD, interaction prompt, markers, journal, Layout help, setup and calibration, terminal and editor scene, input feedback, Controls, first-use inset, settings and toast. No pixel font; body text at least 16 CSS px.

#### Scenario: Token use
- **WHEN** the shipped stylesheet is inspected
- **THEN** component colours and sizes resolve to kit tokens rather than hard-coded values

### Requirement: Instructions use the hint grammar
Every in-game instruction that names keys SHALL give the action, then the conventional key, then the Kanata gesture as a hint, using the wording in the level data.

#### Scenario: Ivo's lap instruction
- **WHEN** Ivo asks for the west walk
- **THEN** the panel shows the action "To walk to the west desk, you need to press Left Arrow." and the hint "Hint: Left Arrow is tap-hold Caps (nav) + H."

### Requirement: The keyboard inset teaches position, hold order, output and effect
On guided and variation scenes the inset SHALL show key position, hold order, output and effect as four separate cells, SHALL never cover the avatar or the current target, and SHALL be absent on recall scenes.

#### Scenario: Recall scene
- **WHEN** the unprompted recall walk starts
- **THEN** the inset and floor markers are hidden

### Requirement: Layout help is rendered from the layout manifest
Layout help SHALL draw all four tabs (`base`, `nav`, `numbers-symbols`, `practice`) and the MacBook and Microsoft variants from `design/layout/layout-manifest.json`, with the key detail card, silent keys marked XX, the toggle-out sequence and the emergency exit shown as unverified, and SHALL work without a pointer: Left and Right (tap-hold Caps + H and L) and Tab and Shift + Tab change tabs, Esc closes and returns focus.

#### Scenario: Manifest drives the screen
- **WHEN** a key's manifest entry changes
- **THEN** the drawn legend changes with it without editing UI code

### Requirement: Accessibility and display
The UI SHALL provide a visible focus ring on every interactive element, nothing conveyed by colour alone (markers by shape, states by text and icon), screen-reader-readable objectives and instruction text, AA contrast, reduced motion honoured from the OS and a setting, larger text and high contrast settings, and SHALL remain legible at 1366x768 and 1920x1080 including with larger text.

#### Scenario: Reduced motion
- **WHEN** the OS requests reduced motion
- **THEN** idle loops hold frame 0 and Ivo's tablet flash holds its dim frame

#### Scenario: Screen reader
- **WHEN** the objective changes
- **THEN** the new objective is announced through a live region

### Requirement: Sound is out of scope and off
The build SHALL contain no audio and SHALL NOT request audio permissions.

#### Scenario: Fresh load
- **WHEN** the game loads
- **THEN** no audio element or context is created
