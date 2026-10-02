import { test } from 'node:test';
import assert from 'node:assert/strict';
import { HintGate, HINT_CARD_TEXT, CONFIDENCE_LABELS, confidenceLabel, weakestConfidence } from '../../src/input/index.js';

test('guided: recorded at once, no card, no star lost', () => {
  const g = new HintGate();
  assert.deepEqual(g.request({ sceneId: 'o01-loop', phase: 'guided' }), { needsCard: false });
  assert.deepEqual(g.uses(), [{ sceneId: 'o01-loop', phase: 'guided', forfeitsStar: false }]);
  assert.equal(g.forfeited('o01-loop'), false);
  assert.equal(g.confirm(), null);
});

test('variation: same as guided', () => {
  const g = new HintGate();
  assert.equal(g.request({ sceneId: 's', phase: 'variation' }).needsCard, false);
  assert.equal(g.uses()[0].forfeitsStar, false);
});

test('recall: card first, nothing recorded until Return confirms, then the star is forfeited', () => {
  const g = new HintGate();
  const r = g.request({ sceneId: 'o01-recall', phase: 'recall' });
  assert.equal(r.needsCard, true);
  assert.equal(r.card.text, HINT_CARD_TEXT);
  assert.equal(r.card.confirmKey, 'Enter');
  assert.deepEqual(g.uses(), []);
  assert.equal(g.forfeited('o01-recall'), false);
  assert.deepEqual(g.pending, { sceneId: 'o01-recall', phase: 'recall' });
  const use = g.confirm();
  assert.deepEqual(use, { sceneId: 'o01-recall', phase: 'recall', forfeitsStar: true });
  assert.equal(g.forfeited('o01-recall'), true);
  assert.equal(g.pending, null);
  assert.equal(g.uses().length, 1);
  assert.equal(g.confirm(), null);
});

test('recall: Esc on the card keeps the star and records nothing', () => {
  const g = new HintGate();
  g.request({ sceneId: 'r', phase: 'recall' });
  g.cancel();
  assert.deepEqual(g.uses(), []);
  assert.equal(g.confirm(), null);
  assert.equal(g.forfeited('r'), false);
});

test('card text says the star is forfeited and how to confirm or keep it', () => {
  assert.match(HINT_CARD_TEXT, /forfeits the third star/);
  assert.match(HINT_CARD_TEXT, /Return/);
  assert.match(HINT_CARD_TEXT, /Esc/);
});

test('a guided hint in another scene does not touch the recall forfeit', () => {
  const g = new HintGate();
  g.request({ sceneId: 'a', phase: 'guided' });
  g.request({ sceneId: 'b', phase: 'recall' });
  g.confirm();
  assert.equal(g.forfeited('a'), false);
  assert.equal(g.forfeited('b'), true);
});

test('invalid input and unsupported difficulty fail loudly; uses() is a copy', () => {
  const g = new HintGate();
  assert.throws(() => g.request({ sceneId: 'x', phase: 'boss' }));
  assert.throws(() => g.request({ phase: 'guided' }));
  assert.throws(() => new HintGate({ difficulty: 'violento' }));
  assert.doesNotThrow(() => new HintGate({ difficulty: 'standard' }));
  g.request({ sceneId: 'x', phase: 'guided' });
  g.uses()[0].forfeitsStar = true;
  assert.equal(g.uses()[0].forfeitsStar, false);
});

test('confidence labels: three, honest wording, weakest wins', () => {
  assert.deepEqual(Object.keys(CONFIDENCE_LABELS), ['observed', 'player_confirmed', 'external_only']);
  assert.equal(confidenceLabel('observed'), 'Observed output');
  assert.equal(confidenceLabel('external_only'), 'Not observable here');
  assert.throws(() => confidenceLabel('detected'));
  assert.equal(weakestConfidence(['observed', 'player_confirmed']), 'player_confirmed');
  assert.equal(weakestConfidence(['observed', 'external_only', 'player_confirmed']), 'external_only');
  assert.equal(weakestConfidence([]), 'observed');
});
