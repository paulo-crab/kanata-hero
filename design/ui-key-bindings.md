# UI key bindings

**Status:** decided by the UI/UX designer on branch `feat/ui-key-bindings` (2026-10-02), under the producer's delegation. It resolves the proposals in the UI kit's decision 10 and the open "Show hint" key. Candidate until the producer merges it. The UI kit (`art-direction/ui-kit/`) draws every binding below; `bindings.py` there holds the same table as data and `check_contrast.py` fails if the kit, the data and this document drift apart.

**Sources:** `docs/game-design.md` (Hint grammar, Layout help, Browser behavior and accessibility, gesture inventory A to D, Difficulty and scoring), `levels.md` (hint lines, Orientation 01 to 06, Records 07), `design/levels/` on `feat/levels-orientation-foundation` (`SCHEMA.md`, `SLICE.md`, level 01 data), `art-direction/ui-kit/` and `~/.config/kanata/kanata.kbd` (read only; nothing copied).

## The rule in one paragraph

Six keys run the whole game. **Return** confirms the main thing in front of you (talk, continue, ride, retry). **Esc** steps back one layer (skip, close, leave) and does nothing in the open world. The **arrows** move you and move a list selection. **Q** opens the journal, **`** (backtick) shows the hint, **?** opens Layout help. Every one is a conventional key that the browser can see, taught by a gesture the player has met before first use. Tab and Space are never game keys.

## Decisions

Each action has one primary binding and, where it helps, one alternative. The mouse is always an alternative and is not listed again.

| Action | Key (observed output) | Kanata gesture (the hint) | Taught before first use in | base / nav / practice |
| --- | --- | --- | --- | --- |
| Interact (talk, use a device, call the elevator) | **Return** | tap-hold Caps + N | Setup calibration step 2 (Caps + N); first used at the level 01 arrival | works / is the nav layer / works |
| Continue (dialogue, award, results, setup) | **Return** | tap-hold Caps + N | same | works / is the nav layer / works |
| Skip (a conversation) | **Esc** | tap Caps | Level 01, the welcome popup | works / n.a. / works |
| Back, close, leave | **Esc**. Alternative from level 07: tap-hold Caps + `[` | tap Caps | Level 01 popup; the alternative at level 07 | works / works / works |
| Move, and choose in a list | **Arrow keys** | tap-hold Caps + H, J, K, L | Setup step 1 (Caps + H); level 01 loop teaches all four | works / is the nav layer / works |
| Show hint | **`** (Backtick) | tap `, a plain tap | Plain tap; Ivo introduces it at level 01 and the first Focused prompt shows it | works / works / works |
| Journal | **Q** | tap Q, a plain tap | Plain letter tap (base typing, level 02); Ivo introduces it at level 01 | works / works / works |
| Layout help | **?** | tap-hold F (Shift), then tap `/` | Setup step 5 (F as Shift); named at level 01 (Ivo's tablet) | works / release Caps first (F types `f` on nav) / works |
| Elevator: open the map | **Return** at the call panel | tap-hold Caps + N | Interact | works / is the nav layer / works |
| Elevator: pick a floor, confirm, go back | **Up / Down**, **Return**, **Esc** | tap-hold Caps + K / J, tap-hold Caps + N, tap Caps | Setup step 2; level 01 | works / works / works |
| Retry (glitch duel, after a wrong result) | **Return** | tap-hold Caps + N | Setup step 2 | works / is the nav layer / works |

Reading the last column: "is the nav layer" means the gesture is Caps held, so it cannot be used from another layer by definition; it still produces the same output while the player stands on base or on practice. The physical Return, Esc and arrow keys also produce these outputs on base, so a player who has not learned Caps + N yet is never stuck. The practice layer silences physical Return, Esc and the arrows, which is why each hint teaches the Caps gesture: **every binding is confirmed to work on `practice`** (see "Checked against kanata.kbd").

Rules that apply to all of them:

1. **One press, one action.** Ignore `event.repeat`. The key press that opens a layer (Return on a person, Q on the HUD) is consumed by that press and never also acts inside the new layer. There is no minimum delay and no time limit on any story interaction.
2. **Return and Esc are layered, not duplicated.** The top layer takes the key. Return runs the top layer's primary button (Continue, Ride, Retry, the focused row). Esc closes or leaves the top layer, one layer per press: popup, overlay, scene, in that order. Nothing the player does with Return or Esc loses progress.
3. **Esc does nothing in the open world.** Beginners often tap Caps by mistake while learning to hold it for walking; that must never open or close anything. (This is why the journal is not on Esc.)
4. **Modifier-free only.** Q, Backtick, Return and Esc act only when no Command, Control, Option or Shift is down (so Cmd + Q, Cmd + `` ` `` and a home-row Shift hold are never intercepted). `?` is Shift + `/`, so it is the one place Shift is expected.
5. **Reserved characters.** In every typing scene (terminal, editor, form, label, keypad, log) exactly two characters are commands: `?` and `` ` ``. No level may ask the player to type either. No other key is taken from a typing scene: Q, Return and the letters are text there, and the journal key is off.
6. **Tab and Space are never game keys.** Tab is captured only inside an announced Tab practice region (with Esc as the exit). Modal overlays keep focus inside while open, Tab and Shift + Tab move between their controls, and Esc always leaves.

### Where each binding appears, where it is off, and why it beats the alternatives

**Interact: Return, tap-hold Caps + N.**
- *Appears:* the prompt beside a person (coral border) or a device (teal border), `Action — key — gesture`; the elevator call panel. *Off:* in dialogue, overlays and typing scenes, where Return means Continue, the focused button, or the scene's own lesson. In a typing scene Return is whatever the scene asks for.
- *Rejected:* **Space** teaches nothing (the hint would read "Space is tap Space"), is typed text in every editor, and a press held 220 ms enters the numbers layer, so a slow press does nothing. **E or F** are letters (text in scenes), and F is a tap-hold Shift that types nothing if held for 200 ms.

**Continue: Return, tap-hold Caps + N.** Same key as Interact on purpose: one habit for "go on", split only by state, because the prompt hides while a dialogue is open.
- *Appears:* the dialogue footer (`Continue  Return  tap-hold Caps + N`), and the primary button of setup, the seal award, Mira's results and the elevator. *Off:* instruction lines (non-modal, below).
- *Rejected:* **Space** (as above) and **a mouse-only button**, which would break the keyboard-only promise.

**Skip: Esc, tap Caps.**
- *Appears:* the dialogue footer. Skipping ends the conversation. Any instruction it carried is not lost: the step's instruction line is shown, and the journal repeats it. *Changes meaning:* in setup, Esc skips the whole setup; a single calibration step is skipped by moving on with Down (a step left alone is recorded as Skipped).
- *Rejected:* **Return twice** (mashing Continue would skip by accident) and **Tab**, which is never bound.

**Back, close, leave: Esc, tap Caps; alternative tap-hold Caps + `[` from level 07.**
- *Appears:* the header of the journal, Layout help, elevator, settings, artifact frame; the bar of every terminal, form and duel scene (`Leave the terminal  Esc  tap Caps`). It is the keyboard exit that is always visible. *Off:* the open world (rule 3). *Changes meaning:* in the Tab practice region it leaves the region first; in a duel it leaves the duel.
- *Rejected:* **Backspace** (text editing, and silent on `practice`) and **Esc as pause or journal** (accidental Caps taps would open it). The alternative exists because tap Caps has a 200 ms window; Caps + `[` has none. Prompts name the alternative only after level 07 has taught it.

**Move or choose: arrows, tap-hold Caps + H, J, K, L.**
- *Appears:* the walking tutorial; every list (journal rows, elevator floors, settings, setup steps). *Off:* typing scenes, where arrows move the cursor as the lesson says.
- *Rejected:* **WASD** (letters, and the game's point is that field and terminal movement share the Caps gesture) and **Tab to move through lists** (never bound outside its region).

**Show hint: `` ` `` (Backtick), a plain tap.**
- *Appears:* a HUD chip (`Hint  `` ` ``) in Standard and Focused; on a Focused line as the dashed prompt `Show hint  `  tap ``; in the Controls screen. *Off:* Violento after a gesture's introduction (no chip, no prompt, the key does nothing). *Meaning by difficulty:* Standard shows all three lines already, so the key re-opens the keyboard inset and the instruction if the player closed them. Focused: reveals the hint line and opens the inset. It is a request (`request:<dialogue id>` in the level data).
- *Rejected:* **H, I or any letter** (text in scenes, and Show hint must work in scenes). **`/`** (also typed in code, and Firefox's Quick Find takes it on a page with no focused field). **`?`** (Layout help, which is free reference and never costs a star; a hint can). **F1** (macOS keeps it for brightness; the browser may never see it). **Tab** (never bound). **Shift + Return** (three keys held across both hands).
- *Why Backtick:* it is the one unmapped key that no curriculum row types (the 23 held-Space outputs are `! @ # $ % ^ & * ( ) _ +`, the digits and minus), it passes through Kanata untouched on every layer, and it is the key that opens the console in many PC games, so players already read it as "ask the game". Bind it by `event.code === 'Backquote'`, with `preventDefault`, so a dead-key input source cannot swallow the next letter.

**Journal: Q, a plain tap.**
- *Appears:* the HUD chip (`Journal  Q`); the journal's header (Esc closes it, and Q toggles it). *Off:* dialogue, overlays and every typing scene (Q is text there); live in `walk` scenes and during Mira's routes (the journal then pauses the route like Layout help). The journal's "Also from here" row holds Layout help, Settings and Controls.
- *Rejected:* **Tab** (the kit's old proposal: it is never bound, and the browser needs it). **J** (a tap-hold Shift: a 200 ms press types nothing, and with Caps held it is Down). **Esc** (rule 3). **I, O, M, B** (I and O sit under the walking hand; M is Caps + M Backspace). Q is a plain unmapped key, reachable with the left hand while the right hand walks, and it reads as "quests".

**Layout help: `?`, tap-hold F (Shift), then tap `/`.**
- *Appears:* the HUD chip (`Layout help  ?`) and the journal's Layout reference row. *Off:* nowhere: it opens from dialogue, overlays, typing scenes and Mira's routes (they pause). The alternative for a player who has not learned the Shift hold: Q, then Return on the Layout reference row. *Inside it:* Left / Right (tap-hold Caps + H / L) and Tab / Shift + Tab switch tabs, Esc closes.
- *Rejected:* **F1** (see Show hint) and **a letter** (text in scenes). The game spec already fixes `?`. Note the gesture must use the left hand's F: see "Checked against kanata.kbd".

**Elevator.** Open: Interact (Return) at the call panel. Inside: Up / Down pick a floor, Return rides (or takes the card's primary button on a locked floor, "Go to Records"), Esc goes back (`Back to the floor`, `Stay on this floor`).
- *Rejected:* **a global map key** such as M or E (a letter, and fast travel from anywhere would hide the locked door's requirement, which the level rules say must stay visible). A "quick route back to the hub" is an open question below.

**Retry (glitch duel): Return, tap-hold Caps + N.**
- *Appears:* the focused button under the code. *Meaning:* a turn ends in success or a wrong result (the level data's `rejects`). The wrong result moves focus to Retry and pauses the editor; Return retries, Esc leaves the duel. *Off:* while the editor has focus, Return is not used by a duel (a duel never asks for Return as typed text; a lesson that needs it is a terminal scene).
- *Rejected:* **Esc then Return** (the kit's old wording: Esc already leaves) and **R** (a letter in the editor, and R is the reload chord).

## Dialogue has two modes

Hint-bearing lines (`hint` is set) and plain conversation lines (`hint: null`) behave differently, because an instruction must stay on screen while the player does the thing:

| Mode | Is | Keys | Closes when |
| --- | --- | --- | --- |
| Conversation (modal) | A speaker's story or welcome lines, no live step | Continue **Return**, Skip **Esc**. World input is paused | The last line, or Skip |
| Instruction line (non-modal) | A line that carries the step's action, key and gesture | None are taken. The world and the scene stay live, so Esc still closes the popup the line is about | The step's `completes_when` is met |

Without this split the level 01 popup would break: "To close the welcome popup, you need to press Escape" would be a modal whose own Esc skips it before the popup sees the key. In Focused the instruction line shows the action and key and the dashed `Show hint  `` ` ``  tap ``` prompt.

## How the held-key teaching inset appears on first use

The inset (four numbered cells) opens by itself, once per binding, the first time that binding's prompt is on screen and its output has not been seen. It closes on the first observed output, on Esc, or when its step ends; after that it opens only on request (the Hint key) or in a new gesture's guided room. Sequence for the first minutes:

1. **Setup calibration** already observed Caps + H and Caps + N (status Observed output), so Return is already familiar to a player who ran setup (setup is optional and never blocks the story).
2. **Level 01 arrival:** Ivo's welcome is a conversation. The footer prompt shows `Continue  Return  tap-hold Caps + N` and the inset opens for it: cell 1 the key position (bottom row and home row, Caps held, N bright), cell 2 Hold Caps then Tap N, cell 3 Output Return, cell 4 Effect "Next line". The first Return closes it.
3. **The welcome popup:** an instruction line asks for Escape; the inset opens for tap Caps (hold order is a single Tap; the header says "release within 200 ms").
4. **Q, Backtick and `?`:** each has an introduction line from Ivo the first time it is useful; its prompt opens a one-key inset (cells 1 and 2 show the key and a single Tap). The HUD chips are visible from the first frame, but chips never open the inset.
5. **Focused and Violento:** the inset opens on first use in every mode, because it is the introduction; afterwards Focused hides it until Hint, and Violento never reopens it.

Mouse alternatives never need the inset.

## Checked against kanata.kbd

Read-only check of `~/.config/kanata/kanata.kbd` (nothing copied or changed):

- **Return** is `nav-enter`: `(input real caps)` then `(unmod ret)`. Works from `base` and `practice` because `caps` is the same `tap-hold-press` in both and the `nav` layer is shared. Physical Return is `XX` in `practice`.
- **Esc** is the tap of `caps` (`tap-hold-press 200 200 esc @nav`): released inside 200 ms it is Esc; held longer, or with another key pressed, it is nav and no Esc. Caps + `[` is `nav-escape` with no timing. Physical Esc is `XX` in `practice`.
- **Arrows** are `@left @down @up @right` on H J K L in `nav`. Physical arrows are `XX` in `practice`.
- **Q** and **Backtick** are not in `defsrc`; `process-unmapped-keys yes` passes them on `base`, `nav` and `practice` (on `numbers-symbols` Q types `!`; Backtick is only used where no layer key is held) (`docs/game-design.md`, number-row coverage: grave, minus and equals still type).
- **`?`**: F is `tap-hold-tap-keys` with the left-hand key list, so `/` (a right-hand key) lets F wait for its 200 ms hold and then Shift applies. J is right-hand and `/` is in `right-hand-keys`, so J + `/` types `j/`. Only the left hand's holds make `?`, and the hold must be established before `/`.
- **Right Command and N:** `nav-enter` needs a real Caps, so Right Command + N is Command + N (new window), not Return. No hint may say "Right Command + N". The Microsoft keyboard's right Alt also reaches `nav` through `rnav`, and the same applies.

## Browser observability

Match Return by `event.key === 'Enter'`, Esc by `'Escape'`, arrows by `ArrowUp`, `ArrowDown`, `ArrowLeft`, `ArrowRight`, Q by `event.key.toLowerCase() === 'q'`, `?` by `event.key === '?'`, and Backtick by `event.code === 'Backquote'`. Ignore events with `isComposing`, with `repeat` (rule 1) and (except `?`) with any of `metaKey`, `ctrlKey`, `altKey`, `shiftKey`. Call `preventDefault` only for these keys and only while the play surface or a modal has focus. Do not use the Fullscreen API without a visible exit: in fullscreen the browser takes the first Esc. No binding relies on Command or Control, a held Space, a held Tab, F-keys or media keys.

## Accessibility

Every binding is visible as a keycap in three places: its prompt (`Action — key — gesture`), the HUD chips, and the Controls screen (reached from the journal footer and from Settings). Each has a screen-reader label in the hint grammar, listed in `bindings.py` (`aria`), for example "Show hint. Key Backtick. Hint: Backtick is a plain tap; Kanata leaves it alone." The keycap for Backtick draws the `` ` `` glyph and the prompt says "Backtick" in words. The Controls screen states which bindings work on `practice`. A held key is never the only cue: every prompt carries its gesture text.

**Future option, out of scope:** a remap table in Settings (action to key), keeping the reserved characters, Tab and Space off the allowed list, and storing the choice in `localStorage` beside the other settings.

## Impact list for the producer

### `levels.md`

I did not edit it. Lines to reword or extend:

- **01 The Lobby, hint lines:** add Ivo's introductions (proposed text below) and keep "To close the welcome popup, you need to press Escape. Hint: Escape is tap Caps." as an instruction line (non-modal).
- **The "Hint lines" intro paragraph** ("Standard difficulty shows all three lines, Focused hides the hint until requested"): add "Focused asks for it with the Hint key, Backtick; Violento shows no hint key after the introduction".
- **World and art rules, Locked doors and elevator** ("The elevator always returns to unlocked districts"): add that the elevator opens by interacting (Return) with its call panel.
- **07 The Door That Answers:** the line "Escape is tap-hold Caps + `[`, or tap Caps" stays; it is also the Back alternative named in prompts from this level.
- **Journal mentions** ("the journal records evidence", artifact rows "Added to the journal"): no key is named in `levels.md`, so nothing breaks; the chip and prompts supply Q.

Proposed Ivo lines for level 01 (after the popup, neutral portrait, three short lines in the hint grammar):

> To open your journal, you need to press **Q**. Hint: Q is **tap Q**. It keeps the step you are on.
> To see a hint again, you need to press **Backtick**. Hint: Backtick is **tap Backtick**, the key at the top left of the letter block.
> To open the Layout help, you need to press **?**. Hint: **?** is **tap-hold F** (Shift), then **tap /**. It is also a row in the journal.

### Level data (`design/levels/`, Orientation `SCHEMA.md`)

- `request:<dialogue id>` and `on_request: true` mean "the Hint key was pressed". In Violento a request is honoured only during a gesture's introduction.
- Add `modal` to a dialogue (default true when `hint` is null, false when `hint` is set), so the validator can prove an instruction line never owns Esc or Return.
- Add a validator rule: no scene's `accepts`, `target` or `prompt` text requires typing `?` or `` ` `` (none does today; a search of the four district branches found none).
- A `terminal_scenes` entry of `kind: walk` keeps Q live; every other kind turns it off. Duel scenes must not ask for Return as typed text.
- Interactions of `kind: elevator` use Interact (Return); `kind: npc`, `terminal`, `door`, `artifact` and `mira` likewise.
- Add one introduction dialogue each for Q, Backtick and `?` in level 01 (text above) so the "taught before first use" claim has a line behind it.

### Proposed text for `docs/game-design.md` (not edited)

Add after "Layout help":

> ### Controls
> Six conventional keys drive the interface, each observed as an ordinary browser key and each reached by a gesture the player has already learned. **Return** talks, uses, continues and confirms the primary button (tap-hold Caps + N). **Esc** skips a conversation and steps back one layer, and does nothing in the open world (tap Caps, or tap-hold Caps + `[` from Records). **Arrow keys** move and choose (tap-hold Caps + H, J, K, L). **Q** opens the journal, **Backtick** shows the hint (Focused and Standard), and **?** opens Layout help (tap-hold F, then `/`). Tab and Space are never game keys; Tab is captured only inside an announced practice region. In typing scenes only `?` and Backtick are commands and no level asks for them as text. Every binding works on `base`, `nav` and `practice`; physical Return, Esc and the arrows are silent on `practice`, so the hints teach the Caps gestures. Bindings are fixed in v1; a remap table is a later option.

Amend hint-grammar rule 8: "Focused shows the action and the conventional key, with the hint on request (the Hint key, Backtick). Violento shows only the action after a gesture's introduction, and the Hint key is then inactive."

Amend Layout help, "Opening and closing": "`?` (Shift + /) opens it. The gesture is a held home-row Shift on the left hand (tap-hold F, then `/`); a right-hand Shift hold on J would type `j/` because `/` is a right-hand key."

### Other documents (not edited by me)

- `art-direction/ui-kit/UI_KIT_SPEC.md` and `COMPONENTS.md`: updated by this change.
- `design/levels/SLICE.md`: its "Components each scene needs" table should name the Controls screen and the first-use inset.
- `README.md` decisions log: one line, "Key bindings decided: Return, Esc, arrows, Q, Backtick, ? (design/ui-key-bindings.md)".

## Conflicts with `kanata.kbd` and contradictions

1. **`docs/game-design.md` says "home-row Shift produces `?` on every layer".** Only the left hand's F does (see above). J + `/` types `j/`. The kit and this document use F.
2. **Esc by tap Caps has a 200 ms window**, against the rule "no timing on story interactions". The alternative Caps + `[` has none, so the Back binding is always reachable without timing, and no step requires the tap.
3. **Return from Right Command is not available** (`nav-enter` needs a real Caps). The Microsoft keyboard's right Alt gives arrows but not Return. Nothing here claims it.
4. **Practice** silences physical Return, Esc and the arrows (decision above), and silences digits 1 to 0: no binding uses a digit.
5. **UI kit decision 10** (journal on Tab) conflicted with "never trap Tab" and with the Layout help's own use of Tab. Resolved: Q.
6. **UI kit duel text** said Esc reaches Retry; Esc leaves. Resolved: a wrong result focuses Retry.

## Open questions for a human

- **A "quick route back to the hub"** is promised by the game spec's opening tutorial but has no key. Recommendation: no new key; add a "Ride to the hub" row to the journal footer (Q, then Return).
- **Does the Hint key cost the third star?** The spec gives three stars for a clean recall run "without hints". Recommendation: yes in `recall` scenes only, and the card says so before it reveals the line.
- **Whether Show hint should also work in Violento during a recall scene.** Today it does not (spec: action only after introduction).

## Player decisions (2026-10-02)

These close the open questions in the first version of this document.

- **Hint costs the third star in recall scenes only.** Using the Hint key (Backtick) in a recall scene forfeits the third star for that scene. Guided and variation scenes are unaffected. The hint card must say so before the player reveals the hint.
- **Hint does not work in Violento recall scenes.** In Violento the Hint key stays off after a gesture's introduction, including in recall scenes.
- **"Ride to the hub" is a journal row, not a new key.** The game spec's quick route back to the hub is reached from the journal's "Also from here" row and confirmed with Return.
- **Backtick and `?` are reserved in typing scenes.** No level may ask the player to type either as text; the level-data validator should reject such a task.

## Playtest 1 changes (2026-10-02)

- In setup and calibration no single key press skips everything. Esc on the setup screen and Up during calibration open a confirm card (Return = yes, Esc = back); Down skips the current calibration step; Return settles step 2 only.
- Output feedback is shown only in typing scenes and calibration, plus a short toast in the world; it is never a persistent card.
