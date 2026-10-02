// Layout manifest consumer. Contract: game/CONTRACTS.md 4.4. Reads design/layout/layout-manifest.json.
// Tabs are the manifest's layers. Nothing here claims to detect a layer or a physical key.
import { DataLoadError } from '../shared/index.js';
import { weakestConfidence } from './confidence.js';

const FILE = '/design/layout/layout-manifest.json';
const STACKED = new Set(['Up', 'Down']);

function shapeError(detail) {
  return new DataLoadError({ file: FILE, kind: 'shape', detail });
}

export class LayoutManifest {
  constructor(json) {
    if (!json || typeof json !== 'object') throw shapeError('not an object');
    for (const f of ['layers', 'keyboards', 'keys', 'sequences', 'practice', 'inventory']) {
      if (!(f in json)) throw shapeError(`missing field ${f}`);
    }
    this.json = json;
    this._keys = new Map(json.keys.map((k) => [k.id, k]));
    this._layers = new Map(json.layers.map((l) => [l.id, l]));
    this._inv = new Map(json.inventory.map((r) => [r.id, r]));
    this._remap = new Map(
      (json.keyboards.microsoft?.remap || []).map((r) => [r.physical, r]),
    );
  }

  tabs() {
    return this.json.layers.map((l) => l.id);
  }

  tabTitle(tab) {
    return this._layer(tab).title;
  }

  variants() {
    return Object.keys(this.json.keyboards).filter((k) => k !== 'default');
  }

  hasKey(id) {
    return this._keys.has(id);
  }

  /** Rows 1 to 4 from keys[].position, the bottom row from keyboards[variant].bottom_row. The F row is not drawn. */
  keyboard(variant) {
    const kb = this._variant(variant);
    const rows = [];
    for (let r = 1; r <= 4; r += 1) {
      rows.push(
        this.json.keys
          .filter((k) => k.position && k.position.row === r && k.keyboards.includes(variant))
          .sort((a, b) => a.position.column - b.position.column)
          .map((k) => ({ id: k.id, row: r, x_u: k.position.x_u, width_u: k.position.width_u })),
      );
    }
    // Bottom row: cumulative x. Up and Down share one slot (stacked half-height keys).
    const bottom = [];
    let x = 0;
    let stackX = null;
    for (const b of kb.bottom_row) {
      const entry = { id: b.id, row: 5, x_u: x, width_u: b.width_u };
      const own = variant === 'macbook' ? this._keys.get(b.id) : null;
      if (own && own.position) {
        // Manifest positions carry the half-unit gap before the arrows. Up and Down share one slot, but
        // the manifest counts them as two columns, so Right sits one unit left of its recorded x_u.
        x = own.position.x_u - (b.id === 'Right' ? 1 : 0);
        if (b.id === 'Down') x = stackX;
        entry.x_u = x;
      }
      if (STACKED.has(b.id)) {
        const pos = this._keys.get(b.id).position;
        entry.height_u = pos.height_u;
        entry.stack = pos.stack;
        if (stackX === null) {
          stackX = x;
          x += b.width_u;
        } else {
          entry.x_u = stackX;
        }
      } else {
        x += b.width_u;
      }
      bottom.push(entry);
    }
    rows.push(bottom);
    return { label: kb.label, rows };
  }

  keyAt(tab, keyId, variant = 'macbook') {
    this._layer(tab);
    this._variant(variant);
    const key = this._keys.get(keyId);
    if (!key) return this._bottomOnly(tab, keyId, variant);
    const entry = this._entry(key, tab, variant);
    const behaviour = entry.behaviour;
    const silent = behaviour === 'silent';
    let legend = entry.legend;
    if (!legend && silent) legend = 'XX';
    if (!legend && behaviour === 'inherits') {
      const under = key.layers[(entry.falls_to || ['base'])[0]];
      legend = (under && (under.legend || (under.tap && under.tap.label))) || key.label;
    }
    if (!legend) legend = (entry.tap && entry.tap.label) || key.label;
    return {
      id: key.id,
      label: key.label,
      legend,
      behaviour,
      tap: entry.tap ? { ...entry.tap } : null,
      hold: entry.hold ? { ...entry.hold, label: holdLabel(entry.hold) } : null,
      silent,
      differsFromBase: entry.differs_from_base === true,
      falls_to: entry.falls_to ? [...entry.falls_to] : null,
    };
  }

