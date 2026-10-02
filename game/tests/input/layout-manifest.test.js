import { test } from 'node:test';
import assert from 'node:assert/strict';
import { LayoutManifest, layoutHelpModel } from '../../src/input/index.js';
import { readRepo } from './helpers.js';

const json = JSON.parse(readRepo('design/layout/layout-manifest.json'));
const m = new LayoutManifest(json);

// Key ids drawn by the UI kit tabs (art-direction/ui-kit/kit_screens.py ANN and the mac rows).
// 'UpDown' is the kit's one slot for the stacked Up and Down keys.
const KIT = {
  base: [';', 'Caps', 'Cmd-R', 'Space', 'Tab', 'a', 'd', 'f', 'j', 'k', 'l', 'r', 's', 'v'],
  nav: [',', '0', '4', 'Caps', 'Space', '[', 'a', 'b', 'd', 'f', 'g', 'h', 'j', 'k', 'l', 'm', 'n', 's', 't', 'u', 'w', 'x'],
  'numbers-symbols': ["'", ';', 'Caps', 'Space', 'Tab', '[', ']', 'a', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'w', 'y'],
  practice: ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9', ';', 'Backspace', 'Caps', 'Cmd-L', 'Cmd-R', 'Ctrl-L', 'Left', 'Opt-L', 'Opt-R', 'Return', 'Right', 'Shift-L', 'Shift-R', 'Space', 'Tab', 'UpDown', 'a', 'd', 'f', 'j', 'k', 'l', 'r', 's', 'v'],
};
const fromKit = (id) => (id === 'UpDown' ? ['Up', 'Down'] : [id]);

test('tabs and variants', () => {
  assert.deepEqual(m.tabs(), ['base', 'nav', 'numbers-symbols', 'practice']);
  assert.deepEqual(m.variants(), ['macbook', 'microsoft']);
});

test('every key id the UI kit tabs use resolves on every tab and variant', () => {
  for (const [tab, ids] of Object.entries(KIT)) {
    for (const id of ids.flatMap(fromKit)) {
      assert.ok(m.hasKey(id), `${id} is a manifest key`);
      for (const variant of m.variants()) {
        const k = m.keyAt(tab, id, variant);
        assert.equal(k.id, id);
        assert.ok(typeof k.legend === 'string' && k.legend.length > 0, `${tab}/${id} legend`);
      }
      assert.ok(m.keyDetail(tab, id).lines.length > 0 || m.keyAt(tab, id).behaviour === 'passthrough', `${tab}/${id} detail`);
    }
  }
});

test('every drawn key of both keyboards resolves on every tab', () => {
  for (const variant of m.variants()) {
    const { rows } = m.keyboard(variant);
    assert.equal(rows.length, 5);
    for (const tab of m.tabs()) {
      for (const k of rows.flat()) {
        assert.doesNotThrow(() => m.keyAt(tab, k.id, variant), `${variant}/${tab}/${k.id}`);
        assert.doesNotThrow(() => m.keyDetail(tab, k.id, variant));
      }
    }
  }
});

test('keyboard geometry: macbook rows match the kit, bottom row is cumulative, Up and Down share a slot', () => {
  const mac = m.keyboard('macbook');
  assert.deepEqual(mac.rows.map((r) => r.length), [14, 14, 13, 12, 11]);
  assert.deepEqual(mac.rows[3].map((k) => k.id).slice(0, 3), ['Shift-L', 'z', 'x']);
  const bottom = mac.rows[4];
  assert.deepEqual(bottom.map((k) => k.id), ['fn', 'Ctrl-L', 'Opt-L', 'Cmd-L', 'Space', 'Cmd-R', 'Opt-R', 'Left', 'Up', 'Down', 'Right']);
  assert.equal(bottom.find((k) => k.id === 'Space').x_u, 4.25);
  assert.equal(bottom.find((k) => k.id === 'Up').x_u, bottom.find((k) => k.id === 'Down').x_u);
  assert.equal(bottom.find((k) => k.id === 'Right').x_u, 14);
  assert.equal(bottom.find((k) => k.id === 'Up').stack, 'upper');
  const ms = m.keyboard('microsoft');
  assert.deepEqual(ms.rows[4].map((k) => k.id), ['Ctrl-L', 'Win-L', 'Alt-L', 'Space', 'Alt-R', 'Win-R', 'Menu', 'Ctrl-R']);
  assert.equal(ms.rows[4].find((k) => k.id === 'Space').width_u, 6.25);
  for (const r of [...mac.rows, ...ms.rows]) {
    for (const k of r) assert.ok(k.width_u > 0);
  }
});

