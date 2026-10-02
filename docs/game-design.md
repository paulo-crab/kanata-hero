# Kanata Hero — game design and curriculum spec (v0.7)

> **v0.7 (2026-10-01):** added the hint grammar that every NPC line, artifact, and overlay prompt uses to tell the player which keys to press, and the Layout help reference screen.
>
> **v0.6 (2026-10-01):** reconciled with the keymap after the practice layer began silencing physical digits 1–0; corrected the emergency-exit description, layer identifiers, courier-patch timing, and per-quest coverage to match `levels.md`; pointed visual references and the pending scale decision to `art-direction/`. See the [document map](../README.md) for how the documents relate.

## Purpose
Build a keyboard-first, story-driven office puzzle game that teaches **the complete non-Swedish behavior of this machine's active Kanata configuration**. This is a product spec for a later OpenSpec implementation session. The **only layout source of truth** is the active `~/.config/kanata/kanata.kbd` symlink target, last reconciled on 2026-10-01 after the practice-layer digit change. Do not derive behavior from its README; it may be stale. The app should ship a versioned, testable layout manifest derived from it. If the keymap changes, reconcile the manifest and curriculum before release.

**Scope:** teach the base (`base`), Caps navigation (`nav`), held-Space numbers/symbols (`numbers-symbols`), and Violento `practice` layers, including their tap/hold behavior, transitions, and meaningful exceptions. Teach the Microsoft keyboard's modifier variant in setup. **Exclude Swedish letter remaps and all Swedish-specific missions, awards, and acceptance criteria.** Ordinary U.S. punctuation can still appear in typing tasks.

## World and game form
**Working title:** *Kanata Hero: The Department of Motion*. You are a software engineer on a late shift in a serene, daylit office whose window views are not quite right. Tickets arrive from departments whose names keep changing. Every resolved incident restores color and autonomy to the floor. A cheerful performance system, **Pace**, measures your movement, while the story slowly reveals why the building wants employees to reach for old keys. The full story, cast, and per-level briefs live in [`levels.md`](../levels.md).

This is a **top-down, single-player adventure RPG**. The player walks through a connected office campus, talks to recurring coworkers, finds terminals, opens shortcuts, and returns to earlier rooms when new keyboard skills make a route easier. Five districts act as hubs with small puzzle dungeons and a capstone “department review.” A quest journal distinguishes main work, optional coworker requests, and repeatable courier races. Main progress earns clearance seals and opens the next district. Optional quests supply lore, desk decorations, alternate routes, and speed medals. Some rooms contain roaming “glitches.” Touching one opens a short, untimed, turn-based repair duel: fix a token, choose a route, or edit a code fragment to clear the path. These encounters use known gestures and give immediate retry, with no random ambushes or speed gate.

