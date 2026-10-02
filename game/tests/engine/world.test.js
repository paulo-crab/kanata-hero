import { test } from 'node:test';
import assert from 'node:assert/strict';
import { World } from '../../src/engine/index.js';
import { CELL_STEPS, STEP_MS } from '../../src/shared/index.js';
import { newWorld, run, realData } from './helpers.js';

const cellsOf = (set) => set.map(([x, y]) => `${x},${y}`);

test('default collision equals the map grid except the glitch-free hub, with npcs added', async () => {
  const { world, data } = await newWorld();
  const diffs = [];
  for (let y = 0; y < 18; y += 1) {
    for (let x = 0; x < 28; x += 1) {
      const base = data.map.collision[y][x] === '1';
      if (world.isBlocked(x, y) !== base) diffs.push(`${x},${y}`);
    }
  }
  // the only differences are standing npcs: Ivo at (5,3) and Mira at (24,8)
  assert.deepEqual(diffs.sort(), ['24,8', '5,3']);
});

test('gates start closed and block their cells; opening frees them in the same call', async () => {
  const { world, data } = await newWorld();
  for (const g of data.map.gates) {
    assert.equal(world.isGateOpen(g.id), false);
    for (const [x, y] of g.cells) assert.equal(world.isBlocked(x, y), true, `${g.id} ${x},${y}`);
  }
  world.openGate('g.turnstile');
  assert.equal(world.isGateOpen('g.turnstile'), true);
  assert.equal(world.isBlocked(23, 12), false);
  assert.equal(world.isBlocked(22, 12), true); // pedestals stay solid
  assert.equal(world.isBlocked(24, 12), true);
  assert.equal(world.placementState('turnstile'), 'open');
  assert.throws(() => world.openGate('g.nope'));
});

test('avatar can walk through the turnstile lane only after it opens', async () => {
  const { world } = await newWorld();
  world.avatar.teleport([23, 11], 's');
  assert.equal(world.avatar.requestStep('s'), 'blocked');
  world.openGate('g.turnstile');
  assert.equal(world.avatar.requestStep('s'), 'started');
  run(world, CELL_STEPS);
  assert.deepEqual(world.avatar.cell, [23, 12]);
});

test('records door and garden cut-through open with their art states', async () => {
  const { world } = await newWorld();
  assert.equal(world.isBlocked(12, 8), true);
  world.openGate('g.garden-cutthrough');
  for (const y of [7, 8, 9, 10]) assert.equal(world.isBlocked(12, y), false);
  assert.equal(world.placementState('garden'), 'after');
  assert.equal(world.isBlocked(11, 8), true);
  world.openGate('g.records-door');
  assert.equal(world.isBlocked(26, 6), false);
  assert.equal(world.isBlocked(27, 7), false);
});

test('the elevator plays closed, half, open in 120 ms steps and frees the car', async () => {
  const { world, events } = await newWorld();
  assert.equal(world.placementState('elevator'), 'closed');
  assert.equal(world.isBlocked(3, 1), true);
  world.playStateSet('elevator', ['closed', 'half', 'open']);
  assert.equal(world.placementState('elevator'), 'closed');
  run(world, 7); // 116.7 ms
  assert.equal(world.placementState('elevator'), 'closed');
  run(world, 1); // 133 ms
  assert.equal(world.placementState('elevator'), 'half');
  assert.equal(world.isBlocked(3, 1), true);
  run(world, 8);
  assert.equal(world.placementState('elevator'), 'open');
  assert.equal(world.isBlocked(3, 1), false);
  assert.equal(world.isBlocked(2, 1), true);
  const done = events.filter(([t]) => t === 'engine:stateset-done');
  assert.deepEqual(done.map(([, p]) => p), [{ placement: 'elevator', state: 'open' }]);
  // and backwards on leave
  world.playStateSet('elevator', ['closed', 'half', 'open'], { reverse: true });
  assert.equal(world.placementState('elevator'), 'open');
  run(world, 20);
  assert.equal(world.placementState('elevator'), 'closed');
  assert.equal(world.isBlocked(3, 1), true);
});

