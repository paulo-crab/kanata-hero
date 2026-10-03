# Kanata Hero game contracts (level 1 build)

Status: group 1 of OpenSpec change `openspec/changes/build-level-one`. Four teams build against this file in parallel: **engine** (A), **input** (B), **runtime** (C), **ui** (D). Tests and tools are team F. Changing a signature or shape here needs the producer; report drift, do not patch around it.

Sources read for the shapes: `design/levels/orientation/{district,map}.json`, `levels/01-the-lobby.json`, `design/levels/{world,gesture-inventory}.json`, `design/layout/layout-manifest.json`, the atlas JSON files under `art-direction/`, `design/ui-key-bindings.md`, `art-direction/ui-kit/COMPONENTS.md`.

## 0. Conventions

- Native ES modules, no bundler. Each module folder exports only through its `index.js`. Other modules import `../engine/index.js` etc., never deep paths. `src/shared/` is real code (bus, clock, errors, layout constants) owned by this contract.
- Naming: files `kebab-case.js`; classes `PascalCase`; functions and fields `camelCase`; constants `UPPER_SNAKE`; bus topics `domain:name` (lowercase, hyphens). Data ids stay exactly as in the data (`o01-popup`, `orientation-01`, `g.turnstile`).
- Coordinates: cell `[x, y]` (16 px cells, origin top-left); pixel positions are `{x, y}` in map pixels; the feet anchor of a person in a cell is `(x*16+8, y*16+16)`.
- Determinism: no `Date.now()`, no `Math.random()`, no `performance.now()` outside `RealClock`. Every time source is a `Clock`. Evidence never stores durations.
- Paths: the game is served from the repo root. Data and art URLs are root-absolute (`/design/levels/...`). `GameData` and `AtlasSet` loaders take a `fetchFn` and a `baseUrl` so tests can load from disk.
- Error handling: any failed load, parse or shape check throws `DataLoadError` (section 2.3) naming the file. The runtime catches it and enters the `error` scene; nothing else swallows it. Handler errors on the bus are re-emitted as `bus:error`, never thrown into the emitter.
- Audio: no `Audio`, `AudioContext`, `<audio>` or permission request anywhere.

## 1. Folder ownership

| Path | Owner | Contents |
| --- | --- | --- |
| `game/CONTRACTS.md`, `game/src/shared/**`, `game/index.html`, `game/package.json`, `game/README.md`, `game/src/main.js` | contracts (group 1, then producer) | this file, bus, clocks, errors, layout constants, boot |
| `game/src/engine/**` | A | loader, atlas, animation, renderer, camera, collision, movement, actors, game loop |
| `game/src/input/**` | B | interpreter, bindings, calibration, layout manifest consumer, hint gate |
| `game/src/runtime/**` | C | scene machine, scenes, rules, dialogue, evidence, progress |
| `game/src/ui/**`, `game/css/**` | D | DOM components and styles |
| `game/tests/**`, `game/tools/**` | F | tests, harness, scenario scripts, `serve.py` |

Each team's tests live in `game/tests/<module>/`. A module may import `shared` and the public `index.js` of modules listed under "Depends on". Dependency order: `shared` <- `engine`, `input` <- `runtime` <- `ui` (ui consumes runtime view-models over the bus only, it imports nothing from runtime).

## 2. Shared (`src/shared/`, implemented)

### 2.1 Event bus (`bus.js`)

```js
export class EventBus {
  /** @param {string} topic exact topic or '*' for all  @returns {() => void} unsubscribe */
  on(topic, handler) {}
  once(topic, handler) {}          // returns unsubscribe
  off(topic, handler) {}
  /** Synchronous, FIFO. An emit made inside a handler is queued and delivered after the current delivery finishes. */
  emit(topic, payload) {}
  /** Handler for '*' receives (topic, payload); others receive (payload, topic). */
}
```
A throwing handler is caught, and `bus:error` `{topic, error}` is emitted. There is one bus per game, created in `main.js` and passed to every module constructor as `bus`.

### 2.2 Clock and fake-clock hooks (`clock.js`)

```js
/** @typedef {{ now(): number, setTimer(ms:number, fn:()=>void): number, clearTimer(id:number): void }} Clock */
export class RealClock {}          // performance.now, window timers
export class FakeClock {
  constructor(startMs = 0) {}
  now() {}
  advance(ms) {}                   // moves time, fires due timers in order (ties: creation order)
  set(ms) {}                       // jump forward, fires due timers
  pending() {}                     // number of timers waiting
}
```
Fake-clock hooks used everywhere: `GameLoop.tick(nowMs)` (engine) and `GameLoop.advance(ms)` run whole fixed steps; `KeyInterpreter` stamps `t = clock.now()`; the scene machine and rule runtime never read time. A scenario test: `clock.advance(n * STEP_MS)` plus `input.handleKeyEvent(...)` is the whole driver.

### 2.3 Errors (`errors.js`)

```js
export class DataLoadError extends Error {
  /** @param {{file:string, kind:'missing'|'parse'|'shape'|'unsupported', detail:string}} p */
  constructor(p) {}   // message: `Cannot load ${file}: ${detail}`; fields file, kind, detail
}
```
`file` is the root-absolute path (`/art-direction/kit/orientation-atlas.json`). The error scene view-model (`vm:error`) is `{file, kind, message}`.

### 2.4 Layout constants (`layout.js`)

```js
export const TILE = 16, VIEW_W = 320, VIEW_H = 180;
export const STAGE_W = 1280, STAGE_H = 720;
export const AVATAR_SCREEN = { x: 160, y: 100 };           // feet anchor on screen
export const INSET_STAGE_RECT = { x: 16, y: 412, w: 572, h: 292 };   // keyboard inset at x4
export const STEP_MS = 1000 / 60;                          // fixed simulation step
export const CELL_STEPS = 16;                              // sim steps per cell move (266.7 ms)
export const WALK_FRAME_STEPS = 8;                         // sim steps per walk frame (133 ms)
```

## 3. Engine contract (`src/engine/index.js`)

Engine knows nothing about keys, levels, scenes or the DOM UI. It reads data and draws.

### 3.1 Data and atlas loading

