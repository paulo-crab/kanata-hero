// Calibration engine. Contract: game/CONTRACTS.md 4.3. Proves the setup without claiming detection:
// a step is `observed` when the browser reported the expected output on the current step, and says
// nothing about which keys were used.

export const CALIBRATION_STEPS = Object.freeze([
  { id: 'caps-h', gesture: 'Caps + H', expected: 'ArrowLeft' },
  { id: 'caps-n', gesture: 'Caps + N', expected: 'Enter' },
  { id: 'space-a', gesture: 'Space + A', expected: '1' },
  { id: 'space-q', gesture: 'Space + Q', expected: '!' },
  { id: 'shift-hold', gesture: 'F (home-row Shift), then /', expected: '?' },
].map(Object.freeze));

/** @typedef {'not_started'|'observed'|'skipped'} StepStatus */
export const STEP_STATUSES = Object.freeze(['not_started', 'observed', 'skipped']);

/** Status copy. No text says detected, verified or which keys were used. */
export const STATUS_LABELS = Object.freeze({
  not_started: 'Not started',
  observed: 'Observed output',
  skipped: 'Skipped',
});

/** Keyboard types chosen in setup. Microsoft: Alt acts as Command, Windows as Option (manifest remap). */
export const KEYBOARD_TYPES = Object.freeze([
  { id: 'macbook', label: 'MacBook (US ANSI), the default' },
  { id: 'microsoft', label: 'Microsoft keyboard: Alt is Command, Windows is Option' },
]);

const KEYBOARD_IDS = KEYBOARD_TYPES.map((k) => k.id);

export class Calibration {
  constructor(keyboard = 'macbook') {
    this._keyboard = 'macbook';
    this._status = Object.fromEntries(CALIBRATION_STEPS.map((s) => [s.id, 'not_started']));
    this.setKeyboard(keyboard);
  }

  get keyboard() {
    return this._keyboard;
  }

  setKeyboard(kind) {
    if (!KEYBOARD_IDS.includes(kind)) throw new RangeError(`Unknown keyboard type: ${kind}`);
    this._keyboard = kind;
  }

  /** First step still not started, or null when every step is settled. */
  get current() {
    const step = CALIBRATION_STEPS.find((s) => this._status[s.id] === 'not_started');
    return step ? step.id : null;
  }

  get finished() {
    return this.current === null;
  }

  /** @returns {{stepId:string, status:'observed'}|null} null when the event does not settle the current step */
  observe(ev) {
    const id = this.current;
    if (id === null || !ev) return null;
    if (ev.confidence !== 'observed' || ev.phase !== 'down' || ev.repeat) return null;
    const step = CALIBRATION_STEPS.find((s) => s.id === id);
    if (ev.output !== step.expected) return null;
    this._status[id] = 'observed';
    return { stepId: id, status: 'observed' };
  }

  /** Skip one step that has not been started. An observed step stays observed. */
  skip(stepId) {
    if (!(stepId in this._status)) throw new RangeError(`Unknown calibration step: ${stepId}`);
    if (this._status[stepId] !== 'not_started') return null;
    this._status[stepId] = 'skipped';
    return { stepId, status: 'skipped' };
  }

  skipCurrent() {
    const id = this.current;
    return id === null ? null : this.skip(id);
  }

  skipAll() {
    const done = [];
    for (const s of CALIBRATION_STEPS) {
      const r = this.skip(s.id);
      if (r) done.push(r.stepId);
    }
    return done;
  }

  /** Rows for a view-model: step data plus status, status label and the current flag. */
  rows() {
    const cur = this.current;
    return CALIBRATION_STEPS.map((s) => ({
      id: s.id,
      gesture: s.gesture,
      expected: s.expected,
      status: this._status[s.id],
      statusLabel: STATUS_LABELS[this._status[s.id]],
      current: s.id === cur,
    }));
  }

  /** @returns {{keyboard:string, steps:Object<string,string>}} plain JSON, safe for progress storage */
  result() {
    return { keyboard: this._keyboard, steps: { ...this._status } };
  }

  /** Tolerant of stored data: unknown keyboards fall back to macbook, unknown steps and statuses are dropped. */
  static fromResult(result) {
    const keyboard = result && KEYBOARD_IDS.includes(result.keyboard) ? result.keyboard : 'macbook';
    const cal = new Calibration(keyboard);
    const steps = (result && result.steps) || {};
    for (const s of CALIBRATION_STEPS) {
      if (STEP_STATUSES.includes(steps[s.id])) cal._status[s.id] = steps[s.id];
    }
    return cal;
  }
}
