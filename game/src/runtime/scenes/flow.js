// Setup, calibration and arrival scenes (the first minutes). Contract: game/CONTRACTS.md sections 5.1, 7.
import { BaseScene } from './base.js';
import { keycap, observedName } from '../common.js';

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

/** The gesture keycaps drawn on the prompt: the key held (or pressed first), then the key tapped. */
const STEP_KEYS = {
  'caps-h': [{ key: 'Caps', label: 'Caps', held: true }, { key: 'h', label: 'H' }],
  'caps-n': [{ key: 'Caps', label: 'Caps', held: true }, { key: 'n', label: 'N' }],
  'space-a': [{ key: 'Space', label: 'Space', held: true }, { key: 'a', label: 'A' }],
  'space-q': [{ key: 'Space', label: 'Space', held: true }, { key: 'q', label: 'Q' }],
  'shift-hold': [{ key: 'f', label: 'F', held: true }, { key: '/', label: '/' }],
};

const SHORT = { Backspace: 'Bksp', Left: '←', Right: '→', Up: '↑', Down: '↓', Delete: 'Del' };
const cleanLabel = (id) => (id.length === 1 ? id.toUpperCase() : SHORT[id] || id.replace(/-[LR]$/, ''));
const shortLegend = (t) => String(t || '').replace(/\s+([←-↓])/g, '$1').replace(/\s*\|\s*/g, '/');

/** Keyboard diagram for the current step; `plain` draws the keyboard with nothing marked (the setup screen). */
function diagramFor(ctx, cal, stepId, plain = false) {
  const { manifest, input } = ctx;
  if (!manifest || !manifest.keyboard) return null;
  const variant = cal.result().keyboard;
  const spec = plain ? { held: null, target: null, layer: 'base', timing: 'caps-hold' } : (STEP_DIAGRAM[stepId] || STEP_DIAGRAM['caps-h']);
  const timing = ((manifest.json && manifest.json.timings) || []).find((t) => t.id === spec.timing) || {};
  const heldId = spec.held;
  const rows = manifest.keyboard(variant).rows.map((row) => row.filter((k) => k.id !== 'Down'));
  const state = (id) => (id === heldId ? 'layer' : id === spec.target ? 'target' : 'plain');
  // A label has to fit its key at 16 px (four characters per unit of width); the full legends are in Layout help.
  const fits = (text, widthU) => text.length <= Math.floor(widthU * 4.05);
  const characters = (id, widthU) => {
    if (id === heldId) return cleanLabel(id);
    let legend = '';
    try { legend = shortLegend(manifest.keyAt(spec.layer, id, variant).legend); } catch { legend = ''; }
    if (legend && fits(legend, widthU)) return legend;
    const name = cleanLabel(id);
    return fits(name, widthU) ? name : '';
  };
  const build = (mode) => rows.map((row) => row.map((k) => ({
    label: mode === 'positions' ? cleanLabel(k.id) : characters(k.id, k.width_u), state: state(k.id), width_u: k.width_u,
  })));
  const holdMs = timing.hold_ms ? ` about ${timing.hold_ms} ms` : '';
  const out = {
    positions: {
      rows: build('positions'),
      caption: plain ? `The ${variant === 'microsoft' ? 'Microsoft' : 'MacBook'} keyboard as the game draws it.`
        : `Physical positions: hold ${cleanLabel(heldId)}${holdMs}, then tap ${cleanLabel(spec.target)}.`,
    },
    stepId,
    stepCount: input.CALIBRATION_STEPS.length,
  };
  if (!plain) {
    out.characters = {
      rows: build('characters'),
      caption: spec.layer === 'base' ? 'Resulting characters: the base layer.' : `Resulting characters on the ${spec.layer} layer.`,
    };
  }
  return out;
}

const NAMED_KEYS = {
  Down: { key: 'ArrowDown', label: 'Down' },
  Up: { key: 'ArrowUp', label: 'Up' },
};