```js
/** @typedef {{district:object, map:object, level:object, world:object, gestureInventory:object, layoutManifest:object}} GameData */
/** Files: /design/levels/orientation/district.json, map.json, levels/01-the-lobby.json,
 *  /design/levels/world.json, gesture-inventory.json, /design/layout/layout-manifest.json */
export async function loadGameData(opts /* {fetchFn?, baseUrl?='/'} */) {}   // -> GameData; throws DataLoadError
export async function loadJson(path, opts) {}                                // -> object; kinds missing|parse
export async function loadAtlasSet(opts /* {fetchFn?, baseUrl?, loadImage?} */) {} // -> AtlasSet
export const ATLAS_FILES = { /* id -> {json, png} root-absolute paths, see src/engine/index.js */ };
```
Atlas ids required for level 1: `kit` (orientation), `engineer`, `ivo`, `mira`, `bgworker_a`, `bgworker_b`, `glitches`, `pace`, `portraits`. `loadAtlasSet` validates the structure it needs (`frame`, `animations` for people; `entries`, `animations`, `landmarks` for kits; `portraits` for portraits) and that every placement `entry`, npc pose and state set named in the map exists; a miss is `kind: 'shape'` naming the atlas or map file. `opts.loadImage(url)` defaults to `new Image()`; tests pass a stub that returns `{width, height}`.

```js
export class AtlasSet {
  image(id) {}                         // PNG bitmap for the atlas id
  kitEntry(name) {}                    // {name, rect, size_px, footprint, collision, layer, y_sort, anchor, contact_shadow?}
  stateSet(name) {}                    // {kind:'state_set', default, states:{[s]:{entries,blocked?}}, play?, ms_per_frame}
  landmark(name) {}                    // {size_px, footprint_origin_px, states:{[s]:{parts,lamps}}}
  animation(name) {}                   // person/glitch/pace animation by full name, e.g. 'ivo_wave_s' -> {atlas, row, frames, ms, mode, px_per_frame?, contact_frames?}
  personAtlas(characterId) {}          // {frame:{w,h}, anchor, animations}
  portrait(key) {}                     // 'ivo_neutral' -> {x,y,w,h}; falls back never: unknown key throws DataLoadError(shape)
  glitch(archetype) {}                 // archetype record + animation names
}
```

### 3.2 Animation

```js
export class AnimationPlayer {
  /** @param {{frames:number, ms:number, mode?:'loop'|'once'|'hold', row:number}} def
   *  @param {{reducedMotion?:boolean}} [opts] */
  constructor(def, opts) {}
  update(dtMs) {}
  get frameIndex() {}          // reducedMotion + loop => 0 always; 'once' holds last frame, done = true
  get done() {}
  reset() {}
}
export function frameForSteps(def, steps) {}   // pure; walk frame index for N sim steps (frameIndex = floor(steps / WALK_FRAME_STEPS) % frames)
```
Defaults from the atlas: idle 2 x 500 ms loop, walk 4 x 133 ms loop (8 px per frame, a cell is two frames), interact 2 x 250 ms once, `ivo_wave_s` loop, `ivo_nod_*` once, `ivo_tablet_flash_*` loop (reduced motion holds its dim frame 0), door and elevator state sets 120 ms per state, lamps 600 ms.

### 3.3 World state, collision, movement, camera

```js
export class World {
  /** @param {GameData} data @param {AtlasSet} atlases */
  constructor(data, atlases) {}
  // placements and state sets
  placementState(id) {}                 // current state name or null
  setPlacementState(id, state) {}       // rebuilds collision for that placement on the same call
  playStateSet(id, sequence /* ['closed','half','open'] */, opts) {}   // timed via update(); emits engine:stateset-done
  // npcs
  setNpcState(npcId, state) {}          // pose from poses_by_state, cell from cells_by_state when present
  npc(npcId) {}                         // {id, character, cell, facing, pose, visible}
  // gates and collision
  openGate(gateId) {}                   // cells become walkable same call; art state follows gate.placement
  isGateOpen(gateId) {}
  isBlocked(x, y) {}                    // map collision + gate state + state-set entries; out of range => true
  // glitch
  spawnGlitch(interactionId) {}         // from level.glitch: archetype, cell
  repairGlitch(interactionId) {}        // plays <archetype>_repaired once then <archetype>_ordinary
  // avatar
  avatar;                               // Avatar
  update(stepMs) {}                     // one fixed step: animations, avatar, npc loops
  /** Drawable snapshot for the renderer (sorted lists by layer). */
  snapshot() {}                         // -> WorldView
  /** Restore from a progress document slice. */
  restore(slice /* {placements, npcs, gates, avatar} */) {}
  serialize() {}                        // -> same slice
}
export class Avatar {
  cell; facing;                         // [x,y], 's'|'n'|'e'|'w'
  get moving() {}
  /** Ask for a one-cell step. Ignored while a step is in progress. Returns 'started'|'blocked'|'busy'. */
  requestStep(dir /* 'n'|'s'|'e'|'w' */) {}
  /** Held-key repeat: while heldDir is set, a new step starts the moment the previous one ends. */
  setHeld(dir /* 'n'|'s'|'e'|'w'|null */) {}
  update() {}                           // advance one sim step; CELL_STEPS per cell; aligns to the grid at the end
  teleport(cell, facing) {}
}
export function computeCamera(feetPx /* {x,y} */, bounds /* district.camera_bounds, cells */) {}
//  -> {x, y} top-left of the 320x180 view in map px: feet at AVATAR_SCREEN, clamped to bounds
```
Movement is grid-stepped: a step takes `CELL_STEPS` sim steps, the avatar moves 1 px per step, walk frames follow `frameForSteps`, and a blocked request turns the avatar to face the direction without moving (idle). Same input script from the same state gives the same cells.

Engine events on the bus (the `World` receives `bus` in its constructor options `{bus}`): `engine:step-complete {cell, facing, dir}`, `engine:blocked {cell, dir}`, `engine:stateset-done {placement, state}`, `engine:glitch-repaired {interaction}`.

### 3.4 Game loop and renderer

```js
export class GameLoop {
  /** @param {{clock:Clock, update:(stepMs:number)=>void, render:()=>void, raf?:Function}} p */
  constructor(p) {}
  start() {}  stop() {}
  tick(nowMs) {}               // accumulate, run whole steps of STEP_MS, then render once. Cap 5 steps per tick.
  advance(ms) {}               // tests: run floor(ms/STEP_MS) steps, no render
  get stepCount() {}
}
export function chooseZoom(winW, winH) {}      // largest integer z>=1 with 320z<=winW && 180z<=winH  (1366x768 -> 4, 1920x1080 -> 6)
export class Renderer {
  /** @param {{canvas:HTMLCanvasElement, atlases:AtlasSet, stageEl?:HTMLElement}} p */
  constructor(p) {}
  resize(winW, winH) {}        // -> {zoom, letterbox:{x,y,w,h}}; sets --world-zoom on the stage element; no state loss
  setReducedMotion(on) {}
  draw(view /* WorldView */, camera /* {x,y} */) {}
}
```
Layer order: `floor, rear_wall, floor_marking, rear_prop, shadow, actor, front_prop, light`, y-sorting within `rear_prop`, `actor`, `front_prop` by anchor y, contact shadows (`#3A4160` outer, `#1C2038` core) under people and glitches, `imageSmoothingEnabled = false`. `WorldView` is `{floor:Draw[], layers:{[layer]:Draw[]}, markers:MarkerDraw[], camera}`; `Draw = {atlas, rect, x, y, anchorY, ySort, shadow?}`; `MarkerDraw = {id, cell, shape:'conversation'|'terminal'|'route'|'glitch', state:'idle'|'reached'}` is data only: the DOM UI draws marker SVGs from `vm:markers` using `worldToStage(cell, camera, zoom)`.

