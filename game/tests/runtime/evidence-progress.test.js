// Evidence and stars (4.5), progress store (4.6), setup flow, journal and settings scenes.
import { test } from 'node:test';
import assert from 'node:assert/strict';
import {
  EvidenceLog, isClean, computeStars, ProgressStore, PROGRESS_KEY,
} from '../../src/runtime/index.js';
import { EventBus } from '../../src/shared/index.js';
import { loadData, makeGame, memoryStorage } from './helpers.js';

const { level, world } = loadData();

function log(over = {}) {
  const e = new EvidenceLog({ level });
  for (const id of ['o01-popup', 'o01-loop', 'o01-four-stops', 'o01-desk-label', 'o01-unprompted']) {
    for (let i = 0; i < 20; i += 1) e.record(id, { output: 'ArrowDown', correct: true, critical: false });
    e.finish(id, true);
  }
  over.fn?.(e);
  return e;
}

test('isClean: critical outputs correct and at least 95 percent of actions', () => {
  assert.ok(isClean({ criticalOk: true, actions: { total: 20, correct: 19 } }));
  assert.ok(!isClean({ criticalOk: true, actions: { total: 20, correct: 18 } }));
  assert.ok(!isClean({ criticalOk: false, actions: { total: 20, correct: 20 } }));
});

test('stars: 1 complete, 2 all clean, 3 clean recall without a hint', () => {
  assert.equal(computeStars('orientation-01', {}, level).stars, 0);
  const three = computeStars('orientation-01', log().all(), level);
  assert.equal(three.stars, 3);
  const unclean = log({ fn: (e) => { for (let i = 0; i < 3; i += 1) e.record('o01-loop', { output: 'ArrowUp', correct: false, critical: false }); } });
  assert.equal(computeStars('orientation-01', unclean.all(), level).stars, 1);
  const hinted = log({ fn: (e) => e.hint({ sceneId: 'o01-unprompted', phase: 'recall', forfeitsStar: true }) });
  assert.equal(computeStars('orientation-01', hinted.all(), level).stars, 2);
  const guidedHint = log({ fn: (e) => e.hint({ sceneId: 'o01-loop', phase: 'guided', forfeitsStar: false }) });
  assert.equal(computeStars('orientation-01', guidedHint.all(), level).stars, 3);
  const incomplete = new EvidenceLog({ level });
  incomplete.record('o01-popup', { output: 'Escape', correct: true, critical: true });
  assert.equal(computeStars('orientation-01', incomplete.all(), level).stars, 0);
});

test('evidence takes phase and gesture ids from level.gestures and round-trips as JSON, with no durations', () => {
  const e = log();
  const s = e.scene('o01-unprompted');
  assert.equal(s.phase, 'recall');
  assert.deepEqual(s.gestureIds, ['B06', 'N01', 'N02', 'N03', 'N04']);
  assert.deepEqual(Object.keys(s).sort(), ['actions', 'confidence', 'criticalOk', 'gestureIds', 'hintForfeit', 'hintUsed', 'observed', 'phase', 'result', 'sceneId']);
  const again = EvidenceLog.fromJSON(JSON.parse(JSON.stringify(e.toJSON())));
  assert.deepEqual(again.all(), e.all());
});

function store(storage) {
  const bus = new EventBus();
  const toasts = [];
  bus.on('vm:toast', (t) => toasts.push(t));
  return { s: new ProgressStore({ storage, world, bus }), toasts };
}

test('progress: fresh document, ids from world.json, flags follow settings and setup', () => {
  const { s } = store(memoryStorage());
  const d = s.load();
  assert.equal(d.schema, 1);
  assert.equal(d.worldVersion, world.version);
  s.update((x) => { x.settings.keyboard = 'microsoft'; x.setup.done = true; x.flags.push('turnstile-open'); });
  assert.ok(s.doc.flags.includes('keyboard-microsoft'));
  assert.ok(!s.doc.flags.includes('keyboard-macbook'));
  assert.ok(s.doc.flags.includes('setup-done'));
  assert.ok(s.persistent);
});

test('progress: save then load round-trips; unknown ids are dropped; corrupt and old schema give a fresh game and a toast', () => {
  const storage = memoryStorage();
  const a = store(storage).s;
  a.load();
  a.update((d) => { d.flags.push('turnstile-open', 'not-a-flag'); d.levelsDone.push('orientation-01', 'nope-99'); d.setup.done = true; });
  const b = store(storage);
  const d = b.s.load();
  assert.ok(d.flags.includes('turnstile-open'));
  assert.ok(!d.flags.includes('not-a-flag'));
  assert.deepEqual(d.levelsDone, ['orientation-01']);
  assert.ok(b.s.hasProgress());
  storage.setItem(PROGRESS_KEY, '{nope');
  const c = store(storage);
  assert.equal(c.s.load().setup.done, false);
  assert.equal(c.toasts.length, 1);
  storage.setItem(PROGRESS_KEY, JSON.stringify({ schema: 2 }));
  const e = store(storage);
  assert.equal(e.s.load().levelsDone.length, 0);
  assert.equal(e.toasts.length, 1);
});

