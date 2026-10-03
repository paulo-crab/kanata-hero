// Playtest 1, item 1: every walkable cell of the district with the dialogue, the inset and the HUD all open.
import { test } from 'node:test';
import assert from 'node:assert/strict';
import { buildHeadlessGame } from '../harness/index.js';
import { avatarStageRect } from '../../src/engine/index.js';

const overlap = (a, b) => a.x < b.x + b.w && a.x + a.w > b.x && a.y < b.y + b.h && a.y + a.h > b.y;

for (const larger of [false, true]) {
test(`every walkable cell (larger text ${larger}): cleared by the camera, or the covering panel is faded (and the camera stays in the bounds)`, async () => {
  const { game } = await buildHeadlessGame({});
  const vc = game.viewControl;
  vc.vms = { 'vm:dialogue': { mode: 'conversation' }, 'vm:inset': {}, 'vm:hud': { compact: false }, 'vm:settings-flags': { largerText: larger } };
  const rows = game.data.map.collision;
  const b = game.data.district.camera_bounds;
  let cells = 0;
  let shifted = 0;
  const faded = [];
  for (let y = 0; y < rows.length; y += 1) {
    for (let x = 0; x < rows[0].length; x += 1) {
      if (game.world.isBlocked(x, y)) continue;
      game.world.avatar.teleport([x, y], 's');
      const v = vc.update();
      cells += 1;
      const cam = game.world.camera();
      assert.ok(cam.x >= b.x * 16 && cam.x <= (b.x + b.w) * 16 - 320 && cam.y >= b.y * 16 && cam.y <= (b.y + b.h) * 16 - 180);
      const av = avatarStageRect(game.world.avatar.feetPx, cam, 4);
      if (v.offset.x || v.offset.y) shifted += 1;
      for (const p of v.panels) {
        if (!overlap(av, p)) continue;
        assert.ok(v.faded.includes(p.id), `cell ${x},${y}: ${p.id} covers the avatar and is not faded`);
        faded.push(`${x},${y}:${p.id}`);
      }
    }
  }
  console.log(`every-cell: ${cells} cells, ${shifted} shifted, ${faded.length} faded`);
  assert.ok(cells > 100);
  if (larger) assert.ok(shifted > 0, 'the look-ahead moved the camera for some cells');
});
}
