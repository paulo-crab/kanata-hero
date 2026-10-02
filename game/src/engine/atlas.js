// Atlas loading and lookup. Contract section 3.1, formats in art-direction/ART_HANDOFF.md section 3.
import { DataLoadError } from '../shared/index.js';
import { ATLAS_FILES, DATA_FILES, PERSON_ATLASES } from './files.js';
import { loadJson, shapeError } from './loader.js';

function defaultMode(name) {
  if (/_(idle|walk)(_|$)/.test(name)) return 'loop';
  if (/_react_/.test(name)) return 'hold';
  return 'once';
}

export class AtlasSet {
  /**
   * @param {{[id:string]: {json:object, image:any, file?:string}}} atlases parsed JSON plus loaded image per atlas id
   */
  constructor(atlases) {
    this._atlases = atlases;
    this._kitEntries = new Map();
    this._anims = new Map();
    const kit = atlases.kit?.json;
    if (kit) for (const e of kit.entries) this._kitEntries.set(e.name, e);
    for (const id of PERSON_ATLASES) this._indexPerson(id);
    this._indexGlitches();
  }

  _file(id) {
    return this._atlases[id]?.file ?? ATLAS_FILES[id]?.json ?? id;
  }

  _json(id) {
    const a = this._atlases[id];
    if (!a) throw shapeError(ATLAS_FILES[id]?.json ?? id, `atlas "${id}" is not loaded`);
    return a.json;
  }

  _indexPerson(id) {
    const a = this._atlases[id];
    if (!a) return;
    const { frame, animations, variants } = a.json;
    const add = (name, raw, extra = {}) => {
      this._anims.set(name, {
        name,
        atlas: id,
        row: raw.row,
        frames: raw.frames,
        ms: raw.ms,
        mode: raw.mode ?? defaultMode(name),
        frame: { w: frame.w, h: frame.h },
        x: 0,
        y: raw.row * frame.h,
        px_per_frame: raw.px_per_frame,
        contact_frames: raw.contact_frames,
        ...extra,
      });
    };
    for (const [name, raw] of Object.entries(animations)) add(name, raw);
    for (const [name, raw] of Object.entries(variants ?? {})) add(name, raw, { variant: true });
  }

  _indexGlitches() {
    const a = this._atlases.glitches;
    if (!a) return;
    for (const [name, raw] of Object.entries(a.json.animations)) {
      this._anims.set(name, {
        name,
        atlas: 'glitches',
        archetype: raw.archetype,
        row: raw.row,
        frames: raw.frames,
        ms: raw.ms ?? 0,
        mode: raw.static ? 'hold' : raw.loop === false ? 'once' : 'loop',
        frame: { w: raw.frame.w, h: raw.frame.h },
        x: raw.x,
        y: raw.y,
        move_px_per_frame: raw.move_px_per_frame,
        lift_px: raw.lift_px,
        then: raw.then,
      });
    }
  }

  image(id) {
    const a = this._atlases[id];
    if (!a) throw shapeError(ATLAS_FILES[id]?.png ?? id, `atlas "${id}" is not loaded`);
    return a.image;
  }

  hasKitEntry(name) {
    return this._kitEntries.has(name);
  }

  kitEntry(name) {
    const e = this._kitEntries.get(name);
    if (!e) throw shapeError(this._file('kit'), `unknown kit entry "${name}"`);
    return e;
  }

  hasPaceEntry(name) {
    return !!this._atlases.pace?.json.entries?.[name];
  }

  /** Pace signage entry: {rect:[x,y,w,h], footprint_cells, origin_px, anchor, layer, collision_cells, state}. */
  paceEntry(name) {
    const e = this._atlases.pace?.json.entries?.[name];
    if (!e) throw shapeError(this._file('pace'), `unknown pace entry "${name}"`);
    return e;
  }

  stateSet(name) {
    const s = this._json('kit').animations[name];
    if (!s) throw shapeError(this._file('kit'), `unknown state set "${name}"`);
    return s;
  }

  hasStateSet(name) {
    return !!this._atlases.kit?.json.animations?.[name];
  }

  landmark(name) {
    const l = this._json('kit').landmarks[name];
    if (!l) throw shapeError(this._file('kit'), `unknown landmark "${name}"`);
    return l;
  }

  hasAnimation(name) {
    return this._anims.has(name);
  }

  /** Normalised animation by full name: {name, atlas, row, frames, ms, mode, frame:{w,h}, x, y, ...}. */
  animation(name) {
    const a = this._anims.get(name);
    if (!a) throw shapeError('art-direction/ (atlas JSON files)', `unknown animation "${name}"`);
    return a;
  }

