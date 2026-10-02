// Journal (vm:journal), Controls (vm:controls) and Settings (vm:settings).
import { Component } from './component.js';
import { html, cmdAttr } from './html.js';
import { icon } from './icons.js';
import { keycap } from './keycap.js';
import { CLOSE, JOURNAL_COPY, CONTROLS_COPY, SETTINGS_COPY, KEYBOARD_LABELS } from './strings.js';

const GROUP_ICON = { main: 'seal', requests: 'bubble', speed: 'stopwatch' };
const STATE = { active: ['play', 'Active'], locked: ['lock', 'Locked'], done: ['check', 'Done'] };
const STEP_ICON = { done: 'check', current: 'play', todo: null };
const ALSO_COMMAND = {
  'layout-help': { type: 'openLayer', id: 'layout-help' },
  settings: { type: 'openLayer', id: 'settings' },
  controls: { type: 'openLayer', id: 'controls' },
  'ride-hub': { type: 'rideHub' },
};

function closeButton() {
  return html`<button type="button" class="close kh-btn" data-fid="close" ${cmdAttr({ type: 'back' })}>Close ${keycap(CLOSE.key, { sm: true })} <span class="g">${CLOSE.gesture}</span></button>`;
}

export function journalView(vm) {
  const groups = vm.groups.map((g) => html`<div class="group ${g.id}"><h3>${icon(GROUP_ICON[g.id] || 'seal', 24)} ${g.heading}</h3>
    ${g.rows.map((r) => {
      const [ic, word] = STATE[r.state] || STATE.locked;
      return html`<button type="button" class="qrow${r.selected ? ' sel' : ''}" data-fid="row-${r.id}" data-row="${r.id}" aria-current="${r.selected ? 'true' : 'false'}"
        ${r.selected ? html`data-autofocus` : ''} ${cmdAttr({ type: 'chooseRow', id: r.id })}>
        <span class="t">${r.title}</span><span class="state ${r.state}">${icon(ic, 20)} ${word}</span><span class="d">${r.detail}</span></button>`;
    })}</div>`);
  const d = vm.detail;
  const detail = d
    ? html`<div class="detail" aria-live="polite"><h3>${d.title}</h3>
      <ul class="steps">${d.steps.map((s) => html`<li class="${s.state === 'current' ? 'next' : s.state}"><span class="dot">${STEP_ICON[s.state] ? icon(STEP_ICON[s.state], 14) : ''}</span> <span>${s.text}</span><span class="vh"> (${s.state === 'current' ? 'current' : s.state === 'done' ? 'done' : 'to do'})</span></li>`)}</ul>
      ${d.keys.length ? html`<div class="keysline">${d.keys.map((k) => html`${keycap(k.key, { sm: true })} <span class="mono">${k.output}</span> <span class="g">${k.gesture}</span>`)}</div>` : ''}
      <p class="stars" aria-label="Stars ${d.stars} of 3">Stars ${d.stars} / 3</p>
      <p class="rowkeys">${JOURNAL_COPY.choose}</p></div>`
    : html`<div class="detail"><p>${JOURNAL_COPY.empty}</p></div>`;
  const also = vm.also.map((a) => html`<button type="button" class="kh-btn${a.id === 'ride-hub' ? ' primary' : ''}" data-fid="also-${a.id}" ${cmdAttr(ALSO_COMMAND[a.id] || { type: 'back' })}>${a.label}${a.key ? html` ${keycap(a.key, { sm: true })}` : ''}</button>`);
  return html`<div class="scrim"></div>
<section class="kh-panel overlay" role="dialog" aria-modal="true" aria-label="${JOURNAL_COPY.title}" data-screen="journal">
  <div class="top"><h2>${JOURNAL_COPY.title}</h2><span class="seals">${icon('seal', 24)} Clearance seals ${vm.seals} / 5</span><span class="grow"></span>${closeButton()}</div>
  <div class="kh-journal"><div class="list">${groups}</div><div class="side">${detail}
    <div class="also"><span class="kh-label">${JOURNAL_COPY.also}</span><div class="btns">${also}</div></div></div></div>
</section>`;
}

export class Journal extends Component {
  static topic = 'vm:journal';
  static modal = true;
  view(vm) { return journalView(vm); }
}