/**
 * Calibration view-model. One step at a time: `current` is the prompt on screen, `lastSeen` is the output the page
 * saw last, `wrong` explains a key that was not the expected one, `success` reports the step just settled.
 * `phase` is 'steps' while a step is waiting, 'summary' when every step is settled. `confirm` is the skip card.
 */
export function calibrationVm(ctx, cal, ui = {}) {
  const { input, manifest } = ctx;
  const res = cal.result();
  const cur = cal.current;
  const toggle = manifest && manifest.sequences
    ? (manifest.sequences().find((s) => s.id === 'violento-toggle') || {}).label : null;
  const steps = input.CALIBRATION_STEPS.map((s, i) => {
    const [action, key] = STEP_COPY[s.id] || [`To observe ${s.expected}, press it.`, s.expected];
    const status = res.steps[s.id] || 'not_started';
    return {
      id: s.id, number: i + 1, gesture: s.gesture, expected: s.expected, expectedName: key, action,
      hintLine: `${action} Hint: ${key} is ${s.gesture}.`,
      keys: (STEP_KEYS[s.id] || []).map((k) => ({ ...k })),
      status, statusLabel: STATUS_LABEL[status], current: cur === s.id,
    };
  });
  const current = steps.find((s) => s.current) || null;
  return {
    keyboard: res.keyboard,
    phase: current ? 'steps' : 'summary',
    stepCount: steps.length,
    steps,
    current: current ? { ...current, waiting: `Waiting for ${current.expectedName}` } : null,
    lastSeen: ui.lastSeen || null,
    wrong: ui.wrong || null,
    success: ui.success || null,
    confirm: !!ui.confirm,
    skipStep: { key: NAMED_KEYS.Down, gesture: 'tap-hold Caps + J' },
    skipAll: { key: NAMED_KEYS.Up, gesture: 'tap-hold Caps + K' },
    diagram: diagramFor(ctx, cal, cur || 'caps-h'),
    diagramView: 'positions',
    toggleOut: {
      keys: ['Control', 'Alt', 'Meta', 'v'].map((k) => keycap(k)),
      text: `Practice toggle-out: ${toggle || 'Control + Alt + GUI + V'}. The game cannot see whether practice is on.`,
      practice: ctx.progress.doc.flags.includes('practice-confirmed') ? 'player-confirmed' : 'unconfirmed',
    },
  };
}

/** Setup: only the keyboard choice and a Next button. The calibration steps are not listed here. */
export class SetupScene extends BaseScene {
  constructor() {
    super('setup', 'setup');
    this.modal = true;
    this.confirm = false;
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

  /** Both setup and calibration are skipped, only after the explicit confirm card. */
  _skipAll() {
    this._store();
    this.ctx.progress.update((d) => {
      d.setup.done = true;
      if (!d.setup.calibration) {
        d.setup.calibration = { keyboard: this.keyboard, steps: Object.fromEntries(
          this.ctx.input.CALIBRATION_STEPS.map((s) => [s.id, 'skipped'])) };
      }
    });
    this.finish({ next: this.ctx.actions.afterSetup() });
  }

  askSkip() {
    this.confirm = true;
  }

  handle(ev) {
    if (ev.phase === 'up' || ev.repeat) return true;
    const reopened = this.payload && this.payload.reopened;
    if (this.confirm) {
      if (ev.action === 'continue') this._skipAll();
      else if (ev.action === 'skip' || ev.action === 'back') this.confirm = false;
      return true;
    }
    if (ev.action === 'choose' && ev.dir) {
      const i = KEYBOARDS.findIndex((k) => k.id === this.keyboard);
      this.keyboard = KEYBOARDS[(i + 1) % KEYBOARDS.length].id;
    } else if (ev.action === 'continue') {
      this._store();
      if (reopened) this.finish({ success: true });
      else this.finish({ next: 'calibration', payload: { keyboard: this.keyboard } });
    } else if (ev.action === 'skip') {
      if (reopened) { this._store(); this.finish({ success: true }); } else this.askSkip();
    }
    return true;
  }

  viewModel() {
    const cal = new this.ctx.input.Calibration(this.keyboard);
    return {
      keyboard: this.keyboard,
      keyboards: KEYBOARDS.map((k) => ({ ...k, selected: k.id === this.keyboard })),
      confirm: this.confirm,
      diagram: diagramFor(this.ctx, cal, null, true),
    };
  }
}

/** Calibration, one step at a time. Every output that is not the expected one is shown, never silently skipped. */
export class CalibrationScene extends BaseScene {
  constructor() {
    super('calibration', 'calibration');
    this.modal = true;
    this.confirm = false;
    this.lastSeen = null;
    this.wrong = null;
    this.success = null;
    this.keys = { typing: false, enter: 'continue', esc: 'skip', arrows: 'choose', journal: false, hint: false };
  }

