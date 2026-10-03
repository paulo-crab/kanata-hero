// mountUi: builds one host per component, wires the bus, delegates clicks to ui:command,
// applies display settings to the stage, announces objectives and restores focus.
import { Component, nextFocusIndex } from './component.js';
import { SPRITE } from './icons.js';
import { Hud, Prompt, Markers } from './play.js';
import { Dialogue, HintCard } from './dialogue.js';
import { Inset, FirstUse } from './inset.js';
import { SceneBar, Feedback } from './scene.js';
import { Journal, Controls, Settings } from './journal.js';
import { LayoutHelp } from './layout-help.js';
import { Setup, Calibration, createScreenState, screenOpen } from './setup.js';
import { Toast, LiveRegion, ErrorScreen } from './misc.js';
import { RealClock } from '../shared/clock.js';
import { DEFAULT_VIEW, sameView, INSET_AVOID_RECT } from './world-space.js';

const MOTION_QUERY = '(prefers-reduced-motion: reduce)';

/** Which classes `.rm`, `.large-text`, `.hc` the stage carries for a settings view-model. */
export function stageClasses(settings, systemReduced) {
  const rm = settings.reducedMotion === 'on' || (settings.reducedMotion !== 'off' && !!systemReduced);
  return { rm, 'large-text': !!settings.largerText, hc: !!settings.highContrast };
}

