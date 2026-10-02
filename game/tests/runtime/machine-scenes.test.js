// Scene machine, key ownership and the level 01 scene kinds (tasks 4.1, 4.3).
import { test } from 'node:test';
import assert from 'node:assert/strict';
import { TRANSITIONS, SceneMachine } from '../../src/runtime/index.js';
import { EventBus } from '../../src/shared/index.js';
import { makeGame } from './helpers.js';

class Stub {
  constructor(kind) { this.id = kind; this.kind = kind; this.modal = false; this.keys = {}; this.finished = null; }
  enter(ctx, p) { this.entered = p; }
  handle() { return false; }
  update() {}
  exit() { return {}; }
  snapshot() { return { s: this.kind }; }
  viewModel() { return null; }
}

function machine() {
  const ctx = { bus: new EventBus() };
  const kinds = Object.keys(TRANSITIONS);
  return new SceneMachine(ctx, Object.fromEntries(kinds.map((k) => [k, () => new Stub(k)])));
}

test('transition table: every legal edge pushes, every other edge throws', () => {
  const kinds = Object.keys(TRANSITIONS);
  for (const from of kinds) {
    for (const to of kinds) {
      const m = machine();
      m.push(from);
      if (TRANSITIONS[from].includes(to)) {
        assert.doesNotThrow(() => m.push(to), `${from}->${to}`);
        assert.equal(m.top.kind, to);
      } else {
        assert.throws(() => m.push(to), /Illegal scene transition/, `${from}->${to}`);
      }
    }
  }
});

test('replace follows the table; pop restores the scene below with its snapshot', () => {
  const m = machine();
  m.push('setup');
  m.replace('calibration');
  m.replace('arrival');
  assert.throws(() => m.replace('journal'));
  m.replace('hub');
  const hub = m.top;
  m.push('journal');
  m.push('layout-help');
  assert.equal(m.stack.length, 3);
  m.pop();
  m.pop();
  assert.equal(m.top, hub);
  assert.deepEqual(hub.entered, { restore: { s: 'hub' } });
});

test('modal layers stop propagation; input context merges the top layer keys', () => {
  const m = machine();
  const events = [];
  m.push('hub');
  m.top.handle = () => { events.push('hub'); return false; };
  m.push('dialogue');
  m.top.modal = true;
  m.top.keys = { enter: 'continue', esc: 'skip', hint: true };
  m.top.handle = () => { events.push('dialogue'); return false; };
  assert.equal(m.handle({}), false);
  assert.deepEqual(events, ['dialogue']);
  assert.deepEqual(
    (({ enter, esc, hint, sceneId, layoutHelp }) => ({ enter, esc, hint, sceneId, layoutHelp }))(m.inputContext()),
    { enter: 'continue', esc: 'skip', hint: true, sceneId: 'dialogue', layoutHelp: true },
  );
});

test('key ownership per scene follows the table in CONTRACTS 5.2', () => {
  const g = makeGame();
  const { session } = g;
  const f = session.machine.factories;
  const own = (kind, p) => {
    const s = f[kind](p);
    s.enter(session.ctx, p || {});
    const { enter, esc, arrows, journal, hint, typing } = { typing: false, ...s.keys };
    return { enter, esc, arrows, journal: !!journal, hint: !!hint, typing: !!typing };
  };
  const table = {
    setup: ['continue', 'skip', 'choose', false, false, false],
    calibration: ['continue', 'skip', 'choose', false, false, false],
    arrival: ['none', 'none', 'none', false, false, false],
    hub: ['interact', 'none', 'move', true, true, false],
    dialogue: ['continue', 'skip', 'none', false, true, false],
    walk: ['interact', 'none', 'move', true, true, false],
    form: ['none', 'text', 'text', false, true, true],
    label: ['text', 'back', 'text', false, true, true],
    editor: ['text', 'back', 'text', false, true, true],
    'layout-help': ['none', 'back', 'choose', false, false, false],
    journal: ['confirm', 'back', 'choose', true, false, false],
    controls: ['confirm', 'back', 'choose', false, false, false],
    settings: ['confirm', 'back', 'choose', false, false, false],
    error: ['none', 'none', 'none', false, false, false],
  };
  const payloads = { walk: { sceneId: 'o01-loop' }, form: { sceneId: 'o01-popup' }, label: { sceneId: 'o01-desk-label' }, editor: { sceneId: 'o01-fold' } };
  for (const [kind, [enter, esc, arrows, journal, hint, typing]] of Object.entries(table)) {
    assert.deepEqual(own(kind, payloads[kind]), { enter, esc, arrows, journal, hint, typing }, kind);
  }
});

test('Layout help open and close leaves the hub unchanged (hub, avatar, step, objective)', () => {
  const g = makeGame();
  g.session.start();
  g.player.tap('Escape');
  g.player.tick(30);
  g.player.tap('Enter');
  g.player.tap('Escape');
  g.player.tap('Enter');
  const before = JSON.stringify([g.world.avatar.cell, g.world.avatar.facing, g.session.rules.snapshot(), g.session.machine.stack.map((s) => s.kind)]);
  g.player.tap('?');
  assert.equal(g.session.machine.top.kind, 'layout-help');
  assert.ok(g.vms['vm:layout-help']);
  g.player.tap('Escape');
  assert.equal(g.vms['vm:layout-help'], null);
  const after = JSON.stringify([g.world.avatar.cell, g.world.avatar.facing, g.session.rules.snapshot(), g.session.machine.stack.map((s) => s.kind)]);
  assert.equal(after, before);
});

// ---- scenes: success and wrong-input paths against the real level data ----------------------

function atPopup() {
  const g = makeGame();
  g.session.start();
  g.player.tap('Escape');
  g.player.tick(30);
  g.player.tap('Enter');
  return g;
}

