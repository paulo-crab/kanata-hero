// Overlay scenes: dialogue layer, Layout help, journal, Controls, settings, error.
import { BaseScene } from './base.js';
import { keycap, KEY_GESTURE } from '../common.js';

export class DialogueScene extends BaseScene {
  constructor() {
    super('dialogue', 'dialogue');
    this.modal = true;
    this.keys = { typing: false, enter: 'continue', esc: 'skip', arrows: 'none', journal: false, hint: true };
  }

  _check() {
    if (!this.ctx.dialogue.hasConversation()) this.finish({ success: true });
  }

  handle(ev) {
    if (ev.phase === 'up' || ev.repeat) return true;
    switch (ev.action) {
      case 'continue': this.ctx.dialogue.advance(); break;
      case 'skip': this.ctx.dialogue.skip(); break;
      case 'hint': this.ctx.actions.requestHint(); break;
      case 'layoutHelp':
        if (this.ctx.machine.canPush('layout-help')) this.ctx.machine.push('layout-help');
        break;
      default: return true;
    }
    this._check();
    return true;
  }

  update() {
    this._check();
  }
}

export class LayoutHelpScene extends BaseScene {
  constructor() {
    super('layout-help', 'layout-help');
    this.modal = true;
    this.keys = { typing: false, enter: 'none', esc: 'back', arrows: 'choose', journal: false, hint: false };
  }

  enter(ctx, payload) {
    super.enter(ctx, payload);
    if (this.state) return;
    const m = ctx.manifest;
    this.state = {
      tab: m ? m.tabs()[0] : 'base',
      variant: ctx.progress.doc.settings.keyboard,
      selectedKey: null,
    };
  }

  select(patch) {
    Object.assign(this.state, patch);
  }

  handle(ev) {
    if (ev.phase === 'up' || ev.repeat) return true;
    if (ev.action === 'back') {
      this.finish({ success: true });
    } else if (ev.action === 'choose' && this.ctx.manifest && (ev.dir === 'e' || ev.dir === 'w')) {
      const tabs = this.ctx.manifest.tabs();
      const i = tabs.indexOf(this.state.tab);
      this.state.tab = tabs[(i + (ev.dir === 'e' ? 1 : tabs.length - 1)) % tabs.length];
    }
    return true;
  }

  viewModel() {
    const { input, manifest } = this.ctx;
    if (!input || !input.layoutHelpModel || !manifest) return { tab: this.state.tab, tabs: [], keys: [] };
    return input.layoutHelpModel(manifest, { ...this.state });
  }
}

const ALSO = [
  { id: 'layout-help', label: 'Layout help', key: '?' },
  { id: 'settings', label: 'Settings' },
  { id: 'controls', label: 'Controls' },
  { id: 'ride-hub', label: 'Ride to the hub' },
];

export class JournalScene extends BaseScene {
  constructor() {
    super('journal', 'journal');
    this.modal = true;
    this.sel = 0;
    this.keys = { typing: false, enter: 'confirm', esc: 'back', arrows: 'choose', journal: true, hint: false };
  }

  _rows() {
    const { level } = this.ctx.data;
    const { rules } = this.ctx;
    const done = rules.holds(`level_complete:${level.id}`);
    const cur = rules.currentStep;
    const mainRows = [{
      id: level.id, title: `${level.number}. ${level.title}`,
      state: done ? 'done' : 'active', detail: cur && !cur.optional ? cur.objective : (done ? 'Complete' : ''),
    }];
    const optional = level.steps.filter((s) => s.optional).map((s) => ({
      id: s.id, title: s.objective,
      state: rules.stepsDone.includes(s.id) ? 'done' : (cur && cur.id === s.id ? 'active' : 'locked'),
      detail: '',
    }));
    return { mainRows, optional };
  }

  _flat() {
    const { mainRows, optional } = this._rows();
    return [...mainRows.map((r) => ({ ...r, group: 'main' })),
      ...optional.map((r) => ({ ...r, group: 'requests' })),
      ...ALSO.map((r) => ({ ...r, group: 'also' }))];
  }

  handle(ev) {
    if (ev.phase === 'up' || ev.repeat) return true;
    const flat = this._flat();
    if (ev.action === 'back' || ev.action === 'journal') {
      this.finish({ success: true });
    } else if (ev.action === 'choose' && (ev.dir === 's' || ev.dir === 'n')) {
      this.sel = (this.sel + (ev.dir === 's' ? 1 : flat.length - 1)) % flat.length;
    } else if (ev.action === 'confirm') {
      this.activate(flat[this.sel]);
    }
    return true;
  }

  activate(row) {
    if (!row || row.group !== 'also') return;
    const m = this.ctx.machine;
    if (row.id === 'ride-hub') {
      this.ctx.bus.emit('vm:toast', { text: 'You are already in the Orientation hub.', tone: 'info' });
      this.finish({ success: true });
    } else if (m.canPush(row.id)) {
      m.push(row.id);
    }
  }

