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
      keys.push({
        id: k.id,
        row: k.row,
        x_u: k.x_u,
        width_u: k.width_u,
        legend: at.legend,
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
