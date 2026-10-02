import { test } from 'node:test';
import assert from 'node:assert/strict';
import { computeCamera, worldToStage, chooseZoom, Avatar, GameLoop } from '../../src/engine/index.js';
import { CELL_STEPS, STEP_MS, FakeClock } from '../../src/shared/index.js';
import { newWorld, run, realData } from './helpers.js';

const BOUNDS = { x: 0, y: 0, w: 28, h: 18 };

test('camera puts the feet at (160,100) and clamps to the district bounds', () => {
  assert.deepEqual(computeCamera({ x: 13 * 16 + 8, y: 12 * 16 + 16 }, BOUNDS), { x: 13 * 16 + 8 - 160, y: 12 * 16 + 16 - 100 });
  assert.deepEqual(computeCamera({ x: 3 * 16 + 8, y: 2 * 16 + 16 }, BOUNDS), { x: 0, y: 0 }); // arrival: top-left clamp
  assert.deepEqual(computeCamera({ x: 27 * 16, y: 17 * 16 }, BOUNDS), { x: 28 * 16 - 320, y: 18 * 16 - 180 });
  // smaller than the view: pinned to the bounds origin
  assert.deepEqual(computeCamera({ x: 500, y: 500 }, { x: 2, y: 3, w: 10, h: 5 }), { x: 32, y: 48 });
});

test('camera moves one pixel per pixel of travel', () => {
  const a = computeCamera({ x: 200, y: 150 }, BOUNDS);
  const b = computeCamera({ x: 201, y: 150 }, BOUNDS);
  assert.equal(b.x - a.x, 1);
});

test('zoom and stage mapping', () => {
  assert.equal(chooseZoom(1366, 768), 4);
  assert.equal(chooseZoom(1920, 1080), 6);
  assert.equal(chooseZoom(300, 100), 1);
  assert.deepEqual(worldToStage({ x: 170, y: 120 }, { x: 10, y: 20 }, 4), { x: 640, y: 400 });
});

test('the hub camera shows the garden: avatar feet land at stage (640, 400) at x4', async () => {
  const { world } = await newWorld();
  world.avatar.teleport([13, 12], 's');
  const cam = world.camera();
  const feet = world.avatar.feetPx;
  assert.deepEqual(worldToStage(feet, cam, 4), { x: 640, y: 400 });
});

test('a step takes 16 sim steps and moves 1 px per step', async () => {
  const { world, events } = await newWorld();
  const a = world.avatar;
  assert.deepEqual(a.cell, [3, 2]);
  assert.equal(a.requestStep('s'), 'started');
  assert.equal(a.requestStep('s'), 'busy');
  const y0 = a.feetPx.y;
  for (let i = 1; i <= CELL_STEPS; i += 1) {
    run(world, 1);
    if (i < CELL_STEPS) assert.equal(a.feetPx.y - y0, i);
  }
  assert.deepEqual(a.cell, [3, 3]);
  assert.equal(a.moving, false);
  assert.equal(a.feetPx.y - y0, 16);
  const done = events.filter(([t]) => t === 'engine:step-complete');
  assert.equal(done.length, 1);
  assert.deepEqual(done[0][1], { cell: [3, 3], facing: 's', dir: 's' });
});

test('walls block: the avatar turns, stays put and reports blocked', async () => {
  const { world, events } = await newWorld();
  const a = world.avatar;
  assert.equal(a.requestStep('n'), 'blocked'); // (3,1) is the elevator car, closed
  assert.equal(a.facing, 'n');
  assert.equal(a.moving, false);
  assert.deepEqual(a.cell, [3, 2]);
  assert.deepEqual(events.find(([t]) => t === 'engine:blocked')[1], { cell: [3, 2], dir: 'n' });
  assert.equal(a.requestStep('w'), 'started');
});

test('map edges are walls and out of range is blocked', async () => {
  const { world } = await newWorld();
  for (const [x, y] of [[-1, 0], [0, -1], [28, 3], [3, 18], [1.5, 3], [NaN, 2]]) assert.equal(world.isBlocked(x, y), true, `${x},${y}`);
  for (let x = 0; x < 28; x += 1) {
    assert.equal(world.isBlocked(x, 0), true);
    assert.equal(world.isBlocked(x, 17), true);
  }
  for (let y = 0; y < 18; y += 1) assert.equal(world.isBlocked(0, y), true);
});

test('held key repeats seamlessly and stops at a wall', async () => {
  const { world, events } = await newWorld();
  const a = world.avatar;
  a.setHeld('s');
  run(world, CELL_STEPS * 3);
  assert.deepEqual(a.cell, [3, 5]);
  assert.equal(a.moving, true); // already on the next step: no idle gap
  a.setHeld(null);
  run(world, CELL_STEPS);
  assert.deepEqual(a.cell, [3, 6]);
  assert.equal(a.moving, false);
  assert.equal(events.filter(([t]) => t === 'engine:step-complete').length, 4);
});

test('a held key into a wall reports blocked once, not every step', async () => {
  const { world, events } = await newWorld();
  const a = world.avatar;
  a.setHeld('n');
  run(world, 60);
  assert.equal(events.filter(([t]) => t === 'engine:blocked').length, 1);
  assert.equal(a.facing, 'n');
  a.setHeld('w');
  run(world, CELL_STEPS);
  assert.deepEqual(a.cell, [2, 2]);
});

