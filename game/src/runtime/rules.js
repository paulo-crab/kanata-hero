// Rule runtime: executes a level's steps, triggers and dialogue conditions from data only.
// Contract: game/CONTRACTS.md section 5.3. No time, no DOM, no randomness.
import { DataLoadError } from '../shared/index.js';
import { parseCondition, atomsOf, evaluate } from './condition.js';

export const SUPPORTED_OPS = [
  'set_state', 'npc_state', 'unlock_gate', 'set_flag',
  'complete_level', 'start_dialogue', 'spawn_glitch', 'journal',
];

const slug = (title) => String(title).toLowerCase().replace(/[^a-z0-9]+/g, '-').replace(/^-|-$/g, '');

/** Fact -> atom key ("scene_success:o01-popup", "reach_cell:3,12"), or null. */
export function factKey(fact) {
  if (!fact || !fact.type) return null;
  if (fact.type === 'reach_cell') {
    return fact.cell ? `reach_cell:${fact.cell[0]},${fact.cell[1]}` : null;
  }
  return fact.id === undefined ? null : `${fact.type}:${fact.id}`;
}

export class RuleRuntime {
  /**
   * @param {{level:object, map:object, district?:object, world?:object, state?:object|(()=>object), bus:object, levelFile?:string}} p
   *  `world` is the world.json document (optional, used to check flag and level ids); `state` is a ProgressDoc
   *  view (or a function returning the live one).
   */
  constructor({ level, map, district, world, state, bus, levelFile }) {
    this.level = level;
    this.map = map;
    this.district = district;
    this.worldDoc = world || null;
    this.bus = bus;
    this._state = state || {};
    this.levelFile = levelFile
      || `/design/levels/${level.district}/levels/${String(level.number).padStart(2, '0')}-${slug(level.title)}.json`;
    this.steps = level.steps || [];
    this._parsed = new Map();
    this._validate();
    this._scope = this._buildCellScope();
    this._autoOpen = this._buildAutoOpen();

    this.facts = new Set();
    this._done = [];
    this._idx = 0;
    this._started = false;
    this._out = null;
    this.npcStates = {};
    for (const n of map.npcs || []) this.npcStates[n.id] = n.initial_state || 'start';
    const st = this._st();
    Object.assign(this.npcStates, st.npc || {});
    const saved = st.levels && st.levels[level.id];
    if (saved && Array.isArray(saved.facts) && saved.facts.length) {
      for (const f of saved.facts) this.facts.add(f);
      this._done = [...(saved.stepsDone || [])];
      this._idx = this._firstUnfinished();
      this._started = true;
    }
  }

  _st() {
    return (typeof this._state === 'function' ? this._state() : this._state) || {};
  }

  _fail(kind, detail) {
    return new DataLoadError({ file: this.levelFile, kind, detail });
  }

  _parse(str, where) {
    if (!this._parsed.has(str)) {
      try {
        this._parsed.set(str, parseCondition(str));
      } catch (e) {
        throw this._fail('shape', `${where}: ${e.message}`);
      }
    }
    return this._parsed.get(str);
  }

