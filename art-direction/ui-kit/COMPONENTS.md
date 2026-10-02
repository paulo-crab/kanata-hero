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

Reference screen over a dimmed world (`--scrim`), panel inset 16 px, z 80. It is drawn from the layout manifest so it cannot drift from `kanata.kbd`. Renders: `screens/layout-base`, `layout-nav`, `layout-numbers-symbols`, `layout-practice` and `layout-base-microsoft` (each `-1366x768.png`); the practice tab also has a `-grey` render.

| Part | Rule |
| --- | --- |
| Header | Title, four layer tabs (`base`, `nav`, `numbers-symbols`, `practice`; the active tab is a filled paper pill with ink text), the **Keyboard** switch (MacBook, the default | Microsoft) and the close key (Esc, tap Caps) |
| How line | One muted line: switch tab with Left / Right (tap-hold Caps + H / L) or Tab / Shift + Tab; click and hold the drawn Caps or Space to preview that layer; Esc closes |
| Diagram | Five rows of 15u at `--key-unit` (64 px) with `--key-gap`. MacBook bottom row: fn, Ctrl, Opt, Cmd, Space (5u), Cmd, Opt, then Left, Up over Down (two half-height keys) and Right. Microsoft bottom row: Ctrl, Win, Alt, Space (6.25u), Alt, Win, Menu, Ctrl (its arrow cluster is not drawn) |
| Detail card | The focused key: its large keycap, **Tap**, **Tap-hold** with timing, behaviour on the shown tab, behaviour on `practice`, then one full-width line in the hint grammar ("To … you need to press **key**. Hint: key is **gesture**.") |
| Legend | One row, only the key kinds that appear on the tab |
| Keyboard switch | A segmented control (`.seg`); the selected segment is a paper pill with a check. It swaps the bottom row and the remap card; it never changes which tab is open |

Key kinds (the diagram is the only place that uses `.kh-lk`):

| Kind | Look | Not colour alone because |
| --- | --- | --- |
| Changes | paper face, teal top bar, the hold action or output printed under the legend (`Ctrl`, `Word →`, `!`) | the printed action |
| Layer key, held | teal face, sunk 3 px, the word `hold` | position and the word |
| Stays a letter | dim face, `= a` printed under the legend | the printed `= a` |
| Silent | `--key-silent-face`, dashed 2 px border, legend `XX`, the key's own name under it (`Bksp`) | dashed border and XX |
| Unchanged | dim face, plain legend | none needed |
| Focused | 2 px `--focus` ring, 3 px offset | a ring is a shape |

What each tab draws (all derived from `kanata.kbd`; Swedish remaps are out of scope and not drawn):

| Tab | Held layer key | Keys that change | Detail card |
| --- | --- | --- | --- |
| `base` | none | A S D F / J K L ; print their hold (Ctrl, Opt, Cmd, Shift / Shift, Cmd, Opt, Ctrl); Caps prints `Esc \| nav`; Space prints `tap Space \| hold numbers`; Tab prints `Homerow`; R prints `reload`; V prints `toggle`; right Cmd prints `+ nav` | F: tap, tap-hold 200 ms, opposite-hand Shift hint |
| `nav` | Caps, `hold` | 0 4 W B U D T G, H J K L (arrows), `[` Esc, M Bksp, X Ctrl+D, `,` Delete, N Return, Space Bksp; A S F stay letters | L: Right arrow |
| `numbers-symbols` | Space, `hold` | A to `'` print 1 to 0 and `-`; Q to `]` print `! @ # $ % ^ & * ( ) _ +`; N and M stay letters; Caps prints `nav`; Tab prints `Homerow` | Q: `!` |
| `practice` | none | Silent: digits 1 to 0, Backspace, Return, both Shift, Ctrl, Opt, Cmd (both sides), arrows. Still working: home-row holds, Caps, Space, Tab; V prints `toggle`. A note lists Esc, Forward Delete, Home, End, Page Up and Down as also silent and `- = \`` as still typing | Three cards: the focused silent key (Backspace, with its Caps + M replacement), the **toggle-out** sequence (Control + Alt + GUI + V, physical keys), and a locked **Emergency exit** card that says only "Shown after its runtime behaviour is verified" (the sequence is never drawn until the runtime check exists) |

