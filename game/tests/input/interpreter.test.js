import { test } from 'node:test';
import assert from 'node:assert/strict';
import { interpretKey, KeyInterpreter, isClaimed } from '../../src/input/index.js';
import { ev, ctx, HUB, LABEL, makeInterpreter } from './helpers.js';

test('Caps + H: the browser reports ArrowLeft, no physical-key or layer claim', () => {
  const { interp, seen, clock } = makeInterpreter(ctx(HUB));
  clock.advance(50);
  // Kanata sends ArrowLeft down and up; the page never sees Caps.
  const down = interp.handleKeyEvent(ev('ArrowLeft', { code: 'ArrowLeft' }), 'down');
  const up = interp.handleKeyEvent(ev('ArrowLeft', { code: 'ArrowLeft' }), 'up');
  assert.equal(down.output, 'ArrowLeft');
  assert.equal(down.confidence, 'observed');
  assert.equal(down.action, 'move');
  assert.equal(down.dir, 'w');
  assert.equal(down.t, 1050);
  assert.equal(up.phase, 'up');
  assert.equal(seen.length, 2);
  const keys = Object.keys(down);
  for (const forbidden of ['layer', 'physical', 'physicalKey', 'source']) assert.ok(!keys.includes(forbidden));
});

test('the same output from a Right Command route is an identical event', () => {
  const a = interpretKey(ev('ArrowLeft', { code: 'ArrowLeft' }), 'down', 5);
  const b = interpretKey(ev('ArrowLeft', { code: 'ArrowLeft', metaKey: false }), 'down', 5);
  assert.deepEqual(a, b);
});

test('tap Caps arrives as Escape', () => {
  const { interp } = makeInterpreter(ctx({ ...HUB, esc: 'none' }));
  const e = interp.handleKeyEvent(ev('Escape', { code: 'Escape' }));
  assert.equal(e.output, 'Escape');
  assert.equal(e.action, null); // Esc does nothing in the open world
  assert.equal(e.text, null);
});

test('Return and typed letters', () => {
  const { interp } = makeInterpreter(ctx(HUB));
  const r = interp.handleKeyEvent(ev('Enter', { code: 'Enter' }));
  assert.equal(r.output, 'Enter');
  assert.equal(r.action, 'interact');
  assert.equal(r.text, null);
  const w = interp.handleKeyEvent(ev('w', { code: 'KeyW' }));
  assert.equal(w.text, 'w');
  assert.equal(w.action, null);
  const cap = interpretKey(ev('W', { code: 'KeyW', shiftKey: true }));
  assert.equal(cap.text, 'W');
  assert.equal(cap.combo, 'W');
});

test('Space output and text; Backquote by code; ? and Backquote are never text', () => {
  const sp = interpretKey(ev(' ', { code: 'Space' }));
  assert.equal(sp.output, 'Space');
  assert.equal(sp.text, ' ');
  const bq = interpretKey(ev('`', { code: 'Backquote' }));
  assert.equal(bq.output, 'Backquote');
  assert.equal(bq.text, null);
  const dead = interpretKey(ev('Dead', { code: 'Backquote', keyCode: 229 }));
  assert.equal(dead.output, 'Backquote'); // a dead-key input source still reaches the Hint key by code
  assert.equal(interpretKey(ev('Dead', { code: 'KeyE' })), null);
  const q = interpretKey(ev('?', { code: 'Slash', shiftKey: true }));
  assert.equal(q.output, '?');
  assert.equal(q.text, null);
  assert.equal(q.combo, '?');
});

test('combo: Ctrl, Alt, Meta in order, Shift omitted', () => {
  assert.equal(interpretKey(ev('ArrowRight', { altKey: true })).combo, 'Alt+ArrowRight');
  assert.equal(interpretKey(ev('ArrowRight', { altKey: true, shiftKey: true })).combo, 'Alt+ArrowRight');
  assert.equal(interpretKey(ev('d', { ctrlKey: true, altKey: true, metaKey: true })).combo, 'Ctrl+Alt+Meta+d');
  assert.equal(interpretKey(ev('ArrowLeft', { metaKey: true })).combo, 'Meta+ArrowLeft');
});

test('ignored keys: composing, IME, bare modifiers, dead keys', () => {
  assert.equal(interpretKey(ev('a', { isComposing: true })), null);
  assert.equal(interpretKey(ev('Process', { keyCode: 229 })), null);
  for (const k of ['Shift', 'Control', 'Alt', 'Meta', 'CapsLock', 'Dead', 'Unidentified']) { // no code given
    assert.equal(interpretKey(ev(k)), null, k);
  }
  const { interp, seen } = makeInterpreter(ctx(HUB));
  assert.equal(interp.handleKeyEvent(ev('Shift')), null);
  assert.equal(seen.length, 0);
});

test('reserved keys: Cmd chords are observed but never resolve or get prevented', () => {
  const { interp } = makeInterpreter(ctx({ ...HUB }));
  const cmdQ = interp.handleKeyEvent(ev('q', { metaKey: true }));
  assert.equal(cmdQ.action, null);
  const cmdBq = interp.handleKeyEvent(ev('`', { code: 'Backquote', metaKey: true }));
  assert.equal(cmdBq.action, null);
  assert.equal(isClaimed(cmdQ, ctx({ ...HUB })), false);
});