test('setPlacementState rebuilds collision on the same call, and rejects bad states', async () => {
  const { world } = await newWorld();
  assert.equal(world.isBlocked(20, 7), false);
  world.setPlacementState('seating_nook', 'shown');
  assert.equal(world.isBlocked(20, 7), true);
  world.setPlacementState('seating_nook', 'hidden');
  assert.equal(world.isBlocked(20, 7), false);
  assert.throws(() => world.setPlacementState('seating_nook', 'nope'));
  assert.throws(() => world.setPlacementState('wall_n_00', 'x'));
  assert.equal(world.placementState('wall_n_00'), null);
  world.setPlacementState('lamp_printer', 'on');
  assert.equal(world.placementState('lamp_printer'), 'on');
});

test('npc state moves Ivo between his cells with the right poses', async () => {
  const { world } = await newWorld();
  let ivo = world.npc('ivo');
  assert.deepEqual([ivo.cell, ivo.pose, ivo.facing], [[5, 3], 'ivo_wave_s', 's']);
  assert.equal(world.isBlocked(5, 3), true);
  world.setNpcState('ivo', 'north');
  ivo = world.npc('ivo');
  assert.deepEqual([ivo.cell, ivo.pose], [[10, 4], 'ivo_interact_s']);
  assert.equal(world.isBlocked(5, 3), false);
  assert.equal(world.isBlocked(10, 4), true);
  world.setNpcState('ivo', 'post_nod');
  assert.deepEqual(world.npc('ivo').cell, [12, 14]);
  assert.equal(world.npc('ivo').pose, 'ivo_nod_s');
  assert.throws(() => world.setNpcState('ivo', 'dancing'));
  assert.throws(() => world.setNpcState('nobody', 'start'));
  assert.equal(world.npc('nobody'), null);
});

test('Ivo nods once and holds the last frame; reduced motion holds the wave on frame 0', async () => {
  const { world } = await newWorld();
  const ivoDraw = (w) => w.snapshot().layers.actor.find((d) => d.atlas === 'ivo');
  world.setNpcState('ivo', 'post_nod');
  run(world, 200);
  const row = world.atlases.animation('ivo_nod_s');
  assert.equal(ivoDraw(world).rect.x, (row.frames - 1) * 16);
  const rm = (await newWorld({ reducedMotion: true })).world;
  run(rm, 400);
  assert.equal(ivoDraw(rm).rect.x, 0);
  rm.setReducedMotion(false);
  run(rm, 30);
  assert.ok(ivoDraw(rm).rect.x > 0);
});

test('background workers walk the same loop on one shared clock', async () => {
  const { world } = await newWorld();
  const a0 = world.npc('worker_a');
  const b0 = world.npc('worker_b');
  assert.deepEqual([a0.cell, b0.cell], [[4, 6], [6, 6]]);
  const seen = [];
  for (let i = 0; i < CELL_STEPS * 5; i += 1) {
    run(world, 1);
    const a = world.npc('worker_a');
    const b = world.npc('worker_b');
    // same phase: b is always a's cell shifted by the +2 x offset between the two loops
    assert.deepEqual([b.cell[0] - a.cell[0], b.cell[1] - a.cell[1], b.facing === a.facing], [2, 0, true]);
    seen.push(`${a.cell}`);
  }
  assert.deepEqual([...new Set(seen)], ['4,6', '5,6', '5,7', '4,7']);
  // frames identical on both
  const frames = world.snapshot().layers.actor.filter((d) => d.atlas === 'bgworker_a' || d.atlas === 'bgworker_b');
  assert.equal(frames.length, 2);
  assert.equal(frames[0].rect.x, frames[1].rect.x);
  assert.equal(frames[0].rect.y, frames[1].rect.y);
  // workers never block the walkway
  assert.equal(world.isBlocked(4, 6), false);
});