Microsoft variant: the same screen with the switch on Microsoft. Win prints `→ Opt`, Alt prints `→ Cmd`, right Alt `→ R Cmd`, right Win `→ R Opt`; the detail card names the physical Alt key and explains that right Alt also holds nav. The remap strip under the diagram repeats the three pairs.

Behaviour (for the implementer; the reference page draws static states): Left / Right and Tab / Shift + Tab switch tabs, Escape closes and returns focus, click-and-hold on the drawn Caps or Space previews that layer for as long as the button is down, focus is trapped in the screen and Escape always leaves, focusing a key moves the detail card to it. The screen never scores anything and is reachable from every scene, including terminals and Mira's routes (which pause).

## Setup and calibration

First-run screen (and Settings, "Run setup again"), a full panel over the dimmed world, inset 16 px, z 80. Renders: `screens/setup-calibration` (MacBook, physical positions) and `screens/setup-characters` (Microsoft, resulting characters).

| Part | Rule |
| --- | --- |
| Header | Title, "About two minutes. Nothing here blocks the story.", **Skip setup** (Esc) and **Continue** (Return, focused). Skipping is always allowed |
| Keyboard choice | Two radio cards: MacBook (default) and Microsoft. Each shows its modifier strip; Microsoft draws `Win → Opt` and `Alt → Cmd` and says right Alt becomes Right Command and also holds nav. The chosen card has the focus outline and the word "Selected" with a check; the other says "Not selected" |
| Calibration | Five optional steps: Caps + H, Caps + N, Space + A, Space + Q, a home-row Shift hold. Each row: number, the gesture and its expected output, one line in the hint grammar, and a status chip. The current step has the focus outline |
| Status chips | **Not started** (hollow circle, solid border), **Observed output** (eye, teal border), **Skipped** (skip icon, dashed border). No other statuses, and no chip says "verified" or "detected" |
| Footnote | "The number row gives the same 1 and ! as Space + A and Space + Q, so observed output never proves which key you used." |
| Diagram | A compact keyboard (`--key-unit-sm`, 28 px) for the current step with a **Physical positions / Resulting characters** switch. Positions: key names, Space drawn held with "(held)", the target key ringed. Characters: what each key gives while Space is held (digits, symbols, plain letters), Space held, `!` ringed. A one-line caption names the view |
| Toggle-out card | The sequence as keycaps (Control + Alt + GUI + V), the instruction in the hint grammar, and the practice-layer chip ("unconfirmed" until the player says otherwise) |

Rules: calibration observes outputs only. It never asks the player to press a number-row key or claims to know which physical key was used. A step can finish as Observed or Skipped; neither blocks the story.

## Terminal and editor scene

Opened from a terminal, a form or a glitch. A panel over the world, which is dimmed with `--scrim-scene` (58%) and stays readable. Renders: `screens/terminal-scene` (working), `terminal-success`, `terminal-tab-practice`, and `glitch-duel`.

