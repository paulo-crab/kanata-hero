// Condition grammar and rule runtime against the real level 01 data (tasks 4.2, 4.4).
import { test } from 'node:test';
import assert from 'node:assert/strict';
import { EventBus, DataLoadError } from '../../src/shared/index.js';
import { parseCondition, RuleRuntime, SUPPORTED_OPS, DialogueRuntime } from '../../src/runtime/index.js';
import { atomsOf } from '../../src/runtime/condition.js';
import { loadData, readJson } from './helpers.js';

function rules(over = {}) {
  const data = loadData();
  const bus = new EventBus();
  const intents = [];
  bus.on('intent', (i) => intents.push(i));
  const state = over.state || { flags: [], levelsDone: [], npc: {}, levels: {} };
  const level = over.level || data.level;
  const r = new RuleRuntime({ level, map: data.map, district: data.district, world: data.world, state, bus });
  return { r, bus, intents, data, state };
}

test('parseCondition: atoms, groups, errors', () => {
  const a = parseCondition('scene_success:a & dialogue_done:b');
  assert.equal(a.terms.length, 2);
  assert.deepEqual(a.terms[0], { type: 'atom', name: 'scene_success', arg: 'a' });
  const g = parseCondition('any_of:scene_success:a|scene_success:b & step_start:x');
  assert.equal(g.terms[0].type, 'any_of');
  assert.equal(g.terms[0].atoms.length, 2);
  const c = parseCondition('count:2:scene_success:a|scene_success:b|scene_success:c');
  assert.equal(c.terms[0].n, 2);
  assert.equal(parseCondition('reach_cell:3,12').terms[0].arg, '3,12');
  assert.throws(() => parseCondition('bogus:x'));
  assert.throws(() => parseCondition('count:3:scene_success:a|scene_success:b'));
  assert.throws(() => parseCondition('any_of:scene_success:a'));
  assert.throws(() => parseCondition('reach_cell:a,b'));
});

test('every condition in the level 01 data parses', () => {
  const { level } = loadData();
  for (const s of level.steps) parseCondition(s.completes_when);
  for (const t of level.triggers) parseCondition(t.when);
  for (const d of level.dialogue) if (d.when && !d.on_request) parseCondition(d.when);
});

test('SUPPORTED_OPS covers every op level 01 uses and not light_state or grant', () => {
  const { level } = loadData();
  const used = new Set(level.triggers.flatMap((t) => t.then.map((o) => o.op)));
  for (const op of used) assert.ok(SUPPORTED_OPS.includes(op), op);
  assert.ok(!SUPPORTED_OPS.includes('light_state') && !SUPPORTED_OPS.includes('grant'));
});

test('an unsupported trigger op fails the load naming the level file', () => {
  const data = loadData();
  const level = structuredClone(data.level);
  level.triggers[0].then.push({ op: 'light_state', light_state: 'x' });
  assert.throws(() => rules({ level }), (e) => e instanceof DataLoadError && e.kind === 'unsupported'
    && e.file === '/design/levels/orientation/levels/01-the-lobby.json' && /light_state/.test(e.detail));
});

test('a trigger naming an unknown gate, npc state or flag fails the load as shape', () => {
  const data = loadData();
  for (const bad of [{ op: 'unlock_gate', gate: 'g.nope' }, { op: 'npc_state', npc: 'ivo', state: 'nope' }, { op: 'set_flag', flag: 'nope' }]) {
    const level = structuredClone(data.level);
    level.triggers[0].then.push(bad);
    assert.throws(() => rules({ level }), (e) => e instanceof DataLoadError && e.kind === 'shape');
  }
});

test('start fires step_start for the first step: objective and the welcome line', () => {
  const { r, intents } = rules();
  r.start();
  assert.equal(r.currentStep.id, 'o01.s.arrive');
  assert.deepEqual(intents.map((i) => i.type), ['objective', 'say']);
  assert.deepEqual(intents[1], { type: 'say', dialogueId: 'o01.d.welcome', modal: true });
});

