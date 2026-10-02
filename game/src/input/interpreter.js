// Key interpreter: KeyboardEvent-like objects to InterpretedEvent. Contract: game/CONTRACTS.md 4.1.
// Pure over plain objects (tests never touch the DOM); KeyInterpreter.attach is the only DOM adapter.
// The interpreter knows nothing about levels or scenes. It never claims which physical key or which
// Kanata layer produced an output: ArrowLeft from Caps + H and from Right Command is the same event.
import { ARROW_DIRS, resolveAction } from './bindings.js';

/** Keys that carry no output of their own and are never delivered. */
const IGNORED_KEYS = new Set([
  'Shift', 'Control', 'Alt', 'Meta', 'AltGraph', 'CapsLock', 'Fn', 'FnLock', 'OS',
  'Dead', 'Process', 'Unidentified', 'Compose',
]);

const NO_MODS = Object.freeze({ alt: false, ctrl: false, meta: false, shift: false });

/** The output name for a raw event: event.key, with ' ' -> 'Space' and the grave key -> 'Backquote'. */
function outputOf(raw) {
  if (raw.code === 'Backquote') return 'Backquote';
  if (raw.key === ' ') return 'Space';
  return raw.key;
}

/** Text a text field would receive. '?' and Backquote are reserved commands and are never text. */
function textOf(raw, output, mods) {
  if (output === 'Backquote' || output === '?') return null;
  if (mods.ctrl || mods.meta) return null;
  if (output === 'Space') return ' ';
  if (typeof raw.key === 'string' && [...raw.key].length === 1) return raw.key;
  return null;
}

function comboOf(output, mods) {
  const parts = [];
  if (mods.ctrl) parts.push('Ctrl');
  if (mods.alt) parts.push('Alt');
  if (mods.meta) parts.push('Meta');
  parts.push(output);
  return parts.join('+');
}

/** True for events the game never sees: composition, IME placeholders and bare modifier keys. */
export function isIgnoredKey(raw) {
  if (!raw || typeof raw.key !== 'string' || raw.key === '') return true;
  if (raw.isComposing) return true;
  // Backquote is keyed by code, so a dead-key input source (key 'Dead', keyCode 229) still reaches Hint.
  if (raw.code === 'Backquote') return false;
  if (raw.keyCode === 229) return true;
  return IGNORED_KEYS.has(raw.key);
}

/**
 * Pure: raw KeyboardEvent-like to an InterpretedEvent without a resolved action.
 * @returns {object|null} null for composing events and keys the game ignores
 */
export function interpretKey(raw, phase = 'down', t = 0) {
  if (isIgnoredKey(raw)) return null;
  const mods = {
    alt: !!raw.altKey,
    ctrl: !!raw.ctrlKey,
    meta: !!raw.metaKey,
    shift: !!raw.shiftKey,
  };
  const output = outputOf(raw);
  return {
    output,
    text: textOf(raw, output, mods),
    confidence: 'observed',
    repeat: !!raw.repeat,
    t,
    phase: phase === 'up' ? 'up' : 'down',
    combo: comboOf(output, mods),
    mods,
    code: typeof raw.code === 'string' ? raw.code : '',
    action: null,
    dir: null,
  };
}

/**
 * Is this output claimed by the context, so preventDefault is allowed while the surface has focus?
 * Never true for Tab or for a Control or Command chord (the browser keeps those).
 */
export function isClaimed(ev, ctx) {
  if (!ctx || !ctx.surfaceFocused) return false;
  if (ev.phase !== 'down') return false;
  if (ev.output === 'Tab') return false;
  if (ev.mods.ctrl || ev.mods.meta) return false;
  if (ev.action) return true;
  if ((ctx.consumes || []).includes(ev.output)) return true;
  if (ev.output === 'Escape' && ctx.esc === 'text') return true;
  if (ev.output === 'Enter' && ctx.enter === 'text') return true;
  if (ev.output in ARROW_DIRS && ctx.arrows === 'text') return true;
  if (ctx.typing && ev.text !== null) return true;
  return false;
}

export class KeyInterpreter {
  /** @param {{clock:object, bus:object, getContext:()=>object, onEvent?:(e:object)=>void}} p */
  constructor({ clock, bus, getContext, onEvent } = {}) {
    if (!clock) throw new TypeError('KeyInterpreter needs a clock');
    this.clock = clock;
    this.bus = bus || null;
    this.getContext = getContext || (() => null);
    this.onEvent = onEvent || null;
    this._held = []; // arrow dirs currently down, oldest first
    this._target = null;
    this._onDown = (e) => this._dom(e, 'down');
    this._onUp = (e) => this._dom(e, 'up');
    this._onBlur = () => this.clearHeld();
  }

  /** @returns {object|null} the InterpretedEvent, or null when composing or a key the game ignores */
  handleKeyEvent(raw, phase = 'down') {
    const ev = interpretKey(raw, phase, this.clock.now());
    if (!ev) return null;
    this._track(ev);
    if (ev.phase === 'down') {
      const r = resolveAction(ev, this.getContext() || null);
      ev.action = r.action;
      ev.dir = r.dir;
    }
    if (this.bus) this.bus.emit('input:event', ev);
    if (this.onEvent) this.onEvent(ev);
    return ev;
  }

  /** Adds keydown and keyup listeners. preventDefault only when the context claims the output. */
  attach(target = globalThis.window) {
    if (!target || typeof target.addEventListener !== 'function') throw new TypeError('attach needs an EventTarget');
    this.detach();
    this._target = target;
    target.addEventListener('keydown', this._onDown);
    target.addEventListener('keyup', this._onUp);
    target.addEventListener('blur', this._onBlur);
  }

  detach() {
    const target = this._target;
    if (!target) return;
    target.removeEventListener('keydown', this._onDown);
    target.removeEventListener('keyup', this._onUp);
    target.removeEventListener('blur', this._onBlur);
    this._target = null;
    this.clearHeld();
  }

  /** Last held arrow ('n','s','e','w') from down and up phases, never from OS auto-repeat; or null. */
  heldDirection() {
    return this._held.length ? this._held[this._held.length - 1] : null;
  }

  /** Forget held arrows (window blur, scene change that clears the held key). */
  clearHeld() {
    this._held.length = 0;
  }

  /** The player says they did the gesture. Never an observed event. */
  playerConfirm(sceneId, choice) {
    if (!['did', 'did_not', 'skip'].includes(choice)) throw new RangeError(`Unknown choice: ${choice}`);
    const ev = {
      output: 'PlayerConfirm',
      text: null,
      confidence: 'player_confirmed',
      repeat: false,
      t: this.clock.now(),
      phase: 'down',
      combo: 'PlayerConfirm',
      mods: { ...NO_MODS },
      code: '',
      action: null,
      dir: null,
      sceneId,
      choice,
    };
    if (this.bus) this.bus.emit('input:event', ev);
    if (this.onEvent) this.onEvent(ev);
    return ev;
  }

  _track(ev) {
    const dir = ARROW_DIRS[ev.output];
    if (!dir) return;
    if (ev.mods.alt || ev.mods.ctrl || ev.mods.meta || ev.mods.shift) return;
    if (ev.phase === 'down') {
      if (ev.repeat) return;
      this._held = this._held.filter((d) => d !== dir);
      this._held.push(dir);
    } else {
      this._held = this._held.filter((d) => d !== dir);
    }
  }

  _dom(e, phase) {
    const ev = this.handleKeyEvent(e, phase);
    if (!ev) return;
    if (phase === 'down' && isClaimed(ev, this.getContext() || null) && typeof e.preventDefault === 'function') {
      e.preventDefault();
    }
  }
}
