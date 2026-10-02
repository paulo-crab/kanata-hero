// Progress store: one versioned localStorage document. Contract: game/CONTRACTS.md section 5.7.
export const PROGRESS_KEY = 'kanata-hero:progress';

const ID_LISTS = [
  ['flags', 'flags'], ['levelsDone', 'levels_done'], ['seals', 'seals'], ['artifacts', 'artifacts'],
  ['patches', 'patches'], ['miraRoutesCleared', 'mira_routes_cleared'],
];

export class ProgressStore {
  /** @param {{storage?:object, world:object, bus:object}} p world is the world.json document */
  constructor({ storage, world, bus } = {}) {
    this.storage = storage || null;
    this.world = world || { version: '0', state_ids: {} };
    this.bus = bus;
    this._persistent = !!storage;
    this._warned = false;
    this.doc = this._fresh();
  }

  get persistent() {
    return this._persistent;
  }

  _fresh() {
    return {
      schema: 1,
      worldVersion: this.world.version,
      settings: { keyboard: 'macbook', reducedMotion: 'system', largerText: false, highContrast: false },
      setup: { done: false, calibration: null },
      flags: [], levelsDone: [], seals: [], artifacts: [], patches: [], miraRoutesCleared: [],
      npc: {}, placements: {}, gatesOpen: [], levels: {}, journal: [], hintUse: [], best: {},
    };
  }

  _toast(text, tone = 'warn') {
    if (this.bus) this.bus.emit('vm:toast', { text, tone });
  }

  _storageFailed() {
    this._persistent = false;
    if (!this._warned) {
      this._warned = true;
      this._toast('Progress will not be saved in this browser.');
    }
  }

  _read() {
    if (!this.storage) return null;
    try {
      return this.storage.getItem(PROGRESS_KEY);
    } catch {
      this._storageFailed();
      return null;
    }
  }

  _clean(doc) {
    const out = this._fresh();
    const ids = this.world.state_ids || {};
    out.settings = { ...out.settings, ...(doc.settings || {}) };
    out.setup = { done: !!(doc.setup && doc.setup.done), calibration: (doc.setup && doc.setup.calibration) || null };
    for (const [field, key] of ID_LISTS) {
      const allowed = ids[key];
      const list = Array.isArray(doc[field]) ? doc[field] : [];
      out[field] = [...new Set(list.filter((x) => typeof x === 'string' && (!allowed || allowed.includes(x))))];
    }
    const strMap = (m) => Object.fromEntries(Object.entries(m || {}).filter(([, v]) => typeof v === 'string'));
    out.npc = strMap(doc.npc);
    out.placements = strMap(doc.placements);
    out.gatesOpen = (Array.isArray(doc.gatesOpen) ? doc.gatesOpen : []).filter((x) => typeof x === 'string');
    out.levels = doc.levels && typeof doc.levels === 'object' ? doc.levels : {};
    out.journal = (Array.isArray(doc.journal) ? doc.journal : []).filter((x) => typeof x === 'string');
    out.hintUse = Array.isArray(doc.hintUse) ? doc.hintUse : [];
    out.best = doc.best && typeof doc.best === 'object' ? doc.best : {};
    this._syncFlags(out);
    return out;
  }

  _syncFlags(d) {
    const ids = (this.world.state_ids || {}).flags;
    const set = new Set(d.flags);
    for (const f of ['keyboard-macbook', 'keyboard-microsoft', 'setup-done', 'calibration-done']) set.delete(f);
    set.add(`keyboard-${d.settings.keyboard === 'microsoft' ? 'microsoft' : 'macbook'}`);
    if (d.setup.done) set.add('setup-done');
    if (d.setup.calibration) set.add('calibration-done');
    d.flags = [...set].filter((f) => !ids || ids.includes(f));
  }

  load() {
    const raw = this._read();
    if (raw === null || raw === undefined) {
      this.doc = this._fresh();
      return this.doc;
    }
    let parsed;
    try {
      parsed = JSON.parse(raw);
    } catch {
      this._toast('Saved progress could not be read, so a new game started.');
      this.doc = this._fresh();
      return this.doc;
    }
    if (!parsed || parsed.schema !== 1) {
      this._toast('Saved progress is from another version, so a new game started.');
      this.doc = this._fresh();
      return this.doc;
    }
    this.doc = this._clean(parsed);
    return this.doc;
  }

  save(doc) {
    if (doc) this.doc = doc;
    this._syncFlags(this.doc);
    if (this.storage) {
      try {
        this.storage.setItem(PROGRESS_KEY, JSON.stringify(this.doc));
      } catch {
        this._storageFailed();
      }
    }
    if (this.bus) this.bus.emit('progress:saved', { persistent: this._persistent });
  }

  update(mutator) {
    mutator(this.doc);
    this.save();
    return this.doc;
  }

  /** After confirmation only. */
  reset() {
    if (this.storage) {
      try {
        this.storage.removeItem(PROGRESS_KEY);
      } catch {
        this._storageFailed();
      }
    }
    this.doc = this._fresh();
    if (this.bus) this.bus.emit('progress:reset', {});
  }

  hasProgress() {
    const raw = this._read();
    if (!raw) return false;
    try {
      const d = JSON.parse(raw);
      return !!(d && d.schema === 1 && ((d.setup && d.setup.done) || (d.levelsDone || []).length
        || Object.keys(d.levels || {}).length));
    } catch {
      return false;
    }
  }
}