test('popup success: trigger ops, success line, next step start (worked example order)', () => {
  const { r, intents } = rules();
  r.start();
  r.notify({ type: 'dialogue_done', id: 'o01.d.welcome' });
  assert.equal(r.currentStep.id, 'o01.s.popup');
  intents.length = 0;
  const out = r.notify({ type: 'scene_success', id: 'o01-popup' });
  assert.deepEqual(out, intents);
  assert.deepEqual(out.map((i) => `${i.type}:${i.dialogueId || i.flag || i.npc || i.stepId || ''}`), [
    'objective:o01.s.keys',
    'setFlag:welcome-popup-closed', 'setNpcState:ivo',
    'say:o01.d.popup-done', 'say:o01.d.journal',
  ]);
  assert.deepEqual(out.find((i) => i.type === 'setNpcState'), { type: 'setNpcState', npc: 'ivo', state: 'post_wave' });
  assert.equal(out.find((i) => i.dialogueId === 'o01.d.popup-done').modal, true);
  assert.equal(out.find((i) => i.dialogueId === 'o01.d.journal').modal, false);
});

test('the keys step needs all three instruction lines (and-joined completes_when)', () => {
  const { r } = rules();
  r.start();
  r.notify({ type: 'dialogue_done', id: 'o01.d.welcome' });
  r.notify({ type: 'scene_success', id: 'o01-popup' });
  r.notify({ type: 'dialogue_done', id: 'o01.d.journal' });
  r.notify({ type: 'dialogue_done', id: 'o01.d.hint-key' });
  assert.equal(r.currentStep.id, 'o01.s.keys');
  const out = r.notify({ type: 'dialogue_done', id: 'o01.d.layout-help' });
  assert.equal(r.currentStep.id, 'o01.s.loop');
  assert.ok(out.some((i) => i.type === 'openScene' && i.sceneId === 'o01-loop' && i.kind === 'walk'));
  assert.ok(out.some((i) => i.dialogueId === 'o01.d.loop-down'));
});

test('reach_cell only counts while the step whose walk scene uses the cell is current', () => {
  const { r } = rules();
  r.start();
  r.notify({ type: 'reach_cell', cell: [3, 12] }); // arrive step: out of scope
  assert.ok(!r.facts.has('reach_cell:3,12'));
  r.notify({ type: 'dialogue_done', id: 'o01.d.welcome' });
  r.notify({ type: 'scene_success', id: 'o01-popup' });
  for (const id of ['journal', 'hint-key', 'layout-help']) r.notify({ type: 'dialogue_done', id: `o01.d.${id}` });
  const out = r.notify({ type: 'reach_cell', cell: [3, 12] });
  assert.deepEqual(out.map((i) => i.dialogueId), ['o01.d.loop-right']);
  assert.deepEqual(r.notify({ type: 'reach_cell', cell: [3, 12] }), []); // once
});

test('route-done trigger yields the four world changes, the glitch and completion', () => {
  const { r } = rules();
  r.start();
  const play = (f) => r.notify(f);
  play({ type: 'dialogue_done', id: 'o01.d.welcome' });
  play({ type: 'scene_success', id: 'o01-popup' });
  for (const id of ['journal', 'hint-key', 'layout-help']) play({ type: 'dialogue_done', id: `o01.d.${id}` });
  play({ type: 'scene_success', id: 'o01-loop' });
  play({ type: 'scene_success', id: 'o01-desk-label' });
  play({ type: 'scene_success', id: 'o01-four-stops' });
  assert.equal(r.currentStep.id, 'o01.s.recall');
  assert.equal(r.npcState('ivo'), 'north');
  assert.ok(r.isVisible('ivo_north'));
  assert.ok(!r.isVisible('ivo'));
  const early = play({ type: 'reach_cell', cell: [11, 4] });
  assert.ok(early.some((i) => i.dialogueId === 'o01.d.reminder'));
  assert.equal(r.npcState('ivo'), 'post_wave');
  assert.ok(r.isVisible('ivo'));
  const out = play({ type: 'scene_success', id: 'o01-unprompted' });
  const types = out.map((i) => `${i.type}:${i.placement || i.gate || i.npc || i.flag || i.interaction || i.level || ''}${i.state ? `=${i.state}` : ''}`);
  assert.deepEqual(types.filter((t) => !t.startsWith('say') && !t.startsWith('objective')), [
    'setPlacementState:turnstile=open', 'unlockGate:g.turnstile', 'setNpcState:ivo=post_nod',
    'setFlag:turnstile-open', 'setFlag:ivo-nodding', 'spawnGlitch:glitch_lobby',
    'journalEntry:', 'completeLevel:orientation-01',
  ]);
  assert.ok(r.isVisible('glitch_lobby'));
  assert.equal(r.currentStep.id, 'o01.s.glitch'); // optional step is current, level still completes
});

