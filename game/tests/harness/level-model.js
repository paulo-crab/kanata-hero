// Pure model of the level 01 geometry, built from the real data files: collision grid, shortest
// walking paths, the camera model of design/levels/SCHEMA.md ("Coordinates and the camera") and
// the keyboard-inset overlap check. Independent of the engine (it is also used to cross-check it).
import { TILE, VIEW_W, VIEW_H, AVATAR_SCREEN, INSET_STAGE_RECT } from '../../src/shared/layout.js';
import { DIRS } from './input-player.js';
import {
  targetIndicator, markerCentre, avatarStageRect, ARROW_SIZE, DIALOGUE_STAGE_RECT, INSET_AVOID_RECT,
} from '../../src/ui/index.js';

export const STAGE_ZOOM = 4; // logical stage 1280x720 = 320x180 x 4; CSS scaling happens outside this model

const VEC = { n: [0, -1], s: [0, 1], e: [1, 0], w: [-1, 0] };
export const DIR_OF_VEC = { '0,-1': 'n', '0,1': 's', '1,0': 'e', '-1,0': 'w' };

/** Collision grid from map.json: true = blocked. `openGates` clears the listed gate ids' cells. */
export function collisionGrid(map, openGates = []) {
  const rows = map.collision.map((r) => [...r].map((c) => c === '1'));
  for (const g of map.gates || []) {
    if (!openGates.includes(g.id)) continue;
    for (const [x, y] of g.cells) rows[y][x] = false;
  }
  return rows;
}

export function isBlockedAt(grid, x, y) {
  return y < 0 || x < 0 || y >= grid.length || x >= grid[0].length || grid[y][x];
}

/**
 * Cheapest 4-connected path of cells from `from` to `to` (inclusive), or null. `stepCost(cell)` is the
 * cost of entering a cell (default 1). Deterministic: ties break in the order n, s, e, w, then insertion.
 */
export function shortestPath(grid, from, to, extraBlocked = [], stepCost = () => 1) {
  const key = (c) => `${c[0]},${c[1]}`;
  const blocked = new Set(extraBlocked.map(key));
  const best = new Map([[key(from), 0]]);
  const prev = new Map([[key(from), null]]);
  const open = [{ cell: from, cost: 0, seq: 0 }];
  let seq = 0;
  while (open.length) {
    open.sort((a, b) => a.cost - b.cost || a.seq - b.seq);
    const cur = open.shift();
    if (cur.cost > best.get(key(cur.cell))) continue;
    if (key(cur.cell) === key(to)) {
      const out = [];
      for (let c = cur.cell; c; c = prev.get(key(c))) out.unshift(c);
      return out;
    }
    for (const d of ['n', 's', 'e', 'w']) {
      const next = [cur.cell[0] + VEC[d][0], cur.cell[1] + VEC[d][1]];
      const nk = key(next);
      if (isBlockedAt(grid, next[0], next[1]) || (blocked.has(nk) && nk !== key(to))) continue;
      const cost = cur.cost + stepCost(next);
      if (best.has(nk) && best.get(nk) <= cost) continue;
      best.set(nk, cost);
      prev.set(nk, cur.cell);
      seq += 1;
      open.push({ cell: next, cost, seq });
    }
  }
  return null;
}

/** Direction letters ('n'|'s'|'e'|'w') for consecutive cells of a path. */
export function pathDirs(cells) {
  const out = [];
  for (let i = 1; i < cells.length; i += 1) {
    const d = DIR_OF_VEC[`${cells[i][0] - cells[i - 1][0]},${cells[i][1] - cells[i - 1][1]}`];
    if (!d) throw new Error(`cells ${cells[i - 1]} and ${cells[i]} are not adjacent`);
    out.push(d);
  }
  return out;
}

