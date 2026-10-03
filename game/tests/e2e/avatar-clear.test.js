// Playtest 1, item 1: the avatar is never under an open panel. The whole level 01 route is played on the real stack and,
// on every simulation step, the avatar's stage rectangle is compared with the rectangle of every visible panel at
// 1366x768 (x4) and 1920x1080 (x6). A panel the camera could not clear must be faded to 35 %.
import { test } from 'node:test';
import assert from 'node:assert/strict';
import { buildHeadlessGame } from '../harness/index.js';
import { playLevel01 } from './level01-script.js';
import { chooseZoom, avatarStageRect, lookAhead } from '../../src/engine/index.js';
import { panelRects, DIALOGUE_RECTS } from '../../src/ui/panels.js';
import { STAGE_W, STAGE_H } from '../../src/shared/layout.js';

const overlap = (a, b) => a.x < b.x + b.w && a.x + a.w > b.x && a.y < b.y + b.h && a.y + a.h > b.y;
const scale = (r, k) => ({ x: r.x * k, y: r.y * k, w: r.w * k, h: r.h * k });

async function walkRoute(opts = {}) {
  const built = await buildHeadlessGame({});
  const { game } = built;
  const seen = { steps: 0, withPanels: 0, faded: new Map(), shifted: 0, unfaded: [] };
  const original = game.viewControl.update.bind(game.viewControl);
  game.viewControl.update = () => {
    const v = original();
    seen.steps += 1;
    if (v.covered) return v;
    const camera = game.world.camera();
    const zoom = 4;
    const av = avatarStageRect(game.world.avatar.feetPx, camera, zoom);
    if (v.panels.length) seen.withPanels += 1;
    if (v.offset.x || v.offset.y) seen.shifted += 1;
    for (const p of v.panels) {
      if (!overlap(av, p)) continue;
      if (v.faded.includes(p.id)) {
        const key = `${p.id}@${game.world.avatar.cell}`;
        seen.faded.set(key, (seen.faded.get(key) || 0) + 1);
      } else {
        seen.unfaded.push({ panel: p.id, cell: [...game.world.avatar.cell], av, p });
      }
    }
    // the camera stays inside the map
    const b = game.data.district.camera_bounds;
    assert.ok(camera.x >= b.x * 16 && camera.x <= (b.x + b.w) * 16 - 320, `camera x ${camera.x} inside the bounds`);
    assert.ok(camera.y >= b.y * 16 && camera.y <= (b.y + b.h) * 16 - 180, `camera y ${camera.y} inside the bounds`);
    return v;
  };
  const out = playLevel01(game, opts);
  return { seen, out, game };
}

test('walking the whole level 01 route, the avatar never sits under a visible panel (faded panels aside)', async () => {
  const { seen } = await walkRoute();
  assert.ok(seen.steps > 1000, `the route ran ${seen.steps} steps`);
  assert.ok(seen.withPanels > 500, 'panels were open for most of the route');
  assert.deepEqual(seen.unfaded, [], 'no panel covers the avatar without being faded');
  console.log(`avatar-clear: ${seen.steps} steps, ${seen.shifted} shifted, faded at ${[...seen.faded.keys()].join(' | ') || 'nowhere'}`);
});

test('the same holds at 1366x768 (x4) and 1920x1080 (x6): the stage scales as a whole, so rectangles keep their relation', async () => {
  for (const [w, h] of [[1366, 768], [1920, 1080]]) {
    const zoom = chooseZoom(w, h);
    assert.equal(zoom, w === 1366 ? 4 : 6);
    const k = zoom / 4;                           // the stage (1280x720) is scaled by zoom / 4
    assert.ok(STAGE_W * k <= w && STAGE_H * k <= h, 'the stage fits the window');
    const { seen } = await walkRoute();
    // Every sampled relation is identical in viewport px: scaling both rectangles by k cannot create an overlap.
    assert.deepEqual(seen.unfaded.map((u) => overlap(scale(u.av, k), scale(u.p, k))), []);
  }
});

test('lookAhead: clears a bottom panel when the bounds allow it and fades what it cannot clear', () => {
  const bounds = { x: 0, y: 0, w: 28, h: 18 };
  const dialogue = { id: 'dialogue', ...DIALOGUE_RECTS.conversation };
  // mid map: the avatar is centred, nothing to do
  const mid = lookAhead({ feetPx: { x: 200, y: 120 }, bounds, panels: [dialogue] });
  assert.deepEqual(mid.offset, { x: 0, y: 0 });
  // a panel across the lower half with room above: the camera moves the avatar clear of it, nothing is faded
  const near = lookAhead({ feetPx: { x: 200, y: 150 }, bounds, panels: [{ id: 'low', x: 0, y: 330, w: 1280, h: 400 }] });
  assert.deepEqual(near.faded, []);
  assert.ok(near.offset.y > 0 || near.offset.x !== 0, 'the camera moved');
  assert.ok(!overlap(avatarStageRect({ x: 200, y: 150 }, near.camera), { x: 0, y: 330, w: 1280, h: 400 }));
  // the south wall: the camera is already at the bottom bound, so the panel is faded
  const south = lookAhead({ feetPx: { x: 300, y: 270 }, bounds, panels: [{ id: 'inset', x: 16, y: 412, w: 572, h: 292 }, { id: 'dialogue', ...DIALOGUE_RECTS.conversation }] });
  assert.ok(south.faded.includes('dialogue'), `faded ${south.faded}`);
  const av = avatarStageRect({ x: 300, y: 270 }, south.camera);
  assert.ok(south.camera.y <= 108 && south.camera.y >= 0, 'clamped to the bounds');
  assert.ok(av.y > 0);
  // no panels: the plain camera
  assert.deepEqual(lookAhead({ feetPx: { x: 10, y: 10 }, bounds, panels: [] }).offset, { x: 0, y: 0 });
});

test('panelRects: full-screen layers need no clearance; the compact HUD drops its strip', () => {
  assert.equal(panelRects({ 'vm:journal': {} }).covered, true);
  const open = panelRects({ 'vm:dialogue': { mode: 'instruction' }, 'vm:inset': {}, 'vm:hud': { compact: true } });
  assert.deepEqual(open.panels.map((p) => p.id), ['dialogue', 'inset', 'hud-chips']);
  const idle = panelRects({ 'vm:hud': { compact: false } });
  assert.deepEqual(idle.panels.map((p) => p.id), ['hud', 'hud-chips']);
});
