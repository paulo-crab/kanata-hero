# Spec Delta

## Purpose

Defines the visual contract that every Kanata Hero asset must satisfy, so art from any artist or agent reads as one game on one pixel grid.

## ADDED Requirements

### Requirement: Single logical pixel grid and integer display
All world art SHALL be authored on one logical grid of 16×16 px tiles, for a 320×180 logical view. The view SHALL be displayed only at whole-number nearest-neighbour zoom: ×4 on 1366×768 (1280×720, letterboxed) and ×6 on 1920×1080. An optional wider view is 427×240 at ×3.

#### Scenario: Laptop display
- **WHEN** the game renders on a 1366×768 screen
- **THEN** the 320×180 view is shown at exactly ×4 with nearest-neighbour sampling and letterboxing, and no pixel is fractional or blurred

#### Scenario: Mixed pixel sizes rejected
- **WHEN** an asset is drawn at a different logical pixel size or scaled fractionally
- **THEN** it fails review and is not accepted into an atlas

### Requirement: Hard-pixel rendering
Assets SHALL use only hard square pixels of listed palette colours (the base palette, the district palettes and, for world art, the rich-finish v2 ramps). Assets SHALL NOT contain gradients, antialiasing, blending, soft brushes, bloom haze, scanlines, CRT effects or dithered faces or outlines. Light SHALL come from the upper left in screen space and be shaded in stepped solid clusters. Glows SHALL be one or two hard-edged steps.

#### Scenario: Off-palette pixel
- **WHEN** an audit of a rendered asset or room finds a colour that is not in the approved palette, character ramps or UI tokens
- **THEN** the asset fails review

### Requirement: Palette and district palettes
The Orientation production palette (32 colours in 8 ramps of 4, STYLE_BIBLE §3) SHALL be the base palette. For world art, the ink, wood, glass, garden-green, brass and coral ramps SHALL be the rich-finish v2 ramps defined in `art-direction/rich-finish/RICH_FINISH_SPEC.md`, and stone SHALL keep its base values. Each district (Records, Systems, Night Shift, Executive) SHALL have a published hex sheet before any of its assets are drawn. Character skin and hair ramps SHALL be per character and not reused across the cast.

#### Scenario: District asset without a palette
- **WHEN** an asset is requested for a district whose hex sheet is not published
- **THEN** the hex sheet is produced and approved first

### Requirement: Interaction-marker colours stay readable
Teal SHALL mark terminals, coral conversations, violet glitches and gold opened routes, and every marker SHALL also carry a distinct shape. People SHALL NOT wear violet. Teal-hued clothing steps (hue 160°–200°) SHALL stay at or below 60% HSL saturation. No person or prop SHALL use a UI marker hex. Gold and other marker-adjacent highlights SHALL be limited to small glints.

#### Scenario: Clothing ramp check
- **WHEN** a clothing ramp contains a step with hue between 160° and 200°
- **THEN** that step's HSL saturation is at or below 60%, or the ramp is rejected

### Requirement: Contour and darkest-step discipline
The default outer outline SHALL be `#0E1020` (the rich-finish ink; it was `#202337`). Lit top and left edges SHALL swap short runs to the part's own dark tone. The darkest step of a ramp SHALL appear only on contours and occlusion edges, never as interior fill.

#### Scenario: Darkest step as fill
- **WHEN** a ramp's darkest step is surrounded on all four sides by the same part's fill
- **THEN** the automated check reports a failure

### Requirement: Layer draw order
The world SHALL draw in this order: floor, rear walls and floor-height markings, rear props, contact shadows, actors, front props and occluders, local light accents, then the DOM UI. There SHALL be no parallax or horizon layer.

#### Scenario: Actor passes behind a front prop
- **WHEN** an actor walks behind a front occluder such as a counter
- **THEN** the occluder draws over the actor and the actor's foot anchor still determines its depth
