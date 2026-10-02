// Camera and zoom helpers. Contract sections 3.3 and 3.4. All pure.
import { AVATAR_SCREEN, TILE, VIEW_H, VIEW_W } from '../shared/index.js';

/** Camera top-left in map px: feet at AVATAR_SCREEN, clamped to camera_bounds (cells). */
export function computeCamera(feetPx, bounds) {
  const minX = bounds.x * TILE;
  const minY = bounds.y * TILE;
  const maxX = (bounds.x + bounds.w) * TILE - VIEW_W;
  const maxY = (bounds.y + bounds.h) * TILE - VIEW_H;
  return {
    x: Math.min(Math.max(feetPx.x - AVATAR_SCREEN.x, minX), Math.max(minX, maxX)),
    y: Math.min(Math.max(feetPx.y - AVATAR_SCREEN.y, minY), Math.max(minY, maxY)),
  };
}

/** Map pixel point to the 1280x720 stage. */
export function worldToStage(pointPx, camera, zoom) {
  return { x: (pointPx.x - camera.x) * zoom, y: (pointPx.y - camera.y) * zoom };
}

/** Largest whole zoom that fits the window. 1366x768 -> 4, 1920x1080 -> 6. */
export function chooseZoom(winW, winH) {
  return Math.max(1, Math.floor(Math.min(winW / VIEW_W, winH / VIEW_H)));
}
