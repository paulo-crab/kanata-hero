// Input module public surface. Contract: game/CONTRACTS.md section 4.
// Stubs: workstream B replaces the throwing bodies.
const nyi = () => {
  throw new Error('not implemented');
};

/** Pure: raw KeyboardEvent-like to an InterpretedEvent without `action`. */
export function interpretKey(raw, phase = 'down', t = 0) { nyi(); }

export class KeyInterpreter {
  constructor(params) { nyi(); }
  handleKeyEvent(raw, phase = 'down') { nyi(); }
  attach(target) { nyi(); }
  detach() { nyi(); }
  heldDirection() { nyi(); }
  playerConfirm(sceneId, choice) { nyi(); }
}

export const BINDINGS = [];
export function resolveAction(interp, ctx) { nyi(); }

export const CALIBRATION_STEPS = [
  { id: 'caps-h', gesture: 'Caps + H', expected: 'ArrowLeft' },
  { id: 'caps-n', gesture: 'Caps + N', expected: 'Enter' },
  { id: 'space-a', gesture: 'Space + A', expected: '1' },
  { id: 'space-q', gesture: 'Space + Q', expected: '!' },
  { id: 'shift-hold', gesture: 'F (home-row Shift), then /', expected: '?' },
];

export class Calibration {
  constructor(keyboard = 'macbook') { nyi(); }
  setKeyboard(kind) { nyi(); }
  get current() { nyi(); }
  observe(ev) { nyi(); }
  skip(stepId) { nyi(); }
  skipCurrent() { nyi(); }
  skipAll() { nyi(); }
  result() { nyi(); }
  static fromResult(result) { nyi(); }
}

export class LayoutManifest {
  constructor(json) { nyi(); }
  tabs() { nyi(); }
  variants() { nyi(); }
  keyboard(variant) { nyi(); }
  keyAt(tab, keyId, variant) { nyi(); }
  keyDetail(tab, keyId, variant) { nyi(); }
  gesture(inventoryId) { nyi(); }
  sequences() { nyi(); }
  silencedInPractice() { nyi(); }
  hasKey(id) { nyi(); }
}
export function layoutHelpModel(manifest, state) { nyi(); }

export const HINT_CARD_TEXT =
  'Using the hint here forfeits the third star for this scene. Press Return to show the hint, or Esc to keep it.';

export class HintGate {
  constructor(opts = {}) { nyi(); }
  request(params) { nyi(); }
  confirm() { nyi(); }
  cancel() { nyi(); }
  uses() { nyi(); }
}