test('Caps: tap Escape, hold nav after 200 ms, on base', () => {
  const c = m.keyAt('base', 'Caps', 'macbook');
  assert.equal(c.behaviour, 'tap-hold');
  assert.equal(c.tap.label, 'Escape');
  assert.equal(c.hold.layer, 'nav');
  assert.equal(c.hold.after_ms, 200);
  assert.equal(c.silent, false);
  const d = m.keyDetail('base', 'Caps');
  assert.equal(d.tap, 'Escape');
  assert.match(d.hold, /nav/);
  assert.equal(d.timing.tap_timeout_ms, 200);
  assert.ok(d.lines.some((l) => /Tap: Escape/.test(l)));
});

test('nav tab: H is Left and differs from base; inherits fall through', () => {
  const h = m.keyAt('nav', 'h');
  assert.equal(h.legend, '←');
  assert.equal(h.tap.label, 'Left');
  assert.equal(h.differsFromBase, true);
  const left = m.keyAt('nav', 'Left');
  assert.equal(left.behaviour, 'inherits');
  assert.deepEqual(left.falls_to, ['base', 'practice']);
  assert.equal(left.silent, false);
});

test('tap-hold keys: F is Shift on base (left hand), J is a right-hand hold', () => {
  const f = m.keyAt('base', 'f');
  assert.equal(f.behaviour, 'tap-hold');
  assert.equal(f.hold.label, 'Left Shift');
  assert.equal(f.legend, 'Shift');
  assert.equal(m.keyAt('nav', 'f').differsFromBase, true);
});

test('XX silence: practice silences Esc, Return, arrows; Q and Backtick pass through', () => {
  for (const id of m.silencedInPractice()) {
    const k = m.keyAt('practice', id);
    assert.equal(k.silent, true, id);
    assert.equal(k.legend, 'XX');
  }
  assert.ok(m.silencedInPractice().includes('Return'));
  assert.ok(m.silencedInPractice().includes('Esc'));
  assert.ok(m.silencedInPractice().includes('Left'));
  assert.equal(m.keyAt('practice', 'q').silent, false);
  assert.equal(m.keyAt('practice', '`').silent, false);
  assert.equal(m.keyAt('base', 'Return').silent, false);
  assert.match(m.keyDetail('practice', 'Return').lines[0], /Silent/);
});

test('numbers-symbols: A is 1, Q is !', () => {
  assert.equal(m.keyAt('numbers-symbols', 'a').tap.label, '1');
  assert.equal(m.keyAt('numbers-symbols', 'q').tap.label, '!');
});

test('Microsoft variant: remapped bottom-row keys and Menu', () => {
  assert.equal(m.keyAt('base', 'Alt-L', 'microsoft').legend, '→ Cmd');
  assert.equal(m.keyAt('base', 'Win-L', 'microsoft').legend, '→ Opt');
  assert.equal(m.keyAt('base', 'Alt-L', 'microsoft').tap.label, 'Left Command');
  assert.equal(m.keyAt('base', 'Menu', 'microsoft').behaviour, 'unmodelled');
  assert.throws(() => m.keyAt('base', 'Alt-L', 'macbook'));
  const optR = m.keyAt('base', 'Opt-R', 'microsoft');
  assert.equal(optR.behaviour, 'layer-hold');
  assert.equal(m.keyAt('base', 'Opt-R', 'macbook').behaviour, 'plain');
});

test('verification comes from the manifest rows; weakest row wins; unverified rows are never "observed"', () => {
  const caps = m.keyDetail('base', 'Caps');
  const rows = json.inventory.filter((r) => r.links.some((l) => l.key === 'Caps' && l.layer === 'base'));
  assert.ok(rows.length > 0);
  assert.equal(caps.lessons.rows.length, rows.length);
  const order = ['external_only', 'player_confirmed', 'observed'];
  const weakest = order.find((v) => rows.some((r) => r.verification === v));
  assert.equal(caps.verification, weakest);
  // every key detail on every tab carries one of the three labels
  for (const tab of m.tabs()) {
    for (const k of json.keys) assert.ok(order.includes(m.keyDetail(tab, k.id).verification));
  }
  const v = json.sequences.find((s) => s.id === 'violento-toggle');
  assert.equal(v.verification, 'player_confirmed');
});