```js
export function worldToStage(pointPx, camera, zoom) {}   // -> {x, y} in the 1280x720 stage
```

## 4. Input contract (`src/input/index.js`)

Input knows nothing about levels or scenes. It converts `KeyboardEvent`s into logical outputs, resolves bindings against a scene-supplied context, runs calibration and gates hints.

### 4.1 Interpreter

```js
/** @typedef {'observed'|'player_confirmed'|'external_only'} Confidence */
/** One interpreted key event. The only thing scenes ever see.
 * @typedef {Object} InterpretedEvent
 * @property {string} output   event.key, except ' ' -> 'Space' and the grave key (code 'Backquote') -> 'Backquote'. e.g. 'ArrowLeft','Enter','Escape','q','?','Backquote'
 * @property {string|null} text  the character a text field would receive ('w','?',' '), else null
 * @property {Confidence} confidence 'observed' for every browser key event; 'player_confirmed' only from playerConfirm()
 * @property {boolean} repeat  event.repeat; scenes ignore repeat for every action (movement uses 'down'/'up' phases)
 * @property {number} t        clock.now() when handled
 * @property {'down'|'up'} phase
 * @property {string} combo    'Alt+ArrowRight' style (modifiers Ctrl, Alt, Meta in that order, Shift omitted) or equal to output
 * @property {{alt:boolean,ctrl:boolean,meta:boolean,shift:boolean}} mods
 * @property {string} code     event.code, kept for diagnostics and the Backquote rule only
 * @property {ActionId|null} action   resolved binding (4.2), null when the output has none in this context
 * @property {'n'|'s'|'e'|'w'|null} dir  for move/choose actions
 */
export function interpretKey(raw /* KeyboardEventLike */, phase, t) {}   // pure, no action yet
export class KeyInterpreter {
  /** @param {{clock:Clock, bus:EventBus, getContext:()=>InputContext, onEvent?:(e:InterpretedEvent)=>void}} p */
  constructor(p) {}
  handleKeyEvent(raw, phase = 'down') {}   // -> InterpretedEvent|null (null: composing, or a key the game ignores)
  attach(target /* EventTarget, default window */) {}   // adds keydown/keyup; calls preventDefault only if getContext().surfaceFocused and the output is claimed by the context; never for Tab or Cmd/Ctrl chords
  detach() {}
  heldDirection() {}                       // last held arrow dir or null, from down/up phases (not from OS repeat)
  playerConfirm(sceneId, choice /* 'did'|'did_not'|'skip' */) {}   // emits input:event with confidence 'player_confirmed'
}
```
Emits `input:event` (the `InterpretedEvent`) for each. No claim is ever made about the physical key or the active layer. `ArrowLeft` from Caps+H or Right Command is the same event.

### 4.2 Bindings (scene-aware)

```js
/** @typedef {'interact'|'continue'|'confirm'|'retry'|'skip'|'back'|'move'|'choose'|'journal'|'hint'|'layoutHelp'} ActionId */
/** The key ownership a scene declares (section 5.2). The scene machine merges the top layer's into the context.
 * @typedef {Object} InputContext
 * @property {string} sceneId
 * @property {boolean} typing        typing scene: only '?' and Backquote are commands, Q/Return/letters are text
 * @property {'interact'|'continue'|'confirm'|'retry'|'text'|'none'} enter   what Enter means
 * @property {'skip'|'back'|'text'|'none'} esc    what Escape means ('none' in the open world)
 * @property {'move'|'choose'|'text'|'none'} arrows
 * @property {boolean} journal       Q opens the journal (world and walk scenes only)
 * @property {boolean} hint          Backquote is the Hint key
 * @property {boolean} layoutHelp    '?' opens Layout help (true everywhere)
 * @property {boolean} surfaceFocused  the play surface or a modal has focus (preventDefault allowed)
 * @property {string[]} consumes     extra outputs the scene reads raw (e.g. ['Escape'] for the popup), still delivered as events
 */
export const BINDINGS = [ /* one row per row of design/ui-key-bindings.md: {id, action, match, outputs, gesture, appearsIn} */ ];
export function resolveAction(interp, ctx) {}   // -> {action, dir}|{action:null,dir:null}
```
Rules: ignore `repeat` and `isComposing`; ignore events with Meta/Ctrl/Alt/Shift except `?`; Q matches `key.toLowerCase()==='q'`; Backquote matches `code === 'Backquote'`; Tab and Space never resolve to an action; `?` and Backquote are never delivered as text to a typing scene (`text: null` for them). The key that opens a layer is consumed by that press (`InterpretedEvent.consumed` is not needed: the machine marks it handled).

### 4.3 Calibration

```js
export const CALIBRATION_STEPS = [
  { id: 'caps-h',     gesture: 'Caps + H', expected: 'ArrowLeft' },
  { id: 'caps-n',     gesture: 'Caps + N', expected: 'Enter' },
  { id: 'space-a',    gesture: 'Space + A', expected: '1' },
  { id: 'space-q',    gesture: 'Space + Q', expected: '!' },
  { id: 'shift-hold', gesture: 'F (home-row Shift), then /', expected: '?' },
];
/** @typedef {'not_started'|'observed'|'skipped'} StepStatus */
/** @typedef {{keyboard:'macbook'|'microsoft', steps:{[id:string]:StepStatus}}} CalibrationResult */
export class Calibration {
  constructor(keyboard = 'macbook') {}
  setKeyboard(kind) {}
  get current() {}                        // step id or null when finished
  observe(ev /* InterpretedEvent */) {}   // -> {stepId, status}|null ; matches ev.output === expected on the current step
  skip(stepId) {}  skipCurrent() {}  skipAll() {}
  result() {}                             // -> CalibrationResult (JSON round-trips through progress)
  static fromResult(result) {}
}
```
Status copy is "Observed output" and "Skipped"; no message says detected, verified or which keys were used. A step left alone when the player moves on becomes `skipped`.

### 4.4 Layout manifest consumer

