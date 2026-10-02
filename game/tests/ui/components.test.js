import { test } from 'node:test';
import assert from 'node:assert/strict';

import {
  keycap, keycapForName, hudView, promptView, markersView, dialogueView, hintCardView, insetView, sceneBarView, feedbackView,
  journalView, controlsView, settingsView, setupScreenView, createScreenState, toastsView, errorView, COMPONENTS, VIEW_MODEL_TOPICS,
} from '../../src/ui/index.js';
import { textOf } from '../../src/ui/html.js';
import { Component } from '../../src/ui/component.js';
import { Inset } from '../../src/ui/inset.js';
import { makeDom, markupProblem } from './dom-stub.js';
import * as F from './fixtures.js';

const s = (x) => String(x);
const ok = (markup, name) => assert.equal(markupProblem(s(markup)), null, `${name}: ${markupProblem(s(markup))}`);

test('every view renders balanced markup from its fixture', () => {
  const state = createScreenState();
  state.setup = F.setupVm();
  state.calibration = F.calibrationVm();
  const views = {
    hud: hudView(F.hudVm()),
    prompt: promptView({ kind: 'person', action: 'Talk to Ivo', key: F.RETURN, gesture: 'tap-hold Caps + N', at: { x: 700, y: 200 } }),
    markers: markersView({ markers: [{ id: 'a', shape: 'conversation', state: 'idle', at: { x: 100, y: 100 } }], floor: [] }),
    dialogue: dialogueView(F.dialogueVm('o01.d.welcome')),
    hintCard: hintCardView({ text: 'Using the hint here forfeits the third star for this scene.', confirm: F.RETURN, cancel: F.ESC }),
    inset: insetView(F.insetVm()),
    sceneBar: sceneBarView({ kind: 'label', title: 'West desk', prompt: 'Type west', field: { text: 'we', cursor: 2, target: 'west' }, leave: { key: F.ESC, gesture: 'tap Caps' } }),
    feedback: feedbackView({ gesture: 'tap Caps', observed: 'Escape', effect: 'Popup closes', confidence: 'observed', confidenceLabel: 'Observed output' }),
    journal: journalView(F.journalVm()),
    controls: controlsView(F.controlsVm()),
    settings: settingsView(F.settingsVm({ confirmReset: true })),
    setup: setupScreenView(state),
    toasts: toastsView([{ id: 1, text: 'Progress will not be saved', tone: 'warn' }]),
    error: errorView({ file: '/x.json', kind: 'missing', message: 'Cannot load /x.json: HTTP 404' }),
  };
  for (const [name, v] of Object.entries(views)) ok(v, name);
});

test('component and topic lists match the contract', () => {
  assert.equal(COMPONENTS.length, 19);
  assert.ok(COMPONENTS.includes('live-region') && COMPONENTS.includes('first-use'));
  assert.equal(VIEW_MODEL_TOPICS.length, 17);
});

