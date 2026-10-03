// Browser-safe view-model builders (no node imports): shared by the node tests and the preview page.
export const key = (label, extra = {}) => ({ key: label, label, ...extra });
export const RETURN = { key: 'Enter', label: 'Return' };
export const ESC = { key: 'Escape', label: 'Esc' };

/** Dialogue view-model for a level 01 dialogue id, the way the runtime builds it from the data. */
export function dialogueVmFrom(LEVEL, PORTRAITS, id, { mode } = {}) {
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

const STEPS = [
  ['caps-h', 'Caps + H', 'Left Arrow', 'To move left, you need to press Left Arrow.', ['Caps', 'H']],
  ['caps-n', 'Caps + N', 'Return', 'To interact or continue, you need to press Return.', ['Caps', 'N']],
  ['space-a', 'Space + A', '1', 'To type the digit one, you need to press 1.', ['Space', 'A']],
  ['space-q', 'Space + Q', '!', 'To type an exclamation mark, you need to press !.', ['Space', 'Q']],
  ['shift-hold', 'F, then /', '?', 'To type a question mark, you need to press ?.', ['F', '/']],
];

/** One-step calibration view-model. `statuses` lists the five step statuses; the first not_started step is current. */
export const calibrationVm = (over = {}) => {
  const statuses = over.statuses || ['observed', 'not_started', 'not_started', 'not_started', 'not_started'];
  const label = { not_started: 'Not started', observed: 'Observed output', skipped: 'Skipped' };
  const cur = statuses.findIndex((x) => x === 'not_started');
  const steps = STEPS.map(([id, gesture, expectedName, action, keys], i) => ({
    id, number: i + 1, gesture, expected: expectedName, expectedName, action, hintLine: `${action} Hint: ${expectedName} is ${gesture}.`,
    keys: keys.map((k, j) => ({ key: k, label: k, ...(j === 0 ? { held: true } : {}) })),
    status: statuses[i], statusLabel: label[statuses[i]], current: i === cur,
  }));
  const { statuses: _drop, ...rest } = over;
  return {
    keyboard: 'macbook',
    phase: cur < 0 ? 'summary' : 'steps',
    stepCount: 5,
    steps,
    current: cur < 0 ? null : { ...steps[cur], waiting: `Waiting for ${steps[cur].expectedName}` },
    lastSeen: null, wrong: null, success: null, confirm: false,
    skipStep: { key: { key: 'ArrowDown', label: 'Down' }, gesture: 'tap-hold Caps + J' },
    skipAll: { key: { key: 'ArrowUp', label: 'Up' }, gesture: 'tap-hold Caps + K' },
    diagram: null,
    diagramView: 'positions',
    toggleOut: { keys: ['Control', 'Alt', 'GUI', 'V'].map((l) => key(l)), text: 'To leave practice, you need to press Control + Alt + GUI + V.', practice: 'unconfirmed' },
    ...rest,
  };
};

export const setupVm = (keyboard = 'macbook') => ({
  keyboard,
  keyboards: [
    { id: 'macbook', label: 'MacBook', selected: keyboard === 'macbook' },
    { id: 'microsoft', label: 'Microsoft', selected: keyboard === 'microsoft' },
  ],
  confirm: false,
  diagram: { positions: { rows: [[{ label: 'Caps', state: 'plain', width_u: 2 }, { label: 'H', state: 'plain' }]], caption: 'The MacBook keyboard as the game draws it.' } },
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