/** Collapse a direction list to [{dir, cells}] runs (so a script holds one arrow per straight leg). */
export function runs(dirs) {
  const out = [];
  for (const d of dirs) {
    if (out.length && out[out.length - 1].dir === d) out[out.length - 1].cells += 1;
    else out.push({ dir: d, cells: 1 });
  }
  return out;
}

/** Script items that walk a path with one cell per tap. */
export function walkScript(cells) {
  return pathDirs(cells).map((d) => ({ step: DIRS[d] }));
}

// ---- camera model (SCHEMA.md) ---------------------------------------------------------------

export function feetOf(cell) {
  return { x: cell[0] * TILE + 8, y: cell[1] * TILE + 16 };
}

/** Top-left of the 320x180 view in map px: feet at AVATAR_SCREEN, clamped to camera_bounds (cells). */
export function cameraFor(cell, bounds) {
  const f = feetOf(cell);
  const minX = bounds.x * TILE;
  const minY = bounds.y * TILE;
  const maxX = (bounds.x + bounds.w) * TILE - VIEW_W;
  const maxY = (bounds.y + bounds.h) * TILE - VIEW_H;
  return {
    x: Math.min(Math.max(f.x - AVATAR_SCREEN.x, minX), Math.max(minX, maxX)),
    y: Math.min(Math.max(f.y - AVATAR_SCREEN.y, minY), Math.max(minY, maxY)),
  };
}

/** Stage-pixel rectangle (1280x720 stage at zoom 4) of one 16 px cell, for a camera. */
export function cellStageRect(cell, camera, zoom = STAGE_ZOOM) {
  return {
    x: (cell[0] * TILE - camera.x) * zoom,
    y: (cell[1] * TILE - camera.y) * zoom,
    w: TILE * zoom,
    h: TILE * zoom,
  };
}

export function rectsOverlap(a, b) {
  return a.x < b.x + b.w && b.x < a.x + a.w && a.y < b.y + b.h && b.y < a.y + a.h;
}

/** The keyboard inset rectangle in stage px at the given zoom (the contract constant is for x4). */
export function insetStageRect(zoom = STAGE_ZOOM) {
  const k = zoom / 4;
  return { x: INSET_STAGE_RECT.x * k, y: INSET_STAGE_RECT.y * k, w: INSET_STAGE_RECT.w * k, h: INSET_STAGE_RECT.h * k };
}

// ---- level 01 legs --------------------------------------------------------------------------

/**
 * The walking legs of level 01 in play order, each with the cells the avatar crosses and the target
 * it is walking to. Guided and variation scenes show the inset; the recall leg does not (position_cue false).
 * @returns {Array<{id:string, scene:string, inset:boolean, cells:number[][], target:number[]}>}
 */
export function level01Legs(data) {
  const { map, level } = data;
  const grid = collisionGrid(map);
  const scenes = Object.fromEntries(level.terminal_scenes.map((s) => [s.id, s]));
  const legs = [];
  // Players choose their own way between desks: take the route that keeps the avatar clear of the inset.
  const inset = insetStageRect(STAGE_ZOOM);
  const clear = (cell) => (rectsOverlap(cellStageRect(cell, cameraFor(cell, data.district.camera_bounds)), inset) ? 1000 : 1);
  const line = (a, b) => {
    const p = shortestPath(grid, a, b, [], clear);
    if (!p) throw new Error(`no path ${a} -> ${b}`);
    return p;
  };
  // Arrival: the avatar steps out of the elevator and walks to Ivo's approach cell (4,3).
  const arrive = level.steps.find((s) => s.id === 'o01.s.arrive');
  legs.push({ id: 'arrival', scene: 'arrival', inset: false, cells: line(map.spawns.find((s) => s.id === 'arrival').cell, arrive.target_cell), target: arrive.target_cell });
  // Lap: straight legs from the scene data. The lap starts at the arrival mat.
  for (const l of scenes['o01-loop'].task.legs) {
    legs.push({ id: `loop-${l.id}`, scene: 'o01-loop', inset: scenes['o01-loop'].position_cue, cells: line(l.from, l.to), target: l.marker, floor: true });
  }
  // Four stops in the fixed order, starting where the lap ended.
  let at = scenes['o01-loop'].task.legs.at(-1).to;
  for (const s of scenes['o01-four-stops'].task.stops) {
    legs.push({ id: `stop-${s.id}`, scene: 'o01-four-stops', inset: scenes['o01-four-stops'].position_cue, cells: line(at, s.cell), target: s.cell, floor: false });
    at = s.cell;
  }
  // Recall: no markers, no inset.
  for (const l of scenes['o01-unprompted'].task.legs) {
    legs.push({ id: `recall-${l.id}`, scene: 'o01-unprompted', inset: scenes['o01-unprompted'].position_cue, cells: line(l.from, l.to), target: l.to });
  }
  return legs;
}

