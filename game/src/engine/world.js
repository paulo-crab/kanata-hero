// World state: placements, state sets, collision, gates, npcs, glitch, avatar. Contract section 3.3.
// Knows nothing about keys, levels, scenes or the DOM. Time comes only from update(stepMs).
import { CELL_STEPS, TILE } from '../shared/index.js';
import { AnimationPlayer, frameForSteps } from './animation.js';
import { Avatar, DIRS } from './avatar.js';
import { computeCamera } from './camera.js';
import { shapeError } from './loader.js';

const LAYERS = ['rear_wall', 'floor_marking', 'rear_prop', 'shadow', 'actor', 'front_prop', 'light'];
const SHADOW_OUTER = '#3A4160';
const SHADOW_CORE = '#1C2038';
const LAMP_BREATH_MS = 600;
const FACINGS = ['n', 's', 'e', 'w'];

/** Contact shadow rectangles under a person anchored at feet (x, y), as drawn by gate1 `contact_shadow`. */
export function personShadow(x, y) {
  return [
    { x: x - 6, y: y - 1, w: 12, h: 1, color: SHADOW_OUTER },
    { x: x - 4, y: y - 1, w: 8, h: 1, color: SHADOW_CORE },
    { x: x - 5, y, w: 10, h: 1, color: SHADOW_OUTER },
  ];
}

/** Contact shadow for a glitch or prop: one outer row with a core, from the atlas {x0, x1, row}. */
export function glitchShadow(left, top, shadow, lift = 0) {
  const shrink = lift >= 2 ? 2 : 0;
  const x0 = left + shadow.x0 + shrink;
  const x1 = left + shadow.x1 - shrink;
  const y = top + shadow.row;
  const rects = [{ x: x0, y, w: x1 - x0, h: 1, color: SHADOW_OUTER }];
  if (x1 - x0 > 2) rects.push({ x: x0 + 1, y, w: x1 - x0 - 2, h: 1, color: SHADOW_CORE });
  return rects;
}

function facingOfPose(pose, fallback) {
  const last = pose.slice(pose.lastIndexOf('_') + 1);
  return FACINGS.includes(last) ? last : fallback;
}

export class World {
  /**
   * @param {object} data GameData
   * @param {object} atlases AtlasSet
   * @param {{bus?:{emit:Function}, random?:()=>number, reducedMotion?:boolean, avatarCharacter?:string, spawn?:string}} [opts]
   */
  constructor(data, atlases, opts = {}) {
    this.data = data;
    this.atlases = atlases;
    this.bus = opts.bus ?? null;
    this._random = opts.random ?? (() => 0);
    this.reducedMotion = !!opts.reducedMotion;
    const map = data.map;
    this.map = map;
    [this.cols, this.rows] = map.size_cells;
    this.timeMs = 0;
    this.steps = 0;
    this._markers = [];
    this._dirty = true;
    this._grid = null;

    this._base = map.collision.map((row) => [...row].map((c) => c === '1'));

    // Placements with a state (state sets and landmarks).
    this._ps = new Map();
    for (const p of map.placements) {
      if (p.state_set) {
        this._ps.set(p.id, { def: p, kind: 'set', set: atlases.stateSet(p.state_set), state: p.state ?? atlases.stateSet(p.state_set).default, play: null });
      } else if (p.landmark) {
        const lm = atlases.landmark(p.landmark);
        this._ps.set(p.id, { def: p, kind: 'landmark', lm, state: p.state ?? lm.default_state, play: null });
      }
    }

    this._gates = new Map(map.gates.map((g) => [g.id, { def: g, open: false }]));

    // Avatar.
    const spawn = map.spawns.find((s) => s.id === (opts.spawn ?? 'arrival')) ?? map.spawns[0];
    this.avatarCharacter = opts.avatarCharacter ?? 'engineer';
    this.avatar = new Avatar({
      isBlocked: (x, y) => this.isBlocked(x, y),
      cell: spawn.cell,
      facing: spawn.facing,
      onStep: (e) => this._emit('engine:step-complete', e),
      onBlocked: (e) => this._emit('engine:blocked', e),
    });
    this._avatarIdle = new AnimationPlayer(this._avatarAnim('idle'), { reducedMotion: this.reducedMotion });
    this._avatarIdleFacing = this.avatar.facing;

    // Npcs.
    this._npcs = new Map();
    for (const def of map.npcs) {
      const n = { def, id: def.id, character: def.character, cell: [...def.start_cell], facing: def.facing, state: null, pose: null, visible: true, player: null, patrolling: false };
      this._npcs.set(def.id, n);
      this._applyNpcState(n, 'poses_by_state' in def && def.poses_by_state.start ? 'start' : Object.keys(def.poses_by_state ?? {})[0]);
    }

    this._glitches = [];
    this._floorDraws = null;
  }

