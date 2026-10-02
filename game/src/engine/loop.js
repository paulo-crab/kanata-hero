// Fixed-timestep game loop. Contract section 3.4. Time comes only from the injected clock.
import { STEP_MS } from '../shared/index.js';

const EPS = 1e-9;
export const MAX_STEPS_PER_TICK = 5;

export class GameLoop {
  /** @param {{clock:{now:()=>number}, update:(stepMs:number)=>void, render:()=>void, raf?:Function, caf?:Function}} p */
  constructor(p) {
    this._clock = p.clock;
    this._update = p.update;
    this._render = p.render;
    this._raf = p.raf ?? null;
    this._caf = p.caf ?? null;
    this._running = false;
    this._last = null;
    this._acc = 0;
    this._steps = 0;
    this._handle = null;
  }

  get stepCount() {
    return this._steps;
  }

  get running() {
    return this._running;
  }

  start() {
    if (this._running) return;
    this._running = true;
    this._last = this._clock.now();
    this._acc = 0;
    if (this._raf) {
      const frame = () => {
        if (!this._running) return;
        this.tick(this._clock.now());
        if (this._running) this._handle = this._raf(frame);
      };
      this._handle = this._raf(frame);
    }
  }

  stop() {
    this._running = false;
    if (this._handle !== null && this._caf) this._caf(this._handle);
    this._handle = null;
  }

  /** Accumulate elapsed time, run whole steps (at most 5), then render once. */
  tick(nowMs) {
    if (this._last === null) this._last = nowMs;
    this._acc += Math.max(0, nowMs - this._last);
    this._last = nowMs;
    let n = 0;
    while (this._acc >= STEP_MS - EPS && n < MAX_STEPS_PER_TICK) {
      this._update(STEP_MS);
      this._steps += 1;
      this._acc -= STEP_MS;
      n += 1;
    }
    if (this._acc >= STEP_MS - EPS) this._acc = 0; // spiral guard: drop the backlog
    this._render();
  }

  /** Tests: run floor(ms / STEP_MS) steps with no render. */
  advance(ms) {
    const n = Math.floor(ms / STEP_MS + EPS);
    for (let i = 0; i < n; i += 1) {
      this._update(STEP_MS);
      this._steps += 1;
    }
  }
}
