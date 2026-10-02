// Fixtures for the UI tests: real data files from the repo, and view-models shaped like the runtime's (contract 7).
// The fake layoutHelpModel below stands in for input.layoutHelpModel (workstream B): same output shape, built from the real manifest.
import { readFileSync } from 'node:fs';
import { fileURLToPath } from 'node:url';
import path from 'node:path';

const here = path.dirname(fileURLToPath(import.meta.url));
export const REPO = path.resolve(here, '..', '..', '..');
export const GAME = path.join(REPO, 'game');
export const read = (rel) => readFileSync(path.join(REPO, rel), 'utf8');
export const readJson = (rel) => JSON.parse(read(rel));

export const LEVEL = readJson('design/levels/orientation/levels/01-the-lobby.json');
export const MAP = readJson('design/levels/orientation/map.json');
export const DISTRICT = readJson('design/levels/orientation/district.json');
export const MANIFEST = readJson('design/layout/layout-manifest.json');
export const PORTRAITS = readJson('art-direction/portraits/portraits-atlas.json');

export const key = (label, extra = {}) => ({ key: label, label, ...extra });
export const RETURN = { key: 'Enter', label: 'Return' };
export const ESC = { key: 'Escape', label: 'Esc' };

/** Dialogue view-model for a level 01 dialogue id, the way the runtime builds it from the data. */
export function dialogueVm(id, { mode } = {}) {
  const d = LEVEL.dialogue.find((x) => x.id === id);
  if (!d) throw new Error(`no dialogue ${id}`);
  const conversation = mode ? mode === 'conversation' : d.modal !== false && !d.hint;
  const pk = `${d.speaker}_${d.portrait}`;
  return {
    id: d.id,
    speaker: d.speaker,
    speakerName: d.speaker[0].toUpperCase() + d.speaker.slice(1),
    role: 'Reception lead',
    portrait: PORTRAITS.portraits[pk] ? { key: pk, rect: PORTRAITS.portraits[pk] } : null,
    objectSpeaker: false,
    text: d.text,
    hint: d.hint,
    mode: conversation ? 'conversation' : 'instruction',
    footer: conversation
      ? [{ action: 'Continue', key: RETURN, gesture: 'tap-hold Caps + N' }, { action: 'Skip', key: ESC, gesture: 'tap Caps' }]
      : [],
  };
}

export const hudVm = (over = {}) => ({
  title: 'Visit the four desks',
  progress: { done: 2, total: 4 },
  seals: { count: 0, total: 5 },
  chips: [
    { id: 'hint', label: 'Hint', key: { key: 'Backquote', label: 'Backtick', glyph: '`' }, aria: 'Show hint. Key Backtick. Hint: Backtick is a plain tap.' },
    { id: 'journal', label: 'Journal', key: key('Q'), aria: 'Open the journal. Key Q. Hint: Q is tap Q.' },
    { id: 'layout-help', label: 'Layout help', key: key('?'), aria: 'Layout help. Key question mark. Hint: tap-hold F, then tap slash.' },
  ],
  ...over,
});

export const insetVm = (over = {}) => ({
  header: 'Move east',
  layer: 'nav layer · tap-hold Caps · 200 ms',
  cells: {
    position: {
      keys: ['Caps', 'A', 'S', 'D', 'F', 'G', 'H', 'J', 'K', 'L', ';', "'"].map((l) => key(l, l === 'Caps' ? { held: true } : {})),
      target: 'L',
    },
    order: [{ key: key('Caps', { held: true }), tag: 'Hold' }, { key: key('L'), tag: 'Tap' }],
    output: { key: { key: 'ArrowRight', label: 'Right' }, name: 'Right arrow' },
    effect: { text: 'Step east' },
  },
  firstUse: false,
  ...over,
});

export const calibrationVm = (over = {}) => ({
  steps: [
    { id: 'caps-h', gesture: 'Caps + H', expected: 'Left arrow', hintLine: 'To move left, you need to press Left Arrow. Hint: Left Arrow is tap-hold Caps + H.', status: 'observed', statusLabel: 'Observed output', current: false },
    { id: 'caps-n', gesture: 'Caps + N', expected: 'Return', hintLine: 'To continue, you need to press Return. Hint: Return is tap-hold Caps + N.', status: 'not_started', statusLabel: 'Not started', current: true },
    { id: 'space-a', gesture: 'Space + A', expected: '1', hintLine: 'Hint: 1 is tap-hold Space + A.', status: 'skipped', statusLabel: 'Skipped', current: false },
    { id: 'space-q', gesture: 'Space + Q', expected: '!', hintLine: 'Hint: ! is tap-hold Space + Q.', status: 'not_started', statusLabel: 'Not started', current: false },
    { id: 'shift-hold', gesture: 'F, then /', expected: '?', hintLine: 'Hint: ? is tap-hold F, then /.', status: 'not_started', statusLabel: 'Not started', current: false },
  ],
  diagramView: 'positions',
  toggleOut: { keys: ['Control', 'Alt', 'GUI', 'V'].map((l) => key(l)), text: 'To leave practice, you need to press Control + Alt + GUI + V.', practice: 'unconfirmed' },
  ...over,
});