test('form (popup): arrows and Return are named in feedback and change nothing; Escape succeeds', () => {
  const g = atPopup();
  const { level } = g.data;
  const def = level.terminal_scenes.find((s) => s.id === 'o01-popup');
  const lines = [];
  g.bus.on('scene:feedback', (e) => lines.push(e));
  for (const [out, key] of [['ArrowLeft', 'ArrowLeft'], ['ArrowUp', 'ArrowUp'], ['Enter', 'other'], ['x', 'other']]) {
    g.player.tap(out);
    assert.equal(g.session.machine.top.kind, 'form');
    assert.equal(lines.at(-1).line, def.task.steps[0].feedback[key]);
  }
  assert.equal(g.vms['vm:feedback'].confidenceLabel, 'Output observed');
  assert.match(g.vms['vm:feedback'].observed, /observed/);
  g.player.tap('Escape');
  assert.equal(g.session.machine.top.kind, 'dialogue');
  const ev = g.session.evidence.scene('o01-popup');
  assert.deepEqual(ev.actions, { total: 5, correct: 1 });
  assert.equal(ev.result, 'success');
  assert.equal(ev.criticalOk, false);
});

test('walk: a wrong direction is never blocked, counts incorrect, the lap continues from there', () => {
  const g = atPopup();
  const { player, world, session } = g;
  player.tap('Enter');
  player.tap('Escape');
  player.tap('Enter');
  for (const k of ['q', 'Escape', 'Backquote', '?', 'Escape']) player.tap(k);
  player.walk('s', 3);
  player.walk('e'); // wrong way for the 'down' leg
  assert.deepEqual(player.cell(), [4, 5]);
  player.walk('w');
  player.walk('s', 7);
  assert.deepEqual(player.cell(), [3, 12]);
  const ev = session.evidence.scene('o01-loop');
  assert.equal(ev.actions.total, 12);
  assert.equal(ev.actions.correct, 11); // only the step east was wrong; stepping back is correct
  assert.equal(session.machine.top.kind, 'walk');
  assert.ok(g.vms['vm:markers'].floor.some((m) => m.state === 'gold'));
  assert.ok(g.vms['vm:markers'].floor.some((m) => m.state === 'teal'));
  assert.equal(world.avatar.facing, 's');
});

test('walk: a hint in a guided scene records use without forfeiting the star', () => {
  const g = atPopup();
  const { player, session } = g;
  player.tap('Enter');
  player.tap('Escape');
  player.tap('Enter');
  for (const k of ['q', 'Escape', 'Backquote', '?', 'Escape']) player.tap(k);
  player.tap('Backquote');
  assert.equal(g.vms['vm:hint-card'] ?? null, null);
  const ev = session.evidence.scene('o01-loop');
  assert.equal(ev.hintUsed, true);
  assert.equal(ev.hintForfeit, false);
});

function atLabel() {
  const g = atPopup();
  const { player } = g;
  player.tap('Enter');
  player.tap('Escape');
  player.tap('Enter');
  for (const k of ['q', 'Escape', 'Backquote', '?', 'Escape']) player.tap(k);
  player.walk('s', 10); player.walk('e', 14); player.walk('n', 7); player.walk('w', 8);
  player.tap('Enter'); player.tap('Enter');
  player.goTo([9, 4]);
  player.goTo([7, 10]);
  return g;
}

test('label: wrong letters, nav chords and held Caps get their own feedback; progress is never lost', () => {
  const g = atLabel();
  const { player } = g;
  const def = g.data.level.terminal_scenes.find((s) => s.id === 'o01-desk-label');
  const lines = [];
  g.bus.on('scene:feedback', (e) => lines.push(e.line));
  assert.equal(g.session.machine.top.kind, 'label');
  player.tap('w');
  assert.equal(g.vms['vm:scene-bar'].nextLetter, 'e');
  player.tap('x');
  assert.equal(lines.at(-1), def.task.feedback.other);
  player.tap('ArrowLeft');
  assert.equal(lines.at(-1), def.task.feedback.ArrowLeft);
  player.tap('e', { mods: { alt: true } });
  player.tap('ArrowRight', { mods: { alt: true } });
  assert.equal(lines.at(-1), def.task.feedback['Alt+ArrowRight']);
  assert.equal(g.vms['vm:scene-bar'].field.text, 'w');
  player.type('est');
  assert.equal(g.session.machine.top.kind, 'walk');
  assert.equal(g.session.evidence.scene('o01-desk-label').result, 'success');
});

test('label: Esc leaves without success; Interact at the stop reopens it; ? opens Layout help in a typing scene', () => {
  const g = atLabel();
  const { player } = g;
  player.tap('?');
  assert.equal(g.session.machine.top.kind, 'layout-help');
  player.tap('Escape');
  assert.equal(g.session.machine.top.kind, 'label');
  assert.equal(g.session.machine.inputContext().typing, true);
  player.tap('Escape');
  assert.equal(g.session.machine.top.kind, 'walk');
  assert.notEqual((g.session.evidence.scene('o01-desk-label') || {}).result, 'success');
  player.tap('Enter');
  assert.equal(g.session.machine.top.kind, 'label');
  player.type('west');
  assert.equal(g.session.machine.top.kind, 'walk');
});

test('stops must be reached in order; a later stop first does nothing', () => {
  const g = atLabel();
  const { player } = g;
  player.tap('Escape'); // leave the label
  player.goTo([19, 10]); // east first
  player.goTo([10, 14]); // then south
  assert.equal(g.session.rules.currentStep.id, 'o01.s.stops');
  assert.equal(g.session.machine.stack.at(-1).idx, 1); // only north is done
});