test('walk frames are continuous across a held run and reset after stopping', async () => {
  const { world } = await newWorld();
  const a = world.avatar;
  a.setHeld('s');
  const seen = [];
  for (let i = 0; i < 40; i += 1) {
    run(world, 1);
    seen.push(world.avatarFrame().frame);
  }
  assert.deepEqual(seen.slice(0, 8), Array(8).fill(0));
  assert.deepEqual(seen.slice(8, 16), Array(8).fill(1));
  assert.deepEqual(seen.slice(16, 24), Array(8).fill(2));
  assert.deepEqual(seen.slice(32, 40), Array(8).fill(0)); // wraps after 4 frames
  assert.equal(world.avatarFrame().name, 'engineer_walk_s');
});

test('four directions each draw the matching walk row', async () => {
  const { world } = await newWorld();
  world.avatar.teleport([13, 12], 's');
  const rows = {};
  for (const d of ['s', 'n', 'e', 'w']) {
    world.avatar.requestStep(d);
    run(world, 4);
    const snap = world.snapshot();
    const actor = snap.layers.actor.find((x) => x.atlas === 'engineer');
    rows[d] = actor.rect.y / 24;
    assert.equal(world.avatarFrame().name, `engineer_walk_${d}`);
    run(world, 12);
  }
  assert.deepEqual(rows, { s: 4, n: 5, e: 6, w: 7 });
});

function script(world, moves) {
  const trace = [];
  for (const [dir, steps] of moves) {
    world.avatar.setHeld(dir);
    for (let i = 0; i < steps; i += 1) {
      world.update(STEP_MS);
      trace.push(`${world.avatar.cell}|${world.avatar.feetPx.x},${world.avatar.feetPx.y}`);
    }
  }
  return trace.join(';');
}

test('same script gives the same positions (determinism)', async () => {
  const moves = [['s', 150], ['e', 200], [null, 20], ['n', 90], ['w', 70], ['s', 33]];
  const a = script((await newWorld()).world, moves);
  const b = script((await newWorld()).world, moves);
  assert.equal(a, b);
});

test('the level 01 lap is walkable end to end with a held key', async () => {
  const { world, data } = await newWorld();
  const route = data.map.routes.main[0].cells;
  for (const [x, y] of route) assert.equal(world.isBlocked(x, y), false, `route cell ${x},${y}`);
  // follow the route cell by cell
  let at = route[0];
  assert.deepEqual(world.avatar.cell, at);
  for (const next of route.slice(1)) {
    const dir = next[0] > at[0] ? 'e' : next[0] < at[0] ? 'w' : next[1] > at[1] ? 's' : 'n';
    assert.equal(world.avatar.requestStep(dir), 'started', `${at}->${next}`);
    run(world, CELL_STEPS);
    assert.deepEqual(world.avatar.cell, next);
    at = next;
  }
});

test('Avatar works standalone on any blocked predicate', () => {
  const a = new Avatar({ isBlocked: (x) => x > 1, cell: [0, 0], facing: 's' });
  a.setHeld('e');
  for (let i = 0; i < 100; i += 1) a.update();
  assert.deepEqual(a.cell, [1, 0]);
  assert.throws(() => a.requestStep('up'));
  a.teleport([0, 0], 'w');
  assert.equal(a.facing, 'w');
  assert.equal(a.moving, false);
});

test('GameLoop runs whole fixed steps, caps at five, renders once per tick', () => {
  const clock = new FakeClock(1000);
  let updates = 0;
  let renders = 0;
  const loop = new GameLoop({ clock, update: () => { updates += 1; }, render: () => { renders += 1; } });
  loop.start();
  loop.tick(1000 + STEP_MS * 3 + 1);
  assert.equal(updates, 3);
  assert.equal(renders, 1);
  loop.tick(1000 + STEP_MS * 3 + 1 + 5000); // a long stall: capped, backlog dropped
  assert.equal(updates, 8);
  assert.equal(loop.stepCount, 8);
  loop.tick(1000 + STEP_MS * 3 + 1 + 5000 + 1);
  assert.equal(updates, 8);
  assert.equal(renders, 3);
  loop.advance(1000);
  assert.equal(updates, 68);
  assert.equal(loop.stepCount, 68);
  assert.equal(renders, 3);
});

test('GameLoop uses the injected raf and clock, and stop cancels it', () => {
  const clock = new FakeClock(0);
  const queue = [];
  const cancelled = [];
  let n = 0;
  const loop = new GameLoop({
    clock, update: () => {}, render: () => {},
    raf: (fn) => { queue.push(fn); return ++n; },
    caf: (h) => cancelled.push(h),
  });
  loop.start();
  assert.equal(queue.length, 1);
  clock.advance(100);
  queue.shift()();
  assert.equal(loop.stepCount, 5);
  assert.equal(queue.length, 1);
  loop.stop();
  assert.deepEqual(cancelled, [2]);
  queue.shift()();
  assert.equal(queue.length, 0);
});

test('realData is shared and stable', async () => {
  assert.equal((await realData()).data, (await realData()).data);
});
