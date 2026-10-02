// Clocks. See game/CONTRACTS.md section 2.2.
export class RealClock {
  now() {
    return performance.now();
  }
  setTimer(ms, fn) {
    return setTimeout(fn, ms);
  }
  clearTimer(id) {
    clearTimeout(id);
  }
}

export class FakeClock {
  constructor(startMs = 0) {
    this._now = startMs;
    this._seq = 0;
    this._timers = [];
  }
  now() {
    return this._now;
  }
  setTimer(ms, fn) {
    const id = ++this._seq;
    this._timers.push({ id, at: this._now + ms, fn });
    return id;
  }
  clearTimer(id) {
    this._timers = this._timers.filter((t) => t.id !== id);
  }
  pending() {
    return this._timers.length;
  }
  advance(ms) {
    this.set(this._now + ms);
  }
  set(ms) {
    if (ms < this._now) throw new Error('FakeClock cannot go backwards');
    for (;;) {
      const due = this._timers
        .filter((t) => t.at <= ms)
        .sort((a, b) => a.at - b.at || a.id - b.id)[0];
      if (!due) break;
      this._timers = this._timers.filter((t) => t !== due);
      this._now = due.at;
      due.fn();
    }
    this._now = ms;
  }
}
