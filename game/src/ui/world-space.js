// Map pixels to stage pixels for markers and the interaction prompt.
// The runtime sends `at` in MAP pixels (cell * 16, top-left of the cell) and has no camera, so the UI converts.
// The camera and zoom reach the UI as `ui:view {camera:{x,y}, zoom}` on the bus (the renderer's boot adapter emits it
// when either changes) or through the `getView()` parameter of mountUi.
import { TILE, STAGE_W, STAGE_H, INSET_STAGE_RECT } from '../shared/layout.js';

export const DEFAULT_VIEW = Object.freeze({ camera: Object.freeze({ x: 0, y: 0 }), zoom: 4 });

/** Same formula as engine worldToStage(pointPx, camera, zoom), kept here so the UI imports nothing from the engine. */
export function worldToStage(pointPx, camera, zoom) {
  return { x: (pointPx.x - camera.x) * zoom, y: (pointPx.y - camera.y) * zoom };
}

/** Cell top-left on the stage, from the map-pixel `at` of a view-model. */
export function cellOnStage(at, view = DEFAULT_VIEW) {
  return worldToStage(at, view.camera, view.zoom);
}

/** Centre of the 64 px marker box. People's markers float above the head (a person is 24 px tall, feet at the cell
 *  bottom); device and route markers sit just above the cell; floor markers are centred on the cell. */
export function markerCentre(at, shape, view = DEFAULT_VIEW, floor = false) {
  const p = cellOnStage(at, view);
  const z = view.zoom;
  const cx = p.x + (TILE * z) / 2;
  if (floor) return { x: cx, y: p.y + (TILE * z) / 2 };
  if (shape === 'conversation' || shape === 'glitch') return { x: cx, y: p.y - 8 * z - 36 };
  return { x: cx, y: p.y - 28 };
}

/** Top-left of the interaction prompt: to the right of the cell, level with the sprite top, kept inside the stage. */
export function promptPosition(at, view = DEFAULT_VIEW, size = { w: 360, h: 120 }) {
  const p = cellOnStage(at, view);
  const z = view.zoom;
  const x = Math.min(Math.max(Math.round(p.x + TILE * z + 16), 0), STAGE_W - size.w);
  const y = Math.min(Math.max(Math.round(p.y - 8 * z), 0), STAGE_H - size.h);
  return { x, y };
}

export const sameView = (a, b) => a.zoom === b.zoom && a.camera.x === b.camera.x && a.camera.y === b.camera.y;

// ---- Current target versus the keyboard inset ----------------------------------------------------------------------
// The camera keeps the avatar at one fixed screen point, so on the west walkway the current target (3,12) and (7,10)
// is drawn under the inset while the avatar walks towards it. The inset stays put; the current target is shown as an
// edge arrow in the free area instead, pointing at where the target is.

/** Dialogue panel on the stage (672x224, 16 px margin, lower right). */
export const DIALOGUE_STAGE_RECT = Object.freeze({ x: STAGE_W - 16 - 672, y: STAGE_H - 16 - 224, w: 672, h: 224 });
export const ARROW_SIZE = 56;
const GAP = 12;

const overlap = (a, b) => a.x < b.x + b.w && a.x + a.w > b.x && a.y < b.y + b.h && a.y + a.h > b.y;
const boxAt = (c, size) => ({ x: c.x - size / 2, y: c.y - size / 2, w: size, h: size });

/**
 * Where the current target is indicated while the inset is open.
 * @param {{centre:{x:number,y:number}, size:number, inset:object|null, avatar?:object|null}} p  stage px; avatar is the
 *   avatar sprite rectangle, when known
 * @returns {null|{x:number,y:number,angle:number}} null: the marker is visible where it is. Otherwise the centre of the
 *   edge arrow (stage px) and its angle in degrees (0 = pointing right) towards the target.
 */
export function targetIndicator({ centre, size, inset, avatar = null }) {
  const stage = { x: 0, y: 0, w: STAGE_W, h: STAGE_H };
  const box = boxAt(centre, size);
  const inside = box.x >= 0 && box.y >= 0 && box.x + box.w <= STAGE_W && box.y + box.h <= STAGE_H;
  const covered = !!inset && overlap(box, inset);
  const visibleBit = overlap(box, stage);
  if (visibleBit && inside && !covered) return null;
  if (visibleBit && !covered && !inset) return null;
  const half = ARROW_SIZE / 2;
  const margin = 16;
  const clampX = (x) => Math.min(Math.max(x, margin + half), STAGE_W - margin - half);
  const clampY = (y) => Math.min(Math.max(y, margin + half), STAGE_H - margin - half);
  const avoid = [inset, DIALOGUE_STAGE_RECT, avatar].filter(Boolean).map((r) => ({ x: r.x - 8, y: r.y - 8, w: r.w + 16, h: r.h + 16 }));
  const right = (inset ? inset.x + inset.w : margin) + GAP + half;
  const above = DIALOGUE_STAGE_RECT.y - 8 - half;
  const spots = [
    { x: clampX(centre.x), y: clampY(centre.y) },
    { x: right, y: Math.min(clampY(centre.y), above) },
    { x: right, y: above },
    { x: right + 96, y: above },
    { x: right + 96, y: margin + half + 96 },
  ];
  const spot = spots.find((c) => !avoid.some((r) => overlap(boxAt(c, ARROW_SIZE), r))) || spots[2];
  const angle = Math.round((Math.atan2(centre.y - spot.y, centre.x - spot.x) * 180) / Math.PI);
  return { x: spot.x, y: spot.y, angle };
}

/**
 * The rectangle the markers keep clear of: the contract inset rectangle at x4 plus 20 px on top, because larger text
 * grows the inset upward by about 10 px (the contract rectangle is for the default text size).
 */
export const INSET_AVOID_RECT = Object.freeze({
  x: INSET_STAGE_RECT.x, y: INSET_STAGE_RECT.y - 20, w: INSET_STAGE_RECT.w, h: INSET_STAGE_RECT.h + 20,
});

/** Avatar sprite rectangle on the stage from its feet in map px (the engineer is 16x24 with feet at 8,24). */
export function avatarStageRect(feetPx, view = DEFAULT_VIEW, sprite = { w: 16, h: 24, ax: 8, ay: 24 }) {
  const p = cellOnStage({ x: feetPx.x - sprite.ax, y: feetPx.y - sprite.ay }, view);
  return { x: p.x, y: p.y, w: sprite.w * view.zoom, h: sprite.h * view.zoom };
}

/** Compass word for an arrow angle (0 = east, 90 = south). */
export function compassWord(angle) {
  const words = ['east', 'south-east', 'south', 'south-west', 'west', 'north-west', 'north', 'north-east'];
  return words[Math.round((((angle % 360) + 360) % 360) / 45) % 8];
}
