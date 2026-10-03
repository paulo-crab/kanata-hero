// Playtest 1, item 1: on the first lobby screens at most two overlays are open (the dialogue or instruction, and the
// keyboard inset); the objective strip steps aside and a dialogue that states the instruction gets no second bar.
import { test } from 'node:test';
import assert from 'node:assert/strict';
import { ScriptedInput, MemoryStorage, BusRecorder, diskFetch, stubLoadImage } from '../harness/index.js';
import { createGame } from '../../src/main.js';
import { FakeClock, EventBus } from '../../src/shared/index.js';

async function start() {
  const bus = new EventBus();
  const rec = new BusRecorder(bus);
  const clock = new FakeClock();
  const game = await createGame({ bus, fetchFn: diskFetch(), baseUrl: '/', loadImage: stubLoadImage(), clock, storage: new MemoryStorage(), headless: true });
  const player = new ScriptedInput({ target: game.interpreter, advance: (ms) => { clock.advance(ms); game.loop.advance(ms); } });
  const open = () => ['vm:dialogue', 'vm:inset', 'vm:scene-bar', 'vm:feedback'].filter((t) => rec.of(t).at(-1));
  return { game, rec, player, open, last: (t) => rec.of(t).at(-1) };
}

test('welcome, popup and key lines: at most two overlays, the objective strip hidden while either is open', async () => {
  const t = await start();
  t.player.tap('Escape');
  t.player.tap('Enter');                      // skip setup
  t.player.wait(90);
  assert.deepEqual(t.open(), ['vm:dialogue'], 'the welcome conversation alone');
  assert.equal(t.last('vm:dialogue').mode, 'conversation');
  t.player.tap('Enter');
  t.player.wait(2);
  assert.equal(t.game.machine.top.kind, 'form');
  assert.deepEqual(t.open(), ['vm:dialogue', 'vm:inset'], 'the popup: the instruction and the inset');
  assert.equal(t.last('vm:dialogue').mode, 'instruction');
  assert.ok(!t.last('vm:scene-bar'), 'no second bar: the instruction already says "press Escape"');
  assert.equal(t.last('vm:hud').compact, true, 'the objective strip steps aside; the shortcut chips stay');
  assert.ok(t.last('vm:hud').chips.length >= 2);
  t.player.tap('Escape');
  t.player.wait(2);
  t.player.tap('Enter');
  t.player.wait(2);
  assert.equal(t.game.machine.top.kind, 'hub');
  assert.ok(t.open().length <= 2, `hub overlays: ${t.open()}`);
});

test('the objective strip returns when no dialogue and no inset is open', async () => {
  const t = await start();
  t.player.tap('Escape');
  t.player.tap('Enter');
  t.player.wait(90);
  t.player.tap('Enter');
  t.player.wait(2);
  t.player.tap('Escape');                      // popup closed
  t.player.wait(2);
  t.player.tap('Enter');                       // popup-done conversation closed
  t.player.wait(2);
  // keys step: the journal instruction is open, so still compact; close it by doing it (Q) and the next ones
  assert.equal(t.last('vm:hud').compact, !!(t.last('vm:dialogue') || t.last('vm:inset')));
  t.game.session.dialogue.clearInstruction();
  t.game.session.pump();
  const hud = t.last('vm:hud');
  assert.equal(hud.compact, !!t.last('vm:inset'));
});
