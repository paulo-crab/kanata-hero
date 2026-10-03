// Toast stack, live region and error screen (vm:toast, vm:announce, vm:error).
import { Component } from './component.js';
import { html } from './html.js';
import { icon } from './icons.js';
import { ERROR_COPY } from './strings.js';

export const TOAST_MS = 6000;
export const TOAST_MAX = 3;

export function toastsView(toasts) {
  const items = toasts.map((t) => html`<div class="kh-toast ${t.tone === 'warn' ? 'warn' : ''}" data-toast="${t.id}">
    <span class="ic">${icon(t.tone === 'warn' ? 'warn' : t.tone === 'feedback' ? 'eye' : 'seal', 32)}</span>
    <span class="t">${t.text}</span>
  </div>`);
  return html`<div class="kh-toasts" role="status" aria-live="polite">${items}</div>`;
}

/** At most three toasts, each gone after about six seconds on the injected clock. A null vm clears the stack. */
export class Toast extends Component {
  static topic = 'vm:toast';
  constructor(host, bus, opts = {}) {
    super(host, bus, opts);
    this.toasts = [];
    this.seq = 0;
    this.timers = new Map();
  }

  render(vm) {
    if (vm === null || vm === undefined) {
      this.clear();
    } else {
      // A toast with a key replaces the one with the same key (walking updates one toast instead of stacking).
      if (vm.key) {
        const same = this.toasts.find((t) => t.key === vm.key);
        if (same) this.expire(same.id, false);
      }
      const id = ++this.seq;
      this.toasts.push({ id, key: vm.key || null, text: vm.text, tone: vm.tone || 'info' });
      while (this.toasts.length > TOAST_MAX) this.expire(this.toasts[0].id, false);
      const clock = this.opts.clock;
      if (clock) this.timers.set(id, clock.setTimer(vm.ms || TOAST_MS, () => this.expire(id)));
    }
    this.paint();
  }

  expire(id, paint = true) {
    this.toasts = this.toasts.filter((t) => t.id !== id);
    const timer = this.timers.get(id);
    if (timer !== undefined && this.opts.clock) this.opts.clock.clearTimer(timer);
    this.timers.delete(id);
    if (paint) this.paint();
  }

  clear() {
    for (const id of [...this.timers.keys()]) {
      if (this.opts.clock) this.opts.clock.clearTimer(this.timers.get(id));
    }
    this.timers.clear();
    this.toasts = [];
  }

  paint() {
    this.vm = this.toasts.length ? this.toasts : null;
    if (!this.toasts.length) {
      this.host.innerHTML = '';
      this.host.hidden = true;
      return;
    }
    this.host.innerHTML = String(toastsView(this.toasts));
    this.host.hidden = false;
  }

  destroy() { this.clear(); super.destroy(); }
}

/** aria-live="polite" region. Identical consecutive bus announcements are not repeated. */
export class LiveRegion extends Component {
  static topic = null;
  constructor(host, bus, opts = {}) {
    super(host, bus, opts);
    this.last = null;
    this.flip = false;
    if (host.setAttribute) {
      host.setAttribute('aria-live', 'polite');
      host.setAttribute('role', 'status');
    }
    host.hidden = false;
  }

  /** Speak text. `repeat` forces a repeat of the same sentence by alternating a trailing no-break space. */
  say(text, { repeat = false } = {}) {
    const t = String(text);
    if (t === this.last && !repeat) return false;
    this.flip = t === this.last ? !this.flip : false;
    this.last = t;
    this.host.textContent = this.flip ? `${t} ` : t;
    return true;
  }

  render(vm) { if (vm && vm.text) this.say(vm.text); }
}

export function errorView(vm) {
  return html`<div class="scrim error-scrim"></div>
<section class="kh-panel kh-error" role="alertdialog" aria-modal="true" aria-label="${ERROR_COPY.title}" tabindex="-1" data-autofocus>
  <h2>${icon('warn', 32)} ${ERROR_COPY.title}</h2>
  <p class="msg">${vm.message}</p>
  <p class="meta"><span class="kh-label">File</span> <span class="mono">${vm.file}</span> <span class="kh-label">Problem</span> <span class="mono">${vm.kind}</span></p>
  <p class="help">${ERROR_COPY.help}</p>
  <button type="button" class="kh-btn primary" data-fid="reload" data-ui="reload">${ERROR_COPY.reload}</button>
</section>`;
}

export class ErrorScreen extends Component {
  static topic = 'vm:error';
  static modal = true;
  view(vm) { return errorView(vm); }
}
