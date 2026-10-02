// Session: wires scene machine, rule runtime, dialogue, evidence, progress, the engine World and the bus.
// Owns the bridge from facts and intents to world changes. Never touches the DOM or real time.
import { ProgressStore } from './progress.js';
import { RuleRuntime } from './rules.js';
import { DialogueRuntime } from './dialogue.js';
import { EvidenceLog, computeStars, phaseInfo } from './evidence.js';
import { SceneMachine } from './machine.js';
import { createSceneFactories } from './scenes/index.js';
import { keycap, KEY_GESTURE } from './common.js';

const WORLD_TOPS = ['hub', 'walk', 'form', 'label', 'editor'];
const HUD_HIDDEN = ['setup', 'calibration', 'arrival', 'error'];
const SHAPE = { conversation: 'conversation', terminal: 'terminal', glitch: 'glitch' };

export class Session {
  /**
   * @param {{bus:object, clock:object, data:object, world:object, atlases?:object, storage?:object,
   *   input:object, manifest?:object}} p  input is the input module namespace (Calibration, HintGate, layoutHelpModel,
   *   CALIBRATION_STEPS); data is GameData.
   */
  constructor({ bus, clock, data, world, atlases, storage, input, manifest }) {
    this.bus = bus;
    this.data = data;
    this.world = world;
    this.level = data.level;
    this.progress = new ProgressStore({ storage, world: data.world, bus });
    this.progress.load();
    const saved = this.progress.doc.levels[this.level.id];
    this.evidence = saved && saved.scenes
      ? EvidenceLog.fromJSON({ scenes: saved.scenes, hints: this.progress.doc.hintUse }, { level: this.level })
      : new EvidenceLog({ level: this.level });
    this.rules = new RuleRuntime({
      level: this.level, map: data.map, district: data.district, world: data.world,
      state: () => this.progress.doc, bus,
    });
    this.dialogue = new DialogueRuntime({
      level: this.level, bus, rules: this.rules,
      portraitRect: atlases && atlases.portrait ? (k) => atlases.portrait(k) : undefined,
      isWorldTop: () => !!this.machine.top && WORLD_TOPS.includes(this.machine.top.kind),
      getPatches: () => this.progress.doc.patches,
    });
    this.hintGate = new input.HintGate({ difficulty: 'standard' });
    this.actions = {
      interact: () => this.interact(),
      requestHint: () => this.requestHint(),
      afterSetup: () => this.afterSetup(),
      resetProgress: () => this.resetProgress(),
    };
    this.ctx = {
      bus, clock, data, world, rules: this.rules, progress: this.progress, input, evidence: this.evidence,
      dialogue: this.dialogue, manifest, actions: this.actions, held: null,
    };
    this.machine = new SceneMachine(this.ctx, createSceneFactories(this.ctx));
    this.pending = [];
    this.pendingHint = null;
    this.hintBase = null;
    this._rulesStarted = false;
    this._vm = new Map();
    this._requestable = new Set((this.level.dialogue || [])
      .filter((d) => d.on_request).map((d) => d.when.replace('request:', '')));
    this._wire();
  }

  _wire() {
    const b = this.bus;
    b.on('input:event', (ev) => this.onInput(ev));
    b.on('intent', (i) => this.applyIntent(i));
    b.on('scene:success', (e) => this.onSceneSuccess(e));
    b.on('scene:progress', (e) => this.onSceneProgress(e));
    b.on('engine:step-complete', (e) => {
      this.machine.notifyEngine('engine:step-complete', e);
      this.rules.notify({ type: 'reach_cell', cell: e.cell });
      this.persist();
      this.pump();
    });
    for (const t of ['engine:blocked', 'engine:stateset-done', 'engine:glitch-repaired']) {
      b.on(t, (e) => { this.machine.notifyEngine(t, e); this.pump(); });
    }
    b.on('rules:step-done', () => { this.dialogue.clearInstruction(); this.persist(); });
    b.on('scene:enter', (e) => this.onSceneEnter(e));
    b.on('scene:exit', () => this.pump());
    b.on('dialogue:open', () => this.pump());
    b.on('dialogue:closed', () => this.pump());
    b.on('ui:command', (c) => this.onCommand(c));
  }

