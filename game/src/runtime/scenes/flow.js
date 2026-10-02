// Setup, calibration and arrival scenes (the first minutes). Contract: game/CONTRACTS.md sections 5.1, 7.
import { BaseScene } from './base.js';
import { keycap } from '../common.js';

const KEYBOARDS = [
  { id: 'macbook', label: 'MacBook keyboard' },
  { id: 'microsoft', label: 'Microsoft keyboard (Alt as Command, Windows as Option)' },
];

const STEP_COPY = {
  'caps-h': ['To move left, you need to press Left Arrow.', 'Left Arrow'],
  'caps-n': ['To interact or continue, you need to press Return.', 'Return'],
  'space-a': ['To type the digit one, you need to press 1.', '1'],
  'space-q': ['To type an exclamation mark, you need to press !.', '!'],
  'shift-hold': ['To type a question mark, you need to press ?.', '?'],
};

const STATUS_LABEL = { not_started: 'Not started', observed: 'Observed output', skipped: 'Skipped' };

/** Per calibration step: the manifest gesture it exercises, the held key, the tapped key and the layer drawn. */
const STEP_DIAGRAM = {
  'caps-h': { gesture: 'N01', held: 'Caps', target: 'h', layer: 'nav', timing: 'caps-hold' },
  'caps-n': { gesture: 'N17', held: 'Caps', target: 'n', layer: 'nav', timing: 'caps-hold' },
  'space-a': { gesture: 'S01', held: 'Space', target: 'a', layer: 'numbers-symbols', timing: 'space-hold' },
  'space-q': { gesture: 'S12', held: 'Space', target: 'q', layer: 'numbers-symbols', timing: 'space-hold' },
  'shift-hold': { gesture: 'B03', held: 'f', target: '/', layer: 'base', timing: 'home-row-hold' },
};

const cleanLabel = (id) => (id.length === 1 ? id.toUpperCase() : id.replace(/-[LR]$/, ''));

function diagramFor(ctx, cal, stepId) {
  const { manifest, input } = ctx;
  if (!manifest || !manifest.keyboard) return null;
  const variant = cal.result().keyboard;
  const spec = STEP_DIAGRAM[stepId] || STEP_DIAGRAM['caps-h'];
  const timing = ((manifest.json && manifest.json.timings) || []).find((t) => t.id === spec.timing) || {};
  const heldId = spec.held;
  const rows = manifest.keyboard(variant).rows.map((row) => row.filter((k) => k.id !== 'Down'));
  const state = (id) => (id === heldId ? 'layer' : id === spec.target ? 'target' : 'plain');
  const characters = (id) => {
    if (id === heldId) return cleanLabel(id);
    try { return manifest.keyAt(spec.layer, id, variant).legend || cleanLabel(id); } catch { return cleanLabel(id); }
  };
  const build = (mode) => rows.map((row) => row.map((k) => ({
    label: mode === 'positions' ? cleanLabel(k.id) : characters(k.id), state: state(k.id), width_u: k.width_u,
  })));
  const holdMs = timing.hold_ms ? ` about ${timing.hold_ms} ms` : '';
  return {
    positions: {
      rows: build('positions'),
      caption: `Physical positions: hold ${cleanLabel(heldId)}${holdMs}, then tap ${cleanLabel(spec.target)}.`,
    },
    characters: {
      rows: build('characters'),
      caption: spec.layer === 'base' ? 'Resulting characters: the base layer.' : `Resulting characters on the ${spec.layer} layer.`,
    },
    stepId,
    stepCount: input.CALIBRATION_STEPS.length,
  };
}


export function calibrationVm(ctx, cal) {
  const { input, manifest } = ctx;
  const res = cal.result();
  const cur = cal.current;
  const toggle = manifest && manifest.sequences
    ? (manifest.sequences().find((s) => s.id === 'violento-toggle') || {}).label : null;
  const inventory = (manifest && manifest.gesture) ? (id) => { try { return manifest.gesture(id); } catch { return null; } } : () => null;
  return {
    keyboard: res.keyboard,
    diagram: diagramFor(ctx, cal, cur || 'caps-h'),
    steps: input.CALIBRATION_STEPS.map((s) => {
      const [action, key] = STEP_COPY[s.id] || [`To observe ${s.expected}, press it.`, s.expected];
      const status = res.steps[s.id] || 'not_started';
      return {
        id: s.id, gesture: s.gesture, expected: s.expected,
        hintLine: `${action} Hint: ${key} is ${s.gesture}.`,
        status, statusLabel: STATUS_LABEL[status], current: cur === s.id,
        // The game cannot see a gesture the manifest rates player_confirmed; every calibration gesture is observable.
        confirmable: status === 'not_started' && cur === s.id
          && ((inventory((STEP_DIAGRAM[s.id] || {}).gesture) || {}).verification === 'player_confirmed'),
      };
    }),
    diagramView: 'positions',
    toggleOut: {
      keys: ['Control', 'Alt', 'Meta', 'v'].map((k) => keycap(k)),
      text: `Practice toggle-out: ${toggle || 'Control + Alt + GUI + V'}. The game cannot see whether practice is on.`,
      practice: ctx.progress.doc.flags.includes('practice-confirmed') ? 'player-confirmed' : 'unconfirmed',
    },
  };
}


