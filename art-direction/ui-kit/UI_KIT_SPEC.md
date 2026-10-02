# UI kit: specification (tasks 10.1 and 10.2, extended with the vertical-slice screens)

**Status:** Approved by the director 2026-10-02. Extended 2026-10-02 by the UI team (branch `feat/ui-layout-help-and-screens`): Layout help on all four tabs, setup and calibration, terminal and editor scenes, input feedback (P0), then the artifact frame, elevator map, seals and toast, Mira's results, and settings (P1). Key bindings decided 2026-10-02 (branch `feat/ui-key-bindings`, decision 10 and `design/ui-key-bindings.md`). Candidate until the producer merges it; the checks below pass.

**Sources:** `openspec/changes/complete-art-production/specs/ui-presentation/spec.md`, `docs/game-design.md` ("Color, materials, and light", "Characters and UI", "Hint grammar", "Layout help", the gesture inventory A to D, "Difficulty, scoring, and awards", "Browser behavior and accessibility", "Implementation slices"), `levels.md` hint lines and the seal list, `art-direction/cast/MIRA_PATCHES_SPEC.md` (patch names and colours), `~/.config/kanata/kanata.kbd` (read only, for key names and the layers; it was cross-checked and nothing was copied from it). `art-direction/ui/README_v2.md` was ignored (rejected).

## Deliverables

| File | What it is |
| --- | --- |
| `tokens.css` | CSS custom properties: anchor colours, panel surfaces, text, keycap tokens, spacing, radius, type, z-layers, the ×4 world zoom and the 1280×720 stage; plus the scene scrim, editor selection and cursor, the compact key unit and Mira's patch colours |
| `check_contrast.py` | Parses `tokens.css` and asserts WCAG AA for every pair it lists (text 4.5:1, UI 3:1), the type minimum, no pixel font, the stage maths and the published anchors; then lints the generated page (see "Page lint") |
| `COMPONENTS.md` | Component spec: keycap, keyboard inset, dialogue, HUD, prompt, markers, journal, Layout help, setup and calibration, terminal and editor scene (Tab region and glitch duel), input feedback, artifact frame, elevator map, seal award, toast, Mira's results, settings |
| `reference.html` | Static reference page (only `tokens.css`, `world-native.png` and inline CSS/SVG; no script). Every screen is also a one-screen target, `#s-<id>` (colour) and `#s-<id>-grey` (greyscale) |
| `build_reference.py` | Generates `reference.html`: the main stage, markers, keycap states and journal; stitches in the two screen modules |
| `kit_screens.py` | P0 screens: Layout help (four tabs and the Microsoft variant), setup and calibration (two views), terminal scene (working, success, Tab region), glitch duel, input feedback |
| `bindings.py` | The key bindings as data (key, event, Kanata gesture, where it is taught, contexts, layers, screen-reader label): the source for the Controls screen and the HUD chips, and the input to the binding lint in `check_contrast.py` (no collisions, no Tab or Space, reserved characters only in typing scenes, every gesture present in `design/ui-key-bindings.md`) |
| `kit_screens2.py` | P1 screens and icons: artifact frame, elevator map, seal award, toast, Mira's results, seal and patch icons, settings, the first-use and Controls screens |
| `render_screens.py` | Renders every screen to `screens/<id>-1366x768.png` (and `-grey-` for the shape-and-text screens) and the main stage to `reference-1366x768.png` / `reference-greyscale-1366x768.png`. Needs Edge or Chrome, so it is not part of `build_all.py` |
| `build_world.py` / `world-native.png` | The approved Gate 1 Orientation scene without its four baked pixel markers, drawn by `build_gate1.scene` |
| `screens/*.png` | 21 colour renders and 7 greyscale twins at 1366×768 (stage 1280×720, world ×4): see the table below |

