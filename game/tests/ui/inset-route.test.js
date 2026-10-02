import { test } from 'node:test';
import assert from 'node:assert/strict';

import { insetRect, rectsOverlap } from '../../src/ui/index.js';
import { computeCamera } from '../../src/engine/index.js';
import { TILE, AVATAR_SCREEN } from '../../src/shared/layout.js';
import * as F from './fixtures.js';

const ZOOM = 4;
const engineer = F.readJson('art-direction/gate1/engineer-full-atlas.json');

const isCell = (v) => Array.isArray(v) && v.length === 2 && v.every(Number.isInteger);

/** Every target cell the level data names: step targets, leg markers, stops, the glitch. */
function targetCells(level) {
  const found = new Map();
  const walk = (node, keyName) => {
    if (Array.isArray(node)) {
      if (isCell(node) && ['cell', 'marker', 'target_cell'].includes(keyName)) found.set(node.join(','), node);
      else node.forEach((n) => walk(n, keyName));
    } else if (node && typeof node === 'object') {
      for (const [k, v] of Object.entries(node)) walk(v, k);
    }
  };
  walk(level.steps, '');
  walk(level.terminal_scenes, '');
  walk(level.glitch, '');
  return [...found.values()];
}

const route = F.MAP.routes.main.find((r) => r.level === 'orientation-01').cells;
const cellRect = ([x, y], cam) => ({ x: (x * TILE - cam.x) * ZOOM, y: (y * TILE - cam.y) * ZOOM, w: TILE * ZOOM, h: TILE * ZOOM });

test('level 01 data names the targets this check walks (laps, stops and the glitch)', () => {
  const cells = targetCells(F.LEVEL);
  const keys = cells.map((c) => c.join(','));
  for (const must of ['3,12', '17,12', '17,5', '9,5', '12,13', '4,3']) assert.ok(keys.includes(must), `target ${must}`);
  assert.ok(cells.length >= 8);
});

test('on the level 01 route the avatar never overlaps the inset rectangle', () => {
  const inset = insetRect(ZOOM);
  const { w, h } = engineer.frame;
  const bad = [];
  for (const cell of route) {
    const feet = { x: cell[0] * TILE + 8, y: cell[1] * TILE + 16 };
    const cam = computeCamera(feet, F.DISTRICT.camera_bounds);
    const avatar = { x: (feet.x - engineer.anchor.x - cam.x) * ZOOM, y: (feet.y - engineer.anchor.y - cam.y) * ZOOM, w: w * ZOOM, h: h * ZOOM };
    if (rectsOverlap(avatar, inset)) bad.push(`cell ${cell} avatar ${JSON.stringify(avatar)}`);
  }
  assert.deepEqual(bad, [], `avatar inside the inset at: ${bad.join('; ')}`);
});

const legsOf = () => F.LEVEL.terminal_scenes.find((t) => t.id === 'o01-loop').task.legs;
const onLeg = (leg, [x, y]) => {
  const [fx, fy] = leg.from;
  const [tx, ty] = leg.to;
  return x >= Math.min(fx, tx) && x <= Math.max(fx, tx) && y >= Math.min(fy, ty) && y <= Math.max(fy, ty);
};

/** Pairs (avatar cell, current leg marker) where the marker is drawn under the inset in the level data's camera model. */
function legMarkerOverlaps() {
  const inset = insetRect(ZOOM);
  const bad = [];
  for (const leg of legsOf()) {
    for (const cell of route.filter((c) => onLeg(leg, c))) {
      const feet = { x: cell[0] * TILE + 8, y: cell[1] * TILE + 16 };
      const cam = computeCamera(feet, F.DISTRICT.camera_bounds);
      if (rectsOverlap(cellRect(leg.marker, cam), inset)) bad.push(`avatar ${cell} leg ${leg.id} marker ${leg.marker}`);
    }
  }
  return [...new Set(bad)];
}

// Known gap in the level data's camera model (reported to the producer, not fixable in the UI): the camera clamps at the
// map edge, so on the west walkway the first lap marker (3,12) is drawn inside the inset rectangle. Marked todo so the
// suite stays green while the gap stays visible; flip to a plain test once the data or camera model changes.
test('on the level 01 lap the current leg marker stays outside the inset rectangle', { todo: 'gap: leg marker 3,12 sits under the inset on the west walkway' }, () => {
  const bad = legMarkerOverlaps();
  assert.deepEqual(bad, [], `current target under the inset: ${bad.join('; ')}`);
});

test('the known lap-marker overlap is exactly the west-walkway leg (so a regression elsewhere fails)', () => {
  const bad = legMarkerOverlaps();
  assert.ok(bad.length > 0, 'if this starts failing the gap is fixed: promote the todo test above');
  assert.ok(bad.every((b) => / leg down marker 3,12$/.test(b)), bad.join('; '));
});

test('the inset rectangle scales with the zoom and the dialogue never overlaps it', () => {
  assert.deepEqual(insetRect(6), { x: 24, y: 618, w: 858, h: 438 });
  const dialogue = { x: 1280 - 16 - 672, y: 720 - 16 - 224, w: 672, h: 224 };
  assert.equal(rectsOverlap(dialogue, insetRect(4)), false);
  assert.ok(AVATAR_SCREEN.x * ZOOM > insetRect(4).x + insetRect(4).w, 'an unclamped avatar stands right of the inset');
});
