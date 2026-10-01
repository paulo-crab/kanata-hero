# Spec Delta

## Purpose

Defines the reusable tiles, props, landmarks and state art for each district, with the metadata developers need for layout, collision and layering.

## ADDED Requirements

### Requirement: District tile and prop atlas
Each district SHALL ship a 16 px tile and prop atlas covering at least floor, floor edges and inlays, walls with top and side planes, glass partitions, doors, desks, seating, shelving, planters and terminals. Every entry SHALL declare its footprint in cells, its collision mask, its draw layer and its anchor.

#### Scenario: Placing a desk
- **WHEN** a level designer places the two-cell desk from the atlas
- **THEN** its metadata gives a 2×1 cell footprint, which cells block movement, which layer it draws on, and where its contact shadow sits

### Requirement: Doors read as doors and have states
Every door SHALL show a frame, its leaves and what lies beyond or a lit threshold. Doors that open SHALL provide state frames (for example a sliding glass door: closed, half open, open). Doorways SHALL be brighter than adjacent dead ends.

#### Scenario: Approaching the Records door
- **WHEN** the player approaches an unlocked door
- **THEN** the renderer can play its opening frames, and the doorway is visibly brighter than the walls beside it

### Requirement: One landmark per district with quest states
Each district SHALL have exactly one richer landmark at the same pixel size as the rest of the world, delivered as layered parts with at least a before and an after quest state. Ordinary rooms SHALL use the shared kit with broad floor groups and no dense texture on every tile.

#### Scenario: Quest completes
- **WHEN** a district's quest that changes the landmark completes
- **THEN** the landmark switches to its after state using the same parts, and at least two visible things change

### Requirement: Routes stay clear and readable
Main routes SHALL be at least two cells wide, free of props, and findable without labels. In-world signage such as the RECORDS mat MAY add wayfinding. The keyboard inset area (bottom-left third of the view) SHALL NOT be the only place a required element appears.

#### Scenario: Route check
- **WHEN** a room is reviewed at ×4 with the keyboard inset open
- **THEN** the two-cell route to the next exit is visible and unobstructed, and no lamp, door or NPC needed for the task is hidden under the inset
