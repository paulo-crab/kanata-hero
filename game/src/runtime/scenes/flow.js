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
    const { input, manifest } = this.ctx;
    const res = this.cal.result();
    const cur = this.cal.current;
    const toggle = manifest && manifest.sequences
      ? (manifest.sequences().find((s) => s.id === 'violento-toggle') || {}).label : null;
    return {
      steps: input.CALIBRATION_STEPS.map((s) => {
        const [action, key] = STEP_COPY[s.id] || [`To observe ${s.expected}, press it.`, s.expected];
        const status = res.steps[s.id] || 'not_started';
        return {
          id: s.id, gesture: s.gesture, expected: s.expected,
          hintLine: `${action} Hint: ${key} is ${s.gesture}.`,
          status, statusLabel: STATUS_LABEL[status], current: cur === s.id,
        };
      }),
      diagramView: 'positions',
      toggleOut: {
        keys: ['Control', 'Alt', 'Meta', 'v'].map((k) => keycap(k)),
        text: `Practice toggle-out: ${toggle || 'Control + Alt + GUI + V'}. The game cannot see whether practice is on.`,
        practice: this.ctx.progress.doc.flags.includes('practice-confirmed') ? 'player-confirmed' : 'unconfirmed',
      },
    };
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
