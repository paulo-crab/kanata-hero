import { test } from 'node:test';
import assert from 'node:assert/strict';
import { AnimationPlayer, frameForSteps } from '../../src/engine/index.js';
import { realData } from './helpers.js';

const play = (def, ms, opts) => {
  const p = new AnimationPlayer(def, opts);
  p.update(ms);
  return p;
};

test('ivo_wave_s loops its three frames at 250 ms', async () => {
  const { atlases } = await realData();
  const def = atlases.animation('ivo_wave_s');
  assert.equal(def.frames, 3);
  assert.equal(def.ms, 250);
  assert.equal(def.mode, 'loop');
  const seen = [0, 249, 250, 499, 500, 750, 1000].map((t) => play(def, t).frameIndex);
  assert.deepEqual(seen, [0, 0, 1, 1, 2, 0, 1]);
});

test('reduced motion holds frame 0 on loops', async () => {
  const { atlases } = await realData();
  const def = atlases.animation('ivo_wave_s');
  assert.equal(play(def, 600, { reducedMotion: true }).frameIndex, 0);
  const flash = atlases.animation('ivo_tablet_flash_s');
  assert.equal(flash.mode, 'loop');
  assert.equal(play(flash, 900, { reducedMotion: true }).frameIndex, 0);
});

test('once animations hold the last frame and report done', async () => {
  const { atlases } = await realData();
  const def = atlases.animation('ivo_nod_s');
  assert.equal(def.mode, 'once');
  const p = new AnimationPlayer(def);
  assert.equal(p.done, false);
  p.update(def.ms * def.frames - 1);
  assert.equal(p.done, false);
  p.update(1);
  assert.equal(p.done, true);
  p.update(5000);
  assert.equal(p.frameIndex, def.frames - 1);
  p.reset();
  assert.equal(p.frameIndex, 0);
  assert.equal(p.done, false);
  // reduced motion does not freeze a once animation
  assert.equal(play(def, 5000, { reducedMotion: true }).frameIndex, def.frames - 1);
});

test('engineer walk: 4 frames, a frame every 8 sim steps, a cell is two frames', async () => {
  const { atlases } = await realData();
  const def = atlases.animation('engineer_walk_e');
  assert.equal(def.frames, 4);
  assert.equal(def.ms, 133);
  assert.equal(def.px_per_frame, 8);
  const frames = [0, 7, 8, 15, 16, 23, 24, 31, 32].map((s) => frameForSteps(def, s));
  assert.deepEqual(frames, [0, 0, 1, 1, 2, 2, 3, 3, 0]);
});

test('engineer idle is 2 x 500 ms and interact is 2 x 250 ms once', async () => {
  const { atlases } = await realData();
  const idle = atlases.animation('engineer_idle_s');
  assert.deepEqual([idle.frames, idle.ms, idle.mode], [2, 500, 'loop']);
  const act = atlases.animation('engineer_interact_s');
  assert.deepEqual([act.frames, act.ms, act.mode], [2, 250, 'once']);
});

test('elevator closed, half, open are three states of 120 ms with the right entries', async () => {
  const { atlases } = await realData();
  const set = atlases.stateSet('elevator');
  assert.deepEqual(set.play, ['closed', 'half', 'open']);
  assert.equal(set.ms_per_frame, 120);
  assert.deepEqual(set.states.closed.entries, ['elevator_closed']);
  assert.deepEqual(set.states.half.entries, ['elevator_half']);
  assert.deepEqual(set.states.open.entries, ['elevator_open']);
  assert.equal(set.states.open.blocked, false);
  // stepping the three states with a player-free timeline
  const states = [0, 119, 120, 239, 240].map((t) => set.play[Math.min(Math.floor(t / set.ms_per_frame), 2)]);
  assert.deepEqual(states, ['closed', 'closed', 'half', 'half', 'open']);
});

test('glitch animations normalise to rects on the 128x192 sheet', async () => {
  const { atlases } = await realData();
  const roam = atlases.animation('form_roam');
  assert.deepEqual([roam.x, roam.y, roam.frames, roam.ms, roam.mode], [0, 128, 4, 120, 'loop']);
  const snap = atlases.animation('form_repaired');
  assert.deepEqual([snap.frames, snap.ms, snap.mode], [1, 160, 'once']);
  assert.equal(atlases.animation('form_ordinary').mode, 'hold');
  assert.equal(atlases.glitch('form').animations.ordinary, 'form_ordinary');
});

test('person atlas, portrait and unknown lookups', async () => {
  const { atlases } = await realData();
  assert.deepEqual(atlases.personAtlas('ivo').frame, { w: 16, h: 24 });
  assert.deepEqual(atlases.portrait('ivo_neutral'), { x: atlases.portrait('ivo_neutral').x, y: atlases.portrait('ivo_neutral').y, w: 48, h: 48 });
  assert.throws(() => atlases.portrait('ivo_nope'), (e) => e.kind === 'shape');
  assert.throws(() => atlases.animation('nope_walk_e'), (e) => e.kind === 'shape');
  assert.throws(() => atlases.kitEntry('nope'), (e) => e.kind === 'shape');
  assert.throws(() => atlases.personAtlas('nobody'), (e) => e.kind === 'shape');
  assert.ok(atlases.animation('bgworker_a_idle_phone_s'));
  assert.ok(atlases.landmark('garden').states.after);
});
