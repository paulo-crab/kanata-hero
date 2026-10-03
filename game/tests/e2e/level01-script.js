// Full-stack level 01 play script (task 6.2). Drives the game only through `interpreter.handleKeyEvent`
// and the fake clock, and observes only the bus and the public module APIs of the contract
// (game/CONTRACTS.md sections 3 to 7). The same script, from the same state, must give the same events.
import {
  ScriptedInput, BusRecorder, STEP_MS, CELL_STEPS, level01Legs, walkScript, loadRealData,
  collisionGrid, shortestPath,
} from '../harness/index.js';

export const SCRIPT_DATA = loadRealData();

/** Result of one headless run. */
function fail(msg) { throw new Error(`level01 script: ${msg}`); }

/**
 * Play level 01 from a cold start.
 * @param {object} game  handles returned by createGame (game-factory.js)
 * @param {{wrongDetours?:number, recallHint?:boolean, stopAfter?:string, wrongTries?:boolean}} [opts]
 *   wrongTries: false skips the deliberate wrong outputs in the popup and label scenes (a clean run for the stars)
 *   wrongDetours: extra wrong-direction steps at the start of the lap (clean-run measure)
 *   recallHint: ask for the hint during the recall walk and confirm the forfeit card
 *   stopAfter: 'setup'|'arrival'|'popup'|'keys-hint'|'keys'|'lap-leg-1'|'lap'|'stops'|'recall' to stop early (resume tests)
 * @returns {{log:object[], events:object[], checkpoints:object}} everything needed to compare two runs
 */