  viewModel() {
    const { level } = this.ctx.data;
    const flat = this._flat();
    const sel = flat[this.sel];
    const groups = [
      { id: 'main', heading: 'Main quests' },
      { id: 'requests', heading: 'Optional' },
      { id: 'speed', heading: 'Optional speed' },
    ].map((g) => ({
      ...g,
      rows: flat.map((r, i) => ({ r, i })).filter(({ r }) => r.group === g.id).map(({ r, i }) => ({
        id: r.id, title: r.title, state: r.state, detail: r.detail, selected: i === this.sel,
      })),
    }));
    const { rules, progress } = this.ctx;
    const detail = sel && sel.group === 'main' ? {
      title: `${level.number}. ${level.title}`,
      steps: level.steps.filter((s) => !s.optional).map((s) => ({
        text: s.objective,
        state: rules.stepsDone.includes(s.id) ? 'done' : (rules.currentStep && rules.currentStep.id === s.id ? 'current' : 'todo'),
      })),
      keys: this._keys(level),
      stars: ((progress.doc.levels[level.id] || {}).stars) || 0,
    } : null;
    return {
      groups, detail, seals: progress.doc.seals.length,
      also: ALSO.map((a, k) => ({
        id: a.id, label: a.label, selected: flat.length - ALSO.length + k === this.sel,
        ...(a.key ? { key: keycap(a.key) } : {}),
      })),
      entries: progress.doc.journal.slice(),
    };
  }

  _keys(level) {
    const seen = new Set();
    const out = [];
    for (const d of level.dialogue) {
      if (!d.hint || seen.has(d.hint.key)) continue;
      seen.add(d.hint.key);
      out.push({ key: keycap(d.hint.key.length === 1 ? d.hint.key : d.hint.key), output: d.hint.key, gesture: d.hint.gesture });
    }
    return out;
  }
}

export const CONTROLS = [
  { action: 'Interact, Continue, Retry', key: 'Enter', gesture: KEY_GESTURE.interact },
  { action: 'Skip, Back, close, leave', key: 'Escape', gesture: KEY_GESTURE.back },
  { action: 'Move and choose', key: 'ArrowLeft', gesture: KEY_GESTURE.move },
  { action: 'Show hint', key: 'Backquote', gesture: KEY_GESTURE.hint },
  { action: 'Journal', key: 'q', gesture: KEY_GESTURE.journal },
  { action: 'Layout help', key: '?', gesture: KEY_GESTURE.layoutHelp },
];

export class ControlsScene extends BaseScene {
  constructor() {
    super('controls', 'controls');
    this.modal = true;
    this.keys = { typing: false, enter: 'confirm', esc: 'back', arrows: 'choose', journal: false, hint: false };
  }

  handle(ev) {
    if (ev.phase === 'up' || ev.repeat) return true;
    if (ev.action === 'back' || ev.action === 'confirm') this.finish({ success: true });
    return true;
  }

  viewModel() {
    return { rows: CONTROLS.map((c) => ({ action: c.action, key: keycap(c.key), gesture: c.gesture, worksOnPractice: true })) };
  }
}

const ROWS = ['keyboard', 'reducedMotion', 'largerText', 'highContrast', 'setup', 'reset'];

export class SettingsScene extends BaseScene {
  constructor() {
    super('settings', 'settings');
    this.modal = true;
    this.sel = 0;
    this.confirmReset = false;
    this.keys = { typing: false, enter: 'confirm', esc: 'back', arrows: 'choose', journal: false, hint: false };
  }

  set(key, value) {
    this.ctx.progress.update((d) => { d.settings[key] = value; });
    this.ctx.bus.emit('vm:announce', { text: `${key} set to ${value}` });
  }

  handle(ev) {
    if (ev.phase === 'up' || ev.repeat) return true;
    const s = this.ctx.progress.doc.settings;
    if (ev.action === 'back') {
      if (this.confirmReset) this.confirmReset = false;
      else this.finish({ success: true });
    } else if (ev.action === 'choose' && (ev.dir === 's' || ev.dir === 'n')) {
      this.confirmReset = false;
      this.sel = (this.sel + (ev.dir === 's' ? 1 : ROWS.length - 1)) % ROWS.length;
    } else if (ev.action === 'confirm') {
      const row = ROWS[this.sel];
      if (row === 'keyboard') this.set('keyboard', s.keyboard === 'macbook' ? 'microsoft' : 'macbook');
      else if (row === 'reducedMotion') this.set('reducedMotion', { system: 'on', on: 'off', off: 'system' }[s.reducedMotion]);
      else if (row === 'largerText' || row === 'highContrast') this.set(row, !s[row]);
      else if (row === 'setup' && this.ctx.machine.canPush('setup')) this.ctx.machine.push('setup', { reopened: true });
      else if (row === 'reset') {
        if (!this.confirmReset) this.confirmReset = true;
        else this.ctx.actions.resetProgress();
      }
    }
    return true;
  }

  viewModel() {
    const s = this.ctx.progress.doc.settings;
    return {
      keyboard: s.keyboard, reducedMotion: s.reducedMotion, largerText: s.largerText, highContrast: s.highContrast,
      confirmReset: this.confirmReset, focus: ROWS[this.sel],
    };
  }
}

export class ErrorScene extends BaseScene {
  constructor() {
    super('error', 'error');
    this.modal = true;
    this.keys = { typing: false, enter: 'none', esc: 'none', arrows: 'none', journal: false, hint: false, layoutHelp: true };
  }

  enter(ctx, payload) {
    super.enter(ctx, payload);
    const e = (payload && payload.error) || {};
    this.vm = { file: e.file || 'unknown', kind: e.kind || 'unknown', message: e.message || String(e) };
  }

  handle() {
    return true;
  }

  viewModel() {
    return this.vm;
  }
}