test('after relaxing, workers idle with injected offsets', async () => {
  const seq = [0.0, 0.5];
  const { world } = await newWorld({ random: () => seq.shift() ?? 0 });
  run(world, 20);
  world.setNpcState('worker_a', 'relaxed');
  world.setNpcState('worker_b', 'relaxed');
  assert.equal(world.npc('worker_a').pose, 'bgworker_a_idle_phone_s');
  assert.equal(world.npc('worker_b').pose, 'bgworker_b_idle_coffee_s');
  run(world, 1);
  const cell = world.npc('worker_a').cell;
  run(world, 100);
  assert.deepEqual(world.npc('worker_a').cell, cell); // stopped patrolling
  const draws = world.snapshot().layers.actor.filter((d) => /bgworker/.test(d.atlas));
  assert.equal(draws.length, 2);
  // offsets 0 and 500 ms put the two on different idle frames
  assert.notEqual(draws[0].rect.x, draws[1].rect.x);
});

test('the folded form glitch roams inside the walkable lobby and never crosses a wall', async () => {
  const { world } = await newWorld();
  world.spawnGlitch('glitch_lobby');
  const xs = [];
  for (let i = 0; i < 600; i += 1) {
    run(world, 1);
    const g = world.glitch('glitch_lobby');
    xs.push(g.x);
    assert.equal(world.isBlocked(Math.floor(g.x / 16), 14), false, `x=${g.x}`);
    assert.equal(g.phase, 'roam');
  }
  assert.ok(Math.max(...xs) - Math.min(...xs) >= 8, 'it actually moves');
  const draw = world.snapshot().layers.actor.find((d) => d.atlas === 'glitches');
  assert.equal(draw.rect.y, 128);
  assert.equal(draw.rect.w, 16);
  assert.ok(world.snapshot().layers.shadow.length >= 2);
  assert.equal(world.spawnGlitch('glitch_lobby'), world.spawnGlitch('glitch_lobby'));
});

test('repair plays the snap frame for 160 ms, then the ordinary prop stays', async () => {
  const { world, events } = await newWorld();
  assert.throws(() => world.repairGlitch('glitch_lobby'));
  world.spawnGlitch('glitch_lobby');
  run(world, 30);
  const at = world.glitch('glitch_lobby');
  world.repairGlitch('glitch_lobby');
  assert.equal(events.filter(([t]) => t === 'engine:glitch-repaired').length, 1);
  assert.deepEqual(events.find(([t]) => t === 'engine:glitch-repaired')[1], { interaction: 'glitch_lobby' });
  const frame = () => world.snapshot().layers.actor.find((d) => d.atlas === 'glitches').rect;
  assert.equal(world.glitch('glitch_lobby').phase, 'repaired');
  assert.deepEqual(frame(), { x: 0, y: 160, w: 16, h: 16 }); // form_repaired
  run(world, 9); // 150 ms
  assert.equal(world.glitch('glitch_lobby').phase, 'repaired');
  run(world, 1); // 166 ms
  assert.equal(world.glitch('glitch_lobby').phase, 'ordinary');
  assert.deepEqual(frame(), { x: 0, y: 176, w: 16, h: 16 }); // form_ordinary
  const settled = world.glitch('glitch_lobby');
  assert.equal(settled.x, at.x); // stopped where it snapped
  run(world, 200);
  assert.equal(world.glitch('glitch_lobby').x, at.x);
  assert.equal(world.glitch('glitch_lobby').phase, 'ordinary');
  world.repairGlitch('glitch_lobby'); // idempotent
  assert.equal(events.filter(([t]) => t === 'engine:glitch-repaired').length, 1);
  // the form is a flat sheet: walkable
  assert.equal(world.isBlocked(settled.cell[0], settled.cell[1]), false);
});