test('keycaps: backtick is spoken as a word, arrows draw an icon, names map from the level data', () => {
  const bt = s(keycap(keycapForName('Backtick'), { sm: true }));
  assert.match(bt, /aria-label="Backtick"/);
  assert.match(bt, />`</);
  assert.match(s(keycap({ key: 'ArrowRight', label: 'Right' })), /aria-label="Right arrow"[^>]*><svg/);
  assert.match(s(keycap({ key: 'Caps', label: 'Caps', held: true })), /kh-key wide held/);
  assert.match(s(keycap({ key: 'x', label: 'XX', silent: true })), /silent/);
  assert.equal(keycapForName('Escape').label, 'Esc');
  assert.equal(keycapForName('Q').label, 'Q');
});

test('HUD: objective strip, seal count, chips (hint is a reminder, the others open a layer)', () => {
  const m = s(hudView(F.hudVm({ seals: { count: 2, total: 5 } })));
  assert.match(m, /2 \/ 4/);
  assert.match(m, /Seals 2/);
  assert.match(m, /Clearance seals 2 of 5/);
  assert.match(m, /<span class="chip" role="note"[^>]*aria-label="Show hint/);
  assert.match(m, /data-cmd="\{&quot;type&quot;:&quot;openLayer&quot;,&quot;id&quot;:&quot;journal&quot;\}"/);
  assert.equal(s(hudView(F.hudVm({ chips: [] }))).includes('shortcuts'), false);
});

test('prompt: coral for people, teal for devices, clamped inside the stage', () => {
  const base = { action: 'Use the badge printer', key: F.RETURN, gesture: 'tap-hold Caps + N' };
  assert.match(s(promptView({ ...base, kind: 'person', at: { x: 10, y: 20 } })), /kh-prompt person" style="left:10px;top:20px/);
  assert.match(s(promptView({ ...base, kind: 'device', at: { x: 5000, y: 5000 } })), /kh-prompt device" style="left:920px;top:600px/);
});

test('markers: four shapes, reached ones gain a check, floor markers go teal to gold', () => {
  const vm = {
    markers: ['conversation', 'terminal', 'route', 'glitch'].map((shape, i) => ({ id: shape, shape, state: i === 2 ? 'reached' : 'idle', at: { x: 100 + i * 100, y: 200 } })),
    floor: [{ id: 'f1', at: { x: 50, y: 50 }, state: 'teal', shape: 'route' }, { id: 'f2', at: { x: 90, y: 50 }, state: 'gold', shape: 'route' }],
  };
  const m = s(markersView(vm));
  for (const sym of ['m-talk', 'm-terminal', 'm-route', 'm-glitch', 'm-route-teal']) assert.match(m, new RegExp(`#${sym}"`), sym);
  assert.match(m, /data-marker="route" data-state="reached"[^]*?kh-marker-badge/);
  assert.match(m, /data-floor="f1" data-state="teal"[^]*?#m-route-teal/);
  assert.equal((m.match(/kh-marker-badge/g) || []).length, 2, 'reached marker and gold floor marker');
  assert.match(m, /left:68px;top:168px/, 'at is the centre of the 64 px box');
});

test('dialogue: hint grammar for every level 01 hint line (action, key, then Hint: gesture)', () => {
  const withHint = F.LEVEL.dialogue.filter((d) => d.hint);
  assert.ok(withHint.length >= 8);
  for (const d of withHint) {
    const m = s(dialogueView(F.dialogueVm(d.id, { mode: 'instruction' })));
    const text = textOf(m);
    const a = text.indexOf(d.text);
    const h = text.indexOf(`Hint: ${d.hint.gesture}`);
    assert.ok(a >= 0, `${d.id}: action line`);
    assert.ok(h > a, `${d.id}: hint after action`);
    assert.match(m, new RegExp(`class="kh-key sm[^"]*"[^>]*>`), `${d.id}: key shown as a keycap`);
  }
  const lap = textOf(s(dialogueView(F.dialogueVm('o01.d.loop-down'))));
  assert.match(lap, /To walk south along the west walkway, you need to press Down Arrow\. .*Hint: Down Arrow is tap-hold Caps \+ J\./);
});

test('dialogue: conversation is a modal dialog with Continue and Skip commands; instruction line is a status with no footer', () => {
  const conv = s(dialogueView(F.dialogueVm('o01.d.welcome')));
  assert.match(conv, /role="dialog" aria-modal="true"/);
  assert.match(conv, /data-autofocus/);
  assert.match(conv, /data-cmd="\{&quot;type&quot;:&quot;continue&quot;\}"/);
  assert.match(conv, /data-cmd="\{&quot;type&quot;:&quot;skip&quot;\}"/);
  assert.match(textOf(conv), /Continue Return tap-hold Caps \+ N/);
  assert.match(textOf(conv), /Skip Esc tap Caps/);
  const line = s(dialogueView(F.dialogueVm('o01.d.popup')));
  assert.match(line, /role="status"/);
  assert.doesNotMatch(line, /data-cmd/);
  assert.doesNotMatch(line, /aria-modal/);
});

test('dialogue portraits come from the portraits atlas rect at world zoom; object speakers have none', () => {
  const vm = F.dialogueVm('o01.d.welcome');
  assert.equal(vm.portrait.key, 'ivo_neutral');
  const m = s(dialogueView(vm, '/'));
  const r = vm.portrait.rect;
  assert.match(m, new RegExp(`width:${r.w}px;height:${r.h}px;background-image:url\\(/art-direction/portraits/portraits-atlas.png\\);background-position:-${r.x}px -${r.y}px`));
  assert.doesNotMatch(s(dialogueView({ ...vm, portrait: null, objectSpeaker: true, speakerName: 'Popup' })), /kh-portrait/);
  assert.match(s(dialogueView(vm, '/game/')), /url\(\/game\/art-direction\/portraits/);
});

test('dialogue text from the data is escaped', () => {
  const m = s(dialogueView({ ...F.dialogueVm('o01.d.welcome'), text: '<b>x</b> & "y"' }));
  assert.doesNotMatch(m, /<b>x<\/b>/);
  assert.match(m, /&lt;b&gt;x&lt;\/b&gt; &amp; &quot;y&quot;/);
});

test('inset: four numbered cells, Caps held, only the target bright, header and layer', () => {
  const m = s(insetView(F.insetVm()));
  const t = textOf(m);
  for (const [n, label] of [[1, 'Key position'], [2, 'Hold order'], [3, 'Output'], [4, 'Effect']]) {
    assert.match(m, new RegExp(`kh-order">${n}</span> ${label}`));
  }
  assert.equal((m.match(/class="kh-cell"/g) || []).length, 4);
  assert.match(t, /Move east nav layer · tap-hold Caps · 200 ms/);
  assert.match(m, /kh-key sm held cap[^>]*>Caps/);
  assert.match(m, /kh-key sm dim[^>]*>A</);
  assert.doesNotMatch(m, /kh-key sm dim[^>]*>L</, 'the target key is at full strength');
  assert.match(m, /kh-tag hold">Hold/);
  assert.match(m, /kh-tag tap">Tap/);
  assert.match(t, /Right arrow/);
  assert.match(t, /Step east/);
});

test('inset: first use adds the tall variant and a foot line; a null vm (recall) hides it', () => {
  assert.match(s(insetView(F.insetVm({ firstUse: true }))), /inset-tall/);
  assert.match(s(insetView(F.insetVm({ firstUse: true }))), /First time for this key/);
  assert.doesNotMatch(s(insetView(F.insetVm())), /First time/);
  const { doc, root } = makeDom();
  const host = doc.createElement('div');
  root.appendChild(host);
  const inset = new Inset(host, null);
  inset.render(F.insetVm());
  assert.equal(host.hidden, false);
  assert.match(host.innerHTML, /kh-inset/);
  inset.render(null);
  assert.equal(host.hidden, true);
  assert.equal(host.innerHTML, '');
});

test('scene bar: label field shows the cursor, editor shows the glitch frame, untimed and next letter', () => {
  const label = s(sceneBarView({ kind: 'label', title: 'West desk label', prompt: 'Type the label west', field: { text: 'we', cursor: 2, target: 'west' }, leave: { key: F.ESC, gesture: 'tap Caps' } }));
  assert.match(label, /we<span class="cur"> <\/span>/);
  assert.match(label, /target: west/);
  assert.match(textOf(label), /Leave Esc tap Caps/);
  const ed = s(sceneBarView({ kind: 'editor', title: 'Folded form', prompt: 'Repair the form', field: { text: 'lobb', cursor: 4 }, nextLetter: 'y', leave: { key: F.ESC, gesture: 'tap Caps' } }));
  assert.match(ed, /kh-term glitch editor/);
  assert.match(ed, /lobb<span class="cur"> <\/span>/);
  assert.match(textOf(ed), /Untimed\. Nothing is lost on a retry\./);
  assert.match(ed, /Next letter y/);
  const walk = s(sceneBarView({ kind: 'walk', title: 'Garden loop', prompt: 'Walk', field: null, leave: { key: F.ESC, gesture: 'tap Caps' } }));
  assert.doesNotMatch(walk, /kh-code/);
});

test('feedback: three confidence states differ by icon, border class and words; no detection claims', () => {
  const words = { observed: 'Observed output', player_confirmed: 'You confirmed this gesture', external_only: "Can't be observed here (OS-reserved)" };
  const seen = new Set();
  for (const [confidence, label] of Object.entries(words)) {
    const m = s(feedbackView({ gesture: 'tap-hold Caps + H', observed: 'ArrowLeft', effect: 'Step west', confidence, confidenceLabel: label }));
    assert.match(textOf(m), new RegExp(label.replace(/[()?]/g, '\\$&')));
    assert.match(textOf(m), /Gesture shown tap-hold Caps \+ H Output ArrowLeft Effect Step west/);
    assert.doesNotMatch(m, /detected|verified|you pressed|nav layer/i);
    seen.add(m.match(/class="kh-fb (\w+)"/)[1] + m.match(/#i-([\w-]+)/)[1]);
  }
  assert.equal(seen.size, 3);
});

test('error view names the file and the problem', () => {
  const m = textOf(s(errorView({ file: '/design/levels/world.json', kind: 'parse', message: 'Cannot load /design/levels/world.json: bad JSON' })));
  assert.match(m, /Cannot load \/design\/levels\/world\.json: bad JSON/);
  assert.match(m, /File \/design\/levels\/world\.json Problem parse/);
});

test('Component base: null hides, a re-render keeps focus on the same data-fid', () => {
  class T extends Component { view(vm) { return `<button data-fid="a">${vm.n}</button><button data-fid="b" data-autofocus>b</button>`; } }
  const { doc, root } = makeDom();
  const host = doc.createElement('div');
  root.appendChild(host);
  const c = new T(host, null);
  c.render({ n: 1 });
  assert.equal(doc.activeElement.getAttribute('data-fid'), 'b', 'first show focuses data-autofocus');
  doc.activeElement = host.querySelector('[data-fid="a"]');
  c.render({ n: 2 });
  assert.equal(doc.activeElement.getAttribute('data-fid'), 'a', 'focus restored after re-render');
  c.render(null);
  assert.equal(host.hidden, true);
});
