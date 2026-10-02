// Fixture loaders over the real data files (design/**, art-direction/**), straight from disk.
// They mirror what the browser fetches, so the same GameData/AtlasSet loaders can be pointed at them
// through `fetchFn` (contract section 0, "Paths").
import { readFileSync, existsSync } from 'node:fs';
import { repoPath } from './paths.js';

export const DATA_PATHS = {
  district: '/design/levels/orientation/district.json',
  map: '/design/levels/orientation/map.json',
  level: '/design/levels/orientation/levels/01-the-lobby.json',
  world: '/design/levels/world.json',
  gestureInventory: '/design/levels/gesture-inventory.json',
  layoutManifest: '/design/layout/layout-manifest.json',
};

export const ATLAS_PATHS = {
  kit: '/art-direction/kit/orientation-atlas.json',
  engineer: '/art-direction/gate1/engineer-full-atlas.json',
  ivo: '/art-direction/cast/ivo-atlas.json',
  mira: '/art-direction/cast/mira-atlas.json',
  bgworker_a: '/art-direction/cast/bgworker_a-atlas.json',
  bgworker_b: '/art-direction/cast/bgworker_b-atlas.json',
  glitches: '/art-direction/glitches/glitches-atlas.json',
  pace: '/art-direction/pace/pace-atlas.json',
  portraits: '/art-direction/portraits/portraits-atlas.json',
};

export function readJson(urlPath) {
  return JSON.parse(readFileSync(repoPath(urlPath), 'utf8'));
}

/** Deep copy so a test can break a fixture without touching the shared object. */
export function clone(x) {
  return JSON.parse(JSON.stringify(x));
}

/**
 * A `fetch` replacement that serves files from disk.
 * @param {{baseUrl?:string, overrides?:{[urlPath:string]: any}, missing?:string[], corrupt?:string[]}} [opts]
 *   overrides: urlPath -> object (served as JSON) or string/Buffer (served raw)
 *   missing: urlPaths answered with 404; corrupt: urlPaths answered with invalid JSON
 */
export function diskFetch(opts = {}) {
  const { baseUrl = '/', overrides = {}, missing = [], corrupt = [] } = opts;
  const calls = [];
  const fn = async (url) => {
    let p = String(url).replace(/^https?:\/\/[^/]+/, '');
    if (baseUrl !== '/' && p.startsWith(baseUrl)) p = '/' + p.slice(baseUrl.length);
    p = p.replace(/\/{2,}/g, '/');
    calls.push(p);
    const reply = (status, body, type) => ({
      ok: status >= 200 && status < 300,
      status,
      statusText: status === 200 ? 'OK' : 'Not Found',
      headers: { get: () => type },
      async json() { return JSON.parse(typeof body === 'string' ? body : body.toString('utf8')); },
      async text() { return typeof body === 'string' ? body : body.toString('utf8'); },
      async arrayBuffer() { return body; },
    });
    if (missing.includes(p)) return reply(404, '', 'text/plain');
    if (corrupt.includes(p)) return reply(200, '{not json', 'application/json');
    if (p in overrides) {
      const o = overrides[p];
      return reply(200, typeof o === 'object' && !Buffer.isBuffer(o) ? JSON.stringify(o) : o, 'application/json');
    }
    const file = repoPath(p);
    if (!existsSync(file)) return reply(404, '', 'text/plain');
    return reply(200, readFileSync(file), p.endsWith('.png') ? 'image/png' : 'application/json');
  };
  fn.calls = calls;
  return fn;
}

/** Stand-in for opts.loadImage(url) (contract 3.1): resolves to {width, height} read from the PNG header. */
export function stubLoadImage() {
  return async (url) => {
    const file = repoPath(String(url).replace(/^https?:\/\/[^/]+/, ''));
    const buf = readFileSync(file);
    return { width: buf.readUInt32BE(16), height: buf.readUInt32BE(20) };
  };
}

/** All six data files, parsed. Same shape as GameData (contract 3.1). */
export function loadRealData() {
  return Object.fromEntries(Object.entries(DATA_PATHS).map(([k, p]) => [k, readJson(p)]));
}

/** All nine atlas JSON files keyed by atlas id. */
export function loadRealAtlasJson() {
  return Object.fromEntries(Object.entries(ATLAS_PATHS).map(([k, p]) => [k, readJson(p)]));
}
