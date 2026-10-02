// Data loading. Contract section 3.1. Every failure is a DataLoadError naming the file.
import { DataLoadError } from '../shared/index.js';
import { DATA_FILES } from './files.js';

function joinUrl(baseUrl, path) {
  if (!baseUrl || baseUrl === '/') return path;
  return baseUrl.replace(/\/+$/, '') + path;
}

/** @returns {Promise<object>} parsed JSON; kinds `missing` and `parse`. */
export async function loadJson(path, opts = {}) {
  const fetchFn = opts.fetchFn ?? globalThis.fetch;
  if (typeof fetchFn !== 'function') {
    throw new DataLoadError({ file: path, kind: 'missing', detail: 'no fetch function available' });
  }
  let res;
  try {
    res = await fetchFn(joinUrl(opts.baseUrl ?? '/', path));
  } catch (error) {
    throw new DataLoadError({ file: path, kind: 'missing', detail: String(error?.message ?? error) });
  }
  if (!res || !res.ok) {
    throw new DataLoadError({ file: path, kind: 'missing', detail: `HTTP ${res ? res.status : 'no response'}` });
  }
  let text;
  try {
    text = await res.text();
  } catch (error) {
    throw new DataLoadError({ file: path, kind: 'missing', detail: String(error?.message ?? error) });
  }
  try {
    return JSON.parse(text);
  } catch (error) {
    throw new DataLoadError({ file: path, kind: 'parse', detail: String(error?.message ?? error) });
  }
}

export function shapeError(file, detail) {
  return new DataLoadError({ file, kind: 'shape', detail });
}

function requireShape(file, obj, checks) {
  if (obj === null || typeof obj !== 'object' || Array.isArray(obj)) throw shapeError(file, 'expected a JSON object');
  for (const [key, type] of Object.entries(checks)) {
    const v = obj[key];
    const ok = type === 'array' ? Array.isArray(v) : type === 'object' ? v && typeof v === 'object' && !Array.isArray(v) : typeof v === type;
    if (!ok) throw shapeError(file, `missing or invalid "${key}" (expected ${type})`);
  }
}

const SHAPES = {
  district: { id: 'string', size_cells: 'array', camera_bounds: 'object', entrances: 'array' },
  map: { size_cells: 'array', floor: 'array', floor_legend: 'object', placements: 'array', collision: 'array', gates: 'array', interactions: 'array', npcs: 'array', spawns: 'array' },
  level: { id: 'string', steps: 'array', triggers: 'array', glitch: 'object' },
  world: { version: 'string', state_ids: 'object' },
  gestureInventory: {},
  layoutManifest: {},
};

function checkMapGrid(file, map) {
  const [cols, rows] = map.size_cells;
  if (map.floor.length !== rows || map.collision.length !== rows) throw shapeError(file, `floor/collision must have ${rows} rows`);
  for (const r of [...map.floor, ...map.collision]) if (typeof r !== 'string' || r.length !== cols) throw shapeError(file, `every grid row must be ${cols} characters`);
}

/** @returns {Promise<{district:object,map:object,level:object,world:object,gestureInventory:object,layoutManifest:object}>} */
export async function loadGameData(opts = {}) {
  const out = {};
  for (const [key, path] of Object.entries(DATA_FILES)) {
    const json = await loadJson(path, opts);
    requireShape(path, json, SHAPES[key]);
    if (key === 'map') checkMapGrid(path, json);
    out[key] = json;
  }
  return out;
}