export function controlsView(vm) {
  const rows = vm.rows.map((r) => html`<div class="kh-crow" role="row" aria-label="${r.action}. Key ${r.key.label}. ${r.gesture}">
    <span class="ac">${r.action}</span><span class="k">${keycap(r.key, { sm: true })}</span><span class="g">${r.gesture}</span>
    <span class="w">${icon(r.worksOnPractice ? 'check' : 'circle', 16)} ${r.worksOnPractice ? 'Works on practice' : 'Release Caps first'}</span></div>`);
  return html`<div class="scrim"></div>
<section class="kh-panel overlay" role="dialog" aria-modal="true" aria-label="${CONTROLS_COPY.title}" data-screen="controls">
  <div class="top"><h2>${CONTROLS_COPY.title}</h2><span class="sub">${CONTROLS_COPY.lede}</span><span class="grow"></span>${closeButton()}</div>
  <p class="ctl-ex" data-autofocus tabindex="-1">${CONTROLS_COPY.example}</p>
  <div class="kh-ctable" role="table"><div class="kh-crow head" role="row"><span>Action</span><span>Key</span><span>Kanata gesture</span><span>Practice layer</span></div>${rows}</div>
  <div class="ctl-cards"><div class="ctl-card"><span class="wh">${icon('check', 20)} ${CONTROLS_COPY.practiceTitle}</span><p>${CONTROLS_COPY.practiceText}</p></div>
    <div class="ctl-card dashed"><span class="wh">${icon('lock', 20)} ${CONTROLS_COPY.neverTitle}</span><p>${CONTROLS_COPY.neverText}</p></div></div>
</section>`;
}

export class Controls extends Component {
  static topic = 'vm:controls';
  static modal = true;
  view(vm) { return controlsView(vm); }
}

function toggle(id, name, desc, on) {
  return html`<div class="kh-opt"><span></span><div><div class="nm">${name}</div><div class="ds">${desc}</div></div>
    <button type="button" class="kh-sw ${on ? 'on' : 'off'}" role="switch" aria-checked="${on ? 'true' : 'false'}" aria-label="${name}" data-fid="set-${id}" data-setting="${id}"
      ${cmdAttr({ type: 'setSetting', key: id, value: !on })}><span class="track"></span>${on ? 'On' : 'Off'}</button></div>`;
}

function choice(id, name, desc, options, current) {
  return html`<div class="kh-opt"><span></span><div><div class="nm">${name}</div><div class="ds">${desc}</div></div>
    <div class="seg" role="group" aria-label="${name}">${options.map(([v, label]) => html`<button type="button" data-fid="set-${id}-${v}" aria-pressed="${v === current ? 'true' : 'false'}"
      ${cmdAttr({ type: 'setSetting', key: id, value: v })}>${v === current ? icon('check', 16) : ''}${label}</button>`)}</div></div>`;
}

export function settingsView(vm) {
  const S = SETTINGS_COPY;
  const reset = vm.confirmReset
    ? html`<div class="kh-reset" role="alertdialog" aria-label="${S.resetQuestion}"><div class="q">${icon('warn', 24)} ${S.resetQuestion}</div><p>${S.resetBody}</p>
      <div class="btns"><button type="button" class="kh-btn primary" data-fid="reset-keep" data-autofocus ${cmdAttr({ type: 'back' })}>${S.keep} ${keycap(CLOSE.key, { sm: true })}</button>
      <button type="button" class="kh-btn" data-fid="reset-do" ${cmdAttr({ type: 'resetProgress', confirmed: true })}>${S.doReset}</button></div></div>`
    : html`<div class="kh-opt"><span></span><div><div class="nm">${S.reset.name}</div><div class="ds">${S.reset.desc}</div></div>
      <button type="button" class="kh-btn" data-fid="reset-ask" ${cmdAttr({ type: 'resetProgress', confirmed: false })}>${S.reset.name}...</button></div>`;
  return html`<div class="scrim"></div>
<section class="kh-panel overlay" role="dialog" aria-modal="true" aria-label="${S.title}" data-screen="settings">
  <div class="top"><h2>${S.title}</h2><span class="grow"></span>${closeButton()}</div>
  <div class="kh-set"><div class="col"><h3>${S.accessibility}</h3>
    ${toggle('largerText', S.largerText.name, S.largerText.desc, vm.largerText)}
    ${toggle('highContrast', S.highContrast.name, S.highContrast.desc, vm.highContrast)}
    ${choice('reducedMotion', S.reducedMotion.name, S.reducedMotion.desc, [['system', 'System'], ['on', 'On'], ['off', 'Off']], vm.reducedMotion)}</div>
  <div class="col"><h3>${S.keyboard.name}</h3>
    ${choice('keyboard', S.keyboard.name, S.keyboard.desc, Object.entries(KEYBOARD_LABELS), vm.keyboard)}
    <h3>${S.reset.name}</h3>${reset}
    <div class="btns"><button type="button" class="kh-btn" data-fid="run-setup" ${cmdAttr({ type: 'openLayer', id: 'setup' })}>${S.runSetup}</button>
    <button type="button" class="kh-btn" data-fid="open-controls" ${cmdAttr({ type: 'openLayer', id: 'controls' })}>${S.controls}</button></div></div></div>
</section>`;
}

export class Settings extends Component {
  static topic = 'vm:settings';
  static modal = true;
  view(vm) { return settingsView(vm); }
}
