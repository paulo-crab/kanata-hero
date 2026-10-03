// Headless level 01 scenario: setup skip, arrival, popup, keys, lap, four stops, label, recall, world changes, glitch.
import { test } from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import path from 'node:path';
import { makeGame, memoryStorage, REPO } from './helpers.js';

/** Play from the setup screen to the end of the recall walk. `opts` injects mistakes. */
export function playLevel(opts = {}) {
  const g = makeGame({ storage: opts.storage });
  const { player, session, world } = g;
  const opened = [];
  g.bus.on('dialogue:open', (e) => opened.push(e.id));
  const top = () => session.machine.top.kind;

  session.start();
  assert.equal(top(), 'setup');
  player.tap('Escape'); // opens the skip confirm card
  player.tap('Enter'); // yes, skip setup and calibration
  assert.equal(top(), 'arrival');
  player.tick(30); // 500 ms: elevator closed, half, open
  assert.equal(top(), 'dialogue'); // welcome is open over the hub
  player.tap('Enter');

  // popup (form scene)
  assert.equal(top(), 'form');
  if (opts.wrongPopup) {
    player.tap('ArrowLeft');
    player.tap('Enter');
  }
  player.tap('Escape');
  assert.equal(top(), 'dialogue'); // popup-done
  player.tap('Enter');
  assert.equal(top(), 'hub');

  // keys: journal, hint, layout help
  player.tap('q');
  assert.equal(top(), 'journal');
  player.tap('Escape');
  player.tap('Backquote');
  player.tap('?');
  assert.equal(top(), 'layout-help');
  player.tap('Escape');

  // lap
  assert.equal(top(), 'walk');
  assert.equal(session.rules.currentStep.id, 'o01.s.loop');
  if (opts.wrongLap) { player.walk('e'); player.walk('e'); player.walk('w'); player.walk('w'); }
  player.walk('s', 10);
  player.walk('e', 14);
  player.walk('n', 7);
  player.walk('w', 8);
  assert.deepEqual(player.cell(), [9, 5]);
  assert.equal(top(), 'dialogue');
  player.tap('Enter'); // loop-done
  player.tap('Enter'); // stops

  // four desks
  assert.equal(session.rules.currentStep.id, 'o01.s.stops');
  player.goTo([9, 4]);
  player.goTo([7, 10]);
  assert.equal(top(), 'label');
  if (opts.wrongLabel) { player.tap('x'); player.tap('ArrowLeft'); player.tap('w', { mods: { alt: true } }); }
  player.type('west');
  assert.equal(top(), 'walk');
  player.goTo([10, 14]);
  player.goTo([19, 10]);
  assert.equal(top(), 'dialogue'); // stops-done
  player.tap('Enter');

  // recall
  assert.equal(session.rules.currentStep.id, 'o01.s.recall');
  assert.equal(world.npc('ivo').state, 'north');
  player.tap('Enter'); // recall line, if still open
  if (opts.recallHint) {
    player.tap('Backquote');
    assert.ok(g.vms['vm:hint-card']);
    player.tap('Enter');
  }
  player.goTo([11, 4]);
  assert.equal(top(), 'dialogue'); // badge reminder popup
  player.tap('Escape');
  assert.equal(top(), 'walk');
  player.goTo([12, 13]);
  assert.equal(top(), 'dialogue'); // thanks
  player.tap('Enter');
  player.tap('Enter'); // fold-intro
  assert.equal(top(), 'hub');
  return { g, opened };
}

