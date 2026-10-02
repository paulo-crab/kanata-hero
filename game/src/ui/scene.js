// Form, label, editor and walk scenes: the reading column (vm:scene-bar) and the confidence card (vm:feedback).
import { Component } from './component.js';
import { html } from './html.js';
import { icon, markerIcon } from './icons.js';
import { keycap } from './keycap.js';
import { CONFIDENCE_ICON, CONFIDENCE_WHY } from './strings.js';

/** The field line: text before the cursor, a block cursor on the next character (or a blank), then the rest. */
export function fieldView(field) {
  const text = field.text ?? '';
  const at = Math.min(Math.max(field.cursor ?? text.length, 0), text.length);
  const before = text.slice(0, at);
  const under = at < text.length ? text[at] : ' ';
  const after = at < text.length ? text.slice(at + 1) : '';
  const target = field.target
    ? html`<span class="tag" aria-label="Target text: ${field.target}">${icon('target', 16)} target: ${field.target}</span>`
    : '';
  return html`<div class="kh-line tl"><span class="no">${icon('target', 16)} 1</span>
    <span class="code-text" role="img" aria-label="Text so far: ${text || 'empty'}. Cursor after ${at} characters.">${before}<span class="cur">${under}</span>${after}</span>${target}</div>`;
}

export function sceneBarView(vm) {
  const glitch = vm.kind === 'editor';
  const name = glitch ? html`<span class="glt">${markerIcon('glitch', 28)} ${vm.title}</span>` : html`<span class="name">${vm.title}</span>`;
  const next = vm.nextLetter
    ? html`<span class="count" aria-label="Next letter ${vm.nextLetter}">Next ${keycap({ key: vm.nextLetter, label: vm.nextLetter.toUpperCase() }, { sm: true })}</span>`
    : '';
  const well = vm.field
    ? html`<div class="kh-code" data-field>${fieldView(vm.field)}</div>`
    : '';
  const untimed = glitch ? html`<p class="untimed">${icon('check', 16)} Untimed. Nothing is lost on a retry.</p>` : '';
  return html`<section class="kh-panel kh-term ${glitch ? 'glitch' : ''} ${vm.kind}" role="region" aria-label="${vm.title}" data-scene-bar="${vm.kind}">
  <div class="bar">${name}<span class="grow"></span>
    <span class="leave">Leave ${keycap(vm.leave.key, { sm: true })} <span class="g">${vm.leave.gesture}</span></span></div>
  <div class="kh-task"><p>${vm.prompt}</p>${next}</div>
  ${well}
  ${untimed}
</section>`;
}

export class SceneBar extends Component {
  static topic = 'vm:scene-bar';
  view(vm) { return sceneBarView(vm); }
}

/** Observed output, You confirmed, or Can't be observed: told by icon, border style and words, never colour alone. */
export function feedbackView(vm) {
  const kind = vm.confidence === 'player_confirmed' ? 'confirmed' : vm.confidence === 'external_only' ? 'reserved' : 'observed';
  const gesture = vm.gesture
    ? html`<dt>Gesture shown</dt><dd>${vm.gesture}</dd>`
    : '';
  return html`<section class="kh-fb ${kind}" role="status" aria-label="Input feedback" data-confidence="${vm.confidence}">
  <div class="what">${icon(CONFIDENCE_ICON[vm.confidence] || 'eye', 24)} ${vm.confidenceLabel}</div>
  <dl>${gesture}<dt>Output</dt><dd><span class="mono">${vm.observed}</span></dd><dt>Effect</dt><dd class="fx">${vm.effect}</dd></dl>
  <p class="why">${CONFIDENCE_WHY[vm.confidence] || ''}</p>
</section>`;
}

export class Feedback extends Component {
  static topic = 'vm:feedback';
  view(vm) { return html`<div class="kh-side">${feedbackView(vm)}</div>`; }
  /** Calibration and setup draw the card inside their own panel instead. */
  isVisible(vm) { return vm !== null && vm !== undefined && !(this.opts.inline && this.opts.inline()); }
}
