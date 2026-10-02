// Integration gaps from the workstreams, tested on the real stack (createGame, real data, fake clock):
// mouse commands, the confirm-reset card, vm:inset, the calibration view-model, overlay stacking and Return in calibration.
import { test } from 'node:test';
import assert from 'node:assert/strict';
import { ScriptedInput, MemoryStorage, BusRecorder, diskFetch, stubLoadImage, ATLAS_PATHS, readJson } from '../harness/index.js';
import { createGame } from '../../src/main.js';
import { FakeClock, EventBus } from '../../src/shared/index.js';

async function start({ storage = new MemoryStorage() } = {}) {
  const bus = new EventBus();
  const rec = new BusRecorder(bus);            // recording from before the first scene, so the first view-models are seen
  const clock = new FakeClock();
  const game = await createGame({ bus, fetchFn: diskFetch(), baseUrl: '/', loadImage: stubLoadImage(), clock, storage, headless: true });
  const player = new ScriptedInput({ target: game.interpreter, advance: (ms) => { clock.advance(ms); game.loop.advance(ms); } });
  const last = (topic) => rec.of(topic).at(-1);
  const command = (c) => { game.bus.emit('ui:command', c); };
  return { game, clock, storage, rec, player, last, command };
}

/** Skip setup and arrival, close the welcome and the popup: the hub on the keys step. */
function intoHub(t) {
  t.player.tap('Escape');
  t.player.wait(90);
  t.player.tap('Enter');
  t.player.tap('Escape');
  t.player.wait(2);
  t.player.tap('Enter');
  return t;
}

test('createGame is headless-safe: no window, document or canvas is touched and every first view-model is emitted', async () => {
  assert.equal(typeof globalThis.window, 'undefined');
  const t = await start();
  for (const topic of ['vm:setup', 'vm:calibration']) assert.ok(t.last(topic), topic);
  assert.equal(t.game.machine.top.id, 'setup');
  assert.ok(t.game.loop, 'a game loop exists');
  t.game.destroy();
});

test('the setup screen also carries the calibration steps and the keyboard diagram (positions and characters)', async () => {
  const t = await start();
  const cal = t.last('vm:calibration');
  assert.equal(cal.steps.length, 5);
  assert.ok(cal.steps.every((s) => s.confirmable === false), 'every calibration gesture is observable, none needs a confirm button');
  assert.deepEqual(Object.keys(cal.diagram).filter((k) => ['positions', 'characters'].includes(k)), ['positions', 'characters']);
  const flat = (rows) => rows.flat();
  assert.ok(flat(cal.diagram.positions.rows).some((k) => k.label === 'Caps' && k.state === 'layer'), 'Caps is the held key');
  assert.ok(flat(cal.diagram.positions.rows).some((k) => k.label === 'H' && k.state === 'target'), 'H is ringed');
  assert.ok(flat(cal.diagram.characters.rows).length > 40);
  assert.match(cal.diagram.positions.caption, /Physical positions: hold Caps about 200 ms, then tap H/);
  // switching the keyboard in setup redraws the diagram for the Microsoft keyboard (bottom row differs)
  t.command({ type: 'selectKeyboard', id: 'microsoft' });
  const ms = t.last('vm:calibration');
  assert.equal(ms.keyboard, 'microsoft');
  const bottom = (v) => v.diagram.positions.rows.at(-1).map((k) => k.label).join(' ');
  assert.notEqual(bottom(ms), bottom(cal));
});

test('Return on calibration step 2 only settles the step; it does not also continue', async () => {
  const t = await start();
  t.player.tap('Enter');                         // setup -> calibration
  assert.equal(t.game.machine.top.id, 'calibration');
  t.player.tap('ArrowLeft');                     // step 1 observed
  t.player.tap('Enter');                         // step 2 observed (Return)
  assert.equal(t.game.machine.top.id, 'calibration', 'still on the calibration screen');
  const cal = t.last('vm:calibration');
  assert.deepEqual(cal.steps.map((s) => s.status), ['observed', 'observed', 'not_started', 'not_started', 'not_started']);
  assert.equal(cal.steps[2].current, true);
});

test('chooseRow selects a calibration step by mouse and leaves the steps before it skipped', async () => {
  const t = await start();
  t.player.tap('Enter');
  t.command({ type: 'chooseRow', id: 'space-a' });
  const cal = t.last('vm:calibration');
  assert.deepEqual(cal.steps.map((s) => s.status), ['skipped', 'skipped', 'not_started', 'not_started', 'not_started']);
  assert.equal(cal.steps.find((s) => s.current).id, 'space-a');
});

test('chooseRow selects journal rows by mouse and opens the Also rows', async () => {
  const t = intoHub(await start());
  t.player.tap('q');
  assert.equal(t.game.machine.top.kind, 'journal');
  const rows = (vm) => vm.groups.flatMap((g) => g.rows);
  assert.equal(rows(t.last('vm:journal')).find((r) => r.selected).id, 'orientation-01');
  t.command({ type: 'chooseRow', id: 'o01.s.glitch' });
  assert.equal(rows(t.last('vm:journal')).find((r) => r.selected).id, 'o01.s.glitch', 'the optional row is selected');
  assert.equal(t.last('vm:journal').detail, null, 'only a main quest has a detail card');
  t.command({ type: 'chooseRow', id: 'controls' });
  assert.equal(t.game.machine.top.kind, 'controls');
  assert.equal(t.last('vm:journal'), null, 'the journal is hidden while Controls is open');
  assert.ok(t.last('vm:controls'));
});

