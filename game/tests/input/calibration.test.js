import { test } from 'node:test';
import assert from 'node:assert/strict';
import { Calibration, CALIBRATION_STEPS, STATUS_LABELS, KEYBOARD_TYPES, interpretKey } from '../../src/input/index.js';
import { ev, readRepo } from './helpers.js';

const obs = (key, extra) => interpretKey(ev(key, extra), 'down', 0);
const EXPECTED = ['ArrowLeft', 'Enter', '1', '!', '?'];

test('five steps with the contract ids and expected outputs', () => {
  assert.deepEqual(CALIBRATION_STEPS.map((s) => s.expected), EXPECTED);
  assert.deepEqual(CALIBRATION_STEPS.map((s) => s.id), ['caps-h', 'caps-n', 'space-a', 'space-q', 'shift-hold']);
});

test('expected outputs are browser events the manifest inventory records', () => {
  const m = JSON.parse(readRepo('design/layout/layout-manifest.json'));
  const seen = new Set(m.inventory.flatMap((r) => (r.observed?.events || []).map((e) => e.key)));
  // '?' is a reserved key, not an inventory output: the manifest records it under reserved_keys.
  const reserved = new Set(m.reserved_keys.map((r) => r.character));
  for (const k of EXPECTED) assert.ok(seen.has(k) || reserved.has(k), `manifest records an observable ${k}`);
});

test('all observed: five steps settle in order', () => {
  const cal = new Calibration();
  assert.equal(cal.current, 'caps-h');
  const results = EXPECTED.map((k) => cal.observe(obs(k)));
  assert.deepEqual(results.map((r) => r.stepId), CALIBRATION_STEPS.map((s) => s.id));
  assert.ok(results.every((r) => r.status === 'observed'));
  assert.equal(cal.current, null);
  assert.equal(cal.finished, true);
  assert.deepEqual(Object.values(cal.result().steps), Array(5).fill('observed'));
  assert.equal(cal.observe(obs('ArrowLeft')), null);
});

test('only the current step matches; other outputs, repeats, key-up and confirmations are ignored', () => {
  const cal = new Calibration();
  assert.equal(cal.observe(obs('Enter')), null);
  assert.equal(cal.observe(interpretKey(ev('ArrowLeft', { repeat: true }), 'down', 0)), null);
  assert.equal(cal.observe(interpretKey(ev('ArrowLeft'), 'up', 0)), null);
  assert.equal(cal.observe({ ...obs('ArrowLeft'), confidence: 'player_confirmed' }), null);
  assert.equal(cal.current, 'caps-h');
  assert.deepEqual(cal.observe(obs('ArrowLeft')), { stepId: 'caps-h', status: 'observed' });
});

test('partial skip: observed, skipped one, observed; the rest not started', () => {
  const cal = new Calibration();
  cal.observe(obs('ArrowLeft'));
  assert.deepEqual(cal.skipCurrent(), { stepId: 'caps-n', status: 'skipped' });
  assert.equal(cal.current, 'space-a');
  cal.observe(obs('1'));
  assert.deepEqual(cal.result().steps, {
    'caps-h': 'observed', 'caps-n': 'skipped', 'space-a': 'observed', 'space-q': 'not_started', 'shift-hold': 'not_started',
  });
  assert.equal(cal.finished, false);
});

test('skip by id, observed steps stay observed, unknown id throws', () => {
  const cal = new Calibration();
  cal.observe(obs('ArrowLeft'));
  assert.equal(cal.skip('caps-h'), null);
  assert.equal(cal.result().steps['caps-h'], 'observed');
  assert.deepEqual(cal.skip('shift-hold'), { stepId: 'shift-hold', status: 'skipped' });
  assert.equal(cal.current, 'caps-n');
  assert.throws(() => cal.skip('nope'));
});

test('full skip: skipAll settles every step as skipped', () => {
  const cal = new Calibration();
  assert.equal(cal.skipAll().length, 5);
  assert.deepEqual(Object.values(cal.result().steps), Array(5).fill('skipped'));
  assert.equal(cal.current, null);
  assert.equal(cal.skipCurrent(), null);
  assert.deepEqual(cal.skipAll(), []);
});

test('skipAll keeps steps already observed', () => {
  const cal = new Calibration();
  cal.observe(obs('ArrowLeft'));
  cal.observe(obs('Enter'));
  assert.deepEqual(cal.skipAll(), ['space-a', 'space-q', 'shift-hold']);
  assert.equal(cal.result().steps['caps-n'], 'observed');
});

test('keyboard type: macbook default, microsoft, invalid rejected, stored in the result', () => {
  const cal = new Calibration();
  assert.equal(cal.result().keyboard, 'macbook');
  cal.setKeyboard('microsoft');
  assert.equal(cal.keyboard, 'microsoft');
  assert.equal(cal.result().keyboard, 'microsoft');
  assert.throws(() => cal.setKeyboard('dvorak'));
  assert.throws(() => new Calibration('x'));
  assert.equal(new Calibration('microsoft').keyboard, 'microsoft');
});

test('keyboard type copy matches the manifest remap (Alt as Command, Windows as Option)', () => {
  const m = JSON.parse(readRepo('design/layout/layout-manifest.json'));
  const remap = Object.fromEntries(m.keyboards.microsoft.remap.map((r) => [r.physical, r.label]));
  assert.equal(remap['Alt-L'], 'Left Command');
  assert.equal(remap['Win-L'], 'Left Option');
  const ms = KEYBOARD_TYPES.find((k) => k.id === 'microsoft');
  assert.match(ms.label, /Alt is Command/);
  assert.match(ms.label, /Windows is Option/);
  assert.deepEqual(KEYBOARD_TYPES.map((k) => k.id), ['macbook', 'microsoft']);
});

test('result round-trips through JSON for all-observed, partial, full skip and fresh', () => {
  const make = {
    all() { const c = new Calibration('microsoft'); EXPECTED.forEach((k) => c.observe(obs(k))); return c; },
    partial() { const c = new Calibration(); c.observe(obs('ArrowLeft')); c.skipCurrent(); return c; },
    skipped() { const c = new Calibration(); c.skipAll(); return c; },
    fresh() { return new Calibration(); },
  };
  for (const [name, f] of Object.entries(make)) {
    const c = f();
    const back = Calibration.fromResult(JSON.parse(JSON.stringify(c.result())));
    assert.deepEqual(back.result(), c.result(), name);
    assert.equal(back.current, c.current, name);
  }
});

test('fromResult tolerates bad stored data', () => {
  assert.equal(Calibration.fromResult(null).keyboard, 'macbook');
  const c = Calibration.fromResult({ keyboard: 'amiga', steps: { 'caps-h': 'observed', 'caps-n': 'weird', nope: 'skipped' } });
  assert.equal(c.keyboard, 'macbook');
  assert.equal(c.result().steps['caps-h'], 'observed');
  assert.equal(c.result().steps['caps-n'], 'not_started');
  assert.ok(!('nope' in c.result().steps));
});

test('result is a copy; status copy never claims detection or keys', () => {
  const c = new Calibration();
  const r = c.result();
  r.steps['caps-h'] = 'observed';
  assert.equal(c.result().steps['caps-h'], 'not_started');
  assert.deepEqual(STATUS_LABELS, { not_started: 'Not started', observed: 'Observed output', skipped: 'Skipped' });
  for (const text of Object.values(STATUS_LABELS)) assert.doesNotMatch(text, /detect|verif|pressed|used/i);
  assert.deepEqual(c.rows().map((x) => x.current), [true, false, false, false, false]);
  assert.equal(c.rows()[0].statusLabel, 'Not started');
});
