// Terminal scenes of level 01: form (popup), label (west desk), editor (folded form).
// They emit scene:success / scene:progress / scene:feedback and record evidence per action.
import { BaseScene } from './base.js';
import {
  keycap, observedName, KEY_GESTURE, CONFIDENCE_LABEL, CONFIDENCE_KEY,
} from '../common.js';

const TITLES = {
  'o01-popup': 'Welcome popup', 'o01-desk-label': 'Desk label', 'o01-fold': 'Folded form',
};

class TerminalScene extends BaseScene {
  constructor(def, ctx, kind) {
    super(def.id, kind);
    this.def = def;
    this.ctx = ctx;
    this.modal = true;
    this.text = '';
    this.cursor = 0;
    this.wrong = false;
  }

  _isCommand(ev) {
    return ev.output === 'Backquote' || ev.output === '?';
  }

  /** Hint and Layout help work in every typing scene. Returns true when the event was one of them. */
  _command(ev) {
    if (ev.output === 'Backquote' || ev.action === 'hint') {
      this.ctx.actions.requestHint();
      return true;
    }
    if (ev.output === '?' || ev.action === 'layoutHelp') {
      if (this.ctx.machine.canPush('layout-help')) this.ctx.machine.push('layout-help');
      return true;
    }
    return false;
  }

  _feedbackLine(ev, map) {
    const fb = map || {};
    return fb[ev.combo] || fb[ev.output] || fb.other || 'That is not what this step needs.';
  }

  _record(ev, correct) {
    this.ctx.evidence.record(this.id, {
      output: ev.combo && ev.combo !== ev.output ? ev.combo : ev.output,
      correct, critical: true, confidence: CONFIDENCE_KEY[this.def.confidence] ? 'observed' : 'observed',
    });
  }

  _say(ev, line, effect) {
    const gesture = this.ctx.dialogue && this.ctx.dialogue.instruction() && this.ctx.dialogue.instruction().hint
      ? this.ctx.dialogue.instruction().hint.gesture : null;
    this.ctx.bus.emit('scene:feedback', { sceneId: this.id, observed: ev.output, line });
    this.ctx.bus.emit('vm:feedback', {
      gesture, observed: `${observedName(ev)} observed`, effect: line || effect,
      confidence: 'observed', confidenceLabel: CONFIDENCE_LABEL[this.def.confidence] || 'Output observed',
    });
  }

  _success(ev, effect) {
    this.ctx.evidence.finish(this.id, true);
    this._say(ev, effect, effect);
    this.ctx.bus.emit('scene:success', { sceneId: this.id });
    this.finish({ success: true });
  }

  _leave() {
    this.finish({ success: false });
  }

  _bar(field, extra = {}) {
    return {
      kind: this.kind, title: TITLES[this.id] || this.id, prompt: this.def.task.prompt || this.def.task_summary,
      field, leave: { key: keycap('Escape'), gesture: KEY_GESTURE.back }, ...extra,
    };
  }
}

/** o01-popup: only Escape closes it; arrows and Return are named in the feedback and nothing is lost. */
export class FormScene extends TerminalScene {
  constructor(def, ctx) {
    super(def, ctx, 'form');
    this.keys = {
      typing: true, enter: 'none', esc: 'text', arrows: 'text', journal: false, hint: true, consumes: ['Escape'],
    };
  }

  handle(ev) {
    if (ev.phase === 'up' || ev.repeat) return false;
    if (this._command(ev)) return true;
    const step = this.def.task.steps[0];
    const ok = step.accepts.includes(ev.output);
    this._record(ev, ok);
    if (ok) {
      this._success(ev, this.def.task.effect === 'popup closes' ? 'Popup closes' : this.def.task.effect);
    } else {
      this._say(ev, this._feedbackLine(ev, step.feedback));
    }
    return true;
  }

  viewModel() {
    return this._bar(null);
  }
}

/** o01-desk-label: the field must read 'west'; a wrong character is refused with a correction. */
export class LabelScene extends TerminalScene {
  constructor(def, ctx) {
    super(def, ctx, 'label');
    this.target = def.task.target;
    this.text = def.task.initial || '';
    this.keys = {
      typing: true, enter: 'text', esc: 'back', arrows: 'text', journal: false, hint: true, consumes: [],
    };
  }

  handle(ev) {
    if (ev.phase === 'up' || ev.repeat) return false;
    if (this._command(ev)) return true;
    if (ev.output === 'Escape') {
      this._leave();
      return true;
    }
    const plain = ev.text && ev.text.length === 1 && ev.combo === ev.output;
    const expected = this.target[this.text.length];
    if (plain && ev.text === expected) {
      this.text += ev.text;
      this._record(ev, true);
      this.ctx.bus.emit('scene:progress', { sceneId: this.id, done: this.text.length, total: this.target.length });
      if (this.text === this.target) this._success(ev, `Label reads ${this.target}`);
      else this._say(ev, null, `Typed ${ev.text}`);
    } else {
      this._record(ev, false);
      this._say(ev, this._feedbackLine(ev, this.def.task.feedback));
    }
    return true;
  }

  viewModel() {
    return this._bar(
      { text: this.text, cursor: this.text.length, target: this.target },
      { nextLetter: this.target[this.text.length] },
    );
  }
}

/** o01-fold: ArrowRight x4 then y; instant retry on a wrong result; untimed. */
export class EditorScene extends TerminalScene {
  constructor(def, ctx) {
    super(def, ctx, 'editor');
    this.initial = def.task.initial;
    this.target = def.task.target;
    this.text = this.initial;
    this.cursor = 0;
    this._keys = {
      typing: true, enter: 'text', esc: 'back', arrows: 'text', journal: false, hint: true, consumes: [],
    };
  }

  get keys() {
    return { ...this._keys, enter: this.wrong ? 'retry' : 'text' };
  }

  set keys(v) {
    this._keys = { ...this._keys, ...v };
  }

  _reset() {
    this.text = this.initial;
    this.cursor = 0;
  }

  handle(ev) {
    if (ev.phase === 'up' || ev.repeat) return false;
    if (this._command(ev)) return true;
    if (ev.output === 'Escape') {
      this._leave();
      return true;
    }
    if (ev.output === 'Enter' && this.wrong) {
      this.wrong = false;
      this._reset();
      return true;
    }
    if (ev.output === 'ArrowRight' && ev.combo === ev.output) {
      this._record(ev, true);
      if (this.cursor < this.text.length) this.cursor += 1;
      this.wrong = false;
      this._say(ev, null, 'Cursor moves right');
      return true;
    }
    if (ev.text === 'y' && ev.combo === ev.output && this.cursor === this.text.length) {
      this._record(ev, true);
      this.text += 'y';
      this._success(ev, `Field reads ${this.text}`);
      return true;
    }
    this._record(ev, false);
    this._reset();
    this.wrong = true;
    this._say(ev, this._feedbackLine(ev, this.def.task.feedback));
    return true;
  }

  viewModel() {
    return this._bar({ text: this.text, cursor: this.cursor, target: this.target });
  }
}
