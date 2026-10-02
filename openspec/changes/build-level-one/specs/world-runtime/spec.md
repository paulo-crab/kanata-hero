# Spec Delta

## Purpose
Defines how the game loads the validated level data and art, draws the world, moves the avatar and runs scenes, so level data alone decides what happens in a room.

## ADDED Requirements

### Requirement: The game loads level data and art as static files
The game SHALL run from static files with no backend, load the Orientation district, level 01, world index, gesture inventory and layout manifest as JSON, and load the kit, cast, glitch, Pace and portrait atlases as PNG plus JSON, all without a build step for the data. A file that fails to load or validate SHALL stop the game with a visible, specific error naming the file.

#### Scenario: Cold start
- **WHEN** the page is opened from a static file server
- **THEN** all required files load and the setup screen appears without console errors

#### Scenario: Missing file
- **WHEN** an atlas JSON is missing or malformed
- **THEN** the game shows an error naming that file and does not start the world

### Requirement: Fixed logical view with integer zoom
The world SHALL render in a 320x180 logical view scaled by a whole-number zoom chosen as the largest integer that fits the window (x4 on 1366x768, x6 on 1920x1080), letterboxed, with nearest-neighbour sampling and no fractional scaling. DOM UI SHALL sit on a 1280x720 CSS-pixel stage independent of the world zoom.

#### Scenario: Laptop size
- **WHEN** the window is 1366x768
- **THEN** the world is drawn at x4 inside a letterboxed 1280x720 stage and no world pixel is blurred

#### Scenario: Window resize
- **WHEN** the window is resized across the x4 to x6 threshold
- **THEN** the zoom changes to the new whole number without reloading and without losing game state

### Requirement: Layered rendering in the style-bible order
The renderer SHALL draw floor, rear wall, floor marking, rear prop, shadow, actor, front prop, light, then DOM UI, sorting entries marked y-sorted by their anchor's y, drawing contact shadows under people and glitches at their anchors, and applying atlas states (doors, lamps, landmarks) exactly as the atlas JSON defines them.

#### Scenario: Actor behind and in front of a prop
- **WHEN** the avatar walks north then south of a y-sorted desk
- **THEN** the avatar is drawn behind the desk when north of its anchor and in front when south of it

#### Scenario: State change
- **WHEN** a rule sets a placement's state (for example the turnstile from closed to open)
- **THEN** the next frame draws the new state's entries and collision, and nothing else moves

### Requirement: Camera follows the avatar inside the bounds
The camera SHALL keep the avatar's feet near the logical screen position (160, 100) and clamp to the district's camera bounds.

#### Scenario: Near a map edge
- **WHEN** the avatar is within half a view of a map edge
- **THEN** the camera stops at the bounds and the avatar moves toward the screen edge

### Requirement: Per-cell collision from level data
Movement SHALL be blocked by the collision grid of the district map (and gates in their current state), authored per 16x16 cell and independent of art, and SHALL be deterministic: the same input sequence from the same state gives the same positions.

#### Scenario: Wall and prop
- **WHEN** the avatar walks into a blocked cell
- **THEN** it does not enter, and the walk animation stops without a frame of overlap

#### Scenario: Gate opens
- **WHEN** a rule opens a gate
- **THEN** the cells it covered become walkable on the same frame its art changes

### Requirement: Avatar and character animation follow the atlas contract
Actors SHALL animate from atlas JSON (idle 2 frames, walk 4 frames at 133 ms, 8 px per frame, interact and reaction sets, play modes as declared), anchored at `feet_bc`, with reduced motion holding idle frame 0.

#### Scenario: Walking a cell
- **WHEN** a movement key is held for one cell
- **THEN** the avatar plays the directional walk for two walk frames per 8 px and ends aligned to the cell grid

### Requirement: A small scene state machine drives play
The game SHALL be a state machine with at least the scenes setup, calibration, arrival, hub, dialogue, walk scene, form or label scene, editor (glitch) scene, Layout help, journal and error. Scene transitions SHALL be explicit; a scene SHALL own which keys are active; returning from a scene SHALL restore the previous scene's state and focus.

#### Scenario: Open and close Layout help
- **WHEN** the player opens Layout help from the hub and closes it
- **THEN** the hub resumes with the avatar, camera and objective unchanged

### Requirement: Level rules run from level data only
Level behaviour (steps, dialogue triggers, scene success, state changes, rewards, glitches) SHALL be executed from the level JSON by a rule runtime that is separate from rendering and from input interpretation, and SHALL support the 0.2 schema features used by level 01 (trigger atoms, `modal`, NPC states, set-state and unlock operations).

#### Scenario: Level 01 completes
- **WHEN** the recall scene succeeds
- **THEN** the declared state changes apply (turnstile opens, Ivo's pose becomes the nod, the mailroom gate unlocks) and the level is marked done

### Requirement: Progress persists locally
Progress (level done, steps, per-scene evidence, settings including keyboard type, hint usage, best results) SHALL be stored in `localStorage` under keys derived from `world.json`, survive reload, be resettable with confirmation, and the game SHALL play when storage is unavailable.

#### Scenario: Reload mid-level
- **WHEN** the page is reloaded during level 01
- **THEN** the game offers to continue at the last completed step and restores world state

#### Scenario: Storage blocked
- **WHEN** `localStorage` throws
- **THEN** the game continues in memory and shows that progress will not be saved
