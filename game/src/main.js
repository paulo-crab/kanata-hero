// Boot. Contract section 8: `createGame` wires every module and works headless; `bootBrowser` adds the
// canvas, the DOM UI, the window listeners and the render loop on top of it.
import { EventBus, RealClock, DataLoadError } from './shared/index.js';
import * as engine from './engine/index.js';
import * as input from './input/index.js';
import * as runtime from './runtime/index.js';
import * as ui from './ui/index.js';

export const modules = { engine, input, runtime, ui };

/** The stage is laid out at x4 (1280x720 logical px); a larger world zoom scales the whole stage with CSS. */
export const STAGE_ZOOM = 4;

function systemReducedMotion(opts) {
  if (typeof opts.systemReducedMotion === 'function') return !!opts.systemReducedMotion();
  return false;
}

/** Display flag value to the effective reduced-motion switch ('system' follows the OS). */
export function effectiveReducedMotion(flag, system) {
  return flag === 'on' || (flag !== 'off' && !!system);
}

/**
 * Build one game. Headless-safe: with `headless: true` it touches no canvas, DOM or `window`, and still
 * emits every `vm:*` topic on the bus.
 * @param {{fetchFn?:Function, baseUrl?:string, loadImage?:Function, clock?:object, storage?:object, headless?:boolean,
 *   bus?:object, render?:Function, systemReducedMotion?:()=>boolean}} [opts]
 * @returns {Promise<object>} {bus, clock, data, atlases, world, rules, dialogue, evidence, progress, machine,
 *   interpreter, loop, session, destroy()}; on a DataLoadError {bus, clock, error, machine, loop:null, destroy()}
 *   with the `error` scene on top (vm:error published).
 */
export async function createGame(opts = {}) {
  const bus = opts.bus || new EventBus();
  const clock = opts.clock || new RealClock();
  const baseUrl = opts.baseUrl ?? '/';
  const fetchFn = opts.fetchFn;
  let data;
  let atlases;
  try {
    data = await engine.loadGameData({ fetchFn, baseUrl });
    atlases = await engine.loadAtlasSet({ fetchFn, baseUrl, loadImage: opts.loadImage });
  } catch (error) {
    if (!(error instanceof DataLoadError)) throw error;
    return failedGame({ bus, clock, error, opts });
  }

  const world = new engine.World(data, atlases, { bus, reducedMotion: false });
  const manifest = new input.LayoutManifest(data.layoutManifest);
  const session = runtime.createSession({ bus, clock, data, world, atlases, storage: opts.storage, input, manifest });
  const interpreter = new input.KeyInterpreter({ clock, bus, getContext: () => session.machine.inputContext() });

  // Reduced motion reaches the world from the settings flags (and the UI's resolved value in the browser).
  let rmFlag = 'system';
  const applyMotion = () => world.setReducedMotion(effectiveReducedMotion(rmFlag, systemReducedMotion(opts)));
  bus.on('vm:settings-flags', (f) => { if (f) { rmFlag = f.reducedMotion; applyMotion(); } });

  // A throwing step must never freeze the page: report it once per message on the bus and keep the loop running.
  const reported = new Set();
  const guarded = (where, fn) => (...args) => {
    try {
      fn(...args);
    } catch (error) {
      const key = `${where}:${error && error.message}`;
      if (!reported.has(key)) {
        reported.add(key);
        bus.emit('bus:error', { topic: `loop:${where}`, error });
        if (typeof console !== 'undefined') console.error(error);
      }
    }
  };
  const loop = new engine.GameLoop({
    clock,
    update: guarded('update', (ms) => { world.update(ms); session.update(ms); }),
    render: guarded('render', () => { if (opts.render) opts.render(); }),
    raf: opts.raf,
    caf: opts.caf,
  });

  session.start();
  applyMotion();

  return {
    bus, clock, data, atlases, world, session, interpreter, loop, manifest,
    rules: session.rules, dialogue: session.dialogue, evidence: session.evidence, progress: session.progress,
    machine: session.machine,
    destroy() {
      loop.stop();
      interpreter.detach();
    },
  };
}

/** A DataLoadError never throws into the page: the error scene names the file. */
function failedGame({ bus, clock, error, opts }) {
  const ctx = { bus, clock };
  const machine = new runtime.SceneMachine(ctx, { error: () => new runtime.ErrorScene() });
  machine.push('error', { error: { file: error.file, kind: error.kind, message: error.message } });
  const interpreter = new input.KeyInterpreter({ clock, bus, getContext: () => machine.inputContext() });
  return {
    bus, clock, error, machine, interpreter, loop: null, data: null, atlases: null, world: null, session: null,
    destroy() { interpreter.detach(); },
    opts,
  };
}

