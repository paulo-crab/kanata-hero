// Headless game factory used by the full-stack scenarios: `createGame` from game/src/main.js on a fake clock,
// real data from disk and an in-memory `localStorage` stand-in. No canvas, DOM or `window` is touched.
import { FakeClock } from '../../src/shared/index.js';
import { diskFetch, stubLoadImage } from './fixtures.js';

/** In-memory `localStorage` stand-in; `throwing: true` makes every call throw (private mode). */
export class MemoryStorage {
  constructor({ throwing = false } = {}) {
    this._m = new Map();
    this._throwing = throwing;
  }
  getItem(k) { if (this._throwing) throw new Error('storage blocked'); return this._m.has(k) ? this._m.get(k) : null; }
  setItem(k, v) { if (this._throwing) throw new Error('storage blocked'); this._m.set(k, String(v)); }
  removeItem(k) { if (this._throwing) throw new Error('storage blocked'); this._m.delete(k); }
  dump() { return Object.fromEntries(this._m); }
}

/** Build one headless game on a fake clock, real data from disk, in-memory storage. */
export async function buildHeadlessGame({ storage = new MemoryStorage(), fetchFn = diskFetch(), clock = new FakeClock() } = {}) {
  const { createGame } = await import('../../src/main.js');
  const game = await createGame({ fetchFn, baseUrl: '/', loadImage: stubLoadImage(), clock, storage, headless: true });
  return { game, storage, clock, fetchFn };
}