  // ---- boot -------------------------------------------------------------------

  hasProgress() {
    return this.progress.hasProgress();
  }

  _levelSaved() {
    const l = this.progress.doc.levels[this.level.id];
    return l && l.facts && l.facts.length ? l : null;
  }

  afterSetup() {
    return this._levelSaved() ? 'hub' : 'arrival';
  }

  /** First visit: setup then arrival. Returning: hub (progress restored through World.restore). */
  start() {
    const doc = this.progress.doc;
    if (!doc.setup.done) {
      this.machine.push('setup');
    } else if (this._levelSaved()) {
      this._restoreWorld();
      this.machine.push('hub');
    } else {
      this.machine.push('arrival');
    }
    this.publishAll();
  }

  _restoreWorld() {
    const doc = this.progress.doc;
    const lvl = this._levelSaved();
    this.world.restore({
      placements: { ...doc.placements }, npcs: { ...doc.npc }, gates: [...doc.gatesOpen],
      avatar: lvl.avatar,
    });
  }

  onSceneEnter(e) {
    if (e.kind === 'hub' && !this._rulesStarted) {
      this._rulesStarted = true;
      this.rules.start();
    }
    this.pump();
  }

  // ---- input -------------------------------------------------------------------

  onInput(ev) {
    if (this.pendingHint) {
      if (ev.phase !== 'up' && !ev.repeat) {
        if (ev.output === 'Enter') this.confirmHint();
        else if (ev.output === 'Escape') this.cancelHint();
      }
      return;
    }
    this.dialogue.observe(ev);
    this.machine.handle(ev);
    this.pump();
  }

  update(stepMs) {
    this.machine.update(stepMs);
    this.pump();
  }

  // ---- layers ------------------------------------------------------------------

  pump() {
    for (let guard = 0; guard < 20; guard += 1) {
      const top = this.machine.top;
      if (!top) break;
      if (this.dialogue.hasConversation()) {
        if (top.kind !== 'dialogue' && this.machine.canPush('dialogue')) {
          this.machine.push('dialogue');
          continue;
        }
        break;
      }
      if (top.kind === 'dialogue' || !this.pending.length) break;
      const next = this.pending[0];
      if (this.machine.stack.some((s) => s.id === next.sceneId)) {
        this.pending.shift();
        continue;
      }
      if (!this.machine.canPush(next.kind)) break;
      this.pending.shift();
      this.machine.push(next.kind, { sceneId: next.sceneId, progress: next.progress });
    }
    this.publishAll();
  }

  // ---- intents -----------------------------------------------------------------