```js
export class LayoutManifest {
  constructor(json /* design/layout/layout-manifest.json */) {}
  tabs() {}                                // ['base','nav','numbers-symbols','practice']
  variants() {}                            // ['macbook','microsoft']
  keyboard(variant) {}                     // {label, rows}: key ids in row order with width_u, from manifest.keys[].position and keyboards[variant].bottom_row
  keyAt(tab, keyId, variant) {}            // {id, legend, behaviour, tap, hold, silent:boolean, differsFromBase, falls_to}
  keyDetail(tab, keyId, variant) {}        // card text model: label, tap, hold, timing, lessons, verification
  gesture(inventoryId) {}                  // {input, output, verification, lessons, observedEvents}
  sequences() {}                           // toggle-out (violento-toggle), reload-config, emergency-exit {status:'present_unverified'}
  silencedInPractice() {}                  // manifest.practice.silenced_keys
  hasKey(id) {}
}
export function layoutHelpModel(manifest, state /* {tab, variant, selectedKey} */) {}  // -> LayoutHelpViewModel (section 7)
```
Silent keys (`behaviour: 'silent'`, legend `XX`) are marked XX. The emergency exit always carries `unverified: true`.

### 4.5 Hint gate

```js
/** @typedef {{sceneId:string, phase:'guided'|'variation'|'recall', forfeitsStar:boolean}} HintUse */
export class HintGate {
  /** @param {{ difficulty?: 'standard' }} [opts] */
  request({ sceneId, phase }) {}   // -> {needsCard:boolean, card?:{text, confirmKey:'Enter'}}  recall => needsCard true
  confirm() {}                     // -> HintUse (forfeitsStar true for recall) after Return on the card; guided/variation record at once with forfeitsStar false
  cancel() {}                      // Esc on the card: no hint, nothing recorded
  uses() {}                        // HintUse[] this session
}
```
The card text: "Using the hint here forfeits the third star for this scene. Press Return to show the hint, or Esc to keep it." (stored in `HINT_CARD_TEXT`).

## 5. Runtime contract (`src/runtime/index.js`)

Depends on `shared`, `engine` (World, loader types), `input` (event and context shapes, Calibration, HintGate, LayoutManifest). Runtime owns the scene machine, rule runtime, dialogue, evidence, progress. It never touches the DOM; it publishes view-models on the bus.

### 5.1 Scene machine

```js
/** @typedef {'setup'|'calibration'|'arrival'|'hub'|'dialogue'|'walk'|'label'|'form'|'editor'|'layout-help'|'journal'|'controls'|'settings'|'error'} SceneKind */
/** @typedef {Object} Scene
 * @property {string} id           scene id: data id ('o01-popup') or kind name ('hub')
 * @property {SceneKind} kind
 * @property {boolean} modal       true: layers below receive no input and do not update
 * @property {Partial<InputContext>} keys   owned keys (see 5.2)
 * enter(ctx: SceneContext, payload?: object): void
 * handle(ev: InterpretedEvent): boolean      // true = consumed. Scenes read only InterpretedEvent, never raw events
 * update(stepMs: number): void               // only the top non-paused layers
 * exit(): SceneResult|undefined              // {success?:boolean, data?:object}
 * snapshot(): object                         // restored via enter(ctx, {restore})
 * viewModel(): object|null                   // published as vm:<kind-specific> by the machine
 */
/** @typedef {{bus:EventBus, clock:Clock, data:GameData, world:World, rules:RuleRuntime, progress:ProgressStore, input:object, evidence:EvidenceLog}} SceneContext */
export class SceneMachine {
  constructor(ctx /* SceneContext */, factories /* {[SceneKind]: (payload)=>Scene} */) {}
  push(kind, payload) {}      // validates against TRANSITIONS; emits scene:enter
  pop(result) {}              // exit(), restores the scene below via enter(ctx,{restore}), emits scene:exit {id, result}, ui:restore-focus
  replace(kind, payload) {}
  get top() {}  get stack() {}
  handle(ev) {}               // top layer first; a modal layer stops propagation; ev.action layering: popup -> overlay -> scene
  update(stepMs) {}
  inputContext() {}           // merges top.keys with surfaceFocused, for KeyInterpreter.getContext
}
export const TRANSITIONS = {
  setup: ['calibration', 'hub', 'arrival', 'error'],
  calibration: ['arrival', 'hub', 'error'],
  arrival: ['hub', 'dialogue', 'error'],
  hub: ['dialogue', 'walk', 'label', 'form', 'editor', 'layout-help', 'journal', 'controls', 'settings', 'error'],
  dialogue: ['hub', 'walk', 'label', 'form', 'editor', 'layout-help'],   // pops only; may push layout-help
  walk: ['dialogue', 'label', 'form', 'layout-help', 'journal'],
  label: ['layout-help'], form: ['layout-help'], editor: ['layout-help'],
  journal: ['layout-help', 'controls', 'settings'], settings: ['setup'], 'layout-help': [], controls: [], error: [],
};
```
Opening and closing Layout help, journal or Controls from the hub is push/pop: the hub's `snapshot()` (avatar cell, facing, held key cleared, camera, current step, objective) is restored on pop.

### 5.2 Key ownership

| Scene | enter | esc | arrows | journal | hint | typing |
| --- | --- | --- | --- | --- | --- | --- |
| setup, calibration | continue | open the skip confirm card (never skips on its own) | choose | no | no | no |
| arrival | none | none | none | no | no | no |
| hub (open world) | interact | none | move | yes | yes | no |
| dialogue modal | continue | skip | none | no | yes | no |
| dialogue instruction line | (not a layer; the scene below keeps its keys) | | | | | |
| walk | interact (at an interaction) | none | move | yes | yes | no |
| form (popup) | none | text (consumed as observed output `Escape`) | text | no | yes | yes |
| label, editor | text (editor retry: retry when wrong result shows) | back | text | no | yes | yes |
| layout-help | none | back | choose (left/right = tabs) | no | no | no |
| journal | confirm (focused row) | back | choose | toggle (Q closes) | no | no |
| controls, settings | confirm | back | choose | no | no | no |
| error | none | none | none | no | no | no |

### 5.3 Rule runtime

