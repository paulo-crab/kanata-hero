# Spec Delta

## Purpose
Defines how the game turns browser keyboard events into game input honestly: what it can and cannot observe, how bindings work and how calibration proves the player's setup.

## ADDED Requirements

### Requirement: The interpreter is independent of level rules
Key events SHALL be translated by an input interpreter into logical outputs (for example `ArrowLeft`, `Enter`, text characters) with a confidence label before any scene or rule sees them. The interpreter SHALL have no knowledge of levels, and scenes SHALL not read raw key events.

#### Scenario: Same output, different physical routes
- **WHEN** the browser reports `ArrowLeft` from tap-hold Caps + H or from a Right Command route
- **THEN** the scene receives the same logical output `ArrowLeft` and the interpreter makes no claim about which physical key produced it

### Requirement: Observed output is never presented as detected gesture
The interface SHALL distinguish three confidence labels: observed output (the browser saw this key), player-confirmed gesture (the player said they did it), and not observable here (OS-reserved or held-state). The game SHALL NOT claim to detect the active Kanata layer, the practice toggle, physical number-row use or which physical key was pressed.

#### Scenario: Held Space demonstration
- **WHEN** a scene asks for a held-Space gesture
- **THEN** the game credits only the observed output and offers a player-confirm control for the hold itself

### Requirement: Decided key bindings
The game SHALL implement the bindings in `design/ui-key-bindings.md`: Return for interact, continue, confirm and retry by state; Esc for skip and back (no effect in the open world); the arrow keys for movement and choice; Q for the journal in the world only; Backtick for the Hint key; `?` for Layout help. Tab and Space SHALL never be bound outside a declared practice region. Backtick and `?` SHALL never be required as typed text in any scene.

#### Scenario: Journal key in a typing scene
- **WHEN** a label scene is active and the player presses Q
- **THEN** the letter Q is typed and the journal does not open

#### Scenario: Esc in the open world
- **WHEN** the player taps Esc while walking with no scene open
- **THEN** nothing happens

### Requirement: Browser behaviour is scoped and escapable
`preventDefault` SHALL apply only while a play surface has focus; the game SHALL not trap Tab; every screen SHALL have a keyboard-accessible exit; OS- or browser-reserved shortcuts SHALL not be required for progress.

#### Scenario: Tab outside a practice region
- **WHEN** the player presses Tab in the hub
- **THEN** browser focus moves normally and the game does not capture it

### Requirement: Calibration proves the setup without claiming detection
The calibration SHALL ask for Caps + H, Caps + N, Space + A, Space + Q and a home-row Shift hold (left F then `/` producing `?`), record per step one of not started, observed output, or skipped, show the expected output, accept a skip at any step, and store the keyboard type chosen in setup (MacBook default, Microsoft with Alt as Command and Windows as Option).

#### Scenario: Observed step
- **WHEN** the player does Caps + H and the browser reports ArrowLeft
- **THEN** the step shows "Observed output", and does not state which keys were used

#### Scenario: Skipped step
- **WHEN** the player moves past a step without the expected output
- **THEN** the step shows "Skipped" and later scenes still work, using the observed-output rule

### Requirement: Hint use is recorded
Standard difficulty is the only mode in this build and shows the action, the conventional key and the gesture hint with every instruction. Pressing the Hint key (Backtick) SHALL re-open the current instruction and the keyboard teaching inset, record that a hint was used for the current scene, and in a recall scene forfeit the third star for that scene after a card says so before the instruction is re-opened. Focused and Violento hint rules are out of scope.

#### Scenario: Hint in a guided scene
- **WHEN** the player presses Backtick in a guided scene
- **THEN** the instruction and inset re-open and no star is lost

#### Scenario: Hint in a recall scene
- **WHEN** the player presses Backtick in a recall scene
- **THEN** a card states that the third star is forfeited, and the instruction re-opens only after the player confirms with Return
