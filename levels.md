# Kanata Hero: The Department of Motion — levels and world

This is the story, quest, and visual production brief for the 20 main levels in [`docs/game-design.md`](docs/game-design.md) v0.7. The game spec owns the curriculum and gesture inventory; this file owns story, cast, and per-level detail; [`art-direction/STYLE_BIBLE.md`](art-direction/STYLE_BIBLE.md) owns visual style. See the [document map](README.md). The gesture IDs below refer to that document's curriculum. The active Kanata configuration remains the authority for actual key behavior; a versioned layout manifest is a planned implementation artifact. Every main quest is untimed. Accurate completion opens the story; Mira's repeatable routes are the optional speed game.

## The story the player uncovers

The player is a software engineer called in to repair a sequence of small office incidents. The campus feels generous: daylight, plants, comfortable furniture, and colleagues who remember the player's work. Its cheerful performance system, **Pace**, congratulates employees for following approved routes. As tickets are repaired, the player finds that Pace has been changing department names and duplicating work orders. It measures *activity along prescribed paths*, then calls the extra movement productivity. Old travel routes and old keyboard habits keep its reports looking healthy. The coworkers have quietly left precise records of the original, shorter workflows.

The campaign's conflict is resolved by an accurate audit, not a fast one. The player restores the original routing records and gives every floor access to the audit. The building's rigid patterns relax; people can choose their own paths. Mira's speed routes tell a parallel, warmer story about learning a place well enough to move through it confidently. Her times never prove that someone deserves access.

The tone moves from curious and welcoming, through quietly uncanny, to humane relief. Pace should sound helpful even when its advice is wrong; it is a system to correct, not a monster to defeat. Glitches are misregistered office objects, cleared through short untimed repair interactions with immediate retry.

## World and art rules

| District | Hub, approximate size, and navigation | Characters and visual signature | Ambient sound and change after review |
| --- | --- | --- | --- |
| **Orientation** | 28×18-cell reception around an indoor garden. Arrival elevator on the north wall, west end; printer north; left and right desks flank garden; mailroom southeast; Records door east. A later garden cut-through shortens the return. | **Ivo**, the precise reception lead, has a broad cardigan silhouette and tablet; **Mira**, the courier, has a messenger bag, asymmetric jacket, and coral strap. Ivory stone, blue-gray glass, terracotta upholstery, teal planting beds. | Air handling, shoes on stone, garden water, distant conversations. Printer and garden lamps wake; synchronized worker loops break into individual idle poses. |
| **Records** | Two-screen archive around a circular desk. Repair door on the entrance route; log and margin rooms left; long-report gallery above; review chamber at the far end. A sliding file wall closes the return loop to Mira's chute. | **Noor**, archive clerk, has a tall narrow silhouette, rolled sleeves, and a cherry-wood stamp. Sea-blue shelving, linen labels, coral folders, luminous ceiling ring. | Paper handling, drawer runners, subdued room tone. Labels regain distinct colors and the hidden corridor becomes walkable. |
| **Systems** | 38×24-cell service floor around a large routing machine. Payroll east, alarm hall west, glass bridge and formula room above, relay review beyond all three branches. Conduits visibly connect tasks to the hub. | **Hal**, systems technician, has a compact utility vest, thick gloves, and a folding stool. Porcelain panels, cobalt equipment, mint circuit light, safety orange edges. | Low ventilation, relay clicks, bridge footfalls. Circuits illuminate in sequence; a service walkway opens and the Night Shift elevator stop is revealed. (The bridge and return walkway open earlier, in levels 12 and 15.) |
| **Night Shift** | 34×20-cell collaboration floor with a safe break-room entry, security vestibule, two parallel office routes, northern ledger, and a service corridor back to Mira. Keep the main route legible in shadow. | **Ada**, night caretaker, has a long coat, warm lantern, and calm posture. Indigo glass, plum carpet, silver frames, islands of desk light. | Quiet HVAC, isolated lamp clicks, footsteps with long room reverb. Break room and service corridor gain warm light and human silhouettes. |
| **Executive Floor** | 30×20-cell atrium around a living tree. Three short incident branches can be done in any order. Final door is visible from entry; the epilogue reuses the same walkable atrium. | **Vale**, executive liaison, has a sharp navy silhouette that gradually loosens; earlier coworkers arrive after repairs. Pale stone, copper details, dark navy seating, living green. | Spacious air, leaves, restrained piano-like discovery notes. Repeated geometry becomes varied, window light warms, and the final door opens to daylight. |

Use the 2D pixel direction in the design spec and the art-direction style bible: 16×16 logical-pixel floor cells and 16×24-pixel people on a one-cell footprint, a fixed 320×180 view scaled by whole numbers (×4 on a 1366×768 laptop), high orthographic three-quarter overhead view, four directional walk sets, bold silhouettes, and selective animation. *CrossCode* and *Sea of Stars* are broad references for readability, color, and light. The player-supplied screenshots in `art-direction/references/` are useful for crisp tile edges, reusable patterns, and unmistakable paths; their outdoor fantasy art is not a template for this office. At 1366×768, the avatar, doors, paths, NPCs, and task marker must read with a keyboard inset open. Use crisp modern UI for dialogue, code, and physical-key diagrams; the world itself is illustrated sprite art, not an ASCII or CRT display. Teal terminal glow, coral conversation marker, violet glitch shape, and gold opened-path marker retain their meaning on every floor, with distinct icons so color is never the only cue. Sound and music start off by default.

**Production budget:** Build the 20 quest spaces from one shared office tile/prop kit, five district palette and lighting treatments, and one focal landmark per district. Reuse desks, doors, shelves, partitions, plants, document frames, and interaction icons; let their placement, labels, and light state explain the quest. A named quest prop in the briefs below is normally a rearrangement or small variant of this kit, not a request for a new illustrated asset. Use 4–6 walk frames per direction as a starting point, a few reusable reaction poses, three glitch archetypes, and one document close-up frame for optional artifacts. Quest completion should usually swap door, light, sign, and NPC-pose states rather than repainting the room.

