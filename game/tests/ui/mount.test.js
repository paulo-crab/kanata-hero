import { test } from 'node:test';
import assert from 'node:assert/strict';
import { readdirSync, readFileSync } from 'node:fs';
import path from 'node:path';

import { EventBus, FakeClock } from '../../src/shared/index.js';
import { mountUi, stageClasses, COMPONENTS, nextFocusIndex } from '../../src/ui/index.js';
import { TOAST_MS, TOAST_MAX } from '../../src/ui/misc.js';
import { makeDom, fakeMatchMedia } from './dom-stub.js';
import * as F from './fixtures.js';

function setup(opts = {}) {
  const { doc, root, stage } = makeDom();
  const bus = new EventBus();
  const clock = new FakeClock();
  const mm = fakeMatchMedia(opts.systemReduced || false);
  const ui = mountUi(root, { bus, clock, stage, matchMedia: mm.matchMedia });
  const commands = [];
  bus.on('ui:command', (c) => commands.push(c));
  const errors = [];
  bus.on('bus:error', (e) => errors.push(e));
  return { doc, root, stage, bus, clock, mm, ui, commands, errors };
}
const host = (t, name) => t.ui.components[name].host;

test('mount builds a hidden host per component and the sprite; nothing shows before a view-model', () => {
  const t = setup();
  const names = Object.keys(t.ui.components);
  for (const n of COMPONENTS.filter((c) => c !== 'keycap' && c !== 'live-region')) assert.ok(names.includes(n), n);
  for (const n of names.filter((x) => x !== 'live-region')) assert.equal(host(t, n).hidden, true, `${n} starts hidden`);
  assert.match(t.root.children[0].innerHTML, /symbol id="m-talk"/);
  assert.equal(t.stage.getAttribute('tabindex'), '0', 'stage is focusable so the play surface can hold focus');
});

test('every view-model topic renders its component, and null hides it again', () => {
  const t = setup();
  const feed = {
    'vm:hud': ['hud', F.hudVm()],
    'vm:dialogue': ['dialogue', F.dialogueVm('o01.d.welcome')],
    'vm:inset': ['inset', F.insetVm()],
    'vm:journal': ['journal', F.journalVm()],
    'vm:layout-help': ['layout-help', F.fakeLayoutHelpModel(F.MANIFEST, { selectedKey: 'h' })],
    'vm:controls': ['controls', F.controlsVm()],
    'vm:settings': ['settings', F.settingsVm()],
    'vm:error': ['error', { file: '/x.json', kind: 'missing', message: 'Cannot load /x.json: HTTP 404' }],
    'vm:prompt': ['prompt', { kind: 'person', action: 'Talk', key: F.RETURN, gesture: 'tap-hold Caps + N', at: { x: 1, y: 1 } }],
    'vm:markers': ['markers', { markers: [{ id: 'm', shape: 'terminal', state: 'idle', at: { x: 9, y: 9 } }], floor: [] }],
    'vm:scene-bar': ['scene-bar', { kind: 'label', title: 'West desk', prompt: 'Type west', field: { text: '', cursor: 0 }, leave: { key: F.ESC, gesture: 'tap Caps' } }],
    'vm:hint-card': ['hint-card', { text: 'Using the hint here forfeits the third star for this scene.', confirm: F.RETURN, cancel: F.ESC }],
  };
  for (const [topic, [name, vm]] of Object.entries(feed)) {
    t.bus.emit(topic, vm);
    assert.equal(host(t, name).hidden, false, `${topic} shows ${name}`);
    assert.ok(host(t, name).innerHTML.length > 20, name);
    t.bus.emit(topic, null);
    assert.equal(host(t, name).hidden, true, `${topic}=null hides ${name}`);
  }
  assert.deepEqual(t.errors, [], 'no handler threw');
});