test('progress: throwing storage falls back to memory, warns once, and the game keeps working', () => {
  const boom = { getItem() { throw new Error('denied'); }, setItem() { throw new Error('full'); }, removeItem() { throw new Error('x'); } };
  const { s, toasts } = store(boom);
  assert.equal(s.load().schema, 1);
  assert.equal(s.persistent, false);
  s.update((d) => { d.flags.push('turnstile-open'); });
  s.update((d) => { d.journal.push('x'); });
  assert.ok(s.doc.flags.includes('turnstile-open'));
  assert.equal(toasts.length, 1);
  assert.match(toasts[0].text, /will not be saved/);
  assert.equal(s.hasProgress(), false);
  const none = store(undefined);
  assert.equal(none.s.load().schema, 1);
});

test('progress: reset clears storage and the document', () => {
  const storage = memoryStorage();
  const { s } = store(storage);
  s.load();
  s.update((d) => { d.setup.done = true; });
  assert.ok(s.hasProgress());
  s.reset();
  assert.equal(storage.getItem(PROGRESS_KEY), null);
  assert.equal(s.doc.setup.done, false);
  assert.equal(s.hasProgress(), false);
});

// ---- setup flow, journal, settings -------------------------------------------------------------

test('first visit: setup, then calibration, then arrival; returning player goes to the hub', () => {
  const storage = memoryStorage();
  const g = makeGame({ storage });
  g.session.start();
  assert.equal(g.session.machine.top.kind, 'setup');
  assert.equal(g.vms['vm:setup'].keyboard, 'macbook');
  g.player.tap('ArrowRight');
  assert.equal(g.vms['vm:setup'].keyboard, 'microsoft');
  g.player.tap('Enter');
  assert.equal(g.session.machine.top.kind, 'calibration');
  const steps = g.vms['vm:calibration'].steps;
  assert.equal(steps.length, 5);
  assert.ok(steps[0].current);
  assert.equal(steps[0].statusLabel, 'Not started');
  g.player.tap('ArrowLeft'); // observed Caps + H output
  assert.equal(g.vms['vm:calibration'].steps[0].statusLabel, 'Observed output');
  g.player.tap('ArrowDown'); // skip the Return step
  assert.equal(g.vms['vm:calibration'].steps[1].statusLabel, 'Skipped');
  g.player.tap('Escape'); // skip the rest
  assert.equal(g.session.machine.top.kind, 'arrival');
  const doc = g.session.progress.doc;
  assert.equal(doc.setup.done, true);
  assert.equal(doc.settings.keyboard, 'microsoft');
  assert.deepEqual(Object.values(doc.setup.calibration.steps), ['observed', 'skipped', 'skipped', 'skipped', 'skipped']);
  assert.ok(doc.flags.includes('calibration-done'));

  const again = makeGame({ storage });
  again.session.start();
  assert.equal(again.session.machine.top.kind, 'arrival'); // setup done, level not started
});

test('journal: Q opens and closes it, rows and Also-from-here list, Layout help round trip, settings toggles', () => {
  const g = makeGame();
  g.session.start();
  g.player.tap('Escape');
  g.player.tick(30);
  g.player.tap('Enter');
  g.player.tap('Escape');
  g.player.tap('Enter');
  g.player.tap('q');
  const j = g.vms['vm:journal'];
  assert.equal(j.groups[0].rows[0].id, 'orientation-01');
  assert.deepEqual(j.also.map((a) => a.id), ['layout-help', 'settings', 'controls', 'ride-hub']);
  assert.ok(j.detail.steps.some((s) => s.state === 'current'));
  g.player.tap('q');
  assert.equal(g.session.machine.top.kind, 'hub');
  g.player.tap('q');
  for (let i = 0; i < 2; i += 1) g.player.tap('ArrowDown'); // to Layout help row
  g.player.tap('Enter');
  assert.equal(g.session.machine.top.kind, 'layout-help');
  g.player.tap('Escape');
  assert.equal(g.session.machine.top.kind, 'journal');
  g.player.tap('ArrowDown'); // Settings
  g.player.tap('Enter');
  assert.equal(g.session.machine.top.kind, 'settings');
  g.player.tap('Enter'); // keyboard
  assert.equal(g.vms['vm:settings'].keyboard, 'microsoft');
  g.player.tap('ArrowDown');
  g.player.tap('ArrowDown');
  g.player.tap('Enter'); // larger text
  assert.equal(g.vms['vm:settings'].largerText, true);
  g.player.tap('Escape');
  g.player.tap('Escape');
  assert.equal(g.session.machine.top.kind, 'hub');
});

test('Controls scene lists the six keys; Escape in the open world does nothing', () => {
  const g = makeGame();
  g.session.start();
  g.player.tap('Escape');
  g.player.tick(30);
  g.player.tap('Enter');
  g.player.tap('Escape');
  g.player.tap('Enter');
  g.player.tap('Escape');
  assert.equal(g.session.machine.top.kind, 'hub');
  g.player.tap('q');
  g.session.machine.top.activate({ group: 'also', id: 'controls' });
  assert.equal(g.session.machine.top.kind, 'controls');
  assert.equal(g.vms['vm:controls'].rows.length, 6);
  g.player.tap('Escape');
  assert.equal(g.session.machine.top.kind, 'journal');
});

test('a load error enters the error scene with the file, kind and message', () => {
  const g = makeGame();
  g.session.start();
  g.session.machine.replace('arrival');
  g.session.machine.replace('error', { error: { file: '/x.json', kind: 'missing', message: 'Cannot load /x.json: HTTP 404' } });
  assert.deepEqual(g.vms['vm:error'], { file: '/x.json', kind: 'missing', message: 'Cannot load /x.json: HTTP 404' });
});
