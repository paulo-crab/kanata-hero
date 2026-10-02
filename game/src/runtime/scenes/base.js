// Scene base class and the world-input helper shared by hub and walk scenes.
import { OUTPUT_DIR } from '../common.js';

export class BaseScene {
  constructor(id, kind) {
    this.id = id;
    this.kind = kind;
    this.modal = false;
    this.keys = {};
    this.finished = null; // {success?, data?, next?, payload?}: the machine pops or replaces when set
  }

  enter(ctx, payload) {
    this.ctx = ctx;
    this.payload = payload || {};
  }

  handle() {
    return false;
  }

  update() {}

  exit() {
    return this.result;
  }

  snapshot() {
    return undefined;
  }

  viewModel() {
    return null;
  }

  finish(result) {
    this.result = result;
    this.finished = result;
  }
}

export function dirOf(ev) {
  return ev.dir || OUTPUT_DIR[ev.output] || null;
}

/**
 * Open-world input: arrows move (held repeat via setHeld), Return interacts, Q opens the journal,
 * ? opens Layout help, Backtick asks for a hint. Returns true when consumed.
 */
export function handleWorldInput(ctx, ev) {
  const avatar = ctx.world.avatar;
  const dir = dirOf(ev);
  if (ev.phase === 'up') {
    if (dir && ctx.held === dir) {
      ctx.held = null;
      avatar.setHeld(null);
      return true;
    }
    return false;
  }
  if (ev.action === 'move' || (!ev.action && dir)) {
    if (ev.repeat || !dir) return true;
    ctx.held = dir;
    avatar.setHeld(dir);
    avatar.requestStep(dir);
    return true;
  }
  if (ev.repeat) return false;
  switch (ev.action) {
    case 'interact':
      ctx.actions.interact();
      return true;
    case 'journal':
      if (ctx.machine.canPush('journal')) ctx.machine.push('journal');
      return true;
    case 'layoutHelp':
      if (ctx.machine.canPush('layout-help')) ctx.machine.push('layout-help');
      return true;
    case 'hint':
      ctx.actions.requestHint();
      return true;
    default:
      return false;
  }
}