test('overlay screens do not stack: Settings over the journal hides the journal view-model', async () => {
  const t = intoHub(await start());
  t.player.tap('q');
  t.command({ type: 'chooseRow', id: 'settings' });
  assert.equal(t.game.machine.top.kind, 'settings');
  assert.equal(t.last('vm:journal'), null);
  assert.ok(t.last('vm:settings'));
  t.player.tap('Escape');
  assert.equal(t.game.machine.top.kind, 'journal');
  assert.ok(t.last('vm:journal'), 'the journal comes back when Settings closes');
});

test('resetProgress without confirmation opens the confirm card and erases nothing; confirmed erases', async () => {
  const storage = new MemoryStorage();
  const t = intoHub(await start({ storage }));
  t.player.tap('q');
  t.command({ type: 'chooseRow', id: 'settings' });
  assert.equal(t.last('vm:settings').confirmReset, false);
  t.command({ type: 'resetProgress', confirmed: false });
  assert.equal(t.last('vm:settings').confirmReset, true, 'the confirm card opens');
  assert.ok(storage.getItem('kanata-hero:progress'), 'nothing is erased yet');
  t.player.tap('Escape');                        // Keep: closes the card only
  assert.equal(t.last('vm:settings').confirmReset, false);
  assert.equal(t.game.machine.top.kind, 'settings');
  t.command({ type: 'resetProgress', confirmed: false });
  let reset = false;
  t.game.bus.on('game:reset', () => { reset = true; });
  t.command({ type: 'resetProgress', confirmed: true });
  assert.equal(reset, true);
  assert.equal(storage.getItem('kanata-hero:progress'), null);
});

test('setSetting reaches the display flags and the world reduced-motion switch', async () => {
  const t = intoHub(await start());
  assert.equal(t.game.world.reducedMotion, false);
  t.command({ type: 'setSetting', key: 'reducedMotion', value: 'on' });
  assert.equal(t.last('vm:settings-flags').reducedMotion, 'on');
  assert.equal(t.game.world.reducedMotion, true, 'reduced motion reaches the world');
  t.command({ type: 'setSetting', key: 'reducedMotion', value: 'off' });
  assert.equal(t.game.world.reducedMotion, false);
  t.command({ type: 'setSetting', key: 'largerText', value: true });
  assert.equal(t.last('vm:settings-flags').largerText, true);
});

test('vm:inset: present on the guided popup and the lap, absent on recall and during overlays, four cells each', async () => {
  const t = intoHub(await start());
  const popupInset = t.rec.of('vm:inset').find((v) => v && v.header === 'Close the popup');
  assert.ok(popupInset, 'the popup teaches Caps tap -> Escape');
  assert.equal(popupInset.cells.output.name, 'Escape');
  assert.deepEqual(popupInset.cells.order.map((o) => o.tag), ['Tap']);
  // finish the keys step, then the lap starts
  t.player.tap('q'); t.player.tap('q'); t.player.tap('Backquote'); t.player.tap('?'); t.player.tap('Escape'); t.player.wait(4);
  const lap = t.last('vm:inset');
  assert.equal(lap.header, 'Move south');
  assert.equal(lap.cells.output.name, 'Down Arrow');
  assert.deepEqual(lap.cells.order.map((o) => `${o.key.label} ${o.tag}`), ['Caps Hold', 'J Tap']);
  assert.equal(lap.cells.position.target, 'J');
  assert.equal(lap.cells.effect.text, 'Step south');
  assert.equal(lap.layer, 'nav layer · tap-hold Caps · 200 ms');
  t.player.tap('?');                              // Layout help covers the screen: no inset behind it
  assert.equal(t.last('vm:inset'), null);
  t.player.tap('Escape');
  assert.ok(t.last('vm:inset'), 'back on the lap');
});

test('vm:markers flags the current target and walks it along the lap', async () => {
  const t = intoHub(await start());
  t.player.tap('q'); t.player.tap('q'); t.player.tap('Backquote'); t.player.tap('?'); t.player.tap('Escape'); t.player.wait(4);
  const current = (vm) => vm.floor.filter((f) => f.current).map((f) => f.id);
  assert.deepEqual(current(t.last('vm:markers')), ['o01-loop:down']);
  for (let i = 0; i < 10; i += 1) t.player.step('ArrowDown');
  assert.deepEqual(current(t.last('vm:markers')), ['o01-loop:right']);
  assert.equal(t.last('vm:markers').floor.find((f) => f.id === 'o01-loop:down').state, 'gold');
});

test('a DataLoadError becomes the error scene with the file named, never a throw', async () => {
  const kit = readJson(ATLAS_PATHS.kit);
  const used = readJson('/design/levels/orientation/map.json').placements.find((p) => p.entry && !p.state_set && kit.entries.some((e) => e.name === p.entry)).entry;
  kit.entries = kit.entries.filter((e) => e.name !== used);
  const fetchFn = diskFetch({ overrides: { [ATLAS_PATHS.kit]: kit } });
  const bus = new EventBus();
  const rec = new BusRecorder(bus);
  const game = await createGame({ bus, fetchFn, baseUrl: '/', loadImage: stubLoadImage(), clock: new FakeClock(), storage: new MemoryStorage(), headless: true });
  assert.ok(game.error, 'the failure is reported on the handle');
  assert.equal(game.machine.top.kind, 'error');
  const vm = rec.of('vm:error').at(-1);
  assert.equal(vm.file, '/design/levels/orientation/map.json', 'the map names an atlas entry that the kit atlas no longer has');
  assert.equal(vm.kind, 'shape');
  assert.ok(vm.message.includes(used), 'the missing name is in the message');
  const missing = diskFetch({ missing: ['/design/levels/world.json'] });
  const g2 = await createGame({ fetchFn: missing, baseUrl: '/', loadImage: stubLoadImage(), clock: new FakeClock(), headless: true });
  assert.equal(g2.error.file, '/design/levels/world.json');
  assert.equal(g2.error.kind, 'missing');
});
