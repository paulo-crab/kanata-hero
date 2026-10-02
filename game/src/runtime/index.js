// Runtime module public surface. Contract: game/CONTRACTS.md section 5.
// Depends on shared, the engine World (injected) and the input module (injected as a namespace).
export { PROGRESS_KEY, ProgressStore } from './progress.js';
export { SUPPORTED_OPS, RuleRuntime } from './rules.js';
export { parseCondition } from './condition.js';
export { TRANSITIONS, SceneMachine } from './machine.js';
export { DialogueRuntime, hintOutputs } from './dialogue.js';
export { EvidenceLog, isClean, computeStars } from './evidence.js';
export {
  HubScene, WalkScene, FormScene, LabelScene, EditorScene, DialogueScene, LayoutHelpScene,
  JournalScene, ControlsScene, SettingsScene, ErrorScene, SetupScene, CalibrationScene, ArrivalScene,
  createSceneFactories,
} from './scenes/index.js';
export { Session, createSession } from './session.js';
