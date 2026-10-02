// Test helpers for the runtime: real data files, a fake engine World, a fake input module and a scripted player.
// Fakes follow game/CONTRACTS.md sections 3 and 4 and never import another module's internals.
import { readFileSync } from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { EventBus, FakeClock, STEP_MS } from '../../src/shared/index.js';
import { createSession } from '../../src/runtime/index.js';

const here = path.dirname(fileURLToPath(import.meta.url));
export const REPO = path.resolve(here, '..', '..', '..');
export const readJson = (rel) => JSON.parse(readFileSync(path.join(REPO, rel), 'utf8'));

export function loadData() {
  return {
    district: readJson('design/levels/orientation/district.json'),
    map: readJson('design/levels/orientation/map.json'),
    level: readJson('design/levels/orientation/levels/01-the-lobby.json'),
    world: readJson('design/levels/world.json'),
    gestureInventory: readJson('design/levels/gesture-inventory.json'),
    layoutManifest: readJson('design/layout/layout-manifest.json'),
  };
}

const DELTA = { n: [0, -1], s: [0, 1], e: [1, 0], w: [-1, 0] };

export class FakeWorld {
  constructor(data, bus) {
    this.data = data;
    this.bus = bus;
    this.timeMs = 0;
    this.stateLog = [];
    this.placements = {};
    this.openGates = new Set();
    this.glitch = {};
    this.npcs = {};
    for (const n of data.map.npcs) {
      this.npcs[n.id] = {
        id: n.id, character: n.character, cell: [...n.start_cell], facing: n.facing,
        pose: n.poses_by_state.start, state: 'start', visible: true,
      };
    }
    const w = this;
    this.avatar = {
      cell: [0, 0], facing: 's', held: null,
      requestStep(dir) {
        this.facing = dir;
        const [dx, dy] = DELTA[dir];
        const cell = [this.cell[0] + dx, this.cell[1] + dy];
        if (w.isBlocked(cell[0], cell[1])) {
          bus.emit('engine:blocked', { cell: [...this.cell], dir });
          return 'blocked';
        }
        this.cell = cell;
        bus.emit('engine:step-complete', { cell: [...cell], facing: dir, dir });
        return 'started';
      },
      setHeld(d) { this.held = d; },
      teleport(c, f) { this.cell = [...c]; this.facing = f; },
    };
    this.playing = null;
  }

  isBlocked(x, y) {
    const rows = this.data.map.collision;
    if (y < 0 || y >= rows.length || x < 0 || x >= rows[0].length) return true;
    if (rows[y][x] !== '1') return false;
    for (const id of this.openGates) {
      const g = this.data.map.gates.find((q) => q.id === id);
      if (g.cells.some((c) => c[0] === x && c[1] === y)) return false;
    }
    return true;
  }

  placementState(id) { return this.placements[id] || null; }

  setPlacementState(id, state) {
    this.placements[id] = state;
    this.stateLog.push({ placement: id, state, atMs: this.timeMs });
  }

  playStateSet(id, sequence) {
    this.playing = { id, sequence, elapsed: 0, shown: -1 };
    this._tickPlay(0);
  }

  _tickPlay(ms) {
    const p = this.playing;
    if (!p) return;
    p.elapsed += ms;
    const idx = Math.min(p.sequence.length - 1, Math.floor(p.elapsed / 120));
    if (idx !== p.shown) {
      p.shown = idx;
      this.setPlacementState(p.id, p.sequence[idx]);
    }
    if (p.elapsed >= 120 * (p.sequence.length - 1) + 120) {
      this.playing = null;
      this.bus.emit('engine:stateset-done', { placement: p.id, state: p.sequence[p.sequence.length - 1] });
    }
  }

  setNpcState(id, state) {
    const def = this.data.map.npcs.find((n) => n.id === id);
    const n = this.npcs[id];
    n.state = state;
    n.pose = def.poses_by_state[state];
    n.cell = (def.cells_by_state && def.cells_by_state[state]) ? [...def.cells_by_state[state]] : [...def.start_cell];
  }

  npc(id) { return this.npcs[id]; }

  openGate(id) {
    this.openGates.add(id);
    const g = this.data.map.gates.find((q) => q.id === id);
    if (g.placement) this.setPlacementState(g.placement, 'open');
  }