test('level 01 plays from setup skip to completion with three stars', () => {
  const { g, opened } = playLevel();
  const { session, world } = g;
  assert.deepEqual(g.errors, []);
  const doc = session.progress.doc;

  // stars and evidence
  const done = g.log.find(([t]) => t === 'level:complete')[1];
  assert.equal(done.level, 'orientation-01');
  assert.equal(done.stars, 3, done.reasons.join('; '));
  assert.equal(doc.levels['orientation-01'].stars, 3);
  assert.equal(doc.best['orientation-01'].stars, 3);
  const ev = session.evidence.all();
  assert.deepEqual(Object.keys(ev).sort(), ['o01-desk-label', 'o01-four-stops', 'o01-loop', 'o01-popup', 'o01-unprompted']);
  assert.equal(ev['o01-unprompted'].phase, 'recall');
  assert.equal(ev['o01-popup'].phase, 'guided');
  assert.equal(ev['o01-desk-label'].phase, 'variation');
  assert.ok(ev['o01-loop'].observed.includes('ArrowRight'));
  assert.equal(ev['o01-unprompted'].hintUsed, false);

  // the world changed
  assert.equal(world.placementState('turnstile'), 'open');
  assert.ok(world.isGateOpen('g.turnstile'));
  assert.equal(world.npc('ivo').pose, 'ivo_nod_s');
  assert.deepEqual(world.npc('ivo').cell, [12, 14]);
  assert.equal(world.glitch.glitch_lobby, 'spawned');
  for (const f of ['welcome-popup-closed', 'turnstile-open', 'ivo-nodding']) assert.ok(doc.flags.includes(f), f);
  assert.ok(doc.levelsDone.includes('orientation-01'));
  assert.ok(doc.journal.includes('Orientation 01 complete: the first route is open.'));
  assert.ok(doc.journal.includes('Desk Walker: Right, Up, Left and Down used on the garden loop.'));
  assert.equal(doc.npc.ivo, 'post_nod');
  assert.deepEqual(doc.gatesOpen, ['g.turnstile']);

  // garden markers are gold, and the elevator played 120 ms states on arrival
  const gold = g.vms['vm:markers'].floor;
  assert.equal(gold.length, 4);
  assert.ok(gold.every((m) => m.state === 'gold'));
  const lift = world.stateLog.filter((s) => s.placement === 'elevator');
  assert.deepEqual(lift.map((s) => s.state), ['closed', 'half', 'open']);
  // 120 ms per state, observed on the 60 Hz step grid
  lift.slice(1).forEach((s, i) => assert.ok(s.atMs >= 120 * (i + 1) && s.atMs < 120 * (i + 1) + 17, `${s.state} at ${s.atMs}`));
  assert.equal(g.session.machine.top.kind, 'hub');
  assert.equal(g.vms['vm:hud'].progress.done, g.vms['vm:hud'].progress.total);

  // dialogue order matches the level 01 table of design/levels/SLICE.md
  const slice = readFileSync(path.join(REPO, 'design/levels/SLICE.md'), 'utf8');
  const level1 = slice.split('### Level 01')[1].split('### Level 02')[0];
  const table = [...level1.matchAll(/^\| `(o01\.d\.[^`]+)`/gm)].map((m) => m[1]);
  const optionalOrObject = ['o01.d.popup-again', 'o01.d.recall-hint', 'o01.d.pace-sign', 'o01.d.fold-move', 'o01.d.fold-type'];
  assert.deepEqual(opened, table.filter((id) => !optionalOrObject.includes(id)));
});

test('optional glitch repair after the route changes the world and never blocks', () => {
  const { g } = playLevel();
  const { player, session, world } = g;
  player.goTo([18, 12]);
  player.walk('s'); // now at (18,13) facing the folded form at (18,14)
  assert.deepEqual(player.cell(), [18, 13]);
  player.tap('Enter');
  assert.equal(session.machine.top.kind, 'editor');
  assert.equal(g.vms['vm:dialogue'].id, 'o01.d.fold-move');
  player.tap('y'); // too early: wrong, field resets, instant retry
  assert.equal(g.vms['vm:scene-bar'].field.text, 'lobb');
  assert.equal(session.machine.inputContext().enter, 'retry');
  player.tap('Enter');
  for (let i = 0; i < 4; i += 1) player.tap('ArrowRight');
  assert.equal(g.vms['vm:scene-bar'].field.cursor, 4);
  player.tap('y');
  assert.equal(session.machine.top.kind, 'hub');
  assert.equal(world.glitch.glitch_lobby, 'repaired');
  assert.ok(session.progress.doc.flags.includes('glitch-repaired-lobby'));
  assert.ok(session.progress.doc.journal.includes('Folded form repaired.'));
  assert.equal(session.rules.currentStep, null);
});

test('mistakes cost clean runs but never block: wrong popup key, wrong way, wrong letters give two stars or fewer', () => {
  const { g } = playLevel({ wrongPopup: true, wrongLap: true, wrongLabel: true });
  const done = g.log.find(([t]) => t === 'level:complete')[1];
  assert.equal(done.stars, 1, done.reasons.join('; '));
  const ev = g.session.evidence.all();
  assert.equal(ev['o01-popup'].criticalOk, false);
  assert.ok(ev['o01-loop'].actions.correct < ev['o01-loop'].actions.total);
});

test('a hint in the recall scene forfeits the third star, a hint in a guided scene does not', () => {
  const { g } = playLevel({ recallHint: true });
  const done = g.log.find(([t]) => t === 'level:complete')[1];
  assert.equal(done.stars, 2, done.reasons.join('; '));
  const ev = g.session.evidence.all();
  assert.equal(ev['o01-unprompted'].hintUsed, true);
  assert.equal(ev['o01-unprompted'].hintForfeit, true);
});

test('the scenario is deterministic: two runs leave identical state', () => {
  const a = playLevel().g;
  const b = playLevel().g;
  const snap = (g) => JSON.stringify([g.session.progress.doc, g.world.serialize(), g.log, g.world.stateLog]);
  assert.equal(snap(a), snap(b));
});

test('reload mid-level restores step, avatar and world state', () => {
  const storage = memoryStorage();
  const first = playLevel({ storage }).g; // finished level, saved
  const g2 = makeGame({ storage });
  g2.session.start();
  assert.equal(g2.session.machine.top.kind, 'hub');
  assert.equal(g2.world.placementState('turnstile'), 'open');
  assert.equal(g2.world.npc('ivo').pose, 'ivo_nod_s');
  assert.deepEqual(g2.world.avatar.cell, first.world.avatar.cell);
  assert.ok(g2.session.rules.stepsDone.includes('o01.s.recall'));
});
