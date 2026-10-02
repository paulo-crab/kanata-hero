// Hub and walk scenes (open-world input). Contract: game/CONTRACTS.md sections 5.1 and 5.5.
import { BaseScene, handleWorldInput } from './base.js';
import {
  DIR_OUTPUT, distanceMap, observedName, CONFIDENCE_LABEL,
} from '../common.js';

const WORLD_KEYS = {
  typing: false, enter: 'interact', esc: 'none', arrows: 'move', journal: true, hint: true, consumes: [],
};

export class HubScene extends BaseScene {
  constructor() {
    super('hub', 'hub');
    this.keys = { ...WORLD_KEYS };
  }

  enter(ctx, payload) {
    super.enter(ctx, payload);
    // The avatar lives in the World, so a restore only has to clear the held key.
    ctx.held = null;
    ctx.world.avatar.setHeld(null);
  }

  handle(ev) {
    return handleWorldInput(this.ctx, ev);
  }

  snapshot() {
    const a = this.ctx.world.avatar;
    const step = this.ctx.rules.currentStep;
    return {
      cell: [...a.cell], facing: a.facing, held: null,
      stepId: step ? step.id : null, objective: step ? step.objective : null,
    };
  }
}

/** Walk scene of level 01: o01-loop (legs), o01-four-stops (ordered stops), o01-unprompted (recall legs). */
export class WalkScene extends BaseScene {
  constructor(def, ctx) {
    super(def.id, 'walk');
    this.def = def;
    this.ctx = ctx;
    this.keys = { ...WORLD_KEYS };
    this.idx = 0;
    this.labelDone = false;
    this.popupClosed = false;
    this.reached = false;
    this._off = [];
    const t = def.task || {};
    if (t.legs) this.targets = t.legs.map((l) => (l.marker || l.to));
    else if (t.stops) this.targets = t.stops.map((s) => s.cell);
    else this.targets = [];
    this.total = this.targets.length;
  }

  get positionCue() {
    return this.def.position_cue !== false;
  }

  enter(ctx, payload) {
    super.enter(ctx, payload);
    if (payload && payload.restore) return;
    if (!this._entered) {
      this._entered = true;
      this.idx = Math.min((payload && payload.progress) || 0, this.total);
      this._off.push(ctx.bus.on('scene:success', (e) => {
        if (e.sceneId === this._labelSceneId()) {
          this.labelDone = true;
          this._advanceStops();
        }
      }));
      this._off.push(ctx.bus.on('dialogue:closed', (e) => this._popupClosed(e)));
    }
    this.cell = [...ctx.world.avatar.cell];
    this._dist = null;
  }

  exit() {
    for (const off of this._off) off();
    this._off = [];
    return this.result;
  }

  handle(ev) {
    return handleWorldInput(this.ctx, ev);
  }

  _labelSceneId() {
    const stops = (this.def.task && this.def.task.stops) || [];
    const s = stops.find((x) => x.triggers_scene);
    return s ? s.triggers_scene : null;
  }

  _target() {
    return this.targets[Math.min(this.idx, this.total - 1)];
  }

  _distance() {
    const key = `${this.idx}`;
    if (!this._dist || this._distKey !== key) {
      const w = this.ctx.world;
      this._dist = distanceMap(this._target(), (x, y) => w.isBlocked(x, y));
      this._distKey = key;
    }
    return this._dist;
  }

  onEngine(topic, payload) {
    if (topic !== 'engine:step-complete' || this.finished) return;
    const prev = this.cell;
    const cell = payload.cell;
    this.cell = [...cell];
    const dist = this._distance();
    const correct = dist(cell) < dist(prev);
    const output = DIR_OUTPUT[payload.dir] || DIR_OUTPUT[payload.facing];
    this.ctx.evidence.record(this.id, { output, correct, critical: false });
    this.ctx.bus.emit('scene:feedback', { sceneId: this.id, observed: output, line: `Step ${payload.dir}` });
    this.ctx.bus.emit('vm:feedback', {
      gesture: null,
      observed: `${observedName({ output })} observed`,
      effect: { n: 'Step north', s: 'Step south', e: 'Step east', w: 'Step west' }[payload.dir] || 'Step',
      confidence: 'observed',
      confidenceLabel: CONFIDENCE_LABEL[this.def.confidence] || 'Output observed',
    });
    this._reachCheck(cell);
  }

