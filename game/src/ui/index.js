// UI module public surface. Contract: game/CONTRACTS.md sections 6 and 7.
// Depends on shared only: it renders view-models from the bus and sends ui:command back.
import { INSET_STAGE_RECT } from '../shared/layout.js';

export { mountUi, stageClasses } from './mount.js';
export { Component, nextFocusIndex } from './component.js';
export { keycap, keyunit, keycapForName, keycapName } from './keycap.js';
export { hudView, promptView, markersView, edgeArrowView } from './play.js';
export {
  targetIndicator, markerCentre, avatarStageRect, compassWord, DIALOGUE_STAGE_RECT, INSET_AVOID_RECT, ARROW_SIZE,
} from './world-space.js';
export { dialogueView, hintCardView, portraitView } from './dialogue.js';
export { insetView } from './inset.js';
export { sceneBarView, feedbackView, fieldView } from './scene.js';
export { layoutHelpView, diagramView, legendKinds } from './layout-help.js';
export { journalView, controlsView, settingsView } from './journal.js';
export { setupScreenView, calibrationBody, createScreenState } from './setup.js';
export { toastsView, errorView, TOAST_MS, TOAST_MAX } from './misc.js';

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

/** Keyboard inset rectangle in stage px (x4 reference). Pure. */
export function insetRect(zoom = 4) {
  const k = zoom / 4;
  const r = INSET_STAGE_RECT;
  return { x: r.x * k, y: r.y * k, w: r.w * k, h: r.h * k };
}

export function rectsOverlap(a, b) {
  return a.x < b.x + b.w && a.x + a.w > b.x && a.y < b.y + b.h && a.y + a.h > b.y;
}