```js
/** @typedef {{type:'step_start'|'reach_cell'|'scene_success'|'dialogue_done'|'interact'|'request'|'state'|'level_complete'|'trigger'|'player_confirm', id?:string, cell?:[number,number]}} Fact */
/** Intents (what the rules ask the rest of the game to do). Emitted on the bus topic 'intent'.
 * @typedef {{type:'say', dialogueId:string, modal:boolean, onRequest?:boolean}
 *  | {type:'setPlacementState', placement:string, state:string}
 *  | {type:'setNpcState', npc:string, state:string}
 *  | {type:'unlockGate', gate:string}
 *  | {type:'spawnGlitch', interaction:string}
 *  | {type:'openScene', kind:SceneKind, sceneId:string}
 *  | {type:'setFlag', flag:string}
 *  | {type:'journalEntry', text:string}
 *  | {type:'completeLevel', level:string}
 *  | {type:'objective', stepId:string, text:string}
 *  | {type:'moveAvatar', path:Array<[number,number]>, facing:string}
 *  | {type:'playStateSet', placement:string, sequence:string[]}} Intent */
export const SUPPORTED_OPS = ['set_state','npc_state','unlock_gate','set_flag','complete_level','start_dialogue','spawn_glitch','journal'];
export function parseCondition(str) {}        // pure; atoms joined by ' & '; any_of:a|b ; count:n:a|b|c ; -> AST
export class RuleRuntime {
  /** Throws DataLoadError(kind 'unsupported', file the level json) when a trigger op is not in SUPPORTED_OPS. */
  constructor({ level, map, district, world, state /* ProgressDoc view */, bus }) {}
  start() {}                                  // fires step_start for the first unfinished step
  notify(fact) {}                             // evaluates step completes_when, dialogue when, trigger when; returns Intent[] (also emitted)
  holds(conditionStr) {}
  get currentStep() {}  get stepsDone() {}
  isVisible(interactionId) {}                 // visible_when: 'level:<id>' and 'npc_state:<npc>=<state>' with trailing '*'
  onRequest(dialogueId) {}                    // Hint key pressed while that line is on screen -> say(on_request line)
}
```
Facts are produced by scenes, the dialogue runtime and the engine bus bridge (`engine:step-complete` -> `reach_cell`). `trigger:<id>` atoms are true after that trigger fired. The level JSON is the only source of step order, dialogue ids and operations.

### 5.4 Dialogue runtime

```js
export class DialogueRuntime {
  constructor({ level, bus, rules }) {}
  open(id) {}             // modal (data `modal`, default true when hint null) pushes a dialogue layer; non-modal shows an instruction line only
  advance() {}  skip() {}       // Return / Esc on a modal conversation; closing emits fact dialogue_done:<id>
  observe(ev) {}          // an instruction line completes when its hint.key is observed (Q, Backquote, ?, Escape...) -> dialogue_done
  current() {}  instruction() {}
}
```
Data fields: `speaker, speaker_kind?, portrait, text, hint {action,key,gesture}|null`. View-model in section 7 (`DialogueViewModel`). Portrait key: `${speaker}_${portrait}`, with Mira's `mira_patchK_` row after `first_delivery`; object speakers (`popup`, `pace_sign`, `form_card`) have no portrait.

### 5.5 Scene kinds for level 01

```js
export class FormScene {}    // o01-popup: steps[].accepts ['Escape']; rejects arrows/Return with feedback[output] naming the observed output
export class WalkScene {}    // o01-loop (legs with markers teal->gold), o01-four-stops (ordered stops, desk glow only), o01-unprompted (position_cue false, popup at ivo_north)
export class LabelScene {}   // o01-desk-label: text equals 'west'; feedback keyed by combo ('Alt+ArrowRight') then output then 'other'
export class EditorScene {}  // o01-fold: initial 'lobb', cursor start, ArrowRight x4 then 'y' after release; instant retry; untimed
```
Each is built from its `terminal_scenes` entry: `new XScene(def, ctx)`. They emit `scene:success {sceneId}`, `scene:progress {sceneId, done, total}`, `scene:feedback {sceneId, observed, line}` and record per action `{correct:boolean, critical:boolean, output}` into `EvidenceLog`. A wrong direction in a walk scene is never blocked: it counts incorrect for the clean-run measure only.

### 5.6 Evidence and stars

```js
/** @typedef {{sceneId:string, phase:'guided'|'variation'|'recall', gestureIds:string[], result:'success'|'incomplete', actions:{total:number,correct:number}, criticalOk:boolean, observed:string[], hintUsed:boolean, hintForfeit:boolean, confidence:Confidence}} SceneEvidence */
export class EvidenceLog {
  record(sceneId, action /* {output, correct, critical} */) {}
  hint(use /* HintUse */) {}
  finish(sceneId, success) {}
  scene(sceneId) {}  all() {}  toJSON() {}  static fromJSON(j) {}
}
export function isClean(ev) {}        // criticalOk && actions.correct / actions.total >= 0.95
export function computeStars(levelId, evidenceMap, levelDef) {}
//  -> {stars:0|1|2|3, reasons:string[]}: 1 complete; 2 all scenes clean; 3 clean AND recall scene clean AND recall hintUsed false
```
Phase of each scene comes from `level.gestures[]`. No durations are stored. A Hint press in a guided or variation scene never changes stars.

### 5.7 Progress

```js
/** @typedef {Object} ProgressDoc  JSON stored under localStorage key PROGRESS_KEY = 'kanata-hero:progress'
 * @property {1} schema
 * @property {string} worldVersion         world.json version, e.g. '0.2'
 * @property {{keyboard:'macbook'|'microsoft', reducedMotion:'system'|'on'|'off', largerText:boolean, highContrast:boolean}} settings
 * @property {{done:boolean, calibration:CalibrationResult|null}} setup
 * @property {string[]} flags              ids from world.json state_ids.flags
 * @property {string[]} levelsDone         ids from state_ids.levels_done
 * @property {string[]} seals  @property {string[]} artifacts  @property {string[]} patches  @property {string[]} miraRoutesCleared
 * @property {{[npcId:string]:string}} npc          current state per npc ('start','post_wave','north','post_nod',...)
 * @property {{[placementId:string]:string}} placements   changed state-set states (e.g. turnstile: 'open')
 * @property {string[]} gatesOpen
 * @property {{[levelId:string]:{currentStepId:string|null, stepsDone:string[], avatar:{cell:[number,number],facing:string}, stars:0|1|2|3, scenes:{[sceneId:string]:SceneEvidence}}}} levels
 * @property {string[]} journal
 * @property {HintUse[]} hintUse
 * @property {{[levelId:string]:{stars:number}}} best
 */
export class ProgressStore {
  /** @param {{storage?:{getItem,setItem,removeItem}, world:object, bus:EventBus}} p  storage undefined or throwing => in-memory */
  constructor(p) {}
  get persistent() {}               // false after any storage throw; UI shows "progress will not be saved" via vm:toast
  load() {}                         // -> ProgressDoc (fresh doc when absent/corrupt); unknown ids dropped; schema mismatch => fresh + toast
  save(doc) {}  update(mutator) {}  // update(draft=>{}) saves and emits progress:saved
  reset() {}                        // after confirmation only
  hasProgress() {}                  // drives the continue prompt
}
```
Ids are validated against `world.json` `state_ids`; `keyboard-macbook` / `keyboard-microsoft`, `setup-done`, `calibration-done` are flags kept in step with `settings` and `setup`. Resume restores step, avatar, npc states, placement states and gates through `World.restore`.

### 5.8 Runtime events and commands on the bus