test('live region announces an objective change and bus announcements, without repeating identical lines', () => {
  const t = setup();
  const live = host(t, 'live-region');
  assert.equal(live.getAttribute('aria-live'), 'polite');
  t.bus.emit('intent', { type: 'objective', stepId: 'o01.s.popup', text: 'Close the welcome popup.' });
  assert.equal(live.textContent, 'Objective: Close the welcome popup.');
  t.bus.emit('intent', { type: 'objective', stepId: 'o01.s.keys', text: 'Learn the journal key.' });
  assert.equal(live.textContent, 'Objective: Learn the journal key.');
  t.bus.emit('vm:announce', { text: 'Objective: Learn the journal key.' });
  assert.equal(live.textContent, 'Objective: Learn the journal key.', 'same line from both routes is spoken once');
  t.bus.emit('vm:announce', { text: 'Journal opened.' });
  assert.equal(live.textContent, 'Journal opened.');
  t.ui.announce('Journal opened.');
  assert.equal(live.textContent, 'Journal opened. ', 'a direct repeat alternates a no-break space so it is read again');
});

test('first-use inset announces itself once per appearance', () => {
  const t = setup();
  const live = host(t, 'live-region');
  t.bus.emit('vm:inset', F.insetVm({ firstUse: true, header: 'Continue' }));
  assert.match(live.textContent, /New key: Continue\. The keyboard inset is open/);
  live.textContent = '';
  t.bus.emit('vm:inset', F.insetVm({ firstUse: true, header: 'Continue' }));
  assert.equal(live.textContent, '', 'a re-render does not announce again');
  t.bus.emit('vm:inset', null);
  t.bus.emit('vm:inset', F.insetVm({ firstUse: false }));
  assert.equal(live.textContent, '');
});

test('settings set .rm, .large-text and .hc on the stage; reduced motion follows the OS when set to system', () => {
  const t = setup();
  const has = (c) => t.stage.classList.contains(c);
  assert.deepEqual([has('rm'), has('large-text'), has('hc')], [false, false, false]);
  t.bus.emit('vm:settings', F.settingsVm({ largerText: true }));
  assert.deepEqual([has('rm'), has('large-text'), has('hc')], [false, true, false]);
  t.bus.emit('vm:settings', F.settingsVm({ largerText: true, highContrast: true, reducedMotion: 'on' }));
  assert.deepEqual([has('rm'), has('large-text'), has('hc')], [true, true, true]);
  t.bus.emit('vm:settings', F.settingsVm({ reducedMotion: 'system' }));
  assert.deepEqual([has('rm'), has('large-text'), has('hc')], [false, false, false]);
  t.mm.mq.set(true);
  assert.equal(has('rm'), true, 'OS reduced-motion turns it on while the setting is system');
  t.bus.emit('vm:settings', F.settingsVm({ reducedMotion: 'off' }));
  assert.equal(has('rm'), false, 'an explicit Off wins over the OS');
  t.mm.mq.set(false);
  t.bus.emit('vm:settings', F.settingsVm({ reducedMotion: 'system' }));
  assert.equal(has('rm'), false);
});

test('OS reduced motion applies at mount before any settings arrive, and the engine hears about it', () => {
  const { doc, root, stage } = makeDom();
  const bus = new EventBus();
  const seen = [];
  bus.on('ui:settings-applied', (s) => seen.push(s));
  mountUi(root, { bus, stage, clock: new FakeClock(), matchMedia: fakeMatchMedia(true).matchMedia });
  assert.equal(stage.classList.contains('rm'), true);
  assert.deepEqual(seen[0], { reducedMotion: true, largerText: false, highContrast: false });
  assert.deepEqual(stageClasses({ reducedMotion: 'off', largerText: true, highContrast: false }, true), { rm: false, 'large-text': true, hc: false });
  void doc;
});

test('toasts: at most three, each gone after six seconds on the injected clock', () => {
  const t = setup();
  const toast = host(t, 'toast');
  for (const n of [1, 2, 3, 4]) t.bus.emit('vm:toast', { text: `Toast ${n}`, tone: 'info' });
  assert.equal((toast.innerHTML.match(/class="kh-toast[" ]/g) || []).length, TOAST_MAX);
  assert.doesNotMatch(toast.innerHTML, /Toast 1</);
  t.clock.advance(TOAST_MS - 1);
  assert.equal((toast.innerHTML.match(/class="kh-toast[" ]/g) || []).length, 3);
  t.clock.advance(1);
  assert.equal(toast.hidden, true);
  assert.equal(t.clock.pending(), 0, 'no timers left behind');
  t.bus.emit('vm:toast', { text: 'Progress will not be saved', tone: 'warn' });
  assert.match(toast.innerHTML, /kh-toast warn/);
  t.bus.emit('vm:toast', null);
  assert.equal(toast.hidden, true);
  assert.equal(t.clock.pending(), 0);
});

