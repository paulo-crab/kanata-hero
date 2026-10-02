// Hint-use recording and the recall-scene star-forfeit card. Contract: game/CONTRACTS.md 4.5.
// Standard difficulty only. Guided and variation scenes record the hint at once and lose nothing.
// A recall scene shows the card first; the third star is forfeited only after Return confirms.

export const HINT_CARD_TEXT =
  'Using the hint here forfeits the third star for this scene. Press Return to show the hint, or Esc to keep it.';

const PHASES = ['guided', 'variation', 'recall'];

export class HintGate {
  /** @param {{ difficulty?: 'standard' }} [opts] */
  constructor(opts = {}) {
    const difficulty = opts.difficulty || 'standard';
    if (difficulty !== 'standard') throw new RangeError(`Difficulty not supported in this build: ${difficulty}`);
    this._uses = [];
    this._pending = null;
  }

  /** @returns {{needsCard:boolean, card?:{text:string, confirmKey:'Enter'}}} */
  request({ sceneId, phase } = {}) {
    if (typeof sceneId !== 'string' || !sceneId) throw new TypeError('request needs a sceneId');
    if (!PHASES.includes(phase)) throw new RangeError(`Unknown scene phase: ${phase}`);
    if (phase === 'recall') {
      this._pending = { sceneId, phase };
      return { needsCard: true, card: { text: HINT_CARD_TEXT, confirmKey: 'Enter' } };
    }
    this._pending = null;
    this._uses.push({ sceneId, phase, forfeitsStar: false });
    return { needsCard: false };
  }

  /** Return on the card. @returns {object|null} the recorded HintUse, or null when no card is open */
  confirm() {
    const p = this._pending;
    if (!p) return null;
    this._pending = null;
    const use = { sceneId: p.sceneId, phase: p.phase, forfeitsStar: true };
    this._uses.push(use);
    return { ...use };
  }

  /** Esc on the card: no hint, nothing recorded. */
  cancel() {
    this._pending = null;
  }

  /** The recall request waiting for Return or Esc, or null. */
  get pending() {
    return this._pending ? { ...this._pending } : null;
  }

  uses() {
    return this._uses.map((u) => ({ ...u }));
  }

  /** Has a confirmed hint cost the third star in this scene? */
  forfeited(sceneId) {
    return this._uses.some((u) => u.sceneId === sceneId && u.forfeitsStar);
  }
}
