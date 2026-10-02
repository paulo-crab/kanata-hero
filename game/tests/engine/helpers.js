// Test helpers: load the real data and atlases from disk through the engine's own loaders.
import { readFile } from 'node:fs/promises';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { EventBus } from '../../src/shared/index.js';
import { loadGameData, loadAtlasSet, World } from '../../src/engine/index.js';

const here = path.dirname(fileURLToPath(import.meta.url));
export const REPO = path.resolve(here, '..', '..', '..');

/** fetch-like reader over the repo root; paths are root-absolute like the browser's. */
export async function fsFetch(url) {
  try {
    const text = await readFile(path.join(REPO, url), 'utf8');
    return { ok: true, status: 200, text: async () => text };
  } catch {
    return { ok: false, status: 404, text: async () => '' };
  }
}

export const opts = { fetchFn: fsFetch, baseUrl: '/' };
export const stubImage = async (url) => ({ width: 640, height: 640, url });

let cache = null;
export async function realData() {
  if (!cache) {
    const data = await loadGameData(opts);
    const atlases = await loadAtlasSet({ ...opts, loadImage: stubImage, map: data.map });
    cache = { data, atlases };
  }
  return cache;
}

export async function newWorld(extra = {}) {
  const { data, atlases } = await realData();
  const bus = new EventBus();
  const events = [];
  bus.on('*', (topic, payload) => events.push([topic, payload]));
  const world = new World(data, atlases, { bus, ...extra });
  return { world, bus, events, data, atlases };
}

/** Run `n` sim steps of STEP_MS. */
export function run(world, n) {
  for (let i = 0; i < n; i += 1) world.update(1000 / 60);
}
