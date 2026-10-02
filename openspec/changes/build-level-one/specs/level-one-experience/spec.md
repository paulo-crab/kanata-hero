# Spec Delta

## Purpose
Defines what a player experiences from first load to the end of level 01, so the build can be accepted by playing it.

## ADDED Requirements

### Requirement: Setup and calibration come first
On first load the game SHALL show the setup screen (MacBook or Microsoft keyboard diagram, with MacBook the default), then the calibration of Caps + H, Caps + N, Space + A, Space + Q and the home-row Shift hold, and the practice toggle-out instructions; the player SHALL be able to skip any step and the whole sequence with Esc; the choice and results SHALL be stored and never shown again unless the player reopens setup from settings.

#### Scenario: First visit
- **WHEN** a new player opens the game
- **THEN** setup appears before any world, and completing or skipping it leads to the arrival

#### Scenario: Returning player
- **WHEN** setup was completed earlier
- **THEN** the game goes to the hub (or the continue prompt) directly

### Requirement: Arrival from the north-wall elevator
A new game SHALL start with the avatar arriving at the `arrival` spawn of the Orientation map: the elevator plays closed, half, open, the avatar steps onto the lift mat, and Ivo's greeting starts level 01.

#### Scenario: New game
- **WHEN** the arrival begins
- **THEN** the elevator doors play their three states in 120 ms steps, the avatar appears on the mat facing south, and `o01.d.welcome` shows

### Requirement: The hub is walkable and readable
The Orientation hub (28x18 cells) SHALL be walkable with the arrows, with collision from the map data, the camera bounds from the district data, and every NPC, interactable, exit and path readable at 1366x768 and 1920x1080 with the keyboard inset open, without relying on labels.

#### Scenario: Walk the lobby
- **WHEN** the player walks the lobby at 1366x768 with the inset open
- **THEN** the avatar, Ivo, the desks and the elevator stay visible outside the inset rectangle, except where the level sheet documents decorative-only floor

### Requirement: Level 01 plays through its steps in order
Level 01 SHALL run its steps from the level data: arrive, close the popup with tap Caps, learn the journal, hint and Layout help keys from Ivo's instruction lines, walk the counter-clockwise lap with the four arrows, visit the four desks in order, type the west desk label, then the unprompted recall walk to Ivo and back, with Ivo's hint lines shown as action, key and gesture, and an optional folded-form glitch repair afterwards.

#### Scenario: Popup
- **WHEN** the welcome popup is open and the player taps Caps
- **THEN** the popup closes, Ivo says the success line and the lap step starts

#### Scenario: Wrong direction
- **WHEN** the player walks a direction other than the one asked
- **THEN** the game does not block them, Ivo's instruction stays available, the lap continues from where they are, and the move counts as an incorrect action for the clean-run measure only

#### Scenario: Desk label
- **WHEN** the player types W, E, S, T at the west desk
- **THEN** the label scene succeeds on the resulting text and a wrong character gets immediate correction without losing progress

#### Scenario: Unprompted recall
- **WHEN** Ivo has gone to the north desk and the markers are off
- **THEN** the player can reach him and return using only the arrows, and the scene records recall evidence

### Requirement: Level 01 changes the world
Completing level 01 SHALL open the reception turnstile, change Ivo's pose from the wave to the nod, flip the garden markers from teal to gold, and unlock the mailroom gate, as the level data declares, with at least two of these visible on screen.

#### Scenario: After the recall walk
- **WHEN** the recall scene succeeds
- **THEN** the turnstile plays its open state, Ivo shows the nod, and the journal marks level 01 done

### Requirement: Optional glitch repair is harmless and untimed
The folded-form glitch SHALL be optional, roam in the south lobby, open a short untimed repair scene with instant retry, play the repaired snap frame on success, and become the ordinary prop; failing or skipping SHALL never block the level.

#### Scenario: Repair
- **WHEN** the player repairs the glitch
- **THEN** the snap frame plays once and the ordinary flat sheet replaces it

### Requirement: Evidence and stars for level 01
The game SHALL record, per gesture and phase (guided, variation, recall), the observed-output evidence, hint use and result of each scene, and award stars as in the game design (one for completing, two for a clean run, three for a clean recall without hints), never timing anything.

#### Scenario: Clean recall without a hint
- **WHEN** the recall scene is clean and no Hint key was pressed in it
- **THEN** the level shows three stars

### Requirement: Level 01 can be left and resumed
The player SHALL be able to open the journal (Q), Layout help (?), and Controls at any time in the hub, close them with Esc, and reload the page without losing progress.

#### Scenario: Layout help mid-level
- **WHEN** the player opens Layout help during the lap and closes it
- **THEN** the lap resumes at the same cell with the same objective