/** Rectangle of a square of `size` centred on `c`. */
const boxAt = (c, size) => ({ x: c.x - size / 2, y: c.y - size / 2, w: size, h: size });

/**
 * How the current target is drawn for an avatar cell on a leg while the inset is open: the marker where it stands,
 * or the edge arrow of the UI (ui/world-space.js targetIndicator) when the inset covers it. Returns the visible
 * rectangle in stage px and which of the two it is.
 */
export function targetDisplay(cell, leg, bounds, zoom = STAGE_ZOOM) {
  const camera = cameraFor(cell, bounds);
  const view = { camera, zoom };
  const at = { x: leg.target[0] * TILE, y: leg.target[1] * TILE };
  const centre = markerCentre(at, 'route', view, !!leg.floor);
  const size = leg.floor ? 48 : 64;
  const feet = feetOf(cell);
  const avatar = avatarStageRect(feet, view);
  const k = zoom / 4;
  const avoid = { x: INSET_AVOID_RECT.x * k, y: INSET_AVOID_RECT.y * k, w: INSET_AVOID_RECT.w * k, h: INSET_AVOID_RECT.h * k };
  const ind = targetIndicator({ centre, size, inset: avoid, avatar });
  return ind
    ? { kind: 'edge-arrow', rect: boxAt(ind, ARROW_SIZE), angle: ind.angle, avatar }
    : { kind: 'marker', rect: boxAt(centre, size), avatar };
}

/**
 * Inset overlap assertion over every leg that shows the inset. Returns a list of violations, each
 * naming the leg, the avatar cell and what overlapped, so a failure reads "cell (x,y)". The avatar is its 16x16 cell;
 * the target is whatever the UI draws for it (the marker, or the edge arrow when the marker would be covered).
 */
export function insetViolations(data, { zoom = STAGE_ZOOM } = {}) {
  const bounds = data.district.camera_bounds;
  const inset = insetStageRect(zoom);
  const out = [];
  for (const leg of level01Legs(data)) {
    if (!leg.inset) continue;
    for (const cell of leg.cells) {
      const cam = cameraFor(cell, bounds);
      const avatar = cellStageRect(cell, cam, zoom);
      if (rectsOverlap(avatar, inset)) out.push({ leg: leg.id, cell, what: 'avatar' });
      const shown = targetDisplay(cell, leg, bounds, zoom);
      const onStage = rectsOverlap(shown.rect, { x: 0, y: 0, w: 320 * zoom, h: 180 * zoom });
      // A marker the avatar stands on is simply reached; only an arrow must keep clear of the avatar and the dialogue panel.
      const bad = !onStage || rectsOverlap(shown.rect, inset)
        || (shown.kind === 'edge-arrow' && (rectsOverlap(shown.rect, shown.avatar) || rectsOverlap(shown.rect, DIALOGUE_STAGE_RECT)));
      if (bad) out.push({ leg: leg.id, cell, what: 'target', target: leg.target, shown: shown.kind });
    }
  }
  return out;
}