test('repeat is carried but never acts', () => {
  const { interp } = makeInterpreter(ctx(HUB));
  const e = interp.handleKeyEvent(ev('Enter', { repeat: true }));
  assert.equal(e.repeat, true);
  assert.equal(e.action, null);
});

test('heldDirection follows down and up phases, not OS repeat', () => {
  const { interp } = makeInterpreter(ctx(HUB));
  assert.equal(interp.heldDirection(), null);
  interp.handleKeyEvent(ev('ArrowLeft'), 'down');
  assert.equal(interp.heldDirection(), 'w');
  interp.handleKeyEvent(ev('ArrowLeft', { repeat: true }), 'down');
  interp.handleKeyEvent(ev('ArrowUp'), 'down');
  assert.equal(interp.heldDirection(), 'n');
  interp.handleKeyEvent(ev('ArrowUp'), 'up');
  assert.equal(interp.heldDirection(), 'w');
  interp.handleKeyEvent(ev('ArrowLeft'), 'up');
  assert.equal(interp.heldDirection(), null);
  interp.handleKeyEvent(ev('ArrowDown'), 'down');
  interp.clearHeld();
  assert.equal(interp.heldDirection(), null);
});

test('stamps t from the injected clock and emits input:event and onEvent', () => {
  const got = [];
  const { interp, clock, seen } = makeInterpreter(ctx(HUB));
  interp.onEvent = (e) => got.push(e);
  interp.handleKeyEvent(ev('a'));
  clock.advance(16);
  interp.handleKeyEvent(ev('b'));
  assert.deepEqual(seen.map((e) => e.t), [1000, 1016]);
  assert.equal(got.length, 2);
});

test('playerConfirm emits a player_confirmed event, never observed', () => {
  const { interp, seen } = makeInterpreter(ctx(HUB));
  const e = interp.playerConfirm('o01-hold', 'did');
  assert.equal(e.confidence, 'player_confirmed');
  assert.equal(e.sceneId, 'o01-hold');
  assert.equal(e.choice, 'did');
  assert.equal(seen.length, 1);
  assert.throws(() => interp.playerConfirm('x', 'maybe'));
});

// --- DOM adapter: a fake EventTarget, no DOM ---

function fakeTarget() {
  const handlers = {};
  return {
    addEventListener(t, h) { (handlers[t] ||= []).push(h); },
    removeEventListener(t, h) { handlers[t] = (handlers[t] || []).filter((x) => x !== h); },
    fire(type, e) { (handlers[type] || []).forEach((h) => h(e)); return e; },
    count: (t) => (handlers[t] || []).length,
  };
}

test('attach: preventDefault only for claimed outputs while the surface has focus', () => {
  const { interp, setContext } = makeInterpreter(ctx(HUB));
  const target = fakeTarget();
  interp.attach(target);
  assert.equal(target.fire('keydown', ev('Enter')).prevented, true); // interact
  assert.equal(target.fire('keydown', ev('a')).prevented, undefined); // unclaimed in the world
  assert.equal(target.fire('keydown', ev('Escape')).prevented, undefined); // Esc is nothing in the open world
  setContext(ctx({ ...HUB, surfaceFocused: false }));
  assert.equal(target.fire('keydown', ev('Enter')).prevented, undefined);
  interp.detach();
  assert.equal(target.count('keydown'), 0);
});

test('attach: Tab is never captured, in any context', () => {
  for (const c of [HUB, LABEL, { ...LABEL, consumes: ['Tab'] }]) {
    const { interp } = makeInterpreter(ctx(c));
    const target = fakeTarget();
    interp.attach(target);
    const e = target.fire('keydown', ev('Tab', { code: 'Tab' }));
    assert.equal(e.prevented, undefined);
    const s = target.fire('keydown', ev('Tab', { code: 'Tab', shiftKey: true }));
    assert.equal(s.prevented, undefined);
  }
});

test('attach: typing scene claims text and consumed Escape, never Cmd chords', () => {
  const popup = ctx({ typing: true, enter: 'none', esc: 'text', arrows: 'text', hint: true, consumes: ['Escape'] });
  const { interp } = makeInterpreter(popup);
  const target = fakeTarget();
  interp.attach(target);
  assert.equal(target.fire('keydown', ev('Escape')).prevented, true);
  assert.equal(target.fire('keydown', ev('w')).prevented, true);
  assert.equal(target.fire('keydown', ev('c', { metaKey: true })).prevented, undefined);
  assert.equal(target.fire('keydown', ev('Tab')).prevented, undefined);
  assert.equal(target.fire('keyup', ev('w')).prevented, undefined);
});

test('attach requires a target; reattach replaces the old listeners', () => {
  const { interp } = makeInterpreter(ctx(HUB));
  assert.throws(() => interp.attach(null));
  const t1 = fakeTarget();
  const t2 = fakeTarget();
  interp.attach(t1);
  interp.attach(t2);
  assert.equal(t1.count('keydown'), 0);
  assert.equal(t2.count('keydown'), 1);
});

test('KeyInterpreter needs a clock', () => {
  assert.throws(() => new KeyInterpreter({}));
});
