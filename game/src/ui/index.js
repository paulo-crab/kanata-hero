// UI module public surface. Contract: game/CONTRACTS.md sections 6 and 7.
// Stubs: workstream D replaces the throwing bodies. Pure helpers are already real.
import { INSET_STAGE_RECT } from '../shared/layout.js';

const nyi = () => {
  throw new Error('not implemented');
};

export const COMPONENTS = [
  'keycap', 'inset', 'dialogue', 'hud', 'prompt', 'markers', 'journal', 'layout-help',
  'setup', 'calibration', 'scene-bar', 'feedback', 'controls', 'first-use', 'settings',
  'toast', 'hint-card', 'error', 'live-region',
];

export const VIEW_MODEL_TOPICS = [
  'vm:dialogue', 'vm:hud', 'vm:prompt', 'vm:markers', 'vm:inset', 'vm:journal',
  'vm:layout-help', 'vm:setup', 'vm:calibration', 'vm:scene-bar', 'vm:feedback',
  'vm:hint-card', 'vm:controls', 'vm:settings', 'vm:toast', 'vm:announce', 'vm:error',
];

export function mountUi(root, params) { nyi(); }

export class Component {
  constructor(host, bus) { nyi(); }
  render(vm) { nyi(); }
  destroy() { nyi(); }
}

/** Keyboard inset rectangle in stage px (x4 reference). Pure. */
export function insetRect(zoom = 4) {
  const k = zoom / 4;
  const r = INSET_STAGE_RECT;
  return { x: r.x * k, y: r.y * k, w: r.w * k, h: r.h * k };
}

export function rectsOverlap(a, b) {
  return a.x < b.x + b.w && a.x + a.w > b.x && a.y < b.y + b.h && a.y + a.h > b.y;
}
