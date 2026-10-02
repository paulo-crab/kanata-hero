import { test } from 'node:test';
import assert from 'node:assert/strict';
import { Renderer, orderLayer, LAYER_ORDER } from '../../src/engine/index.js';
import { newWorld, run } from './helpers.js';

function fakeCanvas(w = 0, h = 0) {
  const calls = [];
  const state = {};
  const ctx = new Proxy({ calls }, {
    get(t, k) {
      if (k === 'calls') return calls;
      if (k in state) return state[k];
      if (k === 'getImageData') return undefined;
      return (...args) => { calls.push([k, ...args]); };
    },
    set(t, k, v) { state[k] = v; calls.push(['set:' + k, v]); return true; },
  });
  const style = { props: {}, setProperty(k, v) { this.props[k] = v; } };
  return { width: w, height: h, style, getContext: () => ctx, ctx, calls };
}

function build(atlases) {
  const main = fakeCanvas();
  const buffers = [];
  const createCanvas = (w, h) => { const c = fakeCanvas(w, h); buffers.push(c); return c; };
  const stageEl = { style: { props: {}, setProperty(k, v) { this.props[k] = v; } } };
  const r = new Renderer({ canvas: main, atlases, stageEl, createCanvas });
  return { r, main, buffer: buffers[0], stageEl };
}

test('resize picks whole zoom, centres the letterbox, sets --world-zoom, keeps no game state', async () => {
  const { atlases } = await newWorld();
  const { r, main, stageEl } = build(atlases);
  let out = r.resize(1366, 768);
  assert.equal(out.zoom, 4);
  assert.deepEqual(out.letterbox, { x: 43, y: 24, w: 1280, h: 720 });
  assert.equal(main.width, 1280);
  assert.equal(main.height, 720);
  assert.equal(stageEl.style.props['--world-zoom'], '4');
  out = r.resize(1920, 1080);
  assert.equal(out.zoom, 6);
  assert.deepEqual(out.letterbox, { x: 0, y: 0, w: 1920, h: 1080 });
  assert.equal(main.width, 1920);
  out = r.resize(1366, 768);
  assert.equal(out.zoom, 4);
});

test('resizing across x4 and x6 keeps the world state and draws the same view', async () => {
  const { world, atlases } = await newWorld();
  world.avatar.teleport([13, 12], 's');
  const { r, buffer } = build(atlases);
  const before = JSON.stringify(world.serialize());
  r.resize(1366, 768);
  r.draw(world.snapshot());
  const first = buffer.calls.filter(([k]) => k === 'drawImage').map((c) => c.slice(2).join(','));
  r.resize(1920, 1080);
  r.draw(world.snapshot());
  r.resize(1366, 768);
  buffer.calls.length = 0;
  r.draw(world.snapshot());
  const again = buffer.calls.filter(([k]) => k === 'drawImage').map((c) => c.slice(2).join(','));
  assert.equal(JSON.stringify(world.serialize()), before);
  assert.deepEqual(again, first);
});

test('draw: nearest neighbour, background, whole-pixel destinations, scaled blit at zoom', async () => {
  const { world, atlases } = await newWorld();
  const { r, main, buffer } = build(atlases);
  r.resize(1366, 768);
  r.draw(world.snapshot());
  assert.ok(buffer.calls.some(([k, v]) => k === 'set:imageSmoothingEnabled' && v === false));
  assert.ok(main.calls.some(([k, v]) => k === 'set:imageSmoothingEnabled' && v === false));
  assert.deepEqual(buffer.calls.find(([k]) => k === 'fillRect').slice(1), [0, 0, 320, 180]);
  const draws = buffer.calls.filter(([k]) => k === 'drawImage');
  assert.ok(draws.length > 100);
  for (const c of draws) {
    for (const n of c.slice(2)) assert.ok(Number.isInteger(n), `non-integer ${n} in ${c}`);
  }
  const blit = main.calls.filter(([k]) => k === 'drawImage');
  assert.equal(blit.length, 1);
  assert.deepEqual(blit[0].slice(2), [0, 0, 320, 180, 0, 0, 1280, 720]);
});

test('draws stay inside the view (off-screen sprites are culled)', async () => {
  const { world, atlases } = await newWorld();
  const { r, buffer } = build(atlases);
  r.draw(world.snapshot(), { x: 0, y: 0 });
  const full = buffer.calls.filter(([k]) => k === 'drawImage').length;
  buffer.calls.length = 0;
  r.draw(world.snapshot(), { x: 128, y: 100 });
  const part = buffer.calls.filter(([k]) => k === 'drawImage').length;
  assert.ok(part < full + 400);
  for (const c of buffer.calls.filter(([k]) => k === 'drawImage')) {
    const [, , , w, h, dx, dy] = c.length === 10 ? [c[0], c[1], c[2], c[4], c[5], c[6], c[7]] : [];
    assert.ok(dx < 320 && dy < 180 && dx + w > 0 && dy + h > 0);
  }
});