test('mouse alternatives send ui:command; a bad payload is ignored', () => {
  const t = setup();
  t.bus.emit('vm:journal', F.journalVm());
  const jh = host(t, 'journal');
  t.root.fire('click', { target: jh.querySelector('[data-row="o02"]') });
  t.root.fire('click', { target: jh.querySelector('[data-fid="also-ride-hub"]') });
  t.root.fire('click', { target: jh.querySelector('[data-fid="close"]') });
  t.root.fire('click', { target: jh.querySelector('h2') || { closest: () => null } });
  assert.deepEqual(t.commands, [{ type: 'chooseRow', id: 'o02' }, { type: 'rideHub' }, { type: 'back' }]);
  t.root.fire('click', { target: { closest: (sel) => (sel === '[data-cmd]' ? { getAttribute: () => '{oops' } : null) } });
  assert.equal(t.commands.length, 3);
});

test('focusing a Layout help key moves the card once; a selected key does not loop', () => {
  const t = setup();
  t.bus.emit('vm:layout-help', F.fakeLayoutHelpModel(F.MANIFEST, { selectedKey: 'h' }));
  const lh = host(t, 'layout-help');
  t.root.fire('focusin', { target: lh.querySelector('[data-fid="key-j"]') });
  t.root.fire('focusin', { target: lh.querySelector('[data-fid="key-h"]') });
  assert.deepEqual(t.commands, [{ type: 'selectKey', id: 'j' }]);
});

test('layout help keeps focus on the same key across a re-render (tab switch) and focuses the selected tab on open', () => {
  const t = setup();
  t.bus.emit('vm:layout-help', F.fakeLayoutHelpModel(F.MANIFEST, { tab: 'base' }));
  assert.equal(t.doc.activeElement.getAttribute('data-fid'), 'tab-base');
  t.doc.activeElement = host(t, 'layout-help').querySelector('[data-fid="variant-microsoft"]');
  t.bus.emit('vm:layout-help', F.fakeLayoutHelpModel(F.MANIFEST, { tab: 'base', variant: 'microsoft' }));
  assert.equal(t.doc.activeElement.getAttribute('data-fid'), 'variant-microsoft');
});

test('focus returns to where it was when the layer closes (ui:restore-focus), or to the stage', () => {
  const t = setup();
  const opener = t.doc.createElement('button');
  t.doc.activeElement = opener;
  t.bus.emit('vm:layout-help', F.fakeLayoutHelpModel(F.MANIFEST));
  assert.notEqual(t.doc.activeElement, opener);
  t.bus.emit('vm:layout-help', null);
  t.bus.emit('ui:restore-focus', {});
  assert.equal(t.doc.activeElement, opener);
  t.doc.activeElement = null;
  t.bus.emit('vm:journal', F.journalVm());
  t.bus.emit('vm:journal', null);
  t.bus.emit('ui:restore-focus', {});
  assert.equal(t.doc.activeElement, t.stage, 'nothing remembered: the play surface');
  t.bus.emit('vm:journal', F.journalVm());
  t.bus.emit('vm:layout-help', F.fakeLayoutHelpModel(F.MANIFEST));
  t.bus.emit('vm:layout-help', null);
  t.doc.activeElement = null;
  t.bus.emit('ui:restore-focus', {});
  assert.equal(t.doc.activeElement, null, 'a layer below is still open: focus stays with it');
});

test('Tab wraps inside an open modal layer and never escapes; Esc stays the way out (no trap)', () => {
  const t = setup();
  t.bus.emit('vm:controls', F.controlsVm());
  const ch = host(t, 'controls');
  const list = ch.querySelectorAll('button:not([disabled]),[tabindex]:not([tabindex="-1"])');
  assert.ok(list.length >= 1);
  t.doc.activeElement = list[list.length - 1];
  const fwd = t.root.fire('keydown', { key: 'Tab' });
  assert.equal(fwd.defaultPrevented, true);
  assert.equal(t.doc.activeElement, list[0]);
  const back = t.root.fire('keydown', { key: 'Tab', shiftKey: true });
  assert.equal(back.defaultPrevented, true);
  assert.equal(t.doc.activeElement, list[list.length - 1]);
  const other = t.root.fire('keydown', { key: 'a' });
  assert.equal(other.defaultPrevented, false);
  t.bus.emit('vm:controls', null);
  assert.equal(t.root.fire('keydown', { key: 'Tab' }).defaultPrevented, false, 'no modal: Tab is the browser\'s');
  assert.deepEqual([nextFocusIndex(3, 2, false), nextFocusIndex(3, 0, true), nextFocusIndex(3, -1, false), nextFocusIndex(0, 0, false)], [0, 2, 0, -1]);
});

