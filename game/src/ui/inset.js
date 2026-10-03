// Keyboard teaching inset (vm:inset): four numbered cells, guided and variation only. The runtime sends
// null on recall. FirstUse reports the first-use inset to the live region (it draws nothing itself).
import { Component } from './component.js';
import { html, textOf } from './html.js';
import { icon } from './icons.js';
import { keycap, keyunit, keycapName } from './keycap.js';
import { INSET_STAGE_RECT } from '../shared/layout.js';

export { INSET_STAGE_RECT };

function cell(n, label, body) {
  return html`<div class="kh-cell"><div class="kh-label"><span class="kh-order">${n}</span> ${label}</div>${body}</div>`;
}

/** Target key at full strength, held keys held, everything else dim: only the relevant keys are bright. */
function miniRow(keys, target) {
  const caps = keys.map((k) => {
    const lit = k.held || k.lit || k.key === target || k.label === target;
    const k2 = { ...k, dim: !lit };
    return keycap(k2, { sm: true, cls: String(k.label).length > 2 ? 'cap' : '' });
  });
  const names = keys.map((k) => keycapName(k)).join(' ');
  return html`<div class="kh-mini" role="img" aria-label="Key position: ${names}">${caps}</div>`;
}

export function insetView(vm) {
  const { cells } = vm;
  const rows = cells.position.rows && cells.position.rows.length ? cells.position.rows : [cells.position.keys];
  const order = [];
  cells.order.forEach((o, i) => {
    if (i > 0) order.push(html`<span class="plus" aria-hidden="true">+</span>`);
    order.push(keyunit(o.key, o.tag));
  });
  const fx = /^step/i.test(cells.effect.text) ? 'step-east' : 'target';
  const foot = vm.firstUse
    ? html`<div class="foot">First time for this key. It closes when the game sees the output, or on Esc.</div>`
    : '';
  const summary = `${vm.header}. Hold order: ${cells.order.map((o) => `${keycapName(o.key)} ${o.tag}`).join(', ')}. Output: ${cells.output.name}. Effect: ${cells.effect.text}.`;
  return html`<section class="kh-panel kh-inset${vm.firstUse || rows.length > 1 ? ' inset-tall' : ''}" aria-label="Keyboard teaching inset: ${summary}" data-inset>
  <div class="head"><h3>${vm.header}</h3><span class="layer">${vm.layer}</span></div>
  ${cell(1, 'Key position', html`${rows.map((r) => miniRow(r, cells.position.target))}`)}
  <div class="row">
    ${cell(2, 'Hold order', html`<div class="kh-hold">${order}</div>`)}
    ${cell(3, 'Output', html`<div class="kh-out">${keycap(cells.output.key)}<span>${cells.output.name}</span></div>`)}
    ${cell(4, 'Effect', html`<div class="kh-effect">${icon(fx, 28)}<span>${cells.effect.text}</span></div>`)}
  </div>
  ${foot}
</section>`;
}

export class Inset extends Component {
  static topic = 'vm:inset';
  view(vm) { return insetView(vm); }
}

/** Announces a first-use inset once per appearance so a screen-reader player learns it opened. */
export class FirstUse extends Component {
  static topic = 'vm:inset';
  isVisible() { return false; }
  render(vm) {
    super.render(vm);
    const announce = this.opts.announce;
    if (vm && vm.firstUse && announce && vm.header !== this._last) {
      announce(`New key: ${textOf(vm.header)}. The keyboard inset is open at the bottom left.`);
    }
    this._last = vm && vm.firstUse ? vm.header : null;
  }
}
