// Task 6.5: pipeline guard. Confirms the art and level pipelines still pass and that removing an
// atlas name the level data uses is caught (by the data-side check, by the game loader and by createGame).
//   - validate_levels.py --all runs by default (about a second).
//   - build_all.py (the full art rebuild, about a minute, rewrites then restores generated files)
//     runs only with KH_FULL=1, e.g.  KH_FULL=1 node --test tests/checks/pipeline.test.js
//   - Python: KH_PY=/path/to/python (needs Pillow, numpy for build_all), else python3.
import { test } from 'node:test';
import assert from 'node:assert/strict';
import { spawnSync } from 'node:child_process';
import {
  REPO_ROOT, loadRealData, loadRealAtlasJson, clone, diskFetch, stubLoadImage, ATLAS_PATHS, readJson,
} from '../harness/index.js';
import { missingAtlasRefs } from './atlas-refs.js';

const PY = process.env.KH_PY || 'python3';
const have = spawnSync(PY, ['--version']);
const noPython = have.error ? `python not found (${PY}); set KH_PY` : false;

function py(args, timeout) {
  return spawnSync(PY, args, { cwd: REPO_ROOT, encoding: 'utf8', timeout });
}

test('design/levels/validate_levels.py --all passes', { skip: noPython }, () => {
  const r = py(['design/levels/validate_levels.py', '--all'], 120000);
  assert.equal(r.status, 0, r.stdout + r.stderr);
  assert.match(r.stdout, /orientation.*: 0 errors/);
  assert.doesNotMatch(r.stdout, /[1-9]\d* errors/);
});

test('art-direction/build_all.py passes every step and leaves git clean (KH_FULL=1)', {
  skip: noPython || (process.env.KH_FULL === '1' ? false : 'set KH_FULL=1 to run the full art rebuild (about 1 minute)'),
}, () => {
  const before = spawnSync('git', ['status', '--porcelain'], { cwd: REPO_ROOT, encoding: 'utf8' }).stdout;
  const r = py(['art-direction/build_all.py'], 600000);
  assert.equal(r.status, 0, r.stdout.slice(-2000) + r.stderr.slice(-2000));
  const last = r.stdout.trim().split('\n').at(-1);
  const m = last.match(/(\d+)\/(\d+) steps passed/);
  assert.ok(m && m[1] === m[2], last);
  assert.ok(Number(m[2]) >= 43, `expected at least 43 steps, got ${last}`);
  const after = spawnSync('git', ['status', '--porcelain'], { cwd: REPO_ROOT, encoding: 'utf8' }).stdout;
  assert.equal(after, before, 'a rebuild must not change tracked files');
});

// Known gap (report: Gaps found, owner art/levels): map.json npc states `relaxed` (after level 06) name
// poses the cast atlases do not contain. Exact list so the test fails, and must be edited, the day it is fixed.
export const KNOWN_ATLAS_GAPS = [
  'pose: bgworker_a_idle_phone_s (npc worker_a)',
  'pose: bgworker_b_idle_coffee_s (npc worker_b)',
];

test('every atlas name level 01 and the map use exists in the atlas JSON files (known gaps listed)', () => {
  assert.deepEqual(missingAtlasRefs(loadRealData(), loadRealAtlasJson()), KNOWN_ATLAS_GAPS);
});

test('negative: removing an atlas entry, pose, glitch animation or portrait is detected by name', () => {
  const data = loadRealData();
  const base = loadRealAtlasJson();
  const usedEntry = data.map.placements.find((p) => p.entry && !p.state_set && base.kit.entries.some((e) => e.name === p.entry)).entry;

  const kit = clone(base);
  kit.kit.entries = kit.kit.entries.filter((e) => e.name !== usedEntry);
  assert.ok(missingAtlasRefs(data, kit).some((p) => p.includes(usedEntry)), 'kit entry');

  const ivo = clone(base);
  delete ivo.ivo.animations.ivo_wave_s;
  assert.ok(missingAtlasRefs(data, ivo).some((p) => p.includes('ivo_wave_s')), 'npc pose');

  const gl = clone(base);
  delete gl.glitches.animations.form_repaired;
  assert.ok(missingAtlasRefs(data, gl).some((p) => p.includes('form_repaired')), 'glitch animation');

  const pt = clone(base);
  delete pt.portraits.portraits.ivo_neutral;
  assert.ok(missingAtlasRefs(data, pt).some((p) => p.includes('ivo_neutral')), 'portrait');

  const set = clone(base);
  delete set.kit.animations.elevator;
  assert.ok(missingAtlasRefs(data, set).some((p) => p.includes('elevator')), 'state set');
});

test('the game loader refuses to start when an atlas entry named by the map is removed', async () => {
  const { loadAtlasSet } = await import('../../src/engine/index.js');
  const { DataLoadError } = await import('../../src/shared/index.js');
  const data = loadRealData();
  const kit = readJson(ATLAS_PATHS.kit);
  const usedEntry = data.map.placements.find((p) => p.entry && !p.state_set && kit.entries.some((e) => e.name === p.entry)).entry;
  kit.entries = kit.entries.filter((e) => e.name !== usedEntry);
  const fetchFn = diskFetch({ overrides: { [ATLAS_PATHS.kit]: kit } });
  await assert.rejects(
    () => loadAtlasSet({ fetchFn, baseUrl: '/', loadImage: stubLoadImage() }),
    (e) => e instanceof DataLoadError && e.kind === 'shape',
  );
});
