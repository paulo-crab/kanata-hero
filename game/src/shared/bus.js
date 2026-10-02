// Event bus. See game/CONTRACTS.md section 2.1.
export class EventBus {
  constructor() {
    this._handlers = new Map();
    this._queue = [];
    this._draining = false;
  }

  on(topic, handler) {
    if (!this._handlers.has(topic)) this._handlers.set(topic, []);
    this._handlers.get(topic).push(handler);
    return () => this.off(topic, handler);
  }

  once(topic, handler) {
    const off = this.on(topic, (...args) => {
      off();
      handler(...args);
    });
    return off;
  }

  off(topic, handler) {
    const list = this._handlers.get(topic);
    if (!list) return;
    const i = list.indexOf(handler);
    if (i >= 0) list.splice(i, 1);
  }

  emit(topic, payload) {
    this._queue.push([topic, payload]);
    if (this._draining) return;
    this._draining = true;
    try {
      while (this._queue.length) {
        const [t, p] = this._queue.shift();
        this._deliver(t, p);
      }
    } finally {
      this._draining = false;
    }
  }

  _deliver(topic, payload) {
    const exact = (this._handlers.get(topic) || []).slice();
    const all = (this._handlers.get('*') || []).slice();
    for (const h of exact) this._call(h, topic, [payload, topic]);
    for (const h of all) this._call(h, topic, [topic, payload]);
  }

  _call(handler, topic, args) {
    try {
      handler(...args);
    } catch (error) {
      if (topic !== 'bus:error') this.emit('bus:error', { topic, error });
    }
  }
}
