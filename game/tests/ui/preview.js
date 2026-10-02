// Preview harness: mounts the real UI and feeds fixture view-models by URL hash. Dev only, not part of the game.
import { EventBus } from '/game/src/shared/index.js';
import { mountUi, VIEW_MODEL_TOPICS } from '/game/src/ui/index.js';
import * as B from './vm-builders.js';

const json = (p) => fetch(p).then((r) => r.json());
const [level, portraits, manifest] = await Promise.all([
  json('/design/levels/orientation/levels/01-the-lobby.json'),
  json('/art-direction/portraits/portraits-atlas.json'),
  json('/design/layout/layout-manifest.json'),
]);

const bus = new EventBus();
const ui = mountUi(document.getElementById('ui'), { bus, stage: document.getElementById('stage') });
window.__bus = bus;
window.__ui = ui;
const log = [];
bus.on('ui:command', (c) => log.push(c));
window.__commands = log;

const dlg = (id, o) => B.dialogueVmFrom(level, portraits, id, o);
const world = () => {
  bus.emit('vm:hud', B.hudVm());
  bus.emit('vm:markers', {
    markers: [
      { id: 'ivo', shape: 'conversation', state: 'idle', at: { x: 512, y: 110 } },
      { id: 'printer', shape: 'terminal', state: 'idle', at: { x: 678, y: 46 } },
      { id: 'door', shape: 'route', state: 'reached', at: { x: 1122, y: 270 } },
      { id: 'glitch', shape: 'glitch', state: 'idle', at: { x: 230, y: 204 } },
    ],
    floor: [{ id: 'f1', at: { x: 400, y: 360 }, state: 'teal', shape: 'route' }, { id: 'f2', at: { x: 480, y: 360 }, state: 'gold', shape: 'route' }],
  });
};

const screens = {
  world() {
    world();
    bus.emit('vm:prompt', { kind: 'device', action: 'Use the badge printer', key: B.RETURN, gesture: 'tap-hold Caps + N', at: { x: 812, y: 128 } });
    bus.emit('vm:inset', B.insetVm());
    bus.emit('vm:dialogue', dlg('o01.d.loop-right', { mode: 'instruction' }));
  },
  conversation() { world(); bus.emit('vm:inset', B.insetVm({ firstUse: true })); bus.emit('vm:dialogue', dlg('o01.d.welcome')); },
  'first-use'() {
    world();
    const row = ['Z', 'X', 'C', 'V', 'B', 'N', 'M'].map((l) => B.key(l));
    bus.emit('vm:inset', B.insetVm({ header: 'Continue', layer: 'nav layer · tap-hold Caps · 200 ms', firstUse: true, cells: {
      position: { keys: [], rows: [row, ['Caps', 'A', 'S', 'D', 'F', 'G', 'H', 'J'].map((l) => B.key(l, l === 'Caps' ? { held: true } : {}))], target: 'N' },
      order: [{ key: B.key('Caps', { held: true }), tag: 'Hold' }, { key: B.key('N'), tag: 'Tap' }],
      output: { key: B.RETURN, name: 'Return' }, effect: { text: 'Next line' } } }));
  },
  setup() { bus.emit('vm:setup', B.setupVm()); bus.emit('vm:calibration', B.calibrationVm({ diagram: {
    positions: { rows: [[{ label: 'Caps', state: 'layer', width_u: 2 }, ...['A', 'S', 'D', 'F', 'G', 'H'].map((l) => ({ label: l, state: l === 'H' ? 'target' : 'plain' }))]], caption: 'Physical positions: Caps held, H ringed.' },
    characters: { rows: [[{ label: 'Caps', state: 'layer', width_u: 2 }, { label: 'Left', state: 'target', width_u: 2 }]], caption: 'Resulting characters.' } } })); },
  calibration() { bus.emit('vm:calibration', B.calibrationVm()); bus.emit('vm:feedback', { gesture: 'tap-hold Caps + H', observed: 'ArrowLeft', effect: 'Step west', confidence: 'observed', confidenceLabel: 'Observed output' }); },
  controls() { bus.emit('vm:controls', B.controlsVm()); },
  journal() { world(); bus.emit('vm:journal', B.journalVm()); },
  'journal-done'() { world(); bus.emit('vm:hud', B.hudVm({ progress: { done: 4, total: 4 }, seals: { count: 1, total: 5 } })); bus.emit('vm:journal', B.journalDoneVm()); },
  settings() { bus.emit('vm:settings', B.settingsVm({ reducedMotion: 'system', largerText: false })); },
  'settings-reset'() { bus.emit('vm:settings', B.settingsVm({ confirmReset: true })); },
  toast() { world(); bus.emit('vm:toast', { text: 'Progress will not be saved on this device.', tone: 'warn' }); bus.emit('vm:toast', { text: 'Seal earned: Orientation', tone: 'info' }); },
  label() {
    world();
    bus.emit('vm:scene-bar', { kind: 'label', title: 'West desk label', prompt: 'To label the west desk, you need to type west.', field: { text: 'we', cursor: 2, target: 'west' }, leave: { key: B.ESC, gesture: 'tap Caps' } });
    bus.emit('vm:feedback', { gesture: null, observed: 'w e', effect: 'Typed two letters', confidence: 'observed', confidenceLabel: 'Observed output' });
    bus.emit('vm:inset', B.insetVm({ header: 'Type a letter', layer: 'base layer · plain taps' }));
  },
  editor() {
    world();
    bus.emit('vm:scene-bar', { kind: 'editor', title: 'Folded form', prompt: 'Move right four times, then type y.', field: { text: 'lobb', cursor: 4 }, nextLetter: 'y', leave: { key: B.ESC, gesture: 'tap Caps' } });
  },
  'hint-card'() { world(); bus.emit('vm:hint-card', { text: 'Using the hint here forfeits the third star for this scene. Press Return to show the hint, or Esc to keep it.', confirm: B.RETURN, cancel: B.ESC }); },
  error() { bus.emit('vm:error', { file: '/art-direction/kit/orientation-atlas.json', kind: 'missing', message: 'Cannot load /art-direction/kit/orientation-atlas.json: HTTP 404' }); },
};
for (const tab of ['base', 'nav', 'numbers-symbols', 'practice']) {
  screens[`layout-${tab}`] = () => { world(); bus.emit('vm:layout-help', B.fakeLayoutHelpModel(manifest, { tab, selectedKey: tab === 'nav' ? 'l' : tab === 'practice' ? 'Backspace' : 'f' })); };
}
screens['layout-microsoft'] = () => {
  world();
  const vm = B.fakeLayoutHelpModel(manifest, { variant: 'microsoft', selectedKey: 'Alt-L' });
  bus.emit('vm:layout-help', { ...vm, remap: manifest.keyboards.microsoft.remap.map((r) => ({ from: r.physical, to: r.becomes || r.output || r.label || '' })) });
};

function show(name) {
  for (const t of VIEW_MODEL_TOPICS) if (t !== 'vm:announce') bus.emit(t, null);
  (screens[name] || screens.world)();
  window.__current = name;
}
window.__show = show;
window.__screens = Object.keys(screens);
show((location.hash || '#world').slice(1));
window.addEventListener('hashchange', () => show(location.hash.slice(1)));