  // ---------------------------------------------------------------- events

  _emit(topic, payload) {
    if (this.bus) this.bus.emit(topic, payload);
  }

  setReducedMotion(on) {
    this.reducedMotion = !!on;
    this._avatarIdle.setReducedMotion(on);
    for (const n of this._npcs.values()) n.player?.setReducedMotion(on);
  }

  setMarkers(markers) {
    this._markers = markers ?? [];
  }

  // ---------------------------------------------------------------- placements and state sets

  placementState(id) {
    return this._ps.get(id)?.state ?? null;
  }

  setPlacementState(id, state) {
    const ps = this._ps.get(id);
    if (!ps) throw new Error(`placement "${id}" has no state`);
    const states = ps.kind === 'set' ? ps.set.states : ps.lm.states;
    if (!states[state]) throw new Error(`placement "${id}" has no state "${state}"`);
    ps.play = null;
    ps.state = state;
    this._dirty = true;
  }

  /** Play states in order, one per ms_per_frame; emits engine:stateset-done at the last one. */
  playStateSet(id, sequence, opts = {}) {
    const ps = this._ps.get(id);
    if (!ps || ps.kind !== 'set') throw new Error(`placement "${id}" is not a state set`);
    const seq = opts.reverse ? [...sequence].reverse() : [...sequence];
    for (const s of seq) if (!ps.set.states[s]) throw new Error(`placement "${id}" has no state "${s}"`);
    ps.state = seq[0];
    this._dirty = true;
    if (seq.length === 1) {
      ps.play = null;
      this._emit('engine:stateset-done', { placement: id, state: seq[0] });
      opts.onDone?.();
      return;
    }
    ps.play = { seq, i: 0, acc: 0, ms: ps.set.ms_per_frame ?? 120, onDone: opts.onDone ?? null };
  }

  _tickPlays(stepMs) {
    for (const [id, ps] of this._ps) {
      const p = ps.play;
      if (!p) continue;
      p.acc += stepMs;
      while (p.acc >= p.ms - 1e-9 && p.i < p.seq.length - 1) {
        p.acc -= p.ms;
        p.i += 1;
        ps.state = p.seq[p.i];
        this._dirty = true;
      }
      if (p.i === p.seq.length - 1) {
        ps.play = null;
        this._emit('engine:stateset-done', { placement: id, state: ps.state });
        p.onDone?.();
      }
    }
  }

  // ---------------------------------------------------------------- gates and collision

  openGate(gateId) {
    const g = this._gates.get(gateId);
    if (!g) throw new Error(`unknown gate "${gateId}"`);
    if (g.open) return;
    g.open = true;
    this._dirty = true;
    const ps = this._ps.get(g.def.placement);
    if (!ps) return;
    if (ps.kind === 'landmark') {
      if (ps.lm.states.after) this.setPlacementState(g.def.placement, 'after');
    } else if (ps.set.states.open) {
      if (ps.set.play && ps.set.play.includes('open')) this.playStateSet(g.def.placement, ps.set.play);
      else this.setPlacementState(g.def.placement, 'open');
    }
  }