  _validate() {
    const { level, map } = this;
    const dialogueIds = new Set((level.dialogue || []).map((d) => d.id));
    const placements = new Set((map.placements || []).map((p) => p.id));
    const npcs = new Map((map.npcs || []).map((n) => [n.id, n]));
    const gates = new Set((map.gates || []).map((g) => g.id));
    const interactions = new Set((map.interactions || []).map((i) => i.id));
    const ids = this.worldDoc && this.worldDoc.state_ids;
    for (const s of this.steps) this._parse(s.completes_when, `step ${s.id}`);
    for (const d of level.dialogue || []) {
      if (d.when !== undefined && !d.on_request) this._parse(d.when, `dialogue ${d.id}`);
    }
    for (const t of level.triggers || []) {
      this._parse(t.when, `trigger ${t.id}`);
      for (const op of t.then || []) {
        if (!SUPPORTED_OPS.includes(op.op)) {
          throw this._fail('unsupported', `trigger ${t.id} uses operation "${op.op}", which the runtime does not support (${SUPPORTED_OPS.join(', ')})`);
        }
        if (op.op === 'start_dialogue' && !dialogueIds.has(op.dialogue)) throw this._fail('shape', `trigger ${t.id}: unknown dialogue ${op.dialogue}`);
        if (op.op === 'set_state' && !placements.has(op.target)) throw this._fail('shape', `trigger ${t.id}: unknown placement ${op.target}`);
        if (op.op === 'npc_state') {
          const n = npcs.get(op.npc);
          if (!n) throw this._fail('shape', `trigger ${t.id}: unknown npc ${op.npc}`);
          if (!n.poses_by_state || !(op.state in n.poses_by_state)) throw this._fail('shape', `trigger ${t.id}: npc ${op.npc} has no state ${op.state}`);
        }
        if (op.op === 'unlock_gate' && !gates.has(op.gate)) throw this._fail('shape', `trigger ${t.id}: unknown gate ${op.gate}`);
        if (op.op === 'spawn_glitch' && !interactions.has(op.interaction)) throw this._fail('shape', `trigger ${t.id}: unknown interaction ${op.interaction}`);
        if (op.op === 'set_flag' && ids && !ids.flags.includes(op.flag)) throw this._fail('shape', `trigger ${t.id}: flag ${op.flag} is not in world.json`);
        if (op.op === 'complete_level' && ids && !ids.levels_done.includes(op.level)) throw this._fail('shape', `trigger ${t.id}: level ${op.level} is not in world.json`);
      }
    }
  }

  /** reach_cell facts for a cell only count while the step whose walk scene uses that cell is current. */
  _buildCellScope() {
    const scope = new Map();
    const stepOfScene = new Map();
    for (const s of this.steps) {
      for (const a of atomsOf(this._parse(s.completes_when, s.id))) {
        if (a.name === 'scene_success') stepOfScene.set(a.arg, s.id);
      }
    }
    for (const sc of this.level.terminal_scenes || []) {
      if (sc.kind !== 'walk') continue;
      const step = stepOfScene.get(sc.id);
      if (!step) continue;
      const cells = [];
      for (const l of (sc.task && sc.task.legs) || []) {
        if (l.to) cells.push(l.to);
        if (l.marker) cells.push(l.marker);
      }
      for (const st of (sc.task && sc.task.stops) || []) if (st.cell) cells.push(st.cell);
      for (const c of cells) {
        const k = `${c[0]},${c[1]}`;
        if (!scope.has(k)) scope.set(k, new Set());
        scope.get(k).add(step);
      }
    }
    return scope;
  }

  /** step id -> scenes the runtime opens by itself when the step starts. */
  _buildAutoOpen() {
    const scenes = this.level.terminal_scenes || [];
    const byId = new Map(scenes.map((s) => [s.id, s]));
    const triggered = new Set();
    for (const s of scenes) {
      for (const st of (s.task && s.task.stops) || []) if (st.triggers_scene) triggered.add(st.triggers_scene);
    }
    const out = new Map();
    for (const step of this.steps) {
      const list = [];
      if (!step.optional) {
        for (const a of atomsOf(this._parse(step.completes_when, step.id))) {
          if (a.name === 'scene_success' && byId.has(a.arg) && !triggered.has(a.arg)) list.push(byId.get(a.arg));
        }
      }
      out.set(step.id, list);
    }
    return out;
  }

  get currentStep() {
    return this.steps[this._idx] || null;
  }

  get stepsDone() {
    return [...this._done];
  }

  get started() {
    return this._started;
  }

  _firstUnfinished() {
    const i = this.steps.findIndex((s) => !this._done.includes(s.id));
    return i < 0 ? this.steps.length : i;
  }

