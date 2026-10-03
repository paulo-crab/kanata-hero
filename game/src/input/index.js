// Input module public surface. Contract: game/CONTRACTS.md section 4.
export { interpretKey, KeyInterpreter, isClaimed, isIgnoredKey } from './interpreter.js';
export { BINDINGS, resolveAction, ARROW_DIRS } from './bindings.js';
export {
  CALIBRATION_STEPS, Calibration, STATUS_LABELS, STEP_STATUSES, KEYBOARD_TYPES,
} from './calibration.js';
export { LayoutManifest } from './layout-manifest.js';
export { layoutHelpModel, keyFace, shortLegend } from './layout-help.js';
export { HINT_CARD_TEXT, HintGate } from './hint-gate.js';
export { CONFIDENCE_LABELS, confidenceLabel, isConfidence, weakestConfidence } from './confidence.js';
