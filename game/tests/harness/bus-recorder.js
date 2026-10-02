// Records every bus emit in order, so scenarios can assert on topics and payloads.
export class BusRecorder {
  /** @param {{on:(topic:string, h:Function)=>Function}} bus */
  constructor(bus) {
    this.events = [];
    this._off = bus.on('*', (topic, payload) => this.events.push({ topic, payload }));
  }
  stop() { this._off(); }
  topics() { return this.events.map((e) => e.topic); }
  of(topic) { return this.events.filter((e) => e.topic === topic).map((e) => e.payload); }
  last(topic) { const l = this.of(topic); return l.length ? l[l.length - 1] : undefined; }
  count(topic) { return this.of(topic).length; }
  clear() { this.events.length = 0; }
}
