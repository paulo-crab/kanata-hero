// Keyboard teaching inset view-model (vm:inset). Guided and variation scenes only: a scene whose phase is
// recall, or whose data says position_cue false, has no inset. Pure: scenes and data in, a view-model out.
// Key names, gestures and timings come from the level data, the gesture inventory and the layout manifest.
import { keycap } from './common.js';
import { phaseInfo } from './evidence.js';

const HOME_ROW = ['Caps', 'a', 's', 'd', 'f', 'g', 'h', 'j', 'k', 'l', ';', "'"];
const ARROW_OF_WORD = { Left: 'ArrowLeft', Right: 'ArrowRight', Up: 'ArrowUp', Down: 'ArrowDown' };
const DIR_WORD = { ArrowLeft: 'west', ArrowRight: 'east', ArrowUp: 'north', ArrowDown: 'south' };
const ARROW_NAME = { ArrowLeft: 'Left Arrow', ArrowRight: 'Right Arrow', ArrowUp: 'Up Arrow', ArrowDown: 'Down Arrow' };
const MINI_COLUMNS = 12;

function cleanLabel(id) {
  return id.replace(/-[LR]$/, '');
}

function miniKey(id, extra = {}) {
  const vm = id.length === 1 ? keycap(id) : { key: id, label: cleanLabel(id) };
  return { ...vm, ...extra };
}

/** The manifest keys of one physical row (left to right), at most MINI_COLUMNS. */
function rowIds(manifestJson, rowNumber) {
  return manifestJson.keys
    .filter((k) => k.position && k.position.row === rowNumber && k.keyboards.includes('macbook'))
    .sort((a, b) => a.position.column - b.position.column)
    .slice(0, MINI_COLUMNS)
    .map((k) => k.id);
}

function rowOf(manifestJson, keyId) {
  const k = manifestJson.keys.find((x) => x.id === keyId);
  return k && k.position ? k.position.row : null;
}

/** Position cell: one mini row, the home row, or the key's own row when the key is off the home row. */
function position(manifestJson, { target, held = [], lit = [] }) {
  const mark = (id) => miniKey(id, { ...(held.includes(id) ? { held: true } : {}), ...(lit.includes(id) ? { lit: true } : {}) });
  const id = target.length === 1 ? target.toLowerCase() : target;
  const row = rowOf(manifestJson, id);
  const homeRow = rowOf(manifestJson, 'h');
  const ids = row !== null && row !== homeRow ? rowIds(manifestJson, row) : HOME_ROW;
  return { keys: ids.map(mark), target: target.length === 1 ? target.toUpperCase() : target };
}

function timing(manifestJson, id) {
  return (manifestJson.timings || []).find((t) => t.id === id) || {};
}

function navLayer(manifestJson) {
  const t = timing(manifestJson, 'caps-hold');
  return `nav layer · tap-hold Caps · ${t.hold_ms || 200} ms`;
}

function outputOf(level, data, gestureId) {
  const row = ((data.gestureInventory && data.gestureInventory.rows) || []).find((r) => r.id === gestureId);
  const key = row ? ARROW_OF_WORD[row.output] : null;
  return key || null;
}

function moveInset(manifestJson, { arrow, tapKey }) {
  return {
    header: `Move ${DIR_WORD[arrow]}`,
    layer: navLayer(manifestJson),
    cells: {
      position: position(manifestJson, { target: tapKey.toUpperCase(), held: ['Caps'] }),
      order: [{ key: miniKey('Caps', { held: true }), tag: 'Hold' }, { key: keycap(tapKey), tag: 'Tap' }],
      output: { key: keycap(arrow), name: ARROW_NAME[arrow] },
      effect: { text: `Step ${DIR_WORD[arrow]}` },
    },
    firstUse: false,
  };
}

/** Variation: the whole nav cluster is shown, no single key is picked for the player. */
function clusterInset(manifestJson) {
  return {
    header: 'Move',
    layer: navLayer(manifestJson),
    cells: {
      position: position(manifestJson, { target: '', held: ['Caps'], lit: ['h', 'j', 'k', 'l'] }),
      order: [{ key: miniKey('Caps', { held: true }), tag: 'Hold' }, { key: { key: 'hjkl', label: 'H J K L' }, tag: 'Tap' }],
      output: { key: { key: 'Arrows', label: 'Arrows' }, name: 'Arrow keys' },
      effect: { text: 'Step on the grid' },
    },
    firstUse: false,
  };
}

function popupInset(manifestJson, def) {
  const t = timing(manifestJson, 'caps-hold');
  const effect = String((def.task && def.task.effect) || 'popup closes');
  return {
    header: 'Close the popup',
    layer: `base layer · tap Caps · ${t.tap_timeout_ms || 200} ms`,
    cells: {
      position: position(manifestJson, { target: 'Caps', lit: ['Caps'] }),
      order: [{ key: miniKey('Caps'), tag: 'Tap' }],
      output: { key: keycap('Escape'), name: 'Escape' },
      effect: { text: effect[0].toUpperCase() + effect.slice(1) },
    },
    firstUse: false,
  };
}

function typeInset(manifestJson, letter, header) {
  return {
    header,
    layer: 'base layer · plain tap, Caps released',
    cells: {
      position: position(manifestJson, { target: letter, lit: [letter] }),
      order: [{ key: keycap(letter), tag: 'Tap' }],
      output: { key: keycap(letter), name: letter },
      effect: { text: `Types ${letter}` },
    },
    firstUse: false,
  };
}

/**
 * @param {{level:object, data:object, manifestJson:object, layers:object[]}} p  layers: the scene stack, bottom first
 * @returns {object|null} InsetViewModel, or null on recall, on overlays and when no scene teaches a key
 */
export function insetViewModel({ level, data, manifestJson, layers }) {
  for (let i = layers.length - 1; i >= 0; i -= 1) {
    const s = layers[i];
    if (s.kind === 'dialogue') continue;
    if (!s.def) return null;
    const def = s.def;
    if (def.position_cue === false || phaseInfo(level, def.id).phase === 'recall') return null;
    if (s.kind === 'form') return popupInset(manifestJson, def);
    if (s.kind === 'label') {
      const next = s.target[s.text.length] || s.target[s.target.length - 1];
      return typeInset(manifestJson, next, 'Type the label');
    }
    if (s.kind === 'editor') {
      if (s.cursor < s.text.length) return moveInset(manifestJson, { arrow: 'ArrowRight', tapKey: 'l' });
      return typeInset(manifestJson, s.target[s.target.length - 1], 'Finish the word');
    }
    if (s.kind === 'walk') {
      const legs = def.task && def.task.legs;
      if (!legs) return clusterInset(manifestJson);
      const leg = legs[Math.min(s.idx, legs.length - 1)];
      const arrow = outputOf(level, data, leg.gesture_id);
      const tapKey = String(leg.key || '').split('+').pop().trim().toLowerCase();
      return arrow && tapKey ? moveInset(manifestJson, { arrow, tapKey }) : clusterInset(manifestJson);
    }
    return null;
  }
  return null;
}
