# Spec Delta

## Purpose

Defines what developer agents receive from the art pipeline, and how they find, load and regenerate every asset without guessing.

## ADDED Requirements

### Requirement: Asset index
A handoff document SHALL list every approved asset with its source module, its generated files, its spec and its approval date. It SHALL be the single entry point for developers.

#### Scenario: Developer looks for Ivo's walk
- **WHEN** a developer needs Ivo's walk-east frames
- **THEN** the index points to `ivo-atlas.png`, its row in `ivo-atlas.json`, and `IVO_SPEC.md`

### Requirement: Atlas and metadata format
Every sprite atlas SHALL be a PNG with transparent background and frames on a fixed grid. Each atlas SHALL have a JSON sidecar declaring frame size, anchor, footprint, and per-animation row, frame count, frame duration and contact frames. Environment atlases SHALL also declare collision and draw layers.

#### Scenario: Loading an animation
- **WHEN** the game loads `engineer_walk_e`
- **THEN** the JSON gives its row, 4 frames, 133 ms per frame, contact frames 0 and 2, and the `feet_bc` anchor at (8, 24)

### Requirement: Generated outputs and reproducible builds
PNG, GIF and JSON art files SHALL be generated from source modules by documented commands and SHALL NOT be hand-edited. The handoff SHALL document the environment the builds need.

#### Scenario: Rebuilding after a palette tweak
- **WHEN** an approved ramp hex changes in a source module
- **THEN** running the documented build command regenerates every affected PNG and JSON, and the checker still passes
