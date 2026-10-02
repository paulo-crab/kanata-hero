import { test } from 'node:test';
import assert from 'node:assert/strict';
import { BINDINGS, resolveAction, interpretKey } from '../../src/input/index.js';
import { ev, ctx, HUB, DIALOGUE, LABEL, readRepo } from './helpers.js';

function resolve(rawKey, extra, context) {
  const i = interpretKey(ev(rawKey, extra), extra && extra.phase === 'up' ? 'up' : 'down', 0);
  return resolveAction(i, context);
}

// The Decisions table of design/ui-key-bindings.md, parsed from the real file.
function tableRows() {
  const md = readRepo('design/ui-key-bindings.md');
  const start = md.indexOf('| Action | Key (observed output)');
  const lines = md.slice(start).split('\n');
  const rows = [];
  for (const line of lines.slice(2)) {
    if (!line.startsWith('|')) break;
    const cells = line.split('|').slice(1, -1).map((c) => c.trim());
    rows.push({ action: cells[0], key: cells[1], gesture: cells[2] });
  }
  return rows;
}

const strip = (s) => s.replace(/\*\*/g, '').replace(/`/g, '').replace(/\s+/g, ' ').trim();

test('BINDINGS has one row per row of the markdown table, in order, with the same gesture text', () => {
  const rows = tableRows();
  assert.equal(rows.length, 11);
  assert.equal(BINDINGS.length, rows.length);
  rows.forEach((r, i) => {
    assert.equal(strip(BINDINGS[i].row), strip(r.action), `row ${i} action`);
    assert.equal(strip(BINDINGS[i].gesture), strip(r.gesture), `row ${i} gesture`);
  });
  assert.equal(new Set(BINDINGS.map((b) => b.id)).size, BINDINGS.length);
});

// One test per row of the table.
const ROW_TESTS = {
  interact() {
    assert.deepEqual(resolve('Enter', {}, ctx(HUB)), { action: 'interact', dir: null });
  },
  continue() {
    assert.deepEqual(resolve('Enter', {}, ctx(DIALOGUE)), { action: 'continue', dir: null });
    assert.deepEqual(resolve('Enter', {}, ctx({ enter: 'confirm' })), { action: 'confirm', dir: null });
  },
  skip() {
    assert.deepEqual(resolve('Escape', {}, ctx(DIALOGUE)), { action: 'skip', dir: null });
  },
  back() {
    assert.deepEqual(resolve('Escape', {}, ctx({ esc: 'back' })), { action: 'back', dir: null });
    assert.deepEqual(resolve('Escape', {}, ctx(LABEL)), { action: 'back', dir: null });
  },
  move() {
    const dirs = { ArrowUp: 'n', ArrowDown: 's', ArrowLeft: 'w', ArrowRight: 'e' };
    for (const [k, d] of Object.entries(dirs)) {
      assert.deepEqual(resolve(k, {}, ctx(HUB)), { action: 'move', dir: d });
      assert.deepEqual(resolve(k, {}, ctx({ arrows: 'choose' })), { action: 'choose', dir: d });
    }
    assert.equal(resolve('ArrowLeft', {}, ctx(LABEL)).action, null); // text in typing scenes
  },
  hint() {
    assert.deepEqual(resolve('`', { code: 'Backquote' }, ctx(HUB)), { action: 'hint', dir: null });
    assert.equal(resolve('`', { code: 'Backquote' }, ctx({ ...HUB, hint: false })).action, null);
    // keyed by code: a dead-key input source still reaches Hint
    assert.equal(resolve('Dead', { code: 'Backquote', keyCode: 229 }, ctx(HUB)).action, 'hint');
    assert.equal(resolve('`', { code: 'Backquote' }, ctx(LABEL)).action, 'hint'); // live in typing scenes
  },
  journal() {
    assert.deepEqual(resolve('q', {}, ctx(HUB)), { action: 'journal', dir: null });
    assert.equal(resolve('Q', { shiftKey: true }, ctx(HUB)).action, null); // Shift held: modifier-free only
    assert.equal(resolve('Q', {}, ctx(HUB)).action, 'journal'); // Caps Lock gives 'Q' without Shift
    assert.equal(resolve('q', {}, ctx({ ...HUB, journal: false })).action, null);
  },
  'layout-help'() {
    assert.deepEqual(resolve('?', { shiftKey: true }, ctx(HUB)), { action: 'layoutHelp', dir: null });
    assert.equal(resolve('?', { shiftKey: true }, ctx(LABEL)).action, 'layoutHelp'); // typing scenes too
    assert.equal(resolve('?', { shiftKey: true }, ctx(DIALOGUE)).action, 'layoutHelp');
    assert.equal(resolve('?', { shiftKey: true, metaKey: true }, ctx(HUB)).action, null);
    assert.equal(resolve('?', { shiftKey: true }, ctx({ ...HUB, layoutHelp: false })).action, null);
  },
  'elevator-open'() {
    assert.deepEqual(resolve('Enter', {}, ctx(HUB)), { action: 'interact', dir: null });
  },
  'elevator-pick'() {
    const floors = ctx({ enter: 'confirm', esc: 'back', arrows: 'choose' });
    assert.deepEqual(resolve('ArrowUp', {}, floors), { action: 'choose', dir: 'n' });
    assert.deepEqual(resolve('ArrowDown', {}, floors), { action: 'choose', dir: 's' });
    assert.deepEqual(resolve('Enter', {}, floors), { action: 'confirm', dir: null });
    assert.deepEqual(resolve('Escape', {}, floors), { action: 'back', dir: null });
  },
  retry() {
    assert.deepEqual(resolve('Enter', {}, ctx({ enter: 'retry', esc: 'back', typing: true })), { action: 'retry', dir: null });
    // while the editor has focus (no wrong result) Return is text
    assert.equal(resolve('Enter', {}, ctx(LABEL)).action, null);
  },
};

