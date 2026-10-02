// Engine module public surface. Contract: game/CONTRACTS.md section 3.
// Stubs: workstream A replaces the throwing bodies. Pure helpers are already real.
import { AVATAR_SCREEN, TILE, VIEW_H, VIEW_W, WALK_FRAME_STEPS } from '../shared/layout.js';

const nyi = () => {
  throw new Error('not implemented');
};

export const DATA_FILES = {
  district: '/design/levels/orientation/district.json',
  map: '/design/levels/orientation/map.json',
  level: '/design/levels/orientation/levels/01-the-lobby.json',
  world: '/design/levels/world.json',
  gestureInventory: '/design/levels/gesture-inventory.json',
  layoutManifest: '/design/layout/layout-manifest.json',
};

export const ATLAS_FILES = {
  kit: { json: '/art-direction/kit/orientation-atlas.json', png: '/art-direction/kit/orientation-atlas.png' },
  engineer: { json: '/art-direction/gate1/engineer-full-atlas.json', png: '/art-direction/gate1/engineer-full-atlas.png' },
  ivo: { json: '/art-direction/cast/ivo-atlas.json', png: '/art-direction/cast/ivo-atlas.png' },
  mira: { json: '/art-direction/cast/mira-atlas.json', png: '/art-direction/cast/mira-atlas.png' },
  bgworker_a: { json: '/art-direction/cast/bgworker_a-atlas.json', png: '/art-direction/cast/bgworker_a-atlas.png' },
  bgworker_b: { json: '/art-direction/cast/bgworker_b-atlas.json', png: '/art-direction/cast/bgworker_b-atlas.png' },
  glitches: { json: '/art-direction/glitches/glitches-atlas.json', png: '/art-direction/glitches/glitches-atlas.png' },
  pace: { json: '/art-direction/pace/pace-atlas.json', png: '/art-direction/pace/pace-atlas.png' },
  portraits: { json: '/art-direction/portraits/portraits-atlas.json', png: '/art-direction/portraits/portraits-atlas.png' },
};

/** @returns {Promise<object>} GameData; throws DataLoadError naming the file. */
export async function loadGameData(opts = {}) { nyi(); }
export async function loadJson(path, opts = {}) { nyi(); }
export async function loadAtlasSet(opts = {}) { nyi(); }

export class AtlasSet {
  image(id) { nyi(); }
  kitEntry(name) { nyi(); }
  stateSet(name) { nyi(); }
  landmark(name) { nyi(); }
  animation(name) { nyi(); }
  personAtlas(characterId) { nyi(); }
  portrait(key) { nyi(); }
  glitch(archetype) { nyi(); }
}

export class AnimationPlayer {
  constructor(def, opts = {}) { nyi(); }
  update(dtMs) { nyi(); }
  get frameIndex() { nyi(); }
  get done() { nyi(); }
  reset() { nyi(); }
}

/** Walk frame index after `steps` simulation steps (pure). */
export function frameForSteps(def, steps) {
  return Math.floor(steps / WALK_FRAME_STEPS) % def.frames;
}

export class World {
  constructor(data, atlases, opts = {}) { nyi(); }
  placementState(id) { nyi(); }
  setPlacementState(id, state) { nyi(); }
  playStateSet(id, sequence, opts) { nyi(); }
  setNpcState(npcId, state) { nyi(); }
  npc(npcId) { nyi(); }
  openGate(gateId) { nyi(); }
  isGateOpen(gateId) { nyi(); }
  isBlocked(x, y) { nyi(); }
  spawnGlitch(interactionId) { nyi(); }
  repairGlitch(interactionId) { nyi(); }
  update(stepMs) { nyi(); }
  snapshot() { nyi(); }
  restore(slice) { nyi(); }
  serialize() { nyi(); }
}

export class Avatar {
  get moving() { nyi(); }
  requestStep(dir) { nyi(); }
  setHeld(dir) { nyi(); }
  update() { nyi(); }
  teleport(cell, facing) { nyi(); }
}

/** Camera top-left in map px: feet at AVATAR_SCREEN, clamped to camera_bounds (cells). Pure. */
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

/** Map pixel point to the 1280x720 stage. Pure. */
export function worldToStage(pointPx, camera, zoom) {
  return { x: (pointPx.x - camera.x) * zoom, y: (pointPx.y - camera.y) * zoom };
}

/** Largest whole zoom that fits the window (pure). 1366x768 -> 4, 1920x1080 -> 6. */
export function chooseZoom(winW, winH) {
  return Math.max(1, Math.floor(Math.min(winW / VIEW_W, winH / VIEW_H)));
}

export class GameLoop {
  constructor(params) { nyi(); }
  start() { nyi(); }
  stop() { nyi(); }
  tick(nowMs) { nyi(); }
  advance(ms) { nyi(); }
  get stepCount() { nyi(); }
}

export class Renderer {
  constructor(params) { nyi(); }
  resize(winW, winH) { nyi(); }
  setReducedMotion(on) { nyi(); }
  draw(view, camera) { nyi(); }
}