// ---- browser ---------------------------------------------------------------------------------------------

function safeStorage(win) {
  try {
    const s = win.localStorage;
    s.getItem('kanata-hero:probe');
    return s;
  } catch {
    return undefined;
  }
}

/**
 * Browser boot on top of createGame: canvas renderer, DOM UI, window key listeners, resize and the render loop.
 * @param {{window?:Window, document?:Document, fetchFn?:Function, baseUrl?:string}} [p]
 */
export async function bootBrowser(p = {}) {
  const win = p.window || globalThis.window;
  const doc = p.document || win.document;
  const stage = doc.getElementById('stage');
  const canvas = doc.getElementById('world');
  const root = doc.getElementById('ui');
  const bus = new EventBus();
  const clock = new RealClock();
  const mq = typeof win.matchMedia === 'function' ? win.matchMedia('(prefers-reduced-motion: reduce)') : null;

  // The UI mounts first so an early DataLoadError still reaches the error screen.
  let game = null;
  let renderer = null;
  let zoom = STAGE_ZOOM;
  let lastView = '';
  const uiHandle = ui.mountUi(root, { bus, stage, assetBase: p.baseUrl || '/', clock });

  const fitStage = (w, h) => {
    if (renderer) {
      ({ zoom } = renderer.resize(w, h));
      // The canvas keeps its logical 1280x720 box; its backing store is 320*zoom wide. The stage scales as a whole.
      canvas.style.width = `${STAGE_W}px`;
      canvas.style.height = `${STAGE_H}px`;
    } else {
      zoom = engine.chooseZoom(w, h);
    }
    stage.style.setProperty('--world-zoom', String(STAGE_ZOOM));
    stage.style.transform = zoom === STAGE_ZOOM ? '' : `scale(${zoom / STAGE_ZOOM})`;
    lastView = '';
  };

  const render = () => {
    if (!game || !game.world || !renderer) return;
    const camera = game.world.camera();
    renderer.draw(game.world.snapshot(), camera);
    const feet = game.world.avatar.feetPx;
    const key = `${camera.x},${camera.y},${feet.x},${feet.y}`;
    if (key !== lastView) {
      lastView = key;
      bus.emit('ui:view', { camera: { x: camera.x, y: camera.y }, zoom: STAGE_ZOOM, avatar: { x: feet.x, y: feet.y } });
    }
  };

  game = await createGame({
    bus,
    clock,
    fetchFn: p.fetchFn || ((url, init) => win.fetch(url, init)),
    baseUrl: p.baseUrl ?? '/',
    loadImage: (url) => new Promise((resolve, reject) => {
      const img = new win.Image();
      img.onload = () => resolve(img);
      img.onerror = () => reject(new Error(`image failed to load: ${url}`));
      img.src = url;
    }),
    storage: safeStorage(win),
    render,
    raf: (fn) => win.requestAnimationFrame(fn),
    caf: (h) => win.cancelAnimationFrame(h),
    systemReducedMotion: () => !!(mq && mq.matches),
  });

  if (game.error) {
    // No world to draw: attach keys (the error scene claims none) and stop.
    game.interpreter.attach(win);
    stage.focus({ preventScroll: true });
    return { game, ui: uiHandle, bus };
  }

  renderer = new engine.Renderer({ canvas, atlases: game.atlases, stageEl: stage });
  bus.on('ui:settings-applied', (s) => {
    game.world.setReducedMotion(s.reducedMotion);
    renderer.setReducedMotion(s.reducedMotion);
  });
  bus.on('game:reset', () => win.location.reload());
  win.addEventListener('resize', () => fitStage(win.innerWidth, win.innerHeight));
  fitStage(win.innerWidth, win.innerHeight);

  game.interpreter.attach(win);
  game.loop.start();
  render();
  stage.focus({ preventScroll: true });
  win.__kanataHero = game; // read-only handle for the browser checks
  return { game, ui: uiHandle, bus, renderer };
}

const STAGE_W = 1280;
const STAGE_H = 720;

if (typeof document !== 'undefined' && typeof window !== 'undefined' && document.getElementById('stage') && !globalThis.__KH_NO_BOOT) {
  bootBrowser().catch((e) => {
    const note = document.getElementById('live');
    if (note) note.textContent = `Kanata Hero could not start: ${e.message}`;
    console.error(e);
  });
}
