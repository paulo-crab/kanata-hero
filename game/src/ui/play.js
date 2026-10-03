// In-world components: HUD, interaction prompt and markers (vm:hud, vm:prompt, vm:markers).
import { Component } from './component.js';
import { html, cmdAttr } from './html.js';
import { icon, markerSvg } from './icons.js';
import { keycap } from './keycap.js';
import {
  DEFAULT_VIEW, markerCentre, promptPosition, targetIndicator, avatarStageRect, compassWord, ARROW_SIZE,
} from './world-space.js';

/** Chips that open a layer by mouse. The Hint chip is a reminder only: it never opens the inset. */
const CHIP_COMMANDS = { journal: { type: 'openLayer', id: 'journal' }, 'layout-help': { type: 'openLayer', id: 'layout-help' } };

export function hudView(vm) {
  const { title, progress, seals, chips = [], compact = false } = vm;
  const strip = compact ? '' : html`<div class="kh-hud obj" role="group" aria-label="Objective">
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

/** Edge arrow for the current target when the inset covers it (or it is off the stage). Angle 0 points right. */
export function edgeArrowView(ind, tone, label) {
  const style = `left:${Math.round(ind.x - ARROW_SIZE / 2)}px;top:${Math.round(ind.y - ARROW_SIZE / 2)}px;width:${ARROW_SIZE}px;height:${ARROW_SIZE}px`;
  return html`<span class="kh-edge-arrow ${tone}" style="${style}" data-edge-arrow data-angle="${ind.angle}" role="img" aria-label="${label}">
  <svg viewBox="0 0 56 56" aria-hidden="true" style="transform:rotate(${ind.angle}deg)"><path class="halo" d="M8 28 H40 M28 14 L42 28 L28 42"/><path class="line" d="M8 28 H40 M28 14 L42 28 L28 42"/></svg></span>`;
}

/**
 * `at` is the cell top-left in MAP pixels (as the runtime sends it); positions are converted with the camera view.
 * `opts.inset` is the stage rectangle of the open keyboard inset (null when closed): the marker flagged `current`
 * is then shown as an edge arrow when the inset covers it. `view.avatar` is the avatar's feet in map pixels.
 */
export function markersView(vm, view = DEFAULT_VIEW, opts = {}) {
  const inset = opts.inset || null;
  const avatar = inset && view.avatar ? avatarStageRect(view.avatar, view) : null;
  const arrows = [];
  const indicate = (item, centre, size, tone, word) => {
    if (!inset || !item.current) return;
    const ind = targetIndicator({ centre, size, inset, avatar });
    if (ind) arrows.push(edgeArrowView(ind, tone, `Next ${word}: ${compassWord(ind.angle)}, under the keyboard inset`));
  };
  const placed = (c, size) => `left:${Math.round(c.x - size / 2)}px;top:${Math.round(c.y - size / 2)}px`;
  const marks = (vm.markers || []).map((m) => {
    const reached = m.state === 'reached';
    const c = markerCentre(m.at, m.shape, view);
    indicate(m, c, 64, 'gold', 'desk');
    const svg = markerSvg(MARKER_SHAPE[m.shape] || 'talk', placed(c, 64), reached ? 'reached' : '');
    const badge = reached
      ? html`<span class="kh-marker-badge" style="${placed({ x: c.x + 22, y: c.y - 22 }, 28)}" aria-hidden="true">${icon('check', 18)}</span>`
      : '';
    return html`<span class="kh-marker-wrap" data-marker="${m.id}" data-state="${m.state}" role="img" aria-label="${MARKER_WORD[m.shape] || m.shape}${reached ? ', reached' : ''}">${svg}${badge}</span>`;
  });
  const floor = (vm.floor || []).map((f) => {
    const gold = f.state === 'gold';
    const c = markerCentre(f.at, 'route', view, true);
    indicate(f, c, 48, gold ? 'gold' : 'teal', 'route marker');
    const svg = markerSvg(gold ? 'route' : 'route-teal', placed(c, 48), 'floor');
    const badge = gold
      ? html`<span class="kh-marker-badge" style="${placed(c, 28)}" aria-hidden="true">${icon('check', 18)}</span>`
      : '';
    return html`<span class="kh-marker-wrap floor" data-floor="${f.id}" data-state="${f.state}" role="img" aria-label="Route marker, ${gold ? 'reached' : 'still to walk'}">${svg}${badge}</span>`;
  });
  return html`${floor}${marks}${arrows}`;
}

export class Markers extends Component {
  static topic = 'vm:markers';
  /** The camera or the avatar moves every step: only touch the DOM when the markup really changed. */
  render(vm) {
    if (vm && this.shown) {
      const next = String(this.view(vm));
      if (next === this._markup && this.host.innerHTML === next) { this.vm = vm; return; }
    }
    super.render(vm);
    this._markup = vm ? this.host.innerHTML : null;
  }
  view(vm) {
    const inset = this.opts.getInset ? this.opts.getInset() : null;
    return markersView(vm, this.opts.getView ? this.opts.getView() : DEFAULT_VIEW, { inset });
  }
}