The reference images sharpen that budget: give Orientation's garden, Records' circular desk, Systems' routing machine, Night Shift's long window, and Executive's tree the composition and color care of a focal illustration (reference 07 and the garden in 08); build the corridors and task rooms from repeated modules like references 03 and 06. Use the clear wall, floor, door, and light hierarchy of references 04 and 05 for puzzle spaces. Reference 07's density is a landmark-quality target, not the density target for every tile. All resulting assets remain original office art.

Every new-skill site follows **hub → short branch → task room → changed return route**. A room teaches a gesture with a physical-position cue, varies the context, then checks recall later without that cue. A completed main quest changes at least two visible elements, such as machine light plus coworker pose or door plus floor route. The elevator always returns to unlocked districts, and it opens by interacting (Return) with its call panel. Locked doors show the needed seal and a visible route back.

**Interface keys (wording for every prompt).** Six conventional keys run the interface ([`design/ui-key-bindings.md`](design/ui-key-bindings.md)). **Interact** and **Continue** are one key, Return (tap-hold Caps + N): it talks, uses a device, calls the elevator and moves a dialogue on. **Skip** is Escape (tap Caps): it ends a conversation, and the step's instruction line and the journal keep whatever it carried. **Back, close and leave** are also Escape, one layer per press; Escape does nothing in the open world. The arrow keys (tap-hold Caps + H, J, K, L) move the avatar and choose in a list. **Q** opens the journal, **Backtick** asks for the hint and **?** opens Layout help. Tab and Space are never interface keys, and no scene asks the player to type `?` or Backtick. A line that carries a hint is an instruction line: the world stays live and it takes no keys. A line without a hint is a conversation line and owns Return (Continue) and Escape (Skip).

### Recurring cast and portrait direction

| Character | Story role and dialogue voice | Sprite and portrait cues |
| --- | --- | --- |
| Engineer avatar | Observant, competent, and mostly defined by the player's choices. Their journal records evidence rather than making grand speeches. | Custom hair, skin, and clothing color within a stable silhouette; deliberate foot placement, quick turns, readable concerned and satisfied poses. |
| Mira | Courier who knows every shortcut. Starts playful, later admits she kept copies of routes Pace tried to erase. | Coral bag strap visible even in dark rooms; lively diagonal posture; one small patch added for each clean courier baseline. |
| Ivo | Reception lead who believes clear instructions help people; begins to question repeated onboarding scripts. | Broad cardigan and rectangular tablet; greeting wave becomes an unscripted laugh after the review. |
| Noor | Archive clerk and keeper of unaltered paper records. Precise, dry humor, quietly defiant. | Tall outline, rolled sleeves, stamp and file tabs; posture straightens as cabinets open. |
| Hal | Technician who built parts of Pace's routing display and notices the wrong assumptions. | Utility vest, folding stool, orange tool roll; crouched repair and puzzled reactions. |
| Ada | Night caretaker who sees what happens when staff leave. Direct, kind, practical about recovery. | Long coat and lantern; warm rim light, steady gestures in otherwise still rooms. |
| Vale | Executive liaison who signed summaries without seeing raw tickets. Wants a defensible audit once shown the evidence. | Navy suit, copper badge, rigid pose that softens across three final repairs. |
| Pace | The campus performance system; a presence in signage and small UI copy. Its language becomes more repetitive as errors accumulate. | Rounded wayfinding icon and orderly horizontal bars; no face, jump scare, or hostile full-screen animation. |

### Portrait cue map

This is the single source for which dialogue portrait each recurring character shows, and when. The portraits are the approved chibi set in [`art-direction/portraits/PORTRAITS_SPEC.md`](art-direction/portraits/PORTRAITS_SPEC.md): every character has **neutral**, **concerned**, and **pleased**, and five have a **signature**. What each face means is in [`PORTRAIT_PERSONAS.md`](art-direction/portraits/PORTRAIT_PERSONAS.md). A line uses **neutral** unless a cue below says otherwise; that includes every hint line, so instructions read calmly. Pace has no portrait.

| Character | Neutral | Concerned | Pleased | Signature |
| --- | --- | --- | --- | --- |
| Engineer (journal and artifact lines) | Task notes and journal entries. | Inspecting a tampering artifact: Unissued badge, Training card (first printing), First route receipt, Carbon copy A, Uncut index, ID envelope, Alarm strip, Scoring proof. | Each seal (06, 11, 16, 19, 20); the Ada's shift book and Public audit copy artifacts. | None. |
| Ivo | 01–03 instructions; 01's scripted wave becoming a nod; Plant Tags before the Orientation review. | 04 when the player shows Ivo the optional Training card (shorter than Ivo's script); 06 when Pace calls the review a "consistency review". | 03 when the clock hands synchronize; 05 when the pinboard turns asymmetrical and human. | `ivo_laugh`: after the 06 seal, then on every later greeting, Plant Tags revisits, and Ivo's 20 arrival. |
| Mira | Offering any route or a repeat run. | Lost Folios, when she shares the copy she kept (the erased-routes admission); Lights-Out Delivery, when she asks the player to keep the safe route open. | Each patch, earned on a route's first clean baseline; her final story scene. | `mira_grin`: the 05 "one useful hand" joke and the Morning Mail introduction. |
| Noor | 07; the 08 instructions; Misfiled Minute. | 08 when she blames the re-indexing; 11 when she sends the correction against Pace. | 08 when her stamp changes to accepted; the 11 seal. | `noor_unimpressed`: at Pace's claims in 09 (the moved sign-off), 10 (the summary that says nobody reviewed it), and 11 ("equivalent"). |
| Hal | Default elsewhere; Quiet Alarm; the end of 13, when Hal sits instead of crouching. | 13 before the nightly run; the start of 14 (anxious). | The 14 fix (settled focus); the 16 seal. | `hal_puzzled`: 12 (the relocated keypad) and 15 (the formula reveals the detour score on a display Hal built). |
| Ada | The 17 greeting; 18 ("a locked tool need not mean a locked route"). | 17's practice-exit and emergency-exit explanation; Desk for Dawn. | 17 once the player confirms understanding and Ada walks alongside; 19 when the break room lights. | None. |
| Vale | The 20 opening, and every branch line before the first repair. | Each time a repaired branch's evidence beats Pace's incomplete summary. | After the second repair. | `vale_softened`: after the third repair, the epilogue audit release, and Names on the Wall. |

