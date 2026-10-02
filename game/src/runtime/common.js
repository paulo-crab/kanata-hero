// Small shared helpers for runtime modules: key names, keycap view-models, key copy.

export const DIR_OUTPUT = { n: 'ArrowUp', s: 'ArrowDown', e: 'ArrowRight', w: 'ArrowLeft' };
export const OUTPUT_DIR = { ArrowUp: 'n', ArrowDown: 's', ArrowRight: 'e', ArrowLeft: 'w' };
export const DIR_DELTA = { n: [0, -1], s: [0, 1], e: [1, 0], w: [-1, 0] };

const LABELS = {
  Enter: 'Return', Escape: 'Esc', ArrowLeft: 'Left Arrow', ArrowRight: 'Right Arrow',
  ArrowUp: 'Up Arrow', ArrowDown: 'Down Arrow', Backquote: 'Backtick', Space: 'Space',
};

export function keycap(output, extra = {}) {
  const label = LABELS[output] || (output.length === 1 ? output.toUpperCase() : output);
  const vm = { key: output, label, ...extra };
  if (output === 'Backquote') vm.glyph = '`';
  return vm;
}

/** Human name of an observed event: 'Left Arrow', 'Option + Right Arrow'. */
export function observedName(ev) {
  const base = LABELS[ev.output] || ev.output;
  const mods = [];
  if (ev.mods && ev.mods.ctrl) mods.push('Control');
  if (ev.mods && ev.mods.alt) mods.push('Option');
  if (ev.mods && ev.mods.meta) mods.push('Command');
  if (!mods.length && typeof ev.combo === 'string' && ev.combo.includes('+') && ev.combo !== ev.output) {
    for (const m of ev.combo.split('+').slice(0, -1)) mods.push(m === 'Alt' ? 'Option' : m === 'Meta' ? 'Command' : m);
  }
  return mods.length ? `${mods.join(' + ')} + ${base.replace(' Arrow', '')}` : base;
}

/** Kanata gestures of the six game keys (design/ui-key-bindings.md). */
export const KEY_GESTURE = {
  interact: 'tap-hold Caps + N',
  continue: 'tap-hold Caps + N',
  skip: 'tap Caps',
  back: 'tap Caps',
  move: 'tap-hold Caps + H, J, K, L',
  hint: 'tap Backtick',
  journal: 'tap Q',
  layoutHelp: 'tap-hold F (Shift), then tap /',
};

export const CONFIDENCE_LABEL = {
  'output-observed': 'Output observed',
  'player-confirmed': 'Player confirmed',
  'external-only': 'External only',
};

export const CONFIDENCE_KEY = {
  'output-observed': 'observed',
  'player-confirmed': 'player_confirmed',
  'external-only': 'external_only',
};

export function isModifierOrCommand(ev) {
  return ev.output === 'Backquote' || ev.output === '?';
}

/** 4-neighbour BFS distances to `target` over cells where isBlocked is false. */
export function distanceMap(target, isBlocked, w = 28, h = 18) {
  const dist = new Map();
  const key = (x, y) => y * w + x;
  const q = [[target[0], target[1]]];
  dist.set(key(target[0], target[1]), 0);
  for (let i = 0; i < q.length; i += 1) {
    const [x, y] = q[i];
    const d = dist.get(key(x, y));
    for (const [dx, dy] of Object.values(DIR_DELTA)) {
      const nx = x + dx;
      const ny = y + dy;
      if (nx < 0 || ny < 0 || nx >= w || ny >= h || dist.has(key(nx, ny)) || isBlocked(nx, ny)) continue;
      dist.set(key(nx, ny), d + 1);
      q.push([nx, ny]);
    }
  }
  return (c) => {
    const v = dist.get(key(c[0], c[1]));
    return v === undefined ? Infinity : v;
  };
}