Emitted: `scene:enter`, `scene:exit`, `scene:success`, `scene:progress`, `scene:feedback`, `intent`, `progress:saved`, `level:complete {level, stars}`, and every `vm:*` topic (section 7). Consumed: `input:event`, `engine:*`, `ui:command` (section 7.3).

## 6. UI contract (`src/ui/index.js`)

UI depends on `shared` only. It renders DOM from view-models and sends commands. It never reads game state, level data or storage. Layout: stage `1280x720` (`#stage`), world canvas inside it, DOM layers by the kit's z tokens. Styles live in `game/css/` and import `/art-direction/ui-kit/tokens.css`; components use `var(--...)` tokens only, 16 px minimum text, no pixel font, focus ring `--focus`.

```js
export function mountUi(root /* HTMLElement */, { bus, assetBase = '/' }) {}   // -> {destroy(), announce(text)}
export class Component { constructor(host, bus) {}  render(vm) {}  destroy() {} }   // vm null hides
export const COMPONENTS = ['keycap','inset','dialogue','hud','prompt','markers','journal','layout-help','setup','calibration','scene-bar','feedback','controls','first-use','settings','toast','hint-card','error','live-region'];
export function insetRect(zoom = 4) {}           // INSET_STAGE_RECT; used by checks to prove avatar and target stay outside
export function rectsOverlap(a, b) {}
```
The live region (`aria-live="polite"`) announces every `vm:announce` and every objective change. Reduced motion, larger text and high contrast are classes on `#stage` (`.rm`, `.large-text`, `.hc`) set from `vm:settings`; reduced motion also follows `prefers-color`/`prefers-reduced-motion`. No audio element is created.

## 7. View-models and UI commands

All view-model topics are `vm:<name>`; payload `null` hides the component. Runtime emits them, UI renders them.

```js
/** @typedef {{key:string, label:string, held?:boolean, dim?:boolean, silent?:boolean, glyph?:string}} KeycapVM  // key 'Enter', label 'Return', glyph '`' */
/** vm:dialogue */
/** @typedef {{id:string, speaker:string, speakerName:string, role?:string, portrait:{key:string, rect:{x,y,w,h}}|null, objectSpeaker:boolean,
 *   text:string, hint:{action:string, key:string, gesture:string}|null,         // "Hint: <gesture>" is rendered from gesture
 *   mode:'conversation'|'instruction', footer:Array<{action:'Continue'|'Skip', key:KeycapVM, gesture:string}>}} DialogueViewModel */
/** vm:hud */
/** @typedef {{title:string, progress:{done:number,total:number}, seals:{count:number,total:5}, chips:Array<{id:'hint'|'journal'|'layout-help', label:string, key:KeycapVM, aria:string}>}} HudViewModel */
/** vm:prompt */
/** @typedef {{kind:'person'|'device', action:string, key:KeycapVM, gesture:string, at:{x:number,y:number} /*stage px*/}} PromptViewModel */
/** vm:markers  (data only; UI draws SVG) */
/** @typedef {{markers:Array<{id:string, shape:'conversation'|'terminal'|'route'|'glitch', state:'idle'|'reached', at:{x,y}}>, floor:Array<{id:string, at:{x,y}, state:'teal'|'gold', shape:'route'}>}} MarkersViewModel */
/** vm:inset  guided and variation only; absent on recall */
/** @typedef {{header:string, layer:string, cells:{position:{keys:KeycapVM[], target:string}, order:Array<{key:KeycapVM, tag:'Hold'|'Tap'}>, output:{key:KeycapVM, name:string}, effect:{text:string}}, firstUse:boolean}} InsetViewModel */
/** vm:journal */
/** @typedef {{groups:Array<{id:'main'|'requests'|'speed', heading:string, rows:Array<{id:string, title:string, state:'active'|'locked'|'done', detail:string, selected:boolean}>}>, detail:{title:string, steps:Array<{text:string, state:'done'|'current'|'todo'}>, keys:Array<{key:KeycapVM, output:string, gesture:string}>, stars:number}|null, seals:number, also:Array<{id:'layout-help'|'settings'|'controls'|'ride-hub', label:string, key?:KeycapVM}>}} JournalViewModel */
/** vm:layout-help  built by input.layoutHelpModel */
/** @typedef {{tab:string, tabs:Array<{id:string,label:string,selected:boolean}>, variant:'macbook'|'microsoft', variants:string[],
 *   keys:Array<{id:string, row:number, x_u:number, width_u:number, legend:string, silent:boolean, selected:boolean, differs:boolean}>,
 *   card:{label:string, lines:string[], verification:'observed'|'player_confirmed'|'external_only'}|null,
 *   toggleOut:{keys:KeycapVM[], text:string}, emergencyExit:{text:string, unverified:true}}} LayoutHelpViewModel */