The structure takes broad inspiration from the exploration, dungeon puzzles, and recurring NPCs of [the original NES *The Legend of Zelda*](https://www.nintendo.com/en-gb/Games/NES/The-Legend-of-Zelda-796345.html) and the journey through places, earned badges, and optional collection goals described in [Pokémon RPGs 101](https://www.pokemon.com/us/strategy/pokemon-rpgs-101/). Keyboard lessons draw on structured command unlocks in [VIM Adventures](https://vim-adventures.com/), repeatable proficiency practice in [VimHero](https://www.vim-hero.com/), and optional efficiency challenges in [VimGolf](https://www.vimgolf.com/). All locations, characters, prose, art, and mechanics are original. The game teaches **this Kanata layout**, not Vim semantics: Caps+B emits a macOS word-left shortcut, while plain `b` remains the letter `b`.

### What the player actually does
1. Explore a small tile map with Caps+H/J/K/L, with an always-visible destination and a quick route back to the hub. A short opening tutorial teaches this before free exploration.
2. Speak to an NPC or inspect a glowing terminal. A dialogue box gives a concrete problem, a hint about the relevant gesture, and a clear objective.
3. Enter an **interaction scene**: a tiny code editor, log, form, filing cabinet, or maze. Use ordinary typing, Caps navigation, held-Space outputs, and home-row modifiers to resolve it. The scene reacts to resulting keyboard events and gives specific feedback.
4. Return to the map. A door opens, a coworker moves, a memo changes, or a shortcut appears. The journal records the solved task and any new route.
5. Visit a department review after its core quests. That review mixes known skills in a new context and awards a clearance seal for accurate completion.

Field movement and terminal movement share the same Caps arrow gesture, reinforcing transfer. Other gestures live in tasks where their real output makes sense: word jumps in logs, numbers in IDs, symbols in expressions, and editing in code. The game never makes an arbitrary word-motion key move an avatar across grass. Newly taught abilities create discoverable routes, but an unavailable shortcut should have a visible explanation and an alternate way back.

## Visual production brief

> **Art-direction status:** This section is the product-level visual brief. Detailed look, palette, and pixel rules for new art are governed by [`art-direction/STYLE_BIBLE.md`](../art-direction/STYLE_BIBLE.md), whose primary authority is the player-approved overhead concept [`references/08-approved-overhead-direction.png`](../art-direction/references/08-approved-overhead-direction.png): a high, orthographic three-quarter overhead camera with 16-bit-era pixel craft. **Scale decided (2026-10-01):** 16×16 logical-pixel tiles and 16×24 people on a fixed 320×180 logical view, chosen by the player after the side-by-side test in [`art-direction/scale-test/`](../art-direction/scale-test/). Earlier 32×32 / 48×64 and 48×48 / 72×96 proposals are retired.

### The look
Build a **contemporary 2D pixel-art RPG** with a high three-quarter overhead view. Take the clear top-down readability and responsive movement of *CrossCode* and the strong color, light, and animated focal points of *Sea of Stars* as broad quality references. The player-supplied screenshots in `art-direction/references/` (catalogued in [`REFERENCE_NOTES.md`](../art-direction/REFERENCE_NOTES.md)) reinforce a useful production target: selective dark outlines, crisp tile boundaries, repeated patterns, and obvious walkable space at a glance. Translate those qualities into an original office setting; do not reproduce its outdoor scenery, characters, HUD, or tile designs. Favor clean silhouettes and selective detail over the dense, individually dressed environments associated with *Eastward*. The result should feel modern and beautiful at laptop size without needing a unique illustrated backdrop for every room.

The office should feel unusually well funded and slightly wrong. It has glass meeting rooms, daylight, plants, polished concrete, wood desks, upholstered seating, soft signage, and devices with inviting light. Express these with a compact reusable tile and prop set: a few clear material shapes, strong district palettes, and one memorable landmark per district. As the story progresses, duplicated plants, identical desk arrangements, repeating carpet motifs, and impossible window views become noticeable through arrangement and lighting rather than extra prop detail. Maintain a welcoming sense of discovery so the player wants to explore and revisit it.

**How to use the visual references** (files in `art-direction/references/`): 08, the approved overhead concept, sets the camera, office palette relationship, and garden landmark. 07 shows the focal richness to spend only on a district's landmark and selected hero moments; its full density is above this project's ordinary-room budget. 03 and 06 show how repeated modules and a small, consistently lit prop kit can make a whole map readable. 04 and 05 show top/side planes, contact shadows, doorways, and localized pools of light for interior puzzle rooms. 01 and 02 show immediate character and path readability. Transfer these composition rules to office materials and original geometry, rather than copying fantasy buildings, scenery, objects, or HUDs.

Four visual priorities govern every asset and room:

1. **Readable play:** The avatar, NPC, terminal, door, obstacle, quest marker, and walkable floor must be distinguishable at normal laptop size without labels.
2. **Expressive sprites:** Faces, hair, clothing, and posture distinguish recurring characters. NPCs react to player actions; the world changes visibly when a quest resolves.
3. **Spatial memory:** Each district has a unique landmark, silhouette, material mix, and accent family. Players should recognize where they are before reading the map title.
4. **Clean learning UI:** The world is pixel art; text and key diagrams are crisp modern UI. Use ASCII only where it belongs in code, logs, and signs, rather than drawing the entire world as glyphs.

### Camera, scale, and sprite rules

| Element | Production target |
| --- | --- |
| World grid | 16×16 logical-pixel floor cells. Furniture can span multiple cells; collision is authored per cell, separately from visible art. |
| Logical view | 320×180 logical pixels (20×11.25 cells), scaled by whole numbers only with nearest-neighbor sampling: ×4 = 1280×720 on a 1366×768 laptop (letterboxed), ×6 = 1920×1080. Never use fractional scaling. |
| Camera | High three-quarter overhead, orthographic view with the avatar slightly below center so the route ahead remains visible. Follow smoothly within a room and stop at its bounds. Avoid camera shake during learning tasks. |
| Player and recurring NPCs | 16×24 logical-pixel frame (1 × 1.5 cells) on a one-cell footprint, feet at the bottom-center anchor. Characters are distinguished by silhouette, hair shape and color, clothing, posture, and a signature prop (Ivo's tablet, Mira's coral bag). Fine facial expression lives in dialogue portraits, not world sprites. |
| Dialogue portraits | 48×48 logical-pixel head-and-shoulders portraits in the approved chibi direction ([`art-direction/portraits/PORTRAITS_SPEC.md`](../art-direction/portraits/PORTRAITS_SPEC.md)): neutral, concerned, and pleased for every recurring character, plus a signature expression for five of them. Drawn in the same palette and shown at the world's scale factor, so pixels stay one consistent size on screen. Which face appears at which story beat is in the [portrait cue map](../levels.md#portrait-cue-map). |
| Standard animation set | Four facing directions; idle, walk, interact, and two reusable reaction poses. Start with 4–6 walk frames per direction and a restrained idle loop. Add frames only where motion tests show a visible benefit. Animation timing should feel responsive to each keypress. |
| Glitches | 16–32 logical pixels depending on role; start with three reusable “misregistered office object” silhouettes, such as a displaced stapler, duplicate chair shadow, and folded form. Palette and behavior variants can distinguish encounters. |
| Environment | Reusable multi-cell walls, floor edges, doors, desk modules, shelves, plants, glass partitions, foreground occluders, and a small number of animated focal props. Distinguish rooms mainly through layout, accent colors, signs, light, and one landmark. |
| Output | Editable layered source files plus PNG sprite sheets/atlases and metadata for frame size, anchor, collision footprint, and animation timing. UI icons may be SVG or clean raster art. |

Use pixel-perfect edges on sprites and tiles. A few stepped, hard-edged light pools and contact shadows can provide depth without per-room painted lighting (STYLE_BIBLE §7). Reserve particles and complex effects for seals, machinery, and the finale. The 320×180 view gives a 20×11-cell play area at every supported size; HUD, dialogue, and the keyboard inset are crisp DOM overlays on top. Optionally offer a wider view (for example 427×240 at ×3 on a 1366×768 laptop, about 26×15 cells) as a whole-number zoom setting, never a fractional one. Because the keyboard inset covers roughly the bottom third of the left side, the camera should keep the avatar and the current target clear of it. Maps can scroll across several screens.

### Color, materials, and light
Use focused district palettes with stable functional colors. **Teal** marks interactable terminals, **coral** marks people with available conversations, **violet** marks glitches, and **gold** marks completed or newly opened paths. These colors need distinct shapes/icons as well, so color alone never carries meaning. The world uses simple value-grouped materials and a few controlled highlights; the UI uses opaque or nearly opaque panels that preserve text contrast.

Provisional interface anchor colors are ink `#182B38`, warm paper `#F4F2EC`, terminal teal `#19AFA2`, conversation coral `#EC776D`, glitch violet `#9876D5`, and discovery gold `#E6B750`. These are starting tokens for UI and interaction markers, not a six-color limit on the artwork. Adjust values after contrast checks while keeping their roles consistent across districts. Use a modern sans-serif for dialogue and UI, a clear monospaced face for code and key outputs, and a display face only for large titles. Body text should not use a pixel font.

| District | Dominant visual identity | Landmark and lighting | Story-state change |
| --- | --- | --- | --- |
| Orientation | Warm ivory, blue-gray glass, fresh teal, terracotta upholstery | Tall indoor garden and skylit reception; soft daylight and warm desk lamps | Badge printer and garden lights activate; workers stop moving in synchronized loops. |
| Records | Desaturated sea blue, linen, cherry wood, coral files | Circular archive desk beneath a luminous ceiling ring; light shafts through high windows | File walls slide open, archive labels regain color, and a hidden corridor becomes visible. |
| Systems | Cool porcelain, saturated cobalt, mint circuitry, safety orange | Large central routing machine with glass service bridges; precise task lighting | Data paths illuminate in readable sequences and machinery reveals new walkways. |
| Night Shift | Deep indigo, plum, muted silver, warm pools of light | Empty collaboration floor and long interior window; lamps and monitor glow against darkness | Human traces reappear: a lit break room, moving silhouettes, and an accessible shortcut. |
| Executive Floor | Pale stone, dark navy, copper, living green | Quiet atrium with a tree whose roots cross the floor plan; clean high-window light | Rigid geometry softens and the final route opens into daylight. |

Give each district one primary daytime or nighttime lighting setup as the story requires, plus a small set of reusable local light masks. Draw clear contact shadows under sprites and furniture, keep doorways brighter than adjacent dead ends, and reserve broader hard-edged glow steps for a few important devices; never a soft bloom haze (STYLE_BIBLE §7). No amber CRT wash, scanlines, chromatic aberration, or fake low-resolution overlay. The mystery comes from composition and changing spaces.

### Characters and UI
- **Engineer avatar:** Customizable hair, skin, and clothing color within a consistent silhouette. A readable idle stance, quick directional turn, and purposeful walk make each Caps navigation press feel immediate. Avoid coding the character as a generic cursor.
- **Mira, the courier:** Messenger bag, asymmetric jacket, energetic stride, and a distinctive coral accent. Reappears in each district; her outfit gains small delivery patches as side quests progress. Her position on the map should be visible from the district's main route.
- **Ivo (reception lead), Noor (archive clerk), Hal (systems technician), Ada (night caretaker), Vale (executive liaison):** Each has a different silhouette, posture, desk/prop language, and reaction set; see the cast table in `levels.md`. Dialogue portraits use the chibi set and the portrait cue map in `levels.md`; bespoke full illustrations are optional.
- **HUD:** Small quest objective and seal count at the top; map/quest journal on demand; contextual interaction prompt next to a person or device. Avoid a permanent wide side panel that shrinks the world.
- **Dialogue:** A clean lower-screen panel with portrait, speaker name, concise text, and clear continue/skip controls. The dialogue panel must not cover the object the NPC is discussing when a task begins.
- **Keyboard teaching overlay:** A focused inset showing the **physical key position**, hold order, emitted output, and task effect as four separate pieces of information. Keycaps are modern UI components, not ASCII art. Show only the relevant keys; the full layout diagram is the [Layout help](#layout-help) screen.
- **Terminal and editor scenes:** Widen the code/log/form to a comfortable reading column and dim the world behind it without hiding context. Use syntax color sparingly, a strong cursor shape, visible selection, line/word targets, and a clear success animation. Keep font size at least 16 CSS pixels by default.
- **Quest states:** Main quests, optional accuracy/puzzle quests, and Mira's speed routes use distinct icons and journal headings. Completion is shown on the map through an environmental change as well as a UI notification.

### Hint grammar
The player is retraining from a normal keyboard to this layout, and already knows Kanata. Whenever a coworker, artifact, sign, or overlay prompt tells the player which keys to press, it bridges from the familiar key to its Kanata gesture in three parts, always in this order:

> **To** *[action in the game]*,
> **you need to press** *[conventional key or shortcut]*.
> **Hint:** *[conventional key]* is *[Kanata gesture]*.

For example:

> To submit the access code, you need to press **Return**.
> Hint: Return is **tap-hold Caps** + **N**.

Rules:

1. **The action** is the effect in the scene, in the speaker's voice ("To file this folder…", "To mark the balance negative…"). It never names a key.
2. **The conventional key** is the output the game observes: Return, Option + Left, `#`, Shift + Tab. This keeps the hint consistent with the feedback panel's "logical output observed" line.
3. **The Kanata gesture** uses Kanata vocabulary, not plain-language timing: **tap** and **tap-hold** for dual-role keys, layer names from the config (`nav`, `numbers-symbols`, `practice`) the first time a layer appears in a quest, and **XX** for keys silenced in `practice`. Hold timings (200 / 220 / 250 ms) belong in the keyboard overlay, not in dialogue.
4. **Multi-key gestures list activation order.** Home-row holds resolve one at a time, so a hint like "tap-hold J (Shift), then tap-hold Caps + W" states the order explicitly.
5. **Home-row modifier hints pick an opposite-hand key.** `tap-hold-tap-keys` types the letter when the next key is on the same hand, so Command + S on D would type `ds`. Choose a target on the other hand, or pair with the mirrored modifier (Control + Shift + R is tap-hold A, then tap-hold J, then R).
6. **When there is no conventional equivalent,** such as the practice toggle or the emergency exit, the gesture *is* the key: "you need to press physical Control + Alt + GUI + V." The hint then explains the Kanata behavior (for example, that home-row holds do not count because the toggle checks `input real`).
7. **Exceptions use the same shape.** "To type an `n` while numbers-symbols is held, you need to press N. Hint: N stays literal on numbers-symbols."
8. **Hints fade by difficulty, not by removing the action.** Standard shows all three lines. Focused shows the action and the conventional key, with the hint on request. Violento shows only the action after a gesture's introduction. The goal is going straight from intent to gesture.

The keyboard teaching overlay shows the same information as keycaps (physical position and hold order) beside the dialogue, so the written hint and the diagram never disagree. Per-level hint lines are in [`levels.md`](../levels.md).

### Layout help
A reference screen that shows the keyboard exactly as `kanata.kbd` configures it, rendered from the layout manifest so it can never drift from the config. It is the "full layout diagram on demand" the teaching overlay promises. It never scores anything and is available everywhere, including inside terminal scenes and Mira's routes (which pause while it is open).

- **Opening and closing:** `?` (Shift + /) opens it; home-row Shift produces `?` on every layer, including `practice`. It is also in the journal, and in the story it lives on Ivo's tablet. Escape (tap Caps) closes it and returns focus to where the player was.
- **Switching layers by keyboard:** the layers are tabs: `base`, `nav`, `numbers-symbols`, `practice`. Left/Right (tap-hold Caps + H / L) moves between them, so the gesture is the same one the player uses to walk. Tab and Shift + Tab also cycle tabs while the screen is open. Tab focus is held inside the screen, and Escape always leaves it. Bare tap-hold Tab still sends the external Homerow shortcut, so the screen relies only on tap Tab.
- **Click-hold a layer key:** pressing and holding the mouse on the drawn Caps or Space keycap shows that layer for as long as the button is held, and releasing returns to the previous tab. This mirrors `layer-while-held`. Keyboard players get the same view by selecting the layer tab instead.
- **Key detail:** selecting any keycap, by click or by moving focus across the drawn keys, shows its tap action, its tap-hold action, its timing, and its practice behavior (normal or XX), in the same wording as the [hint grammar](#hint-grammar).
- **Practice tab:** silenced keys are drawn greyed out and labeled XX; the toggle-out sequence is shown on the tab.
- **Live highlight (best effort):** while the screen is open, each observed event lights the physical key most likely to have produced it, on the matching tab. For example, `ArrowLeft` highlights H on `nav`, and a left Shift key-down highlights F. When an output has two possible sources, such as `1` from tap-hold Space + A or the physical 1 key on `base`, both are shown. The browser cannot see a layer key being held before the next key arrives, so the highlight follows one keypress behind and never claims to detect the active layer.

### Visual rules for level designers
- A hub must be recognizable in one camera view: landmark, two or three visible exits, at least one NPC, and the next useful interaction. Side routes may extend beyond the view, but their entrance must be visible from a traveled path.
- Keep the main path at least two grid cells wide and use furniture, light, and floor patterns to lead the eye. A locked route must visibly show its requirement, nearby objective, and a way back. Never rely on an invisible trigger.
- Use a **hub → short branch → task room → changed return route** shape for each new skill. Put a clean recall task on a later branch rather than immediately repeating the tutorial room.
- Each district needs a main-path loop, one optional shortcut, at least one environmental storytelling find, and a department review space. Orientation and Night Shift each host one Mira route, Records and Systems host two, and the Executive Floor has none (Mira arrives there only for the finale). A speed route should cross known interactions and reward discovering shortcuts, while its score still requires accurate keyboard outputs.
- Distinguish three interaction silhouettes: NPCs occupy open walking cells; terminals glow within furniture; glitches move or animate against the floor. Show an interaction outline when the player is in range.
- When a quest completes, change at least two visible things: for example a door animation and an NPC reaction, or machine lights and a new path. This makes learning progress tangible in the world.
- Keep moving props and particles outside text-editing focus areas. A wrong key should receive a clear local reaction, never an obscuring full-screen effect.
- Concentrate hand-crafted detail in one landmark per district; ordinary task rooms should use a small number of shared modules, open floor, and one strong light or color cue. This keeps new maps affordable and makes routes easier to read.

**Orientation hub reference layout:** Build a roughly 28×18-cell reception floor. Place the arrival elevator near the southwest edge, the garden/skylight in the center, the badge printer to the north, two modifier-training desks on opposite sides, Mira's mailroom along the southeast return path, and the Records exit on the east side. The first Caps movement quest walks a short, unobstructed loop around the garden. Quest 2 brings the player to the printer; its completion opens Mira's speed side quest without drawing the player away from the main route. The east exit becomes available after the department review. At least one shortcut cuts across the garden after a later quest, making a return visit visibly useful.

**Records reference layout:** Build a larger two-screen archive around the circular desk. The first route runs past the repair door and filing cabinets to teach Caps editing; the left branch teaches word and line movement in logs; the upper branch reaches the long report and review chamber. Mira stands by a mail chute on the hub route, and a sliding file wall opens a loop back to her after the archive clerk's quest. A player should be able to see that wall before it opens and remember it when taking the courier route again.

**Systems reference layout:** Build a roughly 38×24-cell service floor centered on a routing machine visible from the elevator. The east branch leads to the payroll ID station, the west branch to alarm glyph terminals, and a glass bridge above the hub leads to the formula room. Use floor conduits to show which machine a terminal affects. Opening the bridge after the first correct number task gives a short return path to Mira's mail chute. The final relay room requires a route through all three branches and visually lights each circuit when its symbol group is mastered.

**Night Shift reference layout:** Build a roughly 34×20-cell collaboration floor with more negative space than prior districts. The entry break room is a safe, well-lit place to explain the practice toggle and recovery. A security vestibule demonstrates silent physical keys in a controlled interaction. The central corridor has paired routes: a visible old route blocked by practice-mode rules and a Caps-driven route through offices. Put the ledger at the north end, with a newly lit service corridor returning to Mira near the break room. Preserve strong edge lighting and character contrast even in the darkest rooms.

**Executive reference layout:** Build a roughly 30×20-cell atrium around the living tree. Three short branches hold final incidents that combine previously taught gestures; the player can choose their order. Each repaired branch changes the atrium and brings earlier coworkers into view; all five (Ivo, Noor, Hal, Ada, Mira) have arrived by the final door. The last door is visible from the entrance and opens after all three accurate repairs. The epilogue uses the same walkable space in its restored state, so the transformation is spatial and visual rather than only a cutscene.

Connect districts through a readable elevator map. The elevator unlocks the next district after its department review and always permits returning to unlocked ones. A district shortcut changes travel time and sight lines, but cannot conceal a required lesson. Every map should have a one-page level sheet with an annotated entrance-to-review route, a Mira route, a backtracking route, and an image of its pre- and post-review state.

### Asset and level handoff
The graphics designer should deliver: one shared office tile/prop atlas; five district palette and material sheets; one landmark kit per district; a master avatar sheet; the recurring NPC sheets; three glitch archetypes; UI keycaps/icons/dialogue frames; reusable lighting masks; and before/after quest-state frames assembled from those assets. Artifacts can share one document close-up frame with different icons and text. Name animations and anchors consistently so the level data can reference them. Validate with one full-resolution Orientation composition and one walkable Records composition built from the shared kit before bulk production. Do not commission a bespoke illustration or unique prop set for each of the 20 quests.

The level designer should deliver per district: tile map, collision map, camera bounds, entrance/exit connections, NPC positions and patrols, interaction footprints, quest triggers, shortcut states, Mira route checkpoints, terminal scene IDs, lighting state changes, and a guided/variation/recall coverage checklist tied to the gesture inventory. Review the walkable map at laptop scale with the keyboard diagram open before declaring a room complete.

Sound should use subtle contemporary ambience—air handling, footsteps on different floor materials, elevator chimes, desk electronics—and short melodic cues for discoveries and seals. Silence should be meaningful in Night Shift. Keep music and effects independently adjustable and off by default; do not copy melodies or sound effects from reference games or shows.

**Example ten-minute session:** The player enters Records, spots Mira beside a blinking mail chute, and accepts a courier side quest. Their first clean delivery records a baseline and earns a courier patch. They then speak to Noor, the archive clerk, navigate a corrupted log with Caps+B/W, repair an address, and earn access to a side corridor. On the way back, they try Mira's route again using the newly opened corridor; a faster clean delivery earns an optional courier medal. They can leave the race unfinished and continue the main story at any point.

## Player experience
- One physical gesture at a time, then a realistic engineering task that reuses it.
- Guided room → changed-context room → no-prompt recall room for each new group.
- Main quests take 2–5 minutes inside the larger explorable world; short NPC side quests can be replayed at any time.
- Feedback always distinguishes **physical gesture shown**, **logical output observed**, and **effect in the game**. Browser output cannot prove which physical key produced it.
- Accuracy and retention determine campaign progress and mastery. Story quests are untimed. Speed is a repeatable **side-quest activity available during the adventure**, with harder versions appearing as new districts and gestures open.
- No long-run death or lost progress; mistakes reset a room or reduce only a bonus.

## The four-layer model

| Layer | Entry and exit | What it teaches | Constraint |
| --- | --- | --- | --- |
| Base / normal | Default at Kanata startup; return from practice with physical Control+Alt+GUI+V | Ordinary typing, tap/hold keys, home-row modifiers, bare Tab/Space/Caps behavior, right-Command navigation, native editing and shortcuts | This is a **full act**, not an unscored fallback. |
| Caps navigation | Hold Caps; release Caps to return to the prior typing layer; tap Caps for Escape | Character, word, line, page, document movement; selection; editing and Return | Caps+key gestures are distinct from plain keys. |
| Numbers/symbols | Hold bare Space about 220 ms; release to return; tap Space for a space | All 11 home-row number/minus outputs and all 12 top-row symbol outputs | Every mapped output receives a teaching room and recall check. |
| Violento practice | Toggle with physical Control+Alt+GUI+V; toggle again to leave | Rebuild base, navigation, and numbers/symbols using allowed keys while physical legacy keys are silent | The app cannot enable, detect, or disable this OS-level layer. Player confirmation is explicit. |

The game should represent **which layer is active in its own scene** and **which Kanata layer the player says is active** separately. Holding Caps or Space temporarily changes the emitted event; a browser generally cannot observe those hold states directly. It should never claim physical-origin detection from `KeyboardEvent.code`.

## Complete gesture inventory
The layout manifest must enumerate every row below as an individual or grouped skill with lesson IDs, an observed-output rule, and a verification confidence (`output-observed`, `player-confirmed`, or `external-only`). Plain unmapped alphanumeric keys can share a base typing lesson; mapped keys and exceptions cannot disappear into a generic “other” bucket.

### A. Base / normal layer

| ID | Physical gesture | Output and rule | Game treatment |
| --- | --- | --- | --- |
| B01 | Plain letter, digit, and punctuation taps, including mapped `B W 0 4 U T M X N V R ,` | Ordinary characters unless a documented chord/layer changes them | Type code, ticket text, and IDs; explicitly contrast plain keys with their Caps or Space variants. |
| B02 | Tap A/S/D/F and J/K/L/; | Literal `a s d f j k l ;` | Accurate home-row typing, including rolls that should remain letters. |
| B03 | Hold A/S/D/F about 200 ms | Left Control / Option / Command / Shift | Teach each hold separately, then safe combined shortcuts and Shift capitals. |
| B04 | Hold J/K/L/; about 200 ms | Right Shift / Command / Option / Control | Mirror B03; require both sides in separate rooms. |
| B05 | Hold home-row modifier, then press an opposite-hand key | Shortcut; same-hand rolls tend to type letters | Practice deliberate hold timing, release order, and opposite-hand choice. For multi-modifier chords, activate holds one at a time. |
| B06 | Tap Caps / hold Caps | Escape / navigation | Teach tap-versus-hold and transition back to typing. |
| B07 | Tap Space / hold bare Space about 220 ms | Space / numbers-symbols layer | Teach timing, no stray inserted space, and normal typing after release. |
| B08 | Hold a modifier **before** pressing Space | Ordinary modified-Space shortcut | Contrast with B07; do not require OS-reserved shortcuts to be browser-verifiable. |
| B09 | Tap Tab / hold bare Tab about 250 ms | Tab / one Shift+Command+Space Homerow activation | Teach the hold, but mark the external Homerow effect player-confirmed; include a safe explanation if that app is absent. |
| B10 | Hold a modifier before Tab | Ordinary modified-Tab shortcut | Show the exception to B09, with OS-reserved cases demonstrated rather than auto-scored. |
| B11 | Hold Right Command + H/J/K/L | Left/Down/Up/Right navigation; other Right Command shortcuts retain their normal meaning | Alternative navigation drill and shortcut-preservation example. |
| B12 | Physical editing/movement/modifier keys in base | Native Backspace, Delete, Return, Escape, arrows, Home/End, Page Up/Down, and modifiers | Baseline comparison before practice mode. |
| B13 | Control+Shift+R | Reload Kanata configuration; plain Control+R remains available | Operations card, not an in-browser scored task; avoid accidental reload in play. |
| B14 | Physical Control+Alt+GUI+V | Toggle Violento practice; ordinary V still types `v` | Guided manual transition and return exercise. |
| B15 | Microsoft keyboard physical Alt/Windows positions | Device-specific Alt→Command, Windows→Option; Right Alt acts as Right Command and navigation | Setup variant with physical diagram; MacBook diagram remains the default. |

**Timing rule:** the home-row hold decision uses 200 ms and same-hand protection; Space's hold is 220 ms; bare Tab's hold is 250 ms. The main campaign never scores speed; its goal is reliable, deliberate muscle memory. It should teach ordinary key taps between hold exercises so the player does not learn to type every letter as a shortcut.

### B. Caps navigation layer
All gestures below mean **hold Caps while pressing the second key**. Releasing Caps returns to ordinary typing. These are macOS outputs; the game simulates corresponding editor behavior where practical.

| ID | Key with Caps | Output / meaning | Required check |
| --- | --- | --- | --- |
| N01–N04 | H / J / K / L | Left / Down / Up / Right | Four directions, including repeated movement and release-to-type. |
| N05–N06 | B / W | Option+Left / Option+Right | Previous / next word in a code-like line. |
| N07–N08 | 0 / 4 | Command+Left / Command+Right | Start / end of line. The `$` gesture also reaches line end when Shift+4 is used. |
| N09–N10 | U / D | Page Up / Page Down | Traverse a long document; show viewport movement. |
| N11–N12 | T / G | Command+Up / Command+Down | Start / end of document. |
| N13–N14 | M / Space | Backspace / Backspace | Both paths practiced independently. |
| N15–N16 | comma / X | Forward Delete / Control+D | Both forward-delete routes; explain the different emitted shortcuts. |
| N17 | N | Return | Submit/open a selected item, then return to typing. |
| N18 | `[` | Escape | Cancel a modal while Caps remains held; tap Caps is the other Escape route. |
| N19 | Shift + supported navigation gesture | Selection where the destination supports it | Teach Shift holds on F/J or physical Shift in base. Establish the Shift hold **before** pressing Caps: once Caps is held, F types a literal `f` (N20) and J is Down. Note Caps+4 consumes Shift and goes to plain line end. |
| N20 | A / S / F while Caps is held | Literal `a` / `s` / `f` | Explicit exception: these do not become nav commands. |
| N21 | Right Command + H/J/K/L | Same four arrow directions | Alternative path; other Caps-only extended mappings are **not** granted by Right Command. |

The source has `D` as page down and `G` as document end in the Caps layer; the table above covers both. Caps+`[` is Escape even though `[` has another base-layer behavior outside this scope. Levels must check that plain `B W 0 4 U D T G M X N ,` continue to type or behave normally after Caps release.

### C. Held-Space numbers and symbols layer
Enter by holding **bare** Space until the layer activates (about 220 ms), then tap the listed physical key. Teach and assess every output, including punctuation that looks similar to a base-layer key. The displayed keyboard should show physical **key positions**, not just characters, and should show when Space is released.

| ID | Physical keys with Space held | Outputs in order | Required check |
| --- | --- | --- | --- |
| S01–S10 | A S D F G H J K L ; | `1 2 3 4 5 6 7 8 9 0` | Each digit appears in a guided mini-task and later in a shuffled code/ID recall task. |
| S11 | apostrophe | `-` | Negative number, range, or CLI flag task. |
| S12–S17 | Q W E R T Y | `! @ # $ % ^` | Each symbol appears in a guided mini-task and later in a shuffled expression recall task. |
| S18–S23 | U I O P [ ] | `& * ( ) _ +` | Same individual coverage, with brackets/parentheses visually distinguished. |
| S24 | N and M while Space is held | Literal `n` and `m` | Teach that these remain letters, not digits or editing. |
| S25 | Caps while Space is held; Tab while Space is held | Caps keeps navigation; Tab keeps its tap/hold behavior | One layer-interaction drill; external Tab hold is player-confirmed. |
| S26 | Modifier-first Space | Space stays a normal modified-Space shortcut when a modifier was already held | Demonstrate the exception without relying on OS-reserved shortcuts for score. |

The symbols correspond to shifted U.S. number-row outputs. The game must teach the **output** and **key position** for all 23 mapped number/minus/symbol keys, then test the entire set in mixed prompts. It must not silently substitute physical number-row input as proof of held-Space mastery.

### D. Violento practice layer
The current `practice` layer retains home-row modifier holds, Caps navigation, held-Space numbers/symbols, ordinary letters, Tab, and the V toggle. It silences original physical Shift, Control, Alt/Option, Command/Windows, Backspace, Forward Delete, Return, Escape, arrows, Home/End, Page Up/Down, and number-row digits 1–0. The learning goal is to complete **base + navigation + number/symbol tasks again under those constraints**, not just to flip a mode switch. The physical Right Command route in B11 is unavailable here because that key is silenced; use Caps navigation. Holding home-row K emits Right Command as a modifier but does not activate the separate physical `@rnav` alias.

| ID | Skill | Required experience |
| --- | --- | --- |
| V01 | Enter and leave | Show the physical Control+Alt+GUI+V sequence, wait for release, ask for player confirmation, and teach the same sequence to exit. |
| V02 | Verify likely state manually | Ask the player to try physical Shift with a letter or physical Backspace in a safe text box; explain that even this is a self-check, not app-level proof. |
| V03 | Replace physical modifiers | Complete Shift, Command, Option, and Control exercises with home-row holds on both sides. |
| V04 | Replace physical navigation/editing | Complete cursor, word, line, page, document, Return, Escape, Backspace, and forward-delete tasks with Caps gestures. |
| V05 | Use held-Space numbers/symbols | Complete a mixed 23-output task while practice mode is player-confirmed. |
| V06 | Recovery | Always expose the toggle-out sequence as the normal way back to base. Physical Left Control+Space+Escape is **not** a layer toggle: it is Kanata's built-in emergency exit, which quits the Kanata process and stops all remapping. On this machine the service does not restart it after that exit, so the player restarts Kanata (or reboots) to get any layer back. Present it only as a last resort, with that consequence and the restart step stated, and confirm the behavior on the target machine before calling it guaranteed. |

**Number-row coverage in the current keymap:** physical digits `1`–`0` are in `defsrc` and silenced in `practice`, which also blocks their shifted symbols `! @ # $ % ^ & * ( )` from the number row. The physical grave, minus, and equals keys are still absent from `defsrc`, and `process-unmapped-keys yes` passes them through, so in practice `-`, `=`, and (with a home-row Shift) `_` and `+` can still be typed without held Space. Independently, the browser cannot distinguish a physical `1` from Space+A when both emit `1`, and it cannot detect the practice layer at all. V05 evidence therefore stays player-confirmed. A separate opt-in Kanata change could also silence minus/equals **only in practice**, preserving base and held-Space outputs. Design and test that change separately; do not modify the live config as part of this game spec. Never require it to finish the campaign.

## Adventure map and twenty main quests
The five connected districts are **Orientation**, **Records**, **Systems**, **Night Shift**, and **Executive Floor**. Each has an NPC hub, 3–5 main quest sites, a department review, optional side paths, and a return shortcut. The player can roam among unlocked districts and revisit old quests. The table gives the teaching order, but quests should appear as places and characters in the world rather than a numbered menu. Each main quest contains a guided use, a variation, and a later recall check; the curriculum still covers the complete gesture inventory above.

| Quest | Location / story beat | New focus | Completion and coverage |
| --- | --- | --- | --- |
| 1 | Orientation — The Lobby | Caps H/J/K/L, Caps tap | Walk to four desks and open the first route (B06, N01–N04). |
| 2 | Orientation — Badge Printer | Base typing and home-row taps | Type ordinary letters, digits, punctuation, and mapped-key taps (B01–B02). |
| 3 | Orientation — The Clock | Tap/hold timing for Space and Tab | Distinguish Space/Tab taps from holds and modifier-first exceptions (B07–B10). |
| 4 | Orientation — Left Desk | A/S/D/F holds | Use four left modifiers, then type the same letters normally (B03, B05). |
| 5 | Orientation — Right Desk | J/K/L/; holds | Mirror four modifier exercises and demonstrate opposite-hand timing (B04–B05). |
| 6 | Orientation — The Other Keyboard | Right Command nav, native keys, hardware variant | B11–B12 with N21 (Right Command arrows) and optional Microsoft physical-position tutorial B15; earn the Orientation seal. |
| 7 | Records — The Door That Answers | Caps N, M, Space, comma, X, `[` | Submit, delete both ways, and cancel (N13–N18). |
| 8 | Records — Filing Drift | Caps B/W and literal B/W after release | Word navigation in a code excerpt (N05–N06). |
| 9 | Records — The Margins | Caps 0/4 and `$` | Reach both line endpoints and edit (N07–N08). |
| 10 | Records — The Long Report | Caps U/D/T/G | Page and document jumps (N09–N12). |
| 11 | Records — Marked for Review | Shift selections, Caps exceptions | Select text, test Caps+4 behavior, and type A/S/F under Caps (N19–N20; revisit N21, introduced in level 06); earn the Records seal. |
| 12 | Systems — Payroll IDs | Space+A–; | Learn all ten digits, then enter shuffled IDs (S01–S10). |
| 13 | Systems — Negative Balance | Space+apostrophe, N/M exceptions | Enter `-` and distinguish N/M from editing (S11, S24). |
| 14 | Systems — Alarm Glyphs | Space+Q/W/E/R/T/Y | Learn and shuffle `! @ # $ % ^` (S12–S17). |
| 15 | Systems — Formula Room | Space+U/I/O/P/[/] | Learn and shuffle `& * ( ) _ +` (S18–S23). |
| 16 | Systems — Crossed Wires | Space/Caps/Tab interaction and modifier-first Space | Layer puzzles and mixed 23-output recall (S25–S26); earn the Systems seal. |
| 17 | Night Shift — Lockdown Drill | Enter/exit practice; silent physical keys | Player-confirmed toggle, safe self-check, reload card, and recovery (B13–B14, V01–V02, V06). |
| 18 | Night Shift — No Old Keys | Home-row modifiers and Caps under practice | Revisit all eight modifier holds and all Caps categories (V03–V04). |
| 19 | Night Shift — The Ledger | Numbers and symbols under practice | Mixed all-output task with the number-row caveat visible (V05); earn the Night seal. |
| 20 | Executive Floor — Exit Interview | All layers | Resolve three code-like incidents, choose a route, unlock the epilogue, and earn the final Department of Motion seal. |

**Operations cards:** B13 (reload), B14 (toggle), and V06 (recovery) are taught in setup and revisited before practice. They are never surprise timed challenges. The Microsoft variant and external Homerow effect are self-confirmed and cannot block the main story if that hardware/app is absent. Systems quests record per-output coverage; a guessed short code cannot award mastery for untouched symbols.

### Side quests inside the adventure
Side quests are discoverable NPC requests and map sites, not a separate post-game list. They can be accepted, paused, and revisited between main quests. Each district contains one small accuracy/puzzle side quest and optional lore artifacts. A recurring courier NPC named **Mira** offers the speed routes in the first four districts (see the table below). The journal labels Mira's quests “Optional speed” and shows their skill prerequisites. Clearing them yields courier patches, room decorations, and snippets of Mira's story; no clearance seal, key skill, or ending depends on them.

| First available | Mira's in-world request | Skills used | Escalation |
| --- | --- | --- | --- |
| After quest 2, in the Orientation mailroom | **Morning Mail**: sort short labels for three desks | Base typing and clean taps | Learn the route with no clock, then try to beat a clean run by about 5%. |
| After quest 7, in the Records corridor | **Courier Loop**: reach desks and correct delivery slips | Caps arrows, Return, Backspace | Longer route and about 7% improvement. |
| After quest 11, in the Records archive | **Lost Folios**: traverse a log to find three addresses | Word, line, page, and document jumps | Mixed navigation and about 10% improvement. |
| After quest 13, in the Systems mail chute | **Payroll Run**: enter changing IDs and signed values | Held-Space digits and minus | Shuffled prompts and about 12% improvement. |
| After quest 16, in the Systems relay room | **Glyph Dispatch**: enter changing expressions and repair a typo | All 23 held-Space outputs plus Caps edits | Full symbol set and about 15% improvement. |
| After quest 18, on the Night Shift route | **Lights-Out Delivery**: finish an incident route in player-confirmed practice | Base, Caps, held Space, home-row modifiers | Mixed skills and a personal-best target. |

Each speed quest's **first clean run establishes a baseline** and earns its story reward; it has no countdown, and the UI says that it records the run's duration as a baseline. A later attempt displays a clearly optional target based on the player's clean baseline. Repeated clean runs can refine the baseline, but three setup runs are never required before trying for speed. A medal requires every task-critical output to be correct, at least 95% correct actions overall, and accuracy at least as high as the baseline run. Faster runs with extra errors do not count. Targets are personal and adjustable; they are not progression gates. The player may replay old courier routes after gaining later skills, discovering faster routes through the map as well as faster gestures.

## Difficulty, scoring, and awards

| Difficulty | Guidance | Pressure | Who it serves |
| --- | --- | --- | --- |
| Standard | Physical key diagram, explicit layer cue, gesture preview, unlimited hints | Untimed | First pass through **all** four layers. |
| Focused | Hints on request; mixed key order and fewer cues | Untimed | Recall and transfer. |
| Violento | Hidden prompts after introduction, player-confirmed Kanata practice checklist, mixed-layer incidents | Untimed in story; optional courier races remain available in the world | Deliberate mastery of the same full curriculum. |

Difficulty is independent of the actual Kanata practice toggle. Offer a visible “Practice layer: player-confirmed / unconfirmed” state; never auto-detect it. Campaign stars measure learning only: one for completing the task, two for a clean run, and three for a clean changed-context recall run without hints. No campaign star depends on elapsed time or action count. A clean run means every task-critical output is correct and at least 95% of all actions are correct; the UI shows which errors count. Core mastery requires clean success across distinct rooms, never a speed target. Show per-skill “introduced / practiced / reliable” with the exact evidence required: e.g., each symbol must succeed in a guided room and an unseen mixed room. Avoid streak loss and global leaderboards.

Awards should reflect coverage: **Desk Walker** (all four arrows), **Mirror Hands** (all eight home-row modifier holds), **Records Clerk** (all Caps navigation categories), **Glyph Accountant** (all 23 held-Space outputs), **After Hours** (practice-layer review), and **Department of Motion** (full campaign). Optional courier medals belong only to Mira’s in-world speed side quests; they do not affect core badges. Office artifacts and dry corporate memos are story collectibles without gameplay advantage. An optional daily shift draws three tasks only from already introduced skills.

## Browser behavior and accessibility
Plain HTML, CSS, and JavaScript, static assets, no backend. Use a deterministic level/gesture schema, an input interpreter separate from level rules, a small state machine, Canvas 2D for the layered sprite world, DOM/CSS for crisp dialogue, editor scenes and keyboard diagrams, and `localStorage` for progress, settings, and best scores. The world renderer should use the style bible's draw order (STYLE_BIBLE §6): floor, rear walls and floor-height markings, rear props, contact shadows, actors, front props/occluders, and local light accents, so characters can move convincingly through rooms. The level schema should reference inventory IDs so coverage can be checked automatically. Support a later JSON export/import.

Browser events report the **resulting** key/modifier state after Kanata and the OS; they generally do not reveal the originating physical key or held layer. Some Command, Control, Tab, Space, and global launcher shortcuts may be intercepted by macOS or the browser. Use safe in-game simulations where possible, player-confirmed demonstrations for external-only gestures, and explicit confidence labels in scoring. Do not pretend a missing event means failure for an OS-reserved shortcut. Do not try to modify the live Kanata config from the webpage. Scope `preventDefault` to an active play surface and keep a visible keyboard-accessible exit.

Offer a setup screen for MacBook versus Microsoft keyboard, a calibration exercise for Caps+H, Caps+N, Space+A, Space+Q, and a home-row Shift hold, plus the practice toggle-out instructions. Include the emergency sequence only after its runtime behavior has been verified. Show physical positions and resulting characters in separate diagram modes. Keep story levels untimed, focus visible, a screen-reader-readable objective, reduced motion, adjustable contrast, readable fonts, and sound off by default. Do not trap Tab; for Tab lessons, provide a clearly announced practice region and an escape route. Use original CSS/2D art; do not copy existing show or game assets.

## Implementation slices for OpenSpec
1. **Vertical slice:** setup/calibration, a walkable Orientation hub, inventory manifest, quests 1–3, one NPC dialogue flow, the Morning Mail speed side quest, Standard mode, local progress, physical-key diagrams, the Layout help screen, and confidence-aware input feedback.
2. **Complete curriculum:** quests 4–16, Records and Systems maps, all 23 held-Space outputs, all Caps categories, base-layer exceptions, Focused mode, badges, per-gesture coverage reporting, and their discoverable side quests.
3. **Practice and finale:** Night Shift and Executive maps, quests 17–20, player-confirmed Violento mode, recovery guidance, mixed reviews, full-campaign awards, and the last courier side quest.
4. **Optional separate keymap work:** the practice layer already silences physical digits 1–0. Propose and validate a minus/equals block in the practice layer only if the user chooses to change the live configuration later.

### Acceptance criteria for the complete game
1. Every B, N, S, and V inventory row is linked to at least one lesson and one assessment or explicitly marked as player-confirmed/external-only; the manifest coverage check reports no unmapped row.
2. All ten digits, minus, and twelve shifted symbols are individually introduced and later recalled in a different order; mastery cannot be awarded from a subset.
3. The player practices all eight home-row modifier holds, all Caps navigation/editing outputs, Right Command's four-direction alternative, tap/hold transitions for Caps/Space/Tab, and the practice-layer restrictions and exit.
4. A player can explore connected district maps, talk to NPCs, solve terminal puzzles, revisit earlier areas, track main and side quests, and earn clearance seals through accurate department reviews. Story quests remain untimed in every difficulty; stars, mastery, badges, and the ending depend on accuracy and recall, never speed. Optional NPC speed side quests appear throughout the adventure and reward faster **clean** runs only; their task complexity grows with newly learned gestures.
5. The UI distinguishes observed output from self-confirmed physical gesture and never claims to detect Kanata practice state or physical number-row use.
6. The game describes the practice layer's number-row coverage honestly (digits and their shifted symbols blocked; minus/equals still pass through) and works with the unchanged current config.
7. No Swedish-specific lesson, award, requirement, or setup blocker appears.
8. Progress and best scores survive reload, can be reset, and are not needed for basic offline play.
9. At 1366×768 and 1920×1080, the player, NPCs, interactables, exits, and walkable paths are readable without labels. Key diagrams and terminal text remain legible at both sizes, including with the larger-text setting.
10. The Orientation and Records art handoff includes a full-size gameplay composition, directional sprite animations, tile/prop atlases, an annotated collision/route map, and visibly different before/after quest states. The remaining three districts follow the same handoff format.
11. The shipped visual style follows the approved art direction in `art-direction/STYLE_BIBLE.md`: clean pixel sprites and crisp UI, with distinct silhouettes, palettes, landmarks, and lighting for all five districts. It reuses a shared tile/prop kit and does not rely on dense per-room art, CRT filters, tiny sprites, or an ASCII-rendered world.

## OpenSpec starting decisions
- Treat this document and the layout manifest (once checked in) as the curriculum source of truth; `levels.md` owns story and per-level detail, and `art-direction/` owns visual style.
- Build the vertical slice first, but reserve level IDs and inventory coverage for the complete campaign.
- Keep Kanata config changes in a separate proposal from the browser game.
- Validate the visual direction with a full-size Orientation gameplay composition and a walkable Records room before producing all five districts; preserve the original office mystery setting and readable keyboard diagrams.