Renders in `screens/`: `layout-base`, `layout-nav`, `layout-numbers-symbols`, `layout-practice`, `layout-base-microsoft`, `setup-calibration`, `setup-characters`, `terminal-scene`, `terminal-success`, `terminal-tab-practice`, `glitch-duel`, `input-feedback`, `artifact-closeup`, `elevator-map`, `seal-award`, `toast`, `mira-results`, `seal-icons`, `settings`, `first-use`, `controls`; greyscale twins (`-grey-`) for `layout-practice`, `setup-calibration`, `input-feedback`, `glitch-duel`, `elevator-map`, `seal-award` and `seal-icons`. The keyboard inset is open in the terminal, success, Tab-region and glitch renders (the screens that can coexist with it); Layout help, setup, elevator, settings and the award cards are full overlays, which sit above the inset (z 80 against 50).

## Rebuild and check

```
cd art-direction/ui-kit
$PY check_contrast.py          # WCAG AA, token sanity and page lint
$PY build_world.py             # markerless world, verified against the approved scene
$PY build_reference.py         # writes reference.html
$PY render_screens.py          # optional: needs Edge or Chrome; rewrites every PNG
```

`$PY art-direction/build_all.py` from the repository root runs the first three. A second run leaves `git status` clean (the PNGs are only rewritten by `render_screens.py`). Renders use headless Microsoft Edge (`--headless=new --window-size=1366,768 --hide-scrollbars --screenshot=…`).

## Director decisions

