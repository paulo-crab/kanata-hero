// Detects which modules are still contract stubs (throw 'not implemented') so the full-stack tests
// can skip with a clear reason instead of failing until integration.
import * as engine from '../../src/engine/index.js';
import * as input from '../../src/input/index.js';
import * as runtime from '../../src/runtime/index.js';
import * as ui from '../../src/ui/index.js';
import { EventBus } from '../../src/shared/index.js';

function isStub(fn) {
  try {
    fn();
    return false;
  } catch (e) {
    return /not implemented/.test(String(e && e.message));
  }
}

/** @returns {{engine:boolean, input:boolean, runtime:boolean, ui:boolean}} true = real implementation present */
export function implemented() {
  return {
    engine: !isStub(() => new engine.AnimationPlayer({ frames: 2, ms: 100, row: 0 })),
    input: !isStub(() => new input.Calibration('macbook')),
    runtime: !isStub(() => runtime.parseCondition('step_start:x')),
    ui: !isStub(() => ui.mountUi({}, { bus: new EventBus() })),
  };
}

/** A skip reason for `test(name, {skip})`, or false when every named module is implemented. */
export function skipUnless(...names) {
  const have = implemented();
  const missing = names.filter((n) => !have[n]);
  return missing.length ? `modules not implemented yet: ${missing.join(', ')} (contract stubs)` : false;
}

