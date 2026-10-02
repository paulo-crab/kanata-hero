import { test } from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync, existsSync, readdirSync } from 'node:fs';
import { fileURLToPath } from 'node:url';
import path from 'node:path';

import { EventBus, FakeClock, DataLoadError, STEP_MS } from '../src/shared/index.js';
import * as engine from '../src/engine/index.js';
import * as input from '../src/input/index.js';
import * as runtime from '../src/runtime/index.js';
import * as ui from '../src/ui/index.js';

const here = path.dirname(fileURLToPath(import.meta.url));
const repo = path.resolve(here, '..', '..');

test('module stubs import and export the contract names', () => {
  for (const n of ['loadGameData', 'loadAtlasSet', 'AtlasSet', 'AnimationPlayer', 'World', 'Avatar', 'GameLoop', 'Renderer', 'computeCamera', 'chooseZoom']) {
    assert.ok(n in engine, `engine.${n}`);
  }
  for (const n of ['KeyInterpreter', 'interpretKey', 'resolveAction', 'Calibration', 'LayoutManifest', 'layoutHelpModel', 'HintGate', 'BINDINGS']) {
    assert.ok(n in input, `input.${n}`);
  }
  for (const n of ['SceneMachine', 'RuleRuntime', 'DialogueRuntime', 'EvidenceLog', 'ProgressStore', 'computeStars', 'parseCondition', 'FormScene', 'WalkScene', 'LabelScene', 'EditorScene']) {
    assert.ok(n in runtime, `runtime.${n}`);
  }
  for (const n of ['mountUi', 'Component', 'COMPONENTS', 'insetRect', 'rectsOverlap']) {
    assert.ok(n in ui, `ui.${n}`);
  }
});

test('stubs throw not implemented', async () => {
  assert.throws(() => new runtime.ProgressStore({}), /not implemented/);
});

test('pure engine helpers match the contract', () => {
  assert.equal(engine.chooseZoom(1366, 768), 4);
  assert.equal(engine.chooseZoom(1920, 1080), 6);
  const cam = engine.computeCamera({ x: 3 * 16 + 8, y: 2 * 16 + 16 }, { x: 0, y: 0, w: 28, h: 18 });
  assert.deepEqual(cam, { x: 0, y: 0 });
  assert.deepEqual(ui.insetRect(4), { x: 16, y: 412, w: 572, h: 292 });
});

test('bus is ordered and isolates handler errors', () => {
  const bus = new EventBus();
  const seen = [];
  bus.on('a', () => { seen.push('a1'); bus.emit('b'); seen.push('a2'); });
  bus.on('b', () => seen.push('b'));
  bus.on('bus:error', (e) => seen.push('err:' + e.topic));
  bus.on('c', () => { throw new Error('x'); });
  bus.emit('a');
  bus.emit('c');
  assert.deepEqual(seen, ['a1', 'a2', 'b', 'err:c']);
});

test('fake clock fires timers in order', () => {
  const c = new FakeClock();
  const out = [];
  c.setTimer(20, () => out.push(20));
  c.setTimer(10, () => out.push(10));
  c.advance(25);
  assert.deepEqual(out, [10, 20]);
  assert.equal(c.now(), 25);
  assert.ok(STEP_MS > 16 && STEP_MS < 17);
});

test('DataLoadError names the file', () => {
  const e = new DataLoadError({ file: '/x.json', kind: 'missing', detail: 'HTTP 404' });
  assert.match(e.message, /\/x\.json/);
});

test('every data and atlas file named by the engine exists', () => {
  const files = [...Object.values(engine.DATA_FILES)];
  for (const a of Object.values(engine.ATLAS_FILES)) files.push(a.json, a.png);
  for (const f of files) assert.ok(existsSync(path.join(repo, f)), f);
});

test('no audio API in game/src', () => {
  const walk = (d) => readdirSync(d, { withFileTypes: true }).flatMap((e) =>
    e.isDirectory() ? walk(path.join(d, e.name)) : [path.join(d, e.name)]);
  for (const f of walk(path.join(repo, 'game', 'src')).filter((p) => p.endsWith('.js'))) {
    assert.doesNotMatch(readFileSync(f, 'utf8'), /\bAudioContext\b|new Audio\(|<audio/, f);
  }
});

test('CONTRACTS.md maps every requirement of the four specs', () => {
  const contracts = readFileSync(path.join(repo, 'game', 'CONTRACTS.md'), 'utf8');
  const specDir = path.join(repo, 'openspec', 'changes', 'build-level-one', 'specs');
  let count = 0;
  for (const cap of readdirSync(specDir)) {
    const text = readFileSync(path.join(specDir, cap, 'spec.md'), 'utf8');
    for (const m of text.matchAll(/^### Requirement: (.+)$/gm)) {
      count += 1;
      assert.ok(contracts.includes(`| ${cap} | ${m[1].trim()} |`), `unmapped: ${cap} / ${m[1]}`);
    }
  }
  assert.equal(count, 29);
});