1. **Anchors unchanged.** Ink, paper, teal, coral, violet and gold keep their published hex values. Roles are fixed.
2. **Text uses lightened accent tints.** Raw teal (4.21:1), coral (4.06:1) and violet (4.08:1, 3.22:1 on raised cards) fail 4.5:1 as text on `--panel-raised`. Added `--accent-terminal #36C3B6`, `--accent-conversation #F2928A` and `--accent-glitch #B79FEA` for text; fills, glyphs and outlines keep the anchor hex. Gold needs no tint.
3. **No text on violet fills.** Ink on violet is 4.08:1, so the kit never sets text on a violet fill. The glitch marker carries no text; the duel's violet is a frame and a glyph, and its title uses `--accent-glitch`.
4. **Panels.** `--panel` is ink, `--panel-bg` is ink at 96% (text is rechecked over white and black worlds), plus `--panel-raised #233C4E` and `--panel-sunken #10202A`. `--border #7A94A5` is 4.58:1 on panel and 3.61:1 on raised.
5. **Type.** Minimum 16 px (`--text-sm`), body 18 px. Sans-serif body stack, monospace for keys, gestures and editor text, a display stack for titles only.
6. **Stage.** `--world-zoom: 4`, 320×180 world, 1280×720 stage, letterbox `#0E1822`. The UI is laid out in stage CSS px and is not zoomed with the world.
7. **Held keys are never colour-only.** Teal face, sunk 3 px, and a "Hold" tag. XX keys have a dashed border.
8. **Markers.** Speech bubble (coral), monitor (teal), diamond with an arched doorway (gold), folded page (violet). Paper halo and ink line. Distinct in greyscale by outline.
9. **Reference world has no baked markers.** `world-native.png` is the approved scene without its four pixel markers; markers are drawn only in the DOM/SVG layer.
10. **Key bindings are decided** ([`design/ui-key-bindings.md`](../../design/ui-key-bindings.md), data in `bindings.py`). **Return** (tap-hold Caps + N, calibrated in setup) is Interact, Continue, ride and Retry, split by state. **Esc** (tap Caps; Caps + `[` from level 07) is Skip and Back, one layer per press, and does nothing in the open world, so a slip of the Caps key is harmless. **Arrows** (tap-hold Caps + H, J, K, L) move and choose. **Q** (tap Q) opens the journal in the world only. **Backtick** (tap Backtick) shows the hint: in Standard it re-opens the inset and instruction, in Focused it reveals the hint line, in Violento it is off after the introduction; it is a reserved character in typing scenes, and the Focused prompt is a keycap with its gesture, not a mouse button. **`?`** (tap-hold F, then `/`) opens Layout help everywhere. The elevator opens with Interact at its call panel, then Up / Down, Return and Esc. Tab is never a game key (the old journal-on-Tab idea is gone) and neither is Space. Dialogue has two modes: a modal conversation (Continue and Skip) and a non-modal instruction line (no keys taken). The held-key inset opens by itself on first use of each binding. Every binding works on `base`, `nav` and `practice`.
11. **Hint wording in written prompts.** Prompts and dialogue use "tap-hold Caps + L" (Kanata vocabulary), not "hold Caps + L". Every instruction on every screen reads "To *action*, you need to press **key**. Hint: key is **gesture**." (the page lint enforces the three parts).
12. **Inset content.** Four numbered cells plus the layer name and hold timing in the header. The inset covers stage x 16–588 and the bottom of the stage. When the key sits off the home row, cell 1 shows two mini rows (the key's row and the home row), which makes the inset about 40 px taller; scenes that coexist with it end their panel above it.
13. **Portrait slot is a placeholder** until the portraits are wired in (the chibi atlas exists).
14. **Greyscale toggle without script.** `#grey` applies `filter: grayscale(1)` through `:target`; `#` clears it.
15. **Layout help is one screen, four tabs, one device switch.** MacBook is the default diagram. The Microsoft keyboard is a segmented switch that swaps the bottom row and states Alt becomes Command, Windows becomes Option, right Alt becomes Right Command and also holds nav, right Windows becomes Right Option. The `lh-` classes style all five renders.
16. **Swedish remaps are not drawn.** The first reference drew `;` as "ö" on the nav tab; `kanata.kbd` does have that mapping, but the game scope excludes Swedish letters, so it is removed. A, S and F on nav are drawn as "stays a letter" (N20) instead.
17. **Practice tab honesty.** It draws XX for digits 1 to 0, Backspace, Return, both Shift, Ctrl, Opt and Cmd on both sides and the arrows; it lists Esc, Forward Delete, Home, End, Page Up and Down as also silent; and it states that minus, equals and grave still type. The emergency exit is a locked card that says "Shown after its runtime behaviour is verified"; the sequence is not drawn anywhere.
18. **Calibration status is exactly three words.** Not started, Observed output, Skipped. There is no "verified" or "detected", and the footnote says the number row gives the same 1 and ! as Space + A and Space + Q.
19. **Diagram modes are separate views, not a combined legend.** Physical positions (key names, Space held, target ringed) and Resulting characters (what each key gives while Space is held). The same compact keyboard (`--key-unit-sm`, 28 px) draws both.
20. **Feedback states differ by icon, border and words.** Observed output: eye, solid teal border. You confirmed this gesture: person with a check, double paper border. Can't be observed here (OS-reserved): shield with a keyhole, dashed border. All three show Gesture shown, Output and Effect separately, and none uses "detected", "you are in the nav layer" or "you used the number row". The practice layer is a "player-confirmed / unconfirmed" chip, and the scene layer and the layer the player says is active are drawn as two separate boxes.
21. **Scenes dim the world less than overlays.** Terminal and glitch scenes use `--scrim-scene` (58%) so the room stays readable; overlays keep `--scrim` (72%).
22. **Editor vocabulary.** Cursor: a paper block with a 2 px focus outline. Selection: `--selection-bg` fill plus a 3 px `--focus` bar. Target line: a gold-tinted line, a gold diamond in the gutter and a "target line" tag. Target word: a dashed gold outline. Success: a thicker gold frame, a check icon and words; never a full-screen effect. Broken token in a duel: a wavy violet-tint underline.
23. **The Tab region is announced in words.** A dashed teal frame labelled with a lock glyph, an "Announced" strip that is also the `aria-live` text, and Esc visible in the bar at all times. Tab never leaves the region by itself and never traps the player.
24. **Duels are untimed with a visible Retry.** A Turns card (done, current, to do) says "Untimed. Nothing is lost on a retry." Retry is a real button, focused, with Return.
25. **Seals are shape-distinct.** Five gold octagons with an ink outline and a glyph each: sprout (Orientation), ring (Records), three-node network (Systems), crescent and star (Night Shift), tree (Executive). An unearned seal is the dashed outline of the same octagon. The seal award card uses static rays; reduced motion shows it at rest.
26. **Patches use Mira's colours and live in the UI as tokens.** `--patch-peach`, `-lime`, `-brass`, `-navy`, `-pale`, `-glint` come from `MIRA_PATCHES_SPEC.md`; none is a marker hex or violet. Each patch is a 48×40 stitched icon with a paper edge; earned has a gold frame and "Earned", the rest are dashed and say "Not yet".
27. **Medal and patch are separate rewards.** A first clean run records a baseline and awards the patch; the medal needs a later, faster clean run with at least 95% accuracy and no less accurate than the baseline. The results card says speed never affects stars, seals or the ending.
28. **Elevator.** Locked stops always show the seal they need, where it is earned and a nearby objective, plus "Stay on this floor" and the header Back key. The current floor is a filled square node with an arrow and the words "You are here".
29. **Settings.** Larger text, high contrast and reduced motion are On/Off switches with a knob; sound is off by default with effects and music as sub-switches. Difficulty previews how hint lines fade (Standard three parts, Focused two plus a dashed "Show hint" prompt that is a keycap with its gesture, Violento action only). Reset progress always shows a confirmation, and the safe button is focused.

## Contrast results (check_contrast.py)

All pairs pass (the last run ended `ALL CHECKS PASSED`). Lowest text ratios: `accent-glitch` on `panel-raised` 5.01:1, `accent-conversation` on `panel-raised` 5.06:1, `accent-terminal` on `panel-raised` 5.27:1, `selection-text` on `selection-bg` 5.52:1, `accent-discovery` on the gold-tinted target line 6.45:1. Lowest UI ratios: `border` on `panel-raised` 3.61:1, `ink` on `violet` 4.08:1, `focus` on `selection-bg` 4.17:1, `teal` on `panel-raised` 4.21:1. New pairs cover the code well, the selection and cursor, the target line (synthetic blend), the six patch glyphs, switches, seals and the paper document.

### Page lint

`check_contrast.py` also builds `reference.html` in memory and asserts: every `font-size` and `font` shorthand is at least 16 px (through `--text-*` tokens); `font-family` appears only through the `--font-*` tokens (no pixel font); teal, coral and violet are never a text colour; nothing sets a background of violet; every sentence "you need to press" is followed by "Hint:" within 420 characters; the page has unique `#s-<id>` targets and no script. It also runs the binding lint: the table in `bindings.py` has no collisions, no Tab, Space or F-keys, reserved characters only in typing scenes, every binding on base, nav and practice, and every gesture appears in `design/ui-key-bindings.md`; the journal chip shows Q on at least three screens and never Tab; Show hint is a keycap; the Controls and first-use screens exist; no wording that leaves a key undecided remains in the page or these two documents.

## Unsure or open

- Whether the Hint key costs the third star in recall scenes, and whether the elevator needs a "quick route back to the hub" row in the journal (both in the open questions of `design/ui-key-bindings.md`). The bindings themselves are decided (decision 10).
- Fonts are system stacks; no web font is bundled. Inter is listed first and used only if installed.
- Layout help's live highlight ("the key most likely to have produced the last event") is behaviour, not drawn. COMPONENTS.md lists the keys and the wording; the reference draws only the static diagram.
- The high-contrast and larger-text variants of each screen are described in COMPONENTS.md ("Settings") but not rendered; the implementer should review each screen at 1366×768 and 1920×1080 with the larger-text setting.
- The Microsoft variant is drawn for the base tab only; the nav, numbers-symbols and practice tabs use the same bottom row, with the same remap strip.
- The practice tab is drawn for the MacBook keyboard; a Microsoft practice view would silence the Windows and Alt keys by their physical positions (the toggle counts them by position).
- The setup screen is drawn at 1280×720 only; the 427×240 optional wide view changes the world, not the UI layer.