export function mountUi(root, params = {}) {
  const { bus, assetBase = '/' } = params;
  const doc = root.ownerDocument;
  const clock = params.clock || new RealClock();
  const stage = params.stage || (root.closest && root.closest('#stage')) || root.parentElement || root;
  const mq = params.matchMedia
    ? params.matchMedia(MOTION_QUERY)
    : (typeof globalThis.matchMedia === 'function' ? globalThis.matchMedia(MOTION_QUERY) : null);
  const offs = [];

  if (stage.getAttribute && !stage.getAttribute('tabindex') && stage.setAttribute) stage.setAttribute('tabindex', '0');

  const sprite = doc.createElement('div');
  sprite.innerHTML = SPRITE;
  sprite.setAttribute('aria-hidden', 'true');
  root.appendChild(sprite);

  const makeHost = (name) => {
    const host = doc.createElement('div');
    host.className = 'ui-host';
    host.setAttribute('data-component', name);
    host.hidden = true;
    root.appendChild(host);
    return host;
  };

  // Live region: adopt the page's #live element when it exists.
  let liveHost = doc.getElementById ? doc.getElementById('live') : null;
  if (!liveHost) { liveHost = doc.createElement('div'); liveHost.className = 'visually-hidden'; root.appendChild(liveHost); }
  const live = new LiveRegion(liveHost, bus);
  const announce = (text) => live.say(text, { repeat: true });

  const state = createScreenState();
  const classes = { markers: Markers, hud: Hud, prompt: Prompt, inset: Inset, dialogue: Dialogue, 'scene-bar': SceneBar, 'hint-card': HintCard,
    journal: Journal, 'layout-help': LayoutHelp, controls: Controls, settings: Settings, error: ErrorScreen };
  const components = {};
  const modalTopics = [Journal, LayoutHelp, Controls, Settings, HintCard, ErrorScreen, Setup, Calibration].map((c) => c.topic);

  // Remember where focus was before the first modal opens (registered before the components so it runs first).
  let focusReturn = null;
  const anyModalShown = () => Object.values(components).some((c) => c.constructor.modal && c.shown);
  for (const topic of modalTopics) {
    offs.push(bus.on(topic, (vm) => { if (vm && !anyModalShown()) focusReturn = doc.activeElement || null; }));
  }

  // Camera and zoom for marker and prompt placement: `ui:view` events, or the getView() parameter polled on each paint.
  let view = DEFAULT_VIEW;
  const getView = () => (params.getView ? params.getView() : view);
  // The keyboard inset rectangle while a vm:inset is on screen (markers keep the current target clear of it).
  let insetOpen = false;
  const getInset = () => (insetOpen ? INSET_AVOID_RECT : null);
  const opts = { assetBase, clock, announce, state, getView, getInset };
  for (const [name, Cls] of Object.entries(classes)) components[name] = new Cls(makeHost(name), bus, opts);
  components['first-use'] = new FirstUse(makeHost('first-use'), bus, opts);
  components.setup = new Setup(makeHost('setup'), bus, opts);
  components.calibration = new Calibration(makeHost('calibration'), bus, opts);
  components.setup.peer = components.calibration;
  components.calibration.peer = components.setup;
  components.feedback = new Feedback(makeHost('feedback'), bus, { ...opts, inline: () => screenOpen(state) });
  components.toast = new Toast(makeHost('toast'), bus, opts);
  components['live-region'] = live;

  offs.push(bus.on('vm:feedback', (vm) => {
    state.feedback = vm ?? null;
    components.setup.paint();
    components.calibration.paint();
    components.feedback.render(components.feedback.vm);
  }));
  // Feedback draws in the side column, or inside setup/calibration while one of those is open.
  for (const t of ['vm:setup', 'vm:calibration']) {
    offs.push(bus.on(t, () => components.feedback.render(components.feedback.vm)));
  }

  // The camera moved: repaint the world-anchored components only when the view actually changed.
  offs.push(bus.on('ui:view', (v) => {
    if (!v || !v.camera) return;
    const avatar = v.avatar ? { x: v.avatar.x, y: v.avatar.y } : null;
    const cameraMoved = !sameView(v, view);
    const avatarMoved = !!avatar && (!view.avatar || avatar.x !== view.avatar.x || avatar.y !== view.avatar.y);
    if (!cameraMoved && !avatarMoved) return;
    view = { camera: { x: v.camera.x, y: v.camera.y }, zoom: v.zoom, avatar };
    components.markers.render(components.markers.vm);
    if (cameraMoved) components.prompt.render(components.prompt.vm);
  }));
  offs.push(bus.on('vm:inset', (vm) => {
    const open = !!vm;
    if (open === insetOpen) return;
    insetOpen = open;
    components.markers.render(components.markers.vm);
  }));

  // The camera could not clear the avatar of these panels: drop them to 35 % opacity (CSS reads data-faded on the stage).
  offs.push(bus.on('ui:faded', (e) => {
    const ids = (e && e.ids) || [];
    if (stage.setAttribute) stage.setAttribute('data-faded', ids.join(' '));
  }));

  // Objectives and announcements go to the live region.
  offs.push(bus.on('vm:announce', (vm) => { if (vm && vm.text) live.say(vm.text); }));
  offs.push(bus.on('intent', (i) => { if (i && i.type === 'objective' && i.text) live.say(`Objective: ${i.text}`); }));

  // Display settings.
  let lastSettings = null;
  const applySettings = () => {
    const s = lastSettings || { reducedMotion: 'system', largerText: false, highContrast: false };
    const c = stageClasses(s, mq && mq.matches);
    for (const [name, on] of Object.entries(c)) {
      if (stage.classList) stage.classList.toggle(name, on);
    }
    bus.emit('ui:settings-applied', { reducedMotion: c.rm, largerText: c['large-text'], highContrast: c.hc });
  };
  // vm:settings-flags is the always-on copy of the display flags (the Settings screen's vm is null while it is closed).
  for (const t of ['vm:settings', 'vm:settings-flags']) {
    offs.push(bus.on(t, (vm) => { if (vm) { lastSettings = { ...lastSettings, ...vm }; applySettings(); } }));
  }
  if (mq && mq.addEventListener) {
    mq.addEventListener('change', applySettings);
    offs.push(() => mq.removeEventListener('change', applySettings));
  }
  applySettings();

  // Focus return when a layer closes.
  offs.push(bus.on('ui:restore-focus', () => {
    if (anyModalShown()) return;
    const target = focusReturn && focusReturn.isConnected !== false && focusReturn.focus ? focusReturn : stage;
    if (target && target.focus) target.focus({ preventScroll: true });
    focusReturn = null;
  }));

  // Mouse alternatives: every clickable carries its ui:command.
  const onClick = (ev) => {
    const t = ev.target;
    const ui = t && t.closest && t.closest('[data-ui]');
    if (ui) {
      const kind = ui.getAttribute('data-ui');
      if (kind === 'reload') { const w = doc.defaultView; if (w && w.location) w.location.reload(); return; }
      if (kind === 'diagram') { state.diagramView = ui.getAttribute('data-view'); components.setup.paint(); components.calibration.paint(); return; }
    }
    const el = t && t.closest && t.closest('[data-cmd]');
    if (!el) return;
    let cmd;
    try { cmd = JSON.parse(el.getAttribute('data-cmd')); } catch { return; }
    bus.emit('ui:command', cmd);
  };
  // Focusing a Layout help key moves the detail card to it (once: a re-render keeps focus without looping).
  const onFocusIn = (ev) => {
    const t = ev.target;
    if (!t || !t.getAttribute || t.getAttribute('data-key') === null) return;
    if (t.getAttribute('aria-pressed') === 'true') return;
    bus.emit('ui:command', { type: 'selectKey', id: t.getAttribute('data-key') });
  };
  // Tab wraps inside a shown modal layer. Esc always leaves, so this is never a trap.
  const onKeyDown = (ev) => {
    if (ev.key !== 'Tab') return;
    const modal = Object.values(components).reverse().find((c) => c.constructor.modal && c.shown);
    if (!modal || !modal.host.querySelectorAll) return;
    const list = [...modal.host.querySelectorAll('button:not([disabled]),[tabindex]:not([tabindex="-1"])')];
    const at = list.indexOf(doc.activeElement);
    // Focus on an element the list does not know (a scroll region the browser made focusable): let the browser move on.
    if (at < 0 && modal.host.contains && modal.host.contains(doc.activeElement) && doc.activeElement !== modal.host) return;
    const next = nextFocusIndex(list.length, at, ev.shiftKey);
    const wraps = at < 0 || (ev.shiftKey ? at === 0 : at === list.length - 1);
    if (wraps && next >= 0) { ev.preventDefault(); list[next].focus(); }
  };
  root.addEventListener('click', onClick);
  root.addEventListener('focusin', onFocusIn);
  root.addEventListener('keydown', onKeyDown);

  return {
    components,
    stage,
    announce,
    destroy() {
      root.removeEventListener('click', onClick);
      root.removeEventListener('focusin', onFocusIn);
      root.removeEventListener('keydown', onKeyDown);
      for (const off of offs) off();
      for (const c of Object.values(components)) if (c !== live) c.destroy();
    },
  };
}

export { Component };