  applyIntent(i) {
    const w = this.world;
    switch (i.type) {
      case 'say': {
        const d = this.dialogue.line(i.dialogueId);
        if (!i.onRequest && (d.hint || this._requestable.has(d.id))) this.hintBase = d.id;
        this.dialogue.open(i.dialogueId);
        break;
      }
      case 'setPlacementState':
        w.setPlacementState(i.placement, i.state);
        this.progress.update((d) => { d.placements[i.placement] = i.state; });
        break;
      case 'setNpcState':
        w.setNpcState(i.npc, i.state);
        this.progress.update((d) => { d.npc[i.npc] = i.state; });
        break;
      case 'unlockGate':
        w.openGate(i.gate);
        this.progress.update((d) => { if (!d.gatesOpen.includes(i.gate)) d.gatesOpen.push(i.gate); });
        break;
      case 'spawnGlitch':
        w.spawnGlitch(i.interaction);
        break;
      case 'openScene': {
        const saved = this._levelSaved();
        const prog = saved && saved.sceneProgress ? saved.sceneProgress[i.sceneId] : undefined;
        this.pending.push({ kind: i.kind, sceneId: i.sceneId, progress: prog });
        break;
      }
      case 'setFlag':
        this.progress.update((d) => { if (!d.flags.includes(i.flag)) d.flags.push(i.flag); });
        break;
      case 'journalEntry':
        this.progress.update((d) => { if (!d.journal.includes(i.text)) d.journal.push(i.text); });
        break;
      case 'completeLevel':
        this.completeLevel(i.level);
        break;
      case 'objective':
        this.bus.emit('vm:announce', { text: `Objective: ${i.text}` });
        break;
      case 'moveAvatar': {
        const last = i.path[i.path.length - 1];
        w.avatar.teleport(last, i.facing);
        break;
      }
      case 'playStateSet':
        w.playStateSet(i.placement, i.sequence);
        break;
      default:
        break;
    }
    this.persist();
    this.pump();
  }

  completeLevel(levelId) {
    const { stars, reasons } = computeStars(levelId, this.evidence.all(), this.level);
    this.progress.update((d) => {
      if (!d.levelsDone.includes(levelId)) d.levelsDone.push(levelId);
      const l = this._levelDoc(d);
      l.stars = stars;
      d.best[levelId] = { stars: Math.max(stars, (d.best[levelId] || {}).stars || 0) };
    });
    this.bus.emit('level:complete', { level: levelId, stars, reasons });
  }

  onSceneSuccess(e) {
    const g = this.level.glitch;
    if (g && g.scene_id === e.sceneId) this.world.repairGlitch(g.interaction);
    this.rules.notify({ type: 'scene_success', id: e.sceneId });
    this.persist();
    this.pump();
  }

  onSceneProgress(e) {
    this.progress.update((d) => {
      const l = this._levelDoc(d);
      l.sceneProgress[e.sceneId] = e.done;
    });
  }

  _levelDoc(d) {
    if (!d.levels[this.level.id]) {
      d.levels[this.level.id] = {
        currentStepId: null, stepsDone: [], avatar: { cell: [0, 0], facing: 's' }, stars: 0,
        scenes: {}, facts: [], sceneProgress: {},
      };
    }
    const l = d.levels[this.level.id];
    if (!l.sceneProgress) l.sceneProgress = {};
    return l;
  }

  persist() {
    if (!this._rulesStarted) return;
    this.progress.update((d) => {
      const l = this._levelDoc(d);
      Object.assign(l, this.rules.snapshot());
      const a = this.world.avatar;
      l.avatar = { cell: [...a.cell], facing: a.facing };
      l.scenes = this.evidence.all();
      d.hintUse = this.evidence.hints();
    });
  }

  // ---- interaction and hints -----------------------------------------------------

  _interactionAt() {
    const a = this.world.avatar;
    const delta = { n: [0, -1], s: [0, 1], e: [1, 0], w: [-1, 0] }[a.facing];
    for (const it of this.data.map.interactions) {
      if (!this.rules.isVisible(it.id)) continue;
      if (it.approach && it.approach.length) {
        if (it.approach.some((p) => p.cell[0] === a.cell[0] && p.cell[1] === a.cell[1] && p.facing === a.facing)) return it;
      } else if (it.marker !== 'route' && it.cells.some((c) => c[0] === a.cell[0] + delta[0] && c[1] === a.cell[1] + delta[1])) {
        return it;
      }
    }
    return null;
  }