| Part | Rule |
| --- | --- |
| Reading column | 900 px wide, `--stage-margin` from the top-left, `--z-dialogue`. Code is `--font-mono` `--text-base` (18 px) on a 32 px line, never below 16 px. The panel is at most 400 px tall and ends above the keyboard inset (which starts below it; with two mini rows the inset starts at about stage y 370, the working scene's panel ends at about y 350), so the inset never covers the cursor line |
| Bar | File or scene name in mono, the place ("Records · Filing Drift"), and the escape route: "Leave the terminal  Esc  tap Caps" |
| Task strip | The hint grammar in two lines (action and key; then the gesture as a muted hint) and a target counter with a gold target glyph ("1 / 3") |
| Code well | `--panel-sunken`, 2 px `--border`, line numbers in the gutter |
| Cursor | A paper block (`--cursor-face`, glyph in `--cursor-text`) with a 2 px `--focus` outline; it never blinks under reduced motion |
| Selection | `--selection-bg` fill, `--selection-text`, and a 3 px `--focus` bar under it: shape plus fill |
| Targets | **Target line:** gold-tinted line, a gold diamond in the gutter and a `target line` tag at the right edge. **Target word:** a dashed 2 px gold outline |
| Success | The task strip becomes a 3 px gold frame with a check icon, "Done." and the next instruction; the target line gets a check and a `selected` tag. No full-screen effect and no motion |
| Side column | Right of the panel (x 932, 332 px): the input-feedback card ("Observed output") for the last gesture. The "Layout help ?" chip stays top-right |
| Inset | The standard keyboard teaching inset, with two mini rows (the key's row and the home row) when the key is off the home row |

Tab practice region: the form sits in a 3 px dashed `--accent-terminal` frame labelled "Tab practice region: Tab moves between these fields only", with a lock glyph. An announcement strip (eye icon, "Announced") states in words: "You are in the Tab practice region. Tab moves between three fields. Esc (tap Caps) leaves it at any time." It is also the text of an `aria-live` region. The bar always shows the Esc route. Tab never moves focus out of the region by itself, and the player is never trapped: Esc, and the "Leave" key, always work.

Glitch-repair duel (variant): a violet 2 px frame; the title carries the glitch marker and its text uses `--accent-glitch`. Turn-based and untimed: a **Turns** card (done = check in gold, current = play glyph in violet, to do = hollow) and "Untimed. Nothing is lost on a retry." The broken token has a wavy `--accent-glitch` underline (shape) as well as colour. **Retry this turn** and **Leave the duel** are real buttons under the code; Retry is focused and carries Return; reach it with Esc from the editor. A wrong result gets a plain sentence in the feedback card ("Not quite yet: one letter is still wrong. Retry restarts this turn."). No timer, no random ambush.

## Confidence-aware input feedback

The card that reports what the game knows about the last gesture. It appears in terminal scenes (side column), in calibration, and in the journal's per-gesture evidence. Render: `screens/input-feedback` (also `-grey`).

| State | Words | Icon | Border | When |
| --- | --- | --- | --- | --- |
| Observed output | "Observed output" | eye | solid 2 px `--accent-terminal` | the page saw a key event it can score |
| You confirmed | "You confirmed this gesture" | person with a check | double 6 px `--paper` | the output is ambiguous (Space + A gives the same 1 as the number row) or the gesture is external, and the player says they did it |
| Can't be observed | "Can't be observed here (OS-reserved)" | shield with a keyhole | dashed 2 px `--border` | macOS or the browser keeps the shortcut (Command + Space, the Tab hold) |

Every card has the same rows, in the order the game spec names them: **Gesture shown** (keycaps), **Output** (the logical output, in mono, or what the browser cannot see), **Effect** (gold). A muted line explains the confidence. A state is told by its icon, its border style and its words, so none depends on colour.

Practice-layer chip: "Practice layer: player-confirmed" (person with a check, solid paper border) or "Practice layer: unconfirmed" (hollow circle, dashed border). The game shows the layer **its own scene** is teaching and the layer **the player says** is active as two separate boxes; it never merges them.

Wording rules (game-design acceptance criteria 5 and 6):

| Say | Never say |
| --- | --- |
| "Observed output: Option + Right." "The game saw a 1." | "You are in the nav layer." The page cannot see held layers |
| "You confirmed tap-hold Space + A." (the player's word, labelled as such) | "You pressed Space + A" or "You used the number row." The same 1 comes from both |
| "Can't be observed here (OS-reserved)." then "Confirm it, or skip: no penalty" | "Failed" for a shortcut the OS keeps |
| "Practice layer: player-confirmed" or "unconfirmed" | "Practice mode detected / enabled / disabled." It cannot be |
| "Digits and their shifted symbols are silent on the number row in practice; minus and equals still type" | A claim that the practice layer blocks every number-row key |

## Accessibility summary

- Contrast AA is asserted by `check_contrast.py` for every pair the kit uses (text 4.5:1, UI glyphs and borders 3:1).
- Nothing is conveyed by colour alone: markers by shape, held keys by position and a tag, states by text and an icon.
- Minimum text size is 16 CSS px. The inset, dialogue and prompt are the same size at every supported zoom.
- A visible focus ring on every interactive element.