  /** Scenes (terminal_scenes entries) a step opens on its own. */
  stepScenes(step) {
    return this._autoOpen.get(step.id) || [];
  }

  snapshot() {
    return {
      currentStepId: this.currentStep ? this.currentStep.id : null,
      stepsDone: this.stepsDone,
      facts: [...this.facts],
    };
  }

  // ---- facts and evaluation -------------------------------------------------

  _has(key) {
    if (this.facts.has(key)) return true;
    const st = this._st();
    if (key.startsWith('state:')) {
      const arg = key.slice(6);
      return arg === 'start' || (st.flags || []).includes(arg) || (st.levelsDone || []).includes(arg);
    }
    if (key.startsWith('level_complete:')) return (st.levelsDone || []).includes(key.slice(15));
    return false;
  }

  _holds(str) {
    return evaluate(this._parse(str, 'condition'), (k) => this._has(k));
  }

  /** Public: does a condition string hold right now? */
  holds(conditionStr) {
    return this._holds(conditionStr);
  }

  _emit(intent) {
    if (this._out) this._out.push(intent);
    this.bus.emit('intent', intent);
  }

  _collect(fn) {
    const outer = this._out;
    this._out = [];
    try {
      fn();
      return this._out;
    } finally {
      this._out = outer;
    }
  }

  start() {
    if (this._started) {
      if (this.currentStep) this._collect(() => this._resume());
      return;
    }
    this._started = true;
    this._collect(() => {
      if (this.currentStep) this._begin(this._idx);
      this._settle();
    });
  }

  _resume() {
    const step = this.currentStep;
    this._emit({ type: 'objective', stepId: step.id, text: step.objective });
    for (const sc of this.stepScenes(step)) {
      if (!this.facts.has(`scene_success:${sc.id}`)) this._emit({ type: 'openScene', kind: sc.kind, sceneId: sc.id });
    }
    for (const d of this.level.dialogue || []) {
      if (d.when === `step_start:${step.id}` && d.hint) {
        this._emit({ type: 'say', dialogueId: d.id, modal: false });
      }
    }
  }

  /** Feed one fact. Returns the intents this fact produced (also emitted on the bus topic 'intent'). */
  notify(fact) {
    return this._collect(() => {
      const key = factKey(fact);
      if (!key || fact.type === 'request') return;
      if (fact.type === 'reach_cell') {
        const scope = this._scope.get(`${fact.cell[0]},${fact.cell[1]}`);
        const step = this.currentStep;
        if (scope && (!step || !scope.has(step.id))) return;
      }
      this.facts.add(key);
      if (this._started) this._settle();
    });
  }

  _begin(i) {
    const step = this.steps[i];
    this.facts.add(`step_start:${step.id}`);
    this.bus.emit('rules:step-start', { id: step.id });
    this._emit({ type: 'objective', stepId: step.id, text: step.objective });
    for (const sc of this.stepScenes(step)) {
      if (!this.facts.has(`scene_success:${sc.id}`)) this._emit({ type: 'openScene', kind: sc.kind, sceneId: sc.id });
    }
  }

  _settle() {
    for (let guard = 0; guard < 200; guard += 1) {
      const step = this.currentStep;
      if (step && this._holds(step.completes_when)) {
        this._done.push(step.id);
        this.facts.add(`step_done:${step.id}`);
        this.bus.emit('rules:step-done', { id: step.id });
        this._idx = this._firstUnfinished();
        if (this.currentStep) this._begin(this._idx);
        continue;
      }
      let progressed = false;
      for (const t of this.level.triggers || []) {
        const k = `trigger:${t.id}`;
        if (!this.facts.has(k) && this._holds(t.when)) {
          this.facts.add(k);
          this._runOps(t);
          progressed = true;
        }
      }
      for (const d of this.level.dialogue || []) {
        if (d.when === undefined || d.on_request) continue;
        const k = `said:${d.id}`;
        if (!this.facts.has(k) && this._holds(d.when)) {
          this.facts.add(k);
          this._say(d);
          progressed = true;
        }
      }
      if (!progressed) return;
    }
    throw this._fail('shape', 'rule evaluation did not settle');
  }