  interact() {
    const walk = this.machine.stack.find((s) => s.kind === 'walk');
    if (walk && walk.openPending()) return;
    const it = this._interactionAt();
    if (!it) return;
    this.rules.notify({ type: 'interact', id: it.id });
    const line = it.dialogue_id && this.level.dialogue.find((d) => d.id === it.dialogue_id);
    if (line && line.when === undefined) this.dialogue.open(line.id);
    const def = it.scene_id && this.level.terminal_scenes.find((s) => s.id === it.scene_id);
    if (def && this.rules.requirementsMet(it.id)) {
      this.pending.push({ kind: def.kind, sceneId: def.id });
    } else if (!line && (it.scene_id || it.kind === 'elevator')) {
      this.bus.emit('vm:toast', { text: 'That comes later in the game.', tone: 'info' });
    }
    this.pump();
  }

  _activeSceneInfo() {
    for (let i = this.machine.layers.length - 1; i >= 0; i -= 1) {
      const s = this.machine.layers[i];
      if (s.def) return { sceneId: s.def.id, phase: phaseInfo(this.level, s.def.id).phase };
    }
    return null;
  }

  requestHint() {
    const info = this._activeSceneInfo();
    if (!info) {
      this._showHint();
      return;
    }
    const r = this.hintGate.request(info);
    if (r.needsCard) {
      this.pendingHint = info;
      this.bus.emit('vm:hint-card', { text: r.card.text, confirm: keycap('Enter'), cancel: keycap('Escape') });
      return;
    }
    this._applyHint(this.hintGate.confirm());
  }

  confirmHint() {
    this.pendingHint = null;
    this.bus.emit('vm:hint-card', null);
    this._applyHint(this.hintGate.confirm());
    this.pump();
  }

  cancelHint() {
    this.pendingHint = null;
    this.hintGate.cancel();
    this.bus.emit('vm:hint-card', null);
  }

  _applyHint(use) {
    this.evidence.hint(use);
    this.progress.update((d) => { d.hintUse = this.evidence.hints(); });
    this._showHint();
  }

  /** Say the on_request line for the line on screen, else re-show the last instruction. */
  _showHint() {
    const said = this.hintBase ? this.rules.onRequest(this.hintBase) : [];
    const last = this.dialogue.lastInstructionId();
    if (!said.length && last && !this.dialogue.instruction()) this.dialogue.open(last);
  }

  resetProgress() {
    this.progress.reset();
    this.bus.emit('game:reset', {});
  }

  // ---- ui commands ---------------------------------------------------------------

  _synth(output) {
    const k = this.machine.inputContext();
    let action = null;
    if (output === 'Enter') action = k.enter === 'none' || k.enter === 'text' ? null : k.enter;
    if (output === 'Escape') action = k.esc === 'none' || k.esc === 'text' ? null : k.esc;
    return {
      output, text: null, confidence: 'observed', repeat: false, t: this.ctx.clock.now(), phase: 'down',
      combo: output, mods: { alt: false, ctrl: false, meta: false, shift: false }, code: output, action, dir: null,
    };
  }

  onCommand(c) {
    const top = this.machine.top;
    switch (c.type) {
      case 'continue': this.onInput(this._synth('Enter')); break;
      case 'skip': case 'back': this.onInput(this._synth('Escape')); break;
      case 'selectKeyboard': if (top && top.select) top.select(c.id); break;
      case 'selectTab': if (top && top.kind === 'layout-help') top.select({ tab: c.id }); break;
      case 'selectVariant': if (top && top.kind === 'layout-help') top.select({ variant: c.id }); break;
      case 'selectKey': if (top && top.kind === 'layout-help') top.select({ selectedKey: c.id }); break;
      case 'openLayer': if (this.machine.canPush(c.id)) this.machine.push(c.id); break;
      case 'chooseRow': if (top && top.kind === 'journal') top.activate({ group: 'also', id: c.id }); break;
      case 'setSetting': this.progress.update((d) => { d.settings[c.key] = c.value; }); break;
      case 'resetProgress': if (c.confirmed) this.resetProgress(); break;
      case 'rideHub': if (top && top.kind === 'journal') top.activate({ group: 'also', id: 'ride-hub' }); break;
      default: break;
    }
    this.pump();
  }

