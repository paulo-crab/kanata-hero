// Grid-stepped avatar. Contract section 3.3. Pure and deterministic: one update() is one sim step.
import { CELL_STEPS, TILE } from '../shared/index.js';

export const DIRS = Object.freeze({ n: [0, -1], s: [0, 1], e: [1, 0], w: [-1, 0] });

export class Avatar {
  /**
   * @param {{isBlocked:(x:number,y:number)=>boolean, cell?:number[], facing?:string,
   *   onStep?:Function, onBlocked?:Function}} p
   */
  constructor({ isBlocked, cell = [0, 0], facing = 's', onStep = null, onBlocked = null }) {
    this._isBlocked = isBlocked;
    this._onStep = onStep;
    this._onBlocked = onBlocked;
    this.cell = [...cell];
    this.facing = facing;
    this._moving = false;
    this._dir = null;
    this._progress = 0;
    this._held = null;
    this._blockedNotified = null;
    this.walkSteps = 0;
  }

  get moving() {
    return this._moving;
  }

  get held() {
    return this._held;
  }

  /** Feet position in map px, including the part-way offset of a step in progress. */
  get feetPx() {
    let x = this.cell[0] * TILE + TILE / 2;
    let y = this.cell[1] * TILE + TILE;
    if (this._moving) {
      const [dx, dy] = DIRS[this._dir];
      x += dx * this._progress;
      y += dy * this._progress;
    }
    return { x, y };
  }

  /** @returns {'started'|'blocked'|'busy'} */
  requestStep(dir) {
    const d = DIRS[dir];
    if (!d) throw new Error(`bad direction: ${dir}`);
    if (this._moving) return 'busy';
    this.facing = dir;
    const tx = this.cell[0] + d[0];
    const ty = this.cell[1] + d[1];
    if (this._isBlocked(tx, ty)) {
      this.walkSteps = 0;
      this._onBlocked?.({ cell: [...this.cell], dir });
      return 'blocked';
    }
    this._moving = true;
    this._dir = dir;
    this._progress = 0;
    return 'started';
  }

  setHeld(dir) {
    if (dir !== null && !DIRS[dir]) throw new Error(`bad direction: ${dir}`);
    if (dir !== this._held) this._blockedNotified = null;
    this._held = dir;
  }

  /** Advance one sim step: 1 px along the step, CELL_STEPS per cell. */
  update() {
    if (!this._moving) {
      this.walkSteps = 0;
      this._startHeld();
      if (!this._moving) return;
    }
    this._progress += 1;
    this.walkSteps += 1;
    if (this._progress >= CELL_STEPS) {
      const dir = this._dir;
      const d = DIRS[dir];
      this.cell = [this.cell[0] + d[0], this.cell[1] + d[1]];
      this._moving = false;
      this._dir = null;
      this._progress = 0;
      this._onStep?.({ cell: [...this.cell], facing: this.facing, dir });
      // Held-key repeat: the next step begins at once, so walk frames stay continuous.
      this._startHeld(true);
    }
  }

  _startHeld(continuing = false) {
    if (!this._held) {
      return;
    }
    const d = DIRS[this._held];
    const blocked = this._isBlocked(this.cell[0] + d[0], this.cell[1] + d[1]);
    if (blocked) {
      this.facing = this._held;
      if (!continuing) this.walkSteps = 0;
      if (this._blockedNotified !== this._held) {
        this._blockedNotified = this._held;
        this._onBlocked?.({ cell: [...this.cell], dir: this._held });
      }
      if (continuing) this.walkSteps = 0;
      return;
    }
    this._blockedNotified = null;
    this.requestStep(this._held);
  }

  teleport(cell, facing) {
    this.cell = [...cell];
    if (facing) this.facing = facing;
    this._moving = false;
    this._dir = null;
    this._progress = 0;
    this.walkSteps = 0;
  }
}
