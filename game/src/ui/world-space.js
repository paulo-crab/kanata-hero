// Map pixels to stage pixels for markers and the interaction prompt.
// The runtime sends `at` in MAP pixels (cell * 16, top-left of the cell) and has no camera, so the UI converts.
// The camera and zoom reach the UI as `ui:view {camera:{x,y}, zoom}` on the bus (the renderer's boot adapter emits it
// when either changes) or through the `getView()` parameter of mountUi.
import { TILE, STAGE_W, STAGE_H } from '../shared/layout.js';

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