  isGateOpen(gateId) {
    const g = this._gates.get(gateId);
    if (!g) throw new Error(`unknown gate "${gateId}"`);
    return g.open;
  }

  _entryCells(entryName, px, py) {
    const e = this.atlases.kitEntry(entryName);
    const out = [];
    e.collision.forEach((row, ry) => [...row].forEach((c, rx) => {
      if (c === '1') out.push([Math.floor(px / TILE) + rx, Math.floor(py / TILE) + ry]);
    }));
    return out;
  }

  _setCells(ps, state) {
    const entries = ps.set.states[state].entries;
    const cells = new Set();
    for (const name of entries) {
      if (!this.atlases.hasKitEntry(name)) continue;
      for (const [x, y] of this._entryCells(name, ps.def.cell[0] * TILE + (ps.def.offset?.[0] ?? 0), ps.def.cell[1] * TILE + (ps.def.offset?.[1] ?? 0))) cells.add(`${x},${y}`);
    }
    return cells;
  }

  _rebuild() {
    const grid = this._base.map((row) => row.slice());
    const set = (key, v) => {
      const [x, y] = key.split(',').map(Number);
      if (y >= 0 && y < this.rows && x >= 0 && x < this.cols) grid[y][x] = v;
    };
    // State sets: doors free the cells their closed state blocks; other sets add what they block.
    for (const ps of this._ps.values()) {
      if (ps.kind !== 'set') continue;
      const isDoor = Object.values(ps.set.states).some((s) => 'blocked' in s);
      const current = this._setCells(ps, ps.state);
      if (isDoor) {
        const closed = this._setCells(ps, ps.set.default);
        for (const k of closed) if (!current.has(k)) set(k, false);
      } else {
        for (const k of current) set(k, true);
      }
    }
    for (const g of this._gates.values()) {
      if (!g.open) continue;
      for (const [x, y] of g.def.cells) set(`${x},${y}`, false);
    }
    // Ordinary props left behind by repaired glitches.
    for (const gl of this._glitches) {
      if (gl.phase !== 'ordinary' && gl.phase !== 'repaired') continue;
      const rec = this.atlases.glitch(gl.archetype).ordinary;
      rec.collision.forEach((row, ry) => [...row].forEach((c, rx) => {
        if (c === '1') set(`${gl.cell[0] + rx},${gl.cell[1] + ry}`, true);
      }));
    }
    // Standing npcs block their cell; patrolling workers are ambient and never block.
    for (const n of this._npcs.values()) {
      if (n.visible && !n.def.patrol) set(`${n.cell[0]},${n.cell[1]}`, true);
    }
    this._grid = grid;
    this._dirty = false;
  }

  /** True when the cell cannot be entered. Out of range is blocked. */
  isBlocked(x, y) {
    if (!Number.isInteger(x) || !Number.isInteger(y) || x < 0 || y < 0 || x >= this.cols || y >= this.rows) return true;
    if (this._dirty) this._rebuild();
    return this._grid[y][x];
  }

  // ---------------------------------------------------------------- npcs

  _applyNpcState(n, state) {
    const pose = n.def.poses_by_state?.[state];
    if (!pose) throw new Error(`npc "${n.id}" has no state "${state}"`);
    const wasPatrolling = n.patrolling;
    n.state = state;
    n.pose = pose;
    n.visible = true;
    const cell = n.def.cells_by_state?.[state];
    if (cell) n.cell = [...cell];
    else if (wasPatrolling) n.cell = [...n._patrolCell ?? n.cell];
    n.facing = facingOfPose(pose, n.facing);
    n.patrolling = !!n.def.patrol && /_walk_/.test(pose);
    const def = this.atlases.animation(pose);
    const offset = this.atlases.animation(pose).variant ? Math.floor(this._random() * 1000) : 0;
    n.player = new AnimationPlayer(def, { reducedMotion: this.reducedMotion, startOffsetMs: offset });
    this._dirty = true;
  }

