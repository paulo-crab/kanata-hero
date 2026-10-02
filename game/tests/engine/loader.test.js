import { test } from 'node:test';
import assert from 'node:assert/strict';
import { DataLoadError } from '../../src/shared/index.js';
import { loadGameData, loadJson, loadAtlasSet, DATA_FILES, ATLAS_FILES } from '../../src/engine/index.js';
import { fsFetch, opts, stubImage, realData } from './helpers.js';

const fakeFetch = (files) => async (url) => {
  if (!(url in files)) return { ok: false, status: 404, text: async () => '' };
  return { ok: true, status: 200, text: async () => files[url] };
};

test('the real data files load', async () => {
  const d = await loadGameData(opts);
  assert.equal(d.district.id, 'orientation');
  assert.equal(d.map.size_cells[0], 28);
  assert.equal(d.level.id, 'orientation-01');
  assert.ok(d.world.state_ids);
  assert.ok(d.layoutManifest);
  assert.ok(d.gestureInventory);
});

test('missing file names the file', async () => {
  await assert.rejects(() => loadJson('/nope.json', opts), (e) => e instanceof DataLoadError && e.kind === 'missing' && /\/nope\.json/.test(e.message));
});

test('a throwing fetch is a missing error', async () => {
  const fetchFn = async () => { throw new Error('offline'); };
  await assert.rejects(() => loadJson('/x.json', { fetchFn }), (e) => e.kind === 'missing' && /offline/.test(e.message));
});

test('broken JSON is a parse error naming the file', async () => {
  await assert.rejects(() => loadJson('/bad.json', { fetchFn: fakeFetch({ '/bad.json': '{oops' }) }), (e) => e.kind === 'parse' && e.file === '/bad.json');
});

test('loadGameData rejects a wrong shape and names that file', async () => {
  const real = {};
  for (const p of Object.values(DATA_FILES)) real[p] = (await (await fsFetch(p)).text());
  const broken = { ...real, [DATA_FILES.map]: JSON.stringify({ size_cells: [28, 18] }) };
  await assert.rejects(() => loadGameData({ fetchFn: fakeFetch(broken) }), (e) => e.kind === 'shape' && e.file === DATA_FILES.map);
  const missing = { ...real };
  delete missing[DATA_FILES.world];
  await assert.rejects(() => loadGameData({ fetchFn: fakeFetch(missing) }), (e) => e.kind === 'missing' && e.file === DATA_FILES.world);
});

test('a grid row of the wrong width is a shape error', async () => {
  const real = {};
  for (const p of Object.values(DATA_FILES)) real[p] = (await (await fsFetch(p)).text());
  const map = JSON.parse(real[DATA_FILES.map]);
  map.collision[3] = map.collision[3].slice(1);
  real[DATA_FILES.map] = JSON.stringify(map);
  await assert.rejects(() => loadGameData({ fetchFn: fakeFetch(real) }), (e) => e.kind === 'shape' && e.file === DATA_FILES.map);
});

test('baseUrl is prefixed to every path', async () => {
  const seen = [];
  const fetchFn = async (u) => { seen.push(u); return fsFetch(u.replace('/game-root', '')); };
  await loadJson(DATA_FILES.world, { fetchFn, baseUrl: '/game-root/' });
  assert.deepEqual(seen, ['/game-root' + DATA_FILES.world]);
});

test('every atlas loads and the map resolves against it', async () => {
  const { atlases } = await realData();
  for (const id of Object.keys(ATLAS_FILES)) assert.ok(atlases.image(id), id);
  assert.ok(atlases.kitEntry('floor_j'));
  assert.ok(atlases.portrait('ivo_neutral'));
});

test('a map naming an unknown entry fails with the map file', async () => {
  const { data } = await realData();
  const map = structuredClone(data.map);
  map.placements.push({ id: 'ghost', entry: 'no_such_entry', cell: [1, 1] });
  await assert.rejects(() => loadAtlasSet({ ...opts, loadImage: stubImage, map }), (e) => e.kind === 'shape' && e.file === DATA_FILES.map && /no_such_entry/.test(e.message));
});

test('a broken atlas json names the atlas file', async () => {
  const fetchFn = async (u) => {
    if (u === ATLAS_FILES.ivo.json) return { ok: true, status: 200, text: async () => '{"frame":{"w":16,"h":24}}' };
    return fsFetch(u);
  };
  await assert.rejects(() => loadAtlasSet({ fetchFn, loadImage: stubImage }), (e) => e.kind === 'shape' && e.file === ATLAS_FILES.ivo.json);
});

test('an image that fails to load names the png', async () => {
  const loadImage = async () => { throw new Error('boom'); };
  await assert.rejects(() => loadAtlasSet({ ...opts, loadImage }), (e) => e.file === ATLAS_FILES.kit.png);
});