export function playLevel01(game, opts = {}) {
  const { wrongDetours = 0, recallHint = false, stopAfter = null, wrongTries = true } = opts;
  const { bus, clock, loop, interpreter, world, rules, machine, progress, evidence } = game;
  const rec = new BusRecorder(bus);
  const player = new ScriptedInput({
    target: interpreter,
    advance: (ms) => { clock.advance(ms); if (loop) loop.advance(ms); },
  });
  const cp = {};
  const legs = Object.fromEntries(level01Legs(SCRIPT_DATA).map((l) => [l.id, l]));
  const topId = () => (machine.top ? machine.top.id : null);
  const cell = () => [...world.avatar.cell];
  const expectCell = (want, what) => {
    const c = cell();
    if (c[0] !== want[0] || c[1] !== want[1]) fail(`${what}: avatar at ${c}, expected ${want}`);
  };
  const grid = collisionGrid(SCRIPT_DATA.map);
  // Walk a leg from wherever the avatar stands: a short transit to the nearest leg cell, then along the leg.
  const walk = (leg) => {
    const here = cell();
    let idx = leg.cells.findIndex((c) => c[0] === here[0] && c[1] === here[1]);
    if (idx < 0) {
      let best = null;
      leg.cells.forEach((c, i) => {
        const p = shortestPath(grid, here, c);
        if (p && (!best || p.length <= best.path.length)) best = { path: p, i };
      });
      if (!best) fail(`no way from ${here} to leg ${leg.id}`);
      player.run(walkScript(best.path));
      idx = best.i;
    }
    player.run(walkScript(leg.cells.slice(idx)));
    return player;
  };
  const letGo = (steps = 2) => player.wait(steps);
  // Enter until the named dialogue has closed, then until any modal line that follows it has closed too
  // (the rules chain modal lines: loop-done -> stops, stops-done -> recall, thanks -> fold-intro).
  const closed = (id) => rec.of('dialogue:closed').some((e) => e.id === id);
  const finishDialogue = (id) => {
    for (let i = 0; i < 12 && !closed(id) && machine.top?.kind === 'dialogue'; i += 1) player.tap('Enter');
    if (!closed(id)) fail(`dialogue ${id} did not close`);
    for (let i = 0; i < 12 && machine.top?.kind === 'dialogue'; i += 1) player.tap('Enter');
    if (machine.top?.kind === 'dialogue') fail(`a dialogue after ${id} did not close`);
  };
  const done = (name) => stopAfter === name;

  // ---- 1. Setup is skipped with Escape, then Return on the confirm card (never by one key alone) ----
  if (topId() !== 'setup') fail(`expected the setup scene first, found ${topId()}`);
  player.tap('Escape');
  letGo(2);
  if (topId() !== 'setup') fail('Escape alone must open the confirm card, not leave setup');
  player.tap('Enter');
  letGo(4);
  cp.afterSetup = { top: topId(), setupDone: progress.load().setup.done };
  if (done('setup')) return { log: player.log, events: rec.events, checkpoints: cp };

  // ---- 2. Arrival: elevator closed -> half -> open, 120 ms per state, avatar on the LIFT mat ----
  const seen = [];
  const sample = () => {
    const st = world.placementState('elevator');
    const last = seen.at(-1);
    if (!last || last.state !== st) seen.push({ state: st, steps: 0 });
    seen.at(-1).steps += 1;
  };
  sample();
  for (let i = 0; i < Math.ceil((5 * 120) / STEP_MS); i += 1) { player.wait(1); sample(); }
  cp.elevatorStates = seen.map((x) => x.state);
  cp.elevatorStateMs = seen.slice(0, -1).map((x) => Math.round(x.steps * STEP_MS));
  cp.elevatorFinal = world.placementState('elevator');
  expectCell([3, 2], 'arrival mat');
  if (done('arrival')) return { log: player.log, events: rec.events, checkpoints: cp };

  // ---- 3. Ivo's welcome opens by itself when the hub starts (step_start), and the popup opens when it closes
  cp.welcome = rec.of('vm:dialogue').at(-1)?.id;
  finishDialogue('o01.d.welcome');
  if (topId() !== 'o01-popup') fail(`expected the welcome popup after the welcome, found ${topId()}`);
  cp.popupOpen = topId();
  if (wrongTries) player.tap('Caps+H');                    // wrong: ArrowLeft observed, popup stays
  cp.popupWrongFeedback = wrongTries ? rec.of('vm:feedback').at(-1)?.observed ?? null : 'Left Arrow observed';
  cp.popupStillOpen = topId() === 'o01-popup';
  player.tap('Caps');                                      // Escape: closes the popup
  letGo();
  cp.popupSuccess = rec.of('scene:success').some((e) => e.sceneId === 'o01-popup');
  cp.ivoAfterPopup = world.npc('ivo').pose;
  finishDialogue('o01.d.popup-done');
  if (done('popup')) return { log: player.log, events: rec.events, checkpoints: cp };

  // ---- 4. Three key lines: journal (Q), hint (Backquote), Layout help (?) --------------------
  player.tap('q');
  cp.journalOpened = rec.of('vm:journal').at(-1) != null && machine.top?.kind === 'journal';
  player.tap('q');                                         // Q closes it again
  player.tap('Backquote');
  if (done('keys-hint')) return { log: player.log, events: rec.events, checkpoints: cp };
  player.tap('?');
  cp.layoutHelpOpened = machine.top?.kind === 'layout-help';
  player.tap('Escape');                                    // back
  letGo();
  cp.stepsAfterKeys = [...rules.stepsDone];
  if (done('keys')) return { log: player.log, events: rec.events, checkpoints: cp };

  // ---- 5. The lap: down, right, up, left. Layout help mid-lap leaves the hub untouched --------
  cp.insetDuringLap = rec.of('vm:inset').at(-1) != null;
  for (let i = 0; i < wrongDetours; i += 1) {
    player.step('ArrowRight');
    player.step('ArrowLeft');
  }
  const lapIds = ['loop-down', 'loop-right', 'loop-up', 'loop-left'];
  for (const id of lapIds) {
    const leg = legs[id];
    walk(leg);
    letGo();
    expectCell(leg.target, `${id} marker`);
    if (id === 'loop-down') {
      const before = { cell: cell(), facing: world.avatar.facing };
      player.tap('?');
      player.tap('Escape');
      letGo();
      cp.layoutHelpRoundTrip = JSON.stringify(before) === JSON.stringify({ cell: cell(), facing: world.avatar.facing })
        && machine.top?.kind !== 'layout-help';
      if (done('lap-leg-1')) return { log: player.log, events: rec.events, checkpoints: cp };
    }
  }
  cp.lapSuccess = rec.of('scene:success').some((e) => e.sceneId === 'o01-loop');
  cp.lapProgress = rec.of('scene:progress').filter((e) => e.sceneId === 'o01-loop').map((e) => e.done);
  finishDialogue('o01.d.loop-done');
  if (done('lap')) return { log: player.log, events: rec.events, checkpoints: cp };

  // ---- 6. Four desks in order; the west desk opens the label scene ---------------------------
  for (const id of ['stop-north', 'stop-west', 'stop-south', 'stop-east']) {
    walk(legs[id]);
    letGo();
    expectCell(legs[id].target, id);
    if (id === 'stop-west') {
      cp.labelOpen = topId() === 'o01-desk-label';
      if (wrongTries) player.tap('Caps+W');                // Option + Right: named in the feedback
      cp.labelWrongFeedback = wrongTries ? rec.of('vm:feedback').at(-1)?.observed ?? null : 'Option + Right observed';
      player.type('west');
      letGo();
      cp.labelSuccess = rec.of('scene:success').some((e) => e.sceneId === 'o01-desk-label');
    }
  }
  cp.stopsSuccess = rec.of('scene:success').some((e) => e.sceneId === 'o01-four-stops');
  cp.ivoAtNorth = world.npc('ivo').cell;
  cp.stopsStepDone = rules.stepsDone.includes('o01.s.stops');
  finishDialogue('o01.d.stops-done');
  if (done('stops')) return { log: player.log, events: rec.events, checkpoints: cp };

  // ---- 7. Recall: no markers, no inset; Ivo at the north desk, then back to reception ---------
  cp.recallInset = rec.of('vm:inset').at(-1) ?? null;
  cp.recallFloorMarkers = (rec.of('vm:markers').at(-1)?.floor ?? []).length;
  if (recallHint) {
    player.tap('Backquote');                               // recall: forfeit card first
    cp.hintCard = rec.of('vm:hint-card').at(-1) ?? null;
    player.tap('Enter');                                   // confirm the forfeit
  }
  walk(legs['recall-to-north']);
  letGo();
  cp.reminder = rec.of('vm:dialogue').at(-1)?.id;          // o01.d.reminder (popup speaker)
  player.tap('Escape');                                    // tap Caps: closes the reminder
  letGo();
  cp.ivoBackAtPost = world.npc('ivo').cell;
  walk(legs['recall-back-to-reception']);
  letGo();
  expectCell([12, 13], 'reception');
  cp.recallSuccess = rec.of('scene:success').some((e) => e.sceneId === 'o01-unprompted');
  finishDialogue('o01.d.thanks');
  if (done('recall')) return { log: player.log, events: rec.events, checkpoints: cp };

  // ---- 8. The world changed ------------------------------------------------------------------
  cp.world = {
    turnstile: world.placementState('turnstile'),
    gateOpen: world.isGateOpen('g.turnstile'),
    ivoPose: world.npc('ivo').pose,
    ivoCell: world.npc('ivo').cell,
    markersGold: (rec.of('vm:markers').at(-1)?.floor ?? []).every((m) => m.state === 'gold') && (rec.of('vm:markers').at(-1)?.floor ?? []).length > 0,
    glitchVisible: rules.isVisible('glitch_lobby'),
  };
  const doc = progress.load();
  cp.progress = {
    levelsDone: doc.levelsDone,
    flags: doc.flags,
    journal: doc.journal,
    stars: doc.levels['orientation-01']?.stars,
  };
  cp.levelComplete = rec.of('level:complete').at(-1) ?? null;
  cp.evidenceScenes = Object.keys(evidence.all ? evidence.all() : {});
  return { log: player.log, events: rec.events, checkpoints: cp };
}

export { CELL_STEPS };
