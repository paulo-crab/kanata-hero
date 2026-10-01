# Kanata Hero UI components

Component spec for the crisp DOM/CSS layer drawn over the pixel world. Every value comes from [`tokens.css`](tokens.css); a component never hard-codes a colour, spacing, radius, type size or z-index. The live example is [`reference.html`](reference.html), built by `build_reference.py`.

## Shared rules

- **Stage.** A 1280×720 CSS px stage holds the 320×180 world at the integer zoom `--world-zoom` (×4), centred and letterboxed in the window (1366×768 gives 43 px side bars and 24 px top and bottom bars). The world is an `<img>` or canvas with `image-rendering: pixelated`. Other zoom levels are whole numbers only (×3 for the optional 427×240 view); the UI layer stays at 1280×720 CSS px scale and is not zoomed with the world.
- **Panels.** `--panel-bg` (ink at 96%), a 2 px `--border`, `--radius-lg`. Nested wells use `--panel-raised` or `--panel-sunken`. Text on any of these is at least 4.5:1 (`check_contrast.py`).
- **Type.** Body and UI: `--font-body`, 16 px minimum (`--text-sm` for labels and captions, `--text-base` 18 px for body and dialogue). Key outputs, gestures and code: `--font-mono`. Titles: `--font-display`. No pixel font anywhere in the UI.
- **Labels.** `.kh-label`: `--text-sm`, bold, uppercase, `--tracking-label`, `--text-muted`.
- **Focus.** A 2 px `--focus` ring with 2–3 px offset on the element that has keyboard focus. Focus is never conveyed by colour change alone.
- **Colour roles.** Teal = terminals and held keys. Coral = people with a conversation. Violet = glitches only. Gold = completed, newly opened, and the effect line. Text on a coloured fill is `--text-on-light` (ink). Where a role colour is used as *text* on a panel, use the lighter `--accent-*` token (AA on every panel surface); the anchor hex is for fills, glyphs and outlines.
- **Hint grammar.** Any component that tells the player which keys to press uses the three parts, in order: the action in the game, the conventional key, then the Kanata gesture ("To walk to the east exit, you need to press Right arrow. Hint: Right arrow is tap-hold Caps + L."). Prompts abbreviate it as `Action — key — gesture`.
- **Layers (z).** world 0, world fx 10, marker 20, HUD 30, prompt 40, inset 50, dialogue 60, journal and Layout help 80 over a scrim, toast 90.

## Keycap

A raised cap that shows one key. Used in the inset, prompts, HUD chips, dialogue controls, the journal and (as the `lk` variant) the Layout help diagram.

| Part | Rule |
| --- | --- |
| Size | 1u = `--key-size-inset` (56 px) square; wide caps are 2u or more; `sm` is 32 px tall for prompts and HUD chips; Layout help 1u = `--key-unit` (64 px) with `--key-gap` (6 px) between keys |
| Face | `--key-face` (paper), legend `--key-text` (ink), `--font-mono` bold; 4 px lower edge `--key-edge`; `--radius-sm` |
| Legend | Letters uppercase (`L`), names as written (`Caps`, `Return`, `Esc`), outputs may be an arrow glyph. At least 16 px |

States:

| State | Look | Not colour alone because |
| --- | --- | --- |
| Tap (default) | paper face, raised | the tag below reads "Tap" in the inset |
| Held | teal face, sunk 3 px, edge shortened | tag "Hold" below it, and the physical sink |
| Dim (neighbour) | `--key-dim-face`, muted legend, regular weight | no tag; used only for context |
| Silent (practice) | `--key-silent-face`, dashed 2 px border, legend `XX` | the dashed border and the word XX |
| Focused | 2 px `--focus` ring, 3 px offset | a ring is a shape |
| Mapped (Layout help) | paper face, teal top bar, new action printed under the legend | the printed action |

## Keyboard teaching inset

Bottom-left panel, `--stage-margin` (16 px) from the stage edges, 572 px wide, about 280 px tall, border `--border-strong` (teal). It never covers the avatar or the current target. It shows four separate pieces of information, each in its own numbered cell:

1. **Key position.** A mini home row (Caps A S D F G H J K L ; ') at 32 px height. Caps drawn held, the target key at full strength, the others dim. Only the relevant keys are bright.
2. **Hold order.** The held keycap, a `+`, then the tapped keycap, each with a Hold or Tap tag. Release is stated in the header ("nav layer · tap-hold Caps · 200 ms"). Timings (200 / 220 / 250 ms) belong here and not in dialogue.
3. **Output.** The logical output the game observes, as a keycap glyph plus its name in mono ("Right arrow").
4. **Effect.** The in-game result in gold with an icon ("Step east").

Header: the action ("Move east", `--text-xl`) and the active layer name. Keycaps, not ASCII. The camera keeps the avatar and the current target outside the inset rectangle (x 16–588, y from about 412 to 704 on the stage). Check scene positions with the reference page: avatar x 832–896, y 300–396; Ivo x 480–544, y 156–252; Records door x 1200–1240, y 288–441.

## Dialogue panel

Lower-right of the stage, 672×224 px, `--stage-margin` from the edges, beside the inset (the two never overlap: inset ends at x 588, dialogue starts at x 592).

| Part | Rule |
| --- | --- |
| Portrait slot | 48×48 native portrait shown at world zoom: 192×192 CSS px at ×4 (`--portrait-size`). Pixelated, 2 px `--accent-conversation` frame, 16 px panel padding. The reference shows a placeholder slot; portraits arrive in task group 9 |
| Speaker | Name in `--font-display` `--text-xl`, role in `--text-sm` muted |
| Text | `--text-base`, one to three lines, action first. The hint line follows in muted text with the key and gesture in bold |
| Controls | Continue (Return, tap-hold Caps + N) and Skip (Esc, tap Caps) as small keycaps, bottom of the text column |
| Placement | Must not cover the object the NPC is discussing when a task begins. The panel top (stage y 480) is below the avatar and the Records door in the reference scene |

## HUD

- **Objective strip**, top-left: quest title (`--text-lg` bold), progress (`2 / 4`, mono), a divider and the seal count with a seal icon in gold. 48 px tall, `--radius-md`.
- **Shortcut chips**, top-right: "Journal Tab" and "Layout help ?" with small keycaps.
- No permanent side panel. The world is never shrunk to make room.

## Interaction prompt

A small panel next to a person or device while the player is in range, with a 20 px tail pointing at it. Border `--accent-terminal` for devices (`--accent-conversation` for people). Line one: the action with a play icon (`--text-lg` bold). Line two: a small keycap with the conventional key and the Kanata gesture in mono (`Return  tap-hold Caps + N`). It hides while a dialogue is open. The reference shows both at once for review.

## Markers

Four SVG symbols in a 64×64 box (`--marker-size`). Shape carries the meaning; colour is the second signal. Each has a 4.5 px paper halo and a 2.5 px ink line so it reads on light and dark floors.

| Marker | Shape | Fill | Means | Where |
| --- | --- | --- | --- | --- |
| Conversation | Speech bubble with three dots and a tail | coral | A coworker has a conversation | Above the person |
| Terminal | Monitor with a prompt on its screen, stand and base | teal | A device you can use | On or above the device |
| Route | Diamond with an arched doorway | gold | A route that is open or newly open | At the door or shortcut |
| Glitch | Page with a folded corner and a broken text line | violet | A repair duel | Above the glitch |

Greyscale check: open `reference.html#grey`, or the `reference-greyscale-1366x768.png` render. Each marker stays identifiable by outline alone: bubble (rounded with tail), monitor (stand and base), diamond (pointed on four sides), page (folded top-right corner). The greyscale toggle is a CSS `filter` applied through a `:target` rule; the page has no script. World pixel art keeps its own palette and never uses the four marker hexes.

## Quest journal

On-demand screen over a dimmed world (`--scrim`), panel inset 24 px from the stage edges. Header: title, district, seal count (`Clearance seals 0 / 5`) and the close key (Esc, tap Caps).

- **Left list**, three groups, each with its own icon and heading colour: Main work (seal icon), Coworker requests (speech bubble, coral), Optional speed, Mira (stopwatch, teal).
- **Row**: title, state, one line of detail. State is text plus an icon: Active (play), Locked (lock), Done (check, gold). The selected row has a focus outline.
- **Detail card**: the selected quest, its steps with a dot per step (done, current, to do), the keys for the current step as keycaps with the output and the gesture, and a button-like row to open Layout help (`?`).
- Mira's quests show their skill prerequisites ("Needs: …").

## Layout help

Reference screen, over a dimmed world, panel inset 24 px. It is drawn from the layout manifest so it cannot drift from `kanata.kbd`.

- **Header**: title, four layer tabs (`base`, `nav`, `numbers-symbols`, `practice`; the active one is a filled pill), close key.
- **Diagram**: a US keyboard (rows of 15u) drawn from keycaps of `--key-unit`. Keys that change on the shown tab are paper with a teal top bar and the new action printed under the legend (`Word →`, `Page ↓`, arrows at 20 px). Unchanged keys are dim. Silent keys on `practice` are dashed and read `XX`. The layer key itself (Caps on `nav`, Space on `numbers-symbols`) is drawn held in teal with the word "hold".
- **Detail card**: for the focused key: Tap, Tap-hold with its timing, behaviour on the shown tab, behaviour on `practice`. Wording follows the hint grammar. The focused key has the focus ring.
- **Behaviour**: Left / Right (tap-hold Caps + H / L) and Tab / Shift + Tab switch tabs; Escape closes; clicking and holding Caps or Space previews that layer while the button is down; focus is trapped in the screen. These behaviours are for the implementer; the reference page draws the static state only.

## Accessibility summary

- Contrast AA is asserted by `check_contrast.py` for every pair the kit uses (text 4.5:1, UI glyphs and borders 3:1).
- Nothing is conveyed by colour alone: markers by shape, held keys by position and a tag, states by text and an icon.
- Minimum text size is 16 CSS px. The inset, dialogue and prompt are the same size at every supported zoom.
- A visible focus ring on every interactive element.
