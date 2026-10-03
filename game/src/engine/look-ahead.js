// Camera look-ahead (playtest 1, item 1). The avatar must never sit under a panel. The camera keeps the feet at one
// screen point, clamped to the camera bounds; when that point falls under an open panel the camera moves the least it
// can so the avatar's stage rectangle clears every panel, still clamped to the bounds. When the bounds make that
// impossible (the avatar walks along the south wall under the bottom panels) the panels that still cover the avatar
// are reported in `faded` so the UI can drop them to 35 % opacity as the last resort. Pure: rectangles in, camera out.
import { TILE, VIEW_H, VIEW_W } from '../shared/index.js';
import { computeCamera } from './camera.js';

/** The engineer sprite: 16x24 with the feet anchor at (8, 24). */
export const AVATAR_SPRITE = Object.freeze({ w: 16, h: 24, ax: 8, ay: 24 });
export const FADED_OPACITY = 0.35;
/** Clear space kept between the avatar and a panel, in stage px. */
export const CLEARANCE = 8;
const MAX_SHIFT = 120;

const overlapArea = (a, b) => {
  const w = Math.min(a.x + a.w, b.x + b.w) - Math.max(a.x, b.x);
  const h = Math.min(a.y + a.h, b.y + b.h) - Math.max(a.y, b.y);
  return w > 0 && h > 0 ? w * h : 0;
};

const STAGE = { w: VIEW_W * 4, h: VIEW_H * 4 };
/** The avatar stays fully on the stage: a camera that pushes it off an edge is not a way to clear a panel. */
const onStage = (r, zoom) => {
  const k = zoom / 4;
  return r.x >= 0 && r.y >= 0 && r.x + r.w <= STAGE.w * k && r.y + r.h <= STAGE.h * k;
};

const inflate = (r, m) => ({ x: r.x - m, y: r.y - m, w: r.w + 2 * m, h: r.h + 2 * m });

/** Avatar sprite rectangle on the stage for a camera (map px) and zoom. */
export function avatarStageRect(feetPx, camera, zoom = 4, sprite = AVATAR_SPRITE) {
  return {
    x: (feetPx.x - sprite.ax - camera.x) * zoom,
    y: (feetPx.y - sprite.ay - camera.y) * zoom,
    w: sprite.w * zoom,
    h: sprite.h * zoom,
  };
}

function clampCamera(cam, bounds) {
  const minX = bounds.x * TILE;
  const minY = bounds.y * TILE;
  const maxX = Math.max(minX, (bounds.x + bounds.w) * TILE - VIEW_W);
  const maxY = Math.max(minY, (bounds.y + bounds.h) * TILE - VIEW_H);
  return { x: Math.min(Math.max(cam.x, minX), maxX), y: Math.min(Math.max(cam.y, minY), maxY) };
}

/**
 * @param {{feetPx:{x:number,y:number}, bounds:object, panels:{id:string,x:number,y:number,w:number,h:number}[], zoom?:number}} p
 *   panels are stage rectangles of the panels that are on screen
 * @returns {{camera:{x:number,y:number}, offset:{x:number,y:number}, faded:string[]}}
 */
export function lookAhead({ feetPx, bounds, panels, zoom = 4 }) {
  const base = computeCamera(feetPx, bounds);
  const cost = (cam, margin) => {
    const av = inflate(avatarStageRect(feetPx, cam, zoom), margin);
    return panels.reduce((sum, p) => sum + overlapArea(av, p), 0);
  };
  const result = (cam, covering) => ({
    camera: cam,
    offset: { x: cam.x - base.x, y: cam.y - base.y },
    faded: covering ? panels.filter((p) => overlapArea(avatarStageRect(feetPx, cam, zoom), p) > 0).map((p) => p.id) : [],
  });
  if (!panels.length || cost(base, CLEARANCE) === 0) return result(base, false);
  // Least movement first, vertical before horizontal: the bottom panels are the usual cause.
  const seen = new Set([`${base.x},${base.y}`]);
  for (let s = 1; s <= MAX_SHIFT; s += 1) {
    for (const [dx, dy] of [[0, s], [0, -s], [s, 0], [-s, 0]]) {
      const cam = clampCamera({ x: base.x + dx, y: base.y + dy }, bounds);
      const key = `${cam.x},${cam.y}`;
      if (seen.has(key)) continue;
      seen.add(key);
      if (!onStage(avatarStageRect(feetPx, cam, zoom), zoom)) continue;
      if (cost(cam, CLEARANCE) === 0) return result(cam, false);
    }
  }
  // Impossible within the bounds: keep the plain camera and fade what still covers the avatar.
  return result(base, cost(base, 0) > 0);
}
