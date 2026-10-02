// Minimal DOM stub, no dependencies. Elements keep innerHTML as a string; querySelector looks at the
// start tags inside it and returns small element objects (stable between calls, focusable, with attributes).

const TAG_RE = /<([a-zA-Z][\w-]*)((?:\s+[^<>]*?)?)\s*\/?>/g;
const ATTR_RE = /([\w:-]+)(?:="([^"]*)")?/g;

const unesc = (s) => s.replace(/&quot;/g, '"').replace(/&#39;/g, "'").replace(/&lt;/g, '<').replace(/&gt;/g, '>').replace(/&amp;/g, '&');

function parseAttrs(src) {
  const attrs = new Map();
  let m;
  ATTR_RE.lastIndex = 0;
  while ((m = ATTR_RE.exec(src))) attrs.set(m[1], m[2] === undefined ? '' : unesc(m[2]));
  return attrs;
}

/** One simple selector: tag?, [attr], [attr="v"], .class, #id, :not([attr]) / :not([attr="v"]). */
function matchSimple(tag, attrs, sel) {
  let rest = sel.trim();
  const tm = /^[a-zA-Z][\w-]*/.exec(rest);
  if (tm) { if (tm[0] !== tag) return false; rest = rest.slice(tm[0].length); }
  const re = /:not\(\[([\w:-]+)(?:="([^"]*)")?\]\)|\[([\w:-]+)(?:="([^"]*)")?\]|\.([\w-]+)|#([\w-]+)/g;
  let m;
  while ((m = re.exec(rest))) {
    if (m[1] !== undefined) {
      const has = attrs.has(m[1]) && (m[2] === undefined || attrs.get(m[1]) === m[2]);
      if (has) return false;
    } else if (m[3] !== undefined) {
      if (!attrs.has(m[3])) return false;
      if (m[4] !== undefined && attrs.get(m[3]) !== m[4]) return false;
    } else if (m[5] !== undefined) {
      if (!(attrs.get('class') || '').split(/\s+/).includes(m[5])) return false;
    } else if (m[6] !== undefined) {
      if (attrs.get('id') !== m[6]) return false;
    }
  }
  return true;
}

const matches = (tag, attrs, selector) => selector.split(/,(?![^(]*\))/).some((s) => matchSimple(tag, attrs, s));

export class El {
  constructor(doc, tag = 'div') {
    this.ownerDocument = doc;
    this.tagName = tag;
    this.children = [];
    this.attrs = new Map();
    this.hidden = false;
    this.className = '';
    this.textContent = '';
    this.listeners = new Map();
    this.focusCount = 0;
    this.host = null;
    this._html = '';
    this._parsed = null;
    this.classes = new Set();
    this.classList = {
      add: (c) => this.classes.add(c),
      remove: (c) => this.classes.delete(c),
      toggle: (c, on) => { const want = on === undefined ? !this.classes.has(c) : !!on; if (want) this.classes.add(c); else this.classes.delete(c); return want; },
      contains: (c) => this.classes.has(c),
    };
  }

  get innerHTML() { return this._html; }
  set innerHTML(v) { this._html = String(v); this._parsed = null; }

  setAttribute(k, v) { this.attrs.set(k, String(v)); }
  getAttribute(k) { return this.attrs.has(k) ? this.attrs.get(k) : null; }
  hasAttribute(k) { return this.attrs.has(k); }
  removeAttribute(k) { this.attrs.delete(k); }
  appendChild(c) { this.children.push(c); c.parentElement = this; return c; }
  addEventListener(t, fn) { if (!this.listeners.has(t)) this.listeners.set(t, []); this.listeners.get(t).push(fn); }
  removeEventListener(t, fn) { const l = this.listeners.get(t); if (l) l.splice(l.indexOf(fn), 1); }
  /** Test helper: deliver an event to this element's listeners. */
  fire(type, ev = {}) {
    const e = { target: this, key: undefined, shiftKey: false, defaultPrevented: false, preventDefault() { this.defaultPrevented = true; }, ...ev };
    for (const fn of this.listeners.get(type) || []) fn(e);
    return e;
  }
  focus() { this.focusCount += 1; this.ownerDocument.activeElement = this; }
  contains(o) { return o === this || o.host === this || this.children.some((c) => c.contains(o)); }
  get isConnected() { return true; }

  matchesSelector(selector) { return matches(this.tagName, this.attrs, selector); }
  closest(selector) {
    let el = this;
    while (el) {
      if (el.matchesSelector && el.matchesSelector(selector)) return el;
      el = el.host || el.parentElement;
    }
    return null;
  }

  _elements() {
    if (this._parsed) return this._parsed;
    const out = [];
    let m;
    TAG_RE.lastIndex = 0;
    while ((m = TAG_RE.exec(this._html))) {
      const e = new El(this.ownerDocument, m[1].toLowerCase());
      e.attrs = parseAttrs(m[2]);
      e.host = this;
      e.outer = m[0];
      out.push(e);
    }
    this._parsed = out;
    return out;
  }

  querySelectorAll(selector) { return this._elements().filter((e) => matches(e.tagName, e.attrs, selector)); }
  querySelector(selector) { return this.querySelectorAll(selector)[0] || null; }
}

export class Doc {
  constructor() {
    this.activeElement = null;
    this.created = [];
    this.defaultView = { location: { reloads: 0, reload() { this.reloads += 1; } } };
  }
  createElement(tag) { const e = new El(this, tag); this.created.push(e); return e; }
  getElementById(id) { return this.created.find((e) => e.getAttribute('id') === id) || null; }
}

export function makeDom() {
  const doc = new Doc();
  const root = doc.createElement('div');
  const stage = doc.createElement('div');
  stage.setAttribute('id', 'stage');
  return { doc, root, stage };
}

/** A matchMedia stand-in whose `matches` and change listeners the test controls. */
export function fakeMatchMedia(initial = false) {
  const mq = {
    matches: initial,
    listeners: [],
    addEventListener(_t, fn) { mq.listeners.push(fn); },
    removeEventListener(_t, fn) { mq.listeners = mq.listeners.filter((f) => f !== fn); },
    set(v) { mq.matches = v; mq.listeners.forEach((f) => f({ matches: v })); },
  };
  return { matchMedia: () => mq, mq };
}

/** Balanced-tag check: catches broken markup from a view. Returns the first problem or null. */
export function markupProblem(markup) {
  const VOID = new Set(['br', 'img', 'input', 'hr', 'meta', 'link', 'path', 'circle', 'rect', 'use']);
  const stack = [];
  const re = /<(\/?)([a-zA-Z][\w-]*)([^<>]*?)(\/?)>/g;
  let m;
  while ((m = re.exec(markup))) {
    const [, close, tag, , selfClose] = m;
    const t = tag.toLowerCase();
    if (selfClose || VOID.has(t)) continue;
    if (!close) stack.push(t);
    else if (stack.pop() !== t) return `unexpected </${t}>`;
  }
  return stack.length ? `unclosed <${stack[stack.length - 1]}>` : null;
}