  enter(ctx, payload) {
    super.enter(ctx, payload);
    if (this.cal) return;
    const kb = (payload && payload.keyboard) || ctx.progress.doc.settings.keyboard;
    this.cal = new ctx.input.Calibration(kb);
  }

  _expectedName(id) {
    const s = this.ctx.input.CALIBRATION_STEPS.find((x) => x.id === id);
    return (STEP_COPY[id] || [null, s ? s.expected : id])[1];
  }

  _number(id) {
    return this.ctx.input.CALIBRATION_STEPS.findIndex((s) => s.id === id) + 1;
  }

  _done() {
    this.ctx.progress.update((d) => {
      d.setup.done = true;
      d.setup.calibration = this.cal.result();
    });
    this.finish({ next: this.ctx.actions.afterSetup() });
  }

  /** The Skip this step button or Down. A step left alone is recorded as Skipped. */
  skipStep() {
    const id = this.cal.current;
    if (id === null) return;
    this.cal.skipCurrent();
    this.wrong = null;
    this.success = { skipped: true, stepId: id, text: `Skipped step ${this._number(id)}.` };
    this.ctx.bus.emit('vm:announce', { text: this.success.text });
  }

  /** The Skip calibration button or Up: only opens the confirm card. */
  askSkip() {
    this.confirm = true;
  }

  _observe(ev) {
    const name = observedName(ev);
    const id = this.cal.current;
    this.lastSeen = { name };
    const hit = this.cal.observe(ev);
    if (hit) {
      this.wrong = null;
      this.success = { stepId: id, text: `Step ${this._number(id)} done: ${name} observed.`, name };
      this.ctx.bus.emit('vm:announce', { text: this.cal.current === null ? 'Calibration finished. Press Return to continue.' : this.success.text });
      return;
    }
    const want = this._expectedName(id);
    const hint = id === 'caps-h' && ev.output === 'Escape'
      ? 'That was a tap. Hold Caps a moment, then press H.' : null;
    this.wrong = { got: name, expected: want, text: `Got ${name}, expected ${want}.`, hint };
    this.success = null;
    this.ctx.bus.emit('vm:announce', { text: `${this.wrong.text}${hint ? ` ${hint}` : ''}` });
  }

  handle(ev) {
    if (ev.phase === 'up' || ev.repeat) return true;
    if (ev.confidence && ev.confidence !== 'observed') return true;
    if (this.confirm) {
      if (ev.action === 'continue') { this.cal.skipAll(); this._done(); }
      else if (ev.action === 'skip' || ev.action === 'back') this.confirm = false;
      return true;
    }
    if (this.cal.current === null) {
      if (ev.action === 'continue') this._done();
      return true;
    }
    if (ev.output === 'ArrowDown') this.skipStep();
    else if (ev.output === 'ArrowUp') this.askSkip();
    else this._observe(ev);
    return true;
  }

  viewModel() {
    return calibrationVm(this.ctx, this.cal, {
      lastSeen: this.lastSeen, wrong: this.wrong, success: this.success, confirm: this.confirm,
    });
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
