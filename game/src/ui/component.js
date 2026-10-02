// Component base class (contract section 6). A component owns one host element.
// `view(vm)` is a pure function from a view-model to markup; `render(vm)` puts it in the host.
// vm === null hides the component. Focus inside the host survives a re-render (matched by data-fid).

export class Component {
  /** Bus topic this component listens to (set on the subclass), or null when mount wires it by hand. */
  static topic = null;
  /** A modal component keeps Tab inside itself while it is shown (Esc always leaves). */
  static modal = false;

  constructor(host, bus, opts = {}) {
    this.host = host;
    this.bus = bus;
    this.opts = opts;
    this.vm = null;
    this.shown = false;
    this._offs = [];
    const topic = this.constructor.topic;
    if (topic && bus) this._offs.push(bus.on(topic, (vm) => this.render(vm)));
    if (host && this.constructor.modal && host.setAttribute) host.setAttribute('data-modal', '');
  }

  /** Whether this vm shows the component. Override for conditional components. */
  isVisible(vm) { return vm !== null && vm !== undefined; }

  /** @returns {string|import('./html.js').Raw} markup for the vm. Pure. */
  view() { return ''; }

  render(vm) {
    const fid = this.captureFocus();
    this.vm = vm === undefined ? null : vm;
    if (!this.isVisible(this.vm)) {
      this.host.innerHTML = '';
      this.host.hidden = true;
      this.shown = false;
      return;
    }
    this.host.innerHTML = String(this.view(this.vm));
    this.host.hidden = false;
    if (!this.shown) {
      this.shown = true;
      this.focusInitial();
    } else if (fid) {
      this.restoreFocus(fid);
    }
  }

  captureFocus() {
    const host = this.host;
    const doc = host && host.ownerDocument;
    const active = doc && doc.activeElement;
    if (!active || !active.getAttribute) return null;
    if (host.contains && !host.contains(active)) return null;
    return active.getAttribute('data-fid');
  }

  restoreFocus(fid) {
    const el = this.host.querySelector(`[data-fid="${fid}"]`);
    if (el && el.focus) el.focus({ preventScroll: true });
  }

  focusInitial() {
    const el = this.host.querySelector('[data-autofocus]');
    if (el && el.focus) el.focus({ preventScroll: true });
  }

  destroy() {
    for (const off of this._offs) off();
    this._offs = [];
    if (this.host) {
      this.host.innerHTML = '';
      this.host.hidden = true;
    }
    this.shown = false;
  }
}

/** Where Tab goes inside a modal layer: wraps at both ends. Pure, so it is testable without a DOM. */
export function nextFocusIndex(count, current, backwards) {
  if (count <= 0) return -1;
  if (current < 0 || current >= count) return backwards ? count - 1 : 0;
  return backwards ? (current - 1 + count) % count : (current + 1) % count;
}
