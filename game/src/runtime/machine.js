// Scene state machine. Contract: game/CONTRACTS.md sections 5.1 and 5.2.

export const TRANSITIONS = {
  setup: ['calibration', 'hub', 'arrival', 'error'],
  calibration: ['arrival', 'hub', 'error'],
  arrival: ['hub', 'dialogue', 'error'],
  hub: ['dialogue', 'walk', 'label', 'form', 'editor', 'layout-help', 'journal', 'controls', 'settings', 'error'],
  dialogue: ['hub', 'walk', 'label', 'form', 'editor', 'layout-help'],
  walk: ['dialogue', 'label', 'form', 'layout-help', 'journal'],
  label: ['layout-help'],
  form: ['layout-help'],
  editor: ['layout-help'],
  journal: ['layout-help', 'controls', 'settings'],
  settings: ['setup'],
  'layout-help': [],
  controls: [],
  error: [],
};

/** Topic a scene kind's view-model is published on (dialogue is published by DialogueRuntime). */
export const VM_TOPIC = {
  setup: 'vm:setup', calibration: 'vm:calibration', form: 'vm:scene-bar', label: 'vm:scene-bar',
  editor: 'vm:scene-bar', walk: 'vm:scene-bar', 'layout-help': 'vm:layout-help', journal: 'vm:journal',
  controls: 'vm:controls', settings: 'vm:settings', error: 'vm:error',
};

const OVERLAYS = new Set(['journal', 'layout-help', 'controls', 'settings']);

const DEFAULT_KEYS = {
  typing: false, enter: 'none', esc: 'none', arrows: 'none', journal: false, hint: false,
  layoutHelp: true, surfaceFocused: true, consumes: [],
};

export class SceneMachine {
  /** @param {object} ctx SceneContext (the machine adds ctx.machine) @param {{[kind:string]:(payload:object)=>object}} factories */
  constructor(ctx, factories) {
    this.ctx = ctx;
    this.factories = factories;
    this.layers = [];
    this._saved = new WeakMap();
    this._vms = new Map();
    ctx.machine = this;
  }

  get top() {
    return this.layers[this.layers.length - 1] || null;
  }

  get stack() {
    return [...this.layers];
  }

  canPush(kind) {
    const top = this.top;
    return !top || (TRANSITIONS[top.kind] || []).includes(kind);
  }

  _make(kind, payload) {
    const f = this.factories[kind];
    if (!f) throw new Error(`No scene factory for "${kind}"`);
    const scene = f(payload || {});
    if (scene.kind !== kind) throw new Error(`Factory for "${kind}" built a "${scene.kind}" scene`);
    return scene;
  }

  push(kind, payload) {
    const top = this.top;
    if (top && !this.canPush(kind)) throw new Error(`Illegal scene transition ${top.kind} -> ${kind}`);
    if (top) this._saved.set(top, top.snapshot ? top.snapshot() : undefined);
    const scene = this._make(kind, payload);
    this.layers.push(scene);
    scene.enter(this.ctx, payload || {});
    this.ctx.bus.emit('scene:enter', { id: scene.id, kind });
    this._after();
    return scene;
  }

  pop(result) {
    const top = this.layers.pop();
    if (!top) return undefined;
    const exitResult = { ...(top.exit() || {}), ...(result || {}) };
    this.ctx.bus.emit('scene:exit', { id: top.id, result: exitResult });
    const below = this.top;
    if (below) {
      below.enter(this.ctx, { restore: this._saved.get(below) });
      // Publish first: the UI only returns focus once the closed layer's view-model is gone.
      this.publish();
      this.ctx.bus.emit('ui:restore-focus', { sceneId: below.id });
    }
    this._after();
    return exitResult;
  }

  replace(kind, payload) {
    const top = this.top;
    if (top && !this.canPush(kind)) throw new Error(`Illegal scene transition ${top.kind} -> ${kind}`);
    if (top) {
      this.layers.pop();
      const res = top.exit() || {};
      this.ctx.bus.emit('scene:exit', { id: top.id, result: res });
    }
    const scene = this._make(kind, payload);
    this.layers.push(scene);
    scene.enter(this.ctx, payload || {});
    this.ctx.bus.emit('scene:enter', { id: scene.id, kind });
    this._after();
    return scene;
  }

  /** Top layer first; a modal layer stops propagation. Returns true when consumed. */
  handle(ev) {
    let consumed = false;
    for (let i = this.layers.length - 1; i >= 0; i -= 1) {
      const layer = this.layers[i];
      if (layer.handle(ev)) {
        consumed = true;
        break;
      }
      if (layer.modal) break;
    }
    this._sweep();
    this.publish();
    return consumed;
  }

  /** Engine events (step-complete, blocked, stateset-done) reach live layers, top first, until a modal one. */
  notifyEngine(topic, payload) {
    for (let i = this.layers.length - 1; i >= 0; i -= 1) {
      const layer = this.layers[i];
      if (layer.onEngine) layer.onEngine(topic, payload);
      if (layer.modal && !layer.passEngine) break;
    }
    this._sweep();
    this.publish();
  }

  update(stepMs) {
    for (let i = this.layers.length - 1; i >= 0; i -= 1) {
      const layer = this.layers[i];
      layer.update(stepMs);
      if (layer.modal) break;
    }
    this._sweep();
    this.publish();
  }

  /** Pop or replace the top layer when it reports it is finished (scene.finished). */
  _sweep() {
    for (let guard = 0; guard < 20; guard += 1) {
      const top = this.top;
      if (!top || !top.finished) return;
      const fin = top.finished;
      top.finished = null;
      if (fin.next) this.replace(fin.next, fin.payload);
      else this.pop(fin);
    }
  }

  inputContext() {
    const top = this.top;
    if (!top) return { ...DEFAULT_KEYS, sceneId: 'none' };
    return { ...DEFAULT_KEYS, ...(top.keys || {}), sceneId: top.id };
  }

  _after() {
    this._sweep();
    this.publish();
  }

  /** Publish the view-model of the top-most layer per topic; null when a topic has no layer. */
  publish() {
    const want = new Map();
    // Overlay screens do not stack: while one sits above another (Settings opened from the journal), only the top
    // one is drawn, so a translucent panel never shows the screen under it.
    let topOverlay = -1;
    this.layers.forEach((l, i) => { if (OVERLAYS.has(l.kind)) topOverlay = i; });
    for (const [i, layer] of this.layers.entries()) {
      const topic = VM_TOPIC[layer.kind];
      if (!topic) continue;
      if (OVERLAYS.has(layer.kind) && i < topOverlay) continue;
      want.set(topic, layer.viewModel ? layer.viewModel() : null);
      // A scene may feed a second topic (the setup screen carries the calibration steps and diagram).
      const extra = layer.extraViewModels ? layer.extraViewModels() : {};
      for (const [t, vm] of Object.entries(extra)) if (!want.has(t)) want.set(t, vm);
    }
    for (const topic of new Set([...this._vms.keys(), ...want.keys()])) {
      const vm = want.has(topic) ? want.get(topic) : null;
      const s = JSON.stringify(vm);
      if (this._vms.get(topic) === s) continue;
      this._vms.set(topic, s);
      this.ctx.bus.emit(topic, vm);
    }
  }
}
