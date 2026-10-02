import { test } from 'node:test';
import assert from 'node:assert/strict';

import {
  layoutHelpView, legendKinds, journalView, controlsView, settingsView, setupScreenView, calibrationBody, createScreenState,
} from '../../src/ui/index.js';
import { textOf } from '../../src/ui/html.js';
import { markupProblem } from './dom-stub.js';
import * as F from './fixtures.js';

const s = (x) => String(x);

// ---- Layout help ----------------------------------------------------------------------------------------------------
test('layout help: four tabs and both keyboard variants render from the manifest, with balanced markup', () => {
  for (const variant of ['macbook', 'microsoft']) {
    for (const tab of ['base', 'nav', 'numbers-symbols', 'practice']) {
      const vm = F.fakeLayoutHelpModel(F.MANIFEST, { tab, variant, selectedKey: 'h' });
      const m = s(layoutHelpView(vm));
      assert.equal(markupProblem(m), null, `${variant}/${tab}`);
      const expected = F.MANIFEST.keys.filter((k) => k.position && k.keyboards.includes(variant)).length;
      assert.equal((m.match(/class="kh-lk [^"]*" style="--w/g) || []).length, expected, `${variant}/${tab}: one drawn key per manifest key`);
      assert.equal((m.match(/role="tab"/g) || []).length, 4);
      assert.match(m, new RegExp(`aria-selected="true"[^>]*>${tab}<`));
      assert.match(m, /Keyboard type/);
    }
  }
});

test('layout help: changing a manifest entry changes the legend', () => {
  const before = F.fakeLayoutHelpModel(F.MANIFEST, { tab: 'base', selectedKey: 'a' });
  const edited = structuredClone(F.MANIFEST);
  const a = edited.keys.find((k) => k.id === 'a');
  a.layers.base.legend = 'Hyper';
  const after = F.fakeLayoutHelpModel(edited, { tab: 'base', selectedKey: 'a' });
  const labelFor = (vm) => s(layoutHelpView(vm)).match(/aria-label="a, (\w+)"/);
  assert.equal(labelFor(before)[1], 'Ctrl', 'unedited manifest: A holds Ctrl');
  assert.equal(labelFor(after)[1], 'Hyper', 'edited manifest: the drawn legend follows');
  assert.notEqual(s(layoutHelpView(before)), s(layoutHelpView(after)));
});

test('layout help: silent keys are drawn XX with their name; practice marks every silenced manifest key', () => {
  const vm = F.fakeLayoutHelpModel(F.MANIFEST, { tab: 'practice' });
  const m = s(layoutHelpView(vm));
  const silentIds = vm.keys.filter((k) => k.silent).map((k) => k.id);
  assert.ok(silentIds.length > 10);
  for (const id of silentIds) assert.ok(F.MANIFEST.practice.silenced_keys.includes(id), `${id} is silenced in the manifest`);
  assert.match(m, /kh-lk silent[^>]*aria-label="Backspace, silent on practice"[^>]*>\s*<span class="l">XX<\/span><span class="s">Backspace</);
  assert.ok(legendKinds(vm.keys).some(([c]) => c === 'silent'));
  assert.equal(legendKinds(F.fakeLayoutHelpModel(F.MANIFEST, { tab: 'base' }).keys).some(([c]) => c === 'silent'), false, 'legend lists only kinds on the tab');
});