  isGateOpen(id) { return this.openGates.has(id); }
  spawnGlitch(id) { this.glitch[id] = 'spawned'; }
  repairGlitch(id) { this.glitch[id] = 'repaired'; }

  update(ms) {
    this.timeMs += ms;
    this._tickPlay(ms);
  }

  serialize() {
    return {
      placements: { ...this.placements }, gates: [...this.openGates],
      npcs: Object.fromEntries(Object.values(this.npcs).map((n) => [n.id, n.state])),
      avatar: { cell: [...this.avatar.cell], facing: this.avatar.facing },
    };
  }

  restore(slice) {
    this.placements = { ...slice.placements };
    for (const g of slice.gates) this.openGates.add(g);
    for (const [id, st] of Object.entries(slice.npcs)) this.setNpcState(id, st);
    this.avatar.teleport(slice.avatar.cell, slice.avatar.facing);
  }
}

// ---- fake input module (contract section 4) ---------------------------------------------------

export const CALIBRATION_STEPS = [
  { id: 'caps-h', gesture: 'Caps + H', expected: 'ArrowLeft' },
  { id: 'caps-n', gesture: 'Caps + N', expected: 'Enter' },
  { id: 'space-a', gesture: 'Space + A', expected: '1' },
  { id: 'space-q', gesture: 'Space + Q', expected: '!' },
  { id: 'shift-hold', gesture: 'F (home-row Shift), then /', expected: '?' },
];

class FakeCalibration {
  constructor(keyboard = 'macbook') {
    this.keyboard = keyboard;
    this.steps = Object.fromEntries(CALIBRATION_STEPS.map((s) => [s.id, 'not_started']));
  }

  get current() {
    const s = CALIBRATION_STEPS.find((x) => this.steps[x.id] === 'not_started');
    return s ? s.id : null;
  }

  observe(ev) {
    const cur = this.current;
    if (!cur) return null;
    const step = CALIBRATION_STEPS.find((s) => s.id === cur);
    if (ev.output !== step.expected) return null;
    this.steps[cur] = 'observed';
    return { stepId: cur, status: 'observed' };
  }

  skipCurrent() { const c = this.current; if (c) this.steps[c] = 'skipped'; }
  skipAll() { for (const k of Object.keys(this.steps)) if (this.steps[k] === 'not_started') this.steps[k] = 'skipped'; }
  result() { return { keyboard: this.keyboard, steps: { ...this.steps } }; }
}

class FakeHintGate {
  constructor() { this._uses = []; this._req = null; }
  request({ sceneId, phase }) {
    this._req = { sceneId, phase };
    if (phase === 'recall') return { needsCard: true, card: { text: 'Using the hint here forfeits the third star for this scene. Press Return to show the hint, or Esc to keep it.', confirmKey: 'Enter' } };
    return { needsCard: false };
  }
  confirm() {
    const use = { ...this._req, forfeitsStar: this._req.phase === 'recall' };
    this._uses.push(use);
    return use;
  }
  cancel() { this._req = null; }
  uses() { return this._uses; }
}

export const fakeInput = {
  CALIBRATION_STEPS,
  Calibration: FakeCalibration,
  HintGate: FakeHintGate,
  layoutHelpModel: (m, state) => ({ tab: state.tab, variant: state.variant, tabs: m.tabs().map((id) => ({ id, label: id, selected: id === state.tab })) }),
};

export const fakeManifest = { tabs: () => ['base', 'nav', 'numbers-symbols', 'practice'], sequences: () => [] };

// ---- scripted player ------------------------------------------------------------------------

const ARROW_DIR = { ArrowUp: 'n', ArrowDown: 's', ArrowLeft: 'w', ArrowRight: 'e' };

