// In-world components: HUD, interaction prompt and markers (vm:hud, vm:prompt, vm:markers).
import { Component } from './component.js';
import { html, cmdAttr } from './html.js';
import { icon, markerSvg } from './icons.js';
import { keycap } from './keycap.js';
import { DEFAULT_VIEW, markerCentre, promptPosition } from './world-space.js';

/** Chips that open a layer by mouse. The Hint chip is a reminder only: it never opens the inset. */
const CHIP_COMMANDS = { journal: { type: 'openLayer', id: 'journal' }, 'layout-help': { type: 'openLayer', id: 'layout-help' } };

export function hudView(vm) {
  const { title, progress, seals, chips = [] } = vm;
  const strip = html`<div class="kh-hud obj" role="group" aria-label="Objective">
  <span class="title">${title}</span>
  <span class="count" aria-label="Progress ${progress.done} of ${progress.total}">${progress.done} / ${progress.total}</span>
  <span class="sep" aria-hidden="true"></span>
  <span class="seals" aria-label="Clearance seals ${seals.count} of ${seals.total}">${icon('seal', 24)} Seals ${seals.count}</span>
</div>`;
  const chipHtml = chips.map((c) => {
    const body = html`${c.label} ${keycap(c.key, { sm: true })}`;
    const command = CHIP_COMMANDS[c.id];
    return command
      ? html`<button type="button" class="chip" data-fid="chip-${c.id}" ${cmdAttr(command)} aria-label="${c.aria}">${body}</button>`
      : html`<span class="chip" role="note" aria-label="${c.aria}">${body}</span>`;
  });
  const shortcuts = chips.length ? html`<div class="kh-hud shortcuts">${chipHtml}</div>` : '';
  return html`${strip}${shortcuts}`;
}

export class Hud extends Component {
  static topic = 'vm:hud';
  view(vm) { return hudView(vm); }
}

/** `vm.at` is the cell's top-left in MAP pixels; `view` is {camera, zoom} (defaults to the origin at x4). */
export function promptView(vm, view = DEFAULT_VIEW) {
  const { x, y } = promptPosition(vm.at, view);
  const device = vm.kind === 'device';
  return html`<div class="kh-prompt ${device ? 'device' : 'person'}" style="left:${x}px;top:${y}px" role="note"
  aria-label="${vm.action}. Key ${vm.key.label}. ${vm.gesture}">
  <div class="action">${icon('play', 20)} ${vm.action}</div>
  <div class="keys">${keycap(vm.key, { sm: true })}<span class="gesture">${vm.gesture}</span></div>
</div>`;
}

export class Prompt extends Component {
  static topic = 'vm:prompt';
  view(vm) { return promptView(vm, this.opts.getView ? this.opts.getView() : DEFAULT_VIEW); }
}

const MARKER_SHAPE = { conversation: 'talk', terminal: 'terminal', route: 'route', glitch: 'glitch' };
const MARKER_WORD = { conversation: 'Conversation', terminal: 'Terminal', route: 'Route', glitch: 'Glitch' };

/** `at` is the cell top-left in MAP pixels (as the runtime sends it); positions are converted with the camera view. */
export function markersView(vm, view = DEFAULT_VIEW) {
  const placed = (c, size) => `left:${Math.round(c.x - size / 2)}px;top:${Math.round(c.y - size / 2)}px`;
  const marks = (vm.markers || []).map((m) => {
    const reached = m.state === 'reached';
    const c = markerCentre(m.at, m.shape, view);
    const svg = markerSvg(MARKER_SHAPE[m.shape] || 'talk', placed(c, 64), reached ? 'reached' : '');
    const badge = reached
      ? html`<span class="kh-marker-badge" style="${placed({ x: c.x + 22, y: c.y - 22 }, 28)}" aria-hidden="true">${icon('check', 18)}</span>`
      : '';
    return html`<span class="kh-marker-wrap" data-marker="${m.id}" data-state="${m.state}" role="img" aria-label="${MARKER_WORD[m.shape] || m.shape}${reached ? ', reached' : ''}">${svg}${badge}</span>`;
  });
  const floor = (vm.floor || []).map((f) => {
    const gold = f.state === 'gold';
    const c = markerCentre(f.at, 'route', view, true);
    const svg = markerSvg(gold ? 'route' : 'route-teal', placed(c, 48), 'floor');
    const badge = gold
      ? html`<span class="kh-marker-badge" style="${placed(c, 28)}" aria-hidden="true">${icon('check', 18)}</span>`
      : '';
    return html`<span class="kh-marker-wrap floor" data-floor="${f.id}" data-state="${f.state}" role="img" aria-label="Route marker, ${gold ? 'reached' : 'still to walk'}">${svg}${badge}</span>`;
  });
  return html`${floor}${marks}`;
}

export class Markers extends Component {
  static topic = 'vm:markers';
  view(vm) { return markersView(vm, this.opts.getView ? this.opts.getView() : DEFAULT_VIEW); }
}
