// Dialogue runtime. Contract: game/CONTRACTS.md section 5.4.
// Conversation lines (modal) own Return/Esc; instruction lines (non-modal) take no keys and close
// when the step ends. The runtime holds state and publishes vm:dialogue; the session pushes the layer.
import { keycap, KEY_GESTURE } from './common.js';

const NAMES = {
  ivo: ['Ivo', 'Reception'], mira: ['Mira', 'Courier'], engineer: ['Engineer', null],
  popup: ['Popup', null], pace_sign: ['Pace sign', null], form_card: ['Form card', null],
  printer_card: ['Printer card', null], slip_card: ['Slip card', null],
};

const KEY_OUTPUT = {
  Escape: 'Escape', Q: 'q', Backtick: 'Backquote', '?': '?', 'Down Arrow': 'ArrowDown', 'Up Arrow': 'ArrowUp',
  'Left Arrow': 'ArrowLeft', 'Right Arrow': 'ArrowRight', Return: 'Enter',
};

/** hint.key text -> ordered list of outputs ('W, E, S, T', 'Up Arrow, then Left Arrow'). */
export function hintOutputs(key) {
  return String(key).split(/,\s*(?:then\s+)?/).map((t) => t.trim()).filter(Boolean)
    .map((t) => KEY_OUTPUT[t] || t.toLowerCase());
}

export class DialogueRuntime {
  /** @param {{level:object, bus:object, rules:object, portraitRect?:(key:string)=>object, isWorldTop?:()=>boolean, getPatches?:()=>string[]}} p */
  constructor({ level, bus, rules, portraitRect, isWorldTop, getPatches }) {
    this.level = level;
    this.bus = bus;
    this.rules = rules;
    this.portraitRect = portraitRect || null;
    this.isWorldTop = isWorldTop || (() => true);
    this.getPatches = getPatches || (() => []);
    this._byId = new Map((level.dialogue || []).map((d) => [d.id, d]));
    this.conversation = null;
    this.queue = [];
    this.instr = null;
    this._pos = 0;
    this._observed = false;
    this._lastId = null;
    this._lastInstructionId = null;
    this._lastVm = 'null';
  }

  line(id) {
    const d = this._byId.get(id);
    if (!d) throw new Error(`Unknown dialogue ${id}`);
    return d;
  }

  isModal(d) {
    return d.modal === undefined ? !d.hint : d.modal;
  }

  /** Modal: becomes the conversation (or queues behind it). Non-modal: becomes the instruction line. */
  open(id) {
    const d = this.line(id);
    this._lastId = id;
    if (this.isModal(d)) {
      if (this.conversation) this.queue.push(d);
      else this.conversation = d;
      this.bus.emit('dialogue:open', { id, modal: true });
    } else {
      this.instr = d;
      this._pos = 0;
      this._observed = false;
      this._lastInstructionId = id;
      this.bus.emit('dialogue:open', { id, modal: false });
    }
    this.publish();
    return this.isModal(d) ? 'modal' : 'instruction';
  }

  hasConversation() {
    return !!this.conversation;
  }

  current() {
    return this.conversation;
  }

  instruction() {
    return this.instr;
  }

  lastLineId() {
    return this._lastId;
  }

  lastInstructionId() {
    return this._lastInstructionId;
  }

  _closeConversation(by) {
    const d = this.conversation;
    if (!d) return;
    this.conversation = this.queue.shift() || null;
    this.bus.emit('dialogue:closed', { id: d.id, by });
    this.rules.notify({ type: 'dialogue_done', id: d.id });
    this.publish();
  }

  advance() {
    this._closeConversation('advance');
  }

  skip() {
    this._closeConversation('skip');
  }

  clearInstruction() {
    if (!this.instr) return;
    this.instr = null;
    this.publish();
  }

  /** An instruction line completes (dialogue_done) when its hint key sequence has been observed. */
  observe(ev) {
    if (!this.instr || !this.instr.hint || ev.phase === 'up' || ev.repeat || this._observed) return;
    const want = hintOutputs(this.instr.hint.key);
    if (ev.output !== want[this._pos]) return;
    this._pos += 1;
    if (this._pos < want.length) return;
    this._observed = true;
    this.rules.notify({ type: 'dialogue_done', id: this.instr.id });
  }

  _portrait(d) {
    if (!d.portrait) return null;
    let speaker = d.speaker;
    if (speaker === 'mira' && this.getPatches().includes('first_delivery')) speaker = 'mira_patch1';
    const key = `${speaker}_${d.portrait}`;
    return { key, rect: this.portraitRect ? this.portraitRect(key) : { x: 0, y: 0, w: 0, h: 0 } };
  }

  viewModelFor(d, mode) {
    const [speakerName, role] = NAMES[d.speaker] || [d.speaker.replace(/_/g, ' '), null];
    const portrait = this._portrait(d);
    const vm = {
      id: d.id, speaker: d.speaker, speakerName, portrait, objectSpeaker: !portrait,
      text: d.text, hint: d.hint ? { ...d.hint } : null, mode,
      footer: mode === 'conversation' ? [
        { action: 'Continue', key: keycap('Enter'), gesture: KEY_GESTURE.continue },
        { action: 'Skip', key: keycap('Escape'), gesture: KEY_GESTURE.skip },
      ] : [],
    };
    if (role) vm.role = role;
    return vm;
  }

  viewModel() {
    if (this.conversation) return this.viewModelFor(this.conversation, 'conversation');
    if (this.instr && this.isWorldTop()) return this.viewModelFor(this.instr, 'instruction');
    return null;
  }

  publish() {
    const vm = this.viewModel();
    const s = JSON.stringify(vm);
    if (s === this._lastVm) return;
    this._lastVm = s;
    this.bus.emit('vm:dialogue', vm);
  }
}
