// Animation timing. Contract section 3.2. Pure: time comes from update(dtMs) only.
import { WALK_FRAME_STEPS } from '../shared/index.js';

export class AnimationPlayer {
  /**
   * @param {{frames:number, ms:number, mode?:'loop'|'once'|'hold'}} def
   * @param {{reducedMotion?:boolean, startOffsetMs?:number}} [opts]
   */
  constructor(def, opts = {}) {
    this.def = def;
    this.reducedMotion = !!opts.reducedMotion;
    this._offset = opts.startOffsetMs ?? 0;
    this._t = this._offset;
  }

  update(dtMs) {
    this._t += dtMs;
  }

  setReducedMotion(on) {
    this.reducedMotion = !!on;
  }

  get mode() {
    return this.def.mode ?? 'loop';
  }

  get frameIndex() {
    const { frames, ms } = this.def;
    if (!(frames > 1) || !(ms > 0)) return 0;
    const raw = Math.floor(this._t / ms);
    if (this.mode === 'loop') return this.reducedMotion ? 0 : raw % frames;
    return Math.min(raw, frames - 1);
  }

  get done() {
    if (this.mode === 'loop') return false;
    const { frames, ms } = this.def;
    return this._t >= frames * ms;
  }

  reset() {
    this._t = this._offset;
  }
}

/** Walk frame index after `steps` simulation steps (pure). */
export function frameForSteps(def, steps) {
  return Math.floor(steps / WALK_FRAME_STEPS) % def.frames;
}
