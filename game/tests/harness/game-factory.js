// Headless game factory used by the full-stack scenarios.
//
// CONTRACT GAP (see report, "Contract change requests"): CONTRACTS.md section 8 describes `main.js`
// wiring the modules but exports no factory a test can call. The scenarios need one, so they look for
//
//   export async function createGame(opts) -> {
//     bus, clock, data, atlases, world, rules, dialogue, evidence, progress, machine, interpreter, loop,
//     destroy()
//   }
//
// in `game/src/main.js` (or `game/src/boot.js`), with opts
//   { fetchFn, baseUrl, loadImage, clock: FakeClock, storage, headless: true }
// `headless: true` means no canvas, DOM or `window` access; UI view-models still go out on the bus.
// Until that export exists the scenarios skip with a clear reason.
import { FakeClock } from '../../src/shared/index.js';
import { diskFetch, stubLoadImage } from './fixtures.js';
import { skipUnless } from './status.js';

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

/** Resolve `createGame` from the boot module, or null with the reason. */
export async function loadCreateGame() {
  for (const spec of ['../../src/main.js', '../../src/boot.js']) {
    try {
      const mod = await import(spec);
      if (typeof mod.createGame === 'function') return { createGame: mod.createGame, reason: null };
    } catch (e) {
      if (e && e.code !== 'ERR_MODULE_NOT_FOUND') return { createGame: null, reason: `${spec} failed to import: ${e.message}` };
    }
  }
  return { createGame: null, reason: 'game/src/main.js exports no createGame(opts) yet (integration, task 7.1)' };
}

/** Why the full-stack scenarios cannot run yet, or false when they can. */
export async function fullStackSkipReason() {
  const mods = skipUnless('engine', 'input', 'runtime');
  if (mods) return mods;
  const { createGame, reason } = await loadCreateGame();
  return createGame ? false : reason;
}

/** Build one headless game on a fake clock, real data from disk, in-memory storage. */
export async function buildHeadlessGame({ storage = new MemoryStorage(), fetchFn = diskFetch(), clock = new FakeClock() } = {}) {
  const { createGame } = await loadCreateGame();
  const game = await createGame({ fetchFn, baseUrl: '/', loadImage: stubLoadImage(), clock, storage, headless: true });
  return { game, storage, clock, fetchFn };
}