  keyDetail(tab, keyId, variant = 'macbook') {
    const at = this.keyAt(tab, keyId, variant);
    const key = this._keys.get(keyId);
    const entry = key ? this._entry(key, tab, variant) : {};
    const rows = key ? this._rowsFor(keyId, tab) : [];
    const lessons = {
      introduced: rows.length ? Math.min(...rows.map((r) => r.lessons.introduced)) : null,
      all: [...new Set(rows.flatMap((r) => r.lessons.all))].sort((a, b) => a - b),
      rows: rows.map((r) => r.id),
    };
    let verification;
    if (rows.length) verification = weakestConfidence(rows.map((r) => r.verification));
    else verification = at.silent ? 'external_only' : 'observed';
    const t = entry.timing || null;
    const timing = t
      ? {
          variant: t.variant,
          tap_timeout_ms: t.tap_timeout_ms,
          hold_ms: t.hold_ms,
          text: `Tap within ${t.tap_timeout_ms} ms; a hold counts from ${t.hold_ms} ms.`,
        }
      : null;
    const lines = [];
    if (at.silent) lines.push('Silent on this layer (XX): the original key sends nothing.');
    if (at.behaviour === 'inherits') lines.push(`Falls through to ${at.falls_to.join(' or ')}.`);
    if (at.tap) lines.push(`Tap: ${at.tap.label}`);
    if (at.hold) lines.push(`Hold: ${at.hold.label}${at.hold.after_ms ? ` after ${at.hold.after_ms} ms` : ''}`);
    if (timing) lines.push(timing.text);
    for (const ex of entry.exceptions || []) {
      if (ex.scope !== 'swedish') lines.push(`When ${ex.when}: ${ex.does}`);
    }
    if (at.differsFromBase) lines.push('Differs from the base layer.');
    return {
      id: at.id,
      label: at.label,
      tap: at.tap ? at.tap.label : null,
      hold: at.hold ? at.hold.label : null,
      timing,
      lessons,
      verification,
      lines,
    };
  }

  gesture(inventoryId) {
    const r = this._inv.get(inventoryId);
    if (!r) throw new RangeError(`Unknown gesture id: ${inventoryId}`);
    return {
      id: r.id,
      layer: r.layer,
      input: r.input,
      output: r.output,
      verification: r.verification,
      lessons: { ...r.lessons },
      observedEvents: ((r.observed && r.observed.events) || []).map((e) => ({ ...e })),
    };
  }

  /** violento-toggle, reload-config, emergency-exit. The emergency exit always carries unverified:true. */
  sequences() {
    return this.json.sequences.map((s) => ({
      id: s.id,
      label: s.label,
      action: s.action || null,
      verification: s.verification,
      status: s.status || null,
      note: s.note || '',
      unverified: s.id === 'emergency-exit' || s.status === 'present_unverified',
    }));
  }

  silencedInPractice() {
    return [...this.json.practice.silenced_keys];
  }

  _layer(tab) {
    const l = this._layers.get(tab);
    if (!l) throw new RangeError(`Unknown tab: ${tab}`);
    return l;
  }

  _variant(v) {
    const kb = this.json.keyboards[v];
    if (!kb || v === 'default') throw new RangeError(`Unknown keyboard variant: ${v}`);
    return kb;
  }

  _entry(key, tab, variant) {
    const e = key.layers[tab];
    const dv = variant === 'microsoft' && e.device_variants && e.device_variants.microsoft;
    return dv ? { ...e, ...dv } : e;
  }

  _rowsFor(keyId, tab) {
    return this.json.inventory.filter((r) => r.links.some((l) => l.key === keyId && l.layer === tab));
  }

  /** Microsoft bottom-row keys that are not manifest keys: remapped modifiers and Menu. */
  _bottomOnly(tab, keyId, variant) {
    const inRow = variant === 'microsoft' && this.json.keyboards.microsoft.bottom_row.some((b) => b.id === keyId);
    if (!inRow) throw new RangeError(`Unknown key: ${keyId}`);
    const r = this._remap.get(keyId);
    return {
      id: keyId,
      label: r ? r.label : keyId,
      legend: r ? r.legend : '',
      behaviour: r ? 'remap' : 'unmodelled',
      tap: r ? { kanata: r.emits, label: r.label } : null,
      hold: null,
      silent: false,
      differsFromBase: false,
      falls_to: null,
    };
  }
}

function holdLabel(h) {
  if (h.label) return h.label;
  if (h.output && h.output.label) return h.output.label;
  if (h.kind === 'layer') return `${h.layer} layer`;
  return h.kind;
}
