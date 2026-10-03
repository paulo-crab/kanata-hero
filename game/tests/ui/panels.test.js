// Playtest 1, item 1: the panel rectangles the camera keeps clear match the CSS (dialogue strip, inset).
import { test } from 'node:test';
import assert from 'node:assert/strict';
import { DIALOGUE_RECTS, HUD_CHIPS_RECT, panelRects } from '../../src/ui/panels.js';
import { INSET_STAGE_RECT, STAGE_W, STAGE_H } from '../../src/shared/layout.js';
import { DIALOGUE_STAGE_RECT } from '../../src/ui/world-space.js';
import { read } from './fixtures.js';

const rule = (css, sel) => new RegExp(`${sel.replace(/\./g, '\\.')}\\s*\\{([^}]*)\\}`).exec(css)[1];

test('the dialogue rectangles sit beside the inset, inside the stage margin, at most 160 px tall', () => {
  const css = read('game/css/components.css');
  const dlg = rule(css, '.kh-dialogue');
  const maxW = Number(/max-width:\s*(\d+)px/.exec(dlg)[1]);
  const maxH = Number(/max-height:\s*(\d+)px/.exec(dlg)[1]);
  for (const r of Object.values(DIALOGUE_RECTS)) {
    assert.ok(r.x >= INSET_STAGE_RECT.x + INSET_STAGE_RECT.w, 'beside the inset, never over it');
    assert.equal(r.x + r.w, STAGE_W - 16, 'docked to the right margin');
    assert.equal(r.y + r.h, STAGE_H - 16, 'docked to the bottom margin');
    assert.ok(r.w >= maxW && r.h <= 160);
  }
  assert.ok(maxH <= 160);
  assert.deepEqual({ ...DIALOGUE_STAGE_RECT }, { ...DIALOGUE_RECTS.conversation });
  assert.ok(HUD_CHIPS_RECT.x + HUD_CHIPS_RECT.w <= STAGE_W - 16);
});

test('a dialogue vm adds the dialogue rectangle by mode; the inset adds the contract rectangle', () => {
  const a = panelRects({ 'vm:dialogue': { mode: 'conversation' }, 'vm:inset': {} });
  assert.deepEqual(a.panels.map((p) => p.id), ['dialogue', 'inset']);
  assert.equal(a.panels[0].h, 160);
  assert.equal(a.panels[1].y, INSET_STAGE_RECT.y);
  const b = panelRects({ 'vm:dialogue': { mode: 'instruction' }, 'vm:inset': {}, 'vm:settings-flags': { largerText: true } });
  assert.equal(b.panels[0].h, 128);
  assert.ok(b.panels[1].y < INSET_STAGE_RECT.y, 'larger text grows the inset upward');
});
