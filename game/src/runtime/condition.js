// Condition grammar of design/levels/SCHEMA.md. Contract: game/CONTRACTS.md section 5.3.
// Pure: no state, no time. Atoms are joined by ' & '; any_of and count are group atoms.

export const ATOM_NAMES = [
  'scene_success', 'dialogue_done', 'interact', 'step_done', 'step_start', 'reach_cell',
  'level_complete', 'trigger', 'request', 'state', 'player_confirm',
];

function parseAtom(text) {
  const i = text.indexOf(':');
  if (i <= 0) throw new Error(`Bad condition atom "${text}"`);
  const name = text.slice(0, i);
  const arg = text.slice(i + 1).trim();
  if (!ATOM_NAMES.includes(name)) throw new Error(`Unknown condition atom "${name}" in "${text}"`);
  if (!arg) throw new Error(`Condition atom "${text}" has no argument`);
  if (name === 'reach_cell' && !/^\d+,\d+$/.test(arg)) throw new Error(`Bad cell in "${text}"`);
  return { type: 'atom', name, arg };
}

function parseGroup(text, kind) {
  let n = 1;
  let rest;
  if (kind === 'any_of') {
    rest = text.slice('any_of:'.length);
  } else {
    const m = /^count:(\d+):(.*)$/.exec(text);
    if (!m) throw new Error(`Bad count group "${text}"`);
    n = Number(m[1]);
    rest = m[2];
  }
  const atoms = rest.split('|').map((s) => parseAtom(s.trim()));
  if (atoms.length < 2) throw new Error(`Group "${text}" needs two or more alternatives`);
  if (n < 1 || n > atoms.length) throw new Error(`Group "${text}" has an impossible count`);
  return { type: kind, n, atoms };
}

/** @returns {{type:'all', terms:Array}} empty terms for an empty string */
export function parseCondition(str) {
  if (typeof str !== 'string') throw new Error('Condition must be a string');
  const text = str.trim();
  if (!text) return { type: 'all', terms: [] };
  const terms = text.split(' & ').map((raw) => {
    const t = raw.trim();
    if (t.startsWith('any_of:')) return parseGroup(t, 'any_of');
    if (t.startsWith('count:')) return parseGroup(t, 'count');
    return parseAtom(t);
  });
  return { type: 'all', terms };
}

export function atomKey(atom) {
  return `${atom.name}:${atom.arg}`;
}

/** All atoms (flattened) of a parsed condition. */
export function atomsOf(ast) {
  const out = [];
  for (const t of ast.terms) {
    if (t.type === 'atom') out.push(t);
    else out.push(...t.atoms);
  }
  return out;
}

/** @param {(key:string)=>boolean} has  true when the atom's fact happened */
export function evaluate(ast, has) {
  return ast.terms.every((t) => {
    if (t.type === 'atom') return has(atomKey(t));
    const hits = t.atoms.filter((a) => has(atomKey(a))).length;
    return t.type === 'any_of' ? hits >= 1 : hits >= t.n;
  });
}