  _say(d, onRequest = false) {
    const modal = d.modal === undefined ? d.hint === null || d.hint === undefined : d.modal;
    const intent = { type: 'say', dialogueId: d.id, modal };
    if (onRequest) intent.onRequest = true;
    this._emit(intent);
  }

  _runOps(trigger) {
    for (const op of trigger.then || []) {
      switch (op.op) {
        case 'set_state':
          this._emit({ type: 'setPlacementState', placement: op.target, state: op.state });
          break;
        case 'npc_state':
          this.npcStates[op.npc] = op.state;
          this._emit({ type: 'setNpcState', npc: op.npc, state: op.state });
          break;
        case 'unlock_gate':
          this._emit({ type: 'unlockGate', gate: op.gate });
          break;
        case 'set_flag':
          this.facts.add(`state:${op.flag}`);
          this._emit({ type: 'setFlag', flag: op.flag });
          break;
        case 'complete_level':
          this.facts.add(`level_complete:${op.level}`);
          this.facts.add(`state:${op.level}`);
          this._emit({ type: 'completeLevel', level: op.level });
          break;
        case 'start_dialogue': {
          const d = (this.level.dialogue || []).find((x) => x.id === op.dialogue);
          this.facts.add(`said:${d.id}`);
          this._say(d);
          break;
        }
        case 'spawn_glitch':
          this._emit({ type: 'spawnGlitch', interaction: op.interaction });
          break;
        case 'journal':
          this._emit({ type: 'journalEntry', text: op.text });
          break;
        default:
          throw this._fail('unsupported', `operation "${op.op}"`);
      }
    }
  }

  /** The Hint key was pressed while `dialogueId` is on screen: say its on_request line (every press). */
  onRequest(dialogueId) {
    return this._collect(() => {
      const d = (this.level.dialogue || []).find((x) => x.on_request && x.when === `request:${dialogueId}`);
      if (d) this._say(d, true);
    });
  }

  // ---- map queries ------------------------------------------------------------

  _levelDone(id) {
    return this._has(`level_complete:${id}`);
  }

  npcState(npcId) {
    return this.npcStates[npcId];
  }

  _visibleWhen(vw) {
    if (!vw) return true;
    if (vw.startsWith('level:')) return this._levelDone(vw.slice(6));
    if (vw.startsWith('npc_state:')) {
      const [npc, want] = vw.slice(10).split('=');
      const cur = this.npcStates[npc];
      if (cur === undefined) return false;
      return want.endsWith('*') ? cur.startsWith(want.slice(0, -1)) : cur === want;
    }
    return true;
  }

  /** visible_when of a map interaction: 'level:<id>' and 'npc_state:<npc>=<state>' (trailing '*' = prefix). */
  isVisible(interactionId) {
    const it = (this.map.interactions || []).find((i) => i.id === interactionId);
    return it ? this._visibleWhen(it.visible_when) : false;
  }

  /** `requires` of a map interaction: level:, seal:, flag:, artifact:, mira:. */
  requirementsMet(interactionId) {
    const it = (this.map.interactions || []).find((i) => i.id === interactionId);
    if (!it) return false;
    const st = this._st();
    return (it.requires || []).every((r) => {
      const i = r.indexOf(':');
      const kind = r.slice(0, i);
      const id = r.slice(i + 1);
      if (kind === 'level') return this._levelDone(id);
      if (kind === 'seal') return (st.seals || []).includes(id);
      if (kind === 'flag') return this._has(`state:${id}`);
      if (kind === 'artifact') return (st.artifacts || []).includes(id);
      if (kind === 'mira') return (st.miraRoutesCleared || []).includes(id);
      return false;
    });
  }
}
