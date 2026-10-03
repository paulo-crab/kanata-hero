// LayoutHelpViewModel builder. Contract: game/CONTRACTS.md 4.4 and 7 (vm:layout-help).
const TAB_LABELS = {
  base: 'Base',
  nav: 'Nav',
  'numbers-symbols': 'Numbers and symbols',
  practice: 'Practice',
};

const TOGGLE_KEYS = [
  { key: 'Control', label: 'Ctrl' },
  { key: 'Alt', label: 'Option' },
  { key: 'Meta', label: 'Command' },
  { key: 'v', label: 'V' },
];

/**
 * Short face names for the keys the diagrams draw. The manifest legend (Page ↑, Esc | nav) stays whole in the key
 * detail card; the key itself shows a short form so a 16 px label fits a 1u key: arrows glue to the word (Page↑), a
 * side letter moves to its own small line (Ctrl-L is Ctrl over L), long key names shorten (Backspace is Bksp).
 */
const FACE_NAMES = {
  Backspace: 'Bksp', Delete: 'Del', 'Shift-L': 'Shift', 'Shift-R': 'Shift',
  'Ctrl-L': 'Ctrl', 'Ctrl-R': 'Ctrl', 'Opt-L': 'Opt', 'Opt-R': 'Opt', 'Cmd-L': 'Cmd', 'Cmd-R': 'Cmd',
  Left: '←', Right: '→', Up: '↑', Down: '↓',
  'Alt-L': 'Alt', 'Alt-R': 'Alt', 'Win-L': 'Win', 'Win-R': 'Win',
};

/** The key's name as printed on a diagram key, and its side (L or R) when it has one. */
export function keyFace(id) {
  const name = FACE_NAMES[id] || id;
  const side = /-([LR])$/.exec(id);
  return { name, side: side ? side[1] : null };
}

/** Longest legend, in characters, a diagram key prints before it falls back to no sub-label (wide keys keep theirs). */
const MAX_SHORT = 8;

/** The manifest legend for a diagram key, shortened to fit: `Word →` is `Word→`, `Esc | nav` is `Esc/nav`. */
export function shortLegend(legend) {
  return String(legend || '')
    .replace(/\s+([←→↑↓])/g, '$1')
    .replace(/\s*\|\s*/g, '/')
    .replace(/^tap Space\/hold numbers$/, 'tap Space / hold numbers');
}

/** A legend that cannot fit its key (Left Control on a 1u key) is dropped; the detail card still says it. */
export function fitLegend(short, widthU) {
  return widthU < 3 && short.length > MAX_SHORT ? '' : short;
}

/** @param {import('./layout-manifest.js').LayoutManifest} manifest
 *  @param {{tab?:string, variant?:string, selectedKey?:string|null}} [state] */
export function layoutHelpModel(manifest, state = {}) {
  const tab = state.tab || 'base';
  const variant = state.variant || 'macbook';
  const selected = state.selectedKey || null;
  const kb = manifest.keyboard(variant);
  const keys = [];
  for (const row of kb.rows) {
    for (const k of row) {
      const at = manifest.keyAt(tab, k.id, variant);
      const face = keyFace(k.id);
      keys.push({
        id: k.id,
        name: face.name,
        side: face.side,
        row: k.row,
        x_u: k.x_u,
        width_u: k.width_u,
        ...(k.stack ? { height_u: k.height_u, stack: k.stack } : {}),
        legend: at.legend,
        short: fitLegend(shortLegend(at.legend), k.width_u),
        silent: at.silent,
        selected: k.id === selected,
        differs: at.differsFromBase,
      });
    }
  }
  let card = null;
  if (selected) {
    const d = manifest.keyDetail(tab, selected, variant);
    card = { label: d.label, lines: d.lines, verification: d.verification };
  }
  const seqs = manifest.sequences();
  const toggle = seqs.find((s) => s.id === 'violento-toggle');
  const exit = seqs.find((s) => s.id === 'emergency-exit');
  return {
    tab,
    tabs: manifest.tabs().map((id) => ({ id, label: TAB_LABELS[id] || id, selected: id === tab })),
    variant,
    variants: manifest.variants(),
    keys,
    card,
    toggleOut: { keys: TOGGLE_KEYS.map((k) => ({ ...k })), text: `${toggle.label}. ${toggle.note}` },
    emergencyExit: { text: `${exit.label}. ${exit.note}`, unverified: true },
  };
}