export class SetupScene extends BaseScene {
  constructor() {
    super('setup', 'setup');
    this.modal = true;
    this.keys = { typing: false, enter: 'continue', esc: 'skip', arrows: 'choose', journal: false, hint: false };
  }

  enter(ctx, payload) {
    super.enter(ctx, payload);
    this.keyboard = ctx.progress.doc.settings.keyboard;
  }

  select(id) {
    if (KEYBOARDS.some((k) => k.id === id)) this.keyboard = id;
  }

  _store() {
    this.ctx.progress.update((d) => { d.settings.keyboard = this.keyboard; });
  }

  _next(skipped) {
    const reopened = this.payload && this.payload.reopened;
    if (skipped) {
      this.ctx.progress.update((d) => {
        d.setup.done = true;
        if (!d.setup.calibration) {
          d.setup.calibration = { keyboard: this.keyboard, steps: Object.fromEntries(
            this.ctx.input.CALIBRATION_STEPS.map((s) => [s.id, 'skipped'])) };
        }
      });
    }
    if (reopened) this.finish({ success: true });
    else if (skipped) this.finish({ next: this.ctx.actions.afterSetup() });
    else this.finish({ next: 'calibration', payload: { keyboard: this.keyboard } });
  }

  handle(ev) {
    if (ev.phase === 'up' || ev.repeat) return true;
    if (ev.action === 'choose' && ev.dir) {
      const i = KEYBOARDS.findIndex((k) => k.id === this.keyboard);
      this.keyboard = KEYBOARDS[(i + 1) % KEYBOARDS.length].id;
    } else if (ev.action === 'continue') {
      this._store();
      this._next(false);
    } else if (ev.action === 'skip') {
      this._store();
      this._next(true);
    }
    return true;
  }

  /** The setup screen also shows the calibration steps and the keyboard diagram (one panel, as in the kit). */
  extraViewModels() {
    const cal = new this.ctx.input.Calibration(this.keyboard);
    return { 'vm:calibration': calibrationVm(this.ctx, cal) };
  }

  viewModel() {
    return {
      keyboard: this.keyboard,
      keyboards: KEYBOARDS.map((k) => ({ ...k, selected: k.id === this.keyboard })),
    };
  }
}

export class CalibrationScene extends BaseScene {
  constructor() {
    super('calibration', 'calibration');
    this.modal = true;
    this.keys = { typing: false, enter: 'continue', esc: 'skip', arrows: 'choose', journal: false, hint: false };
  }

  enter(ctx, payload) {
    super.enter(ctx, payload);
    if (this.cal) return;
    const kb = (payload && payload.keyboard) || ctx.progress.doc.settings.keyboard;
    this.cal = new ctx.input.Calibration(kb);
  }

  /** Mouse selection: a step picked out of order leaves the steps before it skipped (a step left alone is Skipped). */
  choose(id) {
    const { CALIBRATION_STEPS } = this.ctx.input;
    const at = CALIBRATION_STEPS.findIndex((s) => s.id === id);
    if (at < 0) return;
    for (const s of CALIBRATION_STEPS.slice(0, at)) this.cal.skip(s.id);
  }

  _done() {
    this.ctx.progress.update((d) => {
      d.setup.done = true;
      d.setup.calibration = this.cal.result();
    });
    this.finish({ next: this.ctx.actions.afterSetup() });
  }

  handle(ev) {
    if (ev.phase === 'up' || ev.repeat) return true;
    if (ev.action === 'skip' || ev.output === 'Escape') {
      this.cal.skipAll();
      this._done();
      return true;
    }
    const hit = this.cal.observe(ev);
    if (hit) {
      if (this.cal.current === null) this.ctx.bus.emit('vm:announce', { text: 'Calibration finished. Press Return to continue.' });
      return true;
    }
    if (this.cal.current === null && ev.action === 'continue') {
      this._done();
    } else if (ev.action === 'choose' && ev.dir === 's') {
      this.cal.skipCurrent();
    } else if (ev.action === 'continue') {
      this.cal.skipAll();
      this._done();
    }
    return true;
  }

  viewModel() {
    return calibrationVm(this.ctx, this.cal);
  }
}

export class ArrivalScene extends BaseScene {
  constructor() {
    super('arrival', 'arrival');
    this.modal = true;
    this.keys = { typing: false, enter: 'none', esc: 'none', arrows: 'none', journal: false, hint: false };
    this.sequence = ['closed', 'half', 'open'];
  }

  enter(ctx, payload) {
    super.enter(ctx, payload);
    if (this.started) return;
    this.started = true;
    ctx.bus.emit('intent', { type: 'playStateSet', placement: 'elevator', sequence: this.sequence });
  }

  onEngine(topic, p) {
    if (topic !== 'engine:stateset-done' || p.placement !== 'elevator' || p.state !== 'open' || this.arrived) return;
    this.arrived = true;
    const spawn = this.ctx.data.map.spawns.find((s) => s.id === 'arrival');
    this.ctx.bus.emit('intent', { type: 'moveAvatar', path: [spawn.cell], facing: spawn.facing });
    this.finish({ next: 'hub' });
  }

  handle() {
    return true;
  }
}