test('onRequest says the on_request line every time; request is no step condition', () => {
  const { r } = rules();
  r.start();
  assert.deepEqual(r.onRequest('o01.d.popup'), [{ type: 'say', dialogueId: 'o01.d.popup-again', modal: false, onRequest: true }]);
  assert.equal(r.onRequest('o01.d.popup').length, 1);
  assert.deepEqual(r.onRequest('o01.d.journal'), []);
});

test('visible_when and requires on map interactions', () => {
  const { r, state } = rules();
  assert.ok(r.isVisible('ivo_start'));
  assert.ok(!r.isVisible('ivo_north'));
  assert.ok(!r.isVisible('glitch_lobby'));
  assert.ok(!r.requirementsMet('printer_terminal'));
  state.levelsDone.push('orientation-01');
  assert.ok(r.isVisible('glitch_lobby'));
  assert.ok(r.requirementsMet('printer_terminal'));
});

test('resume: facts and steps restore from the progress document', () => {
  const a = rules();
  a.r.start();
  a.r.notify({ type: 'dialogue_done', id: 'o01.d.welcome' });
  const snap = a.r.snapshot();
  const b = rules({ state: { flags: [], levelsDone: [], npc: {}, levels: { 'orientation-01': snap } } });
  assert.equal(b.r.currentStep.id, 'o01.s.popup');
  b.r.start();
  assert.ok(b.intents.some((i) => i.type === 'openScene' && i.sceneId === 'o01-popup'));
});

test('dialogue: every portrait key of level 01 exists in the real portraits atlas', () => {
  const { level } = loadData();
  const portraits = readJson('art-direction/portraits/portraits-atlas.json').portraits;
  const bus = new EventBus();
  const d = new DialogueRuntime({ level, bus, rules: { notify() {} }, portraitRect: (k) => portraits[k] });
  for (const line of level.dialogue) {
    const vm = d.viewModelFor(line, 'conversation');
    if (line.portrait) assert.ok(portraits[vm.portrait.key], vm.portrait.key);
    else assert.equal(vm.portrait, null);
    assert.equal(vm.objectSpeaker, !line.portrait);
  }
});

test('dialogue: modal lines own Return and Esc, instruction lines do not and complete on their key', () => {
  const { level } = loadData();
  const bus = new EventBus();
  const done = [];
  const d = new DialogueRuntime({ level, bus, rules: { notify: (f) => done.push(f.id) } });
  assert.equal(d.open('o01.d.welcome'), 'modal');
  assert.equal(d.open('o01.d.popup-done'), 'modal'); // queues behind the open conversation
  assert.equal(d.current().id, 'o01.d.welcome');
  assert.equal(d.open('o01.d.journal'), 'instruction');
  assert.equal(d.instruction().id, 'o01.d.journal');
  d.skip();
  assert.equal(d.current().id, 'o01.d.popup-done');
  d.advance();
  assert.equal(d.current(), null);
  assert.deepEqual(done, ['o01.d.welcome', 'o01.d.popup-done']);
  d.observe({ output: 'x', phase: 'down', repeat: false });
  d.observe({ output: 'q', phase: 'down', repeat: true }); // repeat ignored
  assert.deepEqual(done.slice(2), []);
  d.observe({ output: 'q', phase: 'down', repeat: false });
  assert.deepEqual(done.slice(2), ['o01.d.journal']);
  const vm = d.viewModel();
  assert.equal(vm.mode, 'instruction');
  assert.deepEqual(vm.hint, level.dialogue.find((x) => x.id === 'o01.d.journal').hint);
  assert.deepEqual(vm.footer, []);
});