/** Resolve an action the way the input module's table does (contract 4.2, 5.2). */
export function resolve(output, k, mods = {}) {
  const plainMods = !mods.alt && !mods.ctrl && !mods.meta && !mods.shift;
  if (output === '?') return { action: k.layoutHelp ? 'layoutHelp' : null, dir: null };
  if (!plainMods) return { action: null, dir: null };
  if (output === 'Backquote') return { action: k.hint ? 'hint' : null, dir: null };
  if (output.toLowerCase() === 'q' && k.journal && !k.typing) return { action: 'journal', dir: null };
  if (output === 'Enter' && ['interact', 'continue', 'confirm', 'retry'].includes(k.enter)) return { action: k.enter, dir: null };
  if (output === 'Escape' && ['skip', 'back'].includes(k.esc)) return { action: k.esc, dir: null };
  if (ARROW_DIR[output] && ['move', 'choose'].includes(k.arrows)) return { action: k.arrows, dir: ARROW_DIR[output] };
  return { action: null, dir: ARROW_DIR[output] || null };
}

export function makeGame(opts = {}) {
  const data = loadData();
  const bus = new EventBus();
  const clock = new FakeClock();
  const world = new FakeWorld(data, bus);
  const errors = [];
  bus.on('bus:error', (e) => errors.push(e));
  const store = opts.storage || null;
  const portraits = readJson('art-direction/portraits/portraits-atlas.json').portraits;
  const atlases = { portrait: (k) => { if (!portraits[k]) throw new Error(`no portrait ${k}`); return portraits[k]; } };
  const session = createSession({ bus, clock, data, world, atlases, storage: store, input: fakeInput, manifest: fakeManifest });
  const vms = {};
  bus.on('*', (topic, payload) => { if (topic.startsWith('vm:')) vms[topic] = payload; });
  const log = [];
  bus.on('*', (topic, payload) => { if (['intent', 'level:complete', 'scene:success'].includes(topic)) log.push([topic, payload]); });

  const player = {
    send(output, { phase = 'down', mods = {}, repeat = false } = {}) {
      const k = session.machine.inputContext();
      const { action, dir } = resolve(output, k, mods);
      const text = output.length === 1 ? output : (output === 'Space' ? ' ' : null);
      const combo = [mods.ctrl && 'Ctrl', mods.alt && 'Alt', mods.meta && 'Meta'].filter(Boolean).concat(output).join('+');
      bus.emit('input:event', {
        output, text: mods.alt || output === '?' ? null : text, confidence: 'observed', repeat, t: clock.now(), phase, combo,
        mods: { alt: !!mods.alt, ctrl: !!mods.ctrl, meta: !!mods.meta, shift: !!mods.shift }, code: output, action, dir,
      });
    },
    tap(output, opts) { this.send(output, opts); this.send(output, { ...opts, phase: 'up' }); },
    tick(n = 1) { for (let i = 0; i < n; i += 1) { world.update(STEP_MS); session.update(STEP_MS); clock.advance(STEP_MS); } },
    walk(dir, n = 1) { for (let i = 0; i < n; i += 1) this.tap({ n: 'ArrowUp', s: 'ArrowDown', e: 'ArrowRight', w: 'ArrowLeft' }[dir]); },
    type(str) { for (const ch of str) this.tap(ch); },
    /** Shortest path between cells, sent as arrow taps. */
    goTo(cell) {
      const path = bfs(world, world.avatar.cell, cell);
      for (const d of path) this.walk(d);
    },
    cell() { return [...world.avatar.cell]; },
  };
  return { data, bus, clock, world, session, vms, log, errors, player };
}

export function bfs(world, from, to) {
  const key = (c) => `${c[0]},${c[1]}`;
  const prev = new Map([[key(from), null]]);
  const q = [from];
  for (let i = 0; i < q.length; i += 1) {
    const c = q[i];
    if (key(c) === key(to)) break;
    for (const [d, [dx, dy]] of Object.entries(DELTA)) {
      const n = [c[0] + dx, c[1] + dy];
      if (prev.has(key(n)) || world.isBlocked(n[0], n[1])) continue;
      prev.set(key(n), { from: c, d });
      q.push(n);
    }
  }
  const out = [];
  let cur = to;
  while (prev.get(key(cur))) { const p = prev.get(key(cur)); out.unshift(p.d); cur = p.from; }
  return out;
}

export function memoryStorage() {
  const m = new Map();
  return {
    getItem: (k) => (m.has(k) ? m.get(k) : null),
    setItem: (k, v) => { m.set(k, v); },
    removeItem: (k) => { m.delete(k); },
    _m: m,
  };
}