Vale's cues follow the **number of repairs completed, not which branch**, because the player chooses the branch order. They match the world sprite's softening states (0 before any repair, then 1–3).

## Main levels

Level numbers are production IDs, not a menu shown to the player. The player encounters each as a place and a coworker's problem. A **seal** is a required department review reward; an **artifact** is an optional lore collectible with no mechanical advantage.

The **Hint lines** under each level are sample prompts in the spec's [hint grammar](docs/game-design.md#hint-grammar): the action, the conventional key, then the Kanata gesture. Coworkers and artifacts say them in their own voice; the keyboard overlay shows the same keys as keycaps. Standard difficulty shows all three lines, Focused hides the hint until requested with the Hint key (Backtick), and Violento shows only the action after a gesture's introduction; the Hint key is then inactive. In a recall scene the Hint key costs that scene's third star, and the hint card says so before it reveals the line.

### Act I — Orientation: learn to move and type deliberately

#### 01. The Lobby

- **Place and story:** The elevator opens on the north wall at the west end of the lobby, northwest of the indoor garden. Ivo asks the new engineer to visit four desks before the first ticket can be assigned. Two workers visibly walk the same tiny loop at the same moment, an early hint that the building is over-managed.
- **Play:** A broad, obstacle-free garden loop teaches Caps+H/J/K/L one direction at a time, then a varied four-stop route and a later unprompted walk to Ivo. A small modal lets the player tap Caps for Escape; release Caps and type a short desk label. Cover B06 and N01–N04. A harmless paper-fold glitch can demonstrate a turn-based repair after the tutorial.
- **Hint lines:**
  - Ivo: "To walk to the west desk, you need to press **Left Arrow**." Hint: Left Arrow is **tap-hold Caps** (nav) + **H**.
  - Ivo: "To close the welcome popup, you need to press **Escape**." Hint: Escape is **tap Caps**.
  - Ivo: "To open your journal, you need to press **Q**." Hint: Q is **tap Q**. It keeps the step you are on.
  - Ivo: "To see a hint again, you need to press **Backtick**." Hint: Backtick is **tap Backtick**, the key at the top left of the letter block.
  - Ivo: "To open the Layout help, you need to press **?**." Hint: **?** is **tap-hold F** (Shift), then **tap /**. It is also a row in the journal.
- **Art and state:** Skylight rays, waist-high planters, floor inlay pointing to each desk. After the route, the reception turnstile opens and Ivo changes from scripted wave to a nod. Garden markers shift from teal to gold. No narrow passage should interrupt the first four-direction drill.

#### 02. Badge Printer

- **Place and story:** North of the garden, a personalized badge printer keeps producing generic employee names. Ivo asks the player to restore the engineer's badge and three coworkers' labels.
- **Play:** Type short names, ordinary digits, punctuation, and home-row sequences. Guided prompts distinguish plain mapped taps such as `b`, `w`, `0`, `4`, `u`, `t`, `m`, `x`, `n`, `v`, `r`, and comma from later held-layer gestures; a shuffled label is the recall check. Include literal A/S/D/F and J/K/L/; taps and same-hand rolls. Cover B01–B02. The printer checks resulting text, not physical key origin. Names and labels are typed in lowercase through level 03, because Shift is first taught in level 04 (the hint's "Bea" is spoken; the typed label is `bea`).
- **Hint lines:**
  - Printer card: "To print the `b` in Bea's name, you need to press **B**." Hint: **tap B**. It only jumps by word while nav is held.
  - Printer card: "To print badge number 40, you need to press **4, then 0**." Hint: **tap 4**, **tap 0**. Plain taps stay digits on base.
- **Art and state:** Three-cell printer counter, stacked blank cards, readable badge preview. Correct cards gain varied colors and the north task light steadies; Mira moves into the southeast mailroom and offers **Morning Mail**. Optional artifact: **Unissued badge**, whose old department name differs from the current sign.

#### 03. The Clock

- **Place and story:** A meeting-room clock shows different times on two sides of the glass. Ivo's scheduling form has spaces and tabs missing from its entries.
- **Play:** Separate tap Space from held bare Space, tap Tab from held bare Tab, and show modifier-first Space/Tab exceptions. Use a safe in-game focus lane for observable Tab behavior; the external Homerow action from held Tab is explained and player-confirmed if available. Show the 220 ms Space and 250 ms Tab hold cues without adding a speed target. Vary by correcting two appointment lines, then recall with a fresh line. Cover B07–B10.
- **Hint lines:**
  - Ivo: "To separate the two times, you need to press **Space**." Hint: **tap Space**. Tap-hold would enter numbers-symbols.
  - Ivo: "To move to the next field, you need to press **Tab**." Hint: **tap Tab**. Tap-hold Tab sends Shift + Command + Space for Homerow.
  - Ivo: "To move back a field, you need to press **Shift + Tab**." Hint: **tap-hold F** (Shift) first, then **tap Tab**. A held modifier keeps Tab ordinary.
- **Art and state:** Twin-faced clock, sunlit glass conference room, projected form with clear focus outline. Correct entries synchronize the hands and slide the glass door aside; Ivo's tablet stops flashing. Leave a visible keyboard exit from the Tab practice region.

#### 04. Left Desk

- **Place and story:** An empty workstation has four approval stamps assigned to one hand. Ivo explains that holding a familiar letter briefly can become a modifier.
- **Play:** Teach A/S/D/F holds as left Control, Option, Command, Shift, then tap the same letters as text. Each hold gets its own safe, local task with an opposite-hand target; combined holds are activated one at a time. A later approval sheet mixes the four without a diagram. Cover B03 and B05, including approximately 200 ms hold timing and release order.
- **Hint lines:**
  - Stamp card: "To italicize the approval note, you need to press **Command + I**." Hint: Command is **tap-hold D**, then **I** on the other hand.
  - Stamp card: "To capitalize the K in Kai, you need to press **Shift + K**." Hint: Shift is **tap-hold F**.
  - Stamp card: "To type the `d` in "desk", you need to press **D**." Hint: **tap D**. No hold, no modifier.
- **Art and state:** Cherry desk, four distinct stamp silhouettes, left-side task lamp. Each approved sheet visibly joins a wall pinboard; the desk lamp and adjacent corridor stripe light together. Optional artifact: **Training card, first printing**, which shows a shorter workflow than Pace's current script.

#### 05. Right Desk

- **Place and story:** Across the garden, the mirror workstation's labels are reversed. Mira jokes that the building seems convinced everyone has only one useful hand.
- **Play:** Teach J/K/L/; holds as right Shift, Command, Option, Control, with separate safe tasks and ordinary taps between them. An opposite-hand edit, a same-hand roll that stays text, and a mixed left/right approval form provide variation and recall. Cover B04–B05 and revisit B02–B03.
- **Hint lines:**
  - Mirror card: "To undo the reversed stamp, you need to press **Command + Z**." Hint: Command is **tap-hold K**, then **Z** on the other hand.
  - Mirror card: "To capitalize the S in Sol, you need to press **Shift + S**." Hint: Shift is **tap-hold J**.
  - Mira: "To type "jk" in the label, you need to press **J, then K**." Hint: **tap J**, **tap K**. A same-hand roll stays text.
- **Art and state:** Same desk family with a deliberately different layout, warmer lamp, distinct right-side stamp shapes. The completed wall pinboard becomes asymmetrical and human; its map points toward the review desk. Optional artifact: **Mirror card**, annotated by an employee who preferred the right-hand route.

#### 06. The Other Keyboard — Orientation review

- **Place and story:** Ivo brings a spare keyboard to the garden desk. The badge roster has one row of native editing actions and one row of alternate navigation. Pace calls this a "consistency review."
- **Play:** Revisit all four directions using physical Right Command+H/J/K/L, compare them with Caps navigation, and demonstrate native Backspace, Delete, Return, Escape, arrows, Home/End, Page Up/Down, and modifiers in base. Use a safe local editor where events are observable and an external-only explanation where the OS intercepts them. Show that other Right Command shortcuts retain their usual meaning. The MacBook physical diagram is default; a Microsoft keyboard setup path maps Alt→Command, Windows→Option, and Right Alt→Right Command. Its device-specific check is player-confirmed and never blocks the seal. Finish with a changed-context roster that accurately uses learned base and movement skills. Cover B11–B12, B15, N21; revisit B01–B06.
- **Hint lines:**
  - Ivo: "To walk up to the roster, you need to press **Up Arrow**." Hint: Up Arrow is also physical **Right Command + K** on base, the same as tap-hold Caps + K.
  - Roster: "To erase the stale row, you need to press **Backspace**." Hint: On base, the physical Backspace key still works. You'll learn tap-hold Caps + M in Records.
  - Setup card: "To press Command on the Microsoft keyboard, you need to press **Command**." Hint: Command is physical **Alt** on that device; Windows is Option.
- **Art and state:** Garden review table with two physically different keyboard props and large selectable diagrams in clean UI. Grant the **Orientation seal**. The east Records door opens, the garden cut-through unlocks for return visits, and background workers stop marching in sync. Optional artifact: **First route receipt**, showing that Pace counted a detour as a successful movement.

### Act II — Records: use movement to repair information

#### 07. The Door That Answers

- **Place and story:** Records' entrance door asks for an address but erases characters at the wrong side of the cursor. Noor is waiting at the circular desk beyond it.
- **Play:** A series of short, untimed door panels teaches Caps+N Return; Caps+M and Caps+Space as two Backspace routes; Caps+comma Forward Delete and Caps+X Control+D as different forward-delete outputs; Caps+`[` Escape. Each route is practiced independently, then mixed on a new address. After Caps release, ordinary `m`, `x`, `n`, and comma are typed into the final address. Cover N13–N18 and B01.
- **Hint lines:**
  - Door panel: "To submit the address, you need to press **Return**." Hint: Return is **tap-hold Caps** + **N**.
  - Door panel: "To erase the last character, you need to press **Backspace**." Hint: Backspace is **tap-hold Caps** + **M**, or **tap-hold Caps** + **Space**.
  - Door panel: "To delete the character in front of the cursor, you need to press **Forward Delete**." Hint: Forward Delete is **tap-hold Caps** + **,**.
  - Noor: "To delete forward the Emacs way, you need to press **Control + D**." Hint: Control + D is **tap-hold Caps** + **X**.
  - Door panel: "To cancel the wrong entry, you need to press **Escape**." Hint: Escape is **tap-hold Caps** + **[**, or **tap Caps**.
- **Art and state:** High archive door with two clear text windows, visible cursor and deletion side; no flashing failure state. The door retracts and Noor steps out from behind the desk; shelf-end lights change to gold. Mira appears beside the chute and offers **Courier Loop**.

#### 08. Filing Drift

- **Place and story:** File addresses are drifting between lines of an incident log. Noor believes the latest automatic re-indexing caused it.
- **Play:** Move by words with Caps+B/W in a code-like line, repair an address, then type plain `b` and `w` after release. The varied log contains punctuation and a different word length; later recall is an unmarked address in another cabinet. Cover N05–N06 and B01.
- **Hint lines:**
  - Noor: "To step back over the drifted word, you need to press **Option + Left**." Hint: Option + Left is **tap-hold Caps** + **B**.
  - Noor: "To reach the next address, you need to press **Option + Right**." Hint: Option + Right is **tap-hold Caps** + **W**.
- **Art and state:** Long cherry cabinets, sea-blue folders with offset labels, ceiling ring reflected on polished floor. Repaired folders align and a left branch opens; Noor's stamp mark changes from rejected to accepted. Optional artifact: **Carbon copy A**, the first original route record.

#### 09. The Margins

- **Place and story:** A ledger has signatures at both ends of each line, but Pace's revised copy moved the sign-off to the middle.
- **Play:** Caps+0 and Caps+4 reach line start and end; demonstrate Shift+4 / `$` reaching the end as mapped. Insert or remove a short token at both margins, then solve a fresh line without arrows on the overlay. Plain `0` and `4` are checked after release. Cover N07–N08 and revisit B01.
- **Hint lines:**
  - Ledger: "To reach the opening signature, you need to press **Command + Left**." Hint: Command + Left is **tap-hold Caps** + **0**.
  - Ledger: "To reach the closing signature, you need to press **Command + Right**." Hint: Command + Right is **tap-hold Caps** + **4**.
- **Art and state:** Two-sided ledger table with a thin beam of daylight across its full width. Correct margins light both ends, and a rolling ladder moves to reveal the upper gallery. Optional artifact: **Margin stamp**, with the archived date visible when inspected.

#### 10. The Long Report

- **Place and story:** Noor's report spans many pages, while Pace's summary claims nobody reviewed its first or last section.
- **Play:** Use Caps+U/D for Page Up/Down and Caps+T/G for document start/end. A viewport indicator makes page motion distinct from document motion. Guided page markers lead to two facts; a changed report asks for a fact at another location; the recall check omits the positional hint. Plain `u`, `d`, `t`, and `g` work as text after release. Cover N09–N12 and B01.
- **Hint lines:**
  - Noor: "To read the next page, you need to press **Page Down**." Hint: Page Down is **tap-hold Caps** + **D**.
  - Noor: "To go back a page, you need to press **Page Up**." Hint: Page Up is **tap-hold Caps** + **U**.
  - Report tab: "To check the first section, you need to press **Command + Up**." Hint: Command + Up is **tap-hold Caps** + **T**.
  - Report tab: "To check the last section, you need to press **Command + Down**." Hint: Command + Down is **tap-hold Caps** + **G**.
- **Art and state:** Tall gallery with stacked binders, an elevator-like rolling shelf, high window shafts. Correct citations bring light to the upper desk and open the review chamber; Noor places the original report beside the summary. Optional artifact: **Uncut index**, proving a department name changed without a staff request.

#### 11. Marked for Review — Records review

- **Place and story:** Noor wants the original routing sentence selected exactly before she sends a correction to the next floor. Pace insists the copy is equivalent.
- **Play:** Select with Shift plus supported Caps navigation, using home-row F/J or a physical Shift in base; the Shift hold must engage before Caps is pressed, because F is a literal `f` and J is Down while Caps is held. Demonstrate that Caps+4 consumes Shift and goes to plain line end. Test Caps+A/S/F as literal letters while Caps is held; an accurate selection and replacement in a new report is the review. Revisit word, line, page, document, editing, Return, Escape, and the four arrows in distinct steps. Cover N19–N20, revisit N21 (introduced in level 06), and review N01–N18, B03–B04. Do not assume Right Command grants Caps-only extended gestures.
- **Hint lines:**
  - Noor: "To select the next word of the routing sentence, you need to press **Shift + Option + Right**." Hint: **tap-hold J** (Shift) first, then **tap-hold Caps** + **W**. While nav is held, J is Down and F is a literal `f`.
  - Noor: "To jump to the line end without selecting, you need to press **Command + Right**." Hint: **tap-hold Caps** + **4** drops Shift, so it moves without extending the selection.
  - Margin note: "To type an `a` while nav is held, you need to press **A**." Hint: A stays literal on nav, as do S and F.
- **Art and state:** Circular review desk beneath the luminous ring; selected text is visibly highlighted in a spacious editor panel. Award the **Records seal**. Shelves slide apart to expose a corridor back to Mira; folder labels regain coral and sea-blue variation. Optional artifact: **Noor's annotation**, a dry note that "equivalent" omitted the actual destination.

### Act III — Systems: build precise values and expressions

#### 12. Payroll IDs

- **Place and story:** The central routing machine rejects employee IDs because the keypad was relocated. Hal asks for the IDs exactly as printed.
- **Play:** Holding bare Space, enter each digit once in separate guided mini-forms: A/S/D/F/G/H/J/K/L/; → `1`–`0`. Vary by entering shuffled IDs, then recall every digit in a new order across an unseen batch. Show physical key positions and emitted digits separately. Record coverage per digit; a short correct ID cannot certify untouched digits. Cover S01–S10 and revisit B07.
- **Hint lines:**
  - Hal: "To enter digit 7 of the ID, you need to press **7**." Hint: 7 is **tap-hold Space** (numbers-symbols) + **J**.
  - Hal: "To enter digit 0, you need to press **0**." Hint: 0 is **tap-hold Space** + **;**.
- **Art and state:** Payroll wing east of the hub; glass-backed ID trays and ten individually lit routing nodes. Each correct node lights a conduit; the first completed batch extends a bridge and return walkway toward Mira's chute. Optional artifact: **ID envelope**, addressed to a department that no longer exists.

#### 13. Negative Balance

- **Place and story:** A ledger has turned a refund into a charge. Hal needs the sign restored before the nightly run.
- **Play:** Space+apostrophe emits `-` in signed values and a short range. Space+N/M stay literal `n` and `m`; they neither become digits nor editing commands. A second invoice changes the values, and a third checks the distinction without a hint. Cover S11 and S24; revisit several digits. If the resulting text is correct, the UI says output observed, not that it proved a physical Space hold.
- **Hint lines:**
  - Hal: "To mark the refund negative, you need to press **-**." Hint: - is **tap-hold Space** + **'**.
  - Invoice: "To type the `n` in "net" mid-value, you need to press **N**." Hint: N stays literal on numbers-symbols, as does M.
- **Art and state:** Smaller side room with orange sign markers, inset calculator display, and a clearly reversible ledger. Refund sign flips to green, the machine's warning light steadies, and Hal sits instead of crouching. Mira offers **Payroll Run** at the nearby chute.

#### 14. Alarm Glyphs

- **Place and story:** The alarm board has lost six punctuation labels, so two distinct alerts look identical. Hal asks for the exact glyphs.
- **Play:** Space+Q/W/E/R/T/Y yields `! @ # $ % ^`. Each output has its own guided alert card, followed by shuffled cards and a later unseen mixed alert string. `#` and `$` appear in plausible code or alert contexts, not as decorative symbols. Cover S12–S17 with individual evidence.
- **Hint lines:**
  - Alarm card: "To tag the alert number, you need to press **# (Shift + 3)**." Hint: # is **tap-hold Space** + **E**.
  - Alarm card: "To mark the alert urgent, you need to press **! (Shift + 1)**." Hint: ! is **tap-hold Space** + **Q**.
  - Hal: "To prefix the cost variable, you need to press **$ (Shift + 4)**." Hint: $ is **tap-hold Space** + **R**.
- **Art and state:** West alarm hall, six distinct alert lights and pictograms above porcelain panels. Correct labels separate the alarms into six hues and open a maintenance door; Hal's portrait changes from concerned (anxious) to pleased (settled focus). Optional artifact: **Alarm strip**, whose old alert names contain an extra department.

#### 15. Formula Room

- **Place and story:** Above the hub, a planning formula was flattened into an unreadable sentence. Restoring punctuation will reveal how Pace scores detours.
- **Play:** Space+U/I/O/P/[/] yields `& * ( ) _ +`. Each symbol receives a guided mini-expression; variation mixes nesting and underscores; recall uses a new expression in a different order. Clearly distinguish physical bracket key positions from displayed parentheses. Cover S18–S23 with individual evidence and revisit prior glyphs.
- **Hint lines:**
  - Formula wall: "To open the clause, you need to press **( (Shift + 9)**." Hint: ( is **tap-hold Space** + **O**.
  - Formula wall: "To join the variable name, you need to press **_ (Shift + -)**." Hint: _ is **tap-hold Space** + **[**.
  - Formula wall: "To add the detour bonus, you need to press **+ (Shift + =)**." Hint: + is **tap-hold Space** + **]**.
- **Art and state:** Glass bridge, large formula wall, hanging planters reflected in the floor. As clauses become valid, connected parts of the formula illuminate; bridge shutters open and a clean sight line back to the routing machine appears. Optional artifact: **Scoring proof**, showing that a longer route earned a higher "engagement" total.

#### 16. Crossed Wires — Systems review

- **Place and story:** The relay room receives all three branches. Hal can repair the machine only if the signal is reconstructed without replacing one output with a lookalike.
- **Play:** Mix all 23 held-Space outputs in new prompts, Caps navigation and edits, Space+Caps navigation, Space+Tab behavior, and modifier-first Space. The external Tab/Homerow effect and OS-reserved modified shortcuts are explanatory or player-confirmed, never required observed outputs. Three circuits require a number sequence, an expression, and a corrected typo; a final mixed recall checks every mapped output across the review batch. Cover S25–S26 and review S01–S24. Keep a per-output checklist visible in the journal rather than asking the player to type a giant arbitrary string.
- **Hint lines:**
  - Hal: "To move left without releasing numbers-symbols, you need to press **Left Arrow**." Hint: **tap-hold Caps** + **H** still works while numbers-symbols is held.
  - Relay card: "To type a space while Shift is already held, you need to press **Shift + Space**." Hint: **tap-hold F** (Shift) first, then **Space**. A held modifier keeps Space ordinary.
- **Art and state:** Relay room around a broad window onto the hub machine; three conduit families stay visually separate. Award the **Systems seal**. The machine lights in an intelligible sequence, a service walkway opens, and Hal pulls down a false panel to reveal the Night Shift elevator stop. Optional artifact: **Original routing diagram**, signed by several employees rather than Pace.

### Act IV — Night Shift: retain skill without legacy keys

#### 17. Lockdown Drill

- **Place and story:** Ada meets the player in a warmly lit break room. The night floor's old input stations have been locked under a training policy. She will only open the vestibule after explaining how to leave practice safely.
- **Play:** Show physical Control+Alt+GUI+V to enter and to leave Violento practice; wait for key release and ask for explicit player confirmation. A safe text box invites a self-check with physical Shift or Backspace. The UI never claims to detect the mode. Keep the toggle-out instruction visible throughout the act. Show Control+Shift+R as an operations card, not an action to perform in a scored scene; present physical Left Control+Space+Escape only as a last resort: it quits Kanata entirely rather than toggling practice, and Kanata stays off until restarted. Cover B13–B14 and V01–V02, V06.
- **Hint lines:**
  - Ada: "To enter the practice layer, you need to press **physical Control + Alt + GUI + V**." Hint: Use the real modifier keys. The toggle checks `input real`, so home-row holds don't count, and V alone still types `v`. Press it again to return to base.
  - Operations card: "To reload Kanata, you need to press **Control + Shift + R**." Hint: **tap-hold A** (Control), then **tap-hold J** (Shift), then **R**. F would type `f`, because R is on the same hand.
  - Ada: "Only as a last resort, to stop Kanata entirely, you need to press **physical Left Control + Space + Escape**." Hint: This is Kanata's emergency exit, not a layer toggle. All remapping stops until Kanata is restarted.
- **Art and state:** Break-room kettle, noticeboard, lamp pools, a vestibule with a clear back exit. Once the player confirms understanding, the security glass opens and Ada walks alongside for a short stretch; an exit instruction card stays pinned to the HUD.

#### 18. No Old Keys

- **Place and story:** Two office paths run north. One is lined with inert legacy stations; the other lets the player repair tickets through the skills already learned. Ada says that a locked tool need not mean a locked route.
- **Play:** Under player-confirmed practice, re-run all eight home-row modifier holds and Caps categories: arrows; word, line, page, document; selection; Return, Escape, backward and forward deletion. Ordinary letters and taps remain part of the task. Physical Right Command navigation is unavailable in practice; K held as Command is not the physical Right Command navigation alias. Offer short, untimed repairs and a changed-context recall desk. Cover V03–V04 and review B01–B05, N01–N20. All tasks remain playable if practice is unconfirmed, but the journal labels that evidence honestly.
- **Hint lines:**
  - Ticket: "To erase the wrong word, you need to press **Backspace**." Hint: Physical Backspace is XX on practice. Use **tap-hold Caps** + **M**.
  - Ada: "To walk north along the lit route, you need to press **Up Arrow**." Hint: Physical arrows and Right Command are XX on practice. Use **tap-hold Caps** + **K**.
  - Ticket: "To capitalize the name, you need to press **Shift + M**." Hint: Physical Shift is XX on practice. Use **tap-hold F**.
- **Art and state:** Repeated rows of desks initially look identical; the Caps route uses varied lamp and carpet cues, while the old route's stations are visibly silent. Each repaired ticket wakes a different office lamp and a coworker silhouette appears behind the interior window. Ada opens the north stair; Mira offers **Lights-Out Delivery** on the return route.

#### 19. The Ledger — Night Shift review

- **Place and story:** The northern ledger contains raw tickets that Pace never included in its reports. Its margins show that staff had proposed shorter routes long before the system did.
- **Play:** In player-confirmed practice, solve a mixed set requiring all 23 held-Space outputs plus Caps edits and ordinary text. Change the order from Systems and use several short natural records. Practice silences physical digits 1–0 (and so their shifted symbols), but the physical minus and equals keys still pass through, so `-`, `_`, `=`, and `+` remain typeable without held Space. The UI explicitly labels held-Space use as player-confirmed; observed character output alone cannot prove its source or the active layer. A final correction checks a modifier and a Caps edit. Cover V05 and review S01–S26, V03–V04.
- **Hint lines:**
  - Ledger: "To write the 0 in the total, you need to press **0**." Hint: The number row is XX on practice. Use **tap-hold Space** + **;**.
  - Ledger: "To mark the range, you need to press **-**." Hint: **tap-hold Space** + **'**. The physical minus key still passes through, but the ledger is asking for the layer.
- **Art and state:** Quiet archive-like room within the collaboration floor, one warm ledger lamp against deep indigo. Award the **Night seal**. The break room and service corridor light up, silhouettes start moving independently, and the elevator reveals the Executive Floor. Optional artifact: **Ada's shift book**, listing employees who kept the raw tickets safe.

### Act V — Executive Floor: make the accurate audit public

#### 20. Exit Interview — Executive review and epilogue

- **Place and story:** Vale waits beneath the atrium tree. Three short incident branches hold the evidence: **The Name** (a renamed department), **The Route** (a rewarded detour), and **The Count** (a corrected total). The player may choose their order. Pace offers an attractive but incomplete summary after each one.
- **Play:** Each branch is a new code-like task mixing base typing and home-row modifiers, Caps navigation/editing, and held-Space values/symbols. The player selects the exact original text, repairs the record, and confirms the destination. No branch is timed; each provides local retries and a clear route back to the atrium. The final audit asks the player to choose the accurate record over Pace's partial one, with all needed evidence visible. Review the playable B01–B12, N01–N21, and S01–S26 skills; the practice evidence from V01–V05 remains player-confirmed, and the B13/B14/V06 operations cards remain available. Never require Microsoft hardware, Homerow, a specific speed, or proof of the physical practice layer.
- **Hint lines:**
  - Vale (Violento, action only): "Restore the department's original name."
  - Vale (Violento, action only): "Confirm the corrected total."
  - By the finale, players on Violento see only the action; Standard still shows the full three-line hint for whichever gestures the incident needs.
- **Art and state:** Each repaired branch changes one atrium feature: nameplates become distinct, copper floor lines straighten into useful paths, and window views resolve into real daylight. Ivo, Noor, Hal, Ada, and Mira arrive as silhouettes first, then as recognizable sprites. After three accurate repairs, the visible final door opens. The epilogue is a playable walk through the restored atrium; Vale releases the raw audit to every floor, Pace's signs become optional guidance, and the player earns the **Department of Motion** seal. Optional artifact: **Public audit copy**, viewable later in the journal. The ending remains available without any courier medal.

### Difficulty and sensory ramp

| Levels | Main-task demand | Map and cue progression | Sound emphasis |
| --- | --- | --- | --- |
| 01–06 | One new gesture family per room, then a short mixed review. Every new hold is followed by ordinary taps. | One-camera garden loop grows into short desk branches; full physical-position cues fade only in later recall. | Welcoming reception bed; soft badge printer, paper, and garden cues mark correct local effects. |
| 07–11 | Cursor direction and word/line/page/document scale are mixed with editing and selection. | Two-screen archive asks players to remember a visible closed wall; later tasks omit the move-by-move prompt. | Drawer and paper textures distinguish cabinet, ledger, and report; shelf movement is a clear route cue. |
| 12–16 | Ten digits, minus, and twelve symbols are introduced separately, then recalled in shuffled mixed tasks. | Three Systems branches cross at the machine; each lit conduit explains where to go next. | Routing clicks build a sequence one circuit at a time, without a failure alarm over text. |
| 17–19 | Known tasks return under player-confirmed practice constraints; no new mandatory speed requirement. | Negative space and paired routes emphasize safe recovery and deliberate Caps navigation. | Deliberate quiet, isolated lamp clicks, then human room tone returning after the review. |
| 20 | Three independent mixed incidents lead to an exact audit decision. | Player chooses branch order; each repair visibly reshapes the same atrium used for the ending. | Sparse atrium ambience gains leaves, footsteps, and a short seal melody as people return. |

At every stage, Standard keeps hints available, Focused moves hints behind a request, and Violento hides familiar prompts only after their introduction. These are game guidance settings, separate from the actual Kanata practice toggle. Increasing complexity comes from combining already learned actions and longer spatial memory, never from reducing text readability or imposing a campaign timer.

## Side quests and revisits

Each district contains one small untimed accuracy puzzle and one or more optional lore artifacts. These can be accepted, paused, and replayed. Their reward is dialogue, a desk decoration, or an alternate sight line; none grants a required skill or seal.

| District | Accuracy side quest | Optional artifact and what it reveals | Revisit payoff |
| --- | --- | --- | --- |
| Orientation | **Plant Tags:** Ivo asks for five accurately typed labels on duplicated planters, including ordinary home-row rolls. | **Unissued badge** and the old training cards show names altered after printing. | The garden cut-through opened by level 6 shortens the walk to Mira and reveals a previously hidden seating nook. |
| Records | **Misfiled Minute:** Noor asks for an exact sentence repair using known Caps movement and selection, with no clock. | **Carbon copy A** and the uncut index show that a route was changed without a request. | The post-review sliding file wall closes a loop to Mira; earlier log cabinets can be reopened for focused practice. |
| Systems | **Quiet Alarm:** Hal needs a short expression corrected so one alert can be muted accurately. | **Scoring proof** and the routing diagram expose the detour metric. | Lit conduits and the service walkway make old branches faster to reach and their symbol exercises easy to revisit. |
| Night Shift | **Desk for Dawn:** Ada asks for an exact handover note using practice-friendly editing. | **Ada's shift book** names the people who protected the raw tickets. | The lit service corridor returns to the break room and Mira without crossing the silent stations. |
| Executive Floor | **Names on the Wall:** Vale invites the player to restore a staff credit list with known skills. | **Public audit copy** records the final correction in everyone's words. | The restored atrium is explorable after the ending; earlier floors retain their changed state and repeatable routes. |

### Mira's repeatable speed routes

Mira is visible from each district's traveled hub path, with a coral bag marker and a distinct **Optional speed** journal heading. The first clean run is an untimed route-learning attempt that records a duration and gives the story reward. Subsequent runs may chase an adjustable personal target. A medal needs every task-critical output correct, at least 95% correct actions overall, and accuracy at least as high as the baseline run. Faster but messier runs do not earn a medal. Routes remain available after the next district opens, so newly discovered shortcuts matter.

| First available | Route and story | Inputs and map design | Optional medal target · story reward (earned on the first clean baseline) |
| --- | --- | --- | --- |
| After 02 | **Morning Mail:** deliver three short labels from the southeast mailroom to visible desks. Mira introduces herself by asking the player to learn the loop first. | Base taps and ordinary text; a simple loop around the garden with no hidden door. | About 5% below the first clean baseline; **First Delivery** patch and a small mail tray for the player's desk. |
| After 07 | **Courier Loop:** correct slips while visiting Records desks. Mira has noticed that the same mail is being sent twice. | Caps arrows, Return, Backspace; longer path past the repair door and chute. | About 7%; **Clear Address** patch. The sliding file wall later provides a legitimate shorter route. |
| After 11 | **Lost Folios:** find three archive addresses in a report before delivering folders. Mira shares a copy she kept. | Word, line, page, document movement; multiple document positions plus the reopened archive loop. | About 10%; **Archive Loop** patch and a desk folder. |
| After 13 | **Payroll Run:** enter changing IDs and signed values at the Systems chute. Mira wants proof that the amounts reach the right people. | Shuffled held-Space digits and minus; east branch, bridge return, three distinct destinations. | About 12%; **Signed and Sent** patch. Later machine walkways can shorten travel. |
| After 16 | **Glyph Dispatch:** send expressions and repair one typo at the relay room. Mira can now route messages across every circuit. | All 23 held-Space outputs across several short prompts, plus Caps edits; full Systems loop. | About 15%; **Signal Keeper** patch and a miniature relay decoration. |
| After 18 | **Lights-Out Delivery:** carry an exact incident response through the collaboration floor. Mira asks the player to keep the safe route open for the next shift. | Base, Caps, held Space, and home-row modifiers in player-confirmed practice; break room to ledger and back via service corridor. | A personal-best target rather than a fixed percentage; **Night Courier** patch and Mira's final story scene. |

Show route checkpoints on the world map after a first attempt. A wrong task output gets immediate correction at that checkpoint, without a lost item or campaign penalty. In later runs, the journal can compare route time and keyboard accuracy separately. Mira's outfit gains the relevant patch after each clean baseline; medals can decorate the mailroom board. Her story scene after all routes is optional and does not alter the ending.

## Artifacts, reviews, and progression

The five **clearance seals** are awarded by levels 06, 11, 16, 19, and 20. The first four unlock the next elevator stop; the fifth records campaign completion. Side artifacts are inspectable objects or documents with a close-up, a two-to-four-line caption, and a placement visible on the walkable map. They never add stats, key abilities, or a hidden ending requirement. A player can collect them later through the elevator. Their visual sequence moves from changed labels, through original route evidence, to a public audit.

| Review | Accuracy evidence | World change and next destination |
| --- | --- | --- |
| Orientation, 06 | Base taps, both modifier hands, Caps arrows, alternate physical Right Command route where available; device-specific pieces player-confirmed. | Garden shortcut and Records door open. |
| Records, 11 | Caps navigation, selection, editing, exceptions, and plain-key return in a changed report. | Archive loop and Systems elevator stop open. |
| Systems, 16 | All 23 mapped held-Space outputs individually introduced and later recalled, plus layer interactions. | Conduits, service walkway, and Night Shift elevator stop open. |
| Night Shift, 19 | Repeated base, Caps, and held-Space use under an explicitly player-confirmed practice state. | Warm return corridor and Executive elevator stop open. |
| Executive, 20 | Three accurate incidents and exact final audit choice across all learned categories. | Restored atrium and playable epilogue open. |

Main quest stars measure completion, clean completion, and a clean changed-context recall without hints. Core mastery requires reliable results in distinct rooms, not low time or few actions. For each gesture, the journal should say whether the game observed the resulting output, the player confirmed the physical behavior, or the action is external-only. The browser cannot identify the original physical key or Kanata layer from a matching character. This matters especially for held-Space digits, Tab/Homerow, OS-reserved shortcuts, and the Violento toggle.

## Handoff checklist for each district

Deliver a layered tile map, collision and interaction footprints, camera bounds, entrance and elevator links, main and Mira route annotations, before/after review frames, NPC starting positions and reaction poses, terminal scene IDs, lighting states, and a gesture coverage sheet with **guided / variation / recall** columns. Also deliver the shared editable sprite source, PNG atlas, district palette and light variants, anchors, frame timing, and prop/lighting masks. Make one full-resolution Orientation gameplay composition and one walkable Records room from the shared kit before bulk production. Review each district at 1366×768 and 1920×1080 with a keyboard inset open, then with larger text, high contrast, and reduced motion.

No room may require a blind route, a speed threshold for story access, or an OS shortcut the browser cannot reliably observe. Keep the practice toggle-out instruction visible in Night Shift, keep all story interactions untimed, and give every route a clear way home.

### Level data status

The checklist above is delivered as validated JSON per district under [`design/levels/`](design/levels/), following the contract in [`SCHEMA.md`](design/levels/SCHEMA.md) and checked by `design/levels/validate_levels.py`. The global gesture inventory is `gesture-inventory.json` and the district, link, seal and Mira index is `world.json`.

- **Orientation: delivered** (levels 01–06, Morning Mail, the Plant Tags side quest) in [`design/levels/orientation/`](design/levels/orientation/): district, map and collision, six level files, the Mira route, coverage, level sheet and the list of art still needed. The vertical-slice file list is [`design/levels/SLICE.md`](design/levels/SLICE.md).
- Records, Systems, Night Shift and Executive deliver the same files in their own folders; this file stays the story and quest brief for them.