  /** @returns {{id:string, frame:{w:number,h:number}, anchor:{x:number,y:number}, animations:object}} */
  personAtlas(characterId) {
    const a = this._atlases[characterId];
    if (!a || !PERSON_ATLASES.includes(characterId)) {
      throw shapeError(ATLAS_FILES[characterId]?.json ?? characterId, `no person atlas for "${characterId}"`);
    }
    return { id: characterId, frame: a.json.frame, anchor: a.json.anchor, animations: a.json.animations };
  }

  portrait(key) {
    const p = this._json('portraits').portraits[key];
    if (!p) throw shapeError(this._file('portraits'), `unknown portrait "${key}"`);
    return p;
  }

  /** Archetype record plus the names of its animations. */
  glitch(archetype) {
    const g = this._json('glitches');
    const rec = g.archetypes[archetype];
    if (!rec) throw shapeError(this._file('glitches'), `unknown glitch archetype "${archetype}"`);
    return {
      archetype,
      ...rec,
      animations: {
        roam: `${archetype}_roam`,
        misregister: `${archetype}_misregister`,
        repaired: `${archetype}_repaired`,
        ordinary: `${archetype}_ordinary`,
      },
    };
  }
}

const PEOPLE_SHAPE = ['frame', 'animations', 'anchor'];
const SHAPES = {
  kit: ['entries', 'animations', 'landmarks'],
  glitches: ['archetypes', 'animations'],
  pace: ['entries'],
  portraits: ['portraits'],
};

function validateAtlasJson(id, file, json) {
  const need = PERSON_ATLASES.includes(id) ? PEOPLE_SHAPE : SHAPES[id] ?? [];
  if (!json || typeof json !== 'object') throw shapeError(file, 'expected a JSON object');
  for (const k of need) if (json[k] === undefined) throw shapeError(file, `missing "${k}"`);
  if (id === 'kit' && !Array.isArray(json.entries)) throw shapeError(file, '"entries" must be an array');
}

/** Every placement entry, state set, landmark and npc pose named by the map must exist. */
export function validateMapAgainstAtlases(atlases, map, mapFile = DATA_FILES.map) {
  for (const p of map.placements) {
    if (p.entry && !atlases.hasKitEntry(p.entry) && !atlases.hasPaceEntry(p.entry)) {
      throw shapeError(mapFile, `placement "${p.id}": entry "${p.entry}" is in no atlas`);
    }
    if (p.state_set) {
      if (!atlases.hasStateSet(p.state_set)) throw shapeError(mapFile, `placement "${p.id}": unknown state set "${p.state_set}"`);
      const states = atlases.stateSet(p.state_set).states;
      if (p.state !== undefined && !states[p.state]) throw shapeError(mapFile, `placement "${p.id}": state set "${p.state_set}" has no state "${p.state}"`);
    }
    if (p.landmark) {
      let lm;
      try { lm = atlases.landmark(p.landmark); } catch { throw shapeError(mapFile, `placement "${p.id}": unknown landmark "${p.landmark}"`); }
      if (p.state && !lm.states[p.state]) throw shapeError(mapFile, `placement "${p.id}": landmark "${p.landmark}" has no state "${p.state}"`);
    }
  }
  for (const n of map.npcs) {
    for (const [state, pose] of Object.entries(n.poses_by_state ?? {})) {
      if (!atlases.hasAnimation(pose)) throw shapeError(mapFile, `npc "${n.id}": state "${state}" names unknown animation "${pose}"`);
    }
  }
}

/** @param {{fetchFn?:Function, baseUrl?:string, loadImage?:(url:string)=>Promise<any>, map?:object}} opts */
export async function loadAtlasSet(opts = {}) {
  const loadImage = opts.loadImage ?? ((url) => new Promise((resolve, reject) => {
    const img = new Image();
    img.onload = () => resolve(img);
    img.onerror = () => reject(new Error('image failed to load'));
    img.src = url;
  }));
  const base = opts.baseUrl ?? '/';
  const loaded = {};
  for (const [id, files] of Object.entries(ATLAS_FILES)) {
    const json = await loadJson(files.json, opts);
    validateAtlasJson(id, files.json, json);
    const url = !base || base === '/' ? files.png : base.replace(/\/+$/, '') + files.png;
    let image;
    try {
      image = await loadImage(url);
    } catch (error) {
      throw new DataLoadError({ file: files.png, kind: 'missing', detail: String(error?.message ?? error) });
    }
    loaded[id] = { json, image, file: files.json };
  }
  const set = new AtlasSet(loaded);
  const map = opts.map ?? (await loadJson(DATA_FILES.map, opts));
  validateMapAgainstAtlases(set, map);
  return set;
}