test('setup and calibration share one panel; calibration alone draws its own; feedback draws inside while one is open', () => {
  const t = setup();
  t.bus.emit('vm:calibration', F.calibrationVm());
  assert.match(host(t, 'calibration').innerHTML, /data-screen="calibration"/);
  t.bus.emit('vm:setup', F.setupVm());
  assert.match(host(t, 'setup').innerHTML, /data-screen="setup"[^]*su-step/, 'one panel holds both');
  assert.equal(host(t, 'calibration').hidden, true);
  t.bus.emit('vm:feedback', { gesture: null, observed: 'ArrowLeft', effect: 'Step west', confidence: 'observed', confidenceLabel: 'Observed output' });
  assert.match(host(t, 'setup').innerHTML, /kh-fb observed/);
  assert.equal(host(t, 'feedback').hidden, true, 'no second card in the side column');
  t.bus.emit('vm:setup', null);
  t.bus.emit('vm:calibration', null);
  assert.equal(host(t, 'feedback').hidden, false, 'with no panel open it returns to the side column');
  assert.match(host(t, 'feedback').innerHTML, /kh-side/);
});

test('diagram view switch repaints the calibration panel locally', () => {
  const t = setup();
  const d = { positions: { rows: [[{ label: 'Caps', state: 'layer' }]], caption: 'Positions' }, characters: { rows: [[{ label: 'a', state: 'lit' }]], caption: 'Characters' } };
  t.bus.emit('vm:calibration', F.calibrationVm({ diagram: d }));
  assert.match(host(t, 'calibration').innerHTML, /Positions/);
  t.root.fire('click', { target: host(t, 'calibration').querySelector('[data-view="characters"]') });
  assert.match(host(t, 'calibration').innerHTML, /kh-sk lit/);
  assert.deepEqual(t.commands, [], 'a local view switch is not a game command');
});

test('error screen reload button reloads the page', () => {
  const t = setup();
  t.bus.emit('vm:error', { file: '/x.json', kind: 'missing', message: 'Cannot load /x.json: HTTP 404' });
  t.root.fire('click', { target: host(t, 'error').querySelector('[data-ui="reload"]') });
  assert.equal(t.doc.defaultView.location.reloads, 1);
});

test('destroy removes listeners and subscriptions', () => {
  const t = setup();
  t.ui.destroy();
  t.bus.emit('vm:hud', F.hudVm());
  assert.equal(host(t, 'hud').hidden, true);
  t.bus.emit('vm:announce', { text: 'x' });
  assert.notEqual(host(t, 'live-region').textContent, 'x');
  t.root.fire('click', { target: { closest: () => ({ getAttribute: () => '{"type":"back"}' }) } });
  assert.deepEqual(t.commands, []);
});

test('no audio anywhere in the UI: no audio element, API or permission request in src/ui and css', () => {
  const t = setup();
  for (const name of Object.keys(t.ui.components)) assert.doesNotMatch(host(t, name).innerHTML, /<audio|<video/i);
  const dir = path.resolve(F.GAME, 'src', 'ui');
  for (const f of readdirSync(dir)) {
    const src = readFileSync(path.join(dir, f), 'utf8');
    assert.doesNotMatch(src, /\bAudio\b|AudioContext|<audio|getUserMedia|speechSynthesis/, f);
  }
});

test('the UI never reads Date.now, performance.now or Math.random', () => {
  const dir = path.resolve(F.GAME, 'src', 'ui');
  for (const f of readdirSync(dir)) {
    const src = readFileSync(path.join(dir, f), 'utf8');
    assert.doesNotMatch(src, /Date\.now|performance\.now|Math\.random|new Date\(/, f);
  }
});
