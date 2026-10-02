// Dialogue panel with portraits (vm:dialogue) and the recall hint-forfeit card (vm:hint-card).
import { Component } from './component.js';
import { html, cmdAttr } from './html.js';
import { icon } from './icons.js';
import { keycap, keycapForName } from './keycap.js';

export const PORTRAIT_ATLAS = 'art-direction/portraits/portraits-atlas.png';

/** Root-relative URL of a static asset under an asset base ('/' by default). */
export function assetUrl(assetBase, path) {
  const base = assetBase.endsWith('/') ? assetBase : `${assetBase}/`;
  return `${base}${path.replace(/^\//, '')}`;
}

/** 48x48 atlas cell drawn at world zoom (--world-zoom), pixelated. The slot is --portrait-size square. */
export function portraitView(portrait, speakerName, assetBase = '/') {
  if (!portrait) return '';
  const { rect } = portrait;
  const style = `width:${rect.w}px;height:${rect.h}px;background-image:url(${assetUrl(assetBase, PORTRAIT_ATLAS)});background-position:-${rect.x}px -${rect.y}px`;
  return html`<div class="kh-portrait" role="img" aria-label="Portrait of ${speakerName}" data-portrait="${portrait.key}">
    <div class="px" style="${style}"></div>
  </div>`;
}

const FOOTER_COMMAND = { Continue: { type: 'continue' }, Skip: { type: 'skip' } };

export function dialogueView(vm, assetBase = '/') {
  const conversation = vm.mode === 'conversation';
  const hint = vm.hint
    ? html`<p class="hint">${keycap(keycapForName(vm.hint.key), { sm: true })} Hint: <b>${vm.hint.gesture}</b></p>`
    : '';
  const footer = (vm.footer || []).map((f) => html`<button type="button" class="ctl-btn" data-fid="footer-${f.action.toLowerCase()}" ${cmdAttr(FOOTER_COMMAND[f.action] || { type: 'continue' })}>
      <b>${f.action}</b> ${keycap(f.key, { sm: true })} <span class="g">${f.gesture}</span></button>`);
  const label = conversation ? `Conversation with ${vm.speakerName}` : `Instruction from ${vm.speakerName}`;
  const roleAttrs = conversation
    ? html`role="dialog" aria-modal="true" tabindex="-1" data-autofocus`
    : html`role="status"`;
  return html`<section class="kh-panel kh-dialogue ${conversation ? 'conversation' : 'instruction'}${vm.objectSpeaker ? ' object' : ''}"
  ${roleAttrs} aria-label="${label}" data-dialogue="${vm.id}">
  ${portraitView(vm.portrait, vm.speakerName, assetBase)}
  <div class="body">
    <div class="who">${vm.speakerName}${vm.role ? html` <span class="role">${vm.role}</span>` : ''}</div>
    <p class="say">${vm.text}</p>
    ${hint}
    <div class="ctl">${footer}</div>
  </div>
</section>`;
}

export class Dialogue extends Component {
  static topic = 'vm:dialogue';
  view(vm) { return dialogueView(vm, this.opts.assetBase || '/'); }
}

export function hintCardView(vm) {
  return html`<div class="scrim card-scrim"></div>
<section class="kh-panel kh-hintcard" role="alertdialog" aria-modal="true" aria-label="Use the hint?" tabindex="-1" data-autofocus>
  <h3>${icon('warn', 24)} Use the hint?</h3>
  <p>${vm.text}</p>
  <div class="btns">
    <button type="button" class="kh-btn primary" data-fid="hint-confirm" ${cmdAttr({ type: 'continue' })}>Show hint ${keycap(vm.confirm, { sm: true })}</button>
    <button type="button" class="kh-btn" data-fid="hint-cancel" ${cmdAttr({ type: 'back' })}>Keep it ${keycap(vm.cancel, { sm: true })}</button>
  </div>
</section>`;
}

export class HintCard extends Component {
  static topic = 'vm:hint-card';
  static modal = true;
  view(vm) { return hintCardView(vm); }
}