/** vm:setup  and vm:calibration */
/** @typedef {{keyboard:'macbook'|'microsoft', keyboards:Array<{id,label,selected:boolean}>}} SetupViewModel */
/** @typedef {{steps:Array<{id:string, gesture:string, expected:string, hintLine:string, status:'not_started'|'observed'|'skipped', statusLabel:'Not started'|'Observed output'|'Skipped', current:boolean}>, diagramView:'positions'|'characters', toggleOut:{keys:KeycapVM[], text:string, practice:'unconfirmed'|'player-confirmed'}}} CalibrationViewModel */
/** vm:scene-bar  (form, label, editor: reading column) */
/** @typedef {{kind:'form'|'label'|'editor'|'walk', title:string, prompt:string, field:{text:string, cursor:number, target?:string}|null, nextLetter?:string, leave:{key:KeycapVM, gesture:string}}} SceneBarViewModel */
/** vm:feedback  three separate lines + confidence label */
/** @typedef {{gesture:string|null, observed:string, effect:string, confidence:'observed'|'player_confirmed'|'external_only', confidenceLabel:string}} FeedbackViewModel */
/** vm:hint-card  recall forfeit */
/** @typedef {{text:string, confirm:KeycapVM, cancel:KeycapVM}} HintCardViewModel */
/** vm:controls  vm:settings  vm:toast  vm:announce  vm:error */
/** @typedef {{rows:Array<{action:string, key:KeycapVM, gesture:string, worksOnPractice:boolean}>}} ControlsViewModel */
/** @typedef {{keyboard:string, reducedMotion:'system'|'on'|'off', largerText:boolean, highContrast:boolean, confirmReset:boolean}} SettingsViewModel */
/** @typedef {{text:string, tone:'info'|'warn'}} ToastViewModel */
/** @typedef {{text:string}} AnnounceViewModel */
```
Hint-grammar text always comes from the level data (`hint.action`, `hint.key`, `hint.gesture`), shown action first, then the key, then "Hint: " + gesture. UI never composes gesture claims.

### 7.3 UI commands (`ui:command`)

`{type:'selectKeyboard', id}`, `{type:'continue'}`, `{type:'skip'}`, `{type:'back'}`, `{type:'chooseRow', id}`, `{type:'openLayer', id:'journal'|'layout-help'|'controls'|'settings'}`, `{type:'selectTab', id}`, `{type:'selectVariant', id}`, `{type:'selectKey', id}`, `{type:'playerConfirm', sceneId, choice}`, `{type:'setSetting', key, value}`, `{type:'resetProgress', confirmed:boolean}`, `{type:'rideHub'}`. Mouse alternatives only; each has a keyboard route through bindings.

## 8. Boot (`src/main.js`)

**Headless entry point (added by the producer, 2026-10-02).** `main.js` also exports `createGame({fetchFn, baseUrl, loadImage, clock, storage, headless: true}) -> {bus, clock, data, atlases, world, rules, dialogue, evidence, progress, machine, interpreter, loop, destroy()}`. With `headless: true` it touches no canvas, DOM or `window`, still emits every `vm:*` topic, and is the entry point of `game/tests/e2e`. The browser boot is `createGame` plus the canvas, DOM and listener adapters. Test-visible handles beyond the contract text: `machine.top.id` and `machine.top.kind`, `world.avatar.cell` and `.facing`, `rules.currentStep.id`; the first scene is `setup`.

**Atlas lookups.** An animation or pose name resolves from the atlas `animations` object or its `variants` object (the background workers' phone, coffee and typing idles live under `variants`). Seated worker sets are in separate `*-seated-atlas.json` files and are not needed for level 01.

**Calibration and Return.** On the calibration screen Return settles step 2 (Caps + N) only; it does not also continue. Continue on that screen is the explicit Next control.

`main.js` creates the bus, clock, loads `GameData` and `AtlasSet`, builds `World`, `ProgressStore`, `SceneMachine`, `KeyInterpreter`, mounts the UI, starts `GameLoop`, and routes `DataLoadError` to the `error` scene. In the skeleton it only loads nothing and shows a "skeleton" notice; integration (group 7) fills it.

## 8a. Runtime and engine additions (producer, 2026-10-02)

Additive changes fixed by the first implementations; they are part of the contract.

- `vm:markers` and `vm:prompt` carry `cell: [x, y]` and `at: {x, y}` in map pixels (cell * 16, top-left), not stage pixels; the UI converts with `worldToStage`.
- `ProgressDoc.levels[levelId]` gains `facts: string[]` and `sceneProgress: {[sceneId]: number}` for resume.
- `SceneContext` gains `machine`, `dialogue`, `manifest`, `actions` and `held`; `input` is the input module namespace, injected by `createSession`.
- `World.serialize()` and `World.restore()` use the slice `{placements: {id: state}, npcs: {id: stateName}, gates: [ids], avatar: {cell, facing}, glitches}`.
- `DialogueRuntime` emits `dialogue:open` and `dialogue:closed {id, by}`; `RuleRuntime` emits `rules:step-start` and `rules:step-done`.
- `World` options are `{bus, random, reducedMotion, avatarCharacter, spawn}`; it also exposes `setReducedMotion`, `setMarkers(list)`, `camera()`, `glitch(id)` and `avatarFrame()`. `engine:glitch-repaired` fires when the snap frame starts.
- `createSession` wires machine, rules, dialogue, evidence, progress, world and bus. `session.update(ms)` updates the machine only, so boot must also call `world.update(ms)` and `world.setReducedMotion`.
- A `reach_cell` fact counts only while the step whose walk scene uses that cell is current.

## 9. Worked example: one Escape press through the whole stack

Situation: level 01, step `o01.s.popup`, the welcome popup (scene `o01-popup`, a `form` scene) is open, the player taps Caps. Kanata sends Escape.

1. Browser fires `keydown {key:'Escape', code:'Escape', repeat:false, metaKey:false,...}` on `window`.
2. `KeyInterpreter.handleKeyEvent` calls `interpretKey` -> `{output:'Escape', text:null, confidence:'observed', repeat:false, phase:'down', combo:'Escape', t:clock.now()}`.
3. `getContext()` returns the top scene's keys: `{sceneId:'o01-popup', typing:true, enter:'none', esc:'text', arrows:'text', journal:false, hint:true, layoutHelp:true, surfaceFocused:true, consumes:['Escape']}`. `resolveAction` yields `action:null` (Escape is consumed raw by the form). Because `surfaceFocused` and the output is claimed, `preventDefault()` is called. The event is emitted as `input:event`.
4. `SceneMachine.handle` gives it to the `FormScene`. Step `tap-caps` accepts `Escape`: `EvidenceLog.record('o01-popup', {output:'Escape', correct:true, critical:true})`; the scene emits `vm:feedback {observed:'Escape observed', effect:'Popup closes', confidence:'observed'}` and `scene:success {sceneId:'o01-popup'}`; the machine pops it, restoring the hub (`ui:restore-focus`).
5. `RuleRuntime.notify({type:'scene_success', id:'o01-popup'})`: step `o01.s.popup` completes; trigger `o01.t.popup-closed` fires (`setFlag welcome-popup-closed`, `setNpcState ivo post_wave`); dialogue `o01.d.popup-done` (`when: scene_success:o01-popup`, modal) yields `say`; step `o01.s.keys` starts and queues `o01.d.journal`. Intents are emitted on `intent`.
6. The engine applies `setNpcState` (`World.setNpcState('ivo','post_wave')`: pose `ivo_wave_s`, cell `[12,14]`). `ProgressStore.update` writes flag, npc state and step list.
7. `DialogueRuntime.open('o01.d.popup-done')` pushes a modal dialogue layer; the runtime emits `vm:dialogue` (`mode:'conversation'`, footer Continue Return / Skip Esc), `vm:hud` (progress 1/..), `vm:announce {text:'Objective: Learn the journal key...'}`.
8. UI renders the dialogue panel from `vm:dialogue`, the HUD, and the live region speaks the objective. Next frame the `Renderer` draws Ivo at his post.

## 10. Requirement map

Every Requirement of the four specs, the interface that satisfies it, and where it is tested. Titles are copied exactly from the specs (a test checks this table against the spec files).

| Spec | Requirement | Satisfied by | Verify |
| --- | --- | --- | --- |
| world-runtime | The game loads level data and art as static files | `loadGameData`, `loadAtlasSet`, `DataLoadError`, `vm:error`, `tools/serve.py` | tests/engine loader good and broken fixtures |
| world-runtime | Fixed logical view with integer zoom | `chooseZoom`, `Renderer.resize`, `layout.js` constants, stage `1280x720` | zoom unit test 1366x768 -> 4, 1920x1080 -> 6 |
| world-runtime | Layered rendering in the style-bible order | `Renderer.draw`, `World.snapshot`, `World.setPlacementState` | draw-order and y-sort test |
| world-runtime | Camera follows the avatar inside the bounds | `computeCamera`, `AVATAR_SCREEN` | camera clamp test |
| world-runtime | Per-cell collision from level data | `World.isBlocked`, `World.openGate`, `Avatar.requestStep` | collision determinism test |
| world-runtime | Avatar and character animation follow the atlas contract | `AnimationPlayer`, `frameForSteps`, `Avatar`, `AtlasSet.animation` | frame index tests from real atlas JSON |
| world-runtime | A small scene state machine drives play | `SceneMachine`, `TRANSITIONS`, `Scene` | transition table and Layout help round trip |
| world-runtime | Level rules run from level data only | `RuleRuntime`, `parseCondition`, `SUPPORTED_OPS`, `Intent` | level 01 triggers test, unsupported op fails load |
| world-runtime | Progress persists locally | `ProgressStore`, `ProgressDoc`, `PROGRESS_KEY` | throwing-storage and reload test |
| input-interpretation | The interpreter is independent of level rules | `KeyInterpreter`, `interpretKey`, `InterpretedEvent` (no level imports) | same output from two routes |
| input-interpretation | Observed output is never presented as detected gesture | `Confidence`, `InterpretedEvent.confidence`, `KeyInterpreter.playerConfirm`, `FeedbackViewModel` | no layer or physical-key claim in any text |
| input-interpretation | Decided key bindings | `BINDINGS`, `resolveAction`, `InputContext`, section 5.2 | one test per row of ui-key-bindings.md |
| input-interpretation | Browser behaviour is scoped and escapable | `KeyInterpreter.attach`, `InputContext.surfaceFocused`, scene `back` keys | preventDefault and Tab tests |
| input-interpretation | Calibration proves the setup without claiming detection | `Calibration`, `CALIBRATION_STEPS`, `CalibrationViewModel` | observed, partial skip and full skip scripts |
| input-interpretation | Hint use is recorded | `HintGate`, `HintUse`, `vm:hint-card`, `EvidenceLog.hint` | guided no loss, recall loss after confirm |
| level-one-experience | Setup and calibration come first | `SceneMachine` setup -> calibration -> arrival, `ProgressDoc.setup`, `SetupViewModel` | first and returning visit tests |
| level-one-experience | Arrival from the north-wall elevator | `Intent playStateSet/moveAvatar`, `World.playStateSet`, map spawn `arrival`, dialogue `o01.d.welcome` | scenario test elevator states 120 ms |
| level-one-experience | The hub is walkable and readable | `World`, `computeCamera`, `insetRect`, `INSET_STAGE_RECT` | walk + inset overlap check |
| level-one-experience | Level 01 plays through its steps in order | `RuleRuntime`, `FormScene`, `WalkScene`, `LabelScene`, `DialogueRuntime` | headless level 01 scenario |
| level-one-experience | Level 01 changes the world | triggers `o01.t.route-done`, `World.setPlacementState/openGate/setNpcState`, `vm:journal` | four state changes asserted |
| level-one-experience | Optional glitch repair is harmless and untimed | `EditorScene`, `World.spawnGlitch/repairGlitch`, glitch atlas `_repaired` then `_ordinary` | fold scene success and wrong paths |
| level-one-experience | Evidence and stars for level 01 | `EvidenceLog`, `isClean`, `computeStars` | three star outcomes |
| level-one-experience | Level 01 can be left and resumed | `SceneMachine.push/pop` snapshots, `ProgressStore`, journal/layout/controls scenes | Layout help mid-lap test, reload test |
| game-ui | The UI follows the UI kit | `mountUi`, `COMPONENTS`, `game/css` importing `tokens.css`, view-models in section 7 | stylesheet lint, screenshot compare |
| game-ui | Instructions use the hint grammar | `DialogueViewModel.hint`, data `hint {action,key,gesture}` | Ivo lap line text test |
| game-ui | The keyboard inset teaches position, hold order, output and effect | `InsetViewModel`, `vm:inset` (null on recall), `insetRect` | four cells, absent on recall |
| game-ui | Layout help is rendered from the layout manifest | `LayoutManifest`, `layoutHelpModel`, `LayoutHelpViewModel` | changing a manifest entry changes the legend |
| game-ui | Accessibility and display | live-region, `vm:settings`, `.rm/.large-text/.hc`, `AnimationPlayer` reduced motion, focus ring tokens | live region and reduced motion tests, checklist 6.4 |
| game-ui | Sound is out of scope and off | no audio API anywhere (section 0), UI mount | grep test: no `Audio`/`AudioContext` in `game/src` |

## 11. Decisions and notes for the producer

- `InterpretedEvent` keeps the task shape `{output, text, confidence, repeat, t}` and adds `phase, combo, mods, code, action, dir` so held movement and combo feedback (`Alt+ArrowRight` in the level data) work without raw events.
- Backquote is the single output keyed by `code` (the bindings document requires it); every other output is `event.key`.
- Progress key is the constant `kanata-hero:progress`; "keys derived from world.json" is read as: every id inside the document comes from `world.json` `state_ids`, plus its `worldVersion`.
- Step timing is in simulation steps: the atlas gives one walk frame per 8 px (two per cell), which differs from the spec scenario wording "two walk frames per 8 px"; the contract follows the atlas JSON.
- "Garden markers teal to gold" is not a level-data state change: it is the `o01-loop` marker state (`teal until reached, gold after`, `vm:markers.floor`). "Mailroom gate unlock" is `g.turnstile`, the mailroom entrance, via `unlock_gate`.
- Level 01 uses ops `set_state, npc_state, unlock_gate, set_flag, complete_level, start_dialogue, spawn_glitch, journal`; `light_state` and `grant` are deliberately unsupported until a level needs them.
- Fixed step is `1000/60` ms, a cell move is 16 steps.

## 12. Playtest 1 decisions (producer, 2026-10-02)

- Setup is the keyboard choice only. Calibration runs one step at a time, shows the expected output, the last output seen and wrong-key feedback; on step 1 an Escape output shows the tap-versus-hold hint.
- Skipping: Down skips the current calibration step, Up opens the "skip calibration" confirm card, and Esc (or the Skip setup button) on setup opens the same kind of confirm card (Return = yes, Esc = back). No single key press skips everything.
- Output feedback (`vm:feedback`) appears only in form, label and editor scenes and is cleared on scene exit; in the world it is a 2.5 s toast for the first three walking bursts. Settings option "Show output feedback": in scenes only (default), always, off.
- The dialogue is a compact strip (at most 160 px tall); a camera look-ahead keeps the avatar clear of open panels, with a 35 % fade of the covering panel as the last resort.
- Tall y-sorted props, contact shadows and actors are sorted together by anchor y, so an actor north of a tall prop is drawn behind it.
