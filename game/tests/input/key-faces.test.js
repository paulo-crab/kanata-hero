// Layout help key faces (playtest 1, item 3): short sub-labels, no 1u key carries a long legend.
import { test } from 'node:test';
import assert from 'node:assert/strict';
import { LayoutManifest, layoutHelpModel, keyFace, shortLegend } from '../../src/input/index.js';
import { readRepo } from './helpers.js';

const m = new LayoutManifest(JSON.parse(readRepo('design/layout/layout-manifest.json')));

test('short legends: arrows glue to the word, long manifest labels drop off 1u keys, the card keeps the full text', () => {
  assert.equal(shortLegend('Word →'), 'Word→');
  assert.equal(shortLegend('Page ↑'), 'Page↑');
  assert.equal(shortLegend('Esc | nav'), 'Esc/nav');
  assert.deepEqual(keyFace('Ctrl-L'), { name: 'Ctrl', side: 'L' });
  assert.deepEqual(keyFace('Down'), { name: '↓', side: null });
  for (const variant of ['macbook', 'microsoft']) {
    for (const tab of m.tabs()) {
      const vm = layoutHelpModel(m, { tab, variant });
      for (const k of vm.keys) {
        if (k.width_u < 3) assert.ok(k.short.length <= 8, `${variant}/${tab}/${k.id}: "${k.short}" is too long for a ${k.width_u}u key`);
        assert.ok(k.name.length <= 6, `${k.id} face ${k.name}`);
      }
    }
  }
  const nav = layoutHelpModel(m, { tab: 'nav' });
  assert.equal(nav.keys.find((k) => k.id === 'w').short, 'Word→');
  assert.equal(nav.keys.find((k) => k.id === 'w').legend, 'Word →', 'the full legend stays in the view-model');
  const up = nav.keys.find((k) => k.id === 'Up');
  const down = nav.keys.find((k) => k.id === 'Down');
  assert.equal(up.stack, 'upper');
  assert.equal(down.stack, 'lower');
  assert.equal(up.x_u, down.x_u, 'Up and Down share one slot');
});