  setNpcState(npcId, state) {
    const n = this._npcs.get(npcId);
    if (!n) throw new Error(`unknown npc "${npcId}"`);
    this._applyNpcState(n, state);
  }

  npc(npcId) {
    const n = this._npcs.get(npcId);
    if (!n) return null;
    return { id: n.id, character: n.character, cell: [...n.cell], facing: n.facing, pose: n.pose, visible: n.visible, state: n.state };
  }

  _updateNpcs() {
    for (const n of this._npcs.values()) {
      if (!n.patrolling) continue;
      const path = n.def.patrol;
      const seg = Math.floor(this.steps / CELL_STEPS) % path.length;
      const from = path[seg];
      const to = path[(seg + 1) % path.length];
      n._patrolCell = from;
      n.cell = [...from];
      const dx = Math.sign(to[0] - from[0]);
      const dy = Math.sign(to[1] - from[1]);
      n.facing = dx > 0 ? 'e' : dx < 0 ? 'w' : dy > 0 ? 's' : 'n';
      n.pose = `${n.character}_walk_${n.facing}`;
    }
  }

  _npcFeet(n) {
    let x = n.cell[0] * TILE + TILE / 2;
    let y = n.cell[1] * TILE + TILE;
    if (n.patrolling) {
      const path = n.def.patrol;
      const seg = Math.floor(this.steps / CELL_STEPS) % path.length;
      const from = path[seg];
      const to = path[(seg + 1) % path.length];
      const t = this.steps % CELL_STEPS;
      x = from[0] * TILE + TILE / 2 + Math.sign(to[0] - from[0]) * t;
      y = from[1] * TILE + TILE + Math.sign(to[1] - from[1]) * t;
    }
    return { x, y };
  }

  // ---------------------------------------------------------------- glitch

  _glitchSource(interactionId) {
    const lg = this.data.level?.glitch;
    if (lg && lg.interaction === interactionId) return { archetype: lg.archetype, cell: lg.cell };
    const it = this.map.interactions.find((i) => i.id === interactionId && i.kind === 'glitch');
    if (it && lg) return { archetype: lg.archetype, cell: it.cells[0] };
    throw new Error(`no glitch for interaction "${interactionId}"`);
  }

  /** Put the level's glitch in the world, roaming. Idempotent. */
  spawnGlitch(interactionId) {
    const existing = this._glitches.find((g) => g.id === interactionId);
    if (existing) return existing;
    const src = this._glitchSource(interactionId);
    const rec = this.atlases.glitch(src.archetype);
    const cx = src.cell[0] * TILE + TILE / 2;
    const free = (dx) => !this.isBlocked(src.cell[0] + dx, src.cell[1]);
    const lo = free(-1) ? cx - TILE : cx;
    const hi = free(1) ? cx + TILE : cx;
    const gl = {
      id: interactionId,
      archetype: src.archetype,
      cell: [...src.cell],
      phase: 'roam',
      x: cx,
      y: src.cell[1] * TILE + TILE,
      lo,
      hi,
      dir: hi > cx ? 1 : -1,
      player: new AnimationPlayer(this.atlases.animation(rec.animations.roam)),
      lastFrame: 0,
      snapMs: 0,
      rec,
    };
    this._glitches.push(gl);
    return gl;
  }

  glitch(interactionId) {
    const g = this._glitches.find((x) => x.id === interactionId);
    if (!g) return null;
    return { id: g.id, archetype: g.archetype, phase: g.phase, cell: [...g.cell], x: g.x, y: g.y };
  }

  /** Snap into register: the repaired frame for its ms, then the ordinary prop stays. */
  repairGlitch(interactionId) {
    const g = this._glitches.find((x) => x.id === interactionId);
    if (!g) throw new Error(`no glitch spawned for "${interactionId}"`);
    if (g.phase !== 'roam') return;
    g.phase = 'repaired';
    g.snapMs = 0;
    g.cell = [Math.min(this.cols - 1, Math.max(0, Math.floor(g.x / TILE))), g.cell[1]];
    g.snapDef = this.atlases.animation(g.rec.animations.repaired);
    this._dirty = true;
    this._emit('engine:glitch-repaired', { interaction: interactionId });
  }

