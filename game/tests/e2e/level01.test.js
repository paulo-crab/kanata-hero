// Task 6.2: headless level 01 scenario. Skips with a reason until engine, input, runtime and a
// `createGame` boot export exist (see harness/game-factory.js); then it runs unchanged.
import { test } from 'node:test';
import assert from 'node:assert/strict';
import { buildHeadlessGame, MemoryStorage } from '../harness/index.js';
import { playLevel01, SCRIPT_DATA } from './level01-script.js';


async function run(opts, storage) {
  const built = await buildHeadlessGame(storage ? { storage } : {});
  const out = playLevel01(built.game, opts);
  return { ...built, ...out };
}

test('level 01 plays through setup skip, arrival, popup, lap, desks, label and recall', async () => {
  const { checkpoints: c } = await run({});
  assert.equal(c.afterSetup.setupDone, true, 'Escape in setup skips the whole setup');
  assert.deepEqual(c.elevatorStates, ['closed', 'half', 'open'], 'elevator plays closed -> half -> open');
  assert.ok(c.elevatorStateMs[1] >= 100 && c.elevatorStateMs[1] <= 150, `the half state lasts about 120 ms, got ${c.elevatorStateMs[1]}`);
  assert.equal(c.elevatorFinal, 'open');
  assert.equal(c.welcome, 'o01.d.welcome');
  assert.equal(c.popupOpen, 'o01-popup');
  assert.match(c.popupWrongFeedback, /Left Arrow observed/);
  assert.equal(c.popupStillOpen, true, 'a wrong output never closes the popup');
  assert.equal(c.popupSuccess, true);
  assert.equal(c.journalOpened, true);
  assert.equal(c.layoutHelpOpened, true);
  assert.ok(c.stepsAfterKeys.includes('o01.s.keys'));
  assert.equal(c.insetDuringLap, true, 'the keyboard inset shows on guided scenes');
  assert.equal(c.layoutHelpRoundTrip, true, 'Layout help mid-lap leaves cell and facing unchanged');
  assert.equal(c.lapSuccess, true);
  assert.deepEqual(c.lapProgress, [1, 2, 3, 4]);
  assert.equal(c.labelOpen, true);
  assert.match(c.labelWrongFeedback, /Option \+ Right observed|Alt\+ArrowRight/);
  assert.equal(c.labelSuccess, true);
  assert.equal(c.stopsSuccess, true);
  assert.deepEqual(c.ivoAtNorth, [10, 4]);
  assert.equal(c.stopsStepDone, true);
  assert.equal(c.recallInset, null, 'no inset on the recall scene');
  assert.equal(c.recallFloorMarkers, 0, 'no floor markers on the recall scene');
  assert.equal(c.reminder, 'o01.d.reminder');
  assert.deepEqual(c.ivoBackAtPost, [12, 14]);
  assert.equal(c.recallSuccess, true);
});

test('level 01 changes the world: turnstile, Ivo, gate, markers, journal, glitch', async () => {
  const { checkpoints: c } = await run({});
  assert.equal(c.world.turnstile, 'open');
  assert.equal(c.world.gateOpen, true);
  assert.equal(c.world.ivoPose, 'ivo_nod_s');
  assert.deepEqual(c.world.ivoCell, [12, 14]);
  assert.equal(c.world.markersGold, true, 'garden markers teal -> gold');
  assert.equal(c.world.glitchVisible, true, 'the folded form appears after the route');
  assert.ok(c.progress.levelsDone.includes('orientation-01'));
  for (const f of ['welcome-popup-closed', 'turnstile-open', 'ivo-nodding']) assert.ok(c.progress.flags.includes(f), f);
  assert.ok(c.progress.journal.includes('Orientation 01 complete: the first route is open.'));
  assert.ok(c.progress.journal.includes('Desk Walker: Right, Up, Left and Down used on the garden loop.'));
});

test('stars: 3 clean without a recall hint, 2 with the forfeited recall hint, 1 after sloppy walking', async () => {
  const clean = await run({ wrongTries: false });
  assert.equal(clean.checkpoints.levelComplete.stars, 3);
  const hinted = await run({ recallHint: true, wrongTries: false });
  assert.ok(hinted.checkpoints.hintCard.text.includes('forfeits the third star'));
  assert.equal(hinted.checkpoints.levelComplete.stars, 2);
  const sloppy = await run({ wrongDetours: 6, wrongTries: false });
  assert.equal(sloppy.checkpoints.levelComplete.stars, 1);
});

test('the scenario is deterministic: two runs give identical input logs, bus events and checkpoints', async () => {
  const a = await run({});
  const b = await run({});
  assert.deepEqual(a.log, b.log);
  assert.deepEqual(a.events, b.events);
  assert.deepEqual(a.checkpoints, b.checkpoints);
});

test('reload mid-lap restores step, avatar and world state from local progress', async () => {
  const storage = new MemoryStorage();
  const first = await run({ stopAfter: 'lap-leg-1' }, storage);
  const cellBefore = [...first.game.world.avatar.cell];
  const second = await buildHeadlessGame({ storage });
  assert.equal(second.game.rules.currentStep.id, 'o01.s.loop');
  assert.deepEqual([...second.game.world.avatar.cell], cellBefore);
  assert.equal(second.game.world.npc('ivo').pose, 'ivo_wave_s');
});

test('blocked storage falls back to memory and the scenario still plays', async () => {
  const { checkpoints: c } = await run({}, new MemoryStorage({ throwing: true }));
  assert.equal(c.levelComplete.level, 'orientation-01');
});

test('script legs exist for every step of level 01 (data sanity, runs without the game)', () => {
  const ids = SCRIPT_DATA.level.steps.map((s) => s.id);
  assert.deepEqual(ids.slice(0, 6), ['o01.s.arrive', 'o01.s.popup', 'o01.s.keys', 'o01.s.loop', 'o01.s.stops', 'o01.s.recall']);
});