test('layout help: nav tab shows the held layer key, the key card, the toggle-out sequence and the emergency exit as unverified', () => {
  const vm = F.fakeLayoutHelpModel(F.MANIFEST, { tab: 'nav', selectedKey: 'l' });
  const m = s(layoutHelpView(vm));
  assert.match(m, /kh-lk layerkey[^>]*data-key="Caps"/);
  assert.match(textOf(m), /Control \+ Alt \+ GUI \+ V/);
  assert.match(m, /data-card="emergency-exit"/);
  assert.match(textOf(m), /Emergency exit \(unverified\) Shown after its runtime behaviour is verified\./);
  assert.match(m, /lh-card locked/);
  assert.match(m, /kh-lk [^"]*focus" style="--w:1" data-fid="key-l"/);
  assert.match(textOf(m), /Tap: Right/);
});

test('layout help: keyboard-only navigation (tabs, variants, keys and close are real buttons with commands)', () => {
  const m = s(layoutHelpView(F.fakeLayoutHelpModel(F.MANIFEST, { tab: 'base' })));
  assert.match(m, /data-fid="tab-nav"[^>]*data-cmd="\{&quot;type&quot;:&quot;selectTab&quot;,&quot;id&quot;:&quot;nav&quot;\}"/);
  assert.match(m, /data-fid="variant-microsoft"[^>]*data-cmd="\{&quot;type&quot;:&quot;selectVariant&quot;,&quot;id&quot;:&quot;microsoft&quot;\}"/);
  assert.match(m, /data-fid="key-q"[^>]*data-cmd="\{&quot;type&quot;:&quot;selectKey&quot;,&quot;id&quot;:&quot;q&quot;\}"/);
  assert.match(m, /data-fid="close"[^>]*data-cmd="\{&quot;type&quot;:&quot;back&quot;\}"/);
  assert.match(m, /data-autofocus/);
  assert.equal((m.match(/<button/g) || []).length, (m.match(/<\/button>/g) || []).length);
  assert.match(m, /role="dialog" aria-modal="true"/);
});

test('layout help: Microsoft remap strip appears only when the view-model carries it', () => {
  const vm = F.fakeLayoutHelpModel(F.MANIFEST, { variant: 'microsoft' });
  assert.doesNotMatch(s(layoutHelpView(vm)), /lh-remap/);
  const m = s(layoutHelpView({ ...vm, remap: [{ from: 'Alt', to: 'Command' }, { from: 'Win', to: 'Option' }] }));
  assert.match(textOf(m), /Alt Command Win Option/);
});

// ---- Setup and calibration -----------------------------------------------------------------------------------------------
test('setup and calibration: skip and continue are keyboard-reachable buttons; statuses are exactly the three allowed words', () => {
  const state = createScreenState();
  state.setup = F.setupVm();
  state.calibration = F.calibrationVm();
  const m = s(setupScreenView(state));
  assert.match(m, /<button type="button" class="kh-btn" data-fid="skip" data-cmd="\{&quot;type&quot;:&quot;skip&quot;\}">Skip setup/);
  assert.match(m, /data-fid="continue"/);
  assert.match(textOf(m), /Skip setup Esc/);
  assert.match(textOf(m), /Continue Return/);
  assert.match(textOf(m), /About two minutes\. Nothing here blocks the story\./);
  const chips = [...m.matchAll(/kh-chip (?:obs|skip|todo)">.*?<\/svg> ([^<]+)</g)].map((x) => x[1]);
  assert.deepEqual([...new Set(chips)].sort(), ['Not started', 'Observed output', 'Skipped']);
  assert.doesNotMatch(textOf(m), /detected|verified/i);
  assert.match(textOf(m), /observed output never proves which key you used/);
  assert.match(m, /aria-current="step"/);
  assert.equal((m.match(/class="su-step[" ]/g) || []).length, 5);
  assert.match(m, /Practice layer: unconfirmed/);
  assert.match(m, /data-autofocus/);
});

test('setup: keyboard cards state Selected and Not selected in words; Microsoft selection follows the view-model', () => {
  const state = createScreenState();
  state.setup = F.setupVm('microsoft');
  const m = s(setupScreenView(state));
  assert.match(m, /role="radio" aria-checked="false"[^>]*data-fid="kb-macbook"/);
  assert.match(m, /role="radio" aria-checked="true"[^>]*data-fid="kb-microsoft"/);
  assert.match(textOf(m), /Not selected/);
  assert.match(textOf(m), /Selected/);
  assert.match(m, /data-cmd="\{&quot;type&quot;:&quot;selectKeyboard&quot;,&quot;id&quot;:&quot;macbook&quot;\}"/);
});

test('calibration alone gets its own panel; the feedback card and diagram switch draw inside it', () => {
  const state = createScreenState();
  state.calibration = F.calibrationVm({ diagram: { positions: { rows: [[{ label: 'Caps', state: 'layer', width_u: 2 }, { label: 'H', state: 'target' }]], caption: 'Physical positions' }, characters: { rows: [[{ label: 'a', state: 'lit' }]], caption: 'Resulting characters' } } });
  state.feedback = { gesture: null, observed: 'ArrowLeft', effect: 'Step west', confidence: 'observed', confidenceLabel: 'Observed output' };
  const m = s(setupScreenView(state));
  assert.match(m, /data-screen="calibration"/);
  assert.match(m, /kh-fb observed/);
  assert.match(m, /kh-sk target/);
  assert.match(m, /data-ui="diagram" data-view="characters"/);
  state.diagramView = 'characters';
  assert.match(s(calibrationBody(state.calibration, state)), /kh-sk lit/);
});

// ---- Journal ------------------------------------------------------------------------------------------------------------
test('journal: level 01 active, then done with the Ride to the hub row', () => {
  const active = s(journalView(F.journalVm()));
  const done = s(journalView(F.journalDoneVm()));
  assert.match(textOf(active), /Main work.*01 The Lobby Active.*02 Badge Printer Locked/);
  assert.match(textOf(active), /Coworker requests/);
  assert.match(textOf(active), /Optional speed, Mira/);
  assert.match(textOf(done), /01 The Lobby Done/);
  assert.match(textOf(done), /Clearance seals 1 \/ 5/);
  assert.match(textOf(done), /Stars 3 \/ 3/);
  for (const m of [active, done]) {
    assert.match(m, /data-cmd="\{&quot;type&quot;:&quot;rideHub&quot;\}"/);
    assert.match(textOf(m), /Ride to the hub/);
    assert.match(m, /aria-current="true"/);
    assert.match(textOf(m), /Return opens the row/);
    assert.equal(markupProblem(m), null);
  }
  assert.match(active, /class="state active"/);
  assert.match(done, /class="state done"/);
  assert.match(active, /class="next"/);
  assert.match(textOf(active), /\(current\)/);
});

test('journal: also-from-here buttons carry layer commands; Q and Esc close hints are shown', () => {
  const m = s(journalView(F.journalVm()));
  for (const id of ['layout-help', 'settings', 'controls']) assert.match(m, new RegExp(`openLayer&quot;,&quot;id&quot;:&quot;${id}`));
  assert.match(textOf(m), /Close Esc tap Caps/);
});

// ---- Controls --------------------------------------------------------------------------------------------------------------
test('controls: one row per binding with key, gesture and a practice-layer note; static cards', () => {
  const m = s(controlsView(F.controlsVm()));
  assert.equal((m.match(/class="kh-crow" role="row"/g) || []).length, 3);
  assert.match(textOf(m), /Interact and continue Return tap-hold Caps \+ N Works on practice/);
  assert.match(textOf(m), /To open the journal, you need to press Q\. Hint: Q is tap Q\./);
  assert.match(textOf(m), /Never game keys/);
});

// ---- Settings -----------------------------------------------------------------------------------------------------------------
test('settings: each toggle changes the rendered output and sends the opposite value', () => {
  const base = s(settingsView(F.settingsVm()));
  const lt = s(settingsView(F.settingsVm({ largerText: true })));
  const hc = s(settingsView(F.settingsVm({ highContrast: true })));
  const rm = s(settingsView(F.settingsVm({ reducedMotion: 'on' })));
  const kb = s(settingsView(F.settingsVm({ keyboard: 'microsoft' })));
  for (const v of [lt, hc, rm, kb]) assert.notEqual(v, base);
  assert.match(base, /aria-checked="false"[^>]*data-setting="largerText"/);
  assert.match(lt, /role="switch" aria-checked="true"[^>]*data-setting="largerText"[^>]*&quot;value&quot;:false/);
  assert.match(hc, /role="switch" aria-checked="true"[^>]*data-setting="highContrast"/);
  assert.match(rm, /aria-pressed="true"[^>]*data-cmd="[^"]*reducedMotion[^"]*on/);
  assert.match(kb, /aria-pressed="true"[^>]*data-cmd="[^"]*keyboard[^"]*microsoft/);
  assert.match(textOf(lt), /Larger text.*?\. On High contrast/);
  assert.match(textOf(base), /Larger text.*?\. Off High contrast/);
});

test('settings: no audio controls; reset needs a confirmation card whose focus starts on Keep', () => {
  const m = s(settingsView(F.settingsVm()));
  assert.doesNotMatch(textOf(m), /sound|audio|music|effects|volume|mute/i);
  assert.doesNotMatch(m, /<audio|AudioContext|<video/i);
  assert.match(m, /resetProgress&quot;,&quot;confirmed&quot;:false/);
  assert.doesNotMatch(m, /confirmed&quot;:true/, 'no reset command before confirmation');
  const c = s(settingsView(F.settingsVm({ confirmReset: true })));
  assert.match(c, /data-fid="reset-keep" data-autofocus/);
  assert.match(c, /confirmed&quot;:true/);
  assert.match(textOf(c), /Keep my progress Esc/);
  assert.match(textOf(c), /Seals, stars, patches, artifacts and best scores are erased\. Your settings stay\./);
});