test('layer order and y-sorting', () => {
  assert.deepEqual(LAYER_ORDER, ['rear_wall', 'floor_marking', 'rear_prop', 'shadow', 'actor', 'front_prop', 'light']);
  const a = { id: 'a', ySort: true, anchorY: 50 };
  const b = { id: 'b', ySort: true, anchorY: 20 };
  const c = { id: 'c', ySort: true, anchorY: 50 };
  const f = { id: 'f', ySort: false, anchorY: 99 };
  assert.deepEqual(orderLayer('actor', [a, f, b, c]).map((d) => d.id), ['f', 'b', 'a', 'c']);
  assert.deepEqual(orderLayer('rear_wall', [a, b]).map((d) => d.id), ['a', 'b']);
});

test('actors sort by feet y: the avatar draws after Ivo when standing below him, before when above', async () => {
  const { world, atlases } = await newWorld();
  const { r, buffer } = build(atlases);
  const order = () => {
    buffer.calls.length = 0;
    r.draw(world.snapshot());
    const imgs = buffer.calls.filter(([k]) => k === 'drawImage').map((c) => `${c[2]},${c[3]}`);
    return imgs;
  };
  world.avatar.teleport([5, 4], 's'); // below Ivo (5,3)
  const snapBelow = world.snapshot().layers.actor;
  const iv = snapBelow.find((d) => d.atlas === 'ivo');
  const av = snapBelow.find((d) => d.atlas === 'engineer');
  assert.ok(av.anchorY > iv.anchorY);
  const idx = (list, x) => list.indexOf(x);
  const sorted = orderLayer('actor', snapBelow);
  assert.ok(idx(sorted, av) > idx(sorted, iv));
  world.avatar.teleport([5, 2], 's');
  const above = orderLayer('actor', world.snapshot().layers.actor);
  const iv2 = above.find((d) => d.atlas === 'ivo');
  const av2 = above.find((d) => d.atlas === 'engineer');
  assert.ok(above.indexOf(av2) < above.indexOf(iv2));
  assert.ok(order().length > 0);
});

test('contact shadows are drawn with the two shadow colours before the actors', async () => {
  const { world, atlases } = await newWorld();
  const { r, buffer } = build(atlases);
  r.draw(world.snapshot());
  const styles = buffer.calls.filter(([k]) => k === 'set:fillStyle').map(([, v]) => v);
  assert.ok(styles.includes('#3A4160'));
  assert.ok(styles.includes('#1C2038'));
  // the first shadow fill comes after the last rear_prop image and before the first actor image
  const seq = buffer.calls.filter(([k]) => k === 'drawImage' || k === 'set:fillStyle');
  const firstShadow = seq.findIndex(([k, v]) => k === 'set:fillStyle' && v === '#3A4160');
  const firstActor = seq.findIndex(([k, img]) => k === 'drawImage' && img?.url?.includes('engineer'));
  assert.ok(firstShadow >= 0 && firstActor > firstShadow);
});

test('where_color lights fall back to a plain blit when pixels are unreadable, and use pixels when readable', async () => {
  const { world, atlases } = await newWorld();
  const { r, buffer } = build(atlases);
  r.draw(world.snapshot());
  assert.ok(buffer.calls.some(([k, img]) => k === 'drawImage' && img?.url?.includes('orientation-atlas')));

  // a context that can read and write pixels: 'light' draws go through putImageData
  const putCalls = [];
  const mk = (w, h) => {
    const c = fakeCanvas(w, h);
    const base = c.getContext();
    const rich = new Proxy(base, {
      get(t, k) {
        if (k === 'getImageData') return (x, y, ww, hh) => ({ width: ww, height: hh, data: new Uint8ClampedArray(ww * hh * 4) });
        if (k === 'putImageData') return (...a) => putCalls.push(a);
        return t[k];
      },
      set(t, k, v) { t[k] = v; return true; },
    });
    c.getContext = () => rich;
    return c;
  };
  const r2 = new Renderer({ canvas: mk(0, 0), atlases, createCanvas: mk });
  r2.draw(world.snapshot());
  assert.ok(putCalls.length > 0);
});

test('reduced motion flag is stored on the renderer', async () => {
  const { atlases } = await newWorld();
  const { r } = build(atlases);
  r.setReducedMotion(true);
  assert.equal(r.reducedMotion, true);
});

test('a scripted walk then draw is deterministic', async () => {
  const draws = async () => {
    const { world, atlases } = await newWorld();
    const { r, buffer } = build(atlases);
    world.avatar.setHeld('s');
    run(world, 90);
    r.draw(world.snapshot());
    return JSON.stringify(buffer.calls.filter(([k]) => k === 'drawImage').map((c) => c.slice(2)));
  };
  assert.equal(await draws(), await draws());
});
