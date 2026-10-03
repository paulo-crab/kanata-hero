// Setup and calibration screens (vm:setup, vm:calibration).
// Setup is only the keyboard choice and a Next button. Calibration is one step at a time: a large prompt with the
// gesture keycaps, what the page is waiting for, the last output it saw, wrong-key feedback, then a success state.
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

function diagramBlock(vm, state) {
  const d = vm.diagram;
  if (!d) return '';
  const view = state.diagramView || vm.diagramView || 'positions';
  const part = d[view] || d.positions || d.characters;
  if (!part) return '';
  const rows = part.rows.map((r) => html`<div class="sk-row">${r.map((k) => html`<span class="kh-sk ${k.state && k.state !== 'plain' ? k.state : ''}" style="--w:${k.width_u || 1}">${k.label}</span>`)}</div>`);
  const views = ['positions', 'characters'].filter((v) => d[v]);
  const seg = views.length > 1
    ? html`<div class="seg" role="group" aria-label="Diagram view">${views.map((v) => html`<button type="button" data-fid="diagram-${v}" aria-pressed="${v === view ? 'true' : 'false'}" data-ui="diagram" data-view="${v}">${v === view ? icon('check', 16) : ''}${v === 'positions' ? 'Physical positions' : 'Resulting characters'}</button>`)}</div>`
    : '';
  return html`<div class="su-diagram"><div class="head"><span class="kh-label">Diagram</span>${seg}</div>
    <div class="sk-rows" role="img" aria-label="${part.caption || 'Keyboard diagram'}">${rows}</div><p class="cap">${part.caption || ''}</p></div>`;
}

/** The skip confirm card: Return is yes, Esc goes back. Nothing is skipped until the player says yes. */
function confirmCard(what) {
  return html`<div class="scrim card-scrim"></div>
<section class="kh-panel kh-confirm" role="alertdialog" aria-modal="true" aria-label="Skip ${what}?" data-confirm="skip">
  <h3>${icon('warn', 24)} Skip ${what}?</h3>
  <p>${what === 'setup' ? 'Setup and calibration will be left undone. You can run setup again from Settings.' : 'The steps you have not done will be recorded as Skipped. You can run setup again from Settings.'}</p>
  <div class="btns">
    <button type="button" class="kh-btn primary" data-fid="skip-yes" data-autofocus ${cmdAttr({ type: 'continue' })}>Yes, skip ${keycap(CONTINUE.key, { sm: true })}</button>
    <button type="button" class="kh-btn" data-fid="skip-no" ${cmdAttr({ type: 'back' })}>Go back ${keycap(CLOSE.key, { sm: true })}</button>
  </div>
</section>`;
}

function stepProgress(vm) {
  return html`<ol class="su-dots" aria-label="Calibration progress">${vm.steps.map((s) => html`<li class="${s.current ? 'cur' : ''} ${s.status}" aria-label="Step ${s.number}: ${STATUS_LABELS[s.status] || s.statusLabel}${s.current ? ', now' : ''}">${s.number}</li>`)}</ol>`;
}

function waitingPrompt(vm) {
  const c = vm.current;
  const keys = c.keys.length
    ? html`<div class="su-gesture" role="group" aria-label="Gesture: ${c.gesture}"><span class="verb">Hold</span>${keycap(c.keys[0])}<span class="plus" aria-hidden="true">+</span><span class="verb">tap</span>${keycap(c.keys[1])}</div>`
    : '';
  const last = vm.lastSeen
    ? html`<p class="su-last" data-last-seen>Last key seen: <b class="mono">${vm.lastSeen.name}</b></p>`
    : html`<p class="su-last" data-last-seen>Last key seen: <span class="mono">nothing yet</span></p>`;
  const wrong = vm.wrong
    ? html`<div class="su-wrong" role="alert" data-wrong>${icon('warn', 24)}<div><b>${vm.wrong.text}</b>${vm.wrong.hint ? html`<p>${vm.wrong.hint}</p>` : ''}</div></div>`
    : '';
  const done = vm.success
    ? html`<div class="su-ok" role="status" data-success>${icon('check', 24)} ${vm.success.text}</div>`
    : '';
  return html`<div class="su-prompt">
    <div class="head"><span class="kh-label">Step ${c.number} of ${vm.stepCount}</span>${stepProgress(vm)}</div>
    ${done}
    <p class="su-say">${c.action}</p>
    ${keys}
    <p class="su-wait" data-waiting><span class="kh-chip todo">${icon('circle', 20)} ${c.waiting}</span></p>
    ${last}
    ${wrong}
    <div class="btns">
      <button type="button" class="kh-btn" data-fid="skip-step" ${cmdAttr({ type: 'skipStep' })}>Skip this step ${keycap(vm.skipStep.key, { sm: true })}</button>
    </div>
  </div>`;
}

