// Task 6.3 (model half): the avatar and the current target must stay outside the keyboard inset
// rectangle, using the level data's camera model (design/levels/SCHEMA.md). The browser script in
// game/tools/browser-check.mjs runs the same model against the live page.
import { test } from 'node:test';
import assert from 'node:assert/strict';
import {
  loadRealData, insetViolations, insetStageRect, rectsOverlap, cellStageRect, cameraFor, level01Legs, targetDisplay, STAGE_ZOOM,
} from '../harness/index.js';
import { INSET_STAGE_RECT } from '../../src/shared/layout.js';
import { DIALOGUE_STAGE_RECT } from '../../src/ui/index.js';

const data = loadRealData();
const fmt = (v) => v.map((x) => `${x.leg}: avatar cell (${x.cell}) ${x.what}${x.target ? ` (target ${x.target})` : ''}`);

test('inset rectangle model equals the contract constant at x4', () => {
  assert.deepEqual(insetStageRect(4), INSET_STAGE_RECT);
  assert.deepEqual(insetStageRect(6), { x: 24, y: 618, w: 858, h: 438 });
});

test('the model flags an overlap (negative control)', () => {
  const cam = cameraFor([3, 12], data.district.camera_bounds);
  // a cell drawn at the bottom-left of the stage sits inside the inset
  assert.equal(rectsOverlap(cellStageRect([3, 14], cam), insetStageRect()), true);
  assert.equal(rectsOverlap({ x: 0, y: 0, w: 10, h: 10 }, { x: 10, y: 0, w: 5, h: 5 }), false);
});

test('level 01 inset legs are exactly the guided and variation scenes', () => {
  const withInset = level01Legs(data).filter((l) => l.inset).map((l) => l.scene);
  assert.deepEqual([...new Set(withInset)], ['o01-loop', 'o01-four-stops']);
});

test('the avatar never stands inside the inset along level 01 (cell listed on failure)', () => {
  const v = insetViolations(data).filter((x) => x.what === 'avatar');
  assert.deepEqual(fmt(v), []);
});

// The level data's camera model draws the first lap marker (3,12) and the west desk (7,10) under the inset while the
// avatar approaches. The UI keeps the inset where the kit puts it and shows the current target as an edge arrow in the
// free area instead (ui/world-space.js targetIndicator), so the visible indicator is never under the inset.
test('the current target is never hidden by the inset (a covered marker becomes an edge arrow)', () => {
  const v = insetViolations(data).filter((x) => x.what === 'target');
  assert.deepEqual(fmt(v), []);
});

test('the edge arrow is used exactly where the marker is under the inset or off the stage, and keeps clear of avatar and dialogue', () => {
  const bounds = data.district.camera_bounds;
  const inset = insetStageRect(STAGE_ZOOM);
  const used = new Set();
  for (const leg of level01Legs(data).filter((l) => l.inset)) {
    for (const cell of leg.cells) {
      const shown = targetDisplay(cell, leg, bounds);
      if (shown.kind === 'edge-arrow') {
        used.add(leg.id);
        assert.equal(rectsOverlap(shown.rect, inset), false, `${leg.id} (${cell}) arrow under the inset`);
        assert.equal(rectsOverlap(shown.rect, shown.avatar), false, `${leg.id} (${cell}) arrow over the avatar`);
        assert.equal(rectsOverlap(shown.rect, DIALOGUE_STAGE_RECT), false, `${leg.id} (${cell}) arrow under the dialogue panel`);
      } else {
        assert.equal(rectsOverlap(shown.rect, inset), false, `${leg.id} (${cell}) marker under the inset`);
      }
    }
  }
  // the west walkway lap leg and the west desk leg sit under the inset; the lap's north-going leg has its marker above the stage
  assert.deepEqual([...used].sort(), ['loop-down', 'loop-up', 'stop-west']);
});

test('x4 and x6 share the same logical stage model', () => {
  assert.equal(STAGE_ZOOM, 4);
  assert.deepEqual(insetViolations(data, { zoom: 6 }).length, insetViolations(data, { zoom: 4 }).length);
});
