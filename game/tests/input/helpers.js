import { readFileSync } from 'node:fs';
import { fileURLToPath } from 'node:url';
import path from 'node:path';
import { EventBus, FakeClock } from '../../src/shared/index.js';
import { KeyInterpreter } from '../../src/input/index.js';

const here = path.dirname(fileURLToPath(import.meta.url));
export const repo = path.resolve(here, '..', '..', '..');

export function readRepo(rel) {
  return readFileSync(path.join(repo, rel), 'utf8');
}

/** A plain KeyboardEvent-shaped object. */
export function ev(key, extra = {}) {
  const code = extra.code ?? (key === '`' ? 'Backquote' : '');
  return { key, code, repeat: false, isComposing: false, altKey: false, ctrlKey: false, metaKey: false, shiftKey: false, ...extra, preventDefault() { this.prevented = true; } };
}

export function ctx(over = {}) {
  return {
    sceneId: 't', typing: false, enter: 'none', esc: 'none', arrows: 'none', journal: false,
    hint: false, layoutHelp: true, surfaceFocused: true, consumes: [], ...over,
  };
}

export const HUB = { sceneId: 'hub', enter: 'interact', esc: 'none', arrows: 'move', journal: true, hint: true };
export const DIALOGUE = { sceneId: 'dlg', enter: 'continue', esc: 'skip', arrows: 'none', hint: true };
export const LABEL = { sceneId: 'label', typing: true, enter: 'text', esc: 'back', arrows: 'text', hint: true };

export function makeInterpreter(context) {
  const clock = new FakeClock(1000);
  const bus = new EventBus();
  const seen = [];
  bus.on('input:event', (e) => seen.push(e));
  let current = context;
  const interp = new KeyInterpreter({ clock, bus, getContext: () => current });
  return { interp, clock, bus, seen, setContext: (c) => { current = c; } };
}