  _same(a, b) {
    return a[0] === b[0] && a[1] === b[1];
  }

  _reachCheck(cell) {
    const kind = this.def.task;
    if (kind.stops) return this._reachStops(cell);
    if (kind.legs && kind.legs[0].target_interaction) return this._reachRecall(cell);
    if (this._same(cell, this._target())) this._legDone();
    return undefined;
  }

  _legDone() {
    this.idx += 1;
    this._progress();
    if (this.idx >= this.total) this._success();
  }

  _progress() {
    this.ctx.bus.emit('scene:progress', { sceneId: this.id, done: this.idx, total: this.total });
  }

  _success() {
    this.ctx.evidence.finish(this.id, true);
    this.ctx.bus.emit('scene:success', { sceneId: this.id });
    this.finish({ success: true });
  }

  _reachStops(cell) {
    const stop = this.def.task.stops[this.idx];
    if (!stop || !this._same(cell, stop.cell)) return;
    if (stop.triggers_scene && !this.labelDone) {
      this._openLabel(stop);
      return;
    }
    this._legDone();
  }

  _openLabel(stop) {
    if (this.ctx.machine.canPush('label')) this.ctx.machine.push('label', { sceneId: stop.triggers_scene });
  }

  /** Called when the label scene succeeded (or the walk scene regains focus after it). */
  _advanceStops() {
    const stops = this.def.task.stops;
    if (!stops) return;
    const stop = stops[this.idx];
    if (stop && stop.triggers_scene && this.labelDone && this._same(this.cell, stop.cell)) this._legDone();
  }

  /** Interact on a pending stop re-opens its label scene. */
  openPending() {
    const stops = this.def.task.stops;
    if (!stops) return false;
    const stop = stops[this.idx];
    if (stop && stop.triggers_scene && !this.labelDone && this._same(this.ctx.world.avatar.cell, stop.cell)) {
      this._openLabel(stop);
      return true;
    }
    return false;
  }

  _reachRecall(cell) {
    if (this.idx === 0 && this._same(cell, this.targets[0])) {
      this.reached = true;
      if (this.popupClosed) this._legDone();
    } else if (this.idx === 1 && this._same(cell, this.targets[1])) {
      this._legDone();
    }
  }

  _popupClosed(e) {
    if (!this.def.task.popup || this.idx !== 0 || !this.reached || this.popupClosed) return;
    if (e.id !== 'o01.d.reminder') return;
    this.popupClosed = true;
    this.ctx.evidence.record(this.id, { output: e.by === 'skip' ? 'Escape' : 'Enter', correct: true, critical: false });
    this._legDone();
  }

  /** Route markers for vm:markers (the session adds conversation, terminal and glitch markers). */
  markers() {
    const out = { markers: [], floor: [] };
    if (!this.positionCue) return out;
    const t = this.def.task;
    const at = (c) => ({ x: c[0] * 16, y: c[1] * 16 });
    if (t.legs && t.legs[0].marker) {
      t.legs.forEach((l, i) => {
        out.floor.push({
          id: `${this.id}:${l.id}`, cell: l.marker, at: at(l.marker), shape: 'route',
          state: i < this.idx ? 'gold' : 'teal',
        });
      });
    } else if (t.stops) {
      t.stops.forEach((s, i) => {
        out.markers.push({
          id: s.interaction, cell: s.cell, at: at(s.cell), shape: 'route', state: i < this.idx ? 'reached' : 'idle',
        });
      });
    }
    return out;
  }

  snapshot() {
    return { idx: this.idx };
  }
}
