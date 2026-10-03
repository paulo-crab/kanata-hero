import { test } from 'node:test';
import assert from 'node:assert/strict';
import { Renderer, orderLayer, orderWorld, LAYER_ORDER } from '../../src/engine/index.js';
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

// ---- tall props occlude actors north of them (playtest 1, item 2) ------------------------------------------------

/** Index in draw order of the first draw whose atlas and rect match. */
function drawIndex(ordered, atlas, rect) {
  return ordered.findIndex(({ draw }) => draw.atlas === atlas && draw.rect && rect
    && draw.rect.x === rect[0] && draw.rect.y === rect[1] && draw.rect.w === rect[2] && draw.rect.h === rect[3]);
}

test('a glass partition draws over an actor standing in the row north of it, and under one standing south of it', async () => {
  const { world, atlases } = await newWorld();
  // The real atlas entries: 28 px tall sprites on 16 px cells, y-sorted rear props with the footprint origin at [0,10].
  const one = atlases.kitEntry('partition_1x1');
  const two = atlases.kitEntry('partition_2x1');
  for (const e of [one, two]) {
    assert.equal(e.layer, 'rear_prop');
    assert.equal(e.y_sort, true);
    assert.equal(e.size_px[1], 28);
    assert.deepEqual(e.footprint.origin_px, [0, 10]);
  }
  const rectOf = (e) => [e.rect[0], e.rect[1], e.size_px[0], e.size_px[1]];
  const order = (cell) => {
    world.avatar.teleport(cell, 's');
    const ordered = orderWorld(world.snapshot().layers);
    const avatar = ordered.findIndex(({ name, draw }) => name === 'actor' && draw.atlas === 'engineer');
    return { ordered, avatar };
  };
  // partition_1x1 at (19,12) and partition_2x1 at (20,12): cells (19,11) and (20,11) are open floor to the north.
  for (const [cell, e] of [[[19, 11], one], [[20, 11], two]]) {
    assert.equal(world.isBlocked(cell[0], cell[1]), false, `${cell} is walkable`);
    const { ordered, avatar } = order(cell);
    const prop = drawIndex(ordered, 'kit', rectOf(e));
    assert.ok(prop >= 0 && avatar >= 0);
    assert.ok(avatar < prop, `an actor north of ${e.name} is drawn behind the glass`);
    // its contact shadow goes behind the glass too
    const shadow = ordered.findIndex(({ name, draw }) => name === 'shadow' && draw.anchorY === world.avatar.feetPx.y);
    assert.ok(shadow >= 0 && shadow < prop && shadow < avatar);
  }
  // The 1x1 partition at (25,12) has open floor on both sides: the mail room is to the south.
  const south = [25, 13];
  assert.equal(world.isBlocked(south[0], south[1]), false);
  const { ordered, avatar } = order(south);
  const prop = ordered.findIndex(({ draw }) => draw.atlas === 'kit' && draw.rect.x === one.rect[0] && draw.rect.y === one.rect[1] && draw.x === 25 * 16);
  assert.ok(prop >= 0 && avatar > prop, 'an actor south of the glass is drawn over it');
});

test('orderWorld: static rear props first, then props, shadows and actors by anchor; later layers keep their order', () => {
  const layers = {
    rear_wall: [{ id: 'w', anchorY: 5 }],
    floor_marking: [{ id: 'm', anchorY: 1 }],
    rear_prop: [
      { id: 'static', ySort: false, anchorY: 500 },
      { id: 'tall', ySort: true, anchorY: 208 },
      { id: 'low', ySort: true, anchorY: 100 },
    ],
    shadow: [{ id: 'sh-n', ySort: false, anchorY: 192 }, { id: 'sh-s', ySort: false, anchorY: 224 }],
    actor: [{ id: 'north', ySort: true, anchorY: 192 }, { id: 'south', ySort: true, anchorY: 224 }],
    front_prop: [{ id: 'f2', ySort: true, anchorY: 30 }, { id: 'f1', ySort: true, anchorY: 10 }],
    light: [{ id: 'l' }],
  };
  assert.deepEqual(orderWorld(layers).map(({ draw }) => draw.id),
    ['w', 'm', 'static', 'low', 'sh-n', 'north', 'tall', 'sh-s', 'south', 'f1', 'f2', 'l']);
  // equal anchors: prop, then shadow, then actor
  const tie = orderWorld({ rear_prop: [{ id: 'p', ySort: true, anchorY: 8 }], shadow: [{ id: 's', anchorY: 8 }], actor: [{ id: 'a', ySort: true, anchorY: 8 }] });
  assert.deepEqual(tie.map(({ draw }) => draw.id), ['p', 's', 'a']);
});

test('the renderer draws the partition after the actor north of it (real draw calls)', async () => {
  const { world, atlases } = await newWorld();
  const { r, buffer } = build(atlases);
  world.avatar.teleport([19, 11], 's');
  r.draw(world.snapshot());
  const imgs = buffer.calls.filter(([k]) => k === 'drawImage');
  const part = atlases.kitEntry('partition_1x1');
  const at = (pred) => imgs.findIndex(pred);
  const actor = at((c) => c[1]?.url?.includes('engineer'));
  const glass = at((c) => c[1]?.url?.includes('orientation-atlas') && c[2] === part.rect[0] && c[3] === part.rect[1] && c[4] === part.size_px[0] && c[5] === part.size_px[1]);
  assert.ok(actor >= 0 && glass >= 0 && glass > actor, 'glass is blitted after the engineer');
});