  _updateGlitches(stepMs) {
    for (const g of this._glitches) {
      if (g.phase === 'roam') {
        g.player.update(stepMs);
        const def = this.atlases.animation(g.rec.animations.roam);
        const frame = g.player.frameIndex;
        // Move by the per-frame distance each time a new frame starts (reduced motion holds still).
        if (!this.reducedMotion) {
          const cycleFrame = Math.floor(g.player._t / def.ms);
          while ((g._moved ?? 0) < cycleFrame) {
            g._moved = (g._moved ?? 0) + 1;
            const step = def.move_px_per_frame[(g._moved - 1) % def.frames];
            let nx = g.x + g.dir * step;
            if (nx >= g.hi || nx <= g.lo) {
              nx = Math.min(g.hi, Math.max(g.lo, nx));
              g.dir = -g.dir;
            }
            g.x = nx;
          }
        }
        g.lastFrame = frame;
      } else if (g.phase === 'repaired') {
        g.snapMs += stepMs;
        if (g.snapMs >= g.snapDef.ms) {
          g.phase = 'ordinary';
          g.cell = [Math.floor(g.x / TILE), g.cell[1]];
          this._dirty = true;
        }
      }
    }
  }

  // ---------------------------------------------------------------- update

  _avatarAnim(set) {
    const name = `${this.avatarCharacter}_${set}_${this.avatar?.facing ?? 's'}`;
    return this.atlases.animation(name);
  }

  /** One fixed sim step. */
  update(stepMs) {
    this.timeMs += stepMs;
    this.steps += 1;
    this._tickPlays(stepMs);
    const wasMoving = this.avatar.moving;
    this.avatar.update();
    if (this.avatar.moving || wasMoving) this._avatarIdle.reset();
    else {
      if (this.avatar.facing !== this._avatarIdleFacing) {
        this._avatarIdleFacing = this.avatar.facing;
        this._avatarIdle = new AnimationPlayer(this._avatarAnim('idle'), { reducedMotion: this.reducedMotion });
      }
      this._avatarIdle.update(stepMs);
    }
    for (const n of this._npcs.values()) n.player?.update(stepMs);
    this._updateNpcs();
    this._updateGlitches(stepMs);
  }

  // ---------------------------------------------------------------- snapshot

  camera() {
    return this._cameraOverride || computeCamera(this.avatar.feetPx, this.data.district.camera_bounds);
  }

  /** A camera chosen by the look-ahead (map px, already clamped); null returns to the avatar-centred camera. */
  setCameraOverride(camera) {
    this._cameraOverride = camera ? { x: camera.x, y: camera.y } : null;
  }

  /** The avatar-centred camera, ignoring any override. */
  baseCamera() {
    return computeCamera(this.avatar.feetPx, this.data.district.camera_bounds);
  }

  _kitDraw(name, fx, fy, atlas = 'kit') {
    const e = this.atlases.kitEntry(name);
    const [ox, oy] = e.footprint.origin_px;
    const y = fy - oy;
    return {
      layer: e.layer,
      draw: {
        atlas,
        rect: { x: e.rect[0], y: e.rect[1], w: e.size_px[0], h: e.size_px[1] },
        x: fx - ox,
        y,
        anchorY: y + e.anchor[1],
        ySort: !!e.y_sort,
        composite: e.composite?.mode === 'where_color' ? e.composite : undefined,
      },
    };
  }

  _paceDraw(name, fx, fy) {
    const e = this.atlases.paceEntry(name);
    const [ox, oy] = e.origin_px;
    const y = fy - oy;
    return {
      layer: e.layer,
      draw: {
        atlas: 'pace',
        rect: { x: e.rect[0], y: e.rect[1], w: e.rect[2], h: e.rect[3] },
        x: fx - ox,
        y,
        anchorY: y + e.anchor.y,
        ySort: e.layer === 'rear_prop',
      },
    };
  }

