// Layout help (vm:layout-help), drawn only from the view-model that input.layoutHelpModel builds from the manifest.
import { Component } from './component.js';
import { html, cmdAttr } from './html.js';
import { icon } from './icons.js';
import { keycap, sequence } from './keycap.js';
import { CLOSE, LAYOUT_HELP_COPY, KEYBOARD_LABELS, CONFIDENCE_ICON } from './strings.js';

const VERIFY_WORDS = { observed: 'Observed output', player_confirmed: 'You confirmed this gesture', external_only: "Can't be observed here" };

function keyView(k) {
  const cls = ['kh-lk'];
  if (k.silent) cls.push('silent');
  else if (k.held) cls.push('layerkey');
  else if (k.differs) cls.push('map');
  else cls.push('same');
  if (k.selected) cls.push('focus');
  const big = k.silent ? 'XX' : k.id;
  const sub = k.silent ? k.id : (k.held ? 'hold' : (k.legend && k.legend.toLowerCase() !== String(k.id).toLowerCase() ? k.legend : ''));
  const name = k.silent ? `${k.id}, silent on practice` : `${k.id}${k.legend && k.legend !== k.id ? `, ${k.legend}` : ''}`;
  return html`<button type="button" class="${cls.join(' ')}" style="--w:${k.width_u}" data-fid="key-${k.id}" data-key="${k.id}"
    aria-pressed="${k.selected ? 'true' : 'false'}" aria-label="${name}" ${cmdAttr({ type: 'selectKey', id: k.id })}>
    <span class="l">${big}</span>${sub ? html`<span class="s">${sub}</span>` : ''}</button>`;
}

/** Group keys by row and place each by its x_u: gaps between keys become spacers. */
export function diagramView(keys) {
  const rows = new Map();
  for (const k of keys) {
    if (!rows.has(k.row)) rows.set(k.row, []);
    rows.get(k.row).push(k);
  }
  const out = [...rows.keys()].sort((a, b) => a - b).map((r) => {
    const list = rows.get(r).slice().sort((a, b) => a.x_u - b.x_u);
    let cursor = 0;
    const cells = list.map((k) => {
      const gap = Math.max(0, k.x_u - cursor);
      cursor = k.x_u + k.width_u;
      const spacer = gap > 0.001 ? html`<span class="lh-gap" style="--gap:${gap}"></span>` : '';
      return html`${spacer}${keyView(k)}`;
    });
    return html`<div class="lh-row" data-row="${r}">${cells}</div>`;
  });
  return html`<div class="lh-rows" role="group" aria-label="Keyboard diagram">${out}</div>`;
}

/** Only the key kinds that appear on the shown tab. */
export function legendKinds(keys) {
  const kinds = [];
  if (keys.some((k) => k.differs && !k.silent && !k.held)) kinds.push(['map', 'Changes: the new action is printed under the key']);
  if (keys.some((k) => k.held)) kinds.push(['layerkey', 'Layer key, held']);
  if (keys.some((k) => k.silent)) kinds.push(['silent', 'Silent (XX)']);
  if (keys.some((k) => !k.differs && !k.silent && !k.held)) kinds.push(['same', 'Unchanged']);
  return kinds;
}

function cardView(card) {
  if (!card) return html`<div class="lh-detail empty"><p>Focus a key to see what it does.</p></div>`;
  const fy = card.verification || 'observed';
  return html`<div class="lh-detail" aria-live="polite">
    <div class="big">${keycap({ key: card.label, label: card.label })}</div>
    <dl>${card.lines.map((l) => html`<dd>${l}</dd>`)}</dl>
    <span class="kh-chip ${fy === 'player_confirmed' ? 'confirmed' : fy === 'external_only' ? 'unconfirmed' : 'obs'}">${icon(CONFIDENCE_ICON[fy] || 'eye', 20)} ${VERIFY_WORDS[fy] || fy}</span>
  </div>`;
}

export function layoutHelpView(vm) {
  const tabs = vm.tabs.map((t) => html`<button type="button" class="tab" role="tab" data-fid="tab-${t.id}" aria-selected="${t.selected ? 'true' : 'false'}"
      ${t.selected ? html`data-autofocus` : ''} ${cmdAttr({ type: 'selectTab', id: t.id })}>${t.label}</button>`);
  const variants = vm.variants.map((v) => html`<button type="button" data-fid="variant-${v}" aria-pressed="${v === vm.variant ? 'true' : 'false'}"
      ${cmdAttr({ type: 'selectVariant', id: v })}>${v === vm.variant ? icon('check', 16) : ''}${KEYBOARD_LABELS[v] || v}</button>`);
  const legend = legendKinds(vm.keys).map(([cls, text]) => html`<span><span class="kh-lk ${cls}"><span class="l">${cls === 'silent' ? 'XX' : 'A'}</span></span> ${text}</span>`);
  const remap = vm.remap && vm.remap.length
    ? html`<div class="lh-remap">${vm.remap.map((r) => html`<span><span class="kh-key sm">${r.from}</span> ${icon('arrow-right', 16)} ${r.to}</span>`)}</div>`
    : '';
  const ee = vm.emergencyExit;
  return html`<div class="scrim"></div>
<section class="kh-panel overlay lh-overlay" role="dialog" aria-modal="true" aria-label="${LAYOUT_HELP_COPY.title}" data-screen="layout-help">
  <div class="top"><h2>${LAYOUT_HELP_COPY.title}</h2>
    <div class="tabs" role="tablist" aria-label="Layers">${tabs}</div><span class="grow"></span>
    <span class="lh-device">${LAYOUT_HELP_COPY.keyboard} <div class="seg" role="group" aria-label="Keyboard type">${variants}</div></span>
    <button type="button" class="close kh-btn" data-fid="close" ${cmdAttr({ type: 'back' })}>Close ${keycap(CLOSE.key, { sm: true })} <span class="g">${CLOSE.gesture}</span></button></div>
  <p class="lh-how">${LAYOUT_HELP_COPY.how}</p>
  <div class="kh-lh">${diagramView(vm.keys)}${remap}
    ${cardView(vm.card)}
    <div class="lh-legend">${legend}</div>
    <div class="lh-cards">
      <div class="lh-card" data-card="toggle-out"><span class="kh-label">${LAYOUT_HELP_COPY.toggleOut}</span>
        <div class="seq">${sequence(vm.toggleOut.keys)}</div><p>${vm.toggleOut.text}</p></div>
      <div class="lh-card locked" data-card="emergency-exit"><span class="kh-label">${icon('lock', 20)} ${LAYOUT_HELP_COPY.emergency}</span>
        <p>${ee.text}</p>${ee.unverified !== false ? html`<p><b>Unverified.</b> ${LAYOUT_HELP_COPY.emergencyNote}</p>` : ''}</div>
    </div>
  </div>
</section>`;
}

export class LayoutHelp extends Component {
  static topic = 'vm:layout-help';
  static modal = true;
  view(vm) { return layoutHelpView(vm); }
}
