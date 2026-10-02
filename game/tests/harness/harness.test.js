// Self-tests for the shared harness (task 6.1): fake clock + scripted input, fixture loaders,
// level model. Everything runs against the real data files.
import { test } from 'node:test';
import assert from 'node:assert/strict';
import {
  FakeClock, EventBus, STEP_MS, CELL_STEPS, ScriptedInput, keyEvent, outputOf, BusRecorder,
  loadRealData, loadRealAtlasJson, diskFetch, stubLoadImage, DATA_PATHS, ATLAS_PATHS, clone,
  collisionGrid, shortestPath, pathDirs, walkScript, cameraFor, feetOf, level01Legs, MemoryStorage,
} from './index.js';
import { computeCamera } from '../../src/engine/index.js';

test('keyEvent builds KeyboardEvent-like objects the interpreter contract expects', () => {
  assert.deepEqual(
    (({ key, code, altKey, shiftKey }) => ({ key, code, altKey, shiftKey }))(keyEvent('Alt+ArrowRight')),
    { key: 'ArrowRight', code: 'ArrowRight', altKey: true, shiftKey: false });
  const bq = keyEvent('Backquote');
  assert.equal(bq.key, '`');
  assert.equal(bq.code, 'Backquote');
  assert.equal(keyEvent('Space').key, ' ');
  assert.equal(keyEvent('?').shiftKey, true);
  assert.equal(keyEvent('w').code, 'KeyW');
  assert.equal(outputOf('Caps+H'), 'ArrowLeft');
  assert.equal(outputOf('Caps'), 'Escape');
  assert.equal(outputOf('Q'), 'Q');
});

test('ScriptedInput + FakeClock: one cell per step() and a deterministic log', () => {
  const seen = [];
  const make = () => {
    const clock = new FakeClock();
    const target = { handleKeyEvent: (raw, phase) => { seen.push([clock.now(), raw.key, phase]); return null; } };
    return { clock, p: new ScriptedInput({ target, advance: (ms) => clock.advance(ms) }) };
  };
  const a = make();
  a.p.run([{ step: 'ArrowDown', cells: 2 }, 'Caps', { type: 'ab' }, { wait: 3 }]);
  const firstRun = seen.splice(0);
  assert.ok(Math.abs(a.clock.now() - (2 * CELL_STEPS + 1 + 2 + 3) * STEP_MS) < 1e-3);
  // down/up pairs, in order, with timestamps on whole steps
  assert.deepEqual(firstRun.slice(0, 4).map((r) => r.slice(1)), [
    ['ArrowDown', 'down'], ['ArrowDown', 'up'], ['ArrowDown', 'down'], ['ArrowDown', 'up']]);
  assert.ok(Math.abs(firstRun[2][0] - CELL_STEPS * STEP_MS) < 1e-3);
  const b = make();
  b.p.run([{ step: 'ArrowDown', cells: 2 }, 'Caps', { type: 'ab' }, { wait: 3 }]);
  assert.deepEqual(a.p.log, b.p.log);
  assert.deepEqual(firstRun, seen);
});

test('ScriptedInput hold() keeps the key down for whole cells and releaseAll() lets go', () => {
  const clock = new FakeClock();
  const phases = [];
  const p = new ScriptedInput({ target: { handleKeyEvent: (r, ph) => phases.push(`${r.key}:${ph}`) }, advance: (ms) => clock.advance(ms) });
  p.hold('Caps+L', 3);
  assert.ok(Math.abs(clock.now() - 3 * CELL_STEPS * STEP_MS) < 1e-3);
  p.down('ArrowUp').releaseAll();
  assert.deepEqual(phases, ['ArrowRight:down', 'ArrowRight:up', 'ArrowUp:down', 'ArrowUp:up']);
  assert.throws(() => p.run([{ nope: 1 }]), /unknown script item/);
});

test('BusRecorder keeps every emit in order', () => {
  const bus = new EventBus();
  const rec = new BusRecorder(bus);
  bus.emit('a', 1);
  bus.emit('b', 2);
  bus.emit('a', 3);
  assert.deepEqual(rec.topics(), ['a', 'b', 'a']);
  assert.deepEqual(rec.of('a'), [1, 3]);
  assert.equal(rec.last('b'), 2);
  rec.stop();
  bus.emit('a', 4);
  assert.equal(rec.count('a'), 2);
});