  _breathing(stateName) {
    // Pulse lamps breathe between the wider and the steady glow; reduced motion holds the wider pulse.
    if (stateName !== 'pulse' || this.reducedMotion) return stateName;
    return Math.floor(this.timeMs / LAMP_BREATH_MS) % 2 === 0 ? 'pulse' : 'on';
  }

  _placementItems(ps, fx, fy, out) {
    if (ps.kind === 'set') {
      const state = ps.set.loop ? this._breathing(ps.state) : ps.state;
      for (const name of ps.set.states[state].entries) out.push(this._kitDraw(name, fx, fy));
    } else {
      const st = ps.lm.states[ps.state];
      for (const name of st.parts) out.push(this._kitDraw(name, fx, fy));
      if (st.lamps) {
        const lampSet = this.atlases.stateSet(st.lamps.anim);
        const lampState = this._breathing(st.lamps.state);
        for (const [dx, dy] of st.lamps.offsets_px) {
          for (const name of lampSet.states[lampState].entries) out.push(this._kitDraw(name, fx + dx, fy + dy));
        }
      }
    }
  }

  _floorDrawList() {
    if (this._floorDraws) return this._floorDraws;
    const list = [];
    const legend = this.map.floor_legend;
    this.map.floor.forEach((row, cy) => [...row].forEach((ch, cx) => {
      const name = legend[ch];
      const item = this._kitDraw(name, cx * TILE, cy * TILE);
      list.push(item.draw);
    }));
    this._floorDraws = list;
    return list;
  }

  _personDraw(animName, frame, feet) {
    const def = this.atlases.animation(animName);
    return {
      atlas: def.atlas,
      rect: { x: def.x + frame * def.frame.w, y: def.y, w: def.frame.w, h: def.frame.h },
      x: feet.x - def.frame.w / 2,
      y: feet.y - def.frame.h,
      anchorY: feet.y,
      ySort: true,
      shadow: personShadow(feet.x, feet.y),
    };
  }

  /** Avatar animation name and frame index right now. */
  avatarFrame() {
    const a = this.avatar;
    if (a.moving) {
      const name = `${this.avatarCharacter}_walk_${a.facing}`;
      return { name, frame: frameForSteps(this.atlases.animation(name), a.walkSteps - 1 < 0 ? 0 : a.walkSteps - 1) };
    }
    return { name: `${this.avatarCharacter}_idle_${a.facing}`, frame: this._avatarIdle.frameIndex };
  }