export const setupVm = (keyboard = 'macbook') => ({
  keyboard,
  keyboards: [
    { id: 'macbook', label: 'MacBook', selected: keyboard === 'macbook' },
    { id: 'microsoft', label: 'Microsoft', selected: keyboard === 'microsoft' },
  ],
});

export const journalVm = (over = {}) => ({
  groups: [
    { id: 'main', heading: 'Main work', rows: [
      { id: 'o01', title: '01 The Lobby', state: 'active', detail: 'Ivo wants four desks visited before the first ticket.', selected: true },
      { id: 'o02', title: '02 Badge Printer', state: 'locked', detail: 'Opens after The Lobby.', selected: false },
    ] },
    { id: 'requests', heading: 'Coworker requests', rows: [{ id: 'r1', title: 'Plant Tags', state: 'locked', detail: 'Ivo asks for five typed labels.', selected: false }] },
    { id: 'speed', heading: 'Optional speed, Mira', rows: [{ id: 's1', title: 'Morning Mail', state: 'locked', detail: 'Needs: base taps and ordinary text.', selected: false }] },
  ],
  detail: {
    title: '01 The Lobby',
    steps: [
      { text: 'Close the welcome popup', state: 'done' },
      { text: 'Walk once around the garden', state: 'current' },
      { text: 'Visit the four desks', state: 'todo' },
    ],
    keys: [{ key: { key: 'ArrowDown', label: 'Down' }, output: 'Down arrow', gesture: 'tap-hold Caps + J' }],
    stars: 0,
  },
  seals: 0,
  also: [
    { id: 'layout-help', label: 'Layout help', key: key('?') },
    { id: 'settings', label: 'Settings' },
    { id: 'controls', label: 'Controls' },
    { id: 'ride-hub', label: 'Ride to the hub' },
  ],
  ...over,
});

/** The journal after level 01: row done, "Ride to the hub" available. */
export const journalDoneVm = () => {
  const vm = journalVm();
  vm.groups[0].rows[0] = { ...vm.groups[0].rows[0], state: 'done', detail: 'Complete. The turnstile is open.' };
  vm.groups[0].rows[1] = { ...vm.groups[0].rows[1], state: 'active', detail: 'Next: the badge printer.' };
  vm.detail = { ...vm.detail, steps: vm.detail.steps.map((s) => ({ ...s, state: 'done' })), stars: 3 };
  vm.seals = 1;
  return vm;
};

export const settingsVm = (over = {}) => ({ keyboard: 'macbook', reducedMotion: 'system', largerText: false, highContrast: false, confirmReset: false, ...over });

export const controlsVm = () => ({
  rows: [
    { action: 'Interact and continue', key: RETURN, gesture: 'tap-hold Caps + N', worksOnPractice: true },
    { action: 'Skip and back', key: ESC, gesture: 'tap Caps', worksOnPractice: true },
    { action: 'Journal', key: key('Q'), gesture: 'tap Q', worksOnPractice: true },
  ],
});

// ---- Fake input.layoutHelpModel over the real manifest --------------------------------------------------------------
const LAYER_KEY = { nav: 'Caps', 'numbers-symbols': 'Space' };
const TAB_LABEL = { base: 'base', nav: 'nav', 'numbers-symbols': 'numbers-symbols', practice: 'practice' };

export function fakeLayoutHelpModel(manifest, { tab = 'base', variant = 'macbook', selectedKey = null } = {}) {
  const keys = manifest.keys
    .filter((k) => k.position && k.keyboards.includes(variant))
    .map((k) => {
      const layer = k.layers[tab] || {};
      const silent = layer.behaviour === 'silent';
      const legend = silent ? 'XX' : (layer.legend ?? (layer.tap && layer.tap.label) ?? k.label);
      const differs = silent || layer.differs_from_base === true || (tab === 'base' && layer.behaviour === 'tap-hold');
      return {
        id: k.id, row: k.position.row, x_u: k.position.x_u, width_u: k.position.width_u,
        legend, silent, selected: k.id === selectedKey, differs, ...(LAYER_KEY[tab] === k.id ? { held: true } : {}),
      };
    });
  const sel = selectedKey && manifest.keys.find((k) => k.id === selectedKey);
  const layer = sel && sel.layers[tab];
  const toggle = manifest.sequences.find((s) => s.id === 'violento-toggle');
  const emergency = manifest.sequences.find((s) => s.id === 'emergency-exit');
  return {
    tab,
    tabs: Object.keys(TAB_LABEL).map((id) => ({ id, label: TAB_LABEL[id], selected: id === tab })),
    variant,
    variants: ['macbook', 'microsoft'],
    keys,
    card: sel ? {
      label: sel.label,
      lines: [`Tap: ${(layer && layer.tap && layer.tap.label) || sel.label}`, `On ${tab}: ${layer ? layer.legend || layer.behaviour : 'plain'}`],
      verification: 'observed',
    } : null,
    toggleOut: { keys: ['Control', 'Alt', 'GUI', 'V'].map((l) => key(l)), text: toggle.label },
    emergencyExit: { text: emergency.status === 'present_unverified' ? 'Shown after its runtime behaviour is verified.' : emergency.label, unverified: true },
  };
}
