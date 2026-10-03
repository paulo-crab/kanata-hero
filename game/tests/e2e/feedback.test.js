// Playtest 1, item 5: the "Output observed" card appears in scenes that teach and clears when the scene exits;
// the open world gets a short toast on the first three uses; Settings can keep the card always or turn it off.
import { test } from 'node:test';
import assert from 'node:assert/strict';
import { ScriptedInput, MemoryStorage, BusRecorder, diskFetch, stubLoadImage } from '../harness/index.js';
import { createGame } from '../../src/main.js';
import { FakeClock, EventBus } from '../../src/shared/index.js';
import { FeedbackPolicy, WORLD_TOAST_MS, WORLD_TOAST_USES } from '../../src/runtime/feedback.js';

async function start({ storage = new MemoryStorage() } = {}) {
  const bus = new EventBus();
  const rec = new BusRecorder(bus);
  const clock = new FakeClock();
  const game = await createGame({ bus, fetchFn: diskFetch(), baseUrl: '/', loadImage: stubLoadImage(), clock, storage, headless: true });
  const player = new ScriptedInput({ target: game.interpreter, advance: (ms) => { clock.advance(ms); game.loop.advance(ms); } });
  return { game, clock, rec, player };
}

const card = (observed = 'Left Arrow observed') => ({ gesture: null, observed, effect: 'Step west', confidence: 'observed', confidenceLabel: 'Output observed' });

function policy(settings = {}) {
  const bus = new EventBus();
  const clock = new FakeClock();
  const doc = { settings: { feedback: 'scenes', ...settings }, counters: { feedbackToasts: 0 } };
  const progress = { doc, update: (fn) => fn(doc) };
  const sent = [];
  bus.on('vm:toast', (t) => sent.push(['toast', t]));
  bus.on('vm:feedback', (c) => sent.push(['card', c]));
  return { fb: new FeedbackPolicy({ bus, clock, progress }), bus, clock, doc, sent };
}

test('the hub shows no persistent card: the popup scene card is cleared when the scene exits', async () => {
  const t = await start();
  t.player.tap('Escape');
  t.player.tap('Enter');                          // skip setup (confirm card)
  t.player.wait(90);
  t.player.tap('Enter');                          // Ivo's welcome
  t.player.wait(2);
  assert.equal(t.game.machine.top.kind, 'form', 'the popup scene is open');
  t.player.tap('ArrowLeft');                      // a wrong key: the card teaches
  const during = t.rec.of('vm:feedback').at(-1);
  assert.match(during.observed, /Left Arrow observed/);
  t.player.tap('Escape');                         // the right key: the popup closes
  t.player.wait(2);
  assert.equal(t.rec.of('vm:feedback').at(-1), null, 'vm:feedback is cleared on scene exit');
  t.player.tap('Enter');
  t.player.wait(2);
  assert.equal(t.game.machine.top.kind, 'hub');
  assert.equal(t.rec.of('vm:feedback').at(-1), null, 'the hub has no card');
  // walking in the hub never brings it back
  t.player.step('ArrowDown');
  t.player.step('ArrowDown');
  assert.equal(t.rec.of('vm:feedback').at(-1), null);
});

test('world feedback is a toast of at most 2.5 s, one per walking burst, for the first three uses only', () => {
  const { fb, clock, sent } = policy();
  const toasts = () => sent.filter(([k]) => k === 'toast').length;
  for (let use = 1; use <= 5; use += 1) {
    fb.world(card(), 'Left Arrow observed: step west');
    clock.advance(500);
    fb.world(card(), 'Left Arrow observed: step west');   // same burst: replaces the toast
    clock.advance(WORLD_TOAST_MS + 100);                   // the toast is gone, the next walk is a new use
  }
  assert.equal(sent.filter(([k]) => k === 'card').length, 0, 'never a card in the default mode');
  assert.equal(toasts(), WORLD_TOAST_USES * 2, 'two updates in each of the first three bursts, then nothing');
  assert.ok(sent.every(([, t]) => t.ms <= 2500 && t.key === 'feedback' && t.tone === 'feedback'));
});

test('scene cards clear on scene exit; "always" keeps the card in the world; "off" shows nothing', () => {
  let p = policy();
  p.fb.scene(card());
  p.bus.emit('scene:exit', { id: 'o01-popup' });
  assert.deepEqual(p.sent.map(([, c]) => (c ? 'card' : 'null')), ['card', 'null']);

  p = policy({ feedback: 'always' });
  p.fb.world(card(), 'x');
  p.fb.world(card(), 'x');
  assert.equal(p.sent.filter(([k, c]) => k === 'card' && c).length, 2, 'the card in the world, as before');
  assert.equal(p.sent.filter(([k]) => k === 'toast').length, 0);

  p = policy({ feedback: 'off' });
  p.fb.scene(card());
  p.fb.world(card(), 'x');
  assert.deepEqual(p.sent, []);
});

test('the toast count is saved with the progress, so a reload does not reset the three uses', () => {
  const a = policy();
  a.fb.world(card(), 'x');
  assert.equal(a.doc.counters.feedbackToasts, 1);
  const b = policy();
  b.doc.counters.feedbackToasts = WORLD_TOAST_USES;
  b.fb.world(card(), 'x');
  assert.deepEqual(b.sent, [], 'already used three times: hidden');
});

test('Settings: Show output feedback cycles in scenes only, always, off and is part of the settings view-model', async () => {
  const t = await start();
  t.player.tap('Escape');
  t.player.tap('Enter');
  t.player.wait(90);
  t.player.tap('Enter');
  t.player.tap('Escape');
  t.player.wait(2);
  t.player.tap('Enter');
  t.player.tap('q');
  t.game.bus.emit('ui:command', { type: 'chooseRow', id: 'settings' });
  assert.equal(t.game.machine.top.kind, 'settings');
  assert.equal(t.rec.of('vm:settings').at(-1).feedback, 'scenes');
  t.game.bus.emit('ui:command', { type: 'setSetting', key: 'feedback', value: 'always' });
  assert.equal(t.game.progress.doc.settings.feedback, 'always');
  t.game.bus.emit('ui:command', { type: 'setSetting', key: 'feedback', value: 'off' });
  assert.equal(t.game.progress.doc.settings.feedback, 'off');
  assert.equal(t.rec.of('vm:settings').at(-1).feedback, 'off');
});