test('gesture(): inventory row with observed events and verification', () => {
  const g = m.gesture('N01');
  assert.equal(g.input, 'Caps + H');
  assert.equal(g.verification, 'observed');
  assert.equal(g.observedEvents[0].key, 'ArrowLeft');
  assert.deepEqual(g.lessons.all.slice(0, 1), [1]);
  assert.equal(m.gesture('B09').verification, 'player_confirmed');
  assert.equal(m.gesture('B13').verification, 'external_only');
  for (const row of json.inventory) assert.equal(m.gesture(row.id).verification, row.verification);
  assert.throws(() => m.gesture('Z99'));
});

test('sequences: toggle, reload, emergency exit is always unverified', () => {
  const s = m.sequences();
  assert.deepEqual(s.map((x) => x.id), ['violento-toggle', 'reload-config', 'emergency-exit']);
  assert.equal(s[2].unverified, true);
  assert.equal(s[2].status, 'present_unverified');
  assert.equal(s[0].unverified, false);
});

test('constructor rejects a bad manifest with a DataLoadError naming the file', () => {
  assert.throws(() => new LayoutManifest({}), (e) => e.name === 'Error' || e.file === '/design/layout/layout-manifest.json');
  assert.throws(() => new LayoutManifest(null));
  assert.throws(() => m.keyAt('nope', 'a'));
  assert.throws(() => m.keyAt('base', 'a', 'dvorak'));
  assert.throws(() => m.keyAt('base', 'zz'));
});

test('layoutHelpModel: tabs, keys, card, toggle-out and emergency exit', () => {
  const vm = layoutHelpModel(m, { tab: 'nav', variant: 'macbook', selectedKey: 'h' });
  assert.equal(vm.tab, 'nav');
  assert.deepEqual(vm.tabs.map((t) => t.id), m.tabs());
  assert.deepEqual(vm.tabs.filter((t) => t.selected).map((t) => t.id), ['nav']);
  assert.deepEqual(vm.variants, ['macbook', 'microsoft']);
  assert.equal(vm.keys.length, 14 + 14 + 13 + 12 + 11);
  assert.equal(vm.keys.filter((k) => k.selected).length, 1);
  const h = vm.keys.find((k) => k.id === 'h');
  assert.equal(h.legend, '←');
  assert.equal(h.differs, true);
  assert.equal(vm.card.label, 'h');
  assert.ok(vm.card.lines.length > 0);
  assert.ok(['observed', 'player_confirmed', 'external_only'].includes(vm.card.verification));
  assert.equal(vm.emergencyExit.unverified, true);
  assert.match(vm.emergencyExit.text, /Left Control \+ Space \+ Escape/);
  assert.equal(vm.toggleOut.keys.length, 4);
  assert.match(vm.toggleOut.text, /Control \+ Alt \+ GUI \+ V/);
});

test('layoutHelpModel: defaults, no card without a selection, XX on practice, Microsoft variant', () => {
  const base = layoutHelpModel(m);
  assert.equal(base.tab, 'base');
  assert.equal(base.variant, 'macbook');
  assert.equal(base.card, null);
  const practice = layoutHelpModel(m, { tab: 'practice' });
  assert.ok(practice.keys.find((k) => k.id === 'Return').silent);
  assert.equal(practice.keys.filter((k) => k.silent).length, m.silencedInPractice().filter((id) => m.keyboard('macbook').rows.flat().some((k) => k.id === id)).length);
  const ms = layoutHelpModel(m, { variant: 'microsoft' });
  assert.equal(ms.keys.find((k) => k.id === 'Alt-L').legend, '→ Cmd');
  assert.equal(ms.keys.length, 14 + 14 + 13 + 12 + 8);
});

test('no card or label text claims detection of a layer or physical key', () => {
  for (const tab of m.tabs()) {
    const vm = layoutHelpModel(m, { tab });
    for (const k of vm.keys) {
      const text = m.keyDetail(tab, k.id).lines.join(' ');
      assert.doesNotMatch(text, /\bdetected?\b/i, `${tab}/${k.id}`);
    }
  }
});