test('fixtures load all six data files and nine atlases from disk', () => {
  const d = loadRealData();
  assert.deepEqual(Object.keys(d), Object.keys(DATA_PATHS));
  assert.equal(d.level.id, 'orientation-01');
  assert.equal(d.map.spawns[0].id, 'arrival');
  const a = loadRealAtlasJson();
  assert.deepEqual(Object.keys(a), Object.keys(ATLAS_PATHS));
  assert.ok(Array.isArray(a.kit.entries));
});

test('diskFetch serves files, overrides, 404s and corrupt JSON like a static server', async () => {
  const f = diskFetch({
    overrides: { '/x.json': { hello: 1 } },
    missing: [DATA_PATHS.world],
    corrupt: [DATA_PATHS.district],
  });
  assert.deepEqual(await (await f('/x.json')).json(), { hello: 1 });
  const ok = await f(DATA_PATHS.level);
  assert.equal(ok.status, 200);
  assert.equal((await ok.json()).id, 'orientation-01');
  assert.equal((await f(DATA_PATHS.world)).status, 404);
  await assert.rejects(async () => (await f(DATA_PATHS.district)).json());
  assert.equal((await f('/nope.json')).ok, false);
  assert.deepEqual(f.calls.slice(0, 2), ['/x.json', DATA_PATHS.level]);
  const based = diskFetch({ baseUrl: 'http://127.0.0.1:8000/' });
  assert.equal((await based('http://127.0.0.1:8000/design/levels/world.json')).status, 200);
});

test('stubLoadImage reads real PNG sizes', async () => {
  const img = await stubLoadImage()('/art-direction/kit/orientation-atlas.png');
  assert.ok(img.width > 0 && img.height > 0);
});

test('clone and MemoryStorage behave', () => {
  const o = { a: [1] };
  const c = clone(o);
  c.a.push(2);
  assert.deepEqual(o, { a: [1] });
  const s = new MemoryStorage();
  s.setItem('k', 'v');
  assert.equal(s.getItem('k'), 'v');
  assert.equal(s.getItem('none'), null);
  const t = new MemoryStorage({ throwing: true });
  assert.throws(() => t.setItem('k', 'v'));
  assert.throws(() => t.getItem('k'));
});

test('level model: collision grid, paths and walk scripts agree with the map', () => {
  const { map } = loadRealData();
  const grid = collisionGrid(map);
  assert.equal(grid.length, 18);
  assert.equal(grid[0][0], true);
  const spawn = map.spawns.find((s) => s.id === 'arrival').cell;
  assert.equal(grid[spawn[1]][spawn[0]], false, 'arrival cell is walkable');
  const route = map.routes.main[0];
  const p = shortestPath(grid, route.from, route.to);
  assert.deepEqual(p[0], route.from);
  assert.deepEqual(p.at(-1), route.to);
  // the documented counter-clockwise lap exists as a walkable path of the same length or longer
  assert.ok(p.length <= route.cells.length);
  for (const [x, y] of route.cells) assert.equal(grid[y][x], false, `route cell ${x},${y} walkable`);
  assert.deepEqual(pathDirs([[0, 0], [1, 0], [1, 1]]), ['e', 's']);
  assert.deepEqual(walkScript([[0, 0], [0, 1]]), [{ step: 'ArrowDown' }]);
  assert.equal(shortestPath(grid, [0, 0], [3, 3]), null, 'a blocked start has no path');
  const closed = collisionGrid(map);
  const open = collisionGrid(map, ['g.turnstile']);
  assert.equal(closed[12][23], true);
  assert.equal(open[12][23], false);
});

test('level model: camera model matches the engine pure helper over the whole map', () => {
  const { district } = loadRealData();
  for (let y = 0; y < 18; y += 1) {
    for (let x = 0; x < 28; x += 1) {
      assert.deepEqual(cameraFor([x, y], district.camera_bounds), computeCamera(feetOf([x, y]), district.camera_bounds), `${x},${y}`);
    }
  }
});

test('level 01 legs follow the documented route and use real cells', () => {
  const data = loadRealData();
  const legs = level01Legs(data);
  assert.deepEqual(legs.map((l) => l.id), [
    'arrival', 'loop-down', 'loop-right', 'loop-up', 'loop-left',
    'stop-north', 'stop-west', 'stop-south', 'stop-east', 'recall-to-north', 'recall-back-to-reception']);
  const lap = data.map.routes.main[0].cells.map(String);
  for (const l of legs.filter((x) => x.id.startsWith('loop-'))) {
    for (const c of l.cells) assert.ok(lap.includes(String(c)), `${l.id} ${c} is on the documented lap`);
  }
  assert.equal(legs.find((l) => l.id === 'recall-to-north').inset, false);
  assert.equal(legs.find((l) => l.id === 'loop-down').inset, true);
});
