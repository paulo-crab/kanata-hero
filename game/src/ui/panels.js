// Stage rectangles of the panels that can cover the world (playtest 1, item 1). The camera look-ahead keeps the avatar
// clear of them. The numbers are the measured worst cases of the real layout at 1280x720 (they hold at x4 and, scaled
// with the stage, at x6): tests/ui/panels.test.js checks them against the CSS, tests/e2e/avatar-clear.test.js walks the
// level with them.
import { STAGE_W, INSET_STAGE_RECT } from '../shared/layout.js';
import { INSET_AVOID_RECT } from './world-space.js';

const MARGIN = 16;

/** Dialogue strip: docked at the bottom edge beside the inset, at most 660 wide and 160 tall. */
export const DIALOGUE_RECTS = Object.freeze({
  conversation: Object.freeze({ x: 604, y: 720 - MARGIN - 160, w: 660, h: 160 }),
  instruction: Object.freeze({ x: 604, y: 720 - MARGIN - 128, w: 660, h: 128 }),
});
export const HUD_STRIP_RECT = Object.freeze({ x: MARGIN, y: MARGIN, w: 400, h: 60 });
export const HUD_CHIPS_RECT = Object.freeze({ x: STAGE_W - MARGIN - 390, y: MARGIN, w: 390, h: 60 });
export const SCENE_BAR_RECT = Object.freeze({ x: MARGIN, y: MARGIN, w: 900, h: 210 });
export const FEEDBACK_RECT = Object.freeze({ x: STAGE_W - MARGIN - 332, y: 88, w: 332, h: 240 });

/** vm:* topics the panel set depends on. */
export const PANEL_TOPICS = [
  'vm:dialogue', 'vm:inset', 'vm:hud', 'vm:scene-bar', 'vm:feedback', 'vm:settings-flags',
  'vm:journal', 'vm:layout-help', 'vm:controls', 'vm:settings', 'vm:setup', 'vm:calibration', 'vm:hint-card', 'vm:error',
];
const FULL_SCREEN = ['vm:journal', 'vm:layout-help', 'vm:controls', 'vm:settings', 'vm:setup', 'vm:calibration', 'vm:hint-card', 'vm:error'];

/**
 * @param {Object<string, object|null>} vms latest view-model per topic (a missing topic is null)
 * @returns {{covered:boolean, panels:{id:string,x:number,y:number,w:number,h:number}[]}} `covered`: a full-screen
 *   layer is open and dims the world, so there is nothing to keep clear
 */
export function panelRects(vms) {
  if (FULL_SCREEN.some((t) => vms[t])) return { covered: true, panels: [] };
  const panels = [];
  const add = (id, r) => panels.push({ id, x: r.x, y: r.y, w: r.w, h: r.h });
  const larger = !!(vms['vm:settings-flags'] && vms['vm:settings-flags'].largerText);
  const dlg = vms['vm:dialogue'];
  if (dlg) add('dialogue', dlg.mode === 'conversation' ? DIALOGUE_RECTS.conversation : DIALOGUE_RECTS.instruction);
  if (vms['vm:inset']) add('inset', larger ? INSET_AVOID_RECT : INSET_STAGE_RECT);
  const hud = vms['vm:hud'];
  if (hud) {
    if (!hud.compact) add('hud', HUD_STRIP_RECT);
    add('hud-chips', HUD_CHIPS_RECT);
  }
  if (vms['vm:scene-bar']) add('scene-bar', SCENE_BAR_RECT);
  if (vms['vm:feedback']) add('feedback', FEEDBACK_RECT);
  return { covered: false, panels };
}

/** Which CSS selector each panel id dims when the camera cannot clear it. */
export const FADE_SELECTORS = Object.freeze({
  dialogue: '.kh-dialogue',
  inset: '.kh-inset',
  hud: '.kh-hud.obj',
  'hud-chips': '.kh-hud.shortcuts',
  'scene-bar': '.kh-term',
  feedback: '.kh-side',
});