  /** Drawable snapshot for the renderer: {floor, layers, markers, camera}. */
  snapshot() {
    const layers = Object.fromEntries(LAYERS.map((l) => [l, []]));
    const floor = [...this._floorDrawList()];
    const items = [];
    for (const p of this.map.placements) {
      const fx = p.cell[0] * TILE + (p.offset?.[0] ?? 0);
      const fy = p.cell[1] * TILE + (p.offset?.[1] ?? 0);
      const ps = this._ps.get(p.id);
      if (ps) this._placementItems(ps, fx, fy, items);
      else if (p.entry) {
        if (this.atlases.hasKitEntry(p.entry)) items.push(this._kitDraw(p.entry, fx, fy));
        else items.push(this._paceDraw(p.entry, fx, fy));
      }
    }
    for (const it of items) {
      if (it.layer === 'floor') floor.push(it.draw);
      else layers[it.layer].push(it.draw);
    }

    const actors = [];
    const addShadow = (rects, anchorY) => layers.shadow.push({ atlas: null, rects, x: 0, y: 0, anchorY, ySort: false });

    for (const n of this._npcs.values()) {
      if (!n.visible) continue;
      const feet = this._npcFeet(n);
      const def = this.atlases.animation(n.pose);
      const frame = n.patrolling ? frameForSteps(def, this.steps) : n.player.frameIndex;
      const d = this._personDraw(n.pose, frame, feet);
      addShadow(d.shadow, feet.y);
      delete d.shadow;
      actors.push(d);
    }

    const av = this.avatarFrame();
    const feet = this.avatar.feetPx;
    const ad = this._personDraw(av.name, av.frame, feet);
    addShadow(ad.shadow, feet.y);
    delete ad.shadow;
    actors.push(ad);

    for (const g of this._glitches) {
      const w = g.rec.frame.w;
      const h = g.rec.frame.h;
      let animName = g.rec.animations.roam;
      let frame = g.player.frameIndex;
      let lift = 0;
      if (g.phase === 'repaired') { animName = g.rec.animations.repaired; frame = 0; }
      else if (g.phase === 'ordinary') { animName = g.rec.animations.ordinary; frame = 0; }
      else lift = this.atlases.animation(animName).lift_px?.[frame] ?? 0;
      const def = this.atlases.animation(animName);
      const left = g.x - w / 2;
      const top = g.y - h - lift;
      actors.push({
        atlas: 'glitches',
        rect: { x: def.x + frame * w, y: def.y, w, h },
        x: left,
        y: top,
        anchorY: g.y,
        ySort: true,
      });
      addShadow(glitchShadow(left, g.y - h, g.rec.contact_shadow, lift), g.y);
    }
    layers.actor.push(...actors);

    return { floor, layers, markers: this._markers.map((m) => ({ ...m })), camera: this.camera() };
  }

  // ---------------------------------------------------------------- persistence

  serialize() {
    const placements = {};
    for (const [id, ps] of this._ps) placements[id] = ps.state;
    const npcs = {};
    // Patrolling workers run on the shared clock, so only their state is stored.
    for (const n of this._npcs.values()) {
      npcs[n.id] = n.patrolling ? { state: n.state } : { state: n.state, cell: [...n.cell], facing: n.facing };
    }
    const gates = {};
    for (const [id, g] of this._gates) gates[id] = g.open;
    const glitches = this._glitches.map((g) => ({ id: g.id, phase: g.phase === 'repaired' ? 'ordinary' : g.phase, x: g.x }));
    return { placements, npcs, gates, avatar: { cell: [...this.avatar.cell], facing: this.avatar.facing }, glitches };
  }

  /** Restore without animating. Unknown ids are ignored so older documents still load. */
  restore(slice) {
    if (!slice) return;
    for (const [id, state] of Object.entries(slice.placements ?? {})) {
      const ps = this._ps.get(id);
      const states = ps ? (ps.kind === 'set' ? ps.set.states : ps.lm.states) : null;
      if (states?.[state]) { ps.state = state; ps.play = null; }
    }
    for (const [id, g] of Object.entries(slice.gates ?? {})) {
      const gate = this._gates.get(id);
      if (gate) gate.open = !!g;
    }
    for (const [id, s] of Object.entries(slice.npcs ?? {})) {
      const n = this._npcs.get(id);
      if (!n || !n.def.poses_by_state?.[s.state]) continue;
      this._applyNpcState(n, s.state);
      if (s.cell && !n.patrolling) n.cell = [...s.cell];
      if (s.facing) n.facing = s.facing;
    }
    if (slice.glitches) this._glitches = [];
    for (const gs of slice.glitches ?? []) {
      let g;
      try { g = this.spawnGlitch(gs.id); } catch { continue; }
      g.x = gs.x ?? g.x;
      if (gs.phase === 'ordinary') {
        g.phase = 'ordinary';
        g.cell = [Math.floor(g.x / TILE), g.cell[1]];
      }
    }
    if (slice.avatar) this.avatar.teleport(slice.avatar.cell, slice.avatar.facing);
    this._avatarIdleFacing = this.avatar.facing;
    this._avatarIdle = new AnimationPlayer(this._avatarAnim('idle'), { reducedMotion: this.reducedMotion });
    this._dirty = true;
  }
}

export { DIRS };
export { shapeError };