for (const b of BINDINGS) {
  test(`binding row: ${b.id}`, () => {
    assert.ok(ROW_TESTS[b.id], `no test for row ${b.id}`);
    ROW_TESTS[b.id]();
  });
}

test('every row id has a test and no test is orphaned', () => {
  assert.deepEqual(Object.keys(ROW_TESTS).sort(), BINDINGS.map((b) => b.id).sort());
});

test('Q typed in a label scene is text and the journal does not open', () => {
  const i = interpretKey(ev('q'), 'down', 0);
  assert.equal(i.text, 'q');
  assert.equal(resolveAction(i, ctx({ ...LABEL, journal: true })).action, null); // even if a scene wrongly sets journal
  assert.equal(resolveAction(i, ctx(LABEL)).action, null);
});

test('Esc in the open world does nothing', () => {
  assert.deepEqual(resolve('Escape', {}, ctx(HUB)), { action: null, dir: null });
});

test('Backquote and ? are never delivered as text', () => {
  assert.equal(interpretKey(ev('`', { code: 'Backquote' })).text, null);
  assert.equal(interpretKey(ev('?', { shiftKey: true })).text, null);
});

test('Tab and Space never resolve to an action, in any context', () => {
  for (const c of [HUB, DIALOGUE, LABEL, { enter: 'confirm', esc: 'back', arrows: 'choose', journal: true, hint: true }]) {
    for (const [k, code] of [['Tab', 'Tab'], [' ', 'Space']]) {
      assert.equal(resolve(k, { code }, ctx(c)).action, null, `${k} in ${c.sceneId}`);
      assert.equal(resolve(k, { code, shiftKey: true }, ctx(c)).action, null);
    }
  }
});

test('modifiers: Command, Control, Option or Shift cancel Q, Backquote, Return, Esc and arrows', () => {
  const all = ctx({ enter: 'interact', esc: 'back', arrows: 'move', journal: true, hint: true });
  const keys = [['q', {}], ['`', { code: 'Backquote' }], ['Enter', {}], ['Escape', {}], ['ArrowLeft', {}]];
  for (const mod of ['metaKey', 'ctrlKey', 'altKey', 'shiftKey']) {
    for (const [k, extra] of keys) {
      assert.equal(resolve(k, { ...extra, [mod]: true }, all).action, null, `${k} with ${mod}`);
    }
  }
});

test('repeat and key-up never act; null context resolves nothing', () => {
  assert.equal(resolve('Enter', { repeat: true }, ctx(HUB)).action, null);
  const up = interpretKey(ev('Enter'), 'up', 0);
  assert.equal(resolveAction(up, ctx(HUB)).action, null);
  assert.equal(resolveAction(interpretKey(ev('Enter'), 'down', 0), null).action, null);
});

test('Return by state: the same key is interact, continue, confirm or retry', () => {
  for (const state of ['interact', 'continue', 'confirm', 'retry']) {
    assert.equal(resolve('Enter', {}, ctx({ enter: state })).action, state);
  }
  for (const state of ['text', 'none']) assert.equal(resolve('Enter', {}, ctx({ enter: state })).action, null);
});

test('typing scene: only ? and Backquote are commands', () => {
  const typing = ctx({ typing: true, enter: 'text', esc: 'text', arrows: 'text', journal: true, hint: true });
  assert.equal(resolve('q', {}, typing).action, null);
  assert.equal(resolve('Enter', {}, typing).action, null);
  assert.equal(resolve('a', {}, typing).action, null);
  assert.equal(resolve('`', { code: 'Backquote' }, typing).action, 'hint');
  assert.equal(resolve('?', { shiftKey: true }, typing).action, 'layoutHelp');
});
