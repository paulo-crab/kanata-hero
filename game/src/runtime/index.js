// Runtime module public surface. Contract: game/CONTRACTS.md section 5.
// Stubs: workstream C replaces the throwing bodies.
const nyi = () => {
  throw new Error('not implemented');
};

export const PROGRESS_KEY = 'kanata-hero:progress';

export const SUPPORTED_OPS = [
  'set_state', 'npc_state', 'unlock_gate', 'set_flag',
  'complete_level', 'start_dialogue', 'spawn_glitch', 'journal',
];

export const TRANSITIONS = {
  setup: ['calibration', 'hub', 'arrival', 'error'],
  calibration: ['arrival', 'hub', 'error'],
  arrival: ['hub', 'dialogue', 'error'],
  hub: ['dialogue', 'walk', 'label', 'form', 'editor', 'layout-help', 'journal', 'controls', 'settings', 'error'],
  dialogue: ['hub', 'walk', 'label', 'form', 'editor', 'layout-help'],
  walk: ['dialogue', 'label', 'form', 'layout-help', 'journal'],
  label: ['layout-help'],
  form: ['layout-help'],
  editor: ['layout-help'],
  journal: ['layout-help', 'controls', 'settings'],
  settings: ['setup'],
  'layout-help': [],
  controls: [],
  error: [],
};

export class SceneMachine {
  constructor(ctx, factories) { nyi(); }
  push(kind, payload) { nyi(); }
  pop(result) { nyi(); }
  replace(kind, payload) { nyi(); }
  get top() { nyi(); }
  get stack() { nyi(); }
  handle(ev) { nyi(); }
  update(stepMs) { nyi(); }
  inputContext() { nyi(); }
}

export function parseCondition(str) { nyi(); }

export class RuleRuntime {
  constructor(params) { nyi(); }
  start() { nyi(); }
  notify(fact) { nyi(); }
  holds(conditionStr) { nyi(); }
  get currentStep() { nyi(); }
  get stepsDone() { nyi(); }
  isVisible(interactionId) { nyi(); }
  onRequest(dialogueId) { nyi(); }
}

export class DialogueRuntime {
  constructor(params) { nyi(); }
  open(id) { nyi(); }
  advance() { nyi(); }
  skip() { nyi(); }
  observe(ev) { nyi(); }
  current() { nyi(); }
  instruction() { nyi(); }
}

export class FormScene { constructor(def, ctx) { nyi(); } }
export class WalkScene { constructor(def, ctx) { nyi(); } }
export class LabelScene { constructor(def, ctx) { nyi(); } }
export class EditorScene { constructor(def, ctx) { nyi(); } }

export class EvidenceLog {
  record(sceneId, action) { nyi(); }
  hint(use) { nyi(); }
  finish(sceneId, success) { nyi(); }
  scene(sceneId) { nyi(); }
  all() { nyi(); }
  toJSON() { nyi(); }
  static fromJSON(json) { nyi(); }
}
export function isClean(evidence) { nyi(); }
export function computeStars(levelId, evidenceMap, levelDef) { nyi(); }

export class ProgressStore {
  constructor(params) { nyi(); }
  get persistent() { nyi(); }
  load() { nyi(); }
  save(doc) { nyi(); }
  update(mutator) { nyi(); }
  reset() { nyi(); }
  hasProgress() { nyi(); }
}
