// Setup and calibration screens (vm:setup, vm:calibration). One panel when both are present, as in the kit.
import { Component } from './component.js';
import { html, cmdAttr } from './html.js';
import { icon } from './icons.js';
import { keycap, sequence } from './keycap.js';
import { feedbackView } from './scene.js';
import { CLOSE, CONTINUE, SETUP_COPY, STATUS_LABELS, KEYBOARD_LABELS } from './strings.js';

const CHIP = { not_started: ['todo', 'circle'], observed: ['obs', 'eye'], skipped: ['skip', 'skip'] };

/** State shared by the two components and the feedback card (they draw one panel). */
export function createScreenState() {
  return { setup: null, calibration: null, feedback: null, diagramView: null };
}

function keyboardCards(vm) {
  return html`<div class="su-choice" role="radiogroup" aria-label="${SETUP_COPY.keyboardHeading}">${vm.keyboards.map((k) => html`
    <button type="button" class="su-opt${k.selected ? ' sel' : ''}" role="radio" aria-checked="${k.selected ? 'true' : 'false'}" data-fid="kb-${k.id}"
      ${k.selected ? html`data-autofocus` : ''} ${cmdAttr({ type: 'selectKeyboard', id: k.id })}>
      <h3>${k.label || KEYBOARD_LABELS[k.id] || k.id}</h3>
      <span class="pick">${k.selected ? html`${icon('check', 18)} Selected` : 'Not selected'}</span>
    </button>`)}</div>`;
}

function stepRow(s, i) {
  const [cls, ic] = CHIP[s.status] || CHIP.not_started;
  const confirm = s.confirmable
    ? html`<button type="button" class="kh-btn" data-fid="confirm-${s.id}" ${cmdAttr({ type: 'playerConfirm', sceneId: 'calibration', choice: 'did' })}>I did this</button>`
    : '';
  return html`<button type="button" class="su-step${s.current ? ' cur' : ''}" data-step="${s.id}" data-fid="step-${s.id}" aria-current="${s.current ? 'step' : 'false'}"
    ${s.current && !s.confirmable ? html`data-autofocus` : ''} ${cmdAttr({ type: 'chooseRow', id: s.id })}>
    <span class="n">${i + 1}</span>
    <span class="t">${s.gesture} <span class="mono">${s.expected}</span></span>
    <span class="kh-chip ${cls}">${icon(ic, 20)} ${STATUS_LABELS[s.status] || s.statusLabel}</span>
    <span class="d">${s.hintLine}</span></button>${confirm}`;
}

function diagramBlock(vm, state) {
  const d = vm.diagram;
  if (!d) return '';
  const view = state.diagramView || vm.diagramView || 'positions';
  const part = d[view] || d.positions || d.characters;
  if (!part) return '';
  const rows = part.rows.map((r) => html`<div class="sk-row">${r.map((k) => html`<span class="kh-sk ${k.state && k.state !== 'plain' ? k.state : ''}" style="--w:${k.width_u || 1}">${k.label}</span>`)}</div>`);
  const seg = ['positions', 'characters'].filter((v) => d[v]).map((v) => html`<button type="button" data-fid="diagram-${v}" aria-pressed="${v === view ? 'true' : 'false'}" data-ui="diagram" data-view="${v}">${v === view ? icon('check', 16) : ''}${v === 'positions' ? 'Physical positions' : 'Resulting characters'}</button>`);
  return html`<div class="su-diagram"><div class="head"><span class="kh-label">Diagram</span><div class="seg" role="group" aria-label="Diagram view">${seg}</div></div>
    <div class="sk-rows" role="img" aria-label="${part.caption || 'Keyboard diagram'}">${rows}</div><p class="cap">${part.caption || ''}</p></div>`;
}

export function calibrationBody(vm, state = createScreenState()) {
  const t = vm.toggleOut;
  const chip = t.practice === 'player-confirmed'
    ? html`<span class="kh-chip confirmed">${icon('person-check', 20)} Practice layer: player-confirmed</span>`
    : html`<span class="kh-chip unconfirmed">${icon('circle', 20)} Practice layer: unconfirmed</span>`;
  return html`<div class="su-body"><div class="su-steps"><div class="head"><span class="kh-label">Calibration</span><span class="sub">Five optional steps</span></div>
    ${vm.steps.map(stepRow)}<p class="su-foot">${SETUP_COPY.footnote}</p></div>
  <div class="su-side">${state.feedback ? feedbackView(state.feedback) : ''}${diagramBlock(vm, state)}
    <div class="su-toggle"><span class="kh-label">Toggle out of practice</span><div class="seq">${sequence(t.keys)}</div><p>${t.text}</p><div>${chip}</div></div></div></div>`;
}

export function setupScreenView(state) {
  const { setup, calibration } = state;
  const title = setup ? SETUP_COPY.title : 'Calibration';
  return html`<div class="scrim"></div>
<section class="kh-panel overlay su" role="dialog" aria-modal="true" aria-label="${title}" data-screen="${setup ? 'setup' : 'calibration'}">
  <div class="top"><h2>${title}</h2><span class="sub">${SETUP_COPY.sub}</span><span class="grow"></span>
    <button type="button" class="kh-btn" data-fid="skip" ${cmdAttr({ type: 'skip' })}>${SETUP_COPY.skip} ${keycap(CLOSE.key, { sm: true })}</button>
    <button type="button" class="kh-btn primary" data-fid="continue" ${cmdAttr({ type: 'continue' })}>Continue ${keycap(CONTINUE.key, { sm: true })}</button></div>
  ${setup ? keyboardCards(setup) : ''}
  ${calibration ? calibrationBody(calibration, state) : ''}
</section>`;
}

/** Draws the whole panel when a setup vm is present (with calibration inside when both are). */
export class Setup extends Component {
  static topic = 'vm:setup';
  static modal = true;
  constructor(host, bus, opts = {}) { super(host, bus, opts); this.state = opts.state || createScreenState(); }
  render(vm) { this.state.setup = vm ?? null; this.paint(); if (this.peer) this.peer.paint(); }
  paint() { super.render(this.state.setup ? this.state : null); }
  isVisible(s) { return !!(s && s.setup); }
  view(s) { return setupScreenView(s); }
}

/** Draws its own panel only when no setup vm is present. */
export class Calibration extends Component {
  static topic = 'vm:calibration';
  static modal = true;
  constructor(host, bus, opts = {}) { super(host, bus, opts); this.state = opts.state || createScreenState(); }
  render(vm) { this.state.calibration = vm ?? null; this.paint(); if (this.peer) this.peer.paint(); }
  paint() { super.render(this.state.calibration && !this.state.setup ? this.state : null); }
  isVisible(s) { return !!(s && s.calibration && !s.setup); }
  view(s) { return setupScreenView(s); }
}

/** True while a setup or calibration panel is on screen (the feedback card then draws inside it). */
export function screenOpen(state) { return !!(state.setup || state.calibration); }