  // ---- view-models ---------------------------------------------------------------

  _emitVm(topic, vm) {
    const s = JSON.stringify(vm);
    if (this._vm.get(topic) === s) return;
    this._vm.set(topic, s);
    this.bus.emit(topic, vm);
  }

  publishAll() {
    this.dialogue.publish();
    this._emitVm('vm:hud', this._hud());
    this._emitVm('vm:markers', this._markers());
    this._emitVm('vm:prompt', this._prompt());
    this._emitVm('vm:settings-flags', this._displayFlags());
  }

  _displayFlags() {
    const s = this.progress.doc.settings;
    return { reducedMotion: s.reducedMotion, largerText: s.largerText, highContrast: s.highContrast };
  }

  _hud() {
    const top = this.machine.top;
    if (!top || HUD_HIDDEN.includes(top.kind)) return null;
    const required = this.level.steps.filter((s) => !s.optional);
    const done = required.filter((s) => this.rules.stepsDone.includes(s.id)).length;
    const typing = ['form', 'label', 'editor'].includes(top.kind);
    const chips = [
      { id: 'hint', label: 'Hint', key: keycap('Backquote'), aria: `Show hint. Key Backtick. Hint: Backtick is ${KEY_GESTURE.hint}.` },
    ];
    if (!typing && top.kind !== 'dialogue') {
      chips.push({ id: 'journal', label: 'Journal', key: keycap('q'), aria: `Journal. Key Q. Hint: Q is ${KEY_GESTURE.journal}.` });
    }
    chips.push({ id: 'layout-help', label: 'Layout help', key: keycap('?'), aria: `Layout help. Key question mark. Hint: ? is ${KEY_GESTURE.layoutHelp}.` });
    return {
      title: this.level.title, progress: { done, total: required.length },
      seals: { count: this.progress.doc.seals.length, total: 5 }, chips,
    };
  }

  _markers() {
    const top = this.machine.top;
    if (!top || HUD_HIDDEN.includes(top.kind)) return null;
    const at = (c) => ({ x: c[0] * 16, y: c[1] * 16 });
    const out = { markers: [], floor: [] };
    for (const it of this.data.map.interactions) {
      if (!SHAPE[it.marker] || it.level !== this.level.id) continue;
      if (!this.rules.isVisible(it.id) || !this.rules.requirementsMet(it.id)) continue;
      out.markers.push({ id: it.id, shape: SHAPE[it.marker], state: 'idle', cell: it.cells[0], at: at(it.cells[0]) });
    }
    const active = new Set();
    for (const s of this.machine.layers) {
      if (!s.markers) continue;
      const m = s.markers();
      out.markers.push(...m.markers);
      out.floor.push(...m.floor);
      active.add(s.id);
    }
    for (const sc of this.level.terminal_scenes) {
      const legs = sc.task && sc.task.legs;
      if (sc.kind === 'walk' && legs && legs[0].marker && !active.has(sc.id) && this.rules.holds(`scene_success:${sc.id}`)) {
        for (const l of legs) {
          out.floor.push({ id: `${sc.id}:${l.id}`, cell: l.marker, at: at(l.marker), shape: 'route', state: 'gold' });
        }
      }
    }
    return out;
  }

  _prompt() {
    const top = this.machine.top;
    if (!top || !['hub', 'walk'].includes(top.kind)) return null;
    const it = this._interactionAt();
    if (!it || !this.rules.isVisible(it.id)) return null;
    const person = it.kind === 'npc' || it.kind === 'mira';
    return {
      kind: person ? 'person' : 'device', action: person ? 'Talk' : 'Use',
      key: keycap('Enter'), gesture: KEY_GESTURE.interact, cell: it.cells[0], at: { x: it.cells[0][0] * 16, y: it.cells[0][1] * 16 },
    };
  }
}

export function createSession(params) {
  return new Session(params);
}