test('snapshot has the contract shape and a draw for every layer in use', async () => {
  const { world, data } = await newWorld();
  const snap = world.snapshot();
  assert.equal(snap.floor.length, 28 * 18);
  assert.deepEqual(Object.keys(snap.layers), ['rear_wall', 'floor_marking', 'rear_prop', 'shadow', 'actor', 'front_prop', 'light']);
  for (const k of ['rear_wall', 'rear_prop', 'shadow', 'actor', 'light']) assert.ok(snap.layers[k].length > 0, k);
  assert.deepEqual(snap.markers, []);
  assert.deepEqual(snap.camera, world.camera());
  // 1 avatar + ivo + mira + two workers
  assert.equal(snap.layers.actor.length, 5);
  assert.equal(snap.layers.shadow.length, 5);
  const avatar = snap.layers.actor.find((d) => d.atlas === 'engineer');
  assert.deepEqual([avatar.x, avatar.y, avatar.anchorY], [3 * 16 + 8 - 8, 2 * 16 + 16 - 24, 2 * 16 + 16]);
  const kit = snap.layers.rear_prop.find((d) => d.atlas === 'kit');
  assert.ok(kit.rect.w > 0 && typeof kit.anchorY === 'number');
  // pace signage comes from the pace atlas
  assert.ok(snap.layers.rear_prop.some((d) => d.atlas === 'pace') || snap.layers.floor_marking.some((d) => d.atlas === 'pace'));
  // lamp glows are where_color lights
  assert.ok(snap.layers.light.every((d) => d.composite?.mode === 'where_color'));
  world.setMarkers([{ id: 'o01-popup', cell: [4, 3], shape: 'conversation', state: 'idle' }]);
  assert.equal(world.snapshot().markers[0].shape, 'conversation');
  assert.ok(data);
});

test('placements draw at footprint origin minus origin_px (pot plant check)', async () => {
  const { world, atlases } = await newWorld();
  const e = atlases.kitEntry('pot_plant_a');
  const snap = world.snapshot();
  const want = { x: 14 * 16 - e.footprint.origin_px[0], y: 16 * 16 - e.footprint.origin_px[1] };
  const found = snap.layers.rear_prop.find((d) => d.atlas === 'kit' && d.x === want.x && d.y === want.y && d.rect.x === e.rect[0] && d.rect.y === e.rect[1]);
  assert.ok(found);
  assert.equal(found.anchorY, want.y + e.anchor[1]);
});

test('pulse lamps breathe and reduced motion holds still', async () => {
  const a = (await newWorld()).world;
  const glowRects = (w) => w.snapshot().layers.light.map((d) => d.rect.x).join(',');
  const first = glowRects(a);
  run(a, 40); // 667 ms
  assert.notEqual(glowRects(a), first);
  const b = (await newWorld({ reducedMotion: true })).world;
  const f2 = glowRects(b);
  run(b, 100);
  assert.equal(glowRects(b), f2);
});

test('serialize and restore round-trip placements, gates, npcs, avatar and glitch', async () => {
  const { world: w1 } = await newWorld();
  w1.openGate('g.turnstile');
  w1.setNpcState('ivo', 'post_nod');
  w1.setPlacementState('lamp_printer', 'on');
  w1.avatar.teleport([12, 12], 'e');
  w1.spawnGlitch('glitch_lobby');
  run(w1, 40);
  w1.repairGlitch('glitch_lobby');
  run(w1, 20);
  const slice = JSON.parse(JSON.stringify(w1.serialize()));
  const { world: w2 } = await newWorld();
  w2.restore(slice);
  assert.deepEqual(w2.serialize(), slice);
  assert.equal(w2.isBlocked(23, 12), false);
  assert.deepEqual(w2.npc('ivo').cell, [12, 14]);
  assert.deepEqual(w2.avatar.cell, [12, 12]);
  assert.equal(w2.glitch('glitch_lobby').phase, 'ordinary');
  // unknown ids from an older document are ignored
  w2.restore({ placements: { gone: 'x' }, gates: { 'g.gone': true }, npcs: { gone: { state: 'x' } } });
  assert.deepEqual(w2.serialize(), slice);
});

test('two worlds fed the same script stay identical (determinism)', async () => {
  const mk = async () => {
    const { world } = await newWorld();
    world.spawnGlitch('glitch_lobby');
    world.avatar.setHeld('s');
    run(world, 100);
    world.avatar.setHeld('e');
    run(world, 150);
    return JSON.stringify([world.serialize(), world.snapshot()]);
  };
  assert.equal(await mk(), await mk());
});

test('World can be built from the shared data without a bus', async () => {
  const { data, atlases } = await realData();
  const w = new World(data, atlases);
  w.avatar.requestStep('e');
  run(w, CELL_STEPS);
  assert.deepEqual(w.avatar.cell, [4, 2]);
  assert.ok(STEP_MS > 0);
  assert.deepEqual(cellsOf([[1, 2]]), ['1,2']);
});
