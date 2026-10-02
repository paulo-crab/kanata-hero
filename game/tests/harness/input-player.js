// Scripted input player: turns a readable script into KeyboardEvent-like objects and feeds them to
// `KeyInterpreter.handleKeyEvent(raw, phase)` (contract 4.1) while a fake clock advances in whole
// simulation steps (contract 2.2). Nothing here reads real time or randomness.
import { STEP_MS, CELL_STEPS } from '../../src/shared/layout.js';

/** What the player's Kanata layout turns a gesture into (output names are `event.key`). */
export const GESTURES = {
  'Caps': 'Escape',          // tap Caps
  'Caps+H': 'ArrowLeft',
  'Caps+J': 'ArrowDown',
  'Caps+K': 'ArrowUp',
  'Caps+L': 'ArrowRight',
  'Caps+N': 'Enter',
  'Caps+W': 'Alt+ArrowRight', // Option + Right: the word jump the label scene names
};

const EPS = 1e-6;

export const DIRS = { n: 'ArrowUp', s: 'ArrowDown', e: 'ArrowRight', w: 'ArrowLeft' };

const NAMED_CODES = {
  ArrowUp: 'ArrowUp', ArrowDown: 'ArrowDown', ArrowLeft: 'ArrowLeft', ArrowRight: 'ArrowRight',
  Enter: 'Enter', Escape: 'Escape', Tab: 'Tab', Backspace: 'Backspace', ' ': 'Space', Space: 'Space',
  '`': 'Backquote', Backquote: 'Backquote', '?': 'Slash', '/': 'Slash', ',': 'Comma', ';': 'Semicolon',
};

/**
 * KeyboardEvent-like object for an output name ('ArrowLeft', 'q', '?', 'Backquote', 'Space',
 * 'Alt+ArrowRight', 'Shift+Tab'). Backquote carries `key: '`'` and `code: 'Backquote'`.
 */
export function keyEvent(name, extra = {}) {
  const parts = String(name).split('+');
  const base = name === '+' ? '+' : parts.pop();
  const mods = new Set(parts);
  let key = base;
  if (base === 'Space') key = ' ';
  if (base === 'Backquote') key = '`';
  let code = NAMED_CODES[base];
  if (!code) code = /^[a-z]$/i.test(base) ? `Key${base.toUpperCase()}` : /^\d$/.test(base) ? `Digit${base}` : base;
  if (base === '?') mods.add('Shift');
  return {
    key,
    code,
    repeat: false,
    isComposing: false,
    altKey: mods.has('Alt'),
    ctrlKey: mods.has('Ctrl'),
    metaKey: mods.has('Meta'),
    shiftKey: mods.has('Shift'),
    preventDefault() { this.defaultPrevented = true; },
    defaultPrevented: false,
    ...extra,
  };
}

/** Resolve a gesture name ('Caps+H') or an output name to an output name. */
export function outputOf(token) {
  return Object.prototype.hasOwnProperty.call(GESTURES, token) ? GESTURES[token] : token;
}

export class ScriptedInput {
  /**
   * @param {{target:{handleKeyEvent:(raw:object, phase?:'down'|'up')=>any}, advance:(ms:number)=>void}} p
   *   target: a KeyInterpreter (or any fake with handleKeyEvent); advance: usually `ms => clock.advance(ms)`
   *   followed by `loop.advance(ms)` when a GameLoop is in play.
   */
  constructor({ target, advance }) {
    this.target = target;
    this.advance = advance;
    this.log = [];        // [{op, key, phase?, steps?}] every action, for determinism comparisons
    this.results = [];    // whatever handleKeyEvent returned, in order
    this._held = new Set();
  }

  /** Advance whole simulation steps. */
  wait(steps = 1) {
    this.log.push({ op: 'wait', steps });
    this.advance((steps + EPS) * STEP_MS); // epsilon: floor(ms / STEP_MS) must never lose a step to float error
    return this;
  }

  down(token) {
    const key = outputOf(token);
    this._held.add(key);
    this.log.push({ op: 'key', key, phase: 'down' });
    this.results.push(this.target.handleKeyEvent(keyEvent(key), 'down'));
    return this;
  }

  up(token) {
    const key = outputOf(token);
    this._held.delete(key);
    this.log.push({ op: 'key', key, phase: 'up' });
    this.results.push(this.target.handleKeyEvent(keyEvent(key), 'up'));
    return this;
  }

  /** Key down, hold for `holdSteps` steps, key up. Default is one step. */
  tap(token, holdSteps = 1) {
    this.down(token);
    this.wait(holdSteps);
    this.up(token);
    return this;
  }

  /** Hold one arrow for exactly `cells` cell moves (CELL_STEPS steps each). */
  hold(token, cells = 1) {
    this.down(token);
    this.wait(cells * CELL_STEPS);
    this.up(token);
    return this;
  }

  /** One cell per tap: tap, then finish the step so the next tap is accepted ('busy' otherwise). */
  step(token, cells = 1) {
    for (let i = 0; i < cells; i += 1) {
      this.tap(token, 1);
      this.wait(CELL_STEPS - 1);
    }
    return this;
  }

  /** Type text with Caps released: one tap per character. */
  type(text) {
    for (const ch of text) this.tap(ch === ' ' ? 'Space' : ch, 1);
    return this;
  }

  /** Release anything still down (a script that ends mid-gesture must not leak a held key). */
  releaseAll() {
    for (const k of [...this._held]) this.up(k);
    return this;
  }

  /**
   * Run a script. Items: 'Escape' | 'Caps+H' (tap) | {tap, steps?} | {step, cells?} | {hold, cells?}
   * | {type} | {wait} | {down} | {up}.
   */
  run(script) {
    for (const item of script) {
      if (typeof item === 'string') this.tap(item);
      else if ('tap' in item) this.tap(item.tap, item.steps ?? 1);
      else if ('step' in item) this.step(item.step, item.cells ?? 1);
      else if ('hold' in item) this.hold(item.hold, item.cells ?? 1);
      else if ('type' in item) this.type(item.type);
      else if ('wait' in item) this.wait(item.wait);
      else if ('down' in item) this.down(item.down);
      else if ('up' in item) this.up(item.up);
      else throw new Error(`unknown script item ${JSON.stringify(item)}`);
    }
    return this;
  }
}