function summary(vm) {
  const rows = vm.steps.map((s) => {
    const [cls, ic] = CHIP[s.status] || CHIP.not_started;
    return html`<li class="su-sum-row" data-step="${s.id}" data-status="${s.status}"><span class="n">${s.number}</span><span class="t">${s.gesture} <span class="mono">${s.expectedName}</span></span><span class="kh-chip ${cls}">${icon(ic, 20)} ${STATUS_LABELS[s.status] || s.statusLabel}</span></li>`;
  });
  return html`<div class="su-prompt summary">
    <div class="head"><span class="kh-label">Calibration finished</span></div>
    ${vm.success ? html`<div class="su-ok" role="status" data-success>${icon('check', 24)} ${vm.success.text}</div>` : ''}
    <ul class="su-sum" aria-label="Calibration summary">${rows}</ul>
    <p class="su-foot">${SETUP_COPY.footnote}</p>
  </div>`;
}

export function calibrationBody(vm, state = createScreenState()) {
  const t = vm.toggleOut;
  const chip = t.practice === 'player-confirmed'
    ? html`<span class="kh-chip confirmed">${icon('person-check', 20)} Practice layer: player-confirmed</span>`
    : html`<span class="kh-chip unconfirmed">${icon('circle', 20)} Practice layer: unconfirmed</span>`;
  const main = vm.phase === 'summary' || !vm.current ? summary(vm) : waitingPrompt(vm);
  return html`<div class="su-body"><div class="su-main">${main}${state.feedback ? feedbackView(state.feedback) : ''}</div>
  <div class="su-side">${diagramBlock(vm, state)}
    <div class="su-toggle"><span class="kh-label">Toggle out of practice</span><div class="seq">${sequence(t.keys)}</div><p>${t.text}</p><div>${chip}</div></div></div></div>`;
}

export function setupScreenView(state) {
  const { setup, calibration } = state;
  const title = setup ? SETUP_COPY.title : 'Calibration';
  let actions;
  if (setup) {
    actions = html`<button type="button" class="kh-btn" data-fid="skip" ${cmdAttr({ type: 'skip' })}>${SETUP_COPY.skip} ${keycap(CLOSE.key, { sm: true })}</button>
    <button type="button" class="kh-btn primary" data-fid="continue" ${cmdAttr({ type: 'continue' })}>Next ${keycap(CONTINUE.key, { sm: true })}</button>`;
  } else if (calibration.phase === 'summary') {
    actions = html`<button type="button" class="kh-btn primary" data-fid="continue" data-autofocus ${cmdAttr({ type: 'continue' })}>Next ${keycap(CONTINUE.key, { sm: true })}</button>`;
  } else {
    actions = html`<button type="button" class="kh-btn" data-fid="skip-calibration" ${cmdAttr({ type: 'skipCalibration' })}>Skip calibration ${keycap(calibration.skipAll.key, { sm: true })}</button>`;
  }
  const confirm = (setup && setup.confirm) ? confirmCard('setup') : (!setup && calibration.confirm ? confirmCard('calibration') : '');
  const sub = setup ? SETUP_COPY.sub : 'Do each gesture once. Nothing here blocks the story.';
  return html`<div class="scrim"></div>
<section class="kh-panel overlay su" role="dialog" aria-modal="true" aria-label="${title}" data-screen="${setup ? 'setup' : 'calibration'}">
  <div class="top"><h2>${title}</h2><span class="sub">${sub}</span><span class="grow"></span>${actions}</div>
  ${setup ? keyboardCards(setup) : ''}
  ${setup ? html`<div class="su-body single"><div class="su-side wide">${diagramBlock(setup, state)}</div></div>` : ''}
  ${calibration && !setup ? calibrationBody(calibration, state) : ''}
  ${confirm}
</section>`;
}

/** Draws the whole panel when a setup vm is present. */
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
